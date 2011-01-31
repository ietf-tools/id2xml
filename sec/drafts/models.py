import datetime

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from sec.core.models import Acronym, Area, AreaDirector, AreaStatus, IESGLogin, PersonOrOrgInfo
from sec.groups.models import IETFWG, WGType, AreaGroup
from sec.utils import FKAsOneToOne
from sec.utils.broken_foreign_key import BrokenForeignKey
from sec.utils.cached_lookup_field import CachedLookupField

TIME_ZONE_CHOICES = (
    (0, 'UTC'),
    (-1, 'UTC -1'),
    (-2, 'UTC -2'),
    (-3, 'UTC -3'),
    (-4, 'UTC -4 (Eastern Summer)'),
    (-5, 'UTC -5 (Eastern Winter)'),
    (-6, 'UTC -6'),
    (-7, 'UTC -7'),
    (-8, 'UTC -8 (Pacific Winter)'),
    (-9, 'UTC -9'),
    (-10, 'UTC -10 (Hawaii Winter)'),
    (-11, 'UTC -11'),
    (+12, 'UTC +12'),
    (+11, 'UTC +11'),
    (+10, 'UTC +10 (Brisbane)'),
    (+9, 'UTC +9'),
    (+8, 'UTC +8 (Perth Winter)'),
    (+7, 'UTC +7'),
    (+6, 'UTC +6'),
    (+5, 'UTC +5'),
    (+4, 'UTC +4'),
    (+3, 'UTC +3 (Moscow Winter)'),
    (+2, 'UTC +2 (Western Europe Summer'),
    (+1, 'UTC +1 (Western Europe Winter)'),
)

class BallotInfo(models.Model):   # Added by Michael Lee
    ballot = models.AutoField(primary_key=True, db_column='ballot_id')
    active = models.BooleanField()
    an_sent = models.BooleanField()
    an_sent_date = models.DateField(null=True, blank=True)
    an_sent_by = models.ForeignKey(IESGLogin, db_column='an_sent_by', related_name='ansent', null=True)
    defer = models.BooleanField(blank=True)
    defer_by = models.ForeignKey(IESGLogin, db_column='defer_by', related_name='deferred', null=True)
    defer_date = models.DateField(null=True, blank=True)
    approval_text = models.TextField(blank=True)
    last_call_text = models.TextField(blank=True)
    ballot_writeup = models.TextField(blank=True)
    ballot_issued = models.IntegerField(null=True, blank=True)
    def __str__(self):
        try:
            return "Ballot for %s" % self.drafts.get(primary_flag=1)
        except IDInternal.DoesNotExist:
            return "Ballot ID %d (no I-D?)" % (self.ballot)
    def remarks(self):
        remarks = list(self.discusses.all()) + list(self.comments.all())
        return remarks
    def active_positions(self):
        '''Returns a list of dicts, with AD and Position tuples'''
        active_iesg = IESGLogin.active_iesg()
        ads = [ad.id for ad in active_iesg]
        positions = {}
        for position in self.positions.filter(ad__in=ads):
            positions[position.ad_id] = position
        ret = []
        for ad in active_iesg:
            ret.append({'ad': ad, 'pos': positions.get(ad.id, None)})
        return ret
    def needed(self, standardsTrack=True):
        '''Returns text answering the question "what does this document
        need to pass?".  The return value is only useful if the document
        is currently in IESG evaluation.'''
        active_iesg = IESGLogin.active_iesg()
        ads = [ad.id for ad in active_iesg]
        yes = 0
        noobj = 0
        discuss = 0
        recuse = 0
        for position in self.positions.filter(ad__in=ads):
            yes += 1 if position.yes > 0 else 0
            noobj += 1 if position.noobj > 0 else 0
            discuss += 1 if position.discuss > 0 else 0
            recuse += 1 if position.recuse > 0 else 0
        answer = ''
        if yes < 1:
            answer += "Needs a YES. "
        if discuss > 0:
            if discuss == 1:
                answer += "Has a DISCUSS. "
            else:
                answer += "Has %d DISCUSSes. " % discuss
        if standardsTrack:
            # For standards-track, need positions from 2/3 of the
            # non-recused current IESG.
            needed = ( active_iesg.count() - recuse ) * 2 / 3
        else:
            # Info and experimental only need one position.
            needed = 1
        have = yes + noobj + discuss
        if have < needed:
            more = needed - have
            if more == 1:
                answer += "Needs %d more position. " % more
            else:
                answer += "Needs %d more positions. " % more
        else:
            answer += "Has enough positions to pass"
            if discuss:
                answer += " once DISCUSSes are resolved"
            answer += ". "

        return answer.rstrip()

    class Meta:
        db_table = 'ballot_info'
        
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

