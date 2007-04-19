from django.db import models

class Acronym(models.Model):
    acronym_id = models.AutoField(primary_key=True)
    acronym = models.CharField(maxlength=12)
    name = models.CharField(maxlength=100)
    name_key = models.CharField(maxlength=50, editable=False)
    def save(self):
        self.name_key = self.name.upper()
	super(Acronym, self).save()
    def __str__(self):
        return self.acronym
    class Meta:
        db_table = "acronym"
    class Admin:
        list_display = ('acronym', 'name')
        pass

class AreaStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status = models.CharField(maxlength=25, db_column='status_value')
    def __str__(self):
	return self.status
    class Meta:
        db_table = 'area_status'
    class Admin:
        pass

# I think equiv_group_flag is historical.
class IDState(models.Model):
    document_state_id = models.AutoField(primary_key=True)
    state = models.CharField(maxlength=50, db_column='document_state_val')
    equiv_group_flag = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True, db_column='document_desc')
    def __str__(self):
        return self.state
    class Meta:
        db_table = 'ref_doc_states_new'

class IDSubState(models.Model):
    sub_state_id = models.AutoField(primary_key=True)
    sub_state = models.CharField(maxlength=55, db_column='sub_state_val')
    description = models.TextField(blank=True, db_column='sub_state_desc')
    def __str__(self):
        return self.sub_state
    class Meta:
        db_table = 'sub_state'


class Areas(models.Model):
    area_acronym = models.ForeignKey(Acronym, primary_key=True, unique=True)
    start_date = models.DateField(auto_now_add=True)
    concluded_date = models.DateField(null=True, blank=True)
    status = models.ForeignKey(AreaStatus)
    comments = models.TextField(blank=True)
    last_modified_date = models.DateField(auto_now=True)
    extra_email_addresses = models.TextField(blank=True)
    def __str__(self):
	return self.area_acronym.acronym
    class Meta:
        db_table = 'areas'
        #ordering = ['area_acronym_id']
	verbose_name="area"
    class Admin:
        list_display = ('area_acronym', 'status')
	pass

class IDStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status = models.CharField(maxlength=25, db_column='status_value')
    def __str__(self):
        return self.status
    class Meta:
        db_table = "id_status"
	verbose_name="I-D Status"
	verbose_name_plural="I-D Statuses"
    class Admin:
        pass

class IDIntendedStatus(models.Model):
    intended_status_id = models.AutoField(primary_key=True)
    intended_status = models.CharField(maxlength=25, db_column='status_value')
    def __str__(self):
        return self.intended_status
    class Meta:
        db_table = "id_intended_status"
	verbose_name="I-D Intended Publication Status"
	verbose_name_plural="I-D Intended Publication Statuses"
    class Admin:
        pass

class InternetDraft(models.Model):
    id_document_tag = models.AutoField(primary_key=True)
    id_document_name = models.CharField(maxlength=255)
    id_document_key = models.CharField(maxlength=255, editable=False)
    group = models.ForeignKey(Acronym, db_column='group_acronym_id')
    filename = models.CharField(maxlength=255, unique=True)
    revision = models.CharField(maxlength=2)
    revision_date = models.DateField()
    file_type = models.CharField(maxlength=20)
    txt_page_count = models.IntegerField()
    local_path = models.CharField(maxlength=255)
    start_date = models.DateField()
    expiration_date = models.DateField()
    abstract = models.TextField()
    dunn_sent_date = models.DateField()
    extension_date = models.DateField()
    status = models.ForeignKey(IDStatus)
    intended_status = models.ForeignKey(IDIntendedStatus)
    lc_sent_date = models.DateField()
    lc_changes = models.CharField(maxlength=3)
    lc_expiration_date = models.DateField()
    b_sent_date = models.DateField()
    b_discussion_date = models.DateField()
    b_approve_date = models.DateField()
    wgreturn_date = models.DateField()
    rfc_number = models.IntegerField()
    comments = models.TextField()
    last_modified_date = models.DateField()
    replaced_by = models.ForeignKey('self', db_column='replaced_by')
    review_by_rfc_editor = models.IntegerField()	# boolean
    expired_tombstone = models.IntegerField() # boolean
    def save(self):
        self.id_document_key = self.id_document_name.upper()
        super(InternetDraft, self).save()
    def __str__(self):
        return self.filename
    def idinternal(self):
	if len(self.idinternal_set.all()) == 0:
	    return None
	else:
	    return self.idinternal_set.all()[0]
    def idstate(self):
	idinternal = self.idinternal()
	if idinternal:
	    if idinternal.cur_sub_state:
		return "%s :: %s" % ( idinternal.cur_state, idinternal.cur_sub_state )
	    else:
		return idinternal.cur_state
	else:
	    return "I-D Exists"
    class Meta:
        db_table = "internet_drafts"
    class Admin:
        search_fields = ['filename']
        pass
        #list_display = ('filename', 'revision', 'status')
        #date_hierarchy = 'revision_date'
        #list_filter = ['revision_date']

