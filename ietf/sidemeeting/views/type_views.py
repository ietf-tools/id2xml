from ietf.sidemeeting.forms import SideMeetingTypeForm
from ietf.sidemeeting.models import SideMeetingType
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django import http

class SideMeetingTypeAddView(CreateView):
    template_name = 'sidemeeting/type_add.html'
    form_class = SideMeetingTypeForm
    success_url = '/sidemeeting/type_list/'    
    model = SideMeetingType

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.slug = self.object.name.lower()
        self.object.save()

        return http.HttpResponseRedirect(self.get_success_url())    

class SideMeetingTypeEditView(UpdateView):
    template_name = 'sidemeeting/type_add.html'
    form_class = SideMeetingTypeForm
    success_url = '/sidemeeting/type_list/'        
    model = SideMeetingType

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.slug = self.object.name.lower()
        self.object.save()

        return http.HttpResponseRedirect(self.get_success_url())    

class SideMeetingTypeDeleteView(DeleteView):
    template_name = 'sidemeeting/type_confirm_delete.html'    
    success_url = '/sidemeeting/type_list/'
    model = SideMeetingType

class SideMeetingTypeListView(ListView):
    context_object_name = 'sidemeetingtypes'
    template_name = 'sidemeeting/type_list.html'
 
    def get_queryset(self):
        return SideMeetingType.objects.all()

class SideMeetingTypeDetailView(DetailView):
    template_name = 'sidemeeting/type_detail.html'
    model = SideMeetingType

    def get_context_data(self, **kwargs):
        context = super(SideMeetingTypeDetailView, self).get_context_data(**kwargs)
        context['field_names'] = ('name')        
        return context

    def get_object(self):
        model = SideMeetingType.objects.get(pk=self.kwargs['slug'])    
    
