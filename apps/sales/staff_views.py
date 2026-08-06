from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import urlencode


def staff_login(request):
    """Staff login uses the same store login page (thesis 4.2.2 / ຮູບ 4.13)."""
    next_url = request.GET.get("next") or request.POST.get("next") or "/staff/"
    query = urlencode({"next": next_url})
    return redirect(f"/login/?{query}")


@login_required(login_url="/login/")
def staff_dashboard(request):
    from django.contrib.auth import logout

    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        logout(request)
        return redirect("/login/?next=/staff/")
        
    from .staff_stats import get_staff_dashboard_stats

    return render(request, "staff/dashboard.html", {
        "staff_section": "home",
        **get_staff_dashboard_stats(),
    })


def staff_logout(request):
    from django.contrib.auth import logout

    logout(request)
    return redirect("/pos/")

@login_required(login_url="/login/")
def staff_slips(request):
    from django.db.models import Q
    from .models import Order
    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/login/?next=/staff/slips/")
        
    # Buy-now PENDING slips + reserve deposits awaiting staff check
    pending_orders = (
        Order.objects.filter(
            Q(status="PENDING") | Q(status="RESERVED"),
            bill__payments__slip_url__isnull=False,
        )
        .exclude(bill__payments__slip_url="")
        .filter(
            Q(status="PENDING")
            | Q(status="RESERVED", reservations__status="RESERVED")
        )
        .distinct()
        .order_by("-order_date")
    )
    
    return render(request, "staff/slips.html", {
        "staff_section": "slips",
        "pending_orders": pending_orders,
    })

@login_required(login_url="/login/")
def verify_slip(request, order_id):
    from decimal import Decimal
    from django.shortcuts import get_object_or_404
    from .models import Order, Bill, Reserved
    from django.contrib import messages
    
    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/login/?next=/staff/slips/")
        
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        action = request.POST.get("action")
        
        if action == "approve":
            if order.status == Order.Status.RESERVED:
                # Deposit slip only — keep reservation open until pickup
                for reserved in order.reservations.filter(status=Reserved.Status.RESERVED):
                    reserved.status = Reserved.Status.PAID
                    reserved.save(update_fields=["status"])
                if hasattr(order, "bill"):
                    bill = order.bill
                    # Deposit already recorded on upload; keep remainder due
                    if bill.balance_due > 0:
                        bill.status = Bill.Status.PARTIAL
                    else:
                        bill.status = Bill.Status.PAID
                    bill.save()
                messages.success(
                    request,
                    f"ອະນຸມັດມັດຈຳອໍເດີ #{order.id} ແລ້ວ — ລໍຖ້າລູກຄ້າມາຮັບ ແລະ ຊຳລະສ່ວນທີ່ເຫຼືອ",
                )
            else:
                order.status = Order.Status.COMPLETED
                order.save()
                if hasattr(order, "bill"):
                    bill = order.bill
                    bill.status = Bill.Status.PAID
                    bill.paid_amount = bill.total_amount
                    bill.balance_due = Decimal("0")
                    bill.save()

                from apps.catalog.stock import deduct_stock
                for item in order.items.all():
                    deduct_stock(item.product_id, item.quantity)

                messages.success(request, f"ອະນຸມັດອໍເດີ #{order.id} ແລ້ວ — ຕັດສະຕັອກ ແລະ ໝາຍວ່າຊຳລະຄົບ")
        elif action == "reject":
            order.status = Order.Status.CANCELLED
            order.save()
            if order.reservations.exists():
                order.reservations.exclude(status=Reserved.Status.CANCELLED).update(
                    status=Reserved.Status.CANCELLED
                )
            messages.warning(request, f"ປະຕິເສດສະລິບອໍເດີ #{order.id} ແລ້ວ")
            
    return redirect("staff_slips")


@login_required(login_url="/login/")
def staff_inventory(request):
    """Thesis 4.2.3 / ຮູບ 4.14 — staff checks warehouse stock (read-only)."""
    from apps.catalog.models import Product
    from apps.inventory.models import Inventory

    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/login/?next=/staff/inventory/")

    products = (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .order_by("category__name", "name")
    )
    recent_batches = Inventory.objects.select_related("product").order_by("-created_at")[:20]

    return render(request, "staff/inventory.html", {
        "staff_section": "inventory",
        "products": products,
        "recent_batches": recent_batches,
    })


@login_required(login_url="/login/")
def staff_reserved(request):
    """Thesis 4.2.4 / ຮູບ 4.16 — staff reservation list."""
    from django.utils import timezone
    from .models import Reserved

    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/login/?next=/staff/reserved/")

    reservations = (
        Reserved.objects.select_related("order", "product", "order__customer", "order__employee")
        .order_by("-res_date")
    )
    return render(request, "staff/reserved.html", {
        "staff_section": "reserved",
        "reservations": reservations,
        "now": timezone.now(),
    })


@login_required(login_url="/login/")
def staff_reserved_action(request, reserved_id):
    from decimal import Decimal
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    from .models import Reserved, Order, Bill

    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/login/?next=/staff/reserved/")

    reserved = get_object_or_404(Reserved, id=reserved_id)

    if request.method == "POST":
        action = request.POST.get("action")
        order = reserved.order

        if action == "complete":
            # Deposit must be staff-confirmed (status -> PAID via verify_slip)
            # before goods can be handed over — regardless of whether a slip
            # was ever uploaded, so an unpaid reservation can never slip through.
            if reserved.status != Reserved.Status.PAID:
                messages.error(
                    request,
                    f"ຈອງ #{reserved.id} ຍັງບໍ່ໄດ້ຢືນຢັນການຈ່າຍມັດຈຳ — ໄປ Payment slips ອະນຸມັດສະລິບກ່ອນ",
                )
                return redirect("staff_slips")

            reserved.status = Reserved.Status.COMPLETED
            reserved.remain_amount = Decimal("0")
            reserved.save()

            from apps.catalog.stock import deduct_stock, consume_allocated_stock
            if reserved.stock_ready:
                consume_allocated_stock(reserved.product_id, reserved.quantity)
            else:
                deduct_stock(reserved.product_id, reserved.quantity)

            if not order.reservations.exclude(status=Reserved.Status.COMPLETED).exists():
                order.status = Order.Status.COMPLETED
                order.save()
                if hasattr(order, "bill"):
                    bill = order.bill
                    bill.paid_amount = bill.total_amount
                    bill.balance_due = Decimal("0")
                    bill.status = Bill.Status.PAID
                    bill.save()
            messages.success(request, f"ຈອງ #{reserved.id} ສຳເລັດແລ້ວ — ລູກຄ້າຮັບເຄື່ອງ ແລະ ຊຳລະຄົບ")

        elif action == "cancel":
            reserved.status = Reserved.Status.CANCELLED
            if reserved.stock_ready:
                from apps.catalog.stock import release_stock
                release_stock(reserved.product_id, reserved.quantity)
                reserved.stock_ready = False
            reserved.save()
            if not order.reservations.exclude(status=Reserved.Status.CANCELLED).exists():
                order.status = Order.Status.CANCELLED
                order.save()
            messages.warning(request, f"ຍົກເລີກການຈອງ #{reserved.id}")

    return redirect("staff_reserved")
