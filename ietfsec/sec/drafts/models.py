import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from sec.core.models import *
from sec.utils import FKAsOneToOne
from sec.utils.broken_foreign_key import BrokenForeignKey
from sec.utils.cached_lookup_field import CachedLookupField

class IDDates(models.Model):
    FIRST_CUT_OFF = 1
    SECOND_CUT_OFF = 2
    IETF_MONDAY = 3
    ALL_IDS_PROCESSED_BY = 4
    IETF_MONDAY_AFTER = 5
    APPROVED_V00_SUBMISSIONS = 6

    date = models.DateField(db_column="id_date")
    description = models.CharField(max_length=255, db_column="date_name")
    f_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'id_dates'

class IDAuthor(models.Model):
    document = models.ForeignKey(InternetDraft, db_column='id_document_tag', related_name='authors')
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    author_order = models.IntegerField()
    def __str__(self):
        return "%s authors %s" % ( self.person, self.document.filename )
    def email(self):
        addresses = self.person.emailaddress_set.filter(type='I-D',priority=self.document_id)
        if len(addresses) == 0:
            return None
        else:
            return addresses[0].address
    def final_author_order(self):
        # Unfortunately, multiple authors for the same draft can have
        # the same value for author_order (although they should not).
        # Sort by person_id in that case to get a deterministic ordering.
        return "%08d%08d" % (self.author_order, self.person_id)
    class Meta:
        db_table = 'id_authors'
        verbose_name = "I-D Author"
        ordering = ['document','author_order']

# ----------------------------------
# models created from inspectdb
# ----------------------------------

class IdApprovedDetail(models.Model):
    id = models.IntegerField(primary_key=True)
    filename = models.CharField(max_length=765, blank=True)
    approved_status = models.IntegerField(null=True, blank=True)
    approved_by = models.ForeignKey(PersonOrOrgInfo, db_column='approved_person_tag',related_name='approved_by')
    approved_date = models.DateField(null=True, blank=True)
    recorded_by = models.ForeignKey(PersonOrOrgInfo, db_column='recorded_by',related_name='recorded_by')
    class Meta:
        db_table = u'id_approved_detail'
    def __str__(self):
        return "%s" % ( self.filename )

class IdSubmissionDetail(models.Model):
    submission_id = models.IntegerField(primary_key=True)
    temp_id_document_tag = models.IntegerField(null=True, blank=True)
    status_id = models.IntegerField(null=True, blank=True)
    last_updated_date = models.DateField(null=True, blank=True)
    last_updated_time = models.CharField(max_length=75, blank=True)
    id_document_name = models.CharField(max_length=765, blank=True)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    filename = models.CharField(max_length=765, blank=True)
    creation_date = models.DateField(null=True, blank=True)
    submission_date = models.DateField(null=True, blank=True)
    remote_ip = models.CharField(max_length=300, blank=True)
    revision = models.CharField(max_length=9, blank=True)
    submitter_tag = models.IntegerField(null=True, blank=True)
    auth_key = models.CharField(max_length=765, blank=True)
    idnits_message = models.TextField(blank=True)
    file_type = models.CharField(max_length=150, blank=True)
    comment_to_sec = models.TextField(blank=True)
    abstract = models.TextField(blank=True)
    txt_page_count = models.IntegerField(null=True, blank=True)
    error_message = models.CharField(max_length=765, blank=True)
    warning_message = models.TextField(blank=True)
    wg_submission = models.IntegerField(null=True, blank=True)
    filesize = models.IntegerField(null=True, blank=True)
    man_posted_date = models.DateField(null=True, blank=True)
    man_posted_by = models.CharField(max_length=765, blank=True)
    first_two_pages = models.TextField(blank=True)
    sub_email_priority = models.IntegerField(null=True, blank=True)
    invalid_version = models.IntegerField(null=True, blank=True)
    idnits_failed = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'id_submission_detail'

