# -*- coding: utf-8 -*-
from django import http
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from ietf.group.models import Group
from ietf.meeting.helpers import get_meeting, can_approve_sidemeeting_request, can_edit_sidemeeting_request, can_request_sidemeeting, can_view_sidemeeting_request, send_sidemeeting_approval_request
from ietf.meeting.models import Meeting
from ietf.name.models import TimeSlotTypeName, SessionStatusName
from ietf.person.models import Person
from ietf.sidemeeting.forms import SideMeetingForm, SideMeetingApproveForm, DETAIL_NAMES
from ietf.sidemeeting.models import SideMeetingSession


@method_decorator(login_required, name='dispatch')
class SideMeetingAddView(CreateView):
    """
    Create a new Side Meeting
    """
    template_name = 'sidemeeting/add.html'
    form_class = SideMeetingForm
    success_url = '/sidemeeting/list/'
    model = SideMeetingSession

    def dispatch(self, request, *args, **kwargs):
        # make sure the user has permissions to create
        if not can_request_sidemeeting(request.user):
            raise PermissionDenied
        return super(SideMeetingAddView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SideMeetingAddView, self).get_context_data(**kwargs)
        # filter out the Group objects available
        context['form'].fields['group'].queryset = Group.objects.filter(type='area',state='active')
        # identify the latest meeting to show first in the template
        context['latest_meeting'] = get_meeting()
        # filter out the interim meetings
        context['form'].fields['meeting'].queryset = Meeting.objects.exclude(number__icontains='interim')
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # force the type field to be a "sidemeeting" type
        self.object.type=TimeSlotTypeName.objects.get(slug="sidemeeting")
        # set the initial status to waiting for approval
        self.object.status=SessionStatusName(slug="apprw")
        # set the requested_by field to a Person object
        self.object.requested_by = Person.objects.get(user=self.request.user)

        # set the group to Secretariat for non-IETF meeting types
        if (not form.cleaned_data['group']) or (self.object.meeting.type.name != "IETF"):
            self.object.group = Group.objects.get(acronym="secretariat")

        self.object.save()
        # Saving manytomany fields is tricky.  here is a starting point to see what this is all about
        # https://stackoverflow.com/questions/38448564/forms-modelform-does-not-save-manytomany-fields
        # https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#the-save-method
        form.save_m2m()

        # send a notification to secretariat (agenda@ietf.org)        
        send_sidemeeting_approval_request(self.object)
        
        return http.HttpResponseRedirect(self.get_success_url())

@method_decorator(login_required, name='dispatch')
class SideMeetingApproveView(UpdateView):
    """
    Update a new Side Meeting
    """    
    template_name = 'sidemeeting/approve.html'
    form_class = SideMeetingApproveForm
    success_url = '/sidemeeting/list/'
    model = SideMeetingSession

    def dispatch(self, request, *args, **kwargs):
        sidemeeting = self.get_object()
        # make sure the user has permissions to approve
        if not can_approve_sidemeeting_request(sidemeeting, request.user):
            raise PermissionDenied
        return super(SideMeetingApproveView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SideMeetingApproveView, self).get_context_data(**kwargs)
        # used for listing details
        context['field_names'] = DETAIL_NAMES
        return context

@method_decorator(login_required, name='dispatch')
class SideMeetingEditView(UpdateView):
    template_name = 'sidemeeting/add.html'
    form_class = SideMeetingForm
    success_url = '/sidemeeting/list/'
    model = SideMeetingSession

    def dispatch(self, request, *args, **kwargs):
        sidemeeting = self.get_object()
        # ensure the current user can modify a sidemeeting
        if not can_edit_sidemeeting_request(sidemeeting, request.user):
            raise PermissionDenied
        return super(SideMeetingEditView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SideMeetingEditView, self).get_context_data(**kwargs)
        # filter out the Group objects available        
        context['form'].fields['group'].queryset = Group.objects.filter(type='area',state='active')
        # filter out the interim meetings
        context['form'].fields['meeting'].queryset = Meeting.objects.exclude(number__icontains='interim')        
        return context

    def form_valid(self, form):
        # posted
        self.object = form.save(commit=False)
        # force the type field to be a "sidemeeting" type
        self.object.type=TimeSlotTypeName.objects.get(slug="sidemeeting")
        # set the requested_by field to a Person object        
        self.object.requested_by = Person.objects.get(user=self.request.user)
        # set the group to Secretariat for non-IETF meeting types        
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
        sidemeeting = self.get_object()
        # ensure the user can modify the db
        if not can_edit_sidemeeting_request(sidemeeting, request.user):
            raise PermissionDenied
        return super(SideMeetingDeleteView, self).dispatch(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
class SideMeetingListView(ListView):
    context_object_name = 'sidemeetings'
    template_name = 'sidemeeting/list.html'

    def dispatch(self, request, *args, **kwargs):
        # ensure the user can view the data from the db        
        if not can_request_sidemeeting(request.user):
            raise PermissionDenied
        return super(SideMeetingListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return SideMeetingSession.objects.all()

@method_decorator(login_required, name='dispatch')
class SideMeetingDetailView(DetailView):
    template_name = 'sidemeeting/detail.html'
    model = SideMeetingSession

    def dispatch(self, request, *args, **kwargs):
        sidemeeting = self.get_object()
        # ensure the user can view the db data
        if not can_view_sidemeeting_request(sidemeeting, request.user):
            raise PermissionDenied
        return super(SideMeetingDetailView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SideMeetingDetailView, self).get_context_data(**kwargs)
        context['field_names'] = DETAIL_NAMES
        return context
