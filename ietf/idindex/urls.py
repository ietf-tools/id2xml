from django.conf.urls.defaults import *
from ietf.idtracker.models import InternetDraft
from ietf.idindex import views

# lame
info_dict = {
    'queryset': InternetDraft.objects.all(),
}
info_dict2 = {
    'queryset': InternetDraft.objects.all(),
    'slug_field': 'filename',
    'template_name': 'idindex/internetdraft_detail.html',
}

urlpatterns = patterns('',
     (r'^(?P<object_id>\d+)/$', 'django.views.generic.list_detail.object_detail', info_dict),
     (r'^(?P<slug>.+)/$', 'django.views.generic.list_detail.object_detail', info_dict2),
#     (r'^$', views.search),
)
