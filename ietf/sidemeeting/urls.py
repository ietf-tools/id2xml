from django.conf.urls import url
from ietf.sidemeeting.views import SideMeetingAddView, SideMeetingThanksView

urlpatterns = [
    url(r'add/$', SideMeetingAddView.as_view(), name='side-meeting-add'),
    url(r'thanks/$', SideMeetingThanksView.as_view(), name='side-meeting-thanks')    
]
