from django import template
from django_dev_toolkit.languages import get_language_info

register = template.Library()


@register.filter
def language_info(lang_code):
    return get_language_info(lang_code)