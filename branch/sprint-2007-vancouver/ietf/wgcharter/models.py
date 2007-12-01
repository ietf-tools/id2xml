from django.db import models

from ietf.idtracker.models import PersonOrOrgInfo

# Create your models here.


class WGCharterInfo(models.Model):
    id = models.AutoField(primary_key=True)
    #approvedVersion = models.ForeignKey(CharterVersion,null=True,editable=False)
    #recentDraftVersion = models.ForeignKey(CharterVersion,null=True,editable=False)

class CharterVersion(models.Model):
    version_id = models.AutoField(primary_key=True)
    STATE_CHOICES = (
	('draft','Draft'),
	('lastCalled','Sent to IETF Last Call'),
	('approved','Approved'),
	)
    creation_date = models.DateField(null=True, blank=True)
    state = models.CharField(maxlength=30,choices=STATE_CHOICES,blank=False,default='draft')
    wg_charter_info = models.ForeignKey(WGCharterInfo,null=True,editable=False)
    text = models.TextField(blank=True)
    submitter = models.ForeignKey(PersonOrOrgInfo,null=False,editable=False)
    

    

