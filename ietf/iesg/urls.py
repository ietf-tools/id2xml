from django.conf.urls.defaults import *
from ietf.iesg.models import TelechatMinutes


#urlpatterns = patterns('django.views.generic.list_detail',
#     (r'^lastcall/$', 'object_list', {
#	     'queryset': InternetDraft.objects.all() }),
#)

telechat = {
    'queryset': TelechatMinutes.objects.all(),
    'date_field': 'telechat_date',
}
telechat2 = telechat.copy()
telechat2.update({
    'allow_empty': True,
})


urlpatterns = patterns('django.views.generic.date_based',
	(r'^telechat/$', 'archive_index', telechat2),
	(r'^telechat/(?P<year>\d{4})/$', 'archive_year', telechat2),
	(r'^telechat/(?P<year>\d{4})/(?P<month>[a-z]{3})/$', 'archive_month', telechat2),
	(r'^telechat/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\d+)/(?P<object_id>\d+)/$', 'object_detail', telechat),
)
