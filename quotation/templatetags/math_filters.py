from django import template

register = template.Library()

@register.filter
def multiplyFloats(value1, value2):
    try:
        return float(value1) * float(value2)
    except:
        return ''