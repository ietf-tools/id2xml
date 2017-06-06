# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from ietf.meeting.models import Session
from ietf.name.models import NameModel


class SideMeetingTypeName(NameModel):
    """ IETF, IRTF, IAB,  "Corporate", "Non-profit" (installed by migrations) """
    

class SideMeetingSession(Session):
    """This is a subclass"""
    requested_prim_start_date = models.DateTimeField()
    requested_alt_start_date = models.DateTimeField()
    requested_start_time = models.CharField(max_length=5)
    sidemeeting_type = models.ForeignKey(SideMeetingTypeName)
    
    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ["name", "id"]

