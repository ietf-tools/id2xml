# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls.defaults import patterns
from ietf.idsubmit import views
#from ietf.idsubmit.models import TelechatMinutes
from ietf.idsubmit.models import IdSubmissionDetail, TempIdAuthors

queryset_idsubmit = IdSubmissionDetail.objects.all()
urlpatterns = patterns('django.views.generic.simple',
     (r'^status/$', 'direct_to_template', {'template': 'idsubmit/status.html'}),
     (r'^adjust/$', 'direct_to_template', {'template': 'idsubmit/adjust.html'}),
)

urlpatterns += patterns('',
     (r'^$', views.file_upload),
     (r'^upload/$', views.file_upload),
     (r'^auto_post/', views.trigger_auto_post),
     (r'^adjust/(?P<submission_id_or_name>\d+)/$', views.adjust_form),

     (r'^status/(?P<submission_id>\d+)/cancel_draft/$', views.cancel_draft),
     (r'^status/(?P<submission_id_or_name>\d+)/$', views.draft_status),
     (r'^status/(?P<submission_id>\w.+)$', views.draft_status),
     (r'^manual_post/$', views.manual_post),
     (r'^verify/(?P<submission_id>\d+)/(?P<auth_key>\w+)/$', views.verify_key),
     (r'^verify/(?P<submission_id>\d+)/(?P<auth_key>\w+)/(?P<from_wg_or_sec>(wg|sec))/$', views.verify_key),
)
urlpatterns += patterns('django.views.generic.list_detail',
        (r'^viewfirsttwo/(?P<object_id>\d+)/$', 'object_detail', { 'queryset': queryset_idsubmit, 'template_name':"idsubmit/first_two_pages.html" }),
        (r'^displayidnits/(?P<object_id>\d+)/$', 'object_detail', { 'queryset': queryset_idsubmit, 'template_name':"idsubmit/idnits.html" }),
)
