# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls.defaults import patterns
from ietf.meeting import views

urlpatterns = patterns('',
    (r'^request/(?P<group_id>\d+)/$', views.schedule_group),
    (r'^request/$', views.show_schedule),
    (r'^(?P<meeting_num>\d+)/agenda.(?P<html_or_txt>\S+)$', views.show_html_agenda),
    (r'^(?P<meeting_num>\d+)/materials.html$', views.show_html_materials),
)

