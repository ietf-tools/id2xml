from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.db.models import Max, Min, Q
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.functional import curry

from sec.proceedings.views import build_choices
from sec.core.forms import GroupSelectForm
#from sec.core.models import Acronym, WGType
from sec.utils.sessions import add_session_activity
from sec.utils.shortcuts import get_group_or_404
from sec.utils.mail import send_mail
from sec.utils.ams_mail import get_cc_list
from sec.core.models import Acronym, IETFWG, IRTF, MeetingHour, SessionConflict, WgMeetingSession,  WGType
from sec.proceedings.models import Proceeding, SessionName

from forms import *
from models import *

import os
import datetime

# --------------------------------------------------
# Globals
# --------------------------------------------------
INFO_TYPES = {'ack':'Acknowledgement',
              'overview1':'IETF Overview Part 1',
              'overview2':'IETF Overview Part 2',
              'future_meeting':'Future Meeting',
              'irtf':'IRTF Home Page in HTML'}
              
NON_SESSION_INITIAL = ((0,NonSessionRef.objects.get(id=1)),
                       (1,NonSessionRef.objects.get(id=1)),
                       (2,NonSessionRef.objects.get(id=1)),
                       (3,NonSessionRef.objects.get(id=1)),
                       (4,NonSessionRef.objects.get(id=1)),
                       (5,NonSessionRef.objects.get(id=1)),
                       (None,NonSessionRef.objects.get(id=3)),
                       (None,NonSessionRef.objects.get(id=6)),
                       (None,NonSessionRef.objects.get(id=2)),
                       (1,NonSessionRef.objects.get(id=4)),
                       (2,NonSessionRef.objects.get(id=4)),
                       (3,NonSessionRef.objects.get(id=4)),
                       (4,NonSessionRef.objects.get(id=4)),
                       (1,NonSessionRef.objects.get(id=5)),
                       (2,NonSessionRef.objects.get(id=5)),
                       (3,NonSessionRef.objects.get(id=5)),
                       (4,NonSessionRef.objects.get(id=5)))

# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def make_directories(meeting):
    '''
    This function takes a meeting object and creates the appropriate materials directories
    '''
    path = meeting.upload_root
    os.umask(0)
    if not os.path.exists(path):
        os.makedirs(path)
    os.mkdir(os.path.join(path,'slides'))
    os.mkdir(os.path.join(path,'agenda'))
    os.mkdir(os.path.join(path,'minutes'))
    os.mkdir(os.path.join(path,'id'))
    os.mkdir(os.path.join(path,'rfc'))
    
def send_notification(request, session):
    '''
    This view generates email notifications for schedule sessions
    '''
    session_info_template = '''{0} Session {1} ({2})
    {3}, {4} {5}
    Room Name: {6}
    ---------------------------------------------
    '''
    group = get_group_or_404(session.group_acronym_id)
    group_name = group.acronym
    try:
        to_email = session.requested_by.email()
    except ObjectDoesNotExist:
        to_email = '[requested_by not found]'
    cc_list = get_cc_list(group, request.person)
    from_email = ('"IETF Secretariat"','agenda@ietf.org')
    subject = '%s - Requested session has been scheduled for IETF %s' % (group_name, session.meeting.meeting_num)
    template = 'meetings/session_schedule_notification.txt'
    
    session_info = session_info_template.format(group_name, 
                                                1, 
                                                session.length_session1,
                                                MeetingTime.DAYS[session.sched_time_id1.day_id],
                                                session.sched_time_id1.session_name,
                                                session.sched_time_id1.time_desc,
                                                session.sched_room_id1.room_name)
    if session.num_session > 1:
        subject = '%s - Requested sessions have been scheduled for IETF %s' % (group_name, session.meeting.meeting_num)
        session_info += session_info_template.format(group_name, 
                                                     2, 
                                                     session.length_session2,
                                                     MeetingTime.DAYS[session.sched_time_id2.day_id],
                                                     session.sched_time_id2.session_name,
                                                     session.sched_time_id2.time_desc,
                                                     session.sched_room_id2.room_name)
    if session.length_session3 and ts_status_id == 4:
        session_info += session_info_template.format(group_name, 
                                                     3, 
                                                     session.length_session3,
                                                     MeetingTime.DAYS[session.sched_time_id3.day_id],
                                                     session.sched_time_id3.session_name,
                                                     session.sched_time_id3.time_desc,
                                                     session.sched_room_id3.room_name)
                                                     
    # send email
    context = {}
    context['to_name'] = str(session.requested_by)
    context['session'] = session
    context['session_info'] = session_info

    send_mail(request,
              to_email,
              from_email,
              subject,
              template,
              context,
              cc=cc_list)
