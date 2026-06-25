from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()


@register.filter
def kip(value):
    """49,000 — ອ່ານງ່າຍ, ໃຊ້ທຸກຫນ້າລາຄາ."""
    try:
        return intcomma(int(float(value)))
    except (TypeError, ValueError):
        return value


@register.simple_tag
def faq_question(item, lang):
    return item.question_for(lang)


@register.simple_tag
def faq_answer(item, lang):
    return item.answer_for(lang)


@register.simple_tag
def testimonial_quote(item, lang):
    return item.quote_for(lang)
