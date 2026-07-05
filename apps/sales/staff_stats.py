from django.utils.timezone import now
from django.db.models import Sum
from .models import Order, Bill
from apps.catalog.models import Product

def get_staff_dashboard_stats():
    today = now().date()
    
    # 1. Total sales today
    today_bills = Bill.objects.filter(bill_date__date=today, status="PAID")
    total_sales = today_bills.aggregate(Sum("total_amount"))["total_amount__sum"] or 0
    
    # 2. Total orders today
    total_orders = Order.objects.filter(order_date__date=today).count()
    
    # 3. Active products
    active_products = Product.objects.filter(is_active=True).count()
    
    # 4. Recent orders
    recent_orders = Order.objects.select_related("employee").order_by("-order_date")[:5]

    return {
        "stat_today_sales": int(total_sales),
        "stat_today_orders": total_orders,
        "stat_active_products": active_products,
        "recent_orders": recent_orders,
    }