# --------------------------------------------------
# STANDARD VIEW FUNCTIONS
# --------------------------------------------------
def add(request):
    """
    Add a new IETF Meeting.  Creates Meeting and Proceeding objects.

    **Templates:**

    * ``meetings/add.html``

    **Template Variables:**

    * proceedingform

    """
    if request.method == 'POST':
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            url = reverse('meetings_main')
            return HttpResponseRedirect(url)

        proceedingform = AddProceedingForm(request.POST)
        if proceedingform.is_valid():
            # get form data - for Meeting Object
            meeting_num = proceedingform.cleaned_data['meeting_num']
            start_date = proceedingform.cleaned_data['start_date']
            end_date = proceedingform.cleaned_data['end_date']
            city = proceedingform.cleaned_data['city']
            state = proceedingform.cleaned_data['state']
            country = proceedingform.cleaned_data['country']
            time_zone = proceedingform.cleaned_data['time_zone']
            
            # get form data - for Proceeding Object
            # dir_name defaults to meeting_num
            dir_name = meeting_num
            sub_begin_date = proceedingform.cleaned_data['sub_begin_date']
            sub_cut_off_date = proceedingform.cleaned_data['sub_cut_off_date']
            c_sub_cut_off_date = proceedingform.cleaned_data['c_sub_cut_off_date']
            pr_from_date= proceedingform.cleaned_data['pr_from_date']
            pr_to_date= proceedingform.cleaned_data['pr_to_date']

            # We will need 2 objects over here Proceedings and Meetings
            # save new Meeting

            meeting_obj = Meeting(meeting_num=meeting_num,start_date=start_date,end_date=end_date,city=city,state=state,country=country,time_zone=time_zone)
            meeting_obj.save()

            # save new Proceeding
            # Using the meeting object to save in the Proceeding(As Meeting and Proceeding models are link together)
            proceeding_obj = Proceeding(meeting_num=meeting_obj,dir_name=dir_name,sub_begin_date=sub_begin_date,sub_cut_off_date=sub_cut_off_date,frozen=0,c_sub_cut_off_date=c_sub_cut_off_date,pr_from_date=pr_from_date,pr_to_date=pr_to_date)
            proceeding_obj.save()
            
            #Create Physical new meeting directory and subdirectories
            make_directories(meeting_obj)

            messages.success(request, 'The Meeting was created successfully!')
            url = reverse('meetings_main')
            return HttpResponseRedirect(url)
    else:
        # display initial forms
        max_meeting_num = Proceeding.objects.aggregate(Max('meeting_num'))['meeting_num__max']
        proceedingform = AddProceedingForm(initial={'meeting_num':max_meeting_num + 1})

    return render_to_response('meetings/add.html', {
        'proceedingform': proceedingform},
        RequestContext(request, {}),
    )

