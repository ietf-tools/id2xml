from django import template
from django.utils.html import escape
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
