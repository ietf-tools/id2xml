# Copyright The IETF Trust 2008, All Rights Reserved

from django.conf.urls.defaults import patterns
from ietf.wginfo import views

urlpatterns = patterns('',
     (r'^summary-by-acronym.txt', views.wg_summary_acronym),
     (r'^summary-by-area.txt', views.wg_summary_area),
     (r'^wg-dir.html', views.wg_dir),
)
