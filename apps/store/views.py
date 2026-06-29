from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from apps.catalog.models import Category, Product, ProductVariant
from apps.cms.models import ContactMessage, FAQItem
from .forms import CustomerLoginForm, CustomerRegistrationForm
from .models import CustomerProfile, WebOrder, WebOrderItem, PaymentConfirmation
from .notifications import notify_shop

User = get_user_model()


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


def _customer_defaults(request):
    """Prefill checkout from logged-in customer profile."""
    if not request.user.is_authenticated:
        return {}
    profile = getattr(request.user, "customer_profile", None)
    if not profile:
        return {}
    return {
        "customer_name": request.user.get_full_name() or request.user.username,
        "phone": profile.phone,
        "address": profile.address,
    }


def register(request):
    if request.user.is_authenticated:
        return redirect("store_home")

    form = CustomerRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        user = User.objects.create_user(
            username=email,
            email=email,
            password=form.cleaned_data["password1"],
            first_name=form.cleaned_data["full_name"],
        )
        CustomerProfile.objects.create(
            user=user,
            phone=form.cleaned_data["phone"],
            address=form.cleaned_data.get("address", ""),
        )
        login(request, user)
        messages.success(request, "ລົງທະບຽນສຳເລັດ — ຍິນດີຕ້ອນຮັບ!")
        return redirect("store_home")

    return render(request, "store/register.html", {"form": form})


def customer_login(request):
    if request.user.is_authenticated:
        return redirect("store_home")

    next_url = request.POST.get("next") or request.GET.get("next") or ""

    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""
        user = authenticate(request, username=email, password=password)
        if user is None:
            messages.error(request, "ອີເມວ ຫຼື ລະຫັດຜ່ານບໍ່ຖືກຕ້ອງ")
            if next_url.startswith("/"):
                return redirect(next_url)
            return redirect("store_home")
        login(request, user)
        if request.POST.get("remember"):
            request.session.set_expiry(60 * 60 * 24 * 30)
        else:
            request.session.set_expiry(0)
        messages.success(request, "ເຂົ້າສູ່ລະບົບສຳເລັດ")
        if next_url.startswith("/"):
            return redirect(next_url)
        return redirect("store_home")

    form = CustomerLoginForm()
    return render(request, "store/login.html", {"form": form, "next": next_url})


def customer_logout(request):
    logout(request)
    messages.info(request, "ອອກຈາກລະບົບແລ້ວ")
    return redirect("store_home")


