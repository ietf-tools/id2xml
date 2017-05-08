from __future__ import unicode_literals

from django.db import models
from ietf.meeting.models import Meeting
from ietf.name.models import MeetingTypeName, TimeSlotTypeName, SessionStatusName, ConstraintName, RoomResourceName
import datetime as dt
from django.utils.timezone import now

class SideMeeting(models.Model):

    name = models.CharField(default='', unique=True, max_length=64)
    email = models.EmailField(default="dummy@amsl.com")
    phone = models.CharField(max_length=256)
    mtg = models.ForeignKey(Meeting)
    mtgdate = models.DateField(default=now)
    altmtgdate = models.DateField(default=now)
    days = models.IntegerField(default=1)
    mtgtype = models.ForeignKey(MeetingTypeName)
    addcontact = models.CharField(default='', max_length=256)
    addemail = models.EmailField(default='')    
    addphone = models.CharField(default='', max_length=256)
    attendance = models.PositiveIntegerField(default=0)
    mtgstart = models.DateTimeField(default=now)
    mtgend = models.DateTimeField(default=now)
    roomconfig = models.CharField(default='', max_length=256)    
    speakerphone = models.BooleanField(default=False)
    projector = models.BooleanField(default=False)
    food = models.BooleanField(default=False)
    comments = models.TextField(default="")    

    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ["name", "id"]

