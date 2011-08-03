from django.conf import settings 
from django.db import models
from django.db import connection
from django.shortcuts import get_object_or_404

from sec.utils import FKAsOneToOne
from sec.utils.broken_foreign_key import BrokenForeignKey
from sec.utils.cached_lookup_field import CachedLookupField

#from sec.groups.models import WGSecretary

import datetime
import os

STATUS_TYPES = (
    ('1', 'Active'),
    ('2', 'Concluded'),
    ('3', 'Unknown'),
)

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
    (+2, 'UTC +2 (Western Europe Summer)'),
    (+1, 'UTC +1 (Western Europe Winter)'),
)

# --------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def get_group_or_404(id):
    '''
    This function takes an id (integer or string) and returns the appropriate IETFWG, IRTF or 
    Acronym object representing a group, raising 404 if it is not found
    '''
    id = int(id)
    if id > 100:
        group = get_object_or_404(IETFWG, group_acronym=id)
    elif 0 < id < 100:
        group = get_object_or_404(IRTF, irtf_id=id)
    elif id < 0:
        group = get_object_or_404(Acronym, acronym_id=id)
    return group
    
# --------------------------------------------------------
# Managers
# --------------------------------------------------------

class CustomManager(models.Manager):
    """Custom manager for complex SQL queries. ie. Django does not support GROUP BY"""

    def multi_search(self, first_name='', last_name='', email='', tag=None):
        """Custom query for initial rolodex search.  Takes one or more of first_name, last_name, email, tag.
           Fields are combined with AND to limit search.  If tag is provided it is the only field used
           for lookup since it uniquely identifies person record.

           Returns a list of dictionary w/ tag, first_name, last_name, email, company"""

        col_names = ['tag', 'first_name', 'last_name', 'email']
        result = []
        cursor = connection.cursor()
        # if tag is provided do a simpler lookup
        if tag != None:
            query = 'SELECT a.person_or_org_tag, a.first_name, a.last_name, b.email_address FROM person_or_org_info a LEFT JOIN email_addresses b ON a.person_or_org_tag=b.person_or_org_tag WHERE a.person_or_org_tag = %s GROUP BY a.person_or_org_tag'
            cursor.execute(query,[tag])
        # if email pattern given don't allow empty NULL emails in results
        elif email != '':
            query = 'SELECT a.person_or_org_tag, a.first_name, a.last_name, b.email_address FROM person_or_org_info a LEFT JOIN email_addresses b ON a.person_or_org_tag=b.person_or_org_tag WHERE a.first_name LIKE %s AND a.last_name LIKE %s AND b.email_address LIKE %s GROUP BY email_address,first_name,last_name ORDER BY a.last_name,a.first_name'
            cursor.execute(query,["%s%%" % first_name, "%s%%" % last_name, "%%%s%%" % email])
        # query for name searches
        else:
            query = 'SELECT a.person_or_org_tag, a.first_name, a.last_name, b.email_address FROM person_or_org_info a LEFT JOIN email_addresses b ON a.person_or_org_tag=b.person_or_org_tag WHERE a.first_name LIKE %s AND a.last_name LIKE %s GROUP BY a.person_or_org_tag ORDER BY a.last_name,a.first_name'
            cursor.execute(query,["%s%%" % first_name, "%s%%" % last_name,])
        for row in cursor.fetchall():
            result.append(dict(zip(col_names,row)))
        # add a company name to the dictionary (use first address found w/ affiliated_company)
        new_result = []
        for item in result:
            addresses = PostalAddress.objects.filter(person_or_org=item['tag'])
            item['affiliated_company'] = ''
            for address in addresses:
                if address.affiliated_company:
                    item['affiliated_company'] = address.affiliated_company
                    break
            new_result.append(item)
        return new_result

    def get_email(self, tag):
        """"Custom query for retrieving email records for one person, grouped by email_address"""

        cursor = connection.cursor()
        query = 'SELECT * from email_addresses WHERE person_or_org_tag = %s GROUP BY email_address'
        cursor.execute(query,[tag])
        return cursor.fetchall()

# --------------------------------------------------------
# Dependents
# --------------------------------------------------------
class IDSubState(models.Model):
    sub_state_id = models.AutoField(primary_key=True)
    sub_state = models.CharField(max_length=55, db_column='sub_state_val')
    description = models.TextField(blank=True, db_column='sub_state_desc')
    def __str__(self):
        return self.sub_state
    class Meta:
        db_table = 'sub_state'
        ordering = ['sub_state_id']
        
# could use a mapping for user_level
class IESGLogin(models.Model):
    USER_LEVEL_CHOICES = (
	(0, 'Secretariat'),
	(1, 'IESG'),
	(2, 'ex-IESG'),
	(3, 'Level 3'),
	(4, 'Comment Only(?)'),
    )
    id = models.AutoField(primary_key=True)
    login_name = models.CharField(blank=True, max_length=255)
    password = models.CharField(max_length=25)
    user_level = models.IntegerField(choices=USER_LEVEL_CHOICES)
    first_name = models.CharField(blank=True, max_length=25)
    last_name = models.CharField(blank=True, max_length=25)
    person = models.ForeignKey('PersonOrOrgInfo', db_column='person_or_org_tag', unique=True)
    pgp_id = models.CharField(blank=True, null=True, max_length=20)
    default_search = models.NullBooleanField()
    def __unicode__(self):
        #return "%s, %s" % ( self.last_name, self.first_name)
        return "%s %s" % ( self.first_name, self.last_name)
    def is_current_ad(self):
	return self.user_level == 1
    def active_iesg():
	return IESGLogin.objects.filter(user_level=1,id__gt=1).order_by('last_name')	#XXX hardcoded
    active_iesg = staticmethod(active_iesg)
    class Meta:
        db_table = 'iesg_login'


