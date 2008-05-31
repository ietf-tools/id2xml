# Copyright The IETF Trust 2007, All Rights Reserved

from django.db import models
from ietf.idtracker.models import Acronym, PersonOrOrgInfo, WGChair
import datetime
import random

# Only some of these status codes can be stored in the database.
# Some are completely unused; some are used but never stored.
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
    id_date = models.DateField()
    date_name = models.CharField(maxlength=255)
    f_name = models.CharField(blank=True, maxlength=255)
    def __str__(self):
        return self.date_name
    class Meta:
        db_table = 'id_dates'
        verbose_name = 'I-D Submission Date'
    class Admin:
        list_display = ('date_name', 'id_date')

class SubmissionEnv(models.Model):
    #max_live = models.IntegerField(help_text='Not used by the code')
    #max_interval = models.IntegerField(help_text='Not used by the code')
    current_manual_proc_date = models.IntegerField(help_text='Business days for manual submission')
    max_same_draft_name = models.IntegerField(help_text='Max versions/day permitted for drafts with the same draft name')
    max_same_draft_size = models.IntegerField(help_text='Max MB/day permitted for drafts with the same draft name')
    max_same_submitter = models.IntegerField(help_text='Max versions/day permitted for drafts with the same submitter')
    max_same_submitter_size = models.IntegerField(help_text='Max MB/day permitted for drafts with the same submitter')
    max_same_wg_draft = models.IntegerField(help_text='Max versions/day permitted for WGN drafts with the same WG ID')
    max_same_wg_draft_size = models.IntegerField(help_text='Max MB/day permitted for WGN drafts with the same WG ID')
    max_daily_submission = models.IntegerField(help_text='Max versions/day permitted via the tool')
    max_daily_submission_size = models.IntegerField(help_text='Max MB/day permitted via the tool')
    cut_off_time = models.TimeField(help_text='Time of day for submission cutoffs')
    cut_off_warn_days = models.IntegerField(help_text='Days before cutoff to display warning message')
    def __str__(self):
        if self.id == 1:
            return "I-D Submission Tool Configuration"
        else:
            return "Should not add -- only edit"
    def save(self):
        if not self.id:
            return # Can't create a new submission environment via admin -- edit the one that's there
        else:
            super(SubmissionEnv, self).save()
    class Meta:
        db_table = 'id_submission_env'
        verbose_name = 'I-D Submission Environment'
    class Admin:
        pass

class IdSubmissionDetail(models.Model):
    submission_id = models.AutoField(primary_key=True)
    # temp_id_document_tag = models.IntegerField(editable=False)        # obsolete
    status_id = models.IntegerField(default=0, choices=STATUS_CODE.items())
    last_updated_date = models.DateField(blank=True)
    last_updated_time = models.CharField(maxlength=100,blank=True)
    title = models.CharField(maxlength=255, db_column='id_document_name')
    group = models.ForeignKey(Acronym, db_column='group_acronym_id', raw_id_admin=True)
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
    wg_submission = models.BooleanField(default=0)
    filesize = models.IntegerField(null=True, blank=True)
    man_posted_date = models.DateField(null=True, blank=True)
    man_posted_by = models.CharField(blank=True, maxlength=255)
    first_two_pages = models.TextField(blank=True)
    sub_email_priority = models.IntegerField(null=True, blank=True)
    invalid_version = models.IntegerField(default=0)
    idnits_failed = models.BooleanField(default=0)
    submitter = models.ForeignKey(PersonOrOrgInfo, null=True, blank=True, db_column="submitter_tag", raw_id_admin=True)

    def submitter_email(self):
        # I don't like knowing this detail, but it's better than
        # scattering it.
        print self.submitter.person_or_org_tag
        print self.sub_email_priority
        if self.sub_email_priority == 1:
            return self.submitter.email()
        else:
            return self.submitter.email(priority=self.sub_email_priority, type='I-D')
    def get_absolute_url(self):
        return "/idsubmit/status/%d/" % self.submission_id
    def set_file_type(self, type_list):
        self.file_type = ','.join(type_list)
    def get_file_type_list(self):
        if self.file_type:
            return self.file_type.split(',')
        else:
            return None
    def valid_submitter(self, submitter_email):
        # The submitter is one of the authors.
        if self.authors.filter(email_address=submitter_email).count():
            return True

        # The submitter is one of the previous authors.
        if self.revision != '00' and \
           self.submitter.emailaddress_set.filter(priority = self.sub_email_priority, type='I-D').count():
            return True

        # The submitter is a WG chair.
        if WGChair.objects.filter(group_acronym=self.group, person=self.submitter):
            return True

        return False

    def save(self,*args,**kwargs):
        self.last_updated_date = datetime.date.today()
        self.last_updated_time = datetime.datetime.now().time()
        if self.submission_id is None:
            self.auth_key = ''.join([random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for i in range(35)])
        super(IdSubmissionDetail, self).save(*args,**kwargs)
        return self.submission_id

    def __str__(self):
        return 'Submission of %s-%s' % ( self.filename, self.revision )

    class Meta:
        db_table = 'id_submission_detail'
        verbose_name = 'I-D Submission Record'
    class Admin:
        date_hierarchy = 'submission_date'
        list_filter = [ 'status_id' ]
        list_display = ('filename', 'revision', 'submission_date', 'status_id')
        search_fields = ['filename']

class IdApprovedDetail(models.Model):
    filename = models.CharField(blank=True, maxlength=255, unique=True)
    approved_status = models.IntegerField(null=True, blank=True)
    approved_person = models.ForeignKey(PersonOrOrgInfo, db_column='approved_person_tag', raw_id_admin=True)
    approved_date = models.DateField(null=True, blank=True)
    recorded_by = models.ForeignKey(PersonOrOrgInfo, db_column='recorded_by', raw_id_admin=True, related_name='idsubmission_recorded')
    def __str__(self):
        return "I-D %s pre-approval" % self.filename
    class Meta:
        db_table = 'id_approved_detail'
        verbose_name = 'Pre-approved -00 I-D'
    class Admin:
        pass

class TempIdAuthors(models.Model):
    #id_document_tag = models.IntegerField(editable=False)      # obsolete
    first_name = models.CharField(maxlength=255, core=True)
    last_name = models.CharField(maxlength=255, core=True)
    email_address = models.EmailField() # maxlength=255
    last_modified_date = models.DateField(editable=False)
    last_modified_time = models.CharField(editable=False, maxlength=100)
    author_order = models.IntegerField(editable=False, default=0)
    submission = models.ForeignKey(IdSubmissionDetail, edit_inline=models.TABULAR, related_name="authors", editable=False)
    def save(self,*args,**kwargs):
        self.last_modified_date = datetime.date.today()
        self.last_modified_time = datetime.datetime.now().time()
        super(TempIdAuthors, self).save(*args,**kwargs)
    def email(self):
        return ( "%s %s" % ( self.first_name, self.last_name ), self.email_address )
    def __str__(self):
        return "%s %s authors %s" % ( self.first_name, self.last_name, self.submission )
    class Meta:
        db_table = 'temp_id_authors'
        unique_together = (("submission", "author_order"),)
        # This makes no sense when accessing the table directly.
        # However, all accesses will be via the related manager
        # from an IdSubmissionDetail, so it'll already be filtered
        # down to a submission.
        ordering = ("author_order",)
