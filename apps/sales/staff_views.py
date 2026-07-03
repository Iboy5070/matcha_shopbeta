from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def staff_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("staff_dashboard")

    next_url = request.POST.get("next") or request.GET.get("next") or ""
    error = False

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            if next_url.startswith("/"):
                return redirect(next_url)
            return redirect("staff_dashboard")
        error = True

    return render(request, "staff/login.html", {
        "next": next_url,
        "error": error,
        "form": {"errors": error},
    })


@login_required(login_url="/staff/login/")
def staff_dashboard(request):
    if not request.user.is_staff:
        logout(request)
        return redirect("staff_login")
    return render(request, "staff/dashboard.html")


def staff_logout(request):
    logout(request)
    return redirect("staff_login")
