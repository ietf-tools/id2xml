from ietf.sidemeeting.forms import SideMeetingForm
from ietf.sidemeeting.models import SideMeeting
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView


class SideMeetingAddView(CreateView):
    template_name = 'sidemeeting/add.html'
    form_class = SideMeetingForm
    success_url = '/sidemeeting/thanks/'
    model = SideMeeting

#     def form_valid(self, form):
#         # This method is called when valid form data has been POSTed.
#         # It should return an HttpResponse.
# #        form.send_email()
#         return super(SideMeetingAddView, self).form_valid(form)

class SideMeetingThanksView(TemplateView):
    template_name = 'sidemeeting/thanks.html'    