def add_tutorial(request, meeting_id):
    '''
    This function essentially adds an entry to the acronym table.  The acronym_id set to the 
    lowest (negative) acronym_id minus one. This designates the acronym as a tutorial and will 
    now appear in the tutorial drop down list when scheduling sessions.
    '''
    meeting = get_object_or_404(Meeting, meeting_num=meeting_id)

    if request.method == 'POST':
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            url = reverse('meetings_schedule_sessions', kwargs={'meeting_id':meeting.pk})
            return HttpResponseRedirect(url)
            
        form = AddTutorialForm(request.POST)
        if form.is_valid():
            acronym = form.save(commit=False)
            new_id = Acronym.objects.all().aggregate(Min('acronym_id'))['acronym_id__min'] - 1
            acronym.acronym_id = new_id
            acronym.save()
            
            messages.success(request, 'The Tutorial was created successfully!')
            url = reverse('meetings_schedule_sessions', kwargs={'meeting_id':meeting.pk})
            return HttpResponseRedirect(url)
            
    else:
        form = AddTutorialForm()
    
    return render_to_response('meetings/add_tutorial.html', {
        'form': form,
        'meeting': meeting},
        RequestContext(request, {}),
    )
        
        
def edit_additional(request, meeting_id, type):
    '''
    This function allows the user to edit Additional Info for the meeting.
    There are four types of additional info:
    ack - Acknowledgment - stored in meetings.ack
    future - Future Meetings - stored in meetings.future_meeting
    overview - IETF Overview - stored in general_info
    irtf - IRTF Home Page - stored in general_info 
    '''
    meeting = get_object_or_404(Meeting, meeting_num=meeting_id)

    if request.method == 'POST':
        form = AdditionalInfoForm(request.POST) 
        if request.POST['submit'] == "Cancel":
            url = reverse('meetings_meeting_detail', kwargs={'meeting_id':meeting_id})
            return HttpResponseRedirect(url)
     
        if form.is_valid():
            text = form.cleaned_data['text'] 
            if type in ('ack','future_meeting'):
                setattr(meeting, type, text)
                meeting.save()
            if type in ('irtf','overview1','overview2'):
                obj, created = GeneralInfo.objects.get_or_create(info_name=type,defaults={'info_text':text})
                if not created:
                    obj.info_text = text
                    obj.save()
            messages.success(request, 'The %s was changed successfully' % INFO_TYPES[type])
            url = reverse('meetings_meeting_detail', kwargs={'meeting_id':meeting_id})
            return HttpResponseRedirect(url)
            
    else:
        # perhaps move to get_info_initial(meeting,type)
        if type in ('ack','future_meeting'):
            initial = {'text': getattr(meeting,type)}
        if type in ('irtf','overview1','overview2'):
            try:
                gi = GeneralInfo.objects.get(info_name=type)
                initial = {'text': gi.info_text}
            except GeneralInfo.DoesNotExist:
                initial = {}
                
        form = AdditionalInfoForm(initial)
        
    return render_to_response('meetings/edit_additional.html', {
        'form': form,
        'type': INFO_TYPES[type],
        'meeting': meeting},
        RequestContext(request, {}),
    )

