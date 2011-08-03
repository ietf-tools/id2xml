from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.views.generic import list_detail

urlpatterns = patterns('',
    (r'^$', 'sec.liaison.views.add_liaison'),
)
