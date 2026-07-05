from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.timezone import now

from apps.catalog.models import Product
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
    featured_products = Product.objects.filter(is_active=True)[:4]
    return render(request, "store/home.html", {"featured_products": featured_products})

from apps.catalog.models import Product, Category

def store_shop(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    
    q = request.GET.get('q')
    if q:
        products = products.filter(name__icontains=q)
        
    cat_slug = request.GET.get('category')
    if cat_slug:
        products = products.filter(category__slug=cat_slug)
        
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

@login_required(login_url="store_login")
@transaction.atomic
def store_checkout(request):
    cart_items, total = get_store_cart(request)
    if not cart_items:
        messages.error(request, "ກະຕ່າຂອງທ່ານວ່າງເປົ່າ")
        return redirect("store_shop")
        
    if request.method == "POST":
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
            
        order = Order.objects.create(
            customer=customer,
            status="PENDING"
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["qty"],
                price=item["unit_price"],
                subtotal=item["line_total"]
            )
            
        bill = Bill.objects.create(
            order=order,
            total_amount=total,
            balance_due=total,
            status="UNPAID"
        )
        
        request.session["store_cart"] = {}
        return redirect("store_confirm_payment", order_id=order.id)
        
    customer = getattr(request.user, "customer_profile", None)
    customer_name = customer.cus_name if customer else request.user.first_name
    phone = customer.cus_tel if customer else ""
    address = customer.address if customer else ""
    
    return render(request, "store/checkout.html", {
        "items": cart_items,
        "total": total,
        "customer_name": customer_name,
        "phone": phone,
        "address": address,
    })

import uuid
from decimal import Decimal, InvalidOperation
from supabase import create_client, Client
from django.conf import settings
from apps.sales.models import Payment

@login_required(login_url="store_login")
def store_confirm_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)
    
    if request.method == "POST":
        slip_image = request.FILES.get("slip_image")
        bank_name = request.POST.get("bank_name", "Transfer")
        paid_amount_str = request.POST.get("paid_amount", "0")
        
        if not slip_image:
            messages.error(request, "ກະລຸນາເລືອກຮູບສະລິບ")
            return redirect("store_confirm_payment", order_id=order.id)
            
        try:
            paid_amount = Decimal(paid_amount_str)
        except InvalidOperation:
            messages.error(request, "ຈຳນວນເງິນບໍ່ຖືກຕ້ອງ")
            return redirect("store_confirm_payment", order_id=order.id)
            
        # Upload to Supabase
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY:
            try:
                supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
                
                # Get file extension
                ext = slip_image.name.split('.')[-1] if '.' in slip_image.name else 'jpg'
                filename = f"order_{order.id}_{uuid.uuid4().hex[:8]}.{ext}"
                
                # Upload file
                res = supabase.storage.from_(settings.SUPABASE_SLIP_BUCKET).upload(
                    filename, 
                    slip_image.read(), 
                    {"content-type": slip_image.content_type}
                )
                
                # Get public URL
                public_url = supabase.storage.from_(settings.SUPABASE_SLIP_BUCKET).get_public_url(filename)
                
                # Create Payment record
                Payment.objects.create(
                    bill=order.bill,
                    pay_amount=paid_amount,
                    pay_with=bank_name,
                    slip_url=public_url
                )
                
                # Update Order Status
                order.status = "WAITING_CONFIRMATION"
                order.save()
                
                messages.success(request, "ສະລິບຂອງທ່ານຖືກສົ່ງສຳເລັດແລ້ວ! ທາງຮ້ານຈະກວດສອບ ແລະ ຈັດສົ່ງສິນຄ້າໃຫ້.")
                return redirect("store_home")
                
            except Exception as e:
                messages.error(request, f"ເກີດຂໍ້ຜິດພາດໃນການອັບໂຫຼດຮູບ: {str(e)}")
                return redirect("store_confirm_payment", order_id=order.id)
        else:
            messages.error(request, "ລະບົບຍັງບໍ່ທັນຕັ້ງຄ່າບ່ອນເກັບຮູບ (Supabase)")
            return redirect("store_confirm_payment", order_id=order.id)
        
    return render(request, "store/confirm_payment.html", {
        "order": order,
        "bill": order.bill,
        "prefill_order_no": order.id,
        "prefill_paid_amount": order.bill.balance_due,
    })

def store_login(request):
    if request.user.is_authenticated:
        return redirect("store_home")
    
    if request.method == "POST":
        # Simplified for demo:
        return redirect("store_home")
        
    return render(request, "store/login.html")

def store_register(request):
    if request.method == "POST":
        return redirect("store_home")
    return render(request, "store/register.html")

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
