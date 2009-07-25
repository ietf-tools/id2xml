# Copyright The IETF Trust 2007, All Rights Reserved

from django import template
from django.core.cache import cache
from django.template import RequestContext, Context, loader

register = template.Library()

@register.simple_tag
def field_item(menu_field):
    return loader.render_to_string("ipr/formfield.html", { 'field': menu_field })
