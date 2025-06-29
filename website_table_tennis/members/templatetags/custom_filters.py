from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    """
    Mengurangkan arg dari value.
    Usage: {{ value|subtract:arg }}
    """
    try:
        return value - arg
    except (TypeError, ValueError):
        return 0
