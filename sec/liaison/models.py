from django.db import models
from sec.core.models import PersonOrOrgInfo

class FromBodies(models.Model):
    from_id = models.AutoField(primary_key=True)
    body_name = models.CharField(blank=True, max_length=35)
    poc = models.ForeignKey(PersonOrOrgInfo, db_column='poc', null=True)
    is_liaison_manager = models.BooleanField()
    other_sdo = models.BooleanField()
    email_priority = models.IntegerField(null=True, blank=True)
    def __unicode__(self):
	return self.body_name
    class Meta:
        db_table = 'from_bodies'
        ordering = ['body_name']
