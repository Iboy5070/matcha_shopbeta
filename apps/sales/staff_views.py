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
def staff_order_detail(request, order_id):
    """Staff-readable order/bill summary (no Admin permission needed)."""
    from django.shortcuts import get_object_or_404
    from .models import Order

    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect(f"/login/?next=/staff/orders/{order_id}/")

    order = get_object_or_404(
        Order.objects.select_related("customer", "employee", "bill").prefetch_related(
            "items__product",
            "bill__payments",
            "reservations__product",
        ),
        pk=order_id,
    )
    bill = getattr(order, "bill", None)
    payments = list(bill.payments.all()) if bill else []
    return render(request, "staff/order_detail.html", {
        "staff_section": "slips" if order.status in ("PENDING", "RESERVED") else "reserved",
        "order": order,
        "bill": bill,
        "payments": payments,
        "items": order.items.all(),
        "reservations": order.reservations.all(),
    })


@login_required(login_url="/login/")
def staff_inventory(request):
    """Thesis 4.2.3 / ຮູບ 4.14 — staff views stock and can receive (+batch)."""
    from django.contrib import messages
    from apps.catalog.models import Product
    from apps.inventory.models import Inventory

    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/login/?next=/staff/inventory/")

    if request.method == "POST":
        try:
            product_id = int(request.POST.get("product_id", "0"))
            quantity = int(request.POST.get("quantity", "0"))
        except (TypeError, ValueError):
            product_id, quantity = 0, 0
        expiry_raw = (request.POST.get("expiry_date") or "").strip()
        product = Product.objects.filter(pk=product_id, is_active=True).first()
        if not product or quantity < 1:
            messages.error(request, "ເລືອກສິນຄ້າ ແລະ ຈຳນວນຢ່າງນ້ອຍ 1")
        else:
            batch = Inventory(product=product, quantity=quantity)
            if expiry_raw:
                from datetime import date
                try:
                    batch.expiry_date = date.fromisoformat(expiry_raw)
                except ValueError:
                    messages.error(request, "ວັນໝົດອາຍຸບໍ່ຖືກຕ້ອງ (ໃຊ້ຮູບແບບ YYYY-MM-DD)")
                    return redirect("staff_inventory")
            batch.save()  # receive_stock via Inventory.save()
            product.refresh_from_db()
            messages.success(
                request,
                f"ຮັບເຂົ້າ {product.name} +{quantity} ແລ້ວ — ສະຕັອກປັດຈຸບັນ {product.stock_qty}",
            )
        return redirect("staff_inventory")

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
    """Thesis 4.2.4 / ຮູບ 4.16 — staff reservation list (grouped by order)."""
    from decimal import Decimal
    from django.utils import timezone
    from .models import Order, Reserved

    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/login/?next=/staff/reserved/")

    orders = (
        Order.objects.filter(reservations__isnull=False)
        .distinct()
        .select_related("customer", "employee", "bill")
        .prefetch_related("reservations__product", "bill__payments")
        .order_by("-order_date")
    )

    groups = []
    for order in orders:
        lines = list(order.reservations.all())
        if not lines:
            continue
        deposit_total = sum((r.deposit_amount or Decimal("0")) for r in lines)
        remain_total = sum((r.remain_amount or Decimal("0")) for r in lines)
        open_lines = [r for r in lines if r.status in (Reserved.Status.RESERVED, Reserved.Status.PAID)]
        if not open_lines:
            if all(r.status == Reserved.Status.CANCELLED for r in lines):
                group_status = "CANCELLED"
            else:
                group_status = "COMPLETED"
        elif any(r.status == Reserved.Status.RESERVED for r in open_lines):
            group_status = "RESERVED"
        else:
            group_status = "PAID"

        needs_slip = any(r.status == Reserved.Status.RESERVED for r in open_lines)
        needs_pos = any(
            r.status == Reserved.Status.PAID and Decimal(r.remain_amount or 0) > 0
            for r in open_lines
        )
        can_complete = bool(open_lines) and all(
            r.status == Reserved.Status.PAID and Decimal(r.remain_amount or 0) <= 0
            for r in open_lines
        )
        expire_at = min((r.expire_at for r in lines), default=None)
        groups.append({
            "order": order,
            "lines": lines,
            "deposit_total": deposit_total,
            "remain_total": remain_total,
            "qty_total": sum(r.quantity for r in lines),
            "group_status": group_status,
            "needs_slip": needs_slip,
            "needs_pos": needs_pos,
            "can_complete": can_complete,
            "can_cancel": bool(open_lines),
            "expire_at": expire_at,
            "open_count": len(open_lines),
        })

    return render(request, "staff/reserved.html", {
        "staff_section": "reserved",
        "reservation_groups": groups,
        "now": timezone.now(),
    })


