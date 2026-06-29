import re
import uuid
from urllib import error, request as urlrequest

from django.conf import settings


def supabase_project_url() -> str:
    explicit = (getattr(settings, "SUPABASE_URL", "") or "").strip().rstrip("/")
    if explicit:
        return explicit
    db_url = getattr(settings, "DATABASE_URL", "") or ""
    match = re.search(r"postgres\.([a-z0-9]+)", db_url, re.I)
    if match:
        return f"https://{match.group(1)}.supabase.co"
    return ""


def upload_slip_to_supabase(uploaded_file, order_no: str) -> str:
    """Upload slip to Supabase Storage when configured. Returns public URL or ''."""
    base_url = supabase_project_url()
    service_key = (getattr(settings, "SUPABASE_SERVICE_KEY", "") or "").strip()
    bucket = getattr(settings, "SUPABASE_SLIP_BUCKET", "slips")
    if not base_url or not service_key:
        return ""

    ext = "jpg"
    if uploaded_file.name and "." in uploaded_file.name:
        ext = uploaded_file.name.rsplit(".", 1)[-1].lower()[:8] or "jpg"
    path = f"{order_no}/{uuid.uuid4().hex}.{ext}"
    upload_url = f"{base_url}/storage/v1/object/{bucket}/{path}"

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
                return ""
    except error.HTTPError:
        return ""
    except error.URLError:
        return ""

    return f"{base_url}/storage/v1/object/public/{bucket}/{path}"
