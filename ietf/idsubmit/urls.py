# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls.defaults import patterns
from ietf.idsubmit import views
from ietf.idsubmit.models import IdSubmissionDetail, TempIdAuthors

queryset_idsubmit = IdSubmissionDetail.objects.all()
idsubmit_dict = {
    'queryset': queryset_idsubmit,
}
urlpatterns = patterns('django.views.generic.list_detail',
        (r'^viewfirsttwo/(?P<object_id>\d+)/$', 'object_detail', { 'queryset': queryset_idsubmit, 'template_name':"idsubmit/first_two_pages.html" }),
        (r'^displayidnits/(?P<object_id>\d+)/$', 'object_detail', { 'queryset': queryset_idsubmit, 'template_name':"idsubmit/idnits.html" }),
)
urlpatterns += patterns('',
     (r'^$', views.file_upload),
     (r'^upload/$', views.file_upload),
     (r'^auto_post/(?P<submission_id>\d+)/$', views.trigger_auto_post, idsubmit_dict),
     (r'^adjust/(?P<submission_id>\d+)/$', views.adjust_form, idsubmit_dict),
     (r'^cancel/(?P<submission_id>\d+)/$', views.cancel_draft),
     (r'^status/(?P<slug>[^/]+)/$', views.draft_status, idsubmit_dict),
     (r'^status/$', views.draft_status, idsubmit_dict),
     (r'^verify/(?P<submission_id>\d+)/(?P<auth_key>\w+)/$', views.verify_key),
     (r'^verify/(?P<submission_id>\d+)/(?P<auth_key>\w+)/(?P<from_wg_or_sec>(wg|sec))/$', views.verify_key),
)
