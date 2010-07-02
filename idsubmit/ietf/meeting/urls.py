# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls.defaults import patterns
from ietf.meeting import views

urlpatterns = patterns('',
    (r'^request/(?P<group_id>\d+)/$', views.schedule_group),
    (r'^request/$', views.show_schedule),
    (r'^(?P<meeting_num>\d+)/materials.html$', views.show_html_materials),
    (r'^agenda/$', views.html_agenda),
    (r'^agenda.html$', views.html_agenda),
    (r'^agenda.txt$', views.text_agenda),
    (r'^(?P<num>\d+)/agenda.html$', views.html_agenda),
    (r'^(?P<num>\d+)/agenda.txt$', views.text_agenda),
    (r'^$', views.current_materials),
)

