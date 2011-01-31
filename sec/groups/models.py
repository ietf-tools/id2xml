from django.db import models
from sec.core.models import Acronym, Area, AreaDirector, AreaStatus, PersonOrOrgInfo

# area_acronym_id is used as a foreign key to both areas or acronym tables
# (see selectareaallshort.cfm and selectsecondaryareas.cfm)
# group_acronym_id is a foreign key to groups_ietf.group_acronym_id (see selectgroupcurrentprimaryarea.cfm)

class WGType(models.Model):
    group_type_id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=25, db_column='group_type')
    def __str__(self):
        return self.type
    class Meta:
        verbose_name = "WG Type"
        db_table = 'g_type'

class WGStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=25, db_column='status_value')
    def __str__(self):
        return self.status
    class Meta:
        verbose_name = "WG Status"
        verbose_name_plural = "WG Statuses"
        db_table = 'g_status'

class IETFWG(models.Model):
    ACTIVE = 1
    #group_acronym = models.ForeignKey(Acronym, primary_key=True, unique=True, editable=False)
    group_acronym = models.OneToOneField(Acronym, parent_link=True, primary_key=True)
    group_type = models.ForeignKey(WGType)
    proposed_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    dormant_date = models.DateField(null=True, blank=True)
    concluded_date = models.DateField(null=True, blank=True)
    status = models.ForeignKey(WGStatus)
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
    def __str__(self):
        return self.group_acronym.acronym
    # added by AMS
    def get_area(self):
        '''Returns the associated area defined in the area_group table.  There should
        only be one, but in some cases a record does not exist.'''
        try:
            ag = AreaGroup.objects.get(group=self.group_acronym)
            return ag.area
        except AreaGroup.DoesNotExist:
            return None
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

class WGEditor(models.Model):
    group_acronym = models.ForeignKey(IETFWG)
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag', unique=True)
    class Meta:
        db_table = 'g_editors'
        verbose_name = "WG Editor"

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

class AreaGroup(models.Model):
    area = models.ForeignKey(Area, db_column='area_acronym_id', related_name='areagroup')
    group = models.ForeignKey(IETFWG, db_column='group_acronym_id', unique=True)
    def __str__(self):
        return "%s is in %s" % ( self.group, self.area )
    class Meta:
        db_table = 'area_group'
        verbose_name = 'Area this group is in'
        verbose_name_plural = 'Area to Group mappings'

class GoalMilestone(models.Model):
    DONE_CHOICES = (
        ('Done', 'Done'),
        ('No', 'Not Done'),
    )
    # need to change gm_id to id to accomodate dynamic_inlines.js
    id = models.AutoField(primary_key=True,db_column='gm_id')
    group_acronym = models.ForeignKey(IETFWG)
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

class WGChair(models.Model):
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    group_acronym = models.ForeignKey('IETFWG')
    def __str__(self):
        return "%s (%s)" % ( self.person, self.role() )
    def role(self):
        return "%s %s Chair" % ( self.group_acronym, self.group_acronym.group_type )
    class Meta:
        db_table = 'g_chairs'
        verbose_name = "WG Chair"

class WGAWP(models.Model):
    id = models.AutoField(primary_key=True, db_column='area_ID')
    #name = models.CharField(max_length=50, db_column='area_Name')
    # For WGs, this is the WG acronym; for areas, it's the area name.
    name = models.ForeignKey(Acronym, to_field='acronym', db_column='area_Name')
    url = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=50, blank=True)
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.description)
    class Meta:
        ordering = ['name']
        verbose_name = "Area/WG URL"
        db_table = "wg_www_pages"
        # this is required to prevent tests from trying to create the table twice
        managed = False

