from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from apps.catalog.models import Category, Product, ProductVariant
from apps.cms.models import ContactMessage, FAQItem
from .models import WebOrder, WebOrderItem, PaymentConfirmation


def _to_decimal(x) -> Decimal:
    try:
        return Decimal(str(x))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")


def _unit_price(variant: ProductVariant) -> Decimal:
    sp = _to_decimal(getattr(variant, "sell_price", None))
    if sp > 0:
        return sp
    return _to_decimal(getattr(variant, "price", 0))


def _make_web_order_no() -> str:
    return timezone.now().strftime("WEB%Y%m%d%H%M%S")


def home(request):
    featured = (
        Product.objects.filter(is_active=True, is_featured=True)
        .select_related("category")
        .prefetch_related("variants")[:6]
    )
    return render(request, "store/home.html", {"featured_products": featured})


def about(request):
    return render(request, "store/about.html")


def faq(request):
    items = FAQItem.objects.filter(is_active=True)
    return render(request, "store/faq.html", {"faq_items": items})


def privacy(request):
    return render(request, "store/privacy.html")


def returns(request):
    return render(request, "store/returns.html")


def contact(request):
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        message = (request.POST.get("message") or "").strip()
        if not name or not message:
            return render(request, "store/contact.html", {
                "error": "กรุณากรอกชื่อและข้อความ",
            })
        ContactMessage.objects.create(
            name=name, email=email, phone=phone, message=message,
        )
        return render(request, "store/contact.html", {"success": True})
    return render(request, "store/contact.html")


def shop(request):
    q = (request.GET.get("q") or "").strip()
    category_slug = (request.GET.get("category") or "").strip()

    qs = ProductVariant.objects.select_related(
        "product", "product__category",
    ).filter(is_active=True, product__is_active=True)
    if q:
        qs = qs.filter(
            Q(sku__icontains=q)
            | Q(display_name__icontains=q)
            | Q(product__name__icontains=q)
        )
    if category_slug:
        qs = qs.filter(product__category__slug=category_slug)
    qs = qs.order_by("product__name", "sku")

    categories = Category.objects.all()
    return render(request, "store/shop.html", {
        "variants": qs,
        "q": q,
        "categories": categories,
        "active_category": category_slug,
    })


def product_detail(request, variant_id: int):
    v = get_object_or_404(
        ProductVariant.objects.select_related("product", "product__category"),
        id=variant_id,
    )
    siblings = ProductVariant.objects.filter(
        product=v.product, is_active=True,
    ).exclude(id=v.id)
    return render(request, "store/product_detail.html", {
        "v": v,
        "siblings": siblings,
    })


def _cart_key():
    # แยกจาก POS cart กันชนกัน
    return "shop_cart"


def cart(request):
    cart = request.session.get(_cart_key(), {})  # {"<variant_id>": qty}
    items = []
    total = Decimal("0")

    for vid, qty in cart.items():
        v = get_object_or_404(ProductVariant, id=int(vid))
        qty = int(qty)
        price = _unit_price(v)
        line = price * qty
        total += line
        items.append({"variant": v, "qty": qty, "unit_price": price, "line_total": line})

    return render(request, "store/cart.html", {"items": items, "total": total})


def add_to_cart(request, variant_id: int):
    cart = request.session.get(_cart_key(), {})
    k = str(variant_id)
    cart[k] = int(cart.get(k, 0)) + 1
    request.session[_cart_key()] = cart
    return redirect("store_cart")


def remove_one(request, variant_id: int):
    cart = request.session.get(_cart_key(), {})
    k = str(variant_id)
    if k in cart:
        new_qty = int(cart[k]) - 1
        if new_qty <= 0:
            del cart[k]
        else:
            cart[k] = new_qty
        request.session[_cart_key()] = cart
    return redirect("store_cart")


def clear_cart(request):
    request.session[_cart_key()] = {}
    return redirect("store_cart")


@transaction.atomic
def checkout(request):
    cart = request.session.get(_cart_key(), {})
    if not cart:
        return redirect("store_cart")

    # lock product rows กัน stock เพี้ยน
    variant_ids = [int(k) for k in cart.keys()]
    variants = ProductVariant.objects.select_for_update().filter(id__in=variant_ids)
    vmap = {v.id: v for v in variants}

    items = []
    subtotal = Decimal("0")
    for vid_str, qty in cart.items():
        vid = int(vid_str)
        qty = int(qty)
        v = vmap.get(vid)
        if not v:
            return redirect("store_cart")

        price = _unit_price(v)
        line = price * qty
        subtotal += line
        items.append({"variant": v, "qty": qty, "unit_price": price, "line_total": line})

    discount = Decimal("0")
    grand_total = subtotal - discount

    if request.method == "POST":
        name = (request.POST.get("customer_name") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        address = (request.POST.get("address") or "").strip()
        payment_method = request.POST.get("payment_method", "transfer")

        if not name or not phone:
            return render(request, "store/checkout.html", {
                "items": items, "subtotal": subtotal, "discount": discount, "grand_total": grand_total,
                "error": "กรุณากรอกชื่อและเบอร์โทร",
            })

        # เช็ค stock
        for it in items:
            v = it["variant"]
            if int(v.stock_qty) < int(it["qty"]):
                return render(request, "store/checkout.html", {
                    "items": items, "subtotal": subtotal, "discount": discount, "grand_total": grand_total,
                    "error": f"Stock ไม่พอ: {v.sku} (มี {v.stock_qty})",
                })

        order = WebOrder.objects.create(
            order_no=_make_web_order_no(),
            customer_name=name,
            phone=phone,
            address=address,
            payment_method=payment_method,
            status="WAITING_PAYMENT" if payment_method == "transfer" else "NEW",
            subtotal=subtotal,
            discount=discount,
            grand_total=grand_total,
        )

        # สร้าง items + ตัด stock (เหมือน POS)
        for it in items:
            v = it["variant"]
            qty = int(it["qty"])

            WebOrderItem.objects.create(
                order=order,
                variant=v,
                qty=qty,
                unit_price=it["unit_price"],
                line_total=it["line_total"],
            )

            v.stock_qty = int(v.stock_qty) - qty
            v.save(update_fields=["stock_qty"])

        request.session[_cart_key()] = {}
        return redirect("store_order_success", order_no=order.order_no)

    return render(request, "store/checkout.html", {
        "items": items,
        "subtotal": subtotal,
        "discount": discount,
        "grand_total": grand_total,
    })


def order_success(request, order_no: str):
    order = get_object_or_404(WebOrder, order_no=order_no)
    return render(request, "store/order_success.html", {"order": order})


def confirm_payment(request):
    if request.method == "POST":
        order_no = (request.POST.get("order_no") or "").strip()
        paid_amount = _to_decimal(request.POST.get("paid_amount"))
        bank_name = (request.POST.get("bank_name") or "").strip()
        note = (request.POST.get("note") or "").strip()
        slip = request.FILES.get("slip_image")

        order = WebOrder.objects.filter(order_no=order_no).first()
        if not order:
            return render(request, "store/confirm_payment.html", {"error": "ไม่พบเลขออเดอร์"})

        PaymentConfirmation.objects.create(
            order=order,
            paid_amount=paid_amount,
            bank_name=bank_name,
            note=note,
            slip_image=slip,
        )

        # ปรับสถานะ (แบบง่าย)
        order.status = "PAID"
        order.save(update_fields=["status"])

        return render(request, "store/confirm_payment.html", {"success": f"ยืนยันชำระเงินแล้ว: {order.order_no}"})

    return render(request, "store/confirm_payment.html")
