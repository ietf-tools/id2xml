from django.conf.urls.defaults import *
from ietf.ipr import views

urlpatterns = patterns('',
     (r'^$', views.default),
     (r'^update/', views.update),
)
