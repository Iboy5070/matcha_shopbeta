from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def staff_required(view_func):
    """Require authenticated staff (POS + staff portal helpers)."""

    @login_required(login_url="/login/")
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            from django.contrib import messages
            from django.contrib.auth import logout

            messages.error(request, "ບັນຊີລູກຄ້າບໍ່ມີສິດເຂົ້າ POS / Staff")
            logout(request)
            return redirect("/login/?next=/pos/")
        return view_func(request, *args, **kwargs)

    return _wrapped