def edit_session(request, session_id):
    '''
    Edit session scheduling details
    '''
    session = get_object_or_404(WgMeetingSession, session_id=session_id)
    meeting = get_object_or_404(Meeting, meeting_num=session.meeting.meeting_num)
    group = session.group
    
    # NOTE special cases for Tutorials / BOFs
    if ( isinstance(group, IETFWG) and group.group_type.pk == 3 ) or group.pk < 0:
        show_request = False
        num_session = 1
    else:
        show_request = True
        num_session = session.real_num_session
    
    # need to use curry here to pass custom variable to form init
    NewSessionFormset = formset_factory(NewSessionForm, extra=0)
    NewSessionFormset.form = staticmethod(curry(NewSessionForm, meeting=meeting))
    
    if request.method == 'POST':
        formset = NewSessionFormset(request.POST)
        extra_form = ExtraSessionForm(request.POST)
        if formset.is_valid() and extra_form.is_valid():
            # do save
            count = 1
            for form in formset.forms:
                time_attr = 'sched_time_id' + str(count)
                room_attr = 'sched_room_id' + str(count)
                time = MeetingTime.objects.get(id=form.cleaned_data['time'])
                room = MeetingRoom.objects.get(id=form.cleaned_data['room'])
                setattr(session, time_attr, time)
                setattr(session, room_attr, room)
                
                # handle "combine" option
                if form.cleaned_data.get('combine',None):
                    # there must be a next slot or validation would have failed
                    next_slot = get_next_slot(time.id)
                    if count != 3:
                        comb_time = 'combined_time_id' + str(count)
                        comb_room = 'combined_room_id' + str(count)
                        setattr(session, comb_time, next_slot)
                        setattr(session, comb_room, room)
                else:
                    if count != 3:
                        comb_time = 'combined_time_id' + str(count)
                        comb_room = 'combined_room_id' + str(count)
                        setattr(session, comb_time, None)
                        setattr(session, comb_room, None)
                    
                if count == 3 and session.ts_status_id == 3:
                    session.ts_status_id = 4
                
                '''
                if isinstance(group, IRTF):
                    one_hour = MeetingHour.objects.get(hour_id=1)
                    session.irtf = 1
                    session.num_session = 1
                    session.length_session1 = one_hour
                    session.requested_by = request.person
                '''
                count = count + 1
                
            session.status_id = 4
            session.scheduled_date = datetime.datetime.now()
            session.special_agenda_note = extra_form.cleaned_data['note']
            session.save()
            
            # update session activity
            add_session_activity(group.pk,'Session was scheduled',meeting,request.person)
            
            # notify.  dont send if Tutorial, BOF or indicated on form
            notification_message = "No notification has been sent to anyone for this session."
            if not extra_form.cleaned_data.get('no_notify',False):
                if group.pk > 0:
                    group = get_group_or_404(group.pk)
                    bof_type = WGType.objects.get(group_type_id=3)
                    if hasattr(group,'group_type') and group.group_type == bof_type:
                        pass
                    else:
                        send_notification(request, session)
                        notification_message = "Notification sent."
                            
            messages.success(request, 'Session(s) Scheduled for %s.  %s' %  (group.acronym, notification_message))
            url = reverse('meetings_schedule_sessions', kwargs={'meeting_id':meeting.pk})
            return HttpResponseRedirect(url)
            
    else:
        # intitialize forms
        initial = []
        if session.sched_time_id1:
            values = {'time':str(session.sched_time_id1.pk),
                      'room':str(session.sched_room_id1.pk)}
            if session.combined_room_id1:
                values['combined'] = True
            initial.append(values)
        if session.sched_time_id2:
            values = {'time':str(session.sched_time_id2.pk),
                      'room':str(session.sched_room_id2.pk)}
            if session.combined_room_id2:
                values['combined'] = True
            initial.append(values)
        if session.sched_time_id3:
            values = {'time':str(session.sched_time_id3.pk),
                      'room':str(session.sched_room_id3.pk)}
            initial.append(values)
        #assert False, initial
        formset = NewSessionFormset(initial=initial)
        extra_form = ExtraSessionForm(initial={'note':session.special_agenda_note})
        
    return render_to_response('meetings/edit_session.html', {
        'extra_form': extra_form,
        'show_request': show_request,
        'session': session,
        'formset': formset},
        RequestContext(request, {}),
    )


def main(request):
    '''
    In this view the user can choose a meeting to manage or elect to create a new meeting.
    '''
    meetings = Meeting.objects.all().order_by('-meeting_num')
    
    if request.method == 'POST':
        redirect_url = reverse('meetings_meeting', kwargs={'meeting_id':request.POST['group']})
        return HttpResponseRedirect(redirect_url)
        
    choices = [ (str(x.meeting_num),str(x.meeting_num)) for x in meetings ]
    form = GroupSelectForm(choices=choices)
    
    return render_to_response('meetings/main.html', {
        'form': form,
        'meetings': meetings},
        RequestContext(request, {}),
    )
