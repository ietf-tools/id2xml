from ietf.sidemeeting.forms import SideMeetingTypeNameForm
from ietf.sidemeeting.models import SideMeetingTypeName
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django import http

class SideMeetingTypeNameAddView(CreateView):
    template_name = 'sidemeeting/type_add.html'
    form_class = SideMeetingTypeNameForm
    success_url = '/sidemeeting/type_list/'    
    model = SideMeetingTypeName

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.slug = self.object.name.lower()
        self.object.save()

        return http.HttpResponseRedirect(self.get_success_url())    

class SideMeetingTypeNameEditView(UpdateView):
    template_name = 'sidemeeting/type_add.html'
    form_class = SideMeetingTypeNameForm
    success_url = '/sidemeeting/type_list/'        
    model = SideMeetingTypeName

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.slug = self.object.name.lower()
        self.object.save()

        return http.HttpResponseRedirect(self.get_success_url())    

class SideMeetingTypeNameDeleteView(DeleteView):
    template_name = 'sidemeeting/type_confirm_delete.html'    
    success_url = '/sidemeeting/type_list/'
    model = SideMeetingTypeName

class SideMeetingTypeNameListView(ListView):
    context_object_name = 'sidemeetingtypes'
    template_name = 'sidemeeting/type_list.html'
 
    def get_queryset(self):
        return SideMeetingTypeName.objects.all()

class SideMeetingTypeNameDetailView(DetailView):
    template_name = 'sidemeeting/type_detail.html'
    model = SideMeetingTypeName

    def get_context_data(self, **kwargs):
        context = super(SideMeetingTypeNameDetailView, self).get_context_data(**kwargs)
        context['field_names'] = ('name')        
        return context

    def get_object(self):
        model = SideMeetingTypeName.objects.get(pk=self.kwargs['slug'])    
    
