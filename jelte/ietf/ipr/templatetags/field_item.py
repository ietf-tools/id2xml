# Copyright The IETF Trust 2007, All Rights Reserved

from django import template
from django.core.cache import cache
from django.template import RequestContext, Context, loader

register = template.Library()

@register.simple_tag
def field_item(form, field_name):
    # the 'form' we get here does not always have fields (when looking at
    # an existing IPR for instance)
    if hasattr(form, "fields"):
        return loader.render_to_string("ipr/formfield.html", { 'field': form.fields[field_name] })
    else:
        return ""
