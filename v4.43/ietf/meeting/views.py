# Copyright The IETF Trust 2007, All Rights Reserved

#import models
import datetime
import os
import re
import tarfile

from tempfile import mkstemp

from django import forms
from django.shortcuts import render_to_response, get_object_or_404
from ietf.idtracker.models import IETFWG, IRTF, Area
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.template import RequestContext
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.decorators import decorator_from_middleware
from ietf.ietfauth.decorators import group_required
from django.middleware.gzip import GZipMiddleware
from django.db.models import Max
from ietf.group.colors import fg_group_colors, bg_group_colors

import debug
import urllib

from ietf.utils.pipe import pipe
from ietf.doc.models import Document, State

# Old model -- needs to be removed
from ietf.proceedings.models import Meeting as OldMeeting, WgMeetingSession, MeetingVenue, IESGHistory, Proceeding, Switches

# New models
from ietf.meeting.models import Meeting, TimeSlot, Session
from ietf.meeting.models import Schedule, ScheduledSession
from ietf.group.models import Group

from ietf.meeting.helpers import NamedTimeSlot, get_ntimeslots_from_ss
from ietf.meeting.helpers import get_ntimeslots_from_agenda, agenda_info
from ietf.meeting.helpers import get_areas, get_area_list_from_sessions
from ietf.meeting.helpers import build_all_agenda_slices, get_wg_name_list
from ietf.meeting.helpers import get_scheduledsessions_from_schedule
from ietf.meeting.helpers import get_modified_from_scheduledsessions
from ietf.meeting.helpers import get_wg_list, session_draft_list
from ietf.meeting.helpers import get_meeting, get_schedule

@decorator_from_middleware(GZipMiddleware)
def show_html_materials(request, meeting_num=None, schedule_name=None):
    proceeding = get_object_or_404(Proceeding, meeting_num=meeting_num)
    begin_date = proceeding.sub_begin_date
    cut_off_date = proceeding.sub_cut_off_date
    cor_cut_off_date = proceeding.c_sub_cut_off_date
    now = datetime.date.today()
    if settings.SERVER_MODE != 'production' and '_testoverride' in request.REQUEST:
        pass
    elif now > cor_cut_off_date:
        return render_to_response("meeting/list_closed.html",{'meeting_num':meeting_num,'begin_date':begin_date, 'cut_off_date':cut_off_date, 'cor_cut_off_date':cor_cut_off_date}, context_instance=RequestContext(request))
    sub_began = 0
    if now > begin_date:
        sub_began = 1

    meeting = get_meeting(meeting_num)
    schedule = get_schedule(meeting, schedule_name)

    scheduledsessions = get_scheduledsessions_from_schedule(schedule)

    plenaries = scheduledsessions.filter(session__name__icontains='plenary')
    ietf      = scheduledsessions.filter(session__group__parent__type__slug = 'area').exclude(session__group__acronym='edu')
    irtf      = scheduledsessions.filter(session__group__parent__acronym = 'irtf')
    training  = scheduledsessions.filter(session__group__acronym='edu')

    cache_version = Document.objects.filter(session__meeting__number=meeting_num).aggregate(Max('time'))["time__max"]
    #
    return render_to_response("meeting/list.html",
                              {'meeting_num':meeting_num,
                               'plenaries': plenaries, 'ietf':ietf, 'training':training, 'irtf': irtf,
                               'begin_date':begin_date, 'cut_off_date':cut_off_date,
                               'cor_cut_off_date':cor_cut_off_date,'sub_began':sub_began,
                               'cache_version':cache_version},
                              context_instance=RequestContext(request))

def current_materials(request):
    meeting = OldMeeting.objects.exclude(number__startswith='interim-').order_by('-meeting_num')[0]
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

##########################################################################################################################
## dispatch based upon request type.
def agenda_html_request(request,num=None, schedule_name=None):
    if request.method == 'POST':
        return agenda_create(request, num, schedule_name)
    else:
        # GET and HEAD.
        return html_agenda(request, num, schedule_name)

def get_agenda_info(request, num=None, schedule_name=None):
    meeting = get_meeting(num)
    schedule = get_schedule(meeting, schedule_name)
    scheduledsessions = get_scheduledsessions_from_schedule(schedule)
    modified = get_modified_from_scheduledsessions(scheduledsessions)

    area_list = get_areas()
    wg_list = get_wg_list(scheduledsessions)
    time_slices,date_slices = build_all_agenda_slices(scheduledsessions, False)
    rooms = meeting.room_set

    return scheduledsessions, schedule, modified, meeting, area_list, wg_list, time_slices, date_slices, rooms