class IdSubmissionEnv(models.Model):
    id = models.IntegerField(primary_key=True)
    max_live = models.IntegerField(null=True, blank=True)
    staging_path = models.CharField(max_length=765, blank=True)
    max_interval = models.IntegerField(null=True, blank=True)
    current_manual_proc_date = models.IntegerField(null=True, blank=True)
    init_rev_approved_msg = models.TextField(blank=True)
    submitter_auth_msg = models.TextField(blank=True)
    id_action_announcement = models.TextField(blank=True)
    target_path_web = models.CharField(max_length=765, blank=True)
    target_path_ftp = models.CharField(max_length=765, blank=True)
    side_bar_html = models.TextField(blank=True)
    staging_url = models.CharField(max_length=765, blank=True)
    top_bar_html = models.TextField(blank=True)
    bottom_bar_html = models.TextField(blank=True)
    id_approval_request_msg = models.TextField(blank=True)
    emerg_auto_response = models.IntegerField(null=True, blank=True)
    max_same_draft_name = models.IntegerField(null=True, blank=True)
    max_same_draft_size = models.IntegerField(null=True, blank=True)
    max_same_submitter = models.IntegerField(null=True, blank=True)
    max_same_submitter_size = models.IntegerField(null=True, blank=True)
    max_same_wg_draft = models.IntegerField(null=True, blank=True)
    max_same_wg_draft_size = models.IntegerField(null=True, blank=True)
    max_daily_submission = models.IntegerField(null=True, blank=True)
    max_daily_submission_size = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'id_submission_env'