class IDIntendedStatus(models.Model):
    intended_status_id = models.AutoField(primary_key=True)
    intended_status = models.CharField(max_length=25, db_column='status_value')
    def __str__(self):
        return self.intended_status
    class Meta:
        db_table = "id_intended_status"
        verbose_name="I-D Intended Publication Status"
        verbose_name_plural="I-D Intended Publication Statuses"

class IDStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=25, db_column='status_value')
    def __str__(self):
        return self.status
    class Meta:
        db_table = "id_status"
        verbose_name="I-D Status"
        verbose_name_plural="I-D Statuses"

class IDState(models.Model):
    PUBLICATION_REQUESTED = 10
    LAST_CALL_REQUESTED = 15
    IN_LAST_CALL = 16
    IESG_EVALUATION = 20
    IESG_EVALUATION_DEFER = 21
    APPROVED_ANNOUNCEMENT_SENT = 30
    DEAD = 99
    DO_NOT_PUBLISH_STATES = (33, 34)
   
    document_state_id = models.AutoField(primary_key=True)
    state = models.CharField(max_length=50, db_column='document_state_val')
    equiv_group_flag = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True, db_column='document_desc')
    def __str__(self):
        return self.state
    def choices():
        return [(state.document_state_id, state.state) for state in IDState.objects.all()]
    choices = staticmethod(choices)
    class Meta:
        db_table = 'ref_doc_states_new'
        ordering = ['document_state_id']

class IDSubState(models.Model):
    sub_state_id = models.AutoField(primary_key=True)
    sub_state = models.CharField(max_length=55, db_column='sub_state_val')
    description = models.TextField(blank=True, db_column='sub_state_desc')
    def __str__(self):
        return self.sub_state
    class Meta:
        db_table = 'sub_state'
        ordering = ['sub_state_id']

