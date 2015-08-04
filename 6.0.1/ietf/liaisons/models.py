# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf import settings
from django.core.urlresolvers import reverse as urlreverse
from django.db import models
from django.utils.text import slugify

from ietf.person.models import Email, Person
from ietf.name.models import (LiaisonStatementPurposeName, LiaisonStatementState,
                              LiaisonStatementEventTypeName, LiaisonStatementTagName,
                              DocRelationshipName)
from ietf.doc.models import Document
from ietf.group.models import Group


class LiaisonStatement(models.Model):
    title = models.CharField(blank=True, max_length=255)
    other_identifiers = models.TextField(blank=True, null=True) # Identifiers from other bodies
    purpose = models.ForeignKey(LiaisonStatementPurposeName)
    body = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)

    from_groups = models.ManyToManyField(Group, blank=True, related_name='liaisonstatement_from_set')
    from_name = models.CharField(max_length=255, help_text="Name of the sender body")
    to_groups = models.ManyToManyField(Group, blank=True, related_name='liaisonstatement_to_set') 
    to_name = models.CharField(max_length=255, help_text="Name of the recipient body")

    tags = models.ManyToManyField(LiaisonStatementTagName, blank=True, null=True)

    from_contact = models.ForeignKey(Email, blank=True, null=True)
    to_contacts = models.CharField(blank=True, max_length=255, help_text="Contacts at recipient body") 
    response_contacts = models.CharField(blank=True, max_length=255, help_text="Where to send a response") # RFC4053 
    technical_contacts = models.CharField(blank=True, max_length=255, help_text="Who to contact for clarification") # RFC4053
    action_holder_contacts = models.CharField(blank=True, max_length=255, help_text="Who makes sure action is completed")  # incoming only?
    cc_contacts = models.TextField(blank=True)

    attachments = models.ManyToManyField(Document, through='LiaisonStatementAttachment', blank=True)

    state = models.ForeignKey(LiaisonStatementState, default='pending')

    def __unicode__(self):
        return self.title or u"<no title>"

    def get_absolute_url(self):
        return settings.IDTRACKER_BASE_URL + urlreverse('liaison_detail',kwargs={'object_id':self.id})

    def name(self):
        if self.from_groups.count():
            frm = ', '.join([i.acronym or i.name for i in self.from_groups.all()])
        else:
            frm = self.from_name
        if self.to_groups.count():
            to = ', '.join([i.acronym or i.name for i in self.to_groups.all()])
        else:
            to = self.to_name
        return slugify("liaison" + " " + self.submitted.strftime("%Y-%m-%d") + " " + frm[:50] + " " + to[:50] + " " + self.title[:115])

    @property
    def submitted(self):
        if getattr(self, '_submitted', None):
            return self._submitted
        event = self.liaisonstatementevent_set.filter(type__slug='submitted')
        if event.count():
            return event[0].time
        return None
    
    @property
    def modified(self):
        event = self.liaisonstatementevent_set.all().order_by('-time').first()
        if event:
            return event.time
        return None

    @property
    def approved(self):
        return self.state_id == 'approved'

    @property
    def action_taken(self):
        return bool(self.tags.filter(slug='taken').count())

    @property
    def awaiting_action(self):
        if getattr(self, '_awaiting_action', None) != None:
            return bool(self._awaiting_action)
        return bool(self.tags.filter(slug='awaiting').count())

    @property
    def from_groups_display(self):
        groups = self.from_groups.order_by('name').values_list('name',flat=True)
        return ', '.join(groups)

    @property
    def to_groups_display(self):
        groups = self.to_groups.order_by('name').values_list('name',flat=True)
        return ', '.join(groups)


class LiaisonStatementAttachment(models.Model):
    statement = models.ForeignKey(LiaisonStatement)
    document = models.ForeignKey(Document)
    removed = models.BooleanField(default=False)


class RelatedLiaisonStatement(models.Model):
    source = models.ForeignKey(LiaisonStatement, related_name='source_of_set')
    target = models.ForeignKey(LiaisonStatement, related_name='target_of_set')
    relationship = models.ForeignKey(DocRelationshipName)


class LiaisonStatementGroupContacts(models.Model):
    group = models.ForeignKey(Group, unique=True) 
    contacts = models.CharField(max_length=255)

    def __unicode__(self):
        return u"{}:{}".format(self.group.name,self.contacts)


class LiaisonStatementEvent(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    type = models.ForeignKey(LiaisonStatementEventTypeName)
    by = models.ForeignKey(Person)
    statement = models.ForeignKey(LiaisonStatement)
    desc = models.TextField()
    
    def __unicode__(self):
        return u"%s %s by %s at %s" % (self.statement.title, self.type.slug, self.by.plain_name(), self.time)

    class Meta:
        ordering = ['-time', '-id']
