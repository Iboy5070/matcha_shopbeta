from django.conf import settings


def site_context(request):
    try:
        from apps.cms.models import Testimonial
        testimonials = list(Testimonial.objects.filter(is_active=True)[:8])
    except Exception:
        testimonials = []
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
        "active_testimonials": testimonials,
    }
