from __future__ import unicode_literals

from django.db import models
from ietf.meeting.models import Meeting
from ietf.name.models import MeetingTypeName, TimeSlotTypeName, SessionStatusName, ConstraintName, RoomResourceName

class SideMeeting(models.Model):

    name = models.CharField(unique=True, max_length=64)
    email = models.EmailField()
    phone = models.CharField(min_length=3,max_length=256)
    mtg = models.ForeignKey(Meeting)
    mtgdate = models.DateField()
    altmtgdate = models.DateField()
    days = models.IntegerField(max_value=14)
    mtgtype = models.ForeignKey(MeetingTypeName)
    addcontact = models.CharField(max_length=256)
    addemail = models.EmailField()    
    addphone = models.CharField(max_length=256)
    attendance = models.PositiveIntegerField(max_value=100000)
    mtgstart = models.DateTimeField()
    mtgend = models.DateTimeField()
    roomconfig = models.CharField(max_length=256)    
    speakerphone = models.BooleanField(default=False)
    projector = models.BooleanField(default=False)
    food = models.BooleanField(default=False)
    comments = models.TextField(default="")    

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ["name", "id"]

