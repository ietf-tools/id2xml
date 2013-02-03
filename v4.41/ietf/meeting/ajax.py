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
    print "got the slot, now trying to assign it a time"
    try:
        print "slots.time:", slots.time
        print "slots.duration:", slots.duration
        print "slots.meeting.date:",slots.meeting.date
        print type(slots.time)
        print "slots.session:",slots.session
        h = int(new_event["time"][:2])
        m = int(new_event["time"][2:4])
        new_date = new_event["date"].split('-')
        sess = slots.session.id
        print sess

        new_time = slots.time.replace(hour=h, minute=m, year=int(new_date[0]), month=int(new_date[1]),day=int(new_date[2]))
        print new_time
        slots.time = new_time
        print slots.duration
        slots.save()

        #slots.time = int(new_event['time'])
    except Exception as e:
        print "error!"
        print e
#    print slots.time
#    print new_event['time']
#    slots.time = 
    print "found this timeslot:",slots
    return simplejson.dumps({'message':'im happy!'})
