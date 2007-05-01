from django.conf.urls.defaults import *
from ietf.ipr import views

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
