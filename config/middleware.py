from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _


class AdminSuperuserOnlyMiddleware:
    """Block non-superuser staff from every /admin/ URL."""

    ALLOW_PREFIXES = (
        "/admin/logout/",
        "/admin/jsi18n/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        user = request.user

        if path.startswith("/admin/") and not any(path.startswith(p) for p in self.ALLOW_PREFIXES):
            if user.is_authenticated and user.is_staff and not user.is_superuser:
                messages.info(
                    request,
                    _("ພະນັກງານເຂົ້າຜ່ານໜ້າ login ດຽວ — ຈະໄປ Staff portal ອັດຕະໂນມັດ"),
                )
                return redirect("staff_dashboard")
            if user.is_authenticated and not user.is_staff:
                messages.error(request, _("ບັນຊີລູກຄ້າບໍ່ມີສິດເຂົ້າ Admin"))
                return redirect("store_home")

        if path.startswith("/staff/") and path not in ("/staff/login/", "/staff/logout/"):
            if user.is_authenticated and not user.is_staff:
                messages.error(request, _("ບັນຊີລູກຄ້າບໍ່ມີສິດເຂົ້າ Staff portal"))
                return redirect("store_home")

        return self.get_response(request)
