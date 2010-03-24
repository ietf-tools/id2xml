# Copyright The IETF Trust 2010, All Rights Reserved

from django.conf.urls.defaults import patterns
from ietf.stats import views

urlpatterns = patterns('',
     (r'^rfc/$', views.rfcstats),
     (r'^rfc/(?P<area_or_wg>.*)/$', views.rfcstats),
)
