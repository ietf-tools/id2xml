from django.db import models

from ietf.idtracker.models import PersonOrOrgInfo

# Create your models here.

class WGCharterInfo(models.Model):
    id = models.AutoField(primary_key=True)
    wg_acronym = models.CharField(maxlength=30,blank=True,null=True,unique=True)
    #ietfwg_id = models.IntegerField(null=False,editable=False)

class CharterVersion(models.Model):
    version_id = models.AutoField(primary_key=True)
    STATE_CHOICES = (
	('draft','Draft'),
	('ad','AD Review'),
	('internal','Internal IESG Review'),
	('external','Sent to IETF Last Call'),
	('approved','Approved'),
	('dead','Entombed'),
	)
    creation_date_time = models.DateTimeField(null=True, blank=True)
    state = models.CharField(maxlength=30,choices=STATE_CHOICES,blank=False,default='draft')
    wg_charter_info = models.ForeignKey(WGCharterInfo,null=True)
    text = models.TextField(blank=True)
    submitter = models.ForeignKey(PersonOrOrgInfo,null=True,editable=False)


    

