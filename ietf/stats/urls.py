from django.conf.urls import patterns, url


urlpatterns = patterns('ietf.stats.views',
    url(r'^$', 'index', name='stats_index'),
    url(r'^docevents/$', 'docevents', name='stats_docevents'),
)
