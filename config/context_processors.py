from django.conf import settings


def site_context(request):
    """Shop branding, contact channels, and bank transfer details available
    in every template. Without this, {{ shop_brand }}, {{ bank_name }}, etc.
    silently render as empty strings site-wide (Django templates don't error
    on missing context vars) — easy to miss since nothing crashes."""
    return {
        "contact_email": settings.CONTACT_EMAIL,
        "line_url": settings.LINE_URL,
        "whatsapp_url": settings.WHATSAPP_URL,
        "facebook_url": settings.FACEBOOK_URL,
        "bank_name": settings.BANK_NAME,
        "bank_account_number": settings.BANK_ACCOUNT_NUMBER,
        "bank_account_name": settings.BANK_ACCOUNT_NAME,
        "bank_qr_image_url": settings.BANK_QR_IMAGE_URL,
        "site_url": settings.SITE_URL,
        "shop_name": settings.SHOP_NAME,
        "shop_tagline": settings.SHOP_TAGLINE,
        "shop_brand": settings.SHOP_BRAND,
        "wake_page_url": settings.WAKE_PAGE_URL,
        "ga_measurement_id": settings.GA_MEASUREMENT_ID,
        "google_oauth_enabled": bool(
            getattr(settings, "GOOGLE_CLIENT_ID", "") and getattr(settings, "GOOGLE_CLIENT_SECRET", "")
        ),
        # Testimonials/CMS app was removed in the DB rewrite; keep the key so
        # {% if active_testimonials %} guards in templates stay safe.
        "active_testimonials": [],
    }
