# Copyright The IETF Trust 2007, All Rights Reserved

from django.db import models
from ietf.idtracker.models import Acronym, PersonOrOrgInfo
import datetime
import random
#from ietf.utils import log
STATUS_CODE = {
    0   : 'Ready To Post',
    1   : 'Uploaded',
    2   : 'ID NITS Passed',
    3   : 'Initial Version Approval Required',
    4   : 'Submitter Authentication Requested',
    5   : 'Manual Post Requested',
    6   : 'External Meta-Data Required',
    7   : 'Internal Database Has Been Updated',
    8   : 'ID Announcement Scheduled',
    9   : 'ID Tracker Notification Scheduled',
    10  : 'Initial Version Approval Requested',
    11  : 'Initial Version Approved',
    -1  : 'Posted by the tool',
    -2  : 'Posted by the Secretariat',
    -3  : 'Dead',
    -4  : 'Cancelled',
    101 : 'Plain text version does not exist',
    102 : 'File size is larger than 20 Mb',
    103 : 'Duplicate Internet-Draft submission is currently in process',
    104 : 'Simultaneous submission from the same IP address',
    105 : 'Auth key does not match',
    106 : 'No such Internet-Draft is currently in process',
    107 : 'Draft is not in an appropriate status for the requested page',
    108 : 'Unknown Request',
    109 : 'Invalid Email Address',
    110 : 'Direc Access is prohibited',
    111 : 'The document does not contain a legitimate filename that start with draft-* and ends with -NN[.txt] where NN indicates revision number',
    112 : 'Filename contains non alpha-numeric character',
    201 : 'Invalid version number',
    202 : 'Invalid filename',
    203 : 'IDNITS are not validated',
    204 : 'Creation Date must be within 3 days of the submission date',
    205 : 'Not a valid submitter',
    206 : 'Incorrect Meta Data'
}

class IdDates(models.Model):
    id = models.IntegerField(primary_key=True)
    id_date = models.DateField(null=True, blank=True)
    date_name = models.CharField(blank=True, maxlength=765)
    f_name = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'id_dates'
    class Admin:
        pass

class SubmissionEnv(models.Model):
    max_live = models.IntegerField()
    max_interval = models.IntegerField()
    current_manual_proc_date = models.IntegerField()
    max_same_draft_name = models.IntegerField()
    max_same_draft_size = models.IntegerField()
    max_same_submitter = models.IntegerField()
    max_same_submitter_size = models.IntegerField()
    max_same_wg_draft = models.IntegerField()
    max_same_wg_draft_size = models.IntegerField()
    max_daily_submission = models.IntegerField()
    max_daily_submission_size = models.IntegerField()
    cut_off_time = models.IntegerField()
    class Meta:
        db_table = 'id_submission_env'
    class Admin:
        pass

class IdSubmissionDetail(models.Model):
    submission_id = models.AutoField(primary_key=True)
    # temp_id_document_tag = models.IntegerField(editable=False)	# obsolete
    status_id = models.IntegerField(default=0)
    last_updated_date = models.DateField(blank=True)
    last_updated_time = models.CharField(maxlength=100,blank=True)
    title = models.CharField(maxlength=255, db_column='id_document_name')
    group = models.ForeignKey(Acronym, db_column='group_acronym_id')
    filename = models.CharField(maxlength=255) # in real mode , unique=True)
    creation_date = models.DateField(null=True, blank=True)
    submission_date = models.DateField(default=datetime.date.today)
    remote_ip = models.IPAddressField(blank=True, maxlength=100)
    revision = models.CharField(blank=True, maxlength=2)
    auth_key = models.CharField(blank=True, maxlength=35)
    idnits_message = models.TextField(blank=True)
    file_type = models.CharField(blank=True, maxlength=20)
    comment_to_sec = models.TextField(blank=True)
    abstract = models.TextField()
    txt_page_count = models.IntegerField()
    error_message = models.CharField(blank=True, maxlength=255)
    warning_message = models.TextField(blank=True)
    wg_submission = models.IntegerField(null=True, blank=True)
    filesize = models.IntegerField(null=True, blank=True)
    man_posted_date = models.DateField(null=True, blank=True)
    man_posted_by = models.CharField(blank=True, maxlength=255)
    first_two_pages = models.TextField(blank=True)
    sub_email_priority = models.IntegerField(null=True, blank=True)
    invalid_version = models.IntegerField(default=0)
    idnits_failed = models.BooleanField(default=0)
    submitter = models.ForeignKey(PersonOrOrgInfo, null=True, blank=True, db_column="submitter_tag")

    def get_absolute_url(self):
        return "/idsubmit/status/%d" % self.submission_id
    def set_file_type(self, type_list):
        self.file_type = ','.join(type_list)
    def get_file_type_list(self):
        if self.file_type:
            return self.file_type.split(',')
        else:
            return None
    def save(self,*args,**kwargs):
	self.last_updated_date = datetime.date.today()
	# self.creation_date = datetime.date.today()
	self.last_updated_time = datetime.datetime.now().time()
        # self.submitter = PersonOrOrgInfo()
        self.auth_key = ''.join([random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(35)])

	super(IdSubmissionDetail, self).save(*args,**kwargs)
        return self.submission_id

    class Meta:
        db_table = 'id_submission_detail'

class IdApprovedDetail(models.Model):
    filename = models.CharField(blank=True, maxlength=255)
    approved_status = models.IntegerField(null=True, blank=True)
    approved_person = models.ForeignKey(PersonOrOrgInfo, db_column='approved_person_tag', raw_id_admin=True)
    approved_date = models.DateField(null=True, blank=True)
    recorded_by = models.IntegerField(null=True, blank=True)
    def __str__(self):
	return "I-D %s pre-approval" % self.filename
    class Meta:
        db_table = 'id_approved_detail'
    class Admin:
	pass

class TempIdAuthors(models.Model):
    #id_document_tag = models.IntegerField(editable=False) 	# obsolete
    first_name = models.CharField(blank=True, maxlength=255)
    last_name = models.CharField(blank=True, maxlength=255)
    email_address = models.CharField(blank=True, maxlength=255)
    last_modified_date = models.DateField(null=True, blank=True)
    last_modified_time = models.CharField(blank=True, maxlength=100)
    author_order = models.IntegerField(default=0)
    submission = models.ForeignKey(IdSubmissionDetail)
    def save(self,*args,**kwargs):
        self.last_modified_date = datetime.date.today()
        self.last_modified_time = datetime.datetime.now().time()
        super(TempIdAuthors, self).save(*args,**kwargs)
    class Meta:
        db_table = 'temp_id_authors'

