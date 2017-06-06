# -*- coding: utf-8 -*-
"""
These template tags correspond to the meeting helpers 
used to control access to views.   They are used here to 
control which widgets are even visible to be used
"""
from django import template

from ietf.meeting.helpers import can_approve_sidemeeting_request, can_edit_sidemeeting_request, can_request_sidemeeting, can_view_sidemeeting_request


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
