# Copyright The IETF Trust 2007, All Rights Reserved

from django.db import models
from ietf.idtracker.models import Acronym, PersonOrOrgInfo, WGChair, InternetDraft, IETFWG, EmailAddress
from utils import sync_docs
import datetime
import random
from django.conf import settings

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

    def posted(self):
        return self.status_id in ( -1, -2 )
    def can_be_cancelled(self):
        return self.status_id > 0 and self.status_id < 100
    def meta_error(self):
        return self.status_id > 200
    def submitter_email(self):
        # I don't like knowing this detail, but it's better than
        # scattering it.  The email_priority can be a small integer
        # if it's one of the known INET addresses for a person;
        # otherwise it's an I-D identifier.
        if self.sub_email_priority < 50:
            type = 'INET'
        else:
            type = 'I-D'
        return self.submitter.email(priority=self.sub_email_priority, type=type)
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
    class ApprovalError(Exception):
        pass
    def approved(self):
        """The submission has been approved, either by the submitter
        submitting the key when auto_post is available, by the wg chair
        or secretariat by approving the -00, or by the secretariat when
        doing manual posting."""

        submission = self

        # Copy Document(s) to production servers:
        try :
            (result, msg) = sync_docs(submission)
            if not result:
                raise self.ApprovalError(msg)
        except OSError :
            raise self.ApprovalError("There was a problem occurred while posting the document to the public server")
        # populate table

        try:
            internet_draft = InternetDraft.objects.get(filename=submission.filename)
        except InternetDraft.DoesNotExist:
            internet_draft = None

        if submission.revision == "00" :
            # if the draft file alreay existed, error will be occured.
            if internet_draft:
                raise self.ApprovalError("00 revision of this document already exists")

            internet_draft = InternetDraft.objects.create(
                title=submission.title,
                group=submission.group,
                filename=submission.filename,
                revision=submission.revision,
                revision_date=submission.submission_date,
                file_type=submission.file_type,
                txt_page_count=submission.txt_page_count,
                abstract=submission.abstract,
                status_id=1,
                intended_status_id=8,
                start_date=now,
                last_modified_date=now,
                review_by_rfc_editor=False,
                expired_tombstone=False,
            )

        else : # Existing version; update the existing record using new values
            if internet_draft is None:
                raise self.ApprovalError("The previous submission of this document cannot be found")
            internet_draft.authors.all().delete()
            EmailAddress.objects.filter(priority=internet_draft.id_document_tag, type='I-D').delete()
            internet_draft.title=submission.title
            internet_draft.revision=submission.revision
            internet_draft.revision_date=submission.submission_date
            internet_draft.file_type=submission.file_type
            internet_draft.txt_page_count=submission.txt_page_count
            internet_draft.abstract=submission.abstract
            internet_draft.last_modified_date=now
            internet_draft.save()

        authors_names = []
        for author_info in submission.authors.all():
            person_or_org = PersonOrOrgInfo.objects.get_or_create_person(
                first_name=author_info.first_name,
                last_name=author_info.last_name,
                created_by="IDST",
                email_address=author_info.email_address,
            )

            internet_draft.authors.create(
                person=person_or_org,
                author_order=author_info.author_order,
            )

            person_or_org.emailaddress_set.create(
                type="I-D",
                priority=internet_draft.id_document_tag,
                address=author_info.email_address,
                comment=internet_draft.filename,
            )

            # gathering author's names
            authors_names.append("%s. %s" % (author_info.first_name[0].upper(), author_info.last_name))
        if len(authors_names) > 2:
            authors = "%s, et al." % authors_names[0]
        else:
            authors = ", ".join(authors_names) 
        submission.status_id = 7
        submission.save()

        #XXX much of from here on should be a helper on InternetDraft?

        # Schedule I-D Announcement:
        cc_val = ""
        try:
            cc_val = IETFWG.objects.get(pk=submission.group_id).email_address
        except IETFWG.DoesNotExist:
            pass
        subject = render_to_string("idsubmit/i-d_action-subject.txt",
            {'submission':submission,
             'authors': authors}).strip()
        body = render_to_string("idsubmit/i-d_action.txt",
            {'submission':submission,
             'authors': authors}).strip()
        ScheduledAnnouncement.objects.create(
            mail_sent =    False,
            scheduled_by =     "IDST",
            to_be_sent_date =  now,
            to_be_sent_time =  "00:00",
            scheduled_date =   now,
            scheduled_time =   str(now.time()),     # sigh
            subject =      subject,
            to_val =       "i-d-announce@ietf.org",
            from_val =     "Internet-Drafts@ietf.org",
            cc_val =       cc_val,
            body =         body,
            content_type =     "Multipart/Mixed; Boundary=\"NextPart\"",
        )

        submission.status_id = 8
        submission.save()
        id_internal = internet_draft.idinternal
        if id_internal and id_internal.cur_state_id < 100:
            # Add comment to ID Tracker
            internet_draft.documentcomment_set.create(
                rfc_flag = 0,
                version = submission.revision,
                comment_text = "New version available",
            )

            msg = ""
            #XXX hardcoded "5"
            if id_internal.cur_sub_state_id == 5:
                msg = "Sub state has been changed to AD Follow up from New Id Needed"
                internet_draft.documentcomment_set.create(
                    rfc_flag = 0,
                    version = submission.revision,
                    comment_text = msg,
                )

                id_internal.prev_sub_state = id_internal.cur_sub_state
                #XXX hardcoded "2"
                id_internal.cur_sub_state_id = 2
                id_internal.save()

            send_to = []
            send_to.append(id_internal.state_change_notice_to)

            email_address = id_internal.job_owner.person.email()[1]
            if email_address not in send_to:
                send_to.append(email_address)
            discuss_positions = id_internal.ballot.positions.filter(discuss = 1)
            for p in discuss_positions:
                if not p.ad.is_current_ad():
                    continue
                email_address = p.ad.person.email()[1]
                if email_address not in send_to:
                    send_to.append(email_address)
            ScheduledAnnouncement.objects.create(
                mail_sent = False,
                scheduled_by = "IDST",
                to_be_sent_date =  now,
                to_be_sent_time =  "00:00",
                scheduled_date =   now,
                scheduled_time =   str(now.time()),     # sigh
                subject = render_to_string("idsubmit/new_version_notify_subject.txt", {'submission': submission}).strip(),
                to_val =  ",".join([str(eb) for eb in send_to if eb is not None]),
                from_val = "Internet-Drafts@ietf.org",
                cc_val =  cc_val,
                body =  render_to_string("idsubmit/new_version_notify.txt",{'submission':submission,'msg':msg}),
            )

            submission.status_id = 9
            submission.save()

        # Notify All Authors:
        # <Please read auto_post.cgi, sub notify_all_authors>

        cc_email = []
        if submission.group_id == Acronym.NONE :
            group_acronym = "Independent Submission"
        else :
            group_acronym = submission.group.name
            #removed cc'ing WG email address by request
            #cc_email.append(IETFWG.objects.get(group_acronym=submission.group).email_address)

        (submitter_name, submitter_email, ) = submission.submitter.email()
        for author_info in submission.authors.all().exclude(email_address=submitter_email) :
            if not author_info.email_address.strip() and submitter_email == author_info.email_address :
                continue

            if author_info.email_address not in cc_email :
                cc_email.append(author_info.email_address)

        to_email = submitter_email
        send_mail(
            None,
            to_email,
            FROM_EMAIL,
            "New Version Notification for %s-%s" % (submission.filename,submission.revision),
            "idsubmit/email_posted_notice.txt", {'subm':submission, 'submitter_name':submitter_name},
            cc_email,
            toUser=True
        )
        submission.status_id = -1
        submission.save()
        # remove files.
        try :
            [os.remove(i) for i in glob.glob("%s-%s.*" % (os.path.join(settings.STAGING_PATH,submission.filename), submission.revision))]
        except :
            pass


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
