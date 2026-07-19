from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError, transaction
from django.utils.timezone import now

from apps.catalog.models import Category, Product
from apps.sales.models import Customer, Order, OrderItem, Bill

def get_store_cart(request):
    cart = request.session.get("store_cart", {})
    cart_items = []
    total = Decimal("0")
    
    product_ids = cart.keys()
    cart_products = {str(p.id): p for p in Product.objects.filter(id__in=product_ids, is_active=True)}
    
    for pid, qty in cart.items():
        if pid in cart_products:
            p = cart_products[pid]
            line_total = p.price * qty
            total += line_total
            cart_items.append({
                "product": p,
                "qty": qty,
                "unit_price": p.price,
                "line_total": line_total
            })
            
    return cart_items, total

def store_home(request):
    try:
        featured_products = list(Product.objects.filter(is_active=True)[:4])
    except DatabaseError:
        # Avoid hard 500 when Supabase/Render DB is briefly unreachable
        featured_products = []
    return render(request, "store/home.html", {"featured_products": featured_products})

def store_shop(request):
    q = request.GET.get('q')
    cat_slug = request.GET.get('category')
    try:
        products = Product.objects.filter(is_active=True)
        categories = Category.objects.all()
        if q:
            products = products.filter(name__icontains=q)
        if cat_slug:
            products = products.filter(category__slug=cat_slug)
        products = list(products)
        categories = list(categories)
    except DatabaseError:
        products = []
        categories = []

    return render(request, "store/shop.html", {
        "products": products,
        "categories": categories,
        "active_category": cat_slug,
        "q": q or ""
    })

def store_product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return render(request, "store/product_detail.html", {"product": product})

def store_cart(request):
    cart_items, total = get_store_cart(request)
    return render(request, "store/cart.html", {
        "items": cart_items, 
        "total": total
    })

def store_add_to_cart(request, product_id):
    cart = request.session.get("store_cart", {})
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    request.session["store_cart"] = cart
    messages.success(request, "ເພີ່ມລົງກະຕ່າສຳເລັດແລ້ວ")
    return redirect("store_cart")

def store_remove_one(request, product_id):
    cart = request.session.get("store_cart", {})
    pid = str(product_id)
    if pid in cart:
        cart[pid] -= 1
        if cart[pid] <= 0:
            del cart[pid]
    request.session["store_cart"] = cart
    return redirect("store_cart")

def store_clear_cart(request):
    request.session["store_cart"] = {}
    return redirect("store_cart")

RESERVE_DEPOSIT_RATE = Decimal("0.5")
RESERVE_EXPIRE_DAYS = 7


@login_required(login_url="store_login")
@transaction.atomic
def store_checkout(request):
    from datetime import timedelta
    from django.utils import timezone
    from apps.sales.models import Reserved

    cart_items, total = get_store_cart(request)
    if not cart_items:
        messages.error(request, "ກະຕ່າຂອງທ່ານວ່າງເປົ່າ")
        return redirect("store_shop")
        
    if request.method == "POST":
        from apps.catalog.stock import check_stock

        order_type = request.POST.get("order_type", "buy")

        if order_type != "reserve":
            insufficient = check_stock(cart_items)
            if insufficient:
                names = ", ".join(item["product"].name for item in insufficient)
                messages.error(
                    request,
                    f"ສິນຄ້າໝົດ ຫຼື ບໍ່ພຽງພໍ: {names} — ກະລຸນາຫຼຸດຈຳນວນ ຫຼື ເລືອກ 'ຈອງລ່ວງໜ້າ' ແທນ",
                )
                return redirect("store_checkout")

        customer = getattr(request.user, "customer_profile", None)
        if not customer:
            customer = Customer.objects.create(
                user=request.user, 
                cus_name=request.POST.get("customer_name", request.user.first_name),
                cus_last="",
                cus_tel=request.POST.get("phone", ""),
                address=request.POST.get("address", ""),
                gender="-"
            )
        else:
            # Update customer details if they changed
            customer.cus_name = request.POST.get("customer_name", customer.cus_name)
            customer.cus_tel = request.POST.get("phone", customer.cus_tel)
            customer.address = request.POST.get("address", customer.address)
            customer.save()

        is_reserve = order_type == "reserve"
        order = Order.objects.create(
            customer=customer,
            status=Order.Status.RESERVED if is_reserve else Order.Status.PENDING,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["qty"],
                price=item["unit_price"],
                subtotal=item["line_total"]
            )

        if is_reserve:
            deposit_total = (total * RESERVE_DEPOSIT_RATE).quantize(Decimal("1"))
            expire_at = timezone.now() + timedelta(days=RESERVE_EXPIRE_DAYS)
            for item in cart_items:
                line_deposit = (item["line_total"] * RESERVE_DEPOSIT_RATE).quantize(Decimal("0.01"))
                Reserved.objects.create(
                    order=order,
                    product=item["product"],
                    quantity=item["qty"],
                    deposit_amount=line_deposit,
                    remain_amount=(item["line_total"] - line_deposit).quantize(Decimal("0.01")),
                    status=Reserved.Status.RESERVED,
                    expire_at=expire_at,
                )
            bill = Bill.objects.create(
                order=order,
                total_amount=total,
                balance_due=deposit_total,
                status=Bill.Status.PENDING,
            )
            messages.info(
                request,
                f"ຈອງລ່ວງໜ້າ — ກະລຸນາຈ່າຍມັດຈຳ {int(deposit_total):,} ກີບ ພາຍໃນ {RESERVE_EXPIRE_DAYS} ມື້",
            )
        else:
            # Stock is only removed once staff approves the payment slip
            # (see verify_slip) — not at checkout time.
            bill = Bill.objects.create(
                order=order,
                total_amount=total,
                balance_due=total,
                status=Bill.Status.PENDING
            )

        request.session["store_cart"] = {}
        return redirect("store_confirm_payment", order_id=order.id)
        
    from apps.catalog.stock import check_stock

    customer = getattr(request.user, "customer_profile", None)
    customer_name = customer.cus_name if customer else request.user.first_name
    phone = customer.cus_tel if customer else ""
    address = customer.address if customer else ""
    deposit_preview = (total * RESERVE_DEPOSIT_RATE).quantize(Decimal("1"))
    out_of_stock_items = check_stock(cart_items)

    return render(request, "store/checkout.html", {
        "items": cart_items,
        "total": total,
        "customer_name": customer_name,
        "phone": phone,
        "address": address,
        "deposit_preview": deposit_preview,
        "reserve_expire_days": RESERVE_EXPIRE_DAYS,
        "has_out_of_stock": bool(out_of_stock_items),
        "out_of_stock_names": ", ".join(i["product"].name for i in out_of_stock_items),
    })