def mobile_user_agent_detect():
    if  settings.SERVER_MODE != 'production' and '_testiphone' in request.REQUEST:
        user_agent = "iPhone"
    elif 'user_agent' in request.REQUEST:
        user_agent = request.REQUEST['user_agent']
    elif 'HTTP_USER_AGENT' in request.META:
        user_agent = request.META["HTTP_USER_AGENT"]
    else:
        user_agent = ""

@decorator_from_middleware(GZipMiddleware)
def html_agenda(request, num=None, schedule_name=None):
    user_agent = mobile_user_agent_detect()
    if "iPhone" in user_agent:
        return iphone_agenda(request, num, schedule_name)

    scheduledsessions, schedule, modified, meeting, area_list, wg_list, time_slices, date_slices, rooms = get_agenda_info(request, num, schedule_name)

    return HttpResponse(render_to_string("meeting/agenda.html",
        {"scheduledsessions":scheduledsessions, "rooms":rooms, "time_slices":time_slices, "date_slices":date_slices  ,"modified": modified, "meeting":meeting,
         "area_list": area_list, "wg_list": wg_list,
         "fg_group_colors": fg_group_colors,
         "bg_group_colors": bg_group_colors,
         "show_inline": set(["txt","htm","html"]) },
        RequestContext(request)), mimetype="text/html")

@decorator_from_middleware(GZipMiddleware)
def html_agenda_utc(request, num=None, schedule_name=None):

    user_agent = mobile_user_agent_detect()
    if "iPhone" in user_agent:
        return iphone_agenda(request, num)

    scheduledsessions, schedule, modified, meeting, area_list, wg_list, time_slices, date_slices, rooms = get_agenda_info(request, num, schedule_name)

    return HttpResponse(render_to_string("meeting/agenda_utc.html",
        {"scheduledsessions":scheduledsessions, "rooms":rooms, "time_slices":time_slices, "date_slices":date_slices  ,"modified": modified, "meeting":meeting,
         "area_list": area_list, "wg_list": wg_list,
         "fg_group_colors": fg_group_colors,
         "bg_group_colors": bg_group_colors,
         "show_inline": set(["txt","htm","html"]) },
        RequestContext(request)), mimetype="text/html")

class SaveAsForm(forms.Form):
    savename = forms.CharField(max_length=100)

@group_required('Area_Director','Secretariat')
def agenda_create(request, num=None, schedule_name=None):
    meeting = get_meeting(num)
    schedule = get_schedule(meeting, schedule_name)

    if schedule is None:
        # here we have to return some ajax to display an error.
        raise Http404("No meeting information for meeting %s schedule %s available" % (num,schedule_name))

    # authorization was enforced by the @group_require decorator above.

    saveasform = SaveAsForm(request.POST)
    if not saveasform.is_valid():
        return HttpResponse(status=404)

    savedname = saveasform.cleaned_data['savename']

    # create the new schedule, and copy the scheduledsessions
    try:
        sched = meeting.schedule_set.get(name=savedname, owner=request.user.person)
        if sched:
            # XXX needs to record a session error and redirect to where?
            return HttpResponseRedirect(
                reverse(edit_agenda,
                        args=[meeting.number, sched.name]))

    except Schedule.DoesNotExist:
        pass

    # must be done
    newschedule = Schedule(name=savedname,
                           owner=request.user.person,
                           meeting=meeting,
                           visible=False,
                           public=False)

    newschedule.save()
    if newschedule is None:
        return HttpResponse(status=500)

    for ss in schedule.scheduledsession_set.all():
        # hack to copy the object, creating a new one
        # just reset the key, and save it again.
        ss.pk = None
        ss.schedule=newschedule
        ss.save()

    # now redirect to this new schedule.
    return HttpResponseRedirect(
        reverse(edit_agenda,
                args=[meeting.number, newschedule.name]))


