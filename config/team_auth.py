from django.shortcuts import redirect


def redirect_team_user(user, next_url: str = ""):
    """Send staff/superuser to the right app after one shared login."""
    next_url = (next_url or "").strip()
    if next_url.startswith("/") and _allowed_next(user, next_url):
        return redirect(next_url)
    if user.is_superuser:
        return redirect("admin:index")
    return redirect("staff_dashboard")


def _allowed_next(user, next_url: str) -> bool:
    if next_url.startswith("/admin/"):
        return user.is_superuser
    if next_url.startswith(("/staff/", "/pos", "/orders")):
        return user.is_staff
    return user.is_staff