def meeting(request, meeting_id):
    
    meeting = get_object_or_404(Meeting, meeting_num=meeting_id)
    
    return render_to_response('meetings/meeting.html', {
        'meeting': meeting},
        RequestContext(request, {}),
    )

def meeting_detail(request, meeting_id):
    
    meeting = get_object_or_404(Meeting, meeting_num=meeting_id)
    proceeding = get_object_or_404(Proceeding, meeting_num=meeting_id)
    
    return render_to_response('meetings/meeting_detail.html', {
        'meeting': meeting,
        'proceeding': proceeding},
        RequestContext(request, {}),
    )
    
def meeting_edit(request, meeting_id):
    """
    Edit Meeting information.

    **Templates:**

    * ``meetings/meeting_edit.html``

    **Template Variables:**

    * meeting, meeting_formset, meeting_form

    """
    # get meeting or return HTTP 404 if record not found
    meeting = get_object_or_404(Meeting, meeting_num=meeting_id)
    proceeding = get_object_or_404(Proceeding, meeting_num=meeting_id)

    ProceedingFormSet = inlineformset_factory(Meeting, Proceeding, form=ProceedingForm, can_delete=False, extra=0)

    if request.method == 'POST':
        button_text = request.POST.get('submit','')
        if button_text == 'Save':
            proceeding_formset = ProceedingFormSet(request.POST, instance=meeting)
            meeting_form = MeetingForm(request.POST, instance=meeting)

            if proceeding_formset.is_valid() and meeting_form.is_valid():
                proceeding_formset.save()
                meeting_form.save()
                messages.success(request,'The meeting entry was changed successfully')
                url = reverse('meetings_meeting_detail', kwargs={'meeting_id':meeting_id})
                return HttpResponseRedirect(url)

        else:
            url = reverse('meetings_meeting_detail', kwargs={'meeting_id':meeting_id})
            return HttpResponseRedirect(url)
    else:
        proceeding_formset = ProceedingFormSet(instance=meeting)
        meeting_form = MeetingForm(instance=meeting)

    return render_to_response('meetings/meeting_edit.html', {
        'meeting': meeting,
        'proceeding_formset': proceeding_formset,
        'meeting_form' : meeting_form, },
        RequestContext(request,{}),
    )

