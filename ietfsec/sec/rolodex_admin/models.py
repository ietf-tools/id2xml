from django.db import models
from django.db import connection

# Changes
# fixed person_or_org_info:affiliation error handling
# add canabolized area_director and wg_chair models w/ FKs and methods commented out

class PersonOrOrgInfo(models.Model):
    person_or_org_tag = models.AutoField(primary_key=True)
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
    modified_by = models.CharField(blank=True, max_length=8, editable=False, default="INTERNAL")
    date_created = models.DateField(auto_now_add=True)
    created_by = models.CharField(blank=True, max_length=8, editable=False, default="INTERNAL")
    address_type = models.CharField(blank=True, max_length=4, editable=False)
    # custom delete to delete area_director and wg_chair entries
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
    def affiliation(self, priority=1):
        try:
            postal = self.postaladdress_set.get(address_priority=priority)
        except PostalAddress.DoesNotExist:
            return "PersonOrOrgInfo with no postal address!"
        except PostalAddress.MultipleObjectsReturned:
            return "PersonOrOrgInfo with multiple priority-%d addresses!" % priority
        return "%s" % ( postal.affiliated_company or postal.department or "???" )
    class Meta:
        db_table = 'person_or_org_info'
        ordering = ['last_name']
        verbose_name="Rolodex Entry"
        verbose_name_plural="Rolodex"

class EmailAddress(models.Model):
    person_or_org = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    type = models.CharField(max_length=4, db_column='email_type',default='INET')
    priority = models.IntegerField(db_column='email_priority',default=1,editable=False)
    address = models.CharField(max_length=255, db_column='email_address')
    comment = models.CharField(blank=True, max_length=255, db_column='email_comment')
    def __unicode__(self):
        return self.address
    class Meta:
        db_table = 'email_addresses'
        #unique_together = (('email_priority', 'person_or_org'), )
        # with this, I get 'ChangeManipulator' object has no attribute 'isUniqueemail_priority_person_or_org'
        verbose_name_plural = 'Email addresses'
    # override save function to handle 'priority'
    def save(self):
        # set priority, max + 1 (under 100) 
        max = EmailAddress.objects.filter(person_or_org=self.person_or_org,priority__lt=100).aggregate(models.Max('priority'))['priority__max']
        if not max:
            self.priority = 1
        else:
            self.priority = max + 1
        super(EmailAddress, self).save()

class PhoneNumber(models.Model):
    person_or_org = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    phone_type = models.CharField(max_length=3,default='W')
    phone_priority = models.IntegerField(default='1', editable=False)
    phone_number = models.CharField(blank=True, max_length=255)
    phone_comment = models.CharField(blank=True, max_length=255)
    def __unicode__(self):
        return self.phone_number
    class Meta:
        db_table = 'phone_numbers'
        verbose_name_plural = "Phone Numbers"
        #unique_together = (('phone_priority', 'person_or_org'), )
    # override save function to handle 'phone_priority'
    def save(self):
        # set priority, number of existing items + 1
        self.phone_priority = PhoneNumber.objects.filter(person_or_org=self.person_or_org).count() + 1
        super(PhoneNumber, self).save()

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
    address_priority = models.IntegerField(null=True,default=1,editable=False)
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

# stripped down model to allow deleting records
class AreaDirector(models.Model):
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    def __str__(self):
        return "%s" % ( self.person )
    class Meta:
        db_table = 'area_directors'

# stripped down model to allow deleting records
class WGChair(models.Model):
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag', unique=True)
    def __str__(self):
        return "%s" % ( self.person )
    class Meta:
        db_table = 'g_chairs'
        verbose_name = "WG Chair"
