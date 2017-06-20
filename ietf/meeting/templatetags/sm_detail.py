# -*- coding: utf-8 -*-
from django import template


register = template.Library()

# display the resources field as a comma separated string
# in the form
@register.simple_tag
def get_field_value(obj, name):
    if name=="resources":
        m2m = getattr(obj, name)
        return ', '.join([x.desc for x in m2m.all()])
    return getattr(obj, name)
