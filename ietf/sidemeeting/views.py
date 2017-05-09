from ietf.sidemeeting.forms import SideMeetingForm
from ietf.sidemeeting.models import SideMeeting
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView    
from django.utils import timezone

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

    # generic view to fetch the data then show in a list
    
class SideMeetingListView(ListView):
    
    # a name to refer to the object_list(to be used in the index.html)
    context_object_name = 'sidemeetings'
    template_name = 'sidemeeting/list.html'
 
    def get_queryset(self):
        return SideMeeting.objects.all()

class SideMeetingDetailView(DetailView):
    template_name = 'sidemeeting/detail.html'
    model = SideMeeting

    def get_context_data(self, **kwargs):
        context = super(SideMeetingDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['field_names'] = ('mtgname', 'name', 'email', 'phone', 'mtg', 'mtgdate', 'altmtgdate', 'days', 'mtgtype', 'addcontact', 'addemail', 'attendance', 'mtgstart', 'mtgend', 'roomconfig', 'speakerphone', 'projector', 'food', 'comments')        
        return context
