from django.utils import simplejson as json
from dajaxice.core import dajaxice_functions
from dajaxice.decorators import dajaxice_register
from ietf.ietfauth.decorators import group_required
from django.http import HttpResponseRedirect, HttpResponse, Http404

from ietf.meeting.views  import get_meeting

from django.core import serializers

# New models
from ietf.meeting.models import Meeting, TimeSlot, Session, ScheduledSession, Room
from ietf.group.models import Group
import datetime

import logging
import sys
from ietf.settings import LOG_DIR

log = logging.getLogger(__name__)

@dajaxice_register
def sayhello(request):
    return json.dumps({'message':'Hello World'})

@group_required('Area_Director','Secretariat')
@dajaxice_register
def update_timeslot(request, session_id=None, scheduledsession_id=None):
    if(session_id == None or scheduledsession_id == None):
        if(scheduledsession_id == None):
            pass # most likely the user moved the item and dropped it in the same box. js should never make the call in this case.
        else:
            logging.debug("session_id=%s , scheduledsession_id=%s doing nothing and returning" % (session_id, scheduledsession_id))

        return

    # if(scheduledsession_id == "Unassigned"):
        
    #     return
    session_id = int(session_id)


    # log.info("%s is updating scheduledsession_id=%u to session_id=%u" %
    #          (request.user, ss_id, session_id))


    try:
       session = Session.objects.get(pk=session_id)
    except:
        return json.dumps({'error':'invalid session'})

    log.debug(session)
    
    ss_id = int(scheduledsession_id)
    for ss in session.scheduledsession_set.all():
        ss.session = None
        ss.save()

    try:
        # find the scheduledsession, assign the Session to it.
        if(ss_id == 0):
            ss.session = None
        else:
            ss = ScheduledSession.objects.get(pk=ss_id)
            ss.session = session
        ss.save()
    except Exception as e:
        return json.dumps({'error':'invalid scheduledsession'})

    return json.dumps({'message':'im happy!'})

#
# this get_info needs to be replaced once we figure out how to get rid of silly
# ajax state we are passing through.
@dajaxice_register
def get_info(request, scheduledsession_id=None, active_slot_id=None, timeslot_id=None, session_id=None):#, event):

    try:
        session = Session.objects.get(pk=int(session_id))
    except Session.DoesNotExist:
        logging.debug("No ScheduledSession was found for id:%s" % (session_id))
        # in this case we want to return empty the session information and perhaps indicate to the user there is a issue.
        return


    sess1 = session.json_dict(request.get_host_protocol())
    sess1['active_slot_id'] = str(active_slot_id)
    sess1['ss_id']          = str(scheduledsession_id)
    sess1['timeslot_id']    = str(timeslot_id)

    return json.dumps(sess1, sort_keys=True, indent=2)

def session_json(request, num, sessionid):
    meeting = get_meeting(num)

    try:
        session = meeting.session_set.get(pk=int(sessionid))
    except Session.DoesNotExist:
        return json.dumps({'error':"no such session %s" % sessionid})

    sess1 = session.json_dict(request.get_host_protocol())
    return HttpResponse(json.dumps(sess1, sort_keys=True, indent=2),
                        mimetype="text/json")

def meeting_json(request, meeting_num):
    meeting = get_meeting(meeting_num)
    #print "request is: %s\n" % (request.get_host_protocol())
    return HttpResponse(json.dumps(meeting.json_dict(request.get_host_protocol()),
                                   sort_keys=True, indent=2),
                        mimetype="text/json")

# current dajaxice does not support GET, only POST.
# it has almost no value for GET, particularly if the results are going to be
# public anyway.
def session_constraints(request, num=None, sessionid=None):
    meeting = get_meeting(num)

    print "Getting meeting=%s session contraints for %s" % (num, sessionid)
    try:
        session = meeting.session_set.get(pk=int(sessionid))
    except Session.DoesNotExist:
        return json.dumps({"error":"no such session"})

    constraint_list = session.constraints_dict(request.get_host_protocol())

    json_str = json.dumps(constraint_list,
                          sort_keys=True, indent=2),
    #print "  gives: %s" % (json_str)

    return HttpResponse(json_str, mimetype="text/json")



