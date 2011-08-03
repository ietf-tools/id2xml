from django.conf.urls.defaults import *
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template, redirect_to
from django.views.generic import list_detail
from sec.roles import views


urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': 'iesg/'}),
    (r'^iesg/$', 'sec.roles.views.iesg'),
    (r'^liaisons/$', 'sec.roles.views.liaisons'),
    url(r'^(?P<type>iab|ietf|nomcom)/$', 'sec.roles.views.chair', name='roles_chair'),
)