# Below two separate "through" models have been defined for one underlying
# db table.  This is to handle odd db schema where not_meeting_groups is 
# essentially a join table with a meeting on one side and a group or IRTF
# object on the other.  The alternative implementation is to get rid of
# both tables and ManyToMany fields and define custom methods on IETFWG and IRTGF
# which search the not_meeting table
class NotMeetingGroups(models.Model):
    '''
    NOTE: this model is defined as a "through" model only
    (see groups_not_meeting ManyToManyField in Meeting model)
    It is a join table with no primary key so the standard
    manager cannot be used on it.
    '''
    group = models.ForeignKey('IETFWG', db_column='group_acronym_id')
    meeting = models.ForeignKey('Meeting', db_column='meeting_num')

    class Meta:
        db_table = 'not_meeting_groups'

class NotMeetingIRTF(models.Model):
    '''
    NOTE: this model is defined as a "through" model only
    (see irtf_not_meeting ManyToManyField in Meeting model)
    It is a join table with no primary key so the standard
    manager cannot be used on it.
    '''
    irtf = models.ForeignKey('IRTF', db_column='group_acronym_id')
    meeting = models.ForeignKey('Meeting', db_column='meeting_num')

    class Meta:
        db_table = 'not_meeting_groups'
        
class RfcIntendedStatus(models.Model):
    NONE=5
    intended_status_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=25, db_column='status_value')
    def __str__(self):
        return self.status
    class Meta:
        db_table = 'rfc_intend_status'
        verbose_name = 'RFC Intended Status Field'
# --------------------------------------------------------
# Models
# --------------------------------------------------------

class Acronym(models.Model):
    acronym_id = models.AutoField(primary_key=True, db_column='acronym_id')
    acronym = models.CharField(max_length=12, unique=True)
    name = models.CharField(max_length=100, unique=True)
    name_key = models.CharField(max_length=100, editable=False)
    def save(self):
        self.name_key = self.name.upper()
        super(Acronym, self).save()
    def __unicode__(self):
        return self.acronym
    def get_area_status(self):
        return self.area.get_status()
    class Meta:
        db_table = 'acronym'
        # we're setting verbose_name=Area here to accomodate the edit page of the areas tool.  It uses
        # acronym as the main object (with area being an inline).  May need to change later.
        verbose_name = 'Area'

class Area(models.Model):
    ACTIVE=1
    #area_acronym = models.ForeignKey(Acronym, primary_key=True, unique=True)
    area_acronym = models.OneToOneField(Acronym, parent_link=True, primary_key=True)
    #start_date = models.DateField(auto_now_add=True)
    start_date = models.DateField()
    concluded_date = models.DateField(null=True, blank=True)
    status = models.ForeignKey('AreaStatus')
    comments = models.TextField(blank=True)
    last_modified_date = models.DateField(auto_now=True)
    # it is considered non-standard to set null=True for text fields
    # but we are doing this to match legacy tool functionality
    extra_email_addresses = models.TextField(null=True,blank=True)
    #area_coordinator_tag = models.ForeignKey(PersonOrOrgInfo)
    area_coordinator_tag = models.IntegerField(blank=True,default=0)
    def __unicode__(self):
        return self.area_acronym.acronym
    def active_area_choices():
        return [(area.area_acronym_id, area.area_acronym.acronym) for area in Area.objects.filter(status=1).select_related().order_by('acronym.acronym')]
    active_area_choices = staticmethod(active_area_choices)
    def get_status(self):
        return self.status.status_value
    class Meta:
        db_table = 'areas'
        verbose_name="area"

class AreaDirector(models.Model):
    area = models.ForeignKey(Area, db_column='area_acronym_id', null=True)
    person = models.ForeignKey('PersonOrOrgInfo', db_column='person_or_org_tag')
    def __unicode__(self):
        return "%s (%s)" % ( self.person, self.role() )
    def role(self):
        try:
            return "%s AD" % self.area
        except Area.DoesNotExist:
            return "?%d? AD" % self.area_id
    class Meta:
        db_table = 'area_directors'

class AreaGroup(models.Model):
    area = models.ForeignKey(Area, db_column='area_acronym_id', related_name='areagroup')
    group = models.ForeignKey('IETFWG', db_column='group_acronym_id', unique=True)
    def __str__(self):
        return "%s is in %s" % ( self.group, self.area )
    class Meta:
        db_table = 'area_group'
        verbose_name = 'Area this group is in'
        verbose_name_plural = 'Area to Group mappings'
        
class AreaStatus(models.Model):
    status_id = models.AutoField(primary_key=True, db_column='status_id')
    status_value = models.CharField(max_length=25, db_column='status_value')
    def __unicode__(self):
        return str(self.status_id)
    class Meta:
        db_table = 'area_status'