##########################################################################################################################
@decorator_from_middleware(GZipMiddleware)
def edit_agenda(request, num=None, schedule_name=None):

    if request.method == 'POST':
        return agenda_create(request, num, schedule_name)

    meeting = get_meeting(num)
    schedule = get_schedule(meeting, schedule_name)

    # get_modified_from needs the query set, not the list
    sessions = meeting.session_set.order_by("id", "group", "requested_by")
    scheduledsessions = get_scheduledsessions_from_schedule(schedule)
    modified = get_modified_from_scheduledsessions(scheduledsessions)

    ntimeslots = get_ntimeslots_from_ss(schedule, scheduledsessions)

    area_list = get_areas()
    wg_name_list = get_wg_name_list(scheduledsessions)
    wg_list = get_wg_list(wg_name_list)

    time_slices,date_slices = build_all_agenda_slices(scheduledsessions, True)

    meeting_base_url = meeting.url(request.get_host_protocol(), "")
    site_base_url =request.get_host_protocol()
    rooms = meeting.room_set
    rooms = rooms.all()
    saveas = SaveAsForm()
    saveasurl=reverse(edit_agenda,
                      args=[meeting.number, schedule.name])

    return HttpResponse(render_to_string("meeting/landscape_edit.html",
                                         {"timeslots":ntimeslots,
                                          "schedule":schedule,
                                          "saveas": saveas,
                                          "saveasurl": saveasurl,
                                          "meeting_base_url": meeting_base_url,
                                          "site_base_url": site_base_url,
                                          "rooms":rooms,
                                          "time_slices":time_slices,
                                          "date_slices":date_slices,
                                          "modified": modified,
                                          "meeting":meeting,
                                          "area_list": area_list,
                                          "wg_list": wg_list ,
                                          "sessions": sessions,
                                          "scheduledsessions": scheduledsessions,
                                          "show_inline": set(["txt","htm","html"]) },
                                         RequestContext(request)), mimetype="text/html")

###########################################################################################################################

def iphone_agenda(request, num, name):
    timeslots, scheduledsessions, update, meeting, venue, ads, plenaryw_agenda, plenaryt_agenda = agenda_info(num, name)

    groups_meeting = set();
    for ss in scheduledsessions:
        groups_meeting.add(ss.session.group.acronym)

    wgs = IETFWG.objects.filter(status=IETFWG.ACTIVE).filter(group_acronym__acronym__in = groups_meeting).order_by('group_acronym__acronym')
    rgs = IRTF.objects.all().filter(acronym__in = groups_meeting).order_by('acronym')
    areas = get_areas()
    template = "meeting/m_agenda.html"
    return render_to_response(template,
            {"timeslots":timeslots,
             "scheduledsessions":scheduledsessions,
             "update":update,
             "meeting":meeting,
             "venue":venue,
             "ads":ads,
             "plenaryw_agenda":plenaryw_agenda,
             "plenaryt_agenda":plenaryt_agenda,
             "wg_list" : wgs,
             "rg_list" : rgs},
            context_instance=RequestContext(request))


def text_agenda(request, num=None, name=None):
    timeslots, scheduledsessions, update, meeting, venue, ads, plenaryw_agenda, plenaryt_agenda = agenda_info(num, name)
    plenaryw_agenda = "   "+plenaryw_agenda.strip().replace("\n", "\n   ")
    plenaryt_agenda = "   "+plenaryt_agenda.strip().replace("\n", "\n   ")

    return HttpResponse(render_to_string("meeting/agenda.txt",
        {"timeslots":timeslots,
         "scheduledsessions":scheduledsessions,
         "update":update,
         "meeting":meeting,
         "venue":venue,
         "ads":ads,
         "plenaryw_agenda":plenaryw_agenda,
         "plenaryt_agenda":plenaryt_agenda, },
        RequestContext(request)), mimetype="text/plain")

def session_agenda(request, num, session):
    d = Document.objects.filter(type="agenda", session__meeting__number=num)
    if session == "plenaryt":
        d = d.filter(session__name__icontains="technical", session__timeslot__type="plenary")
    elif session == "plenaryw":
        d = d.filter(session__name__icontains="admin", session__timeslot__type="plenary")
    else:
        d = d.filter(session__group__acronym=session)

    if d:
        agenda = d[0]
        content = read_agenda_file(num, agenda)
        _, ext = os.path.splitext(agenda.external_url)
        ext = ext.lstrip(".").lower()

        if ext == "txt":
            return HttpResponse(content, mimetype="text/plain")
        elif ext == "pdf":
            return HttpResponse(content, mimetype="application/pdf")
        else:
            return HttpResponse(content)

    raise Http404("No agenda for the %s session of IETF %s is available" % (session, num))