class PersonOrOrgInfo(models.Model):
    person_or_org_tag = models.AutoField(primary_key=True)
    record_type = models.CharField(blank=True, maxlength=8)
    name_prefix = models.CharField(blank=True, maxlength=10)
    first_name = models.CharField(blank=True, maxlength=20)
    first_name_key = models.CharField(blank=True, maxlength=20, editable=False)
    middle_initial = models.CharField(blank=True, maxlength=4)
    middle_initial_key = models.CharField(blank=True, maxlength=4, editable=False)
    last_name = models.CharField(blank=True, maxlength=50)
    last_name_key = models.CharField(blank=True, maxlength=50, editable=False)
    name_suffix = models.CharField(blank=True, maxlength=10)
    date_modified = models.DateField(null=True, blank=True, auto_now=True)
    modified_by = models.CharField(blank=True, maxlength=8)
    date_created = models.DateField(auto_now_add=True)
    created_by = models.CharField(blank=True, maxlength=8)
    address_type = models.CharField(blank=True, maxlength=4)
    def save(self):
        self.first_name_key = self.first_name.upper()
        self.middle_initial_key = self.middle_initial.upper()
        self.last_name_key = self.last_name.upper()
        super(PersonOrOrgInfo, self).save()
    def __str__(self):
        return "%s %s" % ( self.first_name or "<nofirst>", self.last_name or "<nolast>")
    class Meta:
        db_table = 'person_or_org_info'
	ordering = ['last_name']
	verbose_name="Rolodex Entry"
	verbose_name_plural="Rolodex"
    class Admin:
        search_fields = ['first_name','last_name']
        pass

# could use a mapping for user_level
class IESGLogin(models.Model):
    USER_LEVEL_CHOICES = (
	('0', 'Secretariat'),
	('1', 'IESG'),
	('2', 'ex-IESG'),
	('3', 'Level 3'),
	('4', 'Comment Only(?)'),
    )
    id = models.AutoField(primary_key=True)
    login_name = models.CharField(blank=True, maxlength=255)
    password = models.CharField(maxlength=25)
    user_level = models.IntegerField(choices=USER_LEVEL_CHOICES)
    first_name = models.CharField(blank=True, maxlength=25)
    last_name = models.CharField(blank=True, maxlength=25)
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag', raw_id_admin=True, unique=True)
    pgp_id = models.CharField(blank=True, maxlength=20)
    default_search = models.IntegerField(null=True)
    def __str__(self):
        return "%s, %s" % ( self.last_name, self.first_name)
    class Meta:
        db_table = 'iesg_login'
    class Admin:
	list_display = ('login_name', 'first_name', 'last_name', 'user_level')
        ordering = ['user_level','last_name']
	pass

class IDInternal(models.Model):
    draft = models.ForeignKey(InternetDraft, primary_key=True, unique=True, db_column='id_document_tag')
    # the above ignores the possibility that it's an RFC.
    rfc_flag = models.IntegerField(null=True)
    ballot_id = models.IntegerField()
    primary_flag = models.IntegerField(null=True, blank=True)
    group_flag = models.IntegerField(blank=True)
    token_name = models.CharField(blank=True, maxlength=25)
    token_email = models.CharField(blank=True, maxlength=255)
    note = models.TextField(blank=True)
    status_date = models.DateField(null=True)
    email_display = models.CharField(blank=True, maxlength=50)
    agenda = models.IntegerField(null=True, blank=True)
    cur_state = models.ForeignKey(IDState, db_column='cur_state', related_name='docs')
    prev_state = models.ForeignKey(IDState, db_column='prev_state', related_name=None)
    assigned_to = models.CharField(blank=True, maxlength=25)
    mark_by = models.ForeignKey(IESGLogin, db_column='mark_by', related_name='marked')
    job_owner = models.ForeignKey(IESGLogin, db_column='job_owner', related_name='documents')
    event_date = models.DateField(null=True)
    area_acronym = models.ForeignKey(Areas)
    cur_sub_state = models.ForeignKey(IDSubState, related_name='docs', null=True, blank=True)
    prev_sub_state = models.ForeignKey(IDSubState, related_name=None, null=True, blank=True)
    returning_item = models.IntegerField(null=True, blank=True)
    telechat_date = models.DateField(null=True, blank=True)
    via_rfc_editor = models.IntegerField(null=True, blank=True)
    state_change_notice_to = models.CharField(blank=True, maxlength=255)
    dnp = models.IntegerField(null=True, blank=True)
    dnp_date = models.DateField(null=True, blank=True)
    noproblem = models.IntegerField(null=True, blank=True)
    resurrect_requested_by = models.ForeignKey(IESGLogin, db_column='resurrect_requested_by', related_name='docsresurrected', null=True, blank=True)
    approved_in_minute = models.IntegerField(null=True, blank=True)
    def __str__(self):
        if self.rfc_flag:
	    return "RFC%04d" % ( self.id_document_tag )
	else:
	    return self.id_document_tag.filename
    class Meta:
        db_table = 'id_internal'
	verbose_name = 'IDTracker Draft'
    class Admin:
	pass

