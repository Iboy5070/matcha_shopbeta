from functools import wraps

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def staff_required(view_func):
    @login_required(login_url="/staff/login/")
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            logout(request)
            return redirect("staff_login")
        return view_func(request, *args, **kwargs)

    return _wrapped
