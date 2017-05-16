from __future__ import unicode_literals
# -*- coding: utf-8 -*-
from django.db import models
from ietf.name.models import NameModel, TimeSlotTypeName
from ietf.meeting.models import Session


class SideMeetingType(NameModel):
    """ IETF, IRTF, IAB,  "Corporate", "Non-profit" """
    test = models.CharField(max_length=64)
    

class SideMeetingSession(Session):
    requested_prim_start_time = models.DateTimeField()
    requested_alt_start_time = models.DateTimeField()    
    sidemeeting_type = models.ForeignKey(SideMeetingType)
    attendance = models.PositiveIntegerField(default=0)    
    
    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ["name", "id"]

