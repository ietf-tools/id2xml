# Copyright The IETF Trust 2008, All Rights Reserved

# Portion Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved. Contact: Pasi Eronen <pasi.eronen@nokia.com>
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
# 
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
# 
#  * Neither the name of the Nokia Corporation and/or its
#    subsidiary(-ies) nor the names of its contributors may be used
#    to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from ietf.idtracker.models import Area, IETFWG
from ietf.proceedings.models import Meeting, WgMeetingSession, WgAgenda
# MeetingTime, MeetingVenue, IESGHistory, Proceeding, Switches, WgProceedingsActivities
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.conf import settings
from ietf.idrfc.views_search import SearchForm, search_query

def wg_summary_acronym(request):
    areas = Area.active_areas()
    wgs = IETFWG.objects.filter(status=IETFWG.ACTIVE)
    return HttpResponse(loader.render_to_string('wginfo/1wg-summary-by-acronym.txt', {'area_list': areas, 'wg_list': wgs}),mimetype='text/plain; charset=UTF-8')

def wg_summary_area(request):
    wgs = IETFWG.objects.filter(status='1',start_date__isnull=False)
    return HttpResponse(loader.render_to_string('wginfo/1wg-summary.txt', {'wg_list': wgs}),mimetype='text/plain; charset=UTF-8')

def wg_charters(request):
    wgs = IETFWG.objects.filter(status='1',start_date__isnull=False)
    return HttpResponse(loader.render_to_string('wginfo/1wg-charters.txt', {'wg_list': wgs}),mimetype='text/plain; charset=UTF-8')

def wg_charters_by_acronym(request):
    wgs = IETFWG.objects.filter(status='1',start_date__isnull=False)
    return HttpResponse(loader.render_to_string('wginfo/1wg-charters-by-acronym.txt', {'wg_list': wgs}),mimetype='text/plain; charset=UTF-8')

def wg_dir(request):
    areas = Area.active_areas()
    return render_to_response('wginfo/wg-dir.html', {'areas':areas}, RequestContext(request))

def wg_documents(request, acronym):
    wg = get_object_or_404(IETFWG, group_acronym__acronym=acronym, group_type=1)
    concluded = (wg.status_id != 1)
    form = SearchForm({'by':'group', 'group':str(wg.group_acronym.acronym),
                       'rfcs':'on', 'activeDrafts':'on'})
    if not form.is_valid():
        raise ValueError("form did not validate")
    (docs,meta) = search_query(form.cleaned_data)
    return render_to_response('wginfo/wg_documents.html', {'wg': wg, 'concluded':concluded, 'selected':'documents', 'docs':docs, 'meta':meta}, RequestContext(request))

def wg_charter(request, acronym):
    wg = get_object_or_404(IETFWG, group_acronym__acronym=acronym, group_type=1)
    concluded = (wg.status_id != 1)
    return render_to_response('wginfo/wg_charter.html', {'wg': wg, 'concluded':concluded, 'selected':'charter'}, RequestContext(request))

def meeting_info(num=None, acronym=None):
    if num:
        meetings = [ num ]
    else:
        if acronym:
            meetings = list(Meeting.objects.all())
        else:
            meetings = list(Meeting.objects.all())
        meetings.reverse()
        meetings = [ meeting.meeting_num for meeting in meetings ]

    for n in meetings:
        try:
            meeting= Meeting.objects.get(meeting_num=n)
            break
        except (Meeting.DoesNotExist):
            continue
    else:
        raise Http404("No agenda for meeting %s available" % num)

    return meeting

def wg_text(filename=None, typestr="file"):
    if not filename:
        text = "Sorry, no "+ typestr +" available as of today. Either no meeting was held, or the document has not yet been submitted."
    else:
        try:
            text_file = open(filename)
            text = text_file.read()
        except BaseException:
            text =  'Error loading work group ' + typestr # + ' filename ' + filename

    return text

def wg_agenda_text(filename=None):
    return wg_text(filename, "agenda")

def wg_minutes_text(filename=None):
    return wg_text(filename, "minutes")

def wg_meeting(request, acronym=None, num=None):
    wg = get_object_or_404(IETFWG, group_acronym__acronym=acronym, group_type=1)
    concluded = (wg.status_id != 1)
    sessions = WgMeetingSession.objects.all().filter(group_acronym_id=wg.group_acronym.acronym_id)
    if not num:
        session = list(sessions)[-1]
    else:
        session = WgMeetingSession.objects.all().filter(group_acronym_id=wg.group_acronym.acronym_id, meeting__meeting_num=num).get()

    sess_meeting_date1 = None;
    sess_meeting_date2 = None;
    sess_meeting_date3 = None;
    if session and session.sched_time_id1:
        sess_meeting_date1 = session.sched_time_id1.meeting_date()
    if session and session.sched_time_id2:
        sess_meeting_date2 = session.sched_time_id1.meeting_date()
    if session and session.sched_time_id3:
        sess_meeting_date3 = session.sched_time_id1.meeting_date()

    if not num:
        meeting = meeting_info(session.meeting.meeting_num)
    else:
        meeting = meeting_info(num)
 
    agenda_prefix = settings.AGENDA_PATH
    url_prefix = settings.AGENDA_URL

    slides = session.slides()
    for slide in slides:
        slide.filename = slide.file_loc()
        if slide.filename and url_prefix:
            slide.filename = url_prefix + slide.file_loc()

    agenda_file = session.agenda_file()
    if agenda_file and agenda_prefix:
        agenda_file = agenda_prefix + agenda_file
    agenda_text = wg_agenda_text(agenda_file)
    agenda_type = "text";
    if agenda_file[-5:].lower() == ".html":
        agenda_type = "html";
    elif agenda_file[-4:].lower() == ".htm":
        agenda_type = "html";

    minutes_file = session.minute_file()
    if minutes_file and agenda_prefix:
        minutes_file = agenda_prefix + minutes_file
    minutes_text = wg_minutes_text(minutes_file)
    minutes_type = "text";
    if minutes_file[-5:] == ".html":
        minutes_type = "html";
    elif minutes_file[-4:] == ".htm":
        minutes_type = "html";

    template = "wginfo/wg_meeting.html"
    return render_to_response(template,
            {'wg':wg, 'concluded':concluded, 'meeting':meeting, 'session':session, 'sessions':sessions,
                'agenda':agenda_text, 'agenda_type':agenda_type, 'minutes':minutes_text, 'minutes_type':minutes_type,
                'meeting_date1':sess_meeting_date1, 'meeting_date2':sess_meeting_date2, 'meeting_date3':sess_meeting_date3,
                'slides':slides, 'selected':'meeting'}, RequestContext(request))
