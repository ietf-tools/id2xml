from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': 'manage/'}),
    #url(r'^$', 'sec.interim.views.list', name='interim_list'),
    url(r'^list_(?P<order_by>(date|group))/$', 'sec.interim.views.view', name='interim_list'),
    url(r'^manage/$', 'sec.interim.views.manage', name='interim_manage'),
    url(r'^group/(?P<group_id>\d+)/$', 'sec.interim.views.group', name='interim_group'),
    url(r'^meeting/(?P<meeting_id>\d+)/$', 'sec.interim.views.meeting', name='interim_meeting'),
    url(r'^meeting/(?P<meeting_id>\d+)/delete/$', 'sec.interim.views.delete_meeting', name='interim_delete_meeting'),
    url(r'^slide/(?P<slide_id>\d+)/$', 'sec.interim.views.slide', name='interim_slide'),
    url(r'^slide/(?P<slide_id>\d+)/(?P<direction>(up|down))/$', 'sec.interim.views.move_slide', name='interim_move_slide'),
    url(r'^slide/(?P<slide_id>\d+)/delete/$', 'sec.interim.views.delete_slide', name='interim_delete_slide'),
)
