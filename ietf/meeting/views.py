# Copyright The IETF Trust 2007, All Rights Reserved

#import models
from django.shortcuts import render_to_response as render, get_object_or_404
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.list_detail import object_list
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, Http404, HttpResponse, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.template import RequestContext
from django.template.loader import render_to_string
from django.conf import settings
from ietf.proceedings.models import WgMeetingSession, Proceeding, MeetingTime, NonSession, IESGHistory, SessionConflict, Meeting, MeetingHours,MeetingVenue,Switches
from ietf.idtracker.models import IRTF, IETFWG, WGSecretary, WGChair, SessionRequestActivities,IRTFChair
from ietf.meeting.forms import MeetingSession
from ietf.meeting import scheduling
import datetime, re

def show_html_materials(request, meeting_num=None):
    proceeding = get_object_or_404(Proceeding, meeting_num=meeting_num)
    begin_date = proceeding.sub_begin_date
    cut_off_date = proceeding.sub_cut_off_date
    cor_cut_off_date = proceeding.c_sub_cut_off_date
    now = datetime.date.today()
    if settings.SERVER_MODE != 'production' and '_testoverride' in request.REQUEST:
        pass
    elif now > cor_cut_off_date:
        return render("meeting/list_closed.html",{'meeting_num':meeting_num,'begin_date':begin_date, 'cut_off_date':cut_off_date, 'cor_cut_off_date':cor_cut_off_date}, context_instance=RequestContext(request))
    sub_began = 0
    if now > begin_date:
        sub_began = 1
    # List of WG sessions and Plenary sessions
    queryset_list = WgMeetingSession.objects.filter(Q(meeting=meeting_num, group_acronym_id__gte = -2, status_id=4), Q(irtf__isnull=True) | Q(irtf=0))
    queryset_irtf = WgMeetingSession.objects.filter(meeting=meeting_num, group_acronym_id__gte = -2, status_id=4, irtf__gt=0)
    queryset_interim = []
    queryset_training = []
    for item in list(WgMeetingSession.objects.filter(meeting=meeting_num)):
        if item.interim_meeting():
            item.interim=1
            queryset_interim.append(item)
        if item.group_acronym_id < -2:
            if item.slides():
                queryset_training.append(item)
    return object_list(request,queryset=queryset_list, template_name="meeting/list.html",allow_empty=True, extra_context={'meeting_num':meeting_num,'irtf_list':queryset_irtf, 'interim_list':queryset_interim, 'training_list':queryset_training, 'begin_date':begin_date, 'cut_off_date':cut_off_date, 'cor_cut_off_date':cor_cut_off_date,'sub_began':sub_began})

def current_materials(request):
    meeting = Meeting.objects.order_by('-meeting_num')[0]
    return HttpResponseRedirect( reverse(show_html_materials, args=[meeting.meeting_num]) )

def get_plenary_agenda(meeting_num, id):
    try:
        plenary_agenda_file = settings.AGENDA_PATH + WgMeetingSession.objects.get(meeting=meeting_num,group_acronym_id=id).agenda_file()
        try:
            f = open(plenary_agenda_file)
            plenary_agenda = f.read()
            f.close()
            return plenary_agenda
        except IOError:
             return "THE AGENDA HAS NOT BEEN UPLOADED YET"
    except WgMeetingSession.DoesNotExist:
        return "The Plenary has not been scheduled"

def agenda_info(num=None):
    if not num:
        num = list(Meeting.objects.all())[-1].meeting_num
    timeslots = MeetingTime.objects.select_related().filter(meeting=num).order_by("day_id", "time_desc")
    update = get_object_or_404(Switches,id=1)
    meeting=get_object_or_404(Meeting, meeting_num=num)
    venue = get_object_or_404(MeetingVenue, meeting_num=num)
    ads = list(IESGHistory.objects.select_related().filter(meeting=num))
    if not ads:
        ads = list(IESGHistory.objects.select_related().filter(meeting=str(int(num)-1)))
    ads.sort(key=(lambda item: item.area.area_acronym.acronym))
    plenaryw_agenda = get_plenary_agenda(num, -1)
    plenaryt_agenda = get_plenary_agenda(num, -2)

    return timeslots, update, meeting, venue, ads, plenaryw_agenda, plenaryt_agenda
    
def html_agenda(request, num=None):
    timeslots, update, meeting, venue, ads, plenaryw_agenda, plenaryt_agenda = agenda_info(num)
    if  settings.SERVER_MODE != 'production' and '_testiphone' in request.REQUEST:
        user_agent = "iPhone"
    elif 'HTTP_USER_AGENT' in request.META:
        user_agent = request.META["HTTP_USER_AGENT"]
    else:
        user_agent = ""
    #print user_agent
    if "iPhone" in user_agent:
        template = "meeting/m_agenda.html"
    else:
        template = "meeting/agenda.html"
    return render(template,
            {"timeslots":timeslots, "update":update, "meeting":meeting, "venue":venue, "ads":ads,
                "plenaryw_agenda":plenaryw_agenda, "plenaryt_agenda":plenaryt_agenda, },
            RequestContext(request))

