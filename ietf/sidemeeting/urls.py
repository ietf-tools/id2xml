from django.conf.urls import url
from ietf.sidemeeting.views import SideMeetingAddView, SideMeetingThanksView, SideMeetingListView, SideMeetingDetailView

urlpatterns = [
    url(r'add/$', SideMeetingAddView.as_view(), name='side-meeting-add'),
    url(r'list/$', SideMeetingListView.as_view(), name='side-meeting-list'),
    url(r'^detail/(?P<pk>[0-9]+)/$', SideMeetingDetailView.as_view(), name='side-meeting-detail'),        
    url(r'thanks/$', SideMeetingThanksView.as_view(), name='side-meeting-thanks')    
]
