from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.filter
def kip(value):
    """49,000 — ອ່ານງ່າຍ, ໃຊ້ທຸກຫນ້າລາຄາ.

    Forces use_l10n=False: Django's intcomma skips digit grouping for
    locales without NUMBER_GROUPING defined (e.g. "lo"), which is this
    site's default language — without this the comma never appeared.
    """
    try:
        return intcomma(int(float(value)), use_l10n=False)
    except (TypeError, ValueError):
        return value


_STATUS_BADGE_MAP = {
    "PENDING": "warning",
    "RESERVED": "info",
    "PARTIAL": "warning",
    "COMPLETED": "success",
    "PAID": "success",
    "CANCELLED": "danger",
}


@register.filter
def status_badge(value):
    """Bootstrap badge color for Order/Bill/Reserved status values."""
    return _STATUS_BADGE_MAP.get(str(value).upper(), "secondary")


@register.simple_tag
def faq_question(item, lang):
    return item.question_for(lang)


@register.simple_tag
def faq_answer(item, lang):
    return item.answer_for(lang)


@register.simple_tag
def testimonial_quote(item, lang):
    return item.quote_for(lang)
