from django.conf.urls.defaults import *
from ietf.liaisons.models import LiaisonDetail, LiaisonManagers

info_dict = {
    'queryset': LiaisonDetail.objects.all().order_by("-submitted_date"),
}

# there's an opportunity for date-based filtering.
urlpatterns = patterns('django.views.generic.list_detail',
     (r'^$', 'object_list', info_dict),
     (r'^(?P<object_id>\d+)/$', 'object_detail', info_dict),
     (r'^managers/$', 'object_list', { 'queryset': LiaisonManagers.objects.all().select_related().order_by('sdos.sdo_name') }),	#XXX order_by relies on select_related()
)