class BallotInfo(models.Model):   # Added by Michael Lee
    ballot = models.AutoField(primary_key=True, db_column='ballot_id')
    active = models.BooleanField()
    an_sent = models.BooleanField()
    an_sent_date = models.DateField(null=True, blank=True)
    an_sent_by = models.ForeignKey('IESGLogin', db_column='an_sent_by', related_name='ansent', null=True)
    defer = models.BooleanField(blank=True)
    defer_by = models.ForeignKey('IESGLogin', db_column='defer_by', related_name='deferred', null=True)
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
        
class EmailAddress(models.Model):
    person_or_org = models.ForeignKey('PersonOrOrgInfo', db_column='person_or_org_tag')
    type = models.CharField(max_length=4, db_column='email_type', default='INET')
    priority = models.IntegerField(db_column='email_priority',default=1)
    address = models.CharField(blank=True, max_length=255, db_column='email_address')
    comment = models.CharField(blank=True, max_length=255, db_column='email_comment')
    # define managers
    objects = models.Manager() # the default manager.
    custom = CustomManager() # the custom manager.
    def __unicode__(self):
        return self.address
    class Meta:
        db_table = 'email_addresses'
        #unique_together = (('email_priority', 'person_or_org'), )
        # with this, I get 'ChangeManipulator' object has no attribute 'isUniqueemail_priority_person_or_org'
        verbose_name_plural = 'Email addresses'
    # override save function to handle 'priority'
    def save(self, *args, **kwargs):
        '''If no records exist with priority one, set priority = 1, otherwise
        For new records set priority = max + 1 (under 100)
        '''
        #if EmailAddress.objects.filter(person_or_org=self.person_or_org,priority=1).count() == 0:
        if not self.pk:
	    max = EmailAddress.objects.filter(person_or_org=self.person_or_org,priority__lt=100).aggregate(models.Max('priority'))['priority__max']
	    if not max:
		self.priority = 1
	    else:
		self.priority = max + 1
        super(EmailAddress, self).save(*args, **kwargs)

class GoalMilestone(models.Model):
    DONE_CHOICES = (
        ('Done', 'Done'),
        ('No', 'Not Done'),
    )
    # need to change gm_id to id to accomodate dynamic_inlines.js
    id = models.AutoField(primary_key=True,db_column='gm_id')
    group_acronym = models.ForeignKey('IETFWG')
    description = models.TextField()
    expected_due_date = models.DateField()
    done_date = models.DateField(null=True, blank=True)
    done = models.CharField(blank=True, choices=DONE_CHOICES, max_length=4)
    last_modified_date = models.DateField(auto_now=True)
    def __str__(self):
        return self.description
    class Meta:
        db_table = 'goals_milestones'
        verbose_name = 'IETF WG Goal or Milestone'
        verbose_name_plural = 'IETF WG Goals or Milestones'
        ordering = ['expected_due_date']
        
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
    cur_state = models.ForeignKey('IDState', db_column='cur_state', related_name='docs')
    prev_state = models.ForeignKey('IDState', db_column='prev_state', related_name='docs_prev')
    assigned_to = models.CharField(blank=True, max_length=25)
    mark_by = models.ForeignKey('IESGLogin', db_column='mark_by', related_name='marked')
    job_owner = models.ForeignKey('IESGLogin', db_column='job_owner', related_name='documents')
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

class IDIntendedStatus(models.Model):
    intended_status_id = models.AutoField(primary_key=True)
    intended_status = models.CharField(max_length=25, db_column='status_value')
    def __str__(self):
        return self.intended_status
    class Meta:
        db_table = "id_intended_status"
        verbose_name="I-D Intended Publication Status"
        verbose_name_plural="I-D Intended Publication Statuses"
        
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
        
class IDStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=25, db_column='status_value')
    def __str__(self):
        return self.status
    class Meta:
        db_table = "id_status"
        verbose_name="I-D Status"
        verbose_name_plural="I-D Statuses"

