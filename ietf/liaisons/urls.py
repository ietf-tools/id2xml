from django.conf.urls.defaults import *
from ietf.liaisons.models import LiaisonDetail

info_dict = {
    'queryset': LiaisonDetail.objects.all().order_by("-submitted_date"),
}

# there's an opportunity for date-based filtering.
urlpatterns = patterns('django.views.generic.list_detail',
     (r'^$', 'object_list', info_dict),
     (r'^(?P<object_id>\d+)/$', 'object_detail', info_dict),
)
