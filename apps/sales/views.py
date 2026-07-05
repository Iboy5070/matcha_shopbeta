from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from apps.catalog.models import Product
from apps.store.models import Employee
from .models import Order, OrderItem, Bill

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