class IdSubmissionStatus(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_value = models.CharField(max_length=765, blank=True)
    class Meta:
        db_table = u'id_submission_status'

# from inspectdb
class IdRestrictedWord(models.Model):
    id = models.AutoField(primary_key=True)
    restricted_word = models.CharField(max_length=75)
    class Meta:
        db_table = u'id_restricted_word'
        
# from inspectdb
class Messages(models.Model):
    id = models.AutoField(primary_key=True)
    message_name = models.CharField(max_length=75)
    message_content = models.TextField()
    recipient = models.CharField(max_length=300)
    class Meta:
        db_table = u'messages'

class RfcAuthor(models.Model):
    rfc = models.ForeignKey(Rfc, db_column='rfc_number', related_name='authors')
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    def __str__(self):
        return "%s, %s" % ( self.person.last_name, self.person.first_name)
    class Meta:
        db_table = 'rfc_authors'
        verbose_name = 'RFC Author'
        
class RfcObsolete(models.Model):
    ACTION_CHOICES=(('Obsoletes', 'Obsoletes'), ('Updates', 'Updates'))
    rfc = models.ForeignKey(Rfc, db_column='rfc_number', related_name='updates_or_obsoletes')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    rfc_acted_on = models.ForeignKey(Rfc, db_column='rfc_acted_on', related_name='updated_or_obsoleted_by')
    def __str__(self):
        return "RFC%04d %s RFC%04d" % (self.rfc_id, self.action, self.rfc_acted_on_id)
    class Meta:
        db_table = 'rfcs_obsolete'
        verbose_name = 'RFC updates or obsoletes'
        verbose_name_plural = verbose_name

class ScheduledAnnouncement(models.Model):
    mail_sent = models.BooleanField()
    to_be_sent_date = models.DateField(null=True, blank=True)
    to_be_sent_time = models.CharField(blank=True, null=True, max_length=50)
    scheduled_by = models.CharField(blank=True, max_length=100)
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.CharField(blank=True, max_length=50)
    subject = models.CharField(blank=True, max_length=255)
    to_val = models.CharField(blank=True, max_length=255)
    from_val = models.CharField(blank=True, max_length=255)
    cc_val = models.TextField(blank=True,null=True)
    body = models.TextField(blank=True)
    actual_sent_date = models.DateField(null=True, blank=True)
    actual_sent_time = models.CharField(blank=True, max_length=50)
    first_q = models.IntegerField(null=True, blank=True)
    second_q = models.IntegerField(null=True, blank=True)
    note = models.TextField(blank=True,null=True)
    content_type = models.CharField(blank=True, max_length=255)
    replyto = models.CharField(blank=True, null=True, max_length=255)
    bcc_val = models.CharField(blank=True, null=True, max_length=255)
    def __str__(self):
        return "Scheduled Announcement from %s to %s on %s %s" % (self.from_val, self.to_val, self.to_be_sent_date, self.to_be_sent_time)
    class Meta:
        db_table = 'scheduled_announcements'

class DocumentComment(models.Model):
    BALLOT_DISCUSS = 1
    BALLOT_COMMENT = 2
    BALLOT_CHOICES = (
        (BALLOT_DISCUSS, 'discuss'),
        (BALLOT_COMMENT, 'comment'),
    )
    document = models.ForeignKey(IDInternal)
    # NOTE: This flag is often NULL, which complicates its correct use...
    rfc_flag = models.IntegerField(null=True, blank=True)
    public_flag = models.BooleanField()
    date = models.DateField(db_column='comment_date', default=datetime.date.today)
    time = models.CharField(db_column='comment_time', max_length=20, default=lambda: datetime.datetime.now().strftime("%H:%M:%S"))
    version = models.CharField(blank=True, max_length=3)
    comment_text = models.TextField(blank=True)
    # NOTE: This is not a true foreign key -- it sometimes has values
    # (like 999) that do not exist in IESGLogin. So using select_related()
    # will break!
    created_by = BrokenForeignKey(IESGLogin, db_column='created_by', null=True, null_values=(0, 999))
    result_state = BrokenForeignKey(IDState, db_column='result_state', null=True, related_name="comments_leading_to_state", null_values=(0, 99))
    origin_state = models.ForeignKey(IDState, db_column='origin_state', null=True, related_name="comments_coming_from_state")
    ballot = models.IntegerField(null=True, choices=BALLOT_CHOICES)
    def __str__(self):
        return "\"%s...\" by %s" % (self.comment_text[:20], self.get_author())
    def get_absolute_url(self):
        # use self.document.rfc_flag, since
        # self.rfc_flag is not always set properly.
        if self.document.rfc_flag:
            return "/idtracker/rfc%d/comment/%d/" % (self.document_id, self.id)
        else:
            return "/idtracker/%s/comment/%d/" % (self.document.draft.filename, self.id)
    def get_author(self):
        if self.created_by:
            return str(self.created_by)
        else:
            return "(System)"
    def get_username(self):
        if self.created_by:
            return self.created_by.login_name
        else:
            return "(System)"
    def get_fullname(self):
        if self.created_by:
            return self.created_by.first_name + " " + self.created_by.last_name
        else:
            return "(System)"
    def datetime(self):
        # this is just a straightforward combination, except that the time is
        # stored incorrectly in the database.
        return datetime.datetime.combine( self.date, datetime.time( * [int(s) for s in self.time.split(":")] ) )
    class Meta:
        db_table = 'document_comments'

class Position(models.Model):
    ballot = models.ForeignKey(BallotInfo, related_name='positions')
    ad = models.ForeignKey(IESGLogin)
    yes = models.IntegerField(db_column='yes_col')
    noobj = models.IntegerField(db_column='no_col')
    abstain = models.IntegerField()
    approve = models.IntegerField(default=0) # doesn't appear to be used anymore?
    discuss = models.IntegerField()
    recuse = models.IntegerField()
    def __str__(self):
        return "Position for %s on %s" % ( self.ad, self.ballot )
    def abstain_ind(self):
        if self.recuse:
            return 'R'
        if self.abstain:
            return 'X'
        else:
            return ' '
    class Meta:
        db_table = 'ballots'
        unique_together = (('ballot', 'ad'), )
        verbose_name = "IESG Ballot Position"

# ----------------------------------------
# Signal Handlers
# ----------------------------------------
def test_mailer(sender, **kwargs):
    if hasattr(settings, 'TEST_EMAIL'):
        instance = kwargs['instance']
        subject = 'An announcement was scheduled'
        message = """The following announcement was scheduled:
        
To: %s
CC: %s 
Subject: %s
Body: %s """ % (instance.to_val, instance.cc_val, instance.subject, instance.body)
        from_email = 'django@amsl.com'
        recipient_list = settings.TEST_EMAIL
        send_mail(subject,message,from_email,recipient_list)

models.signals.post_save.connect(test_mailer, sender=ScheduledAnnouncement)
