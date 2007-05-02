from django.conf.urls.defaults import *
from ietf.ipr import models, views

urlpatterns = patterns('',
     (r'^$', views.default),
     (r'^show/$', views.showlist),
     (r'^show/(?P<ipr_id>\d+)/$', views.show),
     (r'^update/$', views.updatelist),
     (r'^update/(?P<ipr_id>\d+)/$', views.update),
     (r'^new/$', views.new),
     (r'^new/specific/$', views.new_specific),
     (r'^new/generic/$', views.new_generic),
     (r'^new/third-party/$', views.new_thirdpty),
)

queryset = models.IprDetail.objects.all()
archive = {'queryset':queryset, 'date_field': 'submitted_date', 'allow_empty':True }

urlpatterns += patterns('django.views.generic.date_based',
	(r'^date/$', 'archive_index', archive),
	(r'^date/(?P<year>\d{4})/$', 'archive_year', archive),
	(r'^date/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'archive_month', archive),
)


