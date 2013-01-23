# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import redirect_to

from ietf.meeting import views

urlpatterns = patterns('sec.meetings.views',
    (r'^(?P<meeting_num>\d+)/materials.html$', views.show_html_materials),
    (r'^agenda/$', views.html_agenda),
    (r'^agenda(?:.html)?$', views.html_agenda),
    (r'^agenda/edit$', views.edit_agenda),
    (r'^requests.html$', redirect_to, {"url": '/meeting/requests', "permanent": True}),
    (r'^requests$', views.meeting_requests),
    (r'^agenda.txt$', views.text_agenda),
    (r'^agenda/agenda.ics$', views.ical_agenda),
    (r'^agenda.ics$', views.ical_agenda),
    (r'^agenda.csv$', views.csv_agenda),
    (r'^agenda/week-view.html$', views.week_view),
    (r'^week-view.html$',        views.week_view),
    (r'^(?P<num>\d+)/agenda(?:.html)?/?$', views.html_agenda),
    (r'^(?P<num>\d+)/agenda/edit$', views.edit_agenda),
    (r'^(?P<num>\d+)/requests.html$', redirect_to, {"url": '/meeting/%(num)s/requests', "permanent": True}),
    (r'^(?P<num>\d+)/requests$',   views.meeting_requests),
    (r'^(?P<num>\d+)/agenda.txt$', views.text_agenda),
    (r'^(?P<num>\d+)/agenda.ics$', views.ical_agenda),
    (r'^(?P<num>\d+)/agenda.csv$', views.csv_agenda),
    (r'^(?P<num>\d+)/week-view.html$', views.week_view),
    (r'^(?P<num>\d+)/agenda/week-view.html$', views.week_view),
    (r'^(?P<num>\d+)/agenda/(?P<session>[A-Za-z0-9-]+)-drafts.pdf$', views.session_draft_pdf),
    (r'^(?P<num>\d+)/agenda/(?P<session>[A-Za-z0-9-]+)-drafts.tgz$', views.session_draft_tarfile),
    (r'^(?P<num>\d+)/agenda/(?P<session>[A-Za-z0-9-]+)/?$', views.session_agenda),
    (r'^$', views.current_materials),

    url(r'^add/$', 'add', name='meetings_add'),
    url(r'^ajax/get-times/(?P<meeting_id>\d{1,6})/(?P<day>\d)/$', 'ajax_get_times', name='meetings_ajax_get_times'),
    url(r'^(?P<meeting_id>\d{1,6})/edit/$', 'edit_meeting', name='meetings_edit_meeting'),
    url(r'^(?P<meeting_id>\d{1,6})/rooms/$', 'rooms', name='meetings_rooms'),
    url(r'^(?P<meeting_id>\d{1,6})/times/$', 'times', name='meetings_times'),
    url(r'^(?P<meeting_id>\d{1,6})/times/delete/(?P<time>[0-9\:]+)/$', 'times_delete', name='meetings_times_delete'),
    url(r'^(?P<meeting_id>\d{1,6})/non_session/$', 'non_session', name='meetings_non_session'),
    url(r'^(?P<meeting_id>\d{1,6})/non_session/edit/(?P<slot_id>\d{1,6})/$', 'non_session_edit', name='meetings_non_session_edit'),
    url(r'^(?P<meeting_id>\d{1,6})/non_session/delete/(?P<slot_id>\d{1,6})/$', 'non_session_delete', name='meetings_non_session_delete'),
    url(r'^(?P<meeting_id>\d{1,6})/select/$', 'select_group',
        name='meetings_select_group'),
    url(r'^(?P<meeting_id>\d{1,6})/(?P<acronym>[A-Za-z0-9_\-\+]+)/schedule/$', 'schedule', name='meetings_schedule'),
    url(r'^(?P<meeting_id>\d{1,6})/(?P<acronym>[A-Za-z0-9_\-\+]+)/remove/$', 'remove_session', name='meetings_remove_session'),
)