from decimal import Decimal, InvalidOperation
from django.conf import settings
from apps.sales.models import Payment
from .slip_storage import upload_slip_to_supabase

@login_required(login_url="store_login")
def store_confirm_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)
    
    if request.method == "POST":
        slip_image = request.FILES.get("slip_image")
        paid_amount_str = request.POST.get("paid_amount", "0")
        
        if not slip_image:
            messages.error(request, "ກະລຸນາເລືອກຮູບສະລິບ")
            return redirect("store_confirm_payment", order_id=order.id)
            
        try:
            paid_amount = Decimal(paid_amount_str)
        except InvalidOperation:
            messages.error(request, "ຈຳນວນເງິນບໍ່ຖືກຕ້ອງ")
            return redirect("store_confirm_payment", order_id=order.id)

        public_url = upload_slip_to_supabase(slip_image, f"order_{order.id}")
        if not public_url:
            messages.error(request, "ອັບໂຫຼດຮູບບໍ່ສຳເລັດ — ລະບົບຍັງບໍ່ທັນຕັ້ງຄ່າ ຫຼື ເກີດຂໍ້ຜິດພາດ, ກະລຸນາລອງໃໝ່")
            return redirect("store_confirm_payment", order_id=order.id)

        Payment.objects.create(
            bill=order.bill,
            pay_amount=paid_amount,
            pay_with=Payment.PayWith.TRANSFER,
            slip_url=public_url
        )

        # Record payment on the bill; order stays PENDING until staff verifies
        bill = order.bill
        bill.paid_amount = (bill.paid_amount or Decimal("0")) + paid_amount
        bill.balance_due = max(bill.total_amount - bill.paid_amount, Decimal("0"))
        if bill.paid_amount >= bill.total_amount:
            bill.status = Bill.Status.PAID
        elif bill.paid_amount > 0:
            bill.status = Bill.Status.PARTIAL
        bill.save()

        # Reserved orders stay RESERVED after deposit is paid — staff completes
        # them when the customer picks up and pays the remainder in person.
        if order.status != Order.Status.RESERVED:
            order.status = Order.Status.PENDING
        order.save()

        if order.status == Order.Status.RESERVED:
            messages.success(
                request,
                "ຈ່າຍມັດຈຳສຳເລັດ! ການຈອງຂອງທ່ານຢືນຢັນແລ້ວ — ມາຮັບເຄື່ອງ ແລະ ຊຳລະສ່ວນທີ່ເຫຼືອຢູ່ຮ້ານພາຍໃນກຳນົດ",
            )
        else:
            messages.success(request, "ສະລິບຂອງທ່ານຖືກສົ່ງສຳເລັດແລ້ວ! ທາງຮ້ານຈະກວດສອບ ແລະ ຈັດສົ່ງສິນຄ້າໃຫ້.")
        return redirect("store_home")
        
    return render(request, "store/confirm_payment.html", {
        "order": order,
        "bill": order.bill,
        "prefill_order_no": order.id,
        "prefill_paid_amount": order.bill.balance_due,
        "order_no": order.id,
        "transfer_amount": order.bill.balance_due,
        "is_reserve": order.status == Order.Status.RESERVED,
    })

