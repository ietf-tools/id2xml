from django.utils import simplejson
from dajaxice.core import dajaxice_functions
from dajaxice.decorators import dajaxice_register

# New models
from ietf.meeting.models import Meeting, TimeSlot, Session
from ietf.group.models import Group


@dajaxice_register
def sayhello(request):
    return simplejson.dumps({'message':'Hello World'})


@dajaxice_register
def update_timeslot(request, new_event):
    print "got to me"
    print new_event
    print int(new_event["django_id"])
    slots = TimeSlot.objects.get(id=int(new_event["django_id"]))
    print "found this timeslot:",slots
    return simplejson.dumps({'message':'im happy!'})
