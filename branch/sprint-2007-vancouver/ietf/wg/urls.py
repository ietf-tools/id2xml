# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls.defaults import patterns
from ietf.wg import views

urlpatterns = patterns('',
    (r'^approval.html$', views.index),
)

