from django.conf.urls.defaults import *
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic import list_detail
#from sec.proceedings import views
#from models import Acronym


urlpatterns = patterns('',
    url(r'^$', 'sec.proceedings.views.main', name='proceedings_main'),
    url(r'^(?P<id>\d{1,6})/$', 'sec.proceedings.views.view', name='proceedings_view'),
    url(r'^(?P<meeting_id>\d{1,6})/convert/$', 'sec.proceedings.views.convert', 
        name='proceedings_convert'),
    url(r'^(?P<id>\d{1,6})/(?P<slide_id>\d{1,6})/upload_presentation/$', 
        'sec.proceedings.views.upload_presentation', name='proceedings_upload_presentation'),
    url(r'^(?P<id>\d{1,6})/status/$', 'sec.proceedings.views.status'),
    url(r'^(?P<id>\d{1,6})/status/modify/$', 'sec.proceedings.views.modify'),
    url(r'^(?P<meeting_id>\d{1,6})/select/$', 'sec.proceedings.views.select',
        name='proceedings_select'),
    url(r'^(?P<meeting_id>\d{1,6})/select/(?P<group_id>-?\d{1,6})/$',
        'sec.proceedings.views.upload_unified', name='proceedings_upload_unified'),
    url(r'^delete/(?P<meeting_id>\d{1,6})/(?P<group_id>-?\d{1,6})/(?P<type>(slide|minute|agenda))/(?P<object_id>\d{1,6})/$',
        'sec.proceedings.views.delete_material', name='proceedings_delete_material'),
    url(r'^interim/$', 'sec.proceedings.views.select_interim',
        name='proceedings_select_interim'),
    url(r'^interim/(?P<group_id>-?\d{1,6})/$', 'sec.proceedings.views.interim',
        name='proceedings_interim'),
    url(r'^interim/(?P<meeting_id>\d{1,6})/delete/$',
        'sec.proceedings.views.delete_interim_meeting',
        name='proceedings_delete_interim_meeting'),
    url(r'^(?P<meeting_id>\d{1,6})/(?P<group_id>-?\d{1,6})/(?P<slide_id>\d{1,6})/$',
        'sec.proceedings.views.edit_slide',
        name='proceedings_edit_slide'),
    url(r'^(?P<meeting_id>\d{1,6})/(?P<group_id>-?\d{1,6})/(?P<slide_id>\d{1,6})/replace/$',
        'sec.proceedings.views.replace_slide',
        name='proceedings_replace_slide'),
    url(r'^(?P<meeting_id>\d{1,6})/(?P<group_id>-?\d{1,6})/(?P<slide_id>\d{1,6})/(?P<direction>(up|down))/$',
        'sec.proceedings.views.move_slide', name='proceedings_move_slide'),
)
