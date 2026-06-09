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
        "active_testimonials": testimonials,
    }
