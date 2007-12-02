from ietf.wgcharter import views
from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
        (r'^(?P<wgname>[a-z0-9]+)/$',views.current),
        (r'^(?P<wgname>[a-z0-9]+)/all/$',views.list),
        (r'^(?P<wgname>[a-z0-9]+)/fake/$',views.fake_wg),
        (r'^(?P<wgname>[a-z0-9]+)/add/$',views.add),
        (r'^(?P<wgname>[a-z0-9]+)/(?P<version>\d+)/diff/$',views.diff1),
        (r'^(?P<wgname>[a-z0-9]+)/(?P<version>\d+)/status/$',views.draft_status),
        (r'^(?P<wgname>[a-z0-9]+)/(?P<version1>\d+)/(?P<version2>\d+)/$',views.diff),
        (r'^(?P<wgname>[a-z0-9]+)/(?P<version>\d+)/$',views.draft),
)

