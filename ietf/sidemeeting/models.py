from __future__ import unicode_literals

from django.db import models
from ietf.meeting.models import Meeting, ResourceAssociation, Session
from ietf.name.models import MeetingTypeName, TimeSlotTypeName, SessionStatusName, ConstraintName, RoomResourceName
import datetime as dt
from django.utils.timezone import now
from django.core.mail import send_mail
from ietf.person.models import Person

class SideMeetingSessionTypeName(models.Model):
    # "IETF", "IRTF", "Corporate", "Non-profit", 'related_group'
    name = models.CharField(default='', unique=True,  max_length=255)

    
class SideMeetingSession(Session):
    requested_prim_start_time = models.DateTimeField()
    requested_alt_start_time = models.DateTimeField()    
    sidemeeting_type = models.ForeignKey(SideMeetingSessionTypeName)
    contact_name = models.CharField(blank=True,default='', max_length=256)
    contact_email = models.EmailField(blank=True,default='')
    attendance = models.PositiveIntegerField(default=0)    

    notified = models.BooleanField(default=False)
    notified_date = models.DateTimeField(default=now)
    notified_by = models.ForeignKey(Person, related_name="notified_by")
      
    approved = models.BooleanField(default=False)
    approved_date = models.DateTimeField(default=now)
    approved_by = models.ForeignKey(Person, related_name="approved_by")
    
    def __unicode__(self):
        return u"%s" % self.name

    class Meta:
        ordering = ["name", "id"]

    

# class SideMeeting0(models.Model):
#     name = models.CharField(max_length=64)
#     requester_name = models.CharField(max_length=64)    
#     requester_email = models.EmailField()
#     requester_phone = models.CharField(max_length=256, blank=True)
#     meeting = models.ForeignKey(Meeting)
#     date = models.DateField(default=now)
#     alt_date = models.DateField(default=now)
#     days = models.IntegerField(default=1)
#     type = models.ForeignKey(MeetingTypeName)
#     contact_name = models.CharField(blank=True,default='', max_length=256)
#     contact_email = models.EmailField(blank=True,default='')
#     attendance = models.PositiveIntegerField(default=0)
#     start_time = models.DateTimeField(default=now)
#     end_time = models.DateTimeField(default=now)  
#     resources = models.ManyToManyField(ResourceAssociation, blank=True)
#     comments = models.TextField(blank=True,default='')          
#     # notified = models.BooleanField(default=False)
#     # notified_date = models.DateTimeField(default=now)
#     # notified_by = models.ForeignKey(User)        
#     # approved = models.BooleanField(default=False)
#     # approved_date = models.DateTimeField(default=now)
#     # approved_by = models.ForeignKey(User)


#     # def save(self, *args, **kwargs):
#     #     if created:
#     #         pass
            
#     def __unicode__(self):
#         return u"%s" % self.name

#     class Meta:
#         ordering = ["name", "id"]