class IETFWG(models.Model):
    ACTIVE = 1
    #group_acronym = models.ForeignKey(Acronym, primary_key=True, unique=True, editable=False)
    group_acronym = models.OneToOneField(Acronym, parent_link=True, primary_key=True)
    group_type = models.ForeignKey('WGType')
    proposed_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    dormant_date = models.DateField(null=True, blank=True)
    concluded_date = models.DateField(null=True, blank=True)
    status = models.ForeignKey('WGStatus')
    area_director = models.ForeignKey(AreaDirector, null=True)
    # to conform with legacy db records this value is stored as "YES" or "NO"
    # for some reason we need to allow 5 characters max to accept true/false values
    # used by checkbox widgets the add/edit forms use
    meeting_scheduled = models.CharField(blank=True, max_length=5)
    email_address = models.CharField(blank=True, max_length=60)
    email_subscribe = models.CharField(blank=True, max_length=120)
    email_keyword = models.CharField(blank=True, max_length=50)
    email_archive = models.CharField(blank=True, max_length=95)
    comments = models.TextField(blank=True)
    last_modified_date = models.DateField(auto_now=True)
    meeting_scheduled_old = models.CharField(blank=True, max_length=3)
    #area = FKAsOneToOne('areagroup', reverse=True)
    # AMS add
    #not_meeting = models.ManyToManyField(Meeting,db_table='not_meeting_groups')
    def __str__(self):
        return self.group_acronym.acronym
    # added by AMS ----------------------------------
    def get_area(self):
        '''Returns the associated area defined in the area_group table.  There should
        only be one, but in some cases a record does not exist.'''
        try:
            ag = AreaGroup.objects.get(group=self.group_acronym)
            return ag.area
        except AreaGroup.DoesNotExist:
            return None
            
    def _get_area_name(self):
        return self.get_area().area_acronym.name
    def _get_area_acronym(self):
        return self.get_area().area_acronym.acronym
    def _get_group_name(self):
        return self.group_acronym.name
    def _get_group_acronym(self):
        return self.group_acronym.acronym
    area_name = property(_get_area_name)
    #area_acronym = property(_get_area_acronym)
    group_name = property(_get_group_name)
    acronym = property(_get_group_acronym)
    def is_not_meeting(self):
        '''Returns True if this group has been designated as not meeting at the next meeting'''
        next_meeting = Meeting.objects.all().order_by('-meeting_num')[0]
        #if NotMeetingGroups.objects.filter(group=self,meeting=next_meeting):
        if True:
            return True
        else:
            return False
    # end AMS add ------------------------------------
    def active_drafts(self):
        return self.group_acronym.internetdraft_set.all().filter(status__status="Active")
    def choices():
        return [(wg.group_acronym_id, wg.group_acronym.acronym) for wg in IETFWG.objects.all().filter(group_type__type='WG').select_related().order_by('acronym.acronym')]
    choices = staticmethod(choices)
    def area_acronym(self):
        areas = AreaGroup.objects.filter(group__exact=self.group_acronym)
        if areas:
            return areas[areas.count()-1].area.area_acronym
        else:
            return None
    def area_directors(self):
        areas = AreaGroup.objects.filter(group__exact=self.group_acronym)
        if areas:
            return areas[areas.count()-1].area.areadirector_set.all()
        else:
            return None
    def chairs(self): # return a set of WGChair objects for this work group
        return WGChair.objects.filter(group_acronym__exact=self.group_acronym)
    def secretaries(self): # return a set of WGSecretary objects for this group
        return WGSecretary.objects.filter(group_acronym__exact=self.group_acronym)
    def milestones(self): # return a set of GoalMilestone objects for this group
        return GoalMilestone.objects.filter(group_acronym__exact=self.group_acronym)
    def rfcs(self): # return a set of Rfc objects for this group
        return Rfc.objects.filter(group_acronym__exact=self.group_acronym)
    def drafts(self): # return a set of Rfc objects for this group
        return InternetDraft.objects.filter(group__exact=self.group_acronym)
    def charter_text(self): # return string containing WG description read from file
        # get file path from settings. Syntesize file name from path, acronym, and suffix
        try:
            filename = os.path.join(settings.IETFWG_DESCRIPTIONS_PATH, self.group_acronym.acronym) + ".desc.txt"
            desc_file = open(filename)
            desc = desc_file.read()
        except BaseException:
            desc =  'Error Loading Work Group Description'
        return desc
    def additional_urls(self):
        return AreaWGURL.objects.filter(name=self.group_acronym.acronym)
    def clean_email_archive(self):
        x = self.email_archive
        # remove "current/" and "maillist.html"
        x = re.sub("^(http://www\.ietf\.org/mail-archive/web/)([^/]+/)(current/)?([a-z]+\.html)?$", "\\1\\2", x)
        return x
    # override save function to handle boolean meeting_scheduled
    '''
    def save(self):
        if self.meeting_scheduled == 0 or self.meeting_scheduled == False or self.meeting_scheduled == "False":
            self.meeting_scheduled = 'NO'
        if self.meeting_scheduled == 1 or self.meeting_scheduled == True or self.meeting_scheduled == "True":
            self.meeting_scheduled = 'YES'
        super(IETFWG, self).save()
    '''

    class Meta:
        db_table = 'groups_ietf'
        ordering = ['?']        # workaround django wanting to sort by acronym but not joining with it
        verbose_name = 'IETF Working Group'

class InterimMeeting(models.Model):
    meeting_num = models.AutoField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True)
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
    
    # new fields
    group_acronym_id = models.IntegerField()

    # AMS Add
    def get_upload_root(self):
        path = os.path.join(settings.MEDIA_ROOT,
                            'proceedings/interim',
                            self.start_date.strftime('%Y'),
                            self.start_date.strftime('%m'),
                            self.start_date.strftime('%d'),
                            self.get_group_acronym())
        return path
    upload_root = property(get_upload_root)
    def get_proceedings_path(self, group=None):
        path = os.path.join(self.upload_root,'proceedings.html')
        return path
    def get_proceedings_url(self, group=None):
        url = "%s/proceedings/interim/%s/%s/%s/%s/proceedings.html" % (
            settings.MEDIA_URL,
            self.start_date.strftime('%Y'),
            self.start_date.strftime('%m'),
            self.start_date.strftime('%d'),
            self.get_group_acronym())
        return url  
    def get_group_acronym(self):
        try:
            acronym = Acronym.objects.get(acronym_id=self.group_acronym_id)
        except Acronym.DoesNotExist:
            return ''
        return acronym.acronym
    group_acronym = property(get_group_acronym)
    def get_group_name(self):
        try:
            acronym = Acronym.objects.get(acronym_id=self.group_acronym_id)
        except Acronym.DoesNotExist:
            return ''
        return acronym.name
    group_name = property(get_group_name)
    def __unicode__(self):
        #return str(self.meeting_num)
        name = "%s - %s/%s/%s" % (self.get_group_acronym(),
                                  self.start_date.strftime('%Y'),
                                  self.start_date.strftime('%m'),
                                  self.start_date.strftime('%d'))
        return name
                            
    def get_meeting_date (self,offset):
        return self.start_date + datetime.timedelta(days=offset)
    class Meta:
        db_table = 'interim_meetings'
        
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

