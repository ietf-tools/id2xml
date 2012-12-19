from django.utils import simplejson
from dajaxice.core import dajaxice_functions
from dajaxice.decorators import dajaxice_register

# New models
from ietf.meeting.models import Meeting, TimeSlot, Session, ScheduledSession, Room
from ietf.group.models import Group
import datetime


@dajaxice_register
def sayhello(request):
    return simplejson.dumps({'message':'Hello World'})


@dajaxice_register
def update_timeslot(request, new_event):
    # get the ScheduledSession. 
    ss = ScheduledSession.objects.get(id=int(new_event["session_id"]))
    try:
        # find the timeslot, assign it to the ScheduledSession's timeslot, save it. 
        slots = TimeSlot.objects.get(id=int(new_event["timeslot_id"]))
        ss.timeslot = slots
        ss.save()
        
    except Exception as e:
        print e

    return simplejson.dumps({'message':'im happy!'})
