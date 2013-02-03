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
    print "got to me"
    print new_event
    print int(new_event["session_id"])
    print int(new_event["timeslot_id"])
    ss = ScheduledSession.objects.get(id=int(new_event["session_id"]))
    try:
        slots = TimeSlot.objects.get(id=int(new_event["timeslot_id"]))
        print slots
        print "new_event[session_id]", new_event["session_id"]
        print ss
        ss.timeslot = slots
        ss.save()
        
#    timeslot = 
    
#     try:
#         #print "slots.time:", slots.timeslot.time
#         print "slots.time:", slots.timeslot.time
#         print "slots.timeslot.duration:", slots.timeslot.duration
#         print "slots.timeslot.meeting.date:",slots.timeslot.meeting.date
#         # print type(slots.time)
#         # print "slots.session:",slots.session
#         h = int(new_event["time"][:2])
#         m = int(new_event["time"][2:4])
#         new_date = new_event["date"].split('-')
#         print new_date
#         # sess = slots.session.id
#         # print sess
#         print new_event["room"], type(new_event["room"])
#         room = new_event["room"]
#         room = room.replace('-',' ')
#         print room
#         datetime_obj = datetime.datetime(hour=h, minute=m, year=int(new_date[0]), month=int(new_date[1]),day=int(new_date[2]))

#         rm = Room.objects.filter(name=room)
#         ts = TimeSlot.objects.filter(time=datetime_obj, location=rm)
#         for t in ts:
#             print "timeslot:", t
#         print "done"
# #        y = ScheduledSession.filter()
# #hour=h, minute=m, year=int(new_date[0]), month=int(new_date[1]),day=int(new_date[2]))
#       #  print x
#         #print y
#         # new_time = slots.time.replace(hour=h, minute=m, year=int(new_date[0]), month=int(new_date[1]),day=int(new_date[2]))
#         # print new_time
#         # slots.time = new_time
#         # print slots.duration
#         # #slots.save()

#         # #slots.time = int(new_event['time'])
    except Exception as e:
        print "error! ->>", e, "<<-"

    return simplejson.dumps({'message':'im happy!'})
