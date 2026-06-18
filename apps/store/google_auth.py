import json
import secrets
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from django.urls import reverse

from .models import CustomerProfile

User = get_user_model()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def google_oauth_enabled():
    return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)


def _redirect_uri(request):
    return request.build_absolute_uri(reverse("store_google_callback"))


def _post_json(url, data):
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def _get_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def google_login_start(request):
    if not google_oauth_enabled():
        return redirect("store_login")

    state = secrets.token_urlsafe(32)
    request.session["google_oauth_state"] = state
    request.session["google_oauth_next"] = request.GET.get("next", "")

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": _redirect_uri(request),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
    }
    return redirect(f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}")


def google_login_callback(request):
    if not google_oauth_enabled():
        return redirect("store_login")

    error = request.GET.get("error")
    if error:
        return redirect("store_login")

    state = request.GET.get("state", "")
    if not state or state != request.session.pop("google_oauth_state", None):
        return redirect("store_login")

    code = request.GET.get("code")
    if not code:
        return redirect("store_login")

    try:
        token_data = _post_json(
            GOOGLE_TOKEN_URL,
            {
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": _redirect_uri(request),
                "grant_type": "authorization_code",
            },
        )
        access_token = token_data.get("access_token")
        if not access_token:
            return redirect("store_login")

        profile = _get_json(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    except (urllib.error.URLError, json.JSONDecodeError, KeyError):
        return redirect("store_login")

    email = (profile.get("email") or "").strip().lower()
    if not email:
        return redirect("store_login")

    name = profile.get("name") or email.split("@")[0]
    user = User.objects.filter(username=email).first()
    if user is None:
        user = User.objects.create_user(
            username=email,
            email=email,
            password=User.objects.make_random_password(length=32),
            first_name=name,
        )
        CustomerProfile.objects.create(user=user, phone="")

    login(request, user)
    next_path = request.session.pop("google_oauth_next", "") or reverse("store_home")
    if next_path.startswith("/"):
        return redirect(next_path)
    return redirect("store_home")
