# Copyright The IETF Trust 2007, All Rights Reserved

from django.db import models
from redesign.name.models import *
from redesign.person.models import Email

class Document(models.Model):
    """Any kind of document.  Draft, RFC, Charter, IPR Statement, Liaison Statement"""
    name = models.CharField(maxlength=256, primary_key=True)           # immutable
    # Event related.  Time, comment, and agent related to latest change.
    time = models.DateTimeField(auto_now=True)
    comment = models.TextField()
    agent = models.ForeignKey(Email, null=True, related_name='changed_documents')
    # Document related
    type = models.ForeignKey(DocTypeName, null=True)
    title = models.CharField(maxlength=255)
    # State
    state = models.ForeignKey(DocStateName, null=True) # Active/Expired/RFC/Replaced/Withdrawn
    doc_stream = models.ForeignKey(DocStreamName, null=True) # IETF, IAB, IRTF, Independent Submission
    wg_state  = models.ForeignKey(WgDocStateName, null=True) # Not/Candidate/Active/Parked/LastCall/WriteUp/Submitted/Dead
    iesg_state = models.ForeignKey(IesgDocStateName, null=True) # 
    iana_state = models.ForeignKey(IanaDocStateName, null=True)
    rfc_state = models.ForeignKey(RfcDocStateName, null=True)
    # Other
    abstract = models.TextField()
    rev = models.CharField(maxlength=16)
    pages = models.IntegerField(null=True)
    intended_std_level = models.ForeignKey(StdStatusName, null=True)
    authors = models.ManyToManyField(Email, null=True)
    updates = models.ManyToManyField('Document', related_name='updated_by', null=True)
    replaces = models.ManyToManyField('Document', related_name='replaced_by', null=True)
    obsoletes = models.ManyToManyField('Document', related_name='obsoleted_by', null=True)
    reviews = models.ManyToManyField('Document', related_name='reviewed_by', null=True)
    ad = models.ForeignKey(Email, related_name='ad_documents', null=True)
    shepherd = models.ForeignKey(Email, related_name='shepherded_documents', null=True)
    def __str__(self):
        return self.name
    class Admin:
        pass
        
class DocHistory(models.Model):
    """This holds all the document specific information, except for
    it's immutable name.  Any time a field changes, a new record is
    created for the document, and the 'current' pointer of the
    Document record is updated (That pointer is strictly speaking
    superfluous -- could be skipped if there aren't any performance
    issues ...)
    This gives us a complete record of document state over time.

    This class will actually be implemented as an extension of the
    Document Class, but that requires Django 1.0
    """
    name = models.ForeignKey(Document)   # ID of the Document this relates to
    # Event related
    time = models.DateTimeField()
    comment = models.TextField()
    agent = models.ForeignKey(Email, related_name='document_changes')
    # Document related
    type = models.ForeignKey(DocTypeName)
    title = models.CharField(maxlength=255)
    # State
    doc_stream = models.ForeignKey(DocStreamName, null=True) # IETF, IAB, IRTF, Independent Submission
    doc_state = models.ForeignKey(DocStateName, null=True) # Active/Expired/RFC/Replaced/Withdrawn
    wg_state  = models.ForeignKey(WgDocStateName, null=True) # Not/Candidate/Active/Parked/LastCall/WriteUp/Submitted/Dead
    iesg_state = models.ForeignKey(IesgDocStateName, null=True) # 
    iana_state = models.ForeignKey(IanaDocStateName, null=True)
    rfc_state = models.ForeignKey(RfcDocStateName, null=True)
    # Other
    abstract = models.TextField()
    rev = models.CharField(maxlength=16)
    pages = models.IntegerField(null=True)
    intended_status = models.ForeignKey(StdStatusName, null=True)
    authors = models.ManyToManyField(Email, null=True)
    updates = models.ManyToManyField('Document', related_name='updated_by_history', null=True)
    replaces = models.ManyToManyField('Document', related_name='replaced_by_history', null=True)
    obsoletes = models.ManyToManyField('Document', related_name='obsoleted_by_history', null=True)
    ad = models.ForeignKey(Email, related_name='ads_document_history', null=True)
    shepherd = models.ForeignKey(Email, related_name='shepherded_document_history', null=True)
    class Meta:
        verbose_name_plural="Doc histories"
    class Admin:
        pass

class InfoTag(models.Model):
    """While a document can only be in one state at a given time, it
    can have multiple instances of infirmational tags associated with
    it.  It could for instance both be under some IANA handling and
    under some other action (Specialist review? RFC Ed Queue?) at the
    same time.  This table captures that information.
    """
    document = models.ForeignKey(Document)
    infotag = models.ForeignKey(DocInfoTagName)
    class Admin:
        pass

class Alias(models.Model):
    """This is used for documents that may appear under multiple names,
    and in particular for RFCs, which for continuity still keep the
    same immutable Document.name, in the tables, but will be referred
    to by RFC number, primarily, after achieving RFC status.
    """
    document = models.ForeignKey(Document)
    name = models.CharField(maxlength=256)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural="Aliases"
    class Admin:
        pass

class Message(models.Model):
    time = models.DateTimeField()
    type = models.ForeignKey(MsgTypeName)   # Announcement, IesgComment, BallotPosition, etc.
    doc  = models.ForeignKey(Document)
    frm  = models.ForeignKey(Email, related_name='from_messages')
    subj = models.CharField(maxlength=255)
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
