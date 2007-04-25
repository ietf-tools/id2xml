from django import template
from django.utils.html import escape, fix_ampersands
import re

register = template.Library()

@register.filter(name='expand_comma')
def expand_comma(value):
    return value.replace(",", ", ")

@register.filter(name='parse_email_list')
def parse_email_list(value):
    # parse_email_list from GEN_UTIL.pm
    return escape(value)

# there's an "ahref -> a href" in GEN_UTIL
# but let's wait until we understand what that's for.
@register.filter(name='make_one_per_line')
def make_one_per_line(value):
    return re.sub(", ?", "\n", value)

@register.filter(name='link_if_url')
def link_if_url(value):
    if (re.match('(https?|mailto):', value)):
	return "<a href=\"%s\">%s</a>" % ( fix_ampersands(value), escape(value) )
    else:
	return escape(value)

@register.filter(name='add_scheme')
def add_scheme(value):
    if (re.match('www', value)):
	return "http://" + value
    else:
	return value
