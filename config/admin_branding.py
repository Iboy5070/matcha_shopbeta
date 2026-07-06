from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from urllib.parse import urlencode

import config.admin_users  # noqa: F401 — custom User admin

admin.site.site_header = f"{settings.SHOP_BRAND} — Admin"
admin.site.site_title = f"{settings.SHOP_BRAND} Admin"
admin.site.index_title = "Admin Dashboard"

_index_view = admin.site.index
_login_view = admin.site.login


def _dashboard_index(request, extra_context=None):
    from config.admin_stats import get_admin_dashboard_stats

    ctx = dict(extra_context or {})
    ctx.update(get_admin_dashboard_stats())
    return _index_view(request, ctx)


def _admin_login(request, extra_context=None):
    """Use the same login page as staff — route by role after sign-in."""
    from config.team_auth import redirect_team_user

    if request.user.is_authenticated and request.user.is_staff:
        next_url = request.GET.get("next") or "/admin/"
        return redirect_team_user(request.user, next_url)

    return _login_view(request, extra_context=extra_context)


admin.site.index = _dashboard_index
admin.site.login = _admin_login

_has_permission = admin.site.has_permission


def _superuser_only_permission(request):
    if not request.user.is_active:
        return False
    if request.user.is_staff and not request.user.is_superuser:
        return False
    return _has_permission(request)


admin.site.has_permission = _superuser_only_permission
