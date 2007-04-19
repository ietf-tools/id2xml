from django.conf.urls.defaults import *
from ietf.idtracker.models import InternetDraft
from ietf.idtracker import views

# lame anyway, gotta deal with rfc
info_dict = {
    'queryset': InternetDraft.objects.all(),
}
info_dict2 = {
    'queryset': InternetDraft.objects.all(),
    'slug_field': 'filename',
}

urlpatterns = patterns('',
     (r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', info_dict),
     (r'^(?P<slug>.+)/$', 'django.views.generic.list_detail.object_detail', info_dict2),
     (r'^(?P<id>\d+)/edit/$', views.edit_idinternal),
     (r'^$', views.search),
)