def new_session(request, meeting_id, group_id):
    '''
    Schedule a session
    Requirements:
    - display third session status if not 0
    - display session request info if it exists
    '''
    
    meeting = get_object_or_404(Meeting, meeting_num=meeting_id)
    group = get_group_or_404(group_id)
    
    try:
        session = WgMeetingSession.objects.get(meeting=meeting_id,group_acronym_id=group_id)
    except WgMeetingSession.DoesNotExist:
        session = None
    
    # warn and redirect to edit if there is already a scheduled session for this group
    if session:
        if session.status_id == 4:
            messages.error(request, 'The session for %s is already scheduled for meeting %s' % (session.group, meeting_id))
            url = reverse('meetings_edit_session', kwargs={'session_id':session.session_id})
            return HttpResponseRedirect(url)
            
    # set number of sessions
    if session:
        num_session = session.real_num_session
    else:
        num_session = 1
        
    # need to use curry here to pass custom variable to form init
    NewSessionFormset = formset_factory(NewSessionForm, extra=num_session)
    NewSessionFormset.form = staticmethod(curry(NewSessionForm, meeting=meeting))

    if request.method == 'POST':
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            url = reverse('meetings_schedule_sessions', kwargs={'meeting_id':meeting_id})
            return HttpResponseRedirect(url)

        formset = NewSessionFormset(request.POST)
        extra_form = ExtraSessionForm(request.POST)
        
        
        if formset.is_valid() and extra_form.is_valid():
            # create session now if it doesn't exist (tutorials, BOFs)
            if not session:
                session = WgMeetingSession(meeting=meeting,group_acronym_id=group_id,num_session=1,status=4)
                session.save()
                    
            count = 1
            for form in formset.forms:
                time_attr = 'sched_time_id' + str(count)
                room_attr = 'sched_room_id' + str(count)
                #assert False, form.cleaned_data
                time = MeetingTime.objects.get(id=form.cleaned_data['time'])
                room = MeetingRoom.objects.get(id=form.cleaned_data['room'])
                setattr(session, time_attr, time)
                setattr(session, room_attr, room)
                
                # handle "combine" option
                if form.cleaned_data.get('combine',None):
                    # there must be a next slot or validation would have failed
                    next_slot = get_next_slot(time.id)
                    if count != 3:
                        comb_time = 'combined_time_id' + str(count)
                        comb_room = 'combined_room_id' + str(count)
                        setattr(session, comb_time, next_slot)
                        setattr(session, comb_room, room)
                    
                if count == 3 and session.ts_status_id == 3:
                    session.ts_status_id = 4
                
                '''
                if isinstance(group, IRTF):
                    one_hour = MeetingHour.objects.get(hour_id=1)
                    session.irtf = 1
                    session.num_session = 1
                    session.length_session1 = one_hour
                    session.requested_by = request.person
                '''
                count = count + 1
                
            session.status_id = 4
            session.scheduled_date = datetime.datetime.now()
            session.special_agenda_note = extra_form.cleaned_data['note']
            session.save()
            
            # update session activity
            add_session_activity(group_id,'Session was scheduled',meeting,request.person)
            
            # notify.  dont send if Tutorial, BOF or indicated on form
            notification_message = "No notification has been sent to anyone for this session."
            if not extra_form.cleaned_data.get('no_notify',False):
                if group_id > 0:
                    group = get_group_or_404(group_id)
                    bof_type = WGType.objects.get(group_type_id=3)
                    if hasattr(group,'group_type') and group.group_type == bof_type:
                        pass
                    else:
                        send_notification(request, session)
                        notification_message = "Notification sent."
                
            messages.success(request, 'Session(s) Scheduled for %s.  %s' %  (group.acronym, notification_message))
            url = reverse('meetings_schedule_sessions', kwargs={'meeting_id':meeting_id})
            return HttpResponseRedirect(url)
    else:
        formset = NewSessionFormset()
        extra_form = ExtraSessionForm()
    

    return render_to_response('meetings/new_session.html', {
        'extra_form': extra_form,
        'formset': formset,
        'meeting': meeting,
        'session': session},
        RequestContext(request, {}),
    )
    
def non_session(request, meeting_id):
    '''
    Display and edit "non-session" time slots, ie. registration, beverage and snack breaks
    '''
    meeting = get_object_or_404(Meeting, meeting_num=meeting_id)
    
    # if the NonSession records don't exist yet (new meeting) create them
    if not NonSession.objects.filter(meeting=meeting):
        for record in NON_SESSION_INITIAL:
            new = NonSession(day_id=record[0],
                             non_session_ref=record[1],
                             meeting=meeting)
            new.save()
        
    NonSessionFormset = inlineformset_factory(Meeting, NonSession, form=NonSessionForm, can_delete=False,extra=0)
    
    if request.method == 'POST':
        formset = NonSessionFormset(request.POST, instance=meeting, prefix='non_session')
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Non-Sessions updated successfully')
            url = reverse('meetings_non_session', kwargs={'meeting_id':meeting_id})
            return HttpResponseRedirect(url)
    else:       
        formset = NonSessionFormset(instance=meeting, prefix='non_session')
    
    return render_to_response('meetings/non_session.html', {
        'formset': formset,
        'meeting': meeting},
        RequestContext(request, {}),
    )

