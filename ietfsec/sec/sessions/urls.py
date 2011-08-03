from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to
from forms import SessionForm

urlpatterns = patterns('',
    url(r'^$', 'sec.sessions.views.main', name='sessions_main'),
    url(r'^status/$', 'sec.sessions.views.tool_status', name='sessions_tool_status'),
    url(r'^(?P<session_id>\d{1,6})/$', 'sec.sessions.views.view', name='sessions_view'),
    url(r'^(?P<session_id>\d{1,6})/cancel/$', 'sec.sessions.views.cancel', name='sessions_cancel'),
    url(r'^(?P<session_id>\d{1,6})/edit/$', 'sec.sessions.views.edit', name='sessions_edit'),
    url(r'^new/(?P<group_id>\d{1,6})/$', 'sec.sessions.views.new', name='sessions_new'),
    url(r'^new/(?P<group_id>\d{1,6})/no_session/$', 'sec.sessions.views.no_session', name='sessions_no_session'),
    url(r'^new/(?P<group_id>\d{1,6})/confirm/$', 'sec.sessions.views.confirm', name='sessions_confirm'),
)
