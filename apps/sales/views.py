from datetime import timedelta
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from apps.catalog.models import Product
from apps.store.models import Employee
from .models import Order, OrderItem, Bill, Reserved

@login_required
def pos_view(request):
    q = request.GET.get("q", "").strip()
    products_qs = Product.objects.filter(is_active=True).order_by("name")
    
    if q:
        products_qs = products_qs.filter(Q(name__icontains=q) | Q(slug__icontains=q))

    # Initialize cart
    cart = request.session.get("pos_cart", {})
    
    # Calculate cart total and prepare items for template
    cart_items = []
    total = Decimal("0")
    
    # Fetch all products in cart to avoid N+1
    product_ids = cart.keys()
    cart_products = {str(p.id): p for p in Product.objects.filter(id__in=product_ids)}
    
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

    context = {
        "products": products_qs,
        "cart_items": cart_items,
        "total": total,
        "q": q,
    }
    return render(request, "pos.html", context)


@login_required
def add_to_cart(request, product_id):
    cart = request.session.get("pos_cart", {})
    pid = str(product_id)
    cart[pid] = cart.get(pid, 0) + 1
    request.session["pos_cart"] = cart
    return redirect("pos")


@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get("pos_cart", {})
    pid = str(product_id)
    if pid in cart:
        cart[pid] -= 1
        if cart[pid] <= 0:
            del cart[pid]
    request.session["pos_cart"] = cart
    return redirect("pos")


@login_required
def clear_cart(request):
    request.session["pos_cart"] = {}
    return redirect("pos")


@login_required
@transaction.atomic
def pos_checkout(request):
    if request.method != "POST":
        return redirect("pos")

    cart = request.session.get("pos_cart", {})
    if not cart:
        messages.error(request, "ກະຕ່າສິນຄ້າວ່າງເປົ່າ!")
        return redirect("pos")

    # Get employee
    employee = None
    if hasattr(request.user, "employee_profile"):
        employee = request.user.employee_profile

    # Calculate total
    total = Decimal("0")
    cart_products = {str(p.id): p for p in Product.objects.filter(id__in=cart.keys())}
    
    for pid, qty in cart.items():
        if pid in cart_products:
            total += cart_products[pid].price * qty

    # Create Order
    order = Order.objects.create(
        employee=employee,
        status="COMPLETED"
    )

    # Create Order Items
    for pid, qty in cart.items():
        if pid in cart_products:
            p = cart_products[pid]
            OrderItem.objects.create(
                order=order,
                product=p,
                quantity=qty,
                price=p.price,
                subtotal=p.price * qty
            )
            
    # Create Bill
    Bill.objects.create(
        order=order,
        total_amount=total,
        paid_amount=total,
        status="PAID"
    )

    # Clear cart
    request.session["pos_cart"] = {}
    messages.success(request, f"ຊຳລະເງິນສຳເລັດ! ອໍເດີ #{order.id} ຍອດລວມ {int(total):,} ກີບ")
    return redirect("pos")


def _pos_cart_items(request):
    cart = request.session.get("pos_cart", {})
    cart_products = {str(p.id): p for p in Product.objects.filter(id__in=cart.keys())}
    cart_items = []
    total = Decimal("0")
    for pid, qty in cart.items():
        if pid in cart_products:
            p = cart_products[pid]
            line_total = p.price * qty
            total += line_total
            cart_items.append({"product": p, "qty": qty, "unit_price": p.price, "line_total": line_total})
    return cart_items, total


@login_required
def pos_reserve_form(request):
    cart_items, total = _pos_cart_items(request)
    if not cart_items:
        messages.error(request, "ກະຕ່າສິນຄ້າວ່າງເປົ່າ!")
        return redirect("pos")

    suggested_deposit = (total / 2).quantize(Decimal("1"))
    return render(request, "pos_reserve.html", {
        "cart_items": cart_items,
        "total": total,
        "suggested_deposit": suggested_deposit,
    })


@login_required
@transaction.atomic
def pos_reserve_checkout(request):
    if request.method != "POST":
        return redirect("pos")

    cart_items, total = _pos_cart_items(request)
    if not cart_items:
        messages.error(request, "ກະຕ່າສິນຄ້າວ່າງເປົ່າ!")
        return redirect("pos")

    try:
        deposit = Decimal(request.POST.get("deposit_amount", "0"))
    except InvalidOperation:
        deposit = Decimal("0")
    deposit = max(Decimal("0"), min(deposit, total))

    try:
        expire_days = int(request.POST.get("expire_days", "3"))
    except ValueError:
        expire_days = 3
    expire_days = max(1, min(expire_days, 30))
    expire_at = timezone.now() + timedelta(days=expire_days)

    employee = getattr(request.user, "employee_profile", None)
    order = Order.objects.create(employee=employee, status=Order.Status.RESERVED)

    for item in cart_items:
        p = item["product"]
        qty = item["qty"]
        line_total = item["line_total"]
        OrderItem.objects.create(order=order, product=p, quantity=qty, price=p.price, subtotal=line_total)
        line_deposit = (deposit * line_total / total).quantize(Decimal("0.01")) if total > 0 else Decimal("0")
        Reserved.objects.create(
            order=order,
            product=p,
            quantity=qty,
            deposit_amount=line_deposit,
            remain_amount=(line_total - line_deposit).quantize(Decimal("0.01")),
            status=Reserved.Status.RESERVED,
            expire_at=expire_at,
        )

    Bill.objects.create(
        order=order,
        total_amount=total,
        paid_amount=deposit,
        balance_due=(total - deposit),
        status=Bill.Status.PARTIAL if deposit > 0 else Bill.Status.PENDING,
    )

    request.session["pos_cart"] = {}
    messages.success(
        request,
        f"ຈອງສິນຄ້າສຳເລັດ! ອໍເດີ #{order.id} — ມັດຈຳ {int(deposit):,} ກີບ, ໝົດອາຍຸ {expire_at.strftime('%d/%m/%Y')}",
    )
    return redirect("pos")
