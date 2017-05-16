from ietf.sidemeeting.forms import SideTypeNameForm
from ietf.sidemeeting.models import SideTypeName
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView, ListView
from django.views.generic.detail import DetailView
from django import http

class SideTypeAddView(CreateView):
    template_name = 'sidemeeting/sessiontype_add.html'
    form_class = SideTypeNameForm
    success_url = '/sidemeeting/sessiontype_list/'    
    model = SideTypeName

    def form_valid(self, form):
        self.object = form.save(commit=False)
        import ipdb;ipdb.set_trace()
        self.object.slug = self.object.name.lower()
        self.object.save()

        return http.HttpResponseRedirect(self.get_success_url())    

class SideTypeEditView(UpdateView):
    template_name = 'sidemeeting/sessiontype_add.html'
    form_class = SideTypeNameForm
    success_url = '/sidemeeting/sessiontype_list/'        
    model = SideTypeName

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.slug = self.object.name.lower()
        self.object.save()

        return http.HttpResponseRedirect(self.get_success_url())    

class SideTypeDeleteView(DeleteView):
    template_name = 'sidemeeting/sessiontype_confirm_delete.html'    
    success_url = '/sidemeeting/sessiontype_list/'
    model = SideTypeName

class SideTypeListView(ListView):
    context_object_name = 'sidemeetingsessiontypes'
    template_name = 'sidemeeting/sessiontype_list.html'
 
    def get_queryset(self):
        return SideTypeName.objects.all()

class SideTypeDetailView(DetailView):
    template_name = 'sidemeeting/sessiontype_detail.html'
    model = SideTypeName

    def get_context_data(self, **kwargs):
        context = super(SideTypeDetailView, self).get_context_data(**kwargs)
        context['field_names'] = ('name')        
        return context
