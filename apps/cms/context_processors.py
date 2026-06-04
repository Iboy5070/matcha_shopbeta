from django.conf import settings

from apps.cms.models import Testimonial


def site_context(request):
    return {
        "contact_email": settings.CONTACT_EMAIL,
        "line_url": settings.LINE_URL,
        "active_testimonials": Testimonial.objects.filter(is_active=True)[:8],
    }