def _complete_reserved_line(reserved):
    """Mark one PAID reservation COMPLETED and deduct stock. Caller validates status/remain."""
    from decimal import Decimal
    from apps.catalog.stock import deduct_stock, consume_allocated_stock

    reserved.status = type(reserved).Status.COMPLETED
    reserved.remain_amount = Decimal("0")
    reserved.save()
    if reserved.stock_ready:
        consume_allocated_stock(reserved.product_id, reserved.quantity)
    else:
        deduct_stock(reserved.product_id, reserved.quantity)


@login_required(login_url="/login/")
def staff_reserved_order_action(request, order_id):
    """Confirm or cancel all open reservation lines for one order (single click)."""
    from decimal import Decimal
    from django.shortcuts import get_object_or_404
    from django.contrib import messages
    from .models import Order, Reserved, Bill

    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/login/?next=/staff/reserved/")

    order = get_object_or_404(Order, pk=order_id)
    if request.method != "POST":
        return redirect("staff_reserved")

    action = request.POST.get("action")
    open_lines = list(
        order.reservations.filter(status__in=[Reserved.Status.RESERVED, Reserved.Status.PAID])
    )

    if action == "complete":
        if not open_lines:
            messages.info(request, f"ອໍເດີ #{order.id} ບໍ່ມີລາຍການຈອງທີ່ຕ້ອງຢັ້ງຢືນ")
            return redirect("staff_reserved")
        if any(r.status == Reserved.Status.RESERVED for r in open_lines):
            messages.error(
                request,
                f"ອໍເດີ #{order.id} ຍັງບໍ່ອະນຸມັດມັດຈຳ — ໄປ Payment slips ກ່ອນ",
            )
            return redirect("staff_slips")
        if any(Decimal(r.remain_amount or 0) > 0 for r in open_lines):
            messages.error(
                request,
                f"ອໍເດີ #{order.id} ຍັງຄ້າງຊຳລະ — ຮັບເງິນຄ້າງທີ່ POS ກ່ອນ",
            )
            return redirect("pos_collect_balance", order_id=order.id)

        for reserved in open_lines:
            _complete_reserved_line(reserved)

        order.status = Order.Status.COMPLETED
        order.save()
        if hasattr(order, "bill"):
            bill = order.bill
            bill.paid_amount = bill.total_amount
            bill.balance_due = Decimal("0")
            bill.status = Bill.Status.PAID
            bill.save()
        messages.success(
            request,
            f"ອໍເດີ #{order.id} ສຳເລັດແລ້ວ — ມອບເຄື່ອງທັງໝົດ {len(open_lines)} ລາຍການ",
        )

    elif action == "cancel":
        if not open_lines:
            messages.info(request, f"ອໍເດີ #{order.id} ບໍ່ມີລາຍການຈອງໃຫ້ຍົກເລີກ")
            return redirect("staff_reserved")
        from apps.catalog.stock import release_stock
        for reserved in open_lines:
            reserved.status = Reserved.Status.CANCELLED
            if reserved.stock_ready:
                release_stock(reserved.product_id, reserved.quantity)
                reserved.stock_ready = False
            reserved.save()
        if not order.reservations.exclude(status=Reserved.Status.CANCELLED).exists():
            order.status = Order.Status.CANCELLED
            order.save()
        messages.warning(request, f"ຍົກເລີກການຈອງອໍເດີ #{order.id} ({len(open_lines)} ລາຍການ)")

    return redirect("staff_reserved")


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

            # Option B: remainder must be collected at POS first
            if Decimal(reserved.remain_amount or 0) > 0:
                messages.error(
                    request,
                    f"ຈອງ #{reserved.id} ຍັງຄ້າງຊຳລະ — ຮັບເງິນຄ້າງທີ່ POS ກ່ອນ ຄ່ອຍຢັ້ງຢືນມອບເຄື່ອງ",
                )
                return redirect("pos_collect_balance", order_id=order.id)

            _complete_reserved_line(reserved)

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


def _staff_gate(request, next_path):
    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect(f"/login/?next={next_path}")
    return None