@login_required(login_url="store_login")
def account(request):
    profile = getattr(request.user, "customer_profile", None)
    orders = WebOrder.objects.filter(phone=profile.phone).order_by("-created_at")[:10] if profile else []
    return render(request, "store/account.html", {
        "profile": profile,
        "orders": orders,
    })


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
                "error": "ກະລຸນາໃສ່ຊື່ ແລະ ຂໍ້ຄວາມ",
            })
        ContactMessage.objects.create(
            name=name, email=email, phone=phone, message=message,
        )
        notify_shop(
            f"[{settings.SHOP_BRAND}] ຂໍ້ຄວາມໃໝ່",
            f"ຊື່: {name}\nໂທ: {phone}\nEmail: {email}\n\n{message}",
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
    try:
        add_qty = int(request.POST.get("qty") or request.GET.get("qty") or 1)
    except (TypeError, ValueError):
        add_qty = 1
    add_qty = max(1, min(add_qty, 99))
    cart[k] = int(cart.get(k, 0)) + add_qty
    request.session[_cart_key()] = cart
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url == "detail":
        return redirect("store_product_detail", variant_id=variant_id)
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
                "error": "ກະລຸນາໃສ່ຊື່ ແລະ ເບີໂທ",
                "customer_name": name, "phone": phone, "address": address,
            })

        # เช็ค stock
        for it in items:
            v = it["variant"]
            if int(v.stock_qty) < int(it["qty"]):
                return render(request, "store/checkout.html", {
                    "items": items, "subtotal": subtotal, "discount": discount, "grand_total": grand_total,
                    "error": f"ສິນຄ້າບໍ່ພໍ: {v.display_name} (ຄົງ {v.stock_qty})",
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

        notify_shop(
            f"[{settings.SHOP_BRAND}] ອໍເດີໃໝ່ {order.order_no}",
            f"ຊື່: {name}\nໂທ: {phone}\nລວມ: {grand_total} ກີບ\nຊຳລະ: {payment_method}\nAdmin: /admin/store/weborder/",
        )

        request.session[_cart_key()] = {}
        return redirect("store_order_success", order_no=order.order_no)

    return render(request, "store/checkout.html", {
        "items": items,
        "subtotal": subtotal,
        "discount": discount,
        "grand_total": grand_total,
        **_customer_defaults(request),
    })


def order_success(request, order_no: str):
    order = get_object_or_404(WebOrder, order_no=order_no)
    slip_confirmation = order.payment_confirmations.order_by("-created_at").first()
    slip_success = request.GET.get("slip") == "ok"
    slip_error = request.session.pop("slip_error", None)
    slip_already = order.payment_confirmations.exists()
    return render(request, "store/order_success.html", {
        "order": order,
        "slip_confirmation": slip_confirmation,
        "slip_success": slip_success,
        "slip_error": slip_error,
        "slip_already": slip_already,
    })


def _redirect_slip_error(request, order_no: str, message: str):
    request.session["slip_error"] = message
    return redirect(reverse("store_order_success", kwargs={"order_no": order_no}))


def confirm_payment(request):
    if request.method == "POST":
        order_no = (request.POST.get("order_no") or "").strip()
        paid_amount = _to_decimal(request.POST.get("paid_amount"))
        bank_name = (request.POST.get("bank_name") or settings.BANK_NAME or "").strip()
        note = (request.POST.get("note") or "").strip()
        slip = request.FILES.get("slip_image")

        ctx = {
            "prefill_order_no": order_no,
            "prefill_paid_amount": (request.POST.get("paid_amount") or "").strip(),
            "prefill_bank_name": bank_name,
        }

        if not slip:
            if order_no:
                return _redirect_slip_error(request, order_no, "ກະລຸນາແນບຮູບສลິບໂອນເງິນ")
            return render(request, "store/confirm_payment.html", {
                **ctx,
                "error": "ກະລຸນາແນບຮູບສลິບໂອນເງິນ",
            })

        order = WebOrder.objects.filter(order_no=order_no).first()
        if not order:
            return render(request, "store/confirm_payment.html", {
                **ctx,
                "error": "ບໍ່ພົບເລກອໍເດີ",
            })

        if order.status in ("PAID", "SHIPPING", "DONE"):
            if order_no:
                return _redirect_slip_error(request, order_no, "ອໍເດີນີ້ຊຳລະແລ້ວ")
            return render(request, "store/confirm_payment.html", {
                **ctx,
                "error": "ອໍເດີນີ້ຊຳລະແລ້ວ",
            })

        if order.payment_confirmations.exists():
            if order_no:
                return redirect(reverse("store_order_success", kwargs={"order_no": order_no}) + "?slip=ok")
            return render(request, "store/confirm_payment.html", {
                **ctx,
                "error": "ແຈ້ງຊຳລະອໍເດີນີ້ແລ້ວ — ລໍກວດຈາກຮ້ານ",
            })

        amount_note = ""
        if paid_amount and paid_amount != order.grand_total:
            amount_note = f" (ລູກຄ້າແຈ້ງ {paid_amount}, ຍອດອໍເດີ {order.grand_total})"

        PaymentConfirmation.objects.create(
            order=order,
            paid_amount=paid_amount or order.grand_total,
            bank_name=bank_name,
            note=note,
            slip_image=slip,
        )

        order.status = "PAYMENT_REVIEW"
        order.save(update_fields=["status"])

        notify_shop(
            f"[{settings.SHOP_BRAND}] ແຈ້ງໂອນ {order.order_no}",
            (
                f"ຊື່: {order.customer_name}\n"
                f"ໂທ: {order.phone}\n"
                f"ຈຳນວນ: {paid_amount} ກີບ{amount_note}\n"
                f"ທະນາຄານ: {bank_name}\n"
                f"ໝາຍເຫດ: {note}\n"
                f"Admin → Payment confirmations / Web orders → ປ່ຽນເປັນ PAID"
            ),
        )

        return redirect(reverse("store_order_success", kwargs={"order_no": order.order_no}) + "?slip=ok")

    return render(request, "store/confirm_payment.html", {
        "prefill_order_no": (request.GET.get("order_no") or "").strip(),
        "prefill_paid_amount": (request.GET.get("paid_amount") or "").strip(),
        "prefill_bank_name": settings.BANK_NAME,
    })


def blog_list(request):
    return render(request, "store/blog_list.html")
