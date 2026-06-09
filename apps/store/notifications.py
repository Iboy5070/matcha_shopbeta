import logging
from urllib import parse, request as urlrequest

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def notify_shop(subject: str, body: str) -> None:
    """ແຈ້ງຮ້ານເມື່ອມີອໍເດີ/ສລິບ/ຂໍ້ຄວາມ (email + LINE Notify ຖ້າຕັ້ງ env)."""
    email = getattr(settings, "NOTIFY_EMAIL", "") or settings.CONTACT_EMAIL
    if email:
        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception:
            logger.exception("shop email notify failed")

    token = getattr(settings, "LINE_NOTIFY_TOKEN", "")
    if not token:
        return
    try:
        data = parse.urlencode({"message": f"{subject}\n{body}"}).encode()
        req = urlrequest.Request(
            "https://notify-api.line.me/api/notify",
            data=data,
            headers={"Authorization": f"Bearer {token}"},
            method="POST",
        )
        urlrequest.urlopen(req, timeout=10)
    except Exception:
        logger.exception("LINE Notify failed")