# should edit in document admin?
class IDAuthors(models.Model):
    document = models.ForeignKey(InternetDraft, db_column='id_document_tag', related_name='authors', raw_id_admin=True)
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag', raw_id_admin=True)
    author_order = models.IntegerField(null=True, blank=True)
    def __str__(self):
	return "%s authors %s" % ( self.person, self.document.filename )
    def email(self):
	addr = self.person.emailaddresses_set.filter(type='I-D').filter(priority=self.document_id)
	try:
	    return addr[0].address
	except IndexError:	# no [0]
	    return None
    class Meta:
        db_table = 'id_authors'
	verbose_name = "I-D Author"
        ordering = ['document','author_order']
    class Admin:
	pass

# PostalAddress, EmailAddress and PhoneNumber are edited in
#  the admin for the Rolodex.
# The unique_together constraint is commented out for now, because
#  of a bug in oldforms and AutomaticManipulator which fails to
#  create the isUniquefoo_bar method properly.  Since django is
#  moving away from oldforms, I have to assume that this is going
#  to be fixed by moving admin to newforms.
# A table without a unique primary key!
# must decide which field is/are core.
class PostalAddress(models.Model):
    address_type = models.CharField(maxlength=4)
    address_priority = models.IntegerField(null=True)
    person_or_org = models.ForeignKey(PersonOrOrgInfo, primary_key=True, db_column='person_or_org_tag', edit_inline=models.STACKED)
    person_title = models.CharField(maxlength=50, blank=True)
    affiliated_company = models.CharField(maxlength=70, blank=True)
    # always uppercase(affiliated_company)
    aff_company_key = models.CharField(maxlength=70, blank=True, editable=False)
    department = models.CharField(maxlength=100, blank=True)
    staddr1 = models.CharField(maxlength=40, core=True)
    staddr2 = models.CharField(maxlength=40, blank=True)
    mail_stop = models.CharField(maxlength=20, blank=True)
    city = models.CharField(maxlength=20, blank=True)
    state_or_prov = models.CharField(maxlength=20, blank=True)
    postal_code = models.CharField(maxlength=20, blank=True)
    country = models.CharField(maxlength=20, blank=True)
    def save(self):
	self.aff_company_key = self.affiliated_company.upper()
	super(PersonOrOrgInfo, self).save()
    class Meta:
        db_table = 'postal_addresses'
	#unique_together = (('address_type', 'person_or_org'), )
	verbose_name_plural = 'Postal Addresses'

class EmailAddress(models.Model):
    person_or_org = models.ForeignKey(PersonOrOrgInfo, primary_key=True, db_column='person_or_org_tag', edit_inline=models.TABULAR)
    type = models.CharField(maxlength=12, db_column='email_type')
    priority = models.IntegerField(db_column='email_priority')
    address = models.CharField(maxlength=255, core=True, db_column='email_address')
    comment = models.CharField(blank=True, maxlength=255, db_column='email_comment')
    def __str__(self):
	return self.address
    class Meta:
        db_table = 'email_addresses'
	#unique_together = (('email_priority', 'person_or_org'), )
	# with this, I get 'ChangeManipulator' object has no attribute 'isUniqueemail_priority_person_or_org'

class PhoneNumber(models.Model):
    person_or_org = models.ForeignKey(PersonOrOrgInfo, primary_key=True, db_column='person_or_org_tag', edit_inline=models.TABULAR)
    phone_type = models.CharField(maxlength=3)
    phone_priority = models.IntegerField()
    phone_number = models.CharField(blank=True, maxlength=255, core=True)
    phone_comment = models.CharField(blank=True, maxlength=255)
    class Meta:
        db_table = 'phone_numbers'
	#unique_together = (('phone_priority', 'person_or_org'), )

# No admin panel needed; this is edited in Areas.
class AreaDirectors(models.Model):
    id = models.AutoField(primary_key=True)
    area = models.ForeignKey(Areas, db_column='area_acronym_id', edit_inline=models.STACKED, num_in_admin=2)
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag', raw_id_admin=True, core=True, unique=True)
    def __str__(self):
        return "(%s) %s" % ( self.area, self.person )
    class Meta:
        db_table = 'area_directors'
