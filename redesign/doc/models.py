# Copyright The IETF Trust 2007, All Rights Reserved

from django.db import models
from redesign.group.models import *
from redesign.name.models import *
from redesign.person.models import Email
from redesign.util import admin_link

class RelatedDoc(models.Model):
    relationship = models.ForeignKey(DocRelationshipName)
    doc_alias = models.ForeignKey('DocAlias')
    def __unicode__(self):
        return "%s %s" % (self.relationship.name, self.doc_alias.name)
    source = admin_link("related_document_set")
    target = admin_link("doc_alias__document")

class DocumentInfo(models.Model):
    """Any kind of document.  Draft, RFC, Charter, IPR Statement, Liaison Statement"""
    # Event related.  Time, comment, and agent, related to latest change.
    time = models.DateTimeField(null=True)
    comment = models.TextField()
    agent = models.ForeignKey(Email, null=True, related_name='changed_%(class)s_set')
    # Document related
    type = models.ForeignKey(DocTypeName, null=True) # Draft, Agenda, Minutes, Charter, Discuss, Guideline, Email, Review, Issue, Wiki, External ...
    title = models.CharField(max_length=255)
    # State
    state = models.ForeignKey(DocStateName, null=True) # Active/Expired/RFC/Replaced/Withdrawn
    tags = models.ManyToManyField(DocInfoTagName, null=True) # Revised ID Needed, ExternalParty, AD Followup, ...
    stream = models.ForeignKey(DocStreamName, null=True) # IETF, IAB, IRTF, Independent Submission
    group = models.ForeignKey(Group, null=True) # WG, RG, IAB, IESG, Edu, Tools
    wg_state  = models.ForeignKey(WgDocStateName, null=True) # Not/Candidate/Active/Parked/LastCall/WriteUp/Submitted/Dead
    iesg_state = models.ForeignKey(IesgDocStateName, null=True) # 
    iana_state = models.ForeignKey(IanaDocStateName, null=True)
    rfc_state = models.ForeignKey(RfcDocStateName, null=True)
    # Other
    abstract = models.TextField()
    rev = models.CharField(max_length=16)
    pages = models.IntegerField(null=True)
    intended_std_level = models.ForeignKey(IntendedStatusName, null=True)
    std_level = models.ForeignKey(StdStatusName, null=True)
    authors = models.ManyToManyField(Email, null=True)
    related = models.ManyToManyField(RelatedDoc, related_name='related_%(class)s_set')
    ad = models.ForeignKey(Email, related_name='ad_%(class)s_set', null=True)
    shepherd = models.ForeignKey(Email, related_name='shepherd_%(class)s_set', null=True)
    notify = models.CharField(max_length=255)
    external_url = models.URLField(null=True, blank=True) # Should be set for documents with type 'External'.
    class Meta:
        abstract = True
    def author_list(self):
        return ", ".join([ email.address for email in self.authors.all()])

class Document(DocumentInfo):
    name = models.CharField(max_length=255, primary_key=True)           # immutable
    def __unicode__(self):
        return self.name
    def values(self):
        try:
            fields = dict([(field.name, getattr(self, field.name))
                            for field in self._meta.fields
                                if field is not self._meta.pk])
        except:
            for field in self._meta.fields:
                print "* %24s"%field.name,
                print getattr(self, field.name)
            raise
        many2many = dict([(field.name, getattr(self, field.name).all())
                            for field in self._meta.many_to_many ])
        return fields, many2many
        
    def save(self, force_insert=False, force_update=False):
        fields, many2many = self.values()
        fields["doc"] = self
        try:
            snap = DocHistory.objects.get(**dict([(k,v) for k,v in fields.items() if not k == 'time']))
            if snap.time > fields["time"]:
                snap.time = fields["time"]
                snap.save()
        except DocHistory.DoesNotExist:
            snap = DocHistory(**fields)
            snap.save()
            for m in many2many:
                #print "m2m:", m, many2many[m]
                rel = getattr(snap, m)
                for item in many2many[m]:
                    rel.add(item)
        except DocHistory.MultipleObjectsReturned:
            list = DocHistory.objects.filter(**dict([(k,v) for k,v in fields.items() if not k == 'time']))
            list.delete()
            snap = DocHistory(**fields)
            snap.save()
            print "Deleted list:", snap
        super(Document, self).save(force_insert, force_update)

class DocHistory(DocumentInfo):
    doc = models.ForeignKey(Document)   # ID of the Document this relates to
    def __unicode__(self):
        return unicode(self.doc.name)

class DocAlias(models.Model):
    """This is used for documents that may appear under multiple names,
    and in particular for RFCs, which for continuity still keep the
    same immutable Document.name, in the tables, but will be referred
    to by RFC number, primarily, after achieving RFC status.
    """
    document = models.ForeignKey(Document)
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return "%s-->%s" % (self.name, self.document.name)
    document_link = admin_link("document")
    class Meta:
        verbose_name_plural="Aliases"
    class Admin:
        pass

class Message(models.Model):
    time = models.DateTimeField()
    type = models.ForeignKey(MsgTypeName)   # Announcement, IesgComment, BallotPosition, etc.
    doc  = models.ForeignKey(Document)
    frm  = models.ForeignKey(Email, related_name='from_messages')
    subj = models.CharField(max_length=255)
    pos  = models.ForeignKey(BallotPositionName)
    text = models.TextField()
    class Admin:
        pass

class SendQueue(models.Model):
    time = models.DateTimeField()       # Scheduled at this time
    agent  = models.ForeignKey(Email)     # Scheduled by this person
    comment = models.TextField()
    # 
    msg  = models.ForeignKey(Message)
    to   = models.ForeignKey(Email, related_name='to_messages')
    cc   = models.ManyToManyField(Email, related_name='cc_messages')
    send = models.DateTimeField()       # Send message at this time
    class Admin:
        pass

class Ballot(models.Model):             # A collection of ballot positions
    """A collection of ballot positions, and the actions taken during the
    lifetime of the ballot.

    The actual ballot positions are found by searching Messages for
    BallotPositions for this document between the dates indicated by
    self.initiated.time and (self.closed.time or now)
    """
    initiated = models.ForeignKey(Message,                        related_name="initiated_ballots")
    deferred  = models.ForeignKey(Message, null=True, blank=True, related_name="deferred_ballots")
    last_call = models.ForeignKey(Message, null=True, blank=True, related_name="lastcalled_ballots")
    closed    = models.ForeignKey(Message, null=True, blank=True, related_name="closed_ballots")
    announced = models.ForeignKey(Message, null=True, blank=True, related_name="announced_ballots")
    class Admin:
        pass
