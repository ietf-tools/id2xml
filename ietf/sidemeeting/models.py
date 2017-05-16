from __future__ import unicode_literals
# -*- coding: utf-8 -*-
from django.db import models
from ietf.name.models import NameModel
from ietf.meeting.models import Meeting, ResourceAssociation, Session
from ietf.name.models import MeetingTypeName, TimeSlotTypeName, SessionStatusName, ConstraintName, RoomResourceName
import datetime as dt
from django.utils.timezone import now
from django.core.mail import send_mail
from ietf.person.models import Person


# class SideTypeName(NameModel):
#     """ IETF, IRTF, IAB,  "Corporate", "Non-profit" """
#     test = models.CharField(max_length=64)        
    

class SideMeetingSession(Session):
    requested_prim_start_time = models.DateTimeField()
    requested_alt_start_time = models.DateTimeField()    
#    sidemeeting_type = models.ForeignKey(SideTypeName,db_constraint=False)
    attendance = models.PositiveIntegerField(default=0)    
    
    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ["name", "id"]
        managed = False

