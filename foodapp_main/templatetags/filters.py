from django import template
import locale

register = template.Library()


@register.filter("currency")
def currency(value):
    return locale.currency(val=value)