from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.catalog.models import Product, ProductVariant
from apps.store.models import PaymentConfirmation, WebOrder

from .staff_utils import staff_required


def _absolute_slip_url(request, url: str) -> str:
    if not url:
        return ""
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return request.build_absolute_uri(url)


def _to_decimal(value) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")


WEB_ORDER_STATUSES = [c[0] for c in WebOrder.STATUS_CHOICES]


@staff_required
def staff_web_orders(request):
    q = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()

    qs = WebOrder.objects.order_by("-created_at")
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(
            Q(order_no__icontains=q)
            | Q(customer_name__icontains=q)
            | Q(phone__icontains=q)
        )

    if request.method == "POST":
        order_no = (request.POST.get("order_no") or "").strip()
        action = (request.POST.get("action") or "").strip()
        order = get_object_or_404(WebOrder, order_no=order_no)
        if action == "mark_paid":
            order.status = "PAID"
            order.save(update_fields=["status"])
            messages.success(request, f"ອໍເດີ {order.order_no} → PAID")
        elif action == "set_status":
            new_status = (request.POST.get("status") or "").strip()
            if new_status in WEB_ORDER_STATUSES:
                order.status = new_status
                order.save(update_fields=["status"])
                messages.success(request, f"ອໍເດີ {order.order_no} → {new_status}")
        return redirect("staff_web_orders")

    return render(request, "staff/web_orders.html", {
        "orders": qs[:100],
        "q": q,
        "status_filter": status,
        "status_choices": WebOrder.STATUS_CHOICES,
        "staff_section": "web_orders",
    })


@staff_required
def staff_web_order_detail(request, order_no: str):
    order = get_object_or_404(WebOrder, order_no=order_no)
    items = order.items.select_related("variant", "variant__product")
    slip = order.payment_confirmations.order_by("-created_at").first()
    slip_url = _absolute_slip_url(request, slip.display_slip_url) if slip else ""

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()
        if action == "mark_paid":
            order.status = "PAID"
            order.save(update_fields=["status"])
            messages.success(request, "ຢືນຢັນຊຳລະແລ້ວ (PAID)")
        else:
            new_status = (request.POST.get("status") or "").strip()
            if new_status in WEB_ORDER_STATUSES:
                order.status = new_status
                order.save(update_fields=["status"])
                messages.success(request, f"ປ່ຽນສະຖານະເປັນ {new_status}")
        return redirect("staff_web_order_detail", order_no=order.order_no)

    return render(request, "staff/web_order_detail.html", {
        "order": order,
        "items": items,
        "slip": slip,
        "slip_url": slip_url,
        "status_choices": WebOrder.STATUS_CHOICES,
        "staff_section": "web_orders",
    })


@staff_required
def staff_slips(request):
    qs = PaymentConfirmation.objects.select_related("order").order_by("-created_at")

    if request.method == "POST":
        slip_id = request.POST.get("slip_id")
        slip = get_object_or_404(PaymentConfirmation, id=slip_id)
        slip.order.status = "PAID"
        slip.order.save(update_fields=["status"])
        messages.success(request, f"ອໍເດີ {slip.order.order_no} → PAID")
        return redirect("staff_slips")

    slips = []
    for slip in qs[:80]:
        slips.append({
            "obj": slip,
            "url": _absolute_slip_url(request, slip.display_slip_url),
        })

    return render(request, "staff/slips.html", {
        "slips": slips,
        "staff_section": "slips",
    })


@staff_required
def staff_products(request):
    q = (request.GET.get("q") or "").strip()
    variants = ProductVariant.objects.select_related("product", "product__category").order_by(
        "product__name", "display_name"
    )
    if q:
        variants = variants.filter(
            Q(sku__icontains=q)
            | Q(display_name__icontains=q)
            | Q(product__name__icontains=q)
        )

    if request.method == "POST":
        updated = 0
        seen_ids = set()
        for key in request.POST:
            if not key.startswith("v_") or not key.endswith("_stock"):
                continue
            seen_ids.add(int(key.split("_")[1]))

        for variant in ProductVariant.objects.filter(id__in=seen_ids):
            prefix = f"v_{variant.id}_"
            fields = []
            try:
                variant.stock_qty = int(request.POST.get(f"{prefix}stock", variant.stock_qty))
                fields.append("stock_qty")
            except (TypeError, ValueError):
                pass
            price = _to_decimal(request.POST.get(f"{prefix}price"))
            if price >= 0:
                variant.sell_price = price
                fields.append("sell_price")
            variant.is_active = f"{prefix}active" in request.POST
            fields.append("is_active")
            variant.save(update_fields=list(set(fields)))
            updated += 1
        messages.success(request, f"ບັນທຶກສິນຄ້າ {updated} ລາຍການ")
        return redirect(f"{request.path}?q={q}" if q else request.path)

    return render(request, "staff/products.html", {
        "variants": variants[:200],
        "q": q,
        "staff_section": "products",
    })
