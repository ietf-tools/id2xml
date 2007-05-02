from django import template
from django.utils.html import escape, fix_ampersands
try:
    from email import utils as emailutils
except ImportError:
    from email import Utils as emailutils
import re

register = template.Library()

@register.filter(name='expand_comma')
def expand_comma(value):
    return value.replace(",", ", ")

@register.filter(name='parse_email_list')
def parse_email_list(value):
    addrs = re.split(", ?", value)
    ret = []
    for addr in addrs:
	(name, email) = emailutils.parseaddr(addr)
	if not(name):
	    name = email
	ret.append('<a href="mailto:%s">%s</a>' % ( fix_ampersands(email), escape(name) ))
    return ", ".join(ret)

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

# This replicates the nwg_list.cgi method.
# It'd probably be better to check for the presence of
# a scheme with a better RE.
@register.filter(name='add_scheme')
def add_scheme(value):
    if (re.match('www', value)):
	return "http://" + value
    else:
	return value

@register.filter(name='timesum')
def timesum(value):
    sum = 0.0
    for v in value:
        sum += float(v['time'])
    return sum

@register.filter(name='text_to_html')
def text_to_html(value):
    return "<br>\n".join(escape(value).split("\n"))
