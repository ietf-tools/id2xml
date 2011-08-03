from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic import list_detail
from sec.areas import views
from models import Acronym

acronym_info = {
    "queryset" : Acronym.objects.filter(area__status=1),
    # "template_object_name" : "acronym",
}

urlpatterns = patterns('',
    (r'^$', 'sec.areas.views.list_areas'),
    (r'^(?P<id>\d{1,6})/$', 'sec.areas.views.view'),
    (r'^(?P<id>\d{1,6})/edit/$', 'sec.areas.views.edit'),
    (r'^(?P<id>\d{1,6})/people/$', 'sec.areas.views.people'),
    (r'^(?P<id>\d{1,6})/people/modify/$', 'sec.areas.views.modify'),
    (r'^add/$', 'sec.areas.views.add'),
    (r'^getpeople', 'sec.areas.views.getpeople'),
    (r'^list/$', list_detail.object_list, acronym_info),
)