class IDInternal(models.Model):
    """
    An IDInternal represents a document that has been added to the
    I-D tracker.  It can be either an Internet Draft or an RFC.
    The table has only a single primary key field, meaning that
    there is the danger of RFC number collision with low-numbered
    Internet Drafts.

    Since it's most common to be an Internet Draft, the draft
    field is defined as a FK to InternetDrafts.  One side effect
    of this is that select_related() will only work with
    rfc_flag=0.

    When searching where matches may be either I-Ds or RFCs,
    you cannot use draft__ as that will cause an INNER JOIN
    which will limit the responses to I-Ds.
    """

    ACTIVE=1
    PUBLISHED=3
    EXPIRED=2
    WITHDRAWN_SUBMITTER=4
    REPLACED=5
    WITHDRAWN_IETF=6
    INACTIVE_STATES=[99,32,42]

    draft = models.ForeignKey('InternetDraft', primary_key=True, unique=True, db_column='id_document_tag')
    rfc_flag = models.IntegerField(null=True)
    ballot = models.ForeignKey(BallotInfo, related_name='drafts', db_column="ballot_id")
    primary_flag = models.IntegerField(blank=True, null=True)
    group_flag = models.IntegerField(blank=True, default=0)
    token_name = models.CharField(blank=True, max_length=25)
    token_email = models.CharField(blank=True, max_length=255)
    note = models.TextField(blank=True)
    status_date = models.DateField(blank=True,null=True)
    email_display = models.CharField(blank=True, max_length=50)
    agenda = models.IntegerField(null=True, blank=True)
    cur_state = models.ForeignKey(IDState, db_column='cur_state', related_name='docs')
    prev_state = models.ForeignKey(IDState, db_column='prev_state', related_name='docs_prev')
    assigned_to = models.CharField(blank=True, max_length=25)
    mark_by = models.ForeignKey(IESGLogin, db_column='mark_by', related_name='marked')
    job_owner = models.ForeignKey(IESGLogin, db_column='job_owner', related_name='documents')
    event_date = models.DateField(null=True)
    area_acronym = models.ForeignKey(Area)
    cur_sub_state = BrokenForeignKey(IDSubState, related_name='docs', null=True, blank=True, null_values=(0, -1))
    prev_sub_state = BrokenForeignKey(IDSubState, related_name='docs_prev', null=True, blank=True, null_values=(0, -1))
    returning_item = models.IntegerField(null=True, blank=True)
    telechat_date = models.DateField(null=True, blank=True)
    via_rfc_editor = models.IntegerField(null=True, blank=True)
    state_change_notice_to = models.CharField(blank=True, max_length=255)
    dnp = models.IntegerField(null=True, blank=True)
    dnp_date = models.DateField(null=True, blank=True)
    noproblem = models.IntegerField(null=True, blank=True)
    resurrect_requested_by = BrokenForeignKey(IESGLogin, db_column='resurrect_requested_by', related_name='docsresurrected', null=True, blank=True)
    approved_in_minute = models.IntegerField(null=True, blank=True)
    def __str__(self):
        if self.rfc_flag:
            return "RFC%04d" % ( self.draft_id )
        else:
            return self.draft.filename
    def get_absolute_url(self):
        if self.rfc_flag:
            return "/doc/rfc%d/" % ( self.draft_id )
        else:
            return "/doc/%s/" % ( self.draft.filename )
    _cached_rfc = None
    def document(self):
        if self.rfc_flag:
            if self._cached_rfc is None:
                self._cached_rfc = Rfc.objects.get(rfc_number=self.draft_id)
            return self._cached_rfc
        else:
            return self.draft
    def public_comments(self):
        return self.comments().filter(public_flag=True)
    def comments(self):
        # would filter by rfc_flag but the database is broken. (see
        # trac ticket #96) so this risks collisions.
        # return self.documentcomment_set.all().order_by('-date','-time','-id')
        #
        # the obvious code above doesn't work with django.VERSION 1.0/1.1
        # because "draft" isn't a true foreign key (when rfc_flag=1 the
        # related InternetDraft object doesn't necessarily exist).
        return DocumentComment.objects.filter(document=self.draft_id).order_by('-date','-time','-id')
    def ballot_set(self):
        return IDInternal.objects.filter(ballot=self.ballot_id).order_by('-primary_flag')
    def ballot_primary(self):
        return IDInternal.objects.filter(ballot=self.ballot_id,primary_flag=1)
    def ballot_others(self):
        return IDInternal.objects.filter(models.Q(primary_flag=0)|models.Q(primary_flag__isnull=True), ballot=self.ballot_id)
    def docstate(self):
        return format_document_state(self.cur_state, self.cur_sub_state)
    def change_state(self, state, sub_state):
        self.prev_state = self.cur_state
        self.cur_state = state
        self.prev_sub_state_id = self.cur_sub_state_id
        self.cur_sub_state = sub_state

    class Meta:
        db_table = 'id_internal'
        verbose_name = 'IDTracker Draft'