def remove_session(request, session_id):
    '''
    Remove session from agenda.  Deletes WgMeetingSession record entirely, meaning new session
    request will need to be submitted to re-schedule.
    '''
    session = get_object_or_404(WgMeetingSession, session_id=session_id)
    meeting = get_object_or_404(Meeting, meeting_num=session.meeting.meeting_num)
    group = session.group
    
    # delete the conflicts
    SessionConflict.objects.filter(meeting_num=meeting.meeting_num,group_acronym_id=group.pk).delete()
    
    # update group record
    # set specific values for IETFWG and IRTF, do nothing if group is a tutorial (Acronym)
    if isinstance(group, IRTF):
        group.meeting_scheduled = False
        group.save()
    if isinstance(group, IETFWG):
        group.meeting_scheduled = 'NO'
        group.save()
    
    # delete session record
    session.delete()
    
    # log activity
    add_session_activity(group.pk,'Session was removed from agenda',meeting,request.person)
    
    messages.success(request, '%s Session removed from agenda' % (session.group))
    url = reverse('meetings_schedule_sessions', kwargs={'meeting_id':meeting.meeting_num})
    return HttpResponseRedirect(url)

def rooms(request, meeting_id):
    '''
    Display and edit MeetingRoom records for the specified meeting
    '''
    meeting = get_object_or_404(Meeting, meeting_num=meeting_id)
    
    # if no rooms exist yet (new meeting) formset extra=5
    rooms = meeting.meetingroom_set.all().order_by('room_name')
    extra = 0 if rooms else 5
    RoomFormset = inlineformset_factory(Meeting, MeetingRoom, form=MeetingRoomForm, formset=BaseMeetingRoomFormSet, can_delete=True, extra=extra)

    if request.method == 'POST':
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            url = reverse('meetings', kwargs={'meeting_id':meeting_id})
            return HttpResponseRedirect(url)

        formset = RoomFormset(request.POST, instance=meeting, prefix='room')
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Meeting Rooms changed successfully')
            url = reverse('meetings_rooms', kwargs={'meeting_id':meeting_id})
            return HttpResponseRedirect(url)
    else:
        formset = RoomFormset(instance=meeting, prefix='room')

    return render_to_response('meetings/rooms.html', {
        'meeting': meeting,
        'rooms': rooms,
        'formset': formset},
        RequestContext(request, {}),
    )
    
