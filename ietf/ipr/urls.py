from django.conf.urls.defaults import *
from ietf.ipr import views

urlpatterns = patterns('',
     (r'^$', views.default),
     (r'^show/$', views.showlist),
     (r'^show/(?P<ipr_id>\d+)/$', views.show),
     (r'^update/$', views.updatelist),
     (r'^update/(?P<ipr_id>\d+)/$', views.update),
)
