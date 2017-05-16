from django.conf.urls import url
from ietf.sidemeeting import views

urlpatterns = [
    # SideMeeting Views
    url(r'^add/$', views.SideMeetingAddView.as_view(), name='side-meeting-add'),
    url(r'^edit/(?P<pk>\d+)$', views.SideMeetingEditView.as_view(), name='side-meeting-edit'),
    url(r'^delete/(?P<pk>\d+)$', views.SideMeetingDeleteView.as_view(), name='side-meeting-delete'),
    url(r'^list/$', views.SideMeetingListView.as_view(), name='side-meeting-list'),
    url(r'^detail/(?P<pk>\d+)/$', views.SideMeetingDetailView.as_view(), name='side-meeting-detail'),        

    # SideMeeting Type Views
    # url(r'^sessiontype_add/$', views.SideTypeAddView.as_view(), name='sidemeeting-type-add'),
    # url(r'^sessiontype_edit/(?P<slug>\S+)$', views.SideTypeEditView.as_view(), name='sidemeeting-type-edit'),
    # url(r'^sessiontype_delete/(?P<slug>\S+)$', views.SideTypeDeleteView.as_view(), name='sidemeeting-type-delete'),
    # url(r'^sessiontype_list/$', views.SideTypeListView.as_view(), name='sidemeeting-type-list'),
    # url(r'^sessiontype_detail/(?P<slug>\S+)/$', views.SideTypeDetailView.as_view(), name='sidemeeting-type-detail'),        
]
