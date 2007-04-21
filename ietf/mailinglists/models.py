from django.db import models
from ietf.idtracker.models import Acronym, PersonOrOrgInfo

class ImportedMailingList(models.Model):
    group_acronym = models.ForeignKey(Acronym)
    list_acronym = models.CharField(blank=True, maxlength=255)
    list_name = models.CharField(blank=True, maxlength=255)
    list_domain = models.CharField(blank=True, maxlength=25)
    def __str__(self):
	return self.list_name or self.group_acronym
    class Meta:
        db_table = 'imported_mailing_list'
    class Admin:
	pass

class MailingList(models.Model):
    SUBSCRIPTION_CHOICES = (
	('1', 'Confirm'),
	('2', 'Approval'),
	('3', 'Confirm+Approval'),
    )
    MAILTYPE_CHOICES = (
	('1', 'Create new WG email list at ietf.org'),
	('2', 'Move existing WG email list to ietf.org'),
	('3', 'Move existing non-WG email list to selected domain'),
	('4', 'Create new non-WG email list at selected domain'),
	('5', 'Close existing WG email list at ietf.org'),
	('6', 'Close existing non-WG email list at selected domain'),
    )
    # I don't understand the reasoning behind 2 vs 3.
    # this is set in the javascript and not editable,
    # so I think there's a 1:1 mapping from mail_type -> mail_cat.
    # The existing database doesn't help much since many
    # mail_cat values are NULL.
    MAILCAT_CHOICES = (
	('1', 'WG Mailing List'),
	('2', 'Non-WG Mailing List'),
	('3', 'Close Non-WG Mailing List'),
    )
    mailing_list_id = models.CharField('Unique ID', primary_key=True, maxlength=25)
    request_date = models.DateField()
    mlist_name = models.CharField('Mailing list name', maxlength=250)
    short_desc = models.CharField(maxlength=250)
    long_desc = models.TextField(blank=True)
    requestor = models.CharField(maxlength=250)
    requestor_email = models.CharField(maxlength=250)
    # admins is a VARCHAR but can have multiple lines
    admins = models.TextField(blank=True, maxlength=250)
    archive_remote = models.TextField(blank=True)
    archive_private = models.BooleanField()
    initial = models.TextField('Initial members',blank=True)
    welcome_message = models.TextField(blank=True)
    subscription = models.IntegerField(choices=SUBSCRIPTION_CHOICES)
    post_who = models.BooleanField('Only members can post')
    post_admin = models.BooleanField('Administrator approval required for posts')
    add_comment = models.TextField(blank=True)
    mail_type = models.IntegerField(choices=MAILTYPE_CHOICES)
    mail_cat = models.IntegerField(choices=MAILCAT_CHOICES)
    auth_person = models.ForeignKey(PersonOrOrgInfo, db_column='auth_person_or_org_tag', raw_id_admin=True)
    welcome_new = models.TextField(blank=True)
    approved = models.BooleanField()
    approved_date = models.DateField(null=True, blank=True)
    reason_to_delete = models.TextField(blank=True)
    domain_name = models.CharField(blank=True, maxlength=10)
    def __str__(self):
	return self.mlist_name
    class Meta:
        db_table = 'mailing_list'
    class Admin:
	pass

