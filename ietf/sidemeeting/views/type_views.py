from ietf.sidemeeting.forms import SideMeetingSessionTypeNameForm
from ietf.sidemeeting.models import SideMeetingSessionTypeName
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView

class SideMeetingSessionTypeAddView(CreateView):
    template_name = 'sidemeeting/sessiontype_add.html'
    form_class = SideMeetingSessionTypeNameForm
    success_url = '/sidemeeting/sessiontype_list/'    
    model = SideMeetingSessionTypeName

class SideMeetingSessionTypeEditView(UpdateView):
    template_name = 'sidemeeting/sessiontype_add.html'
    form_class = SideMeetingSessionTypeNameForm
    success_url = '/sidemeeting/sessiontype_list/'        
    model = SideMeetingSessionTypeName

class SideMeetingSessionTypeDeleteView(DeleteView):
    template_name = 'sidemeeting/sessiontype_confirm_delete.html'    
    success_url = '/sidemeeting/sessiontype_list/'
    model = SideMeetingSessionTypeName

class SideMeetingSessionTypeListView(ListView):
    context_object_name = 'sidemeetingsessiontypes'
    template_name = 'sidemeeting/sessiontype_list.html'
 
    def get_queryset(self):
        return SideMeetingSessionTypeName.objects.all()

class SideMeetingSessionTypeDetailView(DetailView):
    template_name = 'sidemeeting/sessiontype_detail.html'
    model = SideMeetingSessionTypeName

    def get_context_data(self, **kwargs):
        context = super(SideMeetingSessionTypeDetailView, self).get_context_data(**kwargs)
        context['field_names'] = ('name')        
        return context
