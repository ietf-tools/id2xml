from django.db import models
from ietf.idtracker.models import PersonOrOrgInfo

class RfcAuthor(models.Model):
    id = models.IntegerField(primary_key=True)
    rfc_number = models.IntegerField(unique=True)
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag', raw_id_admin=True, unique=True)
    def __str__(self):
        return "%s, %s" % ( self.person.last_name, self.person.first_name)
    class Meta:
        db_table = 'rfc_authors'
	verbose_name = 'RFC Author'
    class Admin:
	pass

class RfcIntendedStatus(models.Model):
    intended_status_id = models.IntegerField(primary_key=True)
    status_value = models.CharField(maxlength=25)
    def __str__(self):
        return self.status_value
    class Meta:
        db_table = 'rfc_intend_status'
	verbose_name = 'RFC Intended Status Field'
    class Admin:
	pass

class RfcStatus(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_value = models.CharField(maxlength=25)
    def __str__(self):
        return self.status_value
    class Meta:
        db_table = 'rfc_status'

class RfcsObsolete(models.Model):
    id = models.IntegerField(primary_key=True)
    rfc_number = models.IntegerField(unique=True)
    action = models.CharField(unique=True, maxlength=20)
    rfc_acted_on = models.IntegerField(unique=True)
    def __str__(self):
        return "RFC%04d %s RFC%04d" % (self.rfc_number, self.action, self.rfc_acted_on)
    class Meta:
        db_table = 'rfcs_obsolete'

class Rfc(models.Model):
    rfc_number = models.IntegerField(primary_key=True)
    rfc_name = models.CharField(maxlength=200)
    rfc_name_key = models.CharField(maxlength=200)
    group_acronym = models.CharField(blank=True, maxlength=8)
    area_acronym = models.CharField(blank=True, maxlength=8)
    status = models.ForeignKey(RfcStatus, db_column="status_id")
    intended_status = models.ForeignKey(RfcIntendedStatus, db_column="intended_status_id")
    fyi_number = models.CharField(blank=True, maxlength=20)
    std_number = models.CharField(blank=True, maxlength=20)
    txt_page_count = models.IntegerField(null=True, blank=True)
    online_version = models.CharField(blank=True, maxlength=3)
    rfc_published_date = models.DateField(null=True, blank=True)
    proposed_date = models.DateField(null=True, blank=True)
    draft_date = models.DateField(null=True, blank=True)
    standard_date = models.DateField(null=True, blank=True)
    historic_date = models.DateField(null=True, blank=True)
    lc_sent_date = models.DateField(null=True, blank=True)
    lc_expiration_date = models.DateField(null=True, blank=True)
    b_sent_date = models.DateField(null=True, blank=True)
    b_approve_date = models.DateField(null=True, blank=True)
    comments = models.TextField(blank=True)
    last_modified_date = models.DateField()
    def __str__(self):
	    return "RFC%04d" % ( self.rfc_number )        
    class Meta:
        db_table = 'rfcs'
	verbose_name = 'RFC'
	verbose_name_plural = 'RFCs'
    class Admin:
	pass

