"""Stats for the admin dashboard hub."""

from __future__ import annotations

from apps.sales.staff_stats import get_staff_dashboard_stats


def get_admin_dashboard_stats() -> dict:
    from apps.catalog.models import Category, Product
    from django.contrib.auth import get_user_model

    User = get_user_model()
    base = get_staff_dashboard_stats()

    return {
        **base,
        "product_count": Product.objects.count(),
        "category_count": Category.objects.count(),
        "staff_users": User.objects.filter(is_staff=True, is_superuser=False).count(),
        "admin_users": User.objects.filter(is_superuser=True).count(),
    }