def convert_to_pdf(doc_name):
    inpath = os.path.join(settings.IDSUBMIT_REPOSITORY_PATH, doc_name + ".txt")
    outpath = os.path.join(settings.INTERNET_DRAFT_PDF_PATH, doc_name + ".pdf")

    try:
        infile = open(inpath, "r")
    except IOError:
        return

    t,tempname = mkstemp()
    tempfile = open(tempname, "w")

    pageend = 0;
    newpage = 0;
    formfeed = 0;
    for line in infile:
        line = re.sub("\r","",line)
        line = re.sub("[ \t]+$","",line)
        if re.search("\[?[Pp]age [0-9ivx]+\]?[ \t]*$",line):
            pageend=1
            tempfile.write(line)
            continue
        if re.search("^[ \t]*\f",line):
            formfeed=1
            tempfile.write(line)
            continue
        if re.search("^ *INTERNET.DRAFT.+[0-9]+ *$",line) or re.search("^ *Internet.Draft.+[0-9]+ *$",line) or re.search("^draft-[-a-z0-9_.]+.*[0-9][0-9][0-9][0-9]$",line) or re.search("^RFC.+[0-9]+$",line):
            newpage=1
        if re.search("^[ \t]*$",line) and pageend and not newpage:
            continue
        if pageend and newpage and not formfeed:
            tempfile.write("\f")
        pageend=0
        formfeed=0
        newpage=0
        tempfile.write(line)

    infile.close()
    tempfile.close()
    t,psname = mkstemp()
    pipe("enscript --margins 76::76: -B -q -p "+psname + " " +tempname)
    os.unlink(tempname)
    pipe("ps2pdf "+psname+" "+outpath)
    os.unlink(psname)