class InternetDraft(models.Model):
    DAYS_TO_EXPIRE=185
    id_document_tag = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, db_column='id_document_name')
    id_document_key = models.CharField(max_length=255, editable=False)
    group = models.ForeignKey(Acronym, db_column='group_acronym_id')
    filename = models.CharField(max_length=255, unique=True)
    revision = models.CharField(max_length=2)
    revision_date = models.DateField()
    file_type = models.CharField(max_length=20)
    txt_page_count = models.IntegerField()
    local_path = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField()
    expiration_date = models.DateField(null=True)
    abstract = models.TextField()
    dunn_sent_date = models.DateField(null=True, blank=True)
    extension_date = models.DateField(null=True, blank=True)
    status = models.ForeignKey(IDStatus)
    intended_status = models.ForeignKey(IDIntendedStatus)
    lc_sent_date = models.DateField(null=True, blank=True)
    lc_changes = models.CharField(max_length=3,null=True)
    lc_expiration_date = models.DateField(null=True, blank=True)
    b_sent_date = models.DateField(null=True, blank=True)
    b_discussion_date = models.DateField(null=True, blank=True)
    b_approve_date = models.DateField(null=True, blank=True)
    wgreturn_date = models.DateField(null=True, blank=True)
    rfc_number = models.IntegerField(null=True, blank=True, db_index=True)
    comments = models.TextField(blank=True,null=True)
    last_modified_date = models.DateField(auto_now=True)
    replaced_by = BrokenForeignKey('self', db_column='replaced_by', blank=True, null=True, related_name='replaces_set')
    replaces = FKAsOneToOne('replaces', reverse=True)
    review_by_rfc_editor = models.BooleanField()
    expired_tombstone = models.BooleanField()
    idinternal = FKAsOneToOne('idinternal', reverse=True, query=models.Q(rfc_flag = 0))
    def __str__(self):
        return self.filename
    def save(self):
        self.id_document_key = self.title.upper()
        super(InternetDraft, self).save()
    def displayname(self):
        return self.filename
    # AMS method
    def file(self):
        return "%s-%s.txt" % (self.filename, self.revision_display())
    def file_tag(self):
        return "<%s-%s.txt>" % (self.filename, self.revision_display())
    def group_acronym(self):
        return self.group.acronym
    def idstate(self):
        idinternal = self.idinternal
        if idinternal:
            return idinternal.docstate()
        else:
            return "I-D Exists"
    def revision_display(self):
        r = int(self.revision)
        if self.status.status != 'Active' and not self.expired_tombstone:
           r = max(r - 1, 0)
        return "%02d" % r
    def expiration(self):
        return self.revision_date + datetime.timedelta(self.DAYS_TO_EXPIRE)
    def can_expire(self):
        # Copying the logic from expire-ids-1 without thinking
        # much about it.
        if self.review_by_rfc_editor:
            return False
        idinternal = self.idinternal
        if idinternal:
            cur_state_id = idinternal.cur_state_id
            # 42 is "AD is Watching"; this matches what's in the
            # expire-ids-1 perl script.
            # A better way might be to add a column to the table
            # saying whether or not a document is prevented from
            # expiring.
            if cur_state_id < 42:
                return False
        return True
    # new method for AMS
    def get_area(self):
        '''Returns the Area object this draft is associated with.  Legacy app tested
        specifically for 1027, Individual Submission, but this relationship is properly
        represented in the area_group table so defer to it.'''
        
        try:
            area = AreaGroup.objects.get(group=self.group).area
        except AreaGroup.DoesNotExist:
            return None
        return area

    def clean_abstract(self):
        # Cleaning based on what "id-abstracts-text" script does
        a = self.abstract
        a = re.sub(" *\r\n *", "\n", a)  # get rid of DOS line endings
        a = re.sub(" *\r *", "\n", a)  # get rid of MAC line endings
        a = re.sub("(\n *){3,}", "\n\n", a)  # get rid of excessive vertical whitespace
        a = re.sub("\f[\n ]*[^\n]*\n", "", a)  # get rid of page headers
        # Get rid of 'key words' boilerplate and anything which follows it:
        # (No way that is part of the abstract...)
        a = re.sub("(?s)(Conventions [Uu]sed in this [Dd]ocument|Requirements [Ll]anguage)?[\n ]*The key words \"MUST\", \"MUST NOT\",.*$", "", a)
        # Get rid of status/copyright boilerplate
        a = re.sub("(?s)\nStatus of [tT]his Memo\n.*$", "", a)
        # wrap long lines without messing up formatting of Ok paragraphs:
        while re.match("([^\n]{72,}?) +", a):
            a = re.sub("([^\n]{72,}?) +([^\n ]*)(\n|$)", "\\1\n\\2 ", a)
        # Remove leading and trailing whitespace
        a = a.strip()
        return a

    class Meta:
        db_table = "internet_drafts"

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
    approved_person_tag = models.IntegerField(null=True, blank=True)
    approved_date = models.DateField(null=True, blank=True)
    recorded_by = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'id_approved_detail'

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

