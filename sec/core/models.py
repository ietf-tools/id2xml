from django.db import models
from django.db import connection

STATUS_TYPES = (
    ('1', 'Active'),
    ('2', 'Concluded'),
    ('3', 'Unknown'),
)

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

class AreaStatus(models.Model):
    status_id = models.AutoField(primary_key=True, db_column='status_id')
    status_value = models.CharField(max_length=25, db_column='status_value')
    def __unicode__(self):
        return str(self.status_id)
    class Meta:
        db_table = 'area_status'

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

class TelechatUser(models.Model):
    #person_or_org_tag = models.ForeignKey(PersonOrOrgInfo)
    person_or_org_tag = models.IntegerField(primary_key=True)
    is_iesg = models.IntegerField(null=True, blank=True)
    affiliated_org = models.CharField(max_length=75, blank=True)
    def __unicode__(self):
        return self.affiliated_org
    class Meta:
        db_table = u'telechat_users'

