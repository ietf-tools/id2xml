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

    def do_approve(self, person):
        """Change to approved state, create event"""
        self.set_state('approved')
        LiaisonStatementEvent.objects.create(
            type_id='approved',
            by=person,
            statement=self,
            desc='Statement Approved'
        )
    
    def do_kill(self, person):
        """Change to dead state, create event"""
        self.set_state('dead')
        LiaisonStatementEvent.objects.create(
            type_id='killed',
            by=person,
            statement=self,
            desc='Statement Killed'
        )
        
    def do_post(self, person):
        """Change to posted state, create event"""
        self.set_state('posted')
        LiaisonStatementEvent.objects.create(
            type_id='posted',
            by=person,
            statement=self,
            desc='Statement Posted'
        )
    
    def do_resurrect(self, person):
        """Change to pending pending, create event"""
        self.set_state('pending')
        LiaisonStatementEvent.objects.create(
            type_id='resurrected',
            by=person,
            statement=self,
            desc='Statement Resurrected'
        )
    
    def do_submit(self, person):
        """Change to pending state, create event"""
        self.set_state('pending')
        LiaisonStatementEvent.objects.create(
            type_id='submitted',
            by=person,
            statement=self,
            desc='Statement Submitted'
        )

    def get_absolute_url(self):
        return settings.IDTRACKER_BASE_URL + urlreverse('liaison_detail',kwargs={'object_id':self.id})

    def is_outgoing(self):
        return self.to_groups.first().type_id == 'sdo'

    def latest_event(self, *args, **filter_args):
        """Get latest event of optional Python type and with filter
        arguments, e.g. d.latest_event(type="xyz") returns an LiaisonStatementEvent
        while d.latest_event(WriteupDocEvent, type="xyz") returns a
        WriteupDocEvent event."""
        model = args[0] if args else LiaisonStatementEvent
        e = model.objects.filter(statement=self).filter(**filter_args).order_by('-time', '-id')[:1]
        return e[0] if e else None
        
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
    def posted(self):
        event = self.latest_event(type='posted')
        if event:
            return event.time
        return None
    
    @property
    def submitted(self):
        event = self.latest_event(type='submitted')
        if event:
            return event.time
        return None

    @property
    def sort_date(self):
        """Returns the date to use for sorting, for posted statements this is post date,
        for pending statements this is submitted date"""
        if self.state_id == 'posted':
            return self.posted
        elif self.state_id == 'pending':
            return self.submitted

    @property
    def modified(self):
        event = self.liaisonstatementevent_set.all().order_by('-time').first()
        if event:
            return event.time
        return None

    @property
    def approved(self):
        return self.state_id in ('approved','posted')

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

    def from_groups_short_display(self):
        '''Returns comma separated list of from_group acronyms.  For use in admin
        interface'''
        groups = self.to_groups.order_by('acronym').values_list('acronym',flat=True)
        return ', '.join(groups)
    from_groups_short_display.short_description = 'From Groups'

    def set_state(self,slug):
        try:
            state = LiaisonStatementState.objects.get(slug=slug)
        except LiaisonStatementState.DoesNotExist:
            return
        self.state = state
        self.save()
        
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