def session_draft_tarfile(request, num, session):
    drafts = session_draft_list(num, session);

    response = HttpResponse(mimetype='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s-drafts.tgz'%(session)
    tarstream = tarfile.open('','w:gz',response)
    mfh, mfn = mkstemp()
    manifest = open(mfn, "w")

    for doc_name in drafts:
        pdf_path = os.path.join(settings.INTERNET_DRAFT_PDF_PATH, doc_name + ".pdf")

        if (not os.path.exists(pdf_path)):
            convert_to_pdf(doc_name)

        if os.path.exists(pdf_path):
            try:
                tarstream.add(pdf_path, str(doc_name + ".pdf"))
                manifest.write("Included:  "+pdf_path+"\n")
            except Exception, e:
                manifest.write(("Failed (%s): "%e)+pdf_path+"\n")
        else:
            manifest.write("Not found: "+pdf_path+"\n")

    manifest.close()
    tarstream.add(mfn, "manifest.txt")
    tarstream.close()
    os.unlink(mfn)
    return response

def pdf_pages(file):
    try:
        infile = open(file, "r")
    except IOError:
        return 0
    for line in infile:
        m = re.match('\] /Count ([0-9]+)',line)
        if m:
            return int(m.group(1))
    return 0


def session_draft_pdf(request, num, session):
    drafts = session_draft_list(num, session);
    curr_page = 1
    pmh, pmn = mkstemp()
    pdfmarks = open(pmn, "w")
    pdf_list = ""

    for draft in drafts:
        pdf_path = os.path.join(settings.INTERNET_DRAFT_PDF_PATH, draft + ".pdf")
        if (not os.path.exists(pdf_path)):
            convert_to_pdf(draft)

        if (os.path.exists(pdf_path)):
            pages = pdf_pages(pdf_path)
            pdfmarks.write("[/Page "+str(curr_page)+" /View [/XYZ 0 792 1.0] /Title (" + draft + ") /OUT pdfmark\n")
            pdf_list = pdf_list + " " + pdf_path
            curr_page = curr_page + pages

    pdfmarks.close()
    pdfh, pdfn = mkstemp()
    pipe("gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=" + pdfn + " " + pdf_list + " " + pmn)

    pdf = open(pdfn,"r")
    pdf_contents = pdf.read()
    pdf.close()

    os.unlink(pmn)
    os.unlink(pdfn)
    return HttpResponse(pdf_contents, mimetype="application/pdf")

def get_meeting(num=None):
    if (num == None):
        meeting = Meeting.objects.filter(type="ietf").order_by("-date")[:1].get()
    else:
        meeting = get_object_or_404(Meeting, number=num)
    return meeting

def get_schedule(meeting, name=None):
    if name is None:
        schedule = meeting.agenda
    else:
        schedule = get_object_or_404(meeting.schedule_set, name=name)
    return schedule

def week_view(request, num=None):
    meeting = get_meeting(num)
    timeslots = TimeSlot.objects.filter(meeting__id = meeting.id)

    template = "meeting/week-view.html"
    return render_to_response(template,
            {"timeslots":timeslots,"render_types":["Session","Other","Break","Plenary"]}, context_instance=RequestContext(request))

def ical_agenda(request, num=None, schedule_name=None):
    meeting = get_meeting(num)

    q = request.META.get('QUERY_STRING','') or ""
    filter = urllib.unquote(q).lower().split(',');
    include = set(filter)
    include_types = set(["Plenary","Other"])
    exclude = []

    # Process the special flags.
    #   "-wgname" will remove a working group from the output.
    #   "~Type" will add that type to the output.
    #   "-~Type" will remove that type from the output
    # Current types are:
    #   Session, Other (default on), Break, Plenary (default on)
    # Non-Working Group "wg names" include:
    #   edu, ietf, tools, iesg, iab

    for item in include:
        if item:
            if item[0] == '-' and item[1] == '~':
                include_types -= set([item[2:3].upper()+item[3:]])
            elif item[0] == '-':
                exclude.append(item[1:])
            elif item[0] == '~':
                include_types |= set([item[1:2].upper()+item[2:]])

    schedule = get_schedule(meeting, schedule_name)
    scheduledsessions = get_scheduledsessions_from_schedule(schedule)

    scheduledsessions = scheduledsessions.filter(
        Q(timeslot__type__name__in = include_types) |
        Q(session__group__acronym__in = filter) |
        Q(session__group__parent__acronym__in = filter)
        ).exclude(Q(session__group__acronym__in = exclude))
        #.exclude(Q(session__group__isnull = False),
        #Q(session__group__acronym__in = exclude) |
        #Q(session__group__parent__acronym__in = exclude))

    if meeting.time_zone:
        try:
            tzfn = os.path.join(settings.TZDATA_ICS_PATH, meeting.time_zone + ".ics")
            tzf = open(tzfn)
            icstext = tzf.read()
            debug.show('icstext[:128]')
            vtimezone = re.search("(?sm)(\nBEGIN:VTIMEZONE.*\nEND:VTIMEZONE\n)", icstext).group(1).strip()
            debug.show('vtimezone[:128]')
            tzf.close()
        except IOError:
            vtimezone = None
    else:
        vtimezone = None

    return HttpResponse(render_to_string("meeting/agendaREDESIGN.ics",
        {"scheduledsessions":scheduledsessions, "meeting":meeting, "vtimezone": vtimezone },
        RequestContext(request)), mimetype="text/calendar")

def csv_agenda(request, num=None, name=None):
    timeslots, update, meeting, venue, ads, plenaryw_agenda, plenaryt_agenda = agenda_info(num, name)
    # we should really use the Python csv module or something similar
    # rather than a template file which is one big mess

    return HttpResponse(render_to_string("meeting/agenda.csv",
        {"timeslots":timeslots, "update":update, "meeting":meeting, "venue":venue, "ads":ads,
         "plenaryw_agenda":plenaryw_agenda, "plenaryt_agenda":plenaryt_agenda, },
        RequestContext(request)), mimetype="text/csv")

def meeting_requests(request, num=None) :
    meeting = get_meeting(num)
    sessions = Session.objects.filter(meeting__number=meeting.number,group__parent__isnull = False).exclude(requested_by=0).order_by("group__parent__acronym","status__slug","group__acronym")

    groups_not_meeting = Group.objects.filter(state='Active',type__in=['WG','RG','BOF']).exclude(acronym__in = [session.group.acronym for session in sessions]).order_by("parent__acronym","acronym")

    return render_to_response("meeting/requests.html",
        {"meeting": meeting, "sessions":sessions,
         "groups_not_meeting": groups_not_meeting},
        context_instance=RequestContext(request))