class IRTF(models.Model):
    irtf_id = models.AutoField(primary_key=True)
    acronym = models.CharField(blank=True, max_length=25, db_column='irtf_acronym')
    name = models.CharField(blank=True, max_length=255, db_column='irtf_name')
    charter_text = models.TextField(blank=True,null=True)
    meeting_scheduled = models.BooleanField(blank=True)
    # AMS added
    def _get_area_name(self):
        return 'IRTF'
    def _get_area_acronym(self):
        return 'IRTF'
    def _get_group_name(self):
        return self.name
    def _get_group_acronym(self):
        return self.acronym
    area_name = property(_get_area_name)
    area_acronym = property(_get_area_acronym)
    group_name = property(_get_group_name)
    group_acronym = property(_get_group_acronym)
    # end AMS added

    def __str__(self):
        return self.acronym
    class Meta:
        db_table = 'irtf'
        verbose_name="IRTF Research Group"

class IRTFChair(models.Model):
    irtf = models.ForeignKey(IRTF)
    person = models.ForeignKey('PersonOrOrgInfo', db_column='person_or_org_tag')
    def __str__(self):
        return "%s is chair of %s" % (self.person, self.irtf)
    class Meta:
        db_table = 'irtf_chairs'
        verbose_name="IRTF Research Group Chair"
        
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
    # AMS Add
    groups_not_meeting = models.ManyToManyField(IETFWG,through=NotMeetingGroups,related_name='meetings_not_scheduled')
    irtf_not_meeting = models.ManyToManyField('IRTF',through=NotMeetingIRTF,related_name='meetings_not_scheduled')

    # AMS Add
    def get_upload_root(self):
        path = os.path.join(settings.PROCEEDINGS_DIR,str(self.meeting_num))
        return path
    upload_root = property(get_upload_root)
    def get_proceedings_path(self, group):
        path = os.path.join(self.upload_root,group.acronym + '.html')
        return path
    def get_proceedings_url(self, group):
        url = "%s/proceedings/%s/%s.html" % (
            settings.MEDIA_URL,
            self.meeting_num,
            group.acronym)
        return url
    def tz_display(self):
        d = dict(TIME_ZONE_CHOICES)
        return d[self.time_zone]
    # end AMS add
    def __unicode__(self):
        return str(self.meeting_num)
    def get_meeting_date (self,offset):
        return self.start_date + datetime.timedelta(days=offset)
    class Meta:
        db_table = 'meetings'

class MeetingHour(models.Model):
    hour_id = models.IntegerField(primary_key=True)
    hour_desc = models.CharField(max_length=60, blank=True)
    def __unicode__(self):
        return self.hour_desc
    class Meta:
        db_table = u'meeting_hours'

class MeetingTime(models.Model):
    DAYS = {-1: 'Saturday',
             0: 'Sunday',
             1: 'Monday',
             2: 'Tuesday',
             3: 'Wednesday',
             4: 'Thursday',
             5: 'Friday'}
    #time_id = models.AutoField(primary_key=True)
    id = models.AutoField(primary_key=True,db_column="time_id")
    time_desc = models.CharField(max_length=100)
    meeting = models.ForeignKey(Meeting, db_column='meeting_num')
    day_id = models.IntegerField()
    #session_name = models.ForeignKey(SessionName,null=True)
    session_name_id = models.IntegerField()
    def _get_session_name(self):
        if self.session_name_id == 0:
            return ''
        else:
            return SessionName.objects.get(session_name_id=self.session_name_id)
    session_name = property(_get_session_name)
    def __unicode__(self):
        #return "[%d] |%s| %s" % (self.meeting_id, (self.meeting.start_date + datetime.timedelta(self.day_id)).strftime('%A'), self.time_desc)
        return "%s %s %s" % ((self.meeting.start_date + datetime.timedelta(self.day_id)).strftime('%A'), self.session_name, self.time_desc)
    class Meta:
        db_table = 'meeting_times'
        
class MeetingRoom(models.Model):
    #room_id = models.AutoField(primary_key=True)
    id = models.AutoField(primary_key=True, db_column='room_id')
    meeting = models.ForeignKey(Meeting, db_column='meeting_num')
    room_name = models.CharField(max_length=255)
    def __unicode__(self):
        return "[%d] %s" % (self.meeting_id, self.room_name)
    class Meta:
        db_table = 'meeting_rooms'
        
