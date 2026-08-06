import re
import uuid
from pathlib import Path
from urllib import error, request as urlrequest

from django.conf import settings
from django.core.files.storage import default_storage


def supabase_project_url() -> str:
    explicit = (getattr(settings, "SUPABASE_URL", "") or "").strip().rstrip("/")
    if explicit:
        return explicit
    db_url = getattr(settings, "DATABASE_URL", "") or ""
    match = re.search(r"postgres\.([a-z0-9]+)", db_url, re.I)
    if match:
        return f"https://{match.group(1)}.supabase.co"
    return ""


def _save_slip_locally(uploaded_file, order_no: str) -> str:
    """Fallback for local/demo when Supabase Storage is not configured."""
    ext = "jpg"
    if uploaded_file.name and "." in uploaded_file.name:
        ext = uploaded_file.name.rsplit(".", 1)[-1].lower()[:8] or "jpg"
    relative = f"slips/{order_no}/{uuid.uuid4().hex}.{ext}"
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    saved = default_storage.save(relative, uploaded_file)
    return default_storage.url(saved)


def upload_slip_to_supabase(uploaded_file, order_no: str) -> str:
    """Upload slip to Supabase Storage when configured; else local MEDIA.

    Returns a URL string (remote or /media/...) or '' on hard failure.
    """
    base_url = supabase_project_url()
    service_key = (getattr(settings, "SUPABASE_SERVICE_KEY", "") or "").strip()
    bucket = getattr(settings, "SUPABASE_SLIP_BUCKET", "slips")

    if not base_url or not service_key:
        try:
            return _save_slip_locally(uploaded_file, order_no)
        except Exception:
            return ""

    ext = "jpg"
    if uploaded_file.name and "." in uploaded_file.name:
        ext = uploaded_file.name.rsplit(".", 1)[-1].lower()[:8] or "jpg"
    path = f"{order_no}/{uuid.uuid4().hex}.{ext}"
    upload_url = f"{base_url}/storage/v1/object/{bucket}/{path}"

    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    data = uploaded_file.read()
    content_type = getattr(uploaded_file, "content_type", None) or "image/jpeg"
    req = urlrequest.Request(
        upload_url,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {service_key}",
            "apikey": service_key,
            "Content-Type": content_type,
            "x-upsert": "true",
        },
    )
    try:
        with urlrequest.urlopen(req, timeout=30) as resp:
            if resp.status not in (200, 201):
                return _save_slip_locally(uploaded_file, order_no)
    except (error.HTTPError, error.URLError, OSError):
        # Prefer completing checkout locally over hard-failing the customer.
        try:
            return _save_slip_locally(uploaded_file, order_no)
        except Exception:
            return ""

    return f"{base_url}/storage/v1/object/public/{bucket}/{path}"
