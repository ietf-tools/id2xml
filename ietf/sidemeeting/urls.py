from django.conf.urls import url
from ietf.sidemeeting import views

urlpatterns = [
    url(r'add/$', views.SideMeetingAddView.as_view(), name='side-meeting-add'),
    url(r'edit/(?P<pk>\d+)$', views.SideMeetingEditView.as_view(), name='side-meeting-edit'),
    url(r'delete/(?P<pk>\d+)$', views.SideMeetingDeleteView.as_view(), name='side-meeting-delete'),
    url(r'list/$', views.SideMeetingListView.as_view(), name='side-meeting-list'),
    url(r'detail/(?P<pk>\d+)/$', views.SideMeetingDetailView.as_view(), name='side-meeting-detail'),        
    url(r'sessiontype_add/$', views.SideMeetingSessionTypeAddView.as_view(), name='sidemeeting-type-add'),
    url(r'sessiontype_edit/(?P<pk>\d+)$', views.SideMeetingSessionTypeEditView.as_view(), name='sidemeeting-type-edit'),
    url(r'sessiontype_delete/(?P<pk>\d+)$', views.SideMeetingSessionTypeDeleteView.as_view(), name='sidemeeting-type-delete'),
    url(r'sessiontype_list/$', views.SideMeetingSessionTypeListView.as_view(), name='sidemeeting-type-list'),
    url(r'sessiontype_detail/(?P<pk>\d+)/$', views.SideMeetingSessionTypeDetailView.as_view(), name='sidemeeting-type-detail'),        
]
