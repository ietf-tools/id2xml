from ietf.wgcharter import views
from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
        (r'^(?P<wgname>[a-z0-9]+)/$',views.current),
        (r'^(?P<wgname>[a-z0-9]+)/all/$',views.list),
        (r'^(?P<wgname>[a-z0-9]+)/fake/$',views.fake_wg),
        (r'^(?P<wgname>[a-z0-9]+)/add/$',views.add),
        (r'^(?P<wgname>[a-z0-9]+)/(?P<version>\d+)/status/$',views.draft_status),
        (r'^(?P<wgname>[a-z0-9]+)/(?P<version1>\d+|[a-z]+)/(?P<version2>\d+|[a-z]+)/$',views.diff),
        (r'^(?P<wgname>[a-z0-9]+)/(?P<version>\d+|[a-z]+)/$',views.draft),
)

