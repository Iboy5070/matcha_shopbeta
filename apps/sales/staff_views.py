from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import urlencode


def staff_login(request):
    """Redirect to admin login since store_login is removed."""
    next_url = request.GET.get("next") or request.POST.get("next") or "/staff/"
    query = urlencode({"next": next_url})
    return redirect(f"/admin/login/?{query}")


@login_required(login_url="/admin/login/")
def staff_dashboard(request):
    from django.contrib.auth import logout

    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        logout(request)
        return redirect("/admin/login/")
        
    from .staff_stats import get_staff_dashboard_stats

    return render(request, "staff/dashboard.html", {
        "staff_section": "home",
        **get_staff_dashboard_stats(),
    })


def staff_logout(request):
    from django.contrib.auth import logout

    logout(request)
    return redirect("/pos/")

@login_required(login_url="/admin/login/")
def staff_slips(request):
    from .models import Order
    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/admin/login/")
        
    # Get orders that are PENDING and have a bill with a payment that has a slip_url
    pending_orders = Order.objects.filter(
        status="PENDING",
        bill__payments__slip_url__isnull=False
    ).exclude(bill__payments__slip_url="").distinct().order_by("-order_date")
    
    return render(request, "staff/slips.html", {
        "staff_section": "slips",
        "pending_orders": pending_orders,
    })

@login_required(login_url="/admin/login/")
def verify_slip(request, order_id):
    from decimal import Decimal
    from .models import Order, Bill
    from django.contrib import messages
    
    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/admin/login/")
        
    if request.method == "POST":
        order = Order.objects.get(id=order_id)
        action = request.POST.get("action")
        
        if action == "approve":
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
            messages.warning(request, f"ປະຕິເສດສະລິບອໍເດີ #{order.id} ແລ້ວ")
            
    return redirect("staff_slips")


@login_required(login_url="/admin/login/")
def staff_inventory(request):
    """Read-only stock view for staff — they can see quantities but all
    editing (adding new stock batches, correcting numbers) stays in the
    Admin database, superuser only."""
    from apps.catalog.models import Product
    from apps.inventory.models import Inventory

    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/admin/login/")

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


@login_required(login_url="/admin/login/")
def staff_reserved(request):
    from django.utils import timezone
    from .models import Reserved

    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/admin/login/")

    reservations = (
        Reserved.objects.select_related("order", "product", "order__customer", "order__employee")
        .order_by("-res_date")
    )
    return render(request, "staff/reserved.html", {
        "staff_section": "reserved",
        "reservations": reservations,
        "now": timezone.now(),
    })


@login_required(login_url="/admin/login/")
def staff_reserved_action(request, reserved_id):
    from decimal import Decimal
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    from .models import Reserved, Order, Bill

    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/admin/login/")

    reserved = get_object_or_404(Reserved, id=reserved_id)

    if request.method == "POST":
        action = request.POST.get("action")
        order = reserved.order

        if action == "complete":
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