class Meeting(models.Model):
    meeting_num = models.IntegerField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()
    city = models.CharField(blank=True, max_length=255)
    state = models.CharField(blank=True, max_length=255)
    country = models.CharField(blank=True, max_length=255)
    time_zone = models.IntegerField(null=True, blank=True, choices=TIME_ZONE_CHOICES)
    ack = models.TextField(blank=True)
    agenda_html = models.TextField(blank=True)
    agenda_text = models.TextField(blank=True)
    future_meeting = models.TextField(blank=True)
    overview1 = models.TextField(blank=True)
    overview2 = models.TextField(blank=True)
#    def __str__(self):
#        return "%s" % (self.meeting_num)
    def __unicode__(self):
        return "%s" % (self.meeting_num)

    def get_meeting_date (self,offset):
        return self.start_date + datetime.timedelta(days=offset)
#    def num(self):
#        return self.meeting_num
    class Meta:
        db_table = 'meetings'
        
# from inspectdb
class Messages(models.Model):
    id = models.AutoField(primary_key=True)
    message_name = models.CharField(max_length=75)
    message_content = models.TextField()
    recipient = models.CharField(max_length=300)
    class Meta:
        db_table = u'messages'

class RfcIntendedStatus(models.Model):
    NONE=5
    intended_status_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=25, db_column='status_value')
    def __str__(self):
        return self.status
    class Meta:
        db_table = 'rfc_intend_status'
        verbose_name = 'RFC Intended Status Field'

class RfcStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=25, db_column='status_value')
    def __str__(self):
        return self.status
    class Meta:
        db_table = 'rfc_status'
        verbose_name = 'RFC Status'
        verbose_name_plural = 'RFC Statuses'

class Rfc(models.Model):
    ONLINE_CHOICES=(('YES', 'Yes'), ('NO', 'No'))
    rfc_number = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=200, db_column='rfc_name')
    rfc_name_key = models.CharField(max_length=200, editable=False)
    # AMS Changes
    # group_acronym = models.CharField(blank=True, max_length=8)
    # area_acronym = models.CharField(blank=True, max_length=8)
    group_acronym = models.ForeignKey(Acronym,db_column="group_acronym",to_field='acronym',related_name='rfcs_by_group')
    area_acronym = models.ForeignKey(Acronym,db_column="area_acronym",to_field='acronym',related_name='rfcs_by_area')
    status = models.ForeignKey(RfcStatus, db_column="status_id")
    intended_status = models.ForeignKey(RfcIntendedStatus, db_column="intended_status_id", default=RfcIntendedStatus.NONE)
    fyi_number = models.CharField(blank=True, max_length=20)
    std_number = models.CharField(blank=True, max_length=20)
    # AMS Changes
    #txt_page_count = models.IntegerField(null=True, blank=True)
    txt_page_count = models.IntegerField()
    online_version = models.CharField(choices=ONLINE_CHOICES, max_length=3, default='YES')
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

    idinternal = CachedLookupField(lookup=lambda self: IDInternal.objects.get(draft=self.rfc_number, rfc_flag=1))
    group = CachedLookupField(lookup=lambda self: Acronym.objects.get(acronym=self.group_acronym))

    def __str__(self):
        return "RFC%04d" % ( self.rfc_number )
    def save(self):
        self.rfc_name_key = self.title.upper()
        self.last_modified_date = datetime.date.today()
        super(Rfc, self).save()
    def displayname(self):
        return "%s.txt" % ( self.filename() )
    def filename(self):
        return "rfc%d" % ( self.rfc_number )
    def revision(self):
        return "RFC"
    def revision_display(self):
        return "RFC"
    def file_tag(self):
        return "RFC %s" % self.rfc_number

    # return set of RfcObsolete objects obsoleted or updated by this RFC
    def obsoletes(self):
        return RfcObsolete.objects.filter(rfc=self.rfc_number)

    # return set of RfcObsolete objects obsoleting or updating this RFC
    def obsoleted_by(self):
        return RfcObsolete.objects.filter(rfc_acted_on=self.rfc_number)

    class Meta:
        db_table = 'rfcs'
        verbose_name = 'RFC'
        verbose_name_plural = 'RFCs'

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
    document = models.ForeignKey('IDInternal')
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
    if settings.TEST_EMAIL:
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
