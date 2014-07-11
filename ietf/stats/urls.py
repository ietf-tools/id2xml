from django.conf.urls import patterns, url


urlpatterns = patterns('ietf.stats.views',
    url(r'^$', 'index', name='stats_index'),
    url(r'^docevents/(?P<doctype>[a-zA-Z0-9-._]+)$', 'docevents', name='stats_docevents'),
    url(r'^docevents/(?P<doctype>[a-zA-Z0-9-._]+)/(?P<weeks>[1-9][0-9]*)$', 'docevents', name='stats_docevents'),
)
