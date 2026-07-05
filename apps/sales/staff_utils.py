from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def staff_required(view_func):
    @login_required(login_url="/login/")
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            from django.contrib.auth import logout
            logout(request)
            return redirect("store_login")
        return view_func(request, *args, **kwargs)

    return _wrapped
