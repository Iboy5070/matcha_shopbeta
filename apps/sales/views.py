from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from apps.catalog.models import ProductVariant
from apps.inventory.models import StockMovement
from .models import Order, OrderItem
from django.db.models import Q
from django.db.models import Sum, Count
from django.utils.dateparse import parse_date

def home(request):
    return redirect("pos")


def _to_decimal(x) -> Decimal:
    if x is None:
        return Decimal("0")
    try:
        return Decimal(str(x))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _get_unit_price(variant: ProductVariant) -> Decimal:
    # ຖ້າມີ sell_price (>0) ໃຊ້ sell_price ບໍ່ມີຄ່ອຍ fallback ໄປ price
    sell_price = _to_decimal(getattr(variant, "sell_price", None))
    if sell_price > 0:
        return sell_price
    return _to_decimal(getattr(variant, "price", 0))


def _make_order_no() -> str:
    # ຕົວຢ່າງ: ORD20260209183045
    return timezone.now().strftime("ORD%Y%m%d%H%M%S")

@login_required
def pos(request):
    q = (request.GET.get("q") or "").strip()

    variants_qs = ProductVariant.objects.select_related("product").all()

    # ✅ Search: sku / display_name / product.name
    if q:
        variants_qs = variants_qs.filter(
            Q(sku__icontains=q)
            | Q(display_name__icontains=q)
            | Q(product__name__icontains=q)
        )

    variants = variants_qs.order_by("sku")

    cart = request.session.get("cart", {})  # {"<variant_id>": qty}
    cart_items = []
    total = Decimal("0")

    for vid, qty in cart.items():
        variant = get_object_or_404(ProductVariant, id=int(vid))
        unit_price = _get_unit_price(variant)
        qty_int = int(qty)
        line_total = unit_price * qty_int
        total += line_total
        cart_items.append({
            "variant": variant,
            "qty": qty_int,
            "unit_price": unit_price,
            "line_total": line_total,
        })

    context = {
        "variants": variants,
        "cart_items": cart_items,
        "total": total,
        "q": q,   # ✅ ส่งค่า search กลับไปให้ template
    }
    return render(request, "pos.html", context)


@login_required
def add_to_cart(request, variant_id):
    cart = request.session.get("cart", {})
    key = str(variant_id)
    cart[key] = int(cart.get(key, 0)) + 1
    request.session["cart"] = cart
    return redirect("pos")


@login_required
def remove_from_cart(request, variant_id):
    # ລົດ qty ທີລະ 1 (ຖ້າ 0 ຄ່ອຍລົບ)
    cart = request.session.get("cart", {})
    key = str(variant_id)

    if key in cart:
        new_qty = int(cart.get(key, 0)) - 1
        if new_qty <= 0:
            del cart[key]
        else:
            cart[key] = new_qty

        request.session["cart"] = cart

    return redirect("pos")


@login_required
def clear_cart(request):
    request.session["cart"] = {}
    return redirect("pos")


