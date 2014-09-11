# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls import patterns, url
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy

from ietf.ipr import views, search #new

urlpatterns = patterns('',
     url(r'^$', views.showlist, name='ipr_showlist'),
     (r'^about/$', views.about),
     url(r'^ajax/search/$', views.ajax_search, name='ipr_ajax_search'),
     (r'^by-draft/$', views.iprs_for_drafts_txt),
     url(r'^(?P<id>\d+)/$', views.show, name='ipr_show'),
     url(r'^(?P<id>\d+)/edit/$', views.edit, name='ipr_edit'),
     url(r'^(?P<id>\d+)/history/$', views.history, name='ipr_history'),
     #(r'^update/$', RedirectView.as_view(url=reverse_lazy('ipr_showlist'))),
     #(r'^update/(?P<id>\d+)/$', views.update),
     # update now incorporated in new view
     (r'^new-(?P<type>(specific|generic|third-party))/$', views.new),
     url(r'^search/$', search.search, name="ipr_search"),
)