class PersonOrOrgInfo(models.Model):
    person_or_org_tag = models.AutoField(primary_key=True, editable=False)
    record_type = models.CharField(blank=True, max_length=8, editable=False)
    name_prefix = models.CharField(blank=True, max_length=10)
    first_name = models.CharField(blank=True, max_length=20)
    first_name_key = models.CharField(blank=True, max_length=20, editable=False)
    middle_initial = models.CharField(blank=True, max_length=4)
    middle_initial_key = models.CharField(blank=True, max_length=4, editable=False)
    last_name = models.CharField(blank=True, max_length=50)
    last_name_key = models.CharField(blank=True, max_length=50, editable=False)
    name_suffix = models.CharField(blank=True, max_length=10)
    date_modified = models.DateField(null=True, blank=True, auto_now=True)
    modified_by = models.CharField(blank=True, max_length=8, editable=False)
    date_created = models.DateField(auto_now_add=True, editable=False)
    created_by = models.CharField(blank=True, max_length=8, editable=False)
    address_type = models.CharField(blank=True, max_length=4, editable=False)
    # define managers
    objects = models.Manager() # the default manager.
    custom = CustomManager() # the custom manager.
    def save(self):
        self.first_name_key = self.first_name.upper()
        self.middle_initial_key = self.middle_initial.upper()
        self.last_name_key = self.last_name.upper()
        super(PersonOrOrgInfo, self).save()
    def __unicode__(self):
        # For django.VERSION 1.x
        #if self.first_name == '' and self.last_name == '':
        #    return unicode(self.affiliation())
        return u"%s %s" % ( self.first_name or u"<nofirst>", self.last_name or u"<nolast>")
    def email(self, priority=1, type='INET'):
        name = str(self)
        try:
            email = self.emailaddress_set.get(priority=priority, type=type).address
        except (EmailAddress.DoesNotExist, EmailAddress.MultipleObjectsReturned):
            email = ''
        #return (name, email)
        return (email)
    # Added by Sunny Lee to display person's affiliation - 5/26/2007
    #def affiliation(self, priority=1):
    #    try:
    #        postal = self.postaladdress_set.get(address_priority=priority)
    #    except PostalAddress.DoesNotExist:
    #        return "PersonOrOrgInfo with no priority-%d postal address!" % priority
    #    except PostalAddress.MultipleObjectsReturned:
    #        return "PersonOrOrgInfo with multiple priority-%d addresses!" % priority
    #    return "%s" % ( postal.affiliated_company or postal.department or "???" )
    # returns boolean, true if telechat_users row exists, for use in templates
    #
    # reworked RC 6/17/2010, return highest priority affiliated company or
    # meaningful error message
    def affiliation(self, priority=1):
        qs = PostalAddress.objects.filter(person_or_org=self.person_or_org_tag).order_by('address_priority')
        for address in qs:
            if address.affiliated_company:
                return address.affiliated_company
        return '(no affiliated company defined)'
    def can_vote(self):
        try:
            tuser = TelechatUser.objects.get(person_or_org_tag=self.person_or_org_tag)
        except TelechatUser.DoesNotExist:
            return False
        return True

    class Meta:
        db_table = 'person_or_org_info'
        ordering = ['last_name']
        verbose_name="Rolodex Entry"
        verbose_name_plural="Rolodex"

# PostalAddress, EmailAddress and PhoneNumber are edited in
#  the admin for the Rolodex.
# The unique_together constraint is commented out for now, because
#  of a bug in oldforms and AutomaticManipulator which fails to
#  create the isUniquefoo_bar method properly.  Since django is
#  moving away from oldforms, I have to assume that this is going
#  to be fixed by moving admin to newforms.
# must decide which field is/are core.
class PostalAddress(models.Model):
    address_type = models.CharField(max_length=4,default='W')
    address_priority = models.IntegerField(null=True,default=1)
    person_or_org = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    person_title = models.CharField(max_length=50, blank=True)
    affiliated_company = models.CharField(max_length=70, blank=True)
    aff_company_key = models.CharField(max_length=70, blank=True, editable=False)
    department = models.CharField(max_length=100, blank=True)
    staddr1 = models.CharField(max_length=40, blank=True)
    staddr2 = models.CharField(max_length=40, blank=True)
    mail_stop = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=20, blank=True)
    state_or_prov = models.CharField(max_length=20, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=20, blank=True)
    def save(self):
        # set priority, number of existing items + 1
        self.address_priority = PostalAddress.objects.filter(person_or_org=self.person_or_org).count() + 1
        self.aff_company_key = self.affiliated_company.upper()
        super(PostalAddress, self).save()
    class Meta:
        db_table = 'postal_addresses'
        #unique_together = (('address_type', 'person_or_org'), )
        verbose_name_plural = 'Postal Addresses'

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
    status = models.ForeignKey('RfcStatus', db_column="status_id")
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
        
class RfcStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=25, db_column='status_value')
    def __str__(self):
        return self.status
    class Meta:
        db_table = 'rfc_status'
        verbose_name = 'RFC Status'
        verbose_name_plural = 'RFC Statuses'

class SessionName(models.Model):
    session_name_id = models.AutoField(primary_key=True)
    session_name = models.CharField(blank=True, max_length=255)
    def __unicode__(self):
        return self.session_name
    class Meta:
        db_table = 'session_names'
        
