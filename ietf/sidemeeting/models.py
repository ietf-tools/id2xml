# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from ietf.name.models import NameModel, TimeSlotTypeName
from ietf.meeting.models import Session
from ietf.group.models import Group


class SideMeetingTypeName(NameModel):
    """ IETF, IRTF, IAB,  "Corporate", "Non-profit" """
    

class SideMeetingSession(Session):
    requested_prim_start_date = models.DateTimeField()
    requested_alt_start_date = models.DateTimeField()
    requested_start_time = models.CharField(max_length=5)
    sidemeeting_type = models.ForeignKey(SideMeetingTypeName)
    
    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ["name", "id"]

