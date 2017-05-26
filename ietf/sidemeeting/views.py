from ietf.sidemeeting.forms import SideMeetingForm, SideMeetingApproveForm, FIELD_NAMES, DETAIL_NAMES
from ietf.name.models import TimeSlotTypeName, SessionStatusName
from ietf.sidemeeting.models import SideMeetingSession
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.utils import timezone
from ietf.person.models import Person
from django import http
from ietf.group.models import Group
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from ietf.meeting.helpers import get_meeting, can_approve_sidemeeting_request, can_edit_sidemeeting_request, can_request_sidemeeting, can_view_sidemeeting_request
from django.http import HttpResponseForbidden, Http404
from django.core.exceptions import PermissionDenied



@method_decorator(login_required, name='dispatch')
class SideMeetingAddView(CreateView):
    template_name = 'sidemeeting/add.html'
    form_class = SideMeetingForm
    success_url = '/sidemeeting/list/'
    model = SideMeetingSession

    def dispatch(self, request, *args, **kwargs):
        if not can_request_sidemeeting(request.user):
            raise PermissionDenied
        return super(SideMeetingAddView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SideMeetingAddView, self).get_context_data(**kwargs)
        context['form'].fields['group'].queryset = Group.objects.filter(type='area',state='active')
        context['latest_meeting'] = get_meeting()
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.type=TimeSlotTypeName.objects.get(slug="sidemeeting")
        self.object.status=SessionStatusName(slug="apprw")
        self.object.requested_by = Person.objects.get(user=self.request.user)

        
        if (not form.cleaned_data['group']) or (self.object.meeting.type.name != "IETF"):
            self.object.group = Group.objects.get(acronym="secretariat")

        self.object.save()
        # Saving manytomany fields is tricky.  here is a starting point to see what this is all about
        # https://stackoverflow.com/questions/38448564/forms-modelform-does-not-save-manytomany-fields
        # https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#the-save-method
        form.save_m2m()

        # send notification to secretariat (agenda@ietf.org)        
        send_sidemeeting_approval_request(self.object)
        
        return http.HttpResponseRedirect(self.get_success_url())

@method_decorator(login_required, name='dispatch')
class SideMeetingApproveView(UpdateView):
    template_name = 'sidemeeting/approve.html'
    form_class = SideMeetingApproveForm
    success_url = '/sidemeeting/list/'
    model = SideMeetingSession

    def dispatch(self, request, *args, **kwargs):
        if not can_approve_sidemeeting_request(request.user):
            raise PermissionDenied
        return super(SideMeetingEditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SideMeetingApproveView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['field_names'] = DETAIL_NAMES
        return context

@method_decorator(login_required, name='dispatch')
class SideMeetingEditView(UpdateView):
    template_name = 'sidemeeting/add.html'
    form_class = SideMeetingForm
    success_url = '/sidemeeting/list/'
    model = SideMeetingSession

    def dispatch(self, request, *args, **kwargs):
        if not can_edit_sidemeeting_request(request.user):
            raise PermissionDenied
        return super(SideMeetingEditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SideMeetingEditView, self).get_context_data(**kwargs)
        context['form'].fields['group'].queryset = Group.objects.filter(type='area',state='active')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.type=TimeSlotTypeName.objects.get(slug="sidemeeting")
        self.object.requested_by = Person.objects.get(user=self.request.user)

        if (not form.cleaned_data['group']) or (self.object.meeting.type.name != "IETF"):            
            self.object.group = Group.objects.get(acronym="secretariat")

        self.object.save()
        # Saving manytomany fields is tricky.  here is a starting point to see what this is all about
        # https://stackoverflow.com/questions/38448564/forms-modelform-does-not-save-manytomany-fields
        # https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#the-save-method
        form.save_m2m()

        return http.HttpResponseRedirect(self.get_success_url())

@method_decorator(login_required, name='dispatch')
class SideMeetingDeleteView(DeleteView):
    template_name = 'sidemeeting/confirm_delete.html'
    success_url = '/sidemeeting/list/'
    model = SideMeetingSession

    def dispatch(self, request, *args, **kwargs):
        if not can_edit_sidemeeting_request(request.user):
            raise PermissionDenied
        return super(SideMeetingDeleteView, self).dispatch(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class SideMeetingListView(ListView):
    context_object_name = 'sidemeetings'
    template_name = 'sidemeeting/list.html'

    def dispatch(self, request, *args, **kwargs):
        if not can_request_sidemeeting(request.user):
            raise PermissionDenied
        return super(SideMeetingListView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SideMeetingListView, self).get_context_data(**kwargs)
        return context
    
    def get_queryset(self):
        return SideMeetingSession.objects.all()

@method_decorator(login_required, name='dispatch')
class SideMeetingDetailView(DetailView):
    template_name = 'sidemeeting/detail.html'
    model = SideMeetingSession

    def dispatch(self, request, *args, **kwargs):
        try:
            sidemeeting = SideMeeting.objects.get(pk=self.kwargs['pk'])
        except:
            raise Http404
        if not can_view_sidemeeting_request(sidemeeting, request.user):
            raise PermissionDenied
        return super(SideMeetingDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SideMeetingDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['field_names'] = DETAIL_NAMES
        return context
