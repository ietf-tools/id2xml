# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from ietf.name.models import NameModel, TimeSlotTypeName
from ietf.meeting.models import Session
from ietf.group.models import Group


class SideMeetingTypeName(NameModel):
    """ IETF, IRTF, IAB,  "Corporate", "Non-profit" """
    test = models.CharField(max_length=64)
    

class SideMeetingSession(Session):
    requested_prim_start_time = models.DateTimeField()
    requested_alt_start_time = models.DateTimeField()    
    sidemeeting_type = models.ForeignKey(SideMeetingTypeName)
    area = models.ForeignKey(Group, blank=True)
    attendance = models.PositiveIntegerField(default=0)    
    
    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ["name", "id"]

