from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template
from django.views.generic import list_detail
from sec.rolodex import views
from models import PersonOrOrgInfo

person_detail_info = {
    "queryset" : PersonOrOrgInfo.objects.all(),
    "template_object_name" : "person",
}

urlpatterns = patterns('',
    (r'^$', 'sec.rolodex.views.search'),
    (r'^add/$', 'sec.rolodex.views.add'),
    url(r'^add-confirm/$', direct_to_template, {'template': 'rolodex/add_confirm.html'}, name='rolodex_add_confirm'),
    (r'^add-proceed/$', 'sec.rolodex.views.add_proceed'),
    (r'^(?P<tag>\d{1,6})/bulk-update/$', 'sec.rolodex.views.bulk_update'),
    (r'^(?P<tag>\d{1,6})/edit/$', 'sec.rolodex.views.edit'),
    (r'^(?P<tag>\d{1,6})/delete/$', 'sec.rolodex.views.delete'),
    (r'^(?P<tag>\d{1,6})/$', 'sec.rolodex.views.view'),
)
