# Copyright The IETF Trust 2007, All Rights Reserved

from django import template
from django.core.cache import cache
from django.template import RequestContext, Context, loader
from django.utils.html import escape
import django.newforms as forms

register = template.Library()

@register.simple_tag
def field_item(form, field_name):
    # the 'form' we get here does not always have fields (when looking at
    # an existing IPR for instance)
    if hasattr(form, "fields"):
        field = form.fields[field_name]
        bf = forms.forms.BoundField(form, field, field_name)
        errors = [escape(error) for error in bf.errors]
        return loader.render_to_string("ipr/formfield.html", { 'field': field, "errors": errors, "help_text": field.help_text })
    else:
        return ""
