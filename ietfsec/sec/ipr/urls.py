from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template, redirect_to
import sec.ipr.views


urlpatterns = patterns(
    '',
    (r'^$', redirect_to, {'url': 'admin/'}),
    url(r'^admin/?$', 'sec.ipr.views.admin_list', name="ipr_admin_list"),
    url(r'^admin/detail/(?P<ipr_id>\d+)/?$', 'sec.ipr.views.admin_detail', name="ipr_admin_detail"),
    url(r'^admin/create/?$', 'sec.ipr.views.admin_create', name="ipr_admin_create"),
    url(r'^admin/update/(?P<ipr_id>\d+)/?$', 'sec.ipr.views.admin_update', name="ipr_admin_update"),
    url(r'^admin/notify/(?P<ipr_id>\d+)/?$', 'sec.ipr.views.admin_notify', name="ipr_admin_notify"),
    url(r'^admin/old_submitter_notify/(?P<ipr_id>\d+)/?$', 'sec.ipr.views.old_submitter_notify', name="ipr_old_submitter_notify"),
    url(r'^admin/post/(?P<ipr_id>\d+)/?$', 'sec.ipr.views.admin_post', name="ipr_admin_post"),
    url(r'^admin/delete/(?P<ipr_id>\d+)/?$', 'sec.ipr.views.admin_delete', name="ipr_admin_delete"),
    url(r'^ajax/rfc_num/?$', 'sec.ipr.views.ajax_rfc_num', name="ipr_ajax_rfc_num"),
    url(r'^ajax/internet_draft/?$', 'sec.ipr.views.ajax_internet_draft', name="ipr_ajax_internet_draft"),
   
)








