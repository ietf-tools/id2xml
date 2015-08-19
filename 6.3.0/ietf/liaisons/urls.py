# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls import patterns, url
from django.views.generic import RedirectView, TemplateView

urlpatterns = patterns('',
    (r'^help/$', TemplateView.as_view(template_name='liaisons/help.html')),
    url(r'^help/fields/$', TemplateView.as_view(template_name='liaisons/field_help.html'), name="liaisons_field_help"),
    (r'^help/from_ietf/$', TemplateView.as_view(template_name='liaisons/guide_from_ietf.html')),
    (r'^help/to_ietf/$', TemplateView.as_view(template_name='liaisons/guide_to_ietf.html')),
    (r'^managers/$', RedirectView.as_view(url='https://www.ietf.org/liaison/managers.html')),
)

# AJAX views
urlpatterns += patterns('ietf.liaisons.views',
    url(r'^ajax/get_info/$', 'ajax_get_liaison_info', name='ajax_get_liaison_info'),
    url(r'^ajax/select2search/$', 'ajax_select2_search_liaison_statements', name='ajax_select2_search_liaison_statements'),
    #url(r'^ajax/select2search_groups/(?P<group_type>(internal|external))/$', 'ajax_select2_search_groups', name='ajax_select2_search_groups'),
    url(r'^ajax/liaison_list/$', 'ajax_liaison_list', name='ajax_liaison_list'),
)

urlpatterns += patterns('ietf.liaisons.views',
    url(r'^$', 'liaison_list', name='liaison_list'),
    url(r'^(?P<state>(|posted|pending|dead))/$', 'liaison_list', name='liaison_list'),
    url(r'^(?P<object_id>\d+)/$', 'liaison_detail', name='liaison_detail'),
    url(r'^(?P<object_id>\d+)/edit/$', 'liaison_edit', name='liaison_edit'),
    url(r'^(?P<object_id>\d+)/edit-attachment/(?P<doc_id>[A-Za-z0-9._+-]+)$', 'liaison_edit_attachment', name='liaison_edit_attachment'),
    url(r'^(?P<object_id>\d+)/delete-attachment/(?P<attach_id>[A-Za-z0-9._+-]+)$', 'liaison_delete_attachment', name='liaison_delete_attachment'),
    url(r'^(?P<object_id>\d+)/history/$', 'liaison_history', name='liaison_history'),
    url(r'^(?P<object_id>\d+)/resend/$', 'liaison_resend', name='liaison_resend'),
    #url(r'^dead/$', 'liaison_dead_list', name='liaison_dead_list'),
    url(r'^add/$', 'add_liaison', name='add_liaison'),
    url(r'^add/(?P<type>(incoming|outgoing))/$', 'add_liaison', name='liaison_add'),
    #url(r'^for_approval/$', 'liaison_approval_list', name='liaison_approval_list'),
    #url(r'^for_approval/(?P<object_id>\d+)/$', 'liaison_approval_detail', name='liaison_approval_detail'),
    #url(r'^search/$', 'liaison_search', name='liaison_search'),
)