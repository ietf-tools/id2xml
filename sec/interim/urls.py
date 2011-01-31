from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'sec.interim.views.dashboard'),
    url(r'^group/(?P<group_id>\d+)/$', 'sec.interim.views.group', name='interim_group'),
    url(r'^meeting/(?P<meeting_id>\d+)/$', 'sec.interim.views.meeting', name='interim_meeting'),
    url(r'^slide/(?P<slide_id>\d+)/$', 'sec.interim.views.slide', name='interim_slide'),
    url(r'^slide/(?P<slide_id>\d+)/(?P<direction>(up|down))/$', 'sec.interim.views.move_slide', name='interim_move_slide'),
)