def store_login(request):
    next_url = request.POST.get("next") or request.GET.get("next") or ""

    if request.user.is_authenticated:
        if next_url.startswith("/"):
            return redirect(next_url)
        return redirect("store_home")

    if request.method == "POST":
        from config.auth_helpers import authenticate_by_identifier

        identifier = (request.POST.get("email") or request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        user = authenticate_by_identifier(request, identifier, password)
        if user is None or not user.is_active:
            messages.error(request, "ອີເມວ/ຊື່ຜູ້ໃຊ້ ຫຼື ລະຫັດຜ່ານບໍ່ຖືກຕ້ອງ")
            return redirect("store_login")

        login(request, user)
        if request.POST.get("remember"):
            request.session.set_expiry(60 * 60 * 24 * 30)
        else:
            request.session.set_expiry(0)

        messages.success(request, "ເຂົ້າສູ່ລະບົບສຳເລັດ")
        if next_url.startswith("/"):
            return redirect(next_url)
        return redirect("store_home")

    return render(request, "store/login.html", {"next": next_url})


def store_register(request):
    from django.contrib.auth import get_user_model
    from .forms import CustomerRegistrationForm

    if request.user.is_authenticated:
        return redirect("store_home")

    User = get_user_model()
    form = CustomerRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data["email"]
        user = User.objects.create_user(
            username=email,
            email=email,
            password=form.cleaned_data["password1"],
            first_name=form.cleaned_data["full_name"],
        )
        Customer.objects.create(
            user=user,
            cus_name=form.cleaned_data["full_name"],
            cus_last="",
            cus_tel=form.cleaned_data["phone"],
            address=form.cleaned_data.get("address", ""),
            gender="-",
        )
        login(request, user)
        messages.success(request, "ລົງທະບຽນສຳເລັດ — ຍິນດີຕ້ອນຮັບ!")
        return redirect("store_home")

    return render(request, "store/register.html", {"form": form})

def store_contact(request):
    return render(request, "store/contact.html")

def store_about(request):
    return render(request, "store/about.html")

def store_blog_list(request):
    return render(request, "store/blog_list.html")

def store_faq(request):
    return render(request, "store/faq.html")

def store_returns(request):
    return render(request, "store/returns.html")

def store_privacy(request):
    return render(request, "store/privacy.html")

def store_google_login(request):
    return redirect("store_home")

def store_logout(request):
    logout(request)
    return redirect("store_home")


@login_required(login_url="store_login")
def store_account(request):
    profile = getattr(request.user, "customer_profile", None)
    orders = Order.objects.filter(customer=profile).order_by("-order_date")[:5] if profile else []
    return render(request, "store/account.html", {
        "profile": profile,
        "orders": orders,
    })


@login_required(login_url="store_login")
def store_account_orders(request):
    profile = getattr(request.user, "customer_profile", None)
    orders = (
        Order.objects.filter(customer=profile)
        .select_related("bill")
        .order_by("-order_date")
        if profile else []
    )
    return render(request, "store/account_orders.html", {"orders": orders})


@login_required(login_url="store_login")
def store_account_edit(request):
    from .forms import CustomerProfileEditForm
    from django.contrib.auth import update_session_auth_hash

    user = request.user
    profile = getattr(user, "customer_profile", None)

    if request.method == "POST":
        form = CustomerProfileEditForm(request.POST, user=user)
        if form.is_valid():
            user.first_name = form.cleaned_data["full_name"]
            user.email = form.cleaned_data["email"]
            if form.cleaned_data.get("password1"):
                user.set_password(form.cleaned_data["password1"])
            user.save()

            if profile is None:
                profile = Customer.objects.create(
                    user=user,
                    cus_name=form.cleaned_data["full_name"],
                    cus_last="",
                    cus_tel=form.cleaned_data["phone"],
                    address=form.cleaned_data.get("address", ""),
                    gender="-",
                )
            else:
                profile.cus_name = form.cleaned_data["full_name"]
                profile.cus_tel = form.cleaned_data["phone"]
                profile.address = form.cleaned_data.get("address", "")
                profile.save()

            if form.cleaned_data.get("password1"):
                update_session_auth_hash(request, user)

            messages.success(request, "ບັນທຶກຂໍ້ມູນສຳເລັດ")
            return redirect("store_account")
    else:
        form = CustomerProfileEditForm(
            user=user,
            initial={
                "full_name": user.first_name or user.get_full_name() or user.username,
                "email": user.email or user.username,
                "phone": profile.cus_tel if profile else "",
                "address": profile.address if profile else "",
            },
        )

    return render(request, "store/account_edit.html", {"form": form})