def text_agenda(request, num=None):
    timeslots, update, meeting, venue, ads, plenaryw_agenda, plenaryt_agenda = agenda_info(num)
    plenaryw_agenda = "   "+plenaryw_agenda.strip().replace("\n", "\n   ")
    plenaryt_agenda = "   "+plenaryt_agenda.strip().replace("\n", "\n   ")
    return HttpResponse(render_to_string("meeting/agenda.txt",
        {"timeslots":timeslots, "update":update, "meeting":meeting, "venue":venue, "ads":ads,
            "plenaryw_agenda":plenaryw_agenda, "plenaryt_agenda":plenaryt_agenda, },
        RequestContext(request)), mimetype="text/plain")

def show_schedule(request):
    ''''Display the WG schedules'''
    meeting_num=scheduling.get_meeting_num()
 
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)

    tag = request.user.get_profile().person.person_or_org_tag

    unscheduled_groups = []
    scheduled_groups = []

    # Get scheduled groupd ids list
    scheduled_group_ids = [ schedules['group_acronym_id'] for schedules in WgMeetingSession.objects.filter(meeting=meeting_num).values('group_acronym_id') ]
    group_ids_owned = []
    group_ids_owned += [ chair['group_acronym'] for chair in WGChair.objects.filter(person=tag).values('group_acronym') ]
    group_ids_owned += [ irtfchair['irtf'] for irtfchair in IRTFChair.objects.filter(person=tag).values('irtf') ]
    group_ids_owned += [ secretary['group_acronym'] for secretary in WGSecretary.objects.filter(person=tag).values('group_acronym') ]

    # Get currently scheduled work groups where the user is the chair or secretary
    scheduled_groups = IETFWG.objects.filter( Q(group_acronym__in=scheduled_group_ids) & Q(group_acronym__in=group_ids_owned) & Q(status=1)).select_related().order_by('acronym.acronym')
    # Attach schedules to groups
    for group in scheduled_groups:
        group.meeting_session = WgMeetingSession.objects.get(meeting=meeting_num, group_acronym_id=group.group_acronym_id)

    scheduled_irtf = IRTF.objects.filter(irtfchair__person=tag, irtf_id__in=scheduled_group_ids )

    # Get unscheduled work groups where the user is the chair or secretary
    unscheduled_groups = IETFWG.objects.filter(group_acronym__in=group_ids_owned, status=1).exclude(group_acronym__in=scheduled_group_ids).select_related().order_by('acronym.acronym')

    # Set indicator on unscheduled groups whether they are meeting or not
    for group in unscheduled_groups:
        group.no_meeting = bool( group.is_meeting(meeting_num) == False )

    unscheduled_irtf = IRTF.objects.filter(irtfchair__person=tag ).exclude(irtf_id__in=scheduled_group_ids)

    return render("meeting/schedule.html", {'meeting_num': meeting_num, 'unscheduled_groups':unscheduled_groups, 'scheduled_groups':scheduled_groups, 'scheduled_irtf': scheduled_irtf, 'unscheduled_irtf': unscheduled_irtf,'first_screen':1}, context_instance=RequestContext(request))