@login_required(login_url="/login/")
def staff_print_deposit(request, order_id):
    """ໃບຢືນຢັນມັດຈຳ — printable deposit confirmation (ER report)."""
    from django.shortcuts import get_object_or_404
    from .models import Order

    denied = _staff_gate(request, f"/staff/orders/{order_id}/print/deposit/")
    if denied:
        return denied

    order = get_object_or_404(
        Order.objects.select_related("customer", "employee", "bill").prefetch_related(
            "reservations__product",
            "bill__payments",
        ),
        pk=order_id,
    )
    reservations = list(order.reservations.all())
    if not reservations:
        from django.contrib import messages
        messages.error(request, f"ອໍເດີ #{order.id} ບໍ່ແມ່ນການຈອງ — ບໍ່ມີໃບມັດຈຳ")
        return redirect("staff_order_detail", order_id=order.id)

    bill = getattr(order, "bill", None)
    deposit_total = sum((r.deposit_amount or 0) for r in reservations)
    remain_total = sum((r.remain_amount or 0) for r in reservations)
    payments = list(bill.payments.all()) if bill else []

    return render(request, "staff/print_deposit.html", {
        "staff_section": "reports",
        "order": order,
        "bill": bill,
        "reservations": reservations,
        "deposit_total": deposit_total,
        "remain_total": remain_total,
        "payments": payments,
    })


@login_required(login_url="/login/")
def staff_print_bill(request, order_id):
    """ໃບບິນ / ໃບຮັບເງິນ — printable bill (ER Bill)."""
    from django.shortcuts import get_object_or_404
    from .models import Order

    denied = _staff_gate(request, f"/staff/orders/{order_id}/print/bill/")
    if denied:
        return denied

    order = get_object_or_404(
        Order.objects.select_related("customer", "employee", "bill").prefetch_related(
            "items__product",
            "bill__payments",
            "reservations__product",
        ),
        pk=order_id,
    )
    bill = getattr(order, "bill", None)
    if not bill:
        from django.contrib import messages
        messages.error(request, f"ອໍເດີ #{order.id} ຍັງບໍ່ມີບິນ")
        return redirect("staff_order_detail", order_id=order.id)

    return render(request, "staff/print_bill.html", {
        "staff_section": "reports",
        "order": order,
        "bill": bill,
        "items": order.items.all(),
        "payments": bill.payments.all(),
        "reservations": order.reservations.all(),
    })


@login_required(login_url="/login/")
def staff_daily_report(request):
    """ລາຍງານຍອດຂາຍລາຍວັນ — printable daily sales (ER report)."""
    from datetime import datetime
    from django.utils import timezone
    from django.db.models import Sum
    from .models import Bill, Order

    denied = _staff_gate(request, "/staff/reports/daily/")
    if denied:
        return denied

    date_str = (request.GET.get("date") or "").strip()
    today = timezone.localdate()
    if date_str:
        try:
            report_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            report_date = today
    else:
        report_date = today

    bills = (
        Bill.objects.filter(bill_date__date=report_date, status="PAID")
        .select_related("order", "order__customer", "order__employee")
        .order_by("bill_date")
    )
    orders_count = Order.objects.filter(order_date__date=report_date).count()
    paid_count = bills.count()
    total_sales = bills.aggregate(s=Sum("total_amount"))["s"] or 0

    return render(request, "staff/print_daily.html", {
        "staff_section": "reports",
        "report_date": report_date,
        "bills": bills,
        "orders_count": orders_count,
        "paid_count": paid_count,
        "total_sales": total_sales,
    })


@login_required(login_url="/login/")
def staff_print_po(request, po_id):
    """ໃບກວດສອບໃບສັ່ງຊື້ (Purchase Order)."""
    from django.shortcuts import get_object_or_404
    from apps.inventory.models import PurchaseOrder

    denied = _staff_gate(request, f"/staff/inventory/po/{po_id}/print/")
    if denied:
        return denied

    po = get_object_or_404(
        PurchaseOrder.objects.select_related("supplier", "employee").prefetch_related(
            "details__product"
        ),
        pk=po_id,
    )
    return render(request, "staff/print_po.html", {
        "staff_section": "inventory",
        "po": po,
        "details": po.details.all(),
    })


@login_required(login_url="/login/")
def staff_print_import(request, import_id):
    """ໃບກວດສອບນຳເຂົ້າສິນຄ້າ."""
    from django.shortcuts import get_object_or_404
    from apps.inventory.models import Imports

    denied = _staff_gate(request, f"/staff/inventory/import/{import_id}/print/")
    if denied:
        return denied

    imp = get_object_or_404(
        Imports.objects.select_related("supplier", "employee", "purchase_order").prefetch_related(
            "details__product"
        ),
        pk=import_id,
    )
    return render(request, "staff/print_import.html", {
        "staff_section": "inventory",
        "imp": imp,
        "details": imp.details.all(),
    })
