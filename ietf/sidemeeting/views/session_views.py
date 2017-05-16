from ietf.sidemeeting.forms import SideMeetingForm
from ietf.name.models import TimeSlotTypeName, SessionStatusName
from ietf.sidemeeting.models import SideMeetingSession
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views.generic.detail import DetailView    
from django.utils import timezone
from ietf.person.models import Person
from django import http
from ietf.group.models import Group

class SideMeetingAddView(CreateView):
    template_name = 'sidemeeting/add.html'
    form_class = SideMeetingForm
    success_url = '/sidemeeting/list/'    
    model = SideMeetingSession

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.type=TimeSlotTypeName.objects.get(slug="sidemeeting")
        self.object.requested_by = Person.objects.get(user=self.request.user)
        if self.object.meeting in ["IETF", "IRTF", "IAB"]:
            self.object.group = Group.objects.get(name=self.object.meeting)
        else:
            self.object.group = Group.objects.get(acronym="secretariat")

        self.object.save()

        return http.HttpResponseRedirect(self.get_success_url())    

class SideMeetingEditView(UpdateView):
    template_name = 'sidemeeting/add.html'
    form_class = SideMeetingForm
    success_url = '/sidemeeting/list/'        
    model = SideMeetingSession

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.type=TimeSlotTypeName.objects.get(slug="sidemeeting")
        self.object.requested_by = Person.objects.get(user=self.request.user)
        if self.object.meeting in ["IETF", "IRTF", "IAB"]:
            self.object.group = Group.objects.get(name=self.object.meeting)
        else:
            self.object.group = Group.objects.get(acronym="secretariat")


        self.object.save()

        return http.HttpResponseRedirect(self.get_success_url())    
    
class SideMeetingDeleteView(DeleteView):
    template_name = 'sidemeeting/confirm_delete.html'    
    success_url = '/sidemeeting/list/'
    model = SideMeetingSession

class SideMeetingListView(ListView):
    context_object_name = 'sidemeetings'
    template_name = 'sidemeeting/list.html'
 
    def get_queryset(self):
        return SideMeetingSession.objects.all()

class SideMeetingDetailView(DetailView):
    template_name = 'sidemeeting/detail.html'
    model = SideMeetingSession

    def get_context_data(self, **kwargs):
        context = super(SideMeetingDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['field_names'] = ('mtgname', 'name', 'email', 'phone', 'mtg', 'mtgdate', 'altmtgdate', 'days', 'mtgtype', 'addcontact', 'addemail', 'attendance', 'mtgstart', 'mtgend', 'roomconfig', 'speakerphone', 'projector', 'food', 'comments')        
        return context
