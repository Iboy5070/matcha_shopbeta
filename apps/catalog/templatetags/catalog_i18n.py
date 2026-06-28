from django import template

register = template.Library()


@register.simple_tag
def cat_name(category, lang):
    return category.name_for(lang)


@register.simple_tag
def product_name(product, lang):
    return product.name_for(lang)


@register.simple_tag
def variant_name(variant, lang):
    return variant.display_name_for(lang)


@register.simple_tag
def product_description(product, lang):
    return product.description_for(lang)