def schedule_sessions(request, meeting_id):
    '''
    This view presents lists of WGs, Tutorials, BOFs for the secretariat user to select from to 
    schedule a session
    WGs: those that have pending session requests are listed.
    Tutorials: those that aren't already scheduled are listed
    BOFs: all BOFs which aren't already scheduled are lists
    IRTF: those that have pending session requests are listed.
    '''
    meeting = get_object_or_404(Meeting, meeting_num=meeting_id)
    
    if request.method == 'POST':
        redirect_url = reverse('meetings_new_session', kwargs={'meeting_id':meeting.meeting_num,'group_id':request.POST['group']})
        return HttpResponseRedirect(redirect_url)
            
    scheduled_sessions = WgMeetingSession.objects.filter(meeting=meeting,status_id=4)
    sorted_scheduled_sessions = sorted(scheduled_sessions, key=lambda scheduled_sessions: scheduled_sessions.group.acronym.lower())
    scheduled_group_ids = [ s.group_acronym_id for s in scheduled_sessions ]
    
    # prep group form
    requests = WgMeetingSession.objects.filter(~Q(irtf=1),meeting=meeting,status_id__in=[1,2,3])
    choices = build_choices( [ r.group for r in requests ] )
    group_form = GroupSelectForm(choices=choices)
    
    # prep tutorial form
    tutorials = Acronym.objects.filter(acronym_id__lt=0).order_by('name')
    unscheduled_tutorials = [ t for t in tutorials if t.acronym_id not in scheduled_group_ids ]
    tut_choices = zip([ x.pk for x in unscheduled_tutorials ],
                  [ x.name for x in unscheduled_tutorials ])
    tutorial_form = GroupSelectForm(choices=tut_choices)
    
    # prep BOFs form
    # seems like these should appear in group list above but maybe no request is filled out for them
    bofs = Acronym.objects.filter(ietfwg__group_type=3,ietfwg__status=1).order_by('acronym')
    unscheduled_bofs = [ b for b in bofs if b.acronym_id not in scheduled_group_ids ]
    bof_choices = build_choices(unscheduled_bofs)
    bof_form = GroupSelectForm(choices=bof_choices)
    
    # prep IRTF form
    #irtfs = IRTF.objects.all().order_by('acronym')
    #unscheduled_irtfs = [ i for i in irtfs if i.irtf_id not in scheduled_group_ids ]
    #irtf_choices = build_choices(unscheduled_irtfs)
    requests = WgMeetingSession.objects.filter(irtf=1,meeting=meeting,status_id__in=[1,2,3])
    irtf_choices = build_choices( [ r.group for r in requests ] )
    irtf_form = GroupSelectForm(choices=irtf_choices)
    
    return render_to_response('meetings/schedule_sessions.html', {
        'group_form': group_form,
        'tutorial_form': tutorial_form,
        'bof_form': bof_form,
        'irtf_form': irtf_form,
        'scheduled_sessions': sorted_scheduled_sessions,
        'meeting': meeting},
        RequestContext(request, {}),
    )

def times(request, meeting_id):
    '''
    Display and edit time slots (MeetingTime)
    '''
    meeting = get_object_or_404(Meeting, meeting_num=meeting_id)
    
    # if no times exist yet (new meeting) formset extra=5
    times = meeting.meetingtime_set.all()
    extra = 0 if times else 5
    TimeFormset = inlineformset_factory(Meeting, MeetingTime, form=MeetingTimeForm, formset=BaseMeetingTimeFormSet, can_delete=True, extra=extra)

    if request.method == 'POST':
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            url = reverse('meetings', kwargs={'meeting_id':meeting_id})
            return HttpResponseRedirect(url)

        formset = TimeFormset(request.POST, instance=meeting, prefix='time')
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Meeting Times changed successfully')
            url = reverse('meetings_times', kwargs={'meeting_id':meeting_id})
            return HttpResponseRedirect(url)
    else:
        formset = TimeFormset(instance=meeting, prefix='time')

    return render_to_response('meetings/times.html', {
        'meeting': meeting,
        'formset': formset},
        RequestContext(request, {}),
    )

def venue(request, meeting_id):
    '''
    Display and edit MeetingVenue records (Break Area, Registration Area)
    '''
    meeting = get_object_or_404(Meeting, meeting_num=meeting_id)
    meeting_venue, created = MeetingVenue.objects.get_or_create(meeting_num=meeting)
    
    if request.method == 'POST':
        form = MeetingVenueForm(request.POST, instance=meeting_venue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Meeting Venues changed successfully')
            url = reverse('meetings_venue', kwargs={'meeting_id':meeting_id})
            return HttpResponseRedirect(url)
    
    else:
        form = MeetingVenueForm(instance=meeting_venue)
    
    return render_to_response('meetings/venue.html', {
        'form': form,
        'meeting': meeting},
        RequestContext(request, {}),
    )
    
def view(request, meeting_id):
    """
    View Meeting information.

    **Templates:**

    * ``meetings/view.html``

    **Template Variables:**

    * meeting , proceeding

    """
    meeting = get_object_or_404(Meeting, meeting_num=meeting_id)
    proceeding = get_object_or_404(Proceeding, meeting_num=meeting_id)
    
    return render_to_response('meetings/view.html', {
        'meeting': meeting,
        'proceeding': proceeding},
        RequestContext(request, {}),
    )