def schedule_group(request, meeting_num=None, group_id=None):

    meeting_num=scheduling.get_meeting_num()

    if not request.user.is_authenticated():
        return HttpResponseRedirect('/accounts/login/?next=%s' % request.path)
    irtf_flag = False
    if int(group_id) < 50:
        irtf_flag = True
    group = get_object_or_404(IETFWG, group_acronym=group_id)

    person = request.user.get_profile().person
    # If group is not meeting
    if 'not_meeting' in request.POST:
        scheduling.not_meeting(group, request, meeting_num, person)
        return render("meeting/schedule_not_meeting.html", {'meeting_num': meeting_num, 'group': group, 'person': person}, context_instance=RequestContext(request) )

    elif 'save' in request.POST:
        meetingform = MeetingSession(request.POST)

        if meetingform.is_valid():
            session_id = request.POST.get('session_id')
            if session_id == 'new':
                meeting_session = WgMeetingSession(group_acronym_id = int(request.POST.get('group_acronym_id')), meeting=Meeting.objects.get(meeting_num=meeting_num), requested_date = datetime.datetime.now(), requested_by = person, status_id = 1, ts_status_id=0, approval_ad = 0 )
            else:
                meeting_session = get_object_or_404(WgMeetingSession, session_id=session_id)
            num_session = int(request.POST.get('num_session'))

            if 'third_session' in request.POST:
                num_session = num_session + 1
                meeting_session.length_session3 = MeetingHours(hour_id=request.POST.get('length_session3', ''))
                meeting_session.ts_status_id=2
            meeting_session.num_session = num_session
            meeting_session.length_session1 = MeetingHours(hour_id=request.POST.get('length_session1', ''))
            meeting_session.length_session2 = MeetingHours(hour_id=request.POST.get('length_session2', ''))
            meeting_session.number_attendee = request.POST['number_attendee']
            meeting_session.conflict1 = request.POST['conflict1']
            meeting_session.conflict2 = request.POST['conflict2']
            meeting_session.conflict3 = request.POST['conflict3']
            meeting_session.conflict_other = request.POST['conflict_other']
            meeting_session.special_req = request.POST['special_req']
            meeting_session.irtf=irtf_flag

            # Conflict population
            SessionConflict.objects.filter(meeting_num=Meeting(meeting_num=meeting_num), group_acronym=group.group_acronym).delete()
            conflict_split = re.compile(r'[ ,]+')
            conflict_list = request.POST['conflict1'] + ' ' + request.POST['conflict2'] + ' ' + request.POST['conflict3']
            for group_name in conflict_split.split(conflict_list):
                try:
                    conflict_group = IETFWG.objects.get(group_acronym__acronym=group_name)
                    SessionConflict(meeting_num=Meeting(meeting_num=meeting_num), group_acronym=group.group_acronym, conflict_gid=conflict_group.group_acronym).save()
                except IETFWG.DoesNotExist:
                    pass

            # Save form input to session object
            request.session['meeting_session'] = meeting_session
            # Display confirmation screen
            return render("meeting/schedule_confirm.html", {'meeting_num': meeting_num, 'group': group, 'session': meeting_session}, context_instance=RequestContext(request))
        else:
            # Redisplay form with error messages
            return render("meeting/schedule_group.html", {'meeting_num': meeting_num, 'group': group, 'is_new': True, 'meetingform': meetingform}, context_instance=RequestContext(request) )

    elif 'edit' in request.POST:
        try:
            session_data = WgMeetingSession.objects.filter(meeting=meeting_num, group_acronym_id=group_id).values()[0]
            session_data['length_session1'] = session_data['length_session1_id']
            session_data['length_session2'] = session_data['length_session2_id']
            session_data['length_session3'] = session_data['length_session3_id']
            meetingform = MeetingSession(session_data)
            return render("meeting/schedule_group.html", {'meeting_num': meeting_num, 'group': group, 'meetingform': meetingform, 'last_session': scheduling.last_group_session(meeting_num, group_id)}, context_instance=RequestContext(request) )

        except ObjectDoesNotExist:
            HttpResponseServerError('<h2>Could not find session for IETF meeting %s and group %s</h2>' % (meeting_num, group.group_acronym.acronym))

    elif 'confirm' in request.POST:
        meeting_session = request.session.get('meeting_session', False)
        if meeting_session:
            if meeting_session.session_id:
                request_type='Updated'
            else:
                request_type='New'
            # WORK AROUND: For some strange reason the WgMeetingSession model's
            # primary key name must be set after coming out of pickling because it sets itself to length_session1_id
            meeting_session._meta.pk.attname = 'session_id'
            meeting_session.save()
            SessionRequestActivities(group_acronym_id=group.group_acronym_id, activity=request_type+" session was requested", meeting_num=meeting_num, person=person).save()
            scheduling.send_request_email(request_type,group, request, meeting_num, person)
            del request.session['meeting_session']
        return HttpResponseRedirect('../')

    elif 'cancel' in request.POST:
        scheduling.cancel_meeting(group, request, meeting_num, person)
        return render("meeting/schedule_cancel_meeting.html", {'meeting_num': meeting_num, 'group': group, 'person': person}, context_instance=RequestContext(request) )

    else:

        conflicts = SessionConflict.objects.filter(meeting_num=meeting_num, conflict_gid=group_id).select_related().order_by('acronym.acronym').distinct()
        # See if schedule exists for group
        try:
            Session = WgMeetingSession.objects.get(meeting=meeting_num, group_acronym_id=group_id)
            session_activity = SessionRequestActivities.objects.filter(meeting_num=meeting_num, group_acronym_id=group_id).order_by('-act_date', '-act_time')
            return render("meeting/schedule_group_review.html", {'meeting_num': meeting_num, 'group': group, 'session': Session, 'session_activity': session_activity, 'conflicts': conflicts}, context_instance=RequestContext(request) )

        # Else group is not scheduled yet
        except ObjectDoesNotExist:
            meetingform = MeetingSession({'group_acronym_id': group.group_acronym_id, 'session_id': 'new'})
            return render("meeting/schedule_group.html", {'meeting_num': meeting_num, 'group': group, 'is_new': True, 'meetingform': meetingform, 'conflicts': conflicts, 'last_session': scheduling.last_group_session(meeting_num, group_id) }, context_instance=RequestContext(request) )

