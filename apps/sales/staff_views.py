from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from urllib.parse import urlencode


def staff_login(request):
    """Redirect to admin login since store_login is removed."""
    next_url = request.GET.get("next") or request.POST.get("next") or "/staff/"
    query = urlencode({"next": next_url})
    return redirect(f"/admin/login/?{query}")


@login_required(login_url="/admin/login/")
def staff_dashboard(request):
    from django.contrib.auth import logout

    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        logout(request)
        return redirect("/admin/login/")
        
    from .staff_stats import get_staff_dashboard_stats

    return render(request, "staff/dashboard.html", {
        "staff_section": "home",
        **get_staff_dashboard_stats(),
    })


def staff_logout(request):
    from django.contrib.auth import logout

    logout(request)
    return redirect("/pos/")

@login_required(login_url="/admin/login/")
def staff_slips(request):
    from .models import Order
    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/admin/login/")
        
    # Get orders that are PENDING and have a bill with a payment that has a slip_url
    pending_orders = Order.objects.filter(
        status="PENDING",
        bill__payments__slip_url__isnull=False
    ).exclude(bill__payments__slip_url="").distinct().order_by("-order_date")
    
    return render(request, "staff/slips.html", {
        "staff_section": "slips",
        "pending_orders": pending_orders,
    })

@login_required(login_url="/admin/login/")
def verify_slip(request, order_id):
    from .models import Order
    from django.contrib import messages
    
    if not request.user.is_staff and not hasattr(request.user, "employee_profile"):
        return redirect("/admin/login/")
        
    if request.method == "POST":
        order = Order.objects.get(id=order_id)
        action = request.POST.get("action")
        
        if action == "approve":
            order.status = "PAID"
            order.save()
            if hasattr(order, "bill"):
                order.bill.status = "PAID"
                order.bill.save()
            messages.success(request, f"Order #{order.id} approved successfully!")
        elif action == "reject":
            # For reject, we might keep it PENDING but maybe clear the slip or mark as rejected
            order.status = "REJECTED"
            order.save()
            messages.warning(request, f"Order #{order.id} payment rejected.")
            
    return redirect("staff_slips")
