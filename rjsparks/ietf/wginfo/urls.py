# Copyright The IETF Trust 2008, All Rights Reserved

from django.conf.urls.defaults import patterns
from ietf.wginfo import views

urlpatterns = patterns('',
     (r'^$', views.wg_dir),
     (r'^summary.txt', views.wg_summary_area),
     (r'^summary-by-area.txt', views.wg_summary_area),
     (r'^summary-by-acronym.txt', views.wg_summary_acronym),
     (r'^1wg-charters.txt', views.wg_charters),
     (r'^1wg-charters-by-acronym.txt', views.wg_charters_by_acronym),
)
