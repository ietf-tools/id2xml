from django.utils import simplejson
from dajaxice.core import dajaxice_functions
from dajaxice.decorators import dajaxice_register

# New models
from ietf.meeting.models import Meeting, TimeSlot, Session, ScheduledSession, Room
from ietf.group.models import Group
import datetime

import logging
log = logging.getLogger(__name__)

@dajaxice_register
def sayhello(request):
    return simplejson.dumps({'message':'Hello World'})


@dajaxice_register
def update_timeslot(request, new_event):
    # get the ScheduledSession.
    ss_id = int(new_event["session_id"])
    timeslot_id = int(new_event["timeslot_id"])
    
    log.info("updating scheduledsession_id=%u to timeslot_id=%u" % (ss_id, timeslot_id))
    ss = ScheduledSession.objects.get(id=ss_id)
    try:
        # find the timeslot, assign it to the ScheduledSession's timeslot, save it. 
        slots = TimeSlot.objects.get(id=timeslot_id)
        ss.timeslot = slots
        ss.save()
        
    except Exception as e:
        print e

    return simplejson.dumps({'message':'im happy!'})
