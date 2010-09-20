# Copyright The IETF Trust 2007, All Rights Reserved

from django.db import models

class RoleName(models.Model):
    """AD, Chair"""
    slug = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class DocStreamName(models.Model):
    """IETF, IAB, IRTF, Independent Submission"""
    slug = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class DocStateName(models.Model):
    """Active, Expired, RFC, Replaced, Withdrawn"""
    slug = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class DocRelationshipName(models.Model):
    """Updates, Replaces, Obsoletes, Reviews, ..."""
    slug = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class WgDocStateName(models.Model):
    """Not, Candidate, Active, Parked, LastCall, WriteUp, Submitted, Dead"""
    slug = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class IesgDocStateName(models.Model):
    """Pub Request, Ad Eval, Expert Review, Last Call Requested, In Last Call, Waiting for Writeup, Waiting for AD Go-Ahead, IESG Evaluation, Deferred, Approved, Announcement Sent, Do Not Publish, Ad is watching, Dead """
    slug = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class IanaDocStateName(models.Model):
    """ """
    slug = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class RfcDocStateName(models.Model):
    """Missref, Edit, RFC-Editor, Auth48, Auth, Published; ISR, ISR-Auth, ISR-Timeout;"""
    slug = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class DocTypeName(models.Model):
    """Draft, Agenda, Minutes, Charter, Discuss, Guideline, Email, Review, Issue, Wiki"""
    slug = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    slug = models.CharField(max_length=8) # draft, agenda, minutes, charter, discuss, guide, email, review, issue, wiki
    desc = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class DocInfoTagName(models.Model):
    """Waiting for Reference, IANA Coordination, Revised ID Needed, External Party, AD Followup, Point Raised - Writeup Needed"""
    slug = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class StdStatusName(models.Model):
    """Proposed Standard, Draft Standard, Standard, Experimental, Informational, Best Current Practice, Historic, ..."""
    slug = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class IntendedStatusName(models.Model):
    """Standards Track, Experimental, Informational, Best Current Practice, Historic, ..."""
    slug = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class MsgTypeName(models.Model):
    """
    Announcement, IesgComment, IesgDiscuss, BallotPosition, ...
    """
    slug = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class BallotPositionName(models.Model):
    """ Yes, NoObjection, Abstain, Approve, Discuss, Recuse """
    slug = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(null=True, blank=True)
    used = models.BooleanField(default=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass
