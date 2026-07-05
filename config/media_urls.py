from django.conf import settings


def resolve_public_url(url: str) -> str:
    """Turn /media/... or CDN URLs into a browser-loadable absolute URL."""
    if not url:
        return ""
    if url.startswith(("http://", "https://")):
        return url
    base = settings.SITE_URL.rstrip("/")
    if url.startswith("/"):
        return f"{base}{url}"
    return f"{base}/{url}"
