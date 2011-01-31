from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.views.generic import list_detail
from sec.groups import views

urlpatterns = patterns('',
    url(r'^$', 'sec.groups.views.search', name='groups_search'),
    url(r'^add/$', 'sec.groups.views.add', name='groups_add'),
    url(r'^(?P<id>\d{1,6})/$', 'sec.groups.views.view', name='groups_view'),
    url(r'^(?P<id>\d{1,6})/description/$', 'sec.groups.views.description', name='groups_description'),
    url(r'^(?P<id>\d{1,6})/edit/$', 'sec.groups.views.edit', name='groups_edit'),
    url(r'^(?P<id>\d{1,6})/gm/$', 'sec.groups.views.view_gm', name='groups_view_gm'),
    url(r'^(?P<id>\d{1,6})/gm/edit/$', 'sec.groups.views.edit_gm', name='groups_edit_gm'),
    url(r'^(?P<id>\d{1,6})/people/$', 'sec.groups.views.people', name='groups_people'),
    url(r'^(?P<id>\d{1,6})/people/delete/$', 'sec.groups.views.delete', name='groups_people_delete'),
    (r'^get_ads/$', 'sec.groups.views.get_ads'),
    (r'^list/(?P<id>\d{1,6})/$', 'sec.groups.views.grouplist'),
    (r'^search/$', 'sec.groups.views.search'),
)
