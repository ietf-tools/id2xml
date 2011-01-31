from django.conf.urls.defaults import *
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic import list_detail
from sec.proceedings import views
#from models import Acronym


urlpatterns = patterns('',
    (r'^$', 'sec.proceedings.views.list'),
    (r'^(?P<id>\d{1,6})/$', 'sec.proceedings.views.view'),
    (r'^add/$', 'sec.proceedings.views.add'),
    (r'^(?P<id>\d{1,6})/edit/$', 'sec.proceedings.views.edit'),
    url(r'^(?P<id>\d{1,6})/(?P<menu>group|training|irtf|interim|/)$', 'sec.proceedings.views.upload_group'),
#    url(r'^(?P<id>\d{1,6})/(?P<menu>group|training|irtf|interim|)/(?P<group_acronym_id>\d{1,6})/convert_material/$', 'sec.proceedings.views.current_material'),
    url(r'^(?P<id>\d{1,6})/(?P<acronym_id>\d{1,6})/(?P<menu>group|training|irtf|interim|)/current_material/$', 'sec.proceedings.views.current_material'),
#    url(r'^(?P<id>\d{1,6})/(?P<menu>group|training|irtf|interim|)/(?P<wg_id>\d{1,6})/$', 'sec.proceedings.views.delete_file'),
    url(r'^(?P<id>\d{1,6})/(?P<menu>group|training|irtf|interim|)/(?P<wg_id>\d{1,6})/(?P<min_id>\d{1,6})/(?P<slide_id>\d{1,6})/$', 'sec.proceedings.views.delete_file'),
    (r'^(?P<id>\d{1,6})/convert/$', 'sec.proceedings.views.convert'),
    url(r'^(?P<id>\d{1,6})/(?P<slide_id>\d{1,6})/upload_presentation/$', 'sec.proceedings.views.upload_presentation'),
    (r'^(?P<id>\d{1,6})/status/$', 'sec.proceedings.views.status'),
    (r'^(?P<id>\d{1,6})/status/modify/$', 'sec.proceedings.views.modify'),

)