@login_required
@transaction.atomic
def pos_checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        messages.warning(request, "Cart ວ່າງຢູ່")
        return redirect("pos")

    # lock rows (ກັນ stock ຜິດພາດເວລາຫຼາຍຄົນກົດພ້ອມກັນ)
    variant_ids = [int(k) for k in cart.keys()]
    variants = ProductVariant.objects.select_for_update().filter(id__in=variant_ids)
    variants_map = {v.id: v for v in variants}

    # ໂຫຼດ items + ຄິດ total
    cart_items = []
    subtotal = Decimal("0")

    for vid_str, qty in cart.items():
        vid = int(vid_str)
        qty_int = int(qty)
        variant = variants_map.get(vid)

        if not variant:
            messages.error(request, f"Variant ID {vid} ບໍ່ພົບ")
            return redirect("pos")

        unit_price = _get_unit_price(variant)
        line_total = unit_price * qty_int
        subtotal += line_total

        cart_items.append({
            "variant": variant,
            "qty": qty_int,
            "unit_price": unit_price,
            "line_total": line_total,
        })

        discount = Decimal("0")

        if request.method == "POST":
           discount = _to_decimal(request.POST.get("discount"))

        if discount < 0:
           discount = Decimal("0")

        if discount > subtotal:
           discount = subtotal

        grand_total = subtotal - discount

    if request.method == "POST":
        payment_method = request.POST.get("payment_method", "cash")

        # ກັນ error ເວລາຜູ້ໃຊ້ພິມບໍ່ແມ່ນຕົວເລກ
        paid_amount = _to_decimal(request.POST.get("paid_amount"))

        if paid_amount < grand_total:
            messages.error(request, "ເງິນທີ່ຮັບ (Paid) ຕ້ອງ ≥ Total")
            return render(request, "pos_checkout.html", {
                "cart_items": cart_items,
                "subtotal": subtotal,
                "discount": discount,
                "grand_total": grand_total,
            })

        # ✅ ເຊັກ stock
        for item in cart_items:
            v = item["variant"]
            if int(v.stock_qty) < int(item["qty"]):
                messages.error(request, f"Stock ບໍ່ພໍ: {v.sku} (ມີ {v.stock_qty})")
                return redirect("pos")

        change_amount = paid_amount - grand_total

        # ✅ ສ້າງ Order
        order = Order.objects.create(
            order_no=_make_order_no(),
            cashier=request.user,
            customer=None,
            subtotal=subtotal,
            discount=discount,
            grand_total=grand_total,
            payment_method=payment_method,
            paid_amount=paid_amount,
            change_amount=change_amount,
        )

        # ✅ ສ້າງ OrderItem + ຺ຕັດ stock + ບັນທຶກ StockMovement
        for item in cart_items:
            v = item["variant"]
            qty_int = int(item["qty"])

            OrderItem.objects.create(
                order=order,
                variant=v,
                qty=qty_int,
                unit_price=item["unit_price"],
                line_total=item["line_total"],
            )

            # ຕັດ stock
            v.stock_qty = int(v.stock_qty) - qty_int
            v.save(update_fields=["stock_qty"])

            # ບັນທຶກການເຄື່ອນໄຫວ stock (OUT)
            StockMovement.objects.create(
                variant=v,
                movement_type=StockMovement.OUT,
                qty=qty_int,
                reason="POS Checkout",
                ref_order=order,
                actor=request.user,
            )

        # clear cart
        request.session["cart"] = {}
        messages.success(request, f"ສຳເລັດ! ບັນທຶກອໍເດີ {order.order_no}")

        return redirect("pos_receipt", order_id=order.id)

    # GET -> show form
    return render(request, "pos_checkout.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "discount": discount,
        "grand_total": grand_total,
    })


@login_required
def pos_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.select_related("variant", "variant__product").all()
    return render(request, "pos_receipt.html", {"order": order, "items": items})

@login_required
def orders_list(request):
    """
    ໜ້າລາຍການບິນ (Order History)
    Filter: date_from, date_to, payment_method
    """
    date_from = parse_date(request.GET.get("from") or "")
    date_to = parse_date(request.GET.get("to") or "")
    payment_method = (request.GET.get("pm") or "").strip()

    qs = Order.objects.all().order_by("-created_at")

    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)
    if payment_method:
        qs = qs.filter(payment_method=payment_method)

    summary = qs.aggregate(
        total_orders=Count("id"),
        total_sales=Sum("grand_total"),
    )

    return render(request, "orders.html", {
        "orders": qs[:200],  # ຈຳກັດ 200 ກ່ອນ ກັນໜ້າຊ້າ
        "summary": summary,
        "date_from": request.GET.get("from", ""),
        "date_to": request.GET.get("to", ""),
        "pm": payment_method,
    })


@login_required
def order_detail(request, order_id):
    """
    ເບິ່ງລາຍລະອຽດບິນທີ່ເລືອກ (reuse receipt template)
    """
    return redirect("pos_receipt", order_id=order_id)
@login_required
@transaction.atomic
def refund_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.select_related("variant").select_for_update()

    if request.method == "POST":
        # คืนทั้งบิล (ง่ายสุด)
        for it in items:
            v = it.variant
            v.stock_qty = int(v.stock_qty) + int(it.qty)
            v.save(update_fields=["stock_qty"])

            StockMovement.objects.create(
                variant=v,
                movement_type=StockMovement.IN,
                qty=int(it.qty),
                reason=f"Refund Order {order.order_no}",
                ref_order=order,
                actor=request.user,
            )

        messages.success(request, f"Refund ສຳເລັດ! {order.order_no}")
        return redirect("pos_receipt", order_id=order.id)

    return render(request, "refund_confirm.html", {"order": order, "items": items})