class SessionStatus(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=300, blank=True)
    def __unicode__(self):
        return self.status
    class Meta:
        db_table = u'session_status'
        
class SessionRequestActivity(models.Model):
    #id = models.IntegerField(primary_key=True)
    # group would be foreign key but can refer to many different objects
    group_acronym_id = models.IntegerField()
    meeting = models.ForeignKey(Meeting, db_column='meeting_num')
    activity = models.TextField(blank=True)
    act_date = models.DateField(auto_now=True)
    act_time = models.TimeField(auto_now=True)
    #act_by = models.IntegerField()
    act_by = models.ForeignKey(PersonOrOrgInfo, db_column='act_by')
    def __str__(self):
        return str(self.pk)
    class Meta:
        db_table = u'session_request_activities'
        
class TelechatUser(models.Model):
    #person_or_org_tag = models.ForeignKey(PersonOrOrgInfo)
    person_or_org_tag = models.IntegerField(primary_key=True)
    is_iesg = models.IntegerField(null=True, blank=True)
    affiliated_org = models.CharField(max_length=75, blank=True)
    def __unicode__(self):
        return self.affiliated_org
    class Meta:
        db_table = u'telechat_users'

class SessionConflict(models.Model):
    '''
    The original model from datatracker is flawed.  Both group_acronym and conflict_gid can 
    reference IRTF groups, which do not have a corresponding Acronym record, so the fields
    should not be FKs.  NOTE: removal of the FKs also disables reverse lookups from Acronym.
    ''' 
    #group_acronym = models.ForeignKey(Acronym, related_name='conflicts_set')
    #conflict_gid = models.ForeignKey(Acronym, related_name='conflicts_with_set', db_column='conflict_gid')
    group_acronym_id = models.IntegerField()
    conflict_gid = models.IntegerField()
    meeting_num = models.ForeignKey(Meeting, db_column='meeting_num')
    def __str__(self):
        try:
            return "At IETF %s, %s conflicts with %s" % ( self.meeting_num_id, self.group_acronym.acronym, self.conflict_gid.acronym)
        except BaseException:
            return "At IETF %s, something conflicts with something" % ( self.meeting_num_id )

    class Meta:
        db_table = 'session_conflicts'
        
class LegacyWgPassword(models.Model):
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag', primary_key=True)
    password = models.CharField(blank=True, null=True,max_length=255)
    secrete_question_id = models.IntegerField(null=True, blank=True)
    secrete_answer = models.CharField(blank=True, null=True, max_length=255)
    is_tut_resp = models.IntegerField(null=True, blank=True)
    irtf_id = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True,null=True)
    login_name = models.CharField(blank=True, max_length=100)
    def __str__(self):
        return self.login_name
    class Meta:
        db_table = 'wg_password'
        ordering = ['login_name']

class WGChair(models.Model):
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    group_acronym = models.ForeignKey(IETFWG)
    def __str__(self):
        return "%s (%s)" % ( self.person, self.role() )
    def role(self):
        return "%s %s Chair" % ( self.group_acronym, self.group_acronym.group_type )
    class Meta:
        db_table = 'g_chairs'
        verbose_name = "WG Chair"
        
