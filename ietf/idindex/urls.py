from django.conf.urls.defaults import *
from ietf.idtracker.models import InternetDraft
from ietf.idindex import views
from ietf.idindex import forms

info_dict = {
    'queryset': InternetDraft.objects.all(),
    'template_name': 'idindex/internetdraft_detail.html',
}
info_dict2 = info_dict
info_dict2.update({
    'slug_field': 'filename',
})

urlpatterns = patterns('',
     (r'^wgdocs/(?P<id>\d+)/$', views.wgdocs),
     (r'^wgdocs/(?P<slug>[^/]+)/$', views.wgdocs),
     (r'^wglist/(?P<wg>[^/]+)/$', views.wglist),
     (r'^inddocs/(?P<filter>[^/]+)/$', views.inddocs),
     (r'^otherdocs/(?P<cat>[^/]+)/$', views.otherdocs),
     (r'^showdocs/(?P<cat>[^/]+)/((?P<sortby>[^/]+)/)?$', views.showdocs),
     (r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', info_dict),
     (r'^(?P<slug>[^/]+)/$', 'django.views.generic.list_detail.object_detail', info_dict2),
     (r'^$', views.search),
)
