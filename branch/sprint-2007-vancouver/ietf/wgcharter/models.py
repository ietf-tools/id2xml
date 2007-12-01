from django.db import models

from ietf.idtracker import models

# Create your models here.


class CharterVersion(models.Model):
    STATE_CHOICES = (
	('draft','Draft'),
	('lastCalled','Sent to IETF Last Call'),
	('approved','Approved'),
	)
     version_id = models.AutoField(primary_key=True)
     creation_date = models.DateField(null=True, blank=True)
     state = models.CharField(maxlength=30,choices=STATE_CHOICES,blank=False,default='draft')
     text = models.TextField(blank=True)
     submitter = models.ForeignKey(PersonOrOrgInfo,null=False,editable=False)

class WGCharterInfo:
    id = models.AutoField(primary_key=True)
    approvedVersion = models.ForeignKey(CharterVersion,null=True,editable=False)
    recentDraftVersion = models.ForeignKey(CharterVersion,null=True,editable=False)