class WgMeetingSession(models.Model):
    session_id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(Meeting, db_column='meeting_num')
    group_acronym_id = models.IntegerField()
    irtf = models.NullBooleanField(default=False)
    num_session = models.IntegerField()
    # AMS Changes
    #length_session1 = models.CharField(blank=True, max_length=100)
    #length_session2 = models.CharField(blank=True, max_length=100)
    #length_session3 = models.CharField(blank=True, max_length=100)
    LENGTH_SESSION_CHOICES = list(MeetingHour.objects.values_list('hour_id','hour_desc'))
    length_session1 = models.ForeignKey(MeetingHour,db_column="length_session1")
    length_session2 = models.ForeignKey(MeetingHour,db_column="length_session2",blank=True,null=True)
    #length_session3 = models.ForeignKey(MeetingHour,db_column="length_session3",blank=True,null=True)
    length_session3 = BrokenForeignKey(MeetingHour,db_column="length_session3",blank=True,null=True,null_values=('0',))
    conflict1 = models.CharField(blank=True, max_length=255)
    conflict2 = models.CharField(blank=True, max_length=255)
    conflict3 = models.CharField(blank=True, max_length=255)
    conflict_other = models.TextField(blank=True)
    special_req = models.TextField(blank=True)
    number_attendee = models.IntegerField()
    approval_ad = models.IntegerField(blank=True,default=0)
    status_id = models.IntegerField(default=1)
    ts_status_id = models.IntegerField(default=0)
    requested_date = models.DateField(default=datetime.date.today)
    approved_date = models.DateField(null=True, blank=True)
    requested_by = models.ForeignKey(PersonOrOrgInfo, db_column='requested_by')
    scheduled_date = models.DateField(null=True, blank=True)
    last_modified_date = models.DateField(auto_now=True)
    ad_comments = models.TextField(blank=True,null=True)
    sched_room_id1 = models.ForeignKey(MeetingRoom, db_column='sched_room_id1', null=True, blank=True, related_name='here1')
    sched_time_id1 = models.ForeignKey(MeetingTime, db_column='sched_time_id1', null=True, blank=True, related_name='now1')
    sched_date1 = models.DateField(null=True, blank=True)
    sched_room_id2 = models.ForeignKey(MeetingRoom, db_column='sched_room_id2', null=True, blank=True, related_name='here2')
    sched_time_id2 = models.ForeignKey(MeetingTime, db_column='sched_time_id2', null=True, blank=True, related_name='now2')
    sched_date2 = models.DateField(null=True, blank=True)
    sched_room_id3 = models.ForeignKey(MeetingRoom, db_column='sched_room_id3', null=True, blank=True, related_name='here3')
    sched_time_id3 = models.ForeignKey(MeetingTime, db_column='sched_time_id3', null=True, blank=True, related_name='now3')
    sched_date3 = models.DateField(null=True, blank=True)
    special_agenda_note = models.CharField(blank=True, max_length=255)
    #combined_room_id1 = models.ForeignKey(MeetingRoom, db_column='combined_room_id1', null=True, blank=True, related_name='here4')
    #combined_time_id1 = models.ForeignKey(MeetingTime, db_column='combined_time_id1', null=True, blank=True, related_name='now4')
    #combined_room_id2 = models.ForeignKey(MeetingRoom, db_column='combined_room_id2', null=True, blank=True, related_name='here5')
    #combined_time_id2 = models.ForeignKey(MeetingTime, db_column='combined_time_id2', null=True, blank=True, related_name='now5')
    combined_room_id1 = BrokenForeignKey(MeetingRoom, db_column='combined_room_id1', null=True, blank=True, related_name='here4')
    combined_time_id1 = BrokenForeignKey(MeetingTime, db_column='combined_time_id1', null=True, blank=True, related_name='now4')
    combined_room_id2 = BrokenForeignKey(MeetingRoom, db_column='combined_room_id2', null=True, blank=True, related_name='here5')
    combined_time_id2 = BrokenForeignKey(MeetingTime, db_column='combined_time_id2', null=True, blank=True, related_name='now5')

    # AMS added methods
    # they should have been ForeignKeys
    def _get_group(self):
        '''
        Returns a group(IETFWG) or IRTF object depending on the value of the irtf attribute
        Or returns an acronym object if it is a tutorial
        '''
        if self.group_acronym_id < 0:
            return Acronym.objects.get(acronym_id=self.group_acronym_id)
        if self.irtf:
            return IRTF.objects.get(irtf_id=self.group_acronym_id)
        else:
            return IETFWG.objects.get(group_acronym=self.group_acronym_id)
    group = property(_get_group)
    def _get_status(self):
        return str(SessionStatus.objects.get(status_id=self.status_id))
    status = property(_get_status)
    def _get_ts_status(self):
        return str(SessionStatus.objects.get(status_id=self.ts_status_id))
    ts_status = property(_get_ts_status)
    def _get_other_group_conflicts(self):
        object_list = []
        session_conflicts = SessionConflict.objects.filter(meeting_num=self.meeting,conflict_gid=self.group_acronym_id)
        for item in session_conflicts:
            object_list.append(get_group_or_404(item.group_acronym_id))
        names_list = [ str(x) for x in object_list ]
        other_groups = ', '.join(names_list)
        return other_groups
    other_group_conflicts = property(_get_other_group_conflicts)
    def _get_real_num_session(self):
        if self.num_session == 2 and self.ts_status_id in (3,4):
            return 3
        else:
            return self.num_session
    real_num_session = property(_get_real_num_session)
    # end AMS --------
        
    def __unicode__(self):
        return "%s %s " %(self.group_acronym_id,self.meeting)
    class Meta:
        db_table = 'wg_meeting_sessions'
        
# Note: there is an empty table 'g_secretary'.
# This uses the 'g_secretaries' table but is called 'GSecretary' to
# match the model naming scheme.
class WGSecretary(models.Model):
    group_acronym = models.ForeignKey(IETFWG)
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    def __str__(self):
        return "%s (%s)" % ( self.person, self.role() )
    def role(self):
        return "%s %s Secretary" % ( self.group_acronym, self.group_acronym.group_type )
    class Meta:
        db_table = 'g_secretaries'
        verbose_name = "WG Secretary"
        verbose_name_plural = "WG Secretaries"
        
class WGStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=25, db_column='status_value')
    def __str__(self):
        return self.status
    class Meta:
        verbose_name = "WG Status"
        verbose_name_plural = "WG Statuses"
        db_table = 'g_status'
        
class WGEditor(models.Model):
    group_acronym = models.ForeignKey(IETFWG)
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag', unique=True)
    class Meta:
        db_table = 'g_editors'
        verbose_name = "WG Editor"

class WGTechAdvisor(models.Model):
    group_acronym = models.ForeignKey(IETFWG)
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    def __str__(self):
        return "%s (%s)" % ( self.person, self.role() )
    def role(self):
        return "%s Technical Advisor" % self.group_acronym
    class Meta:
        db_table = 'g_tech_advisors'
        verbose_name = "WG Technical Advisor"

class WGType(models.Model):
    group_type_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=25, db_column='group_type')
    def __str__(self):
        return self.type
    class Meta:
        verbose_name = "WG Type"
        db_table = 'g_type'
