from django import template
from ietf.meeting.helpers import get_meeting, can_approve_sidemeeting_request, can_edit_sidemeeting_request, can_request_sidemeeting, can_view_sidemeeting_request

register = template.Library()

@register.simple_tag(takes_context=True)
def can_edit_sidemeeting(context, obj, user):
    return can_edit_sidemeeting_request(obj, user)

@register.simple_tag(takes_context=True)
def can_create_sidemeeting(context, user):
    return can_request_sidemeeting(user)

@register.simple_tag(takes_context=True)
def can_view_sidemeeting(context, obj, user):
    return can_view_sidemeeting_request(obj, user)

@register.simple_tag(takes_context=True)
def can_approve_sidemeeting(context, obj, user):
    return can_approve_sidemeeting_request(obj, user)
