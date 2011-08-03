from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to

urlpatterns = patterns('sec.meetings.views',
    url(r'^$', 'main', name='meetings_main'),
    url(r'^add/$', 'add', name='meetings_add'),
    url(r'^(?P<meeting_id>\d{1,6})/add-tutorial/$', 'add_tutorial', name='meetings_add_tutorial'),
    url(r'^(?P<meeting_id>\d{1,6})/$', 'meeting', name='meetings_meeting'),
    url(r'^(?P<meeting_id>\d{1,6})/detail/$', 'meeting_detail', 
        name='meetings_meeting_detail'),
    url(r'^(?P<meeting_id>\d{1,6})/edit/$', 'meeting_edit',
        name='meetings_meeting_edit'),
    url(r'^(?P<meeting_id>\d{1,6})/edit_additional/(?P<type>ack|overview.|future_meeting|irtf)/$',
        'edit_additional', name='meetings_edit_additional'),
    url(r'^(?P<meeting_id>\d{1,6})/new_session/(?P<group_id>-?\d{1,6})$', 'new_session', name='meetings_new_session'),
    url(r'^(?P<meeting_id>\d{1,6})/rooms/$', 'rooms', name='meetings_rooms'),
    url(r'^(?P<meeting_id>\d{1,6})/times/$', 'times', name='meetings_times'),
    url(r'^(?P<meeting_id>\d{1,6})/non_session/$', 'non_session', name='meetings_non_session'),
    url(r'^(?P<meeting_id>\d{1,6})/venue/$', 'venue', name='meetings_venue'),
    url(r'^(?P<meeting_id>\d{1,6})/schedule/$', 'schedule_sessions',
        name='meetings_schedule_sessions'),
    url(r'^(?P<session_id>\d{1,6})/edit_session/$', 'edit_session', name='meetings_edit_session'),
    url(r'^(?P<session_id>\d{1,6})/remove/$', 'remove_session', name='meetings_remove_session'),
)
