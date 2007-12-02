from ietf.wgcharter import views
from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
        (r'^(?P<wgname>[a-z]+)/$',views.current),
        (r'^(?P<wgname>[a-z]+)/all/$',views.list),
        (r'^(?P<wgname>[a-z]+)/add/$',views.add),
        (r'^(?P<wgname>[a-z]+)/(?P<version>\d+)/status/$',views.draft_status),
        (r'^(?P<wgname>[a-z]+)/(?P<version1>\d+|[a-z]+)/(?P<version2>\d+|[a-z]+)/$',views.diff),
        (r'^(?P<wgname>[a-z]+)/(?P<version>\d+|[a-z]+)/$',views.draft),
)

