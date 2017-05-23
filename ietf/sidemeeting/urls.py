from django.conf.urls import url, handler403
from ietf.sidemeeting import views

urlpatterns = [
    # SideMeeting Views
    url(r'^add/$', views.SideMeetingAddView.as_view(), name='side-meeting-add'),
    url(r'^approve/(?P<pk>\d+)/$', views.SideMeetingApproveView.as_view(), name='side-meeting-approve'),    
    url(r'^edit/(?P<pk>\d+)/$', views.SideMeetingEditView.as_view(), name='side-meeting-edit'),
    url(r'^delete/(?P<pk>\d+)/$', views.SideMeetingDeleteView.as_view(), name='side-meeting-delete'),
    url(r'^list/$', views.SideMeetingListView.as_view(), name='side-meeting-list'),
    url(r'^detail/(?P<pk>\d+)/$', views.SideMeetingDetailView.as_view(), name='side-meeting-detail'),        

#    SideMeeting Type Views
    url(r'^type_add/$', views.SideMeetingTypeNameAddView.as_view(), name='sidemeeting-type-add'),
    url(r'^type_edit/(?P<slug>[\w-]+)/$', views.SideMeetingTypeNameEditView.as_view(), name='sidemeeting-type-edit'),
    url(r'^type_delete/(?P<slug>[\w-]+)/$', views.SideMeetingTypeNameDeleteView.as_view(), name='sidemeeting-type-delete'),
    url(r'^type_list/$', views.SideMeetingTypeNameListView.as_view(), name='sidemeeting-type-list'),
    url(r'^type_detail/(?P<slug>\S+)/$', views.SideMeetingTypeNameDetailView.as_view(), name='sidemeeting-type-detail'),        
]
