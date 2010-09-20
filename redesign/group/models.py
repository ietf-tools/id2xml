# Copyright The IETF Trust 2007, All Rights Reserved

from django.db import models
from redesign.name.models import RoleName
from redesign.person.models import Email

class GroupState(models.Model):
    # States: BOF, Proposed, Active, Dormant, Concluded
    name = models.CharField(max_length=32)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class GroupType(models.Model):
    # Types: IETF, Area, WG, RG, Team, etc.
    name = models.CharField(max_length=32)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

class Group(models.Model):
    name = models.CharField(max_length=64)
    acronym = models.CharField(max_length=16)
    status = models.ForeignKey(GroupState, null=True)
    type = models.ForeignKey(GroupType, null=True)
    charter = models.ForeignKey('doc.Document', related_name='chartered_group', null=True)
    parent = models.ForeignKey('Group', null=True)
    chairs = models.ManyToManyField(Email, related_name='chaired_groups')
    list_email = models.CharField(max_length=64)
    list_pages = models.CharField(max_length=64)
    comments = models.TextField(blank=True)
    def __unicode__(self):
        return self.name
    class Admin:
        pass

# This will actually be extended from Groups, but that requires Django 1.0
# This will record the new state and the date it occurred for any changes
# to a group.  The group acronym must be unique and is the invariant used
# to select group history from this table.
class GroupHistory(models.Model):
    group = models.ForeignKey('Group', related_name='group_history')
    # Event related
    time = models.DateTimeField()
    comment = models.TextField()
    who = models.ForeignKey(Email, related_name='group_changes')
    # inherited from Group:
    name = models.CharField(max_length=64)
    acronym = models.CharField(max_length=16)
    status = models.ForeignKey(GroupState)
    type = models.ForeignKey(GroupType)
    charter = models.ForeignKey('doc.Document', related_name='chartered_group_history')
    parent = models.ForeignKey('Group')
    chairs = models.ManyToManyField(Email, related_name='chaired_groups_history')
    list_email = models.CharField(max_length=64)
    list_pages = models.CharField(max_length=64)
    comments = models.TextField(blank=True)
    def __unicode__(self):
        return self.group.name
    class Meta:
        verbose_name_plural="Doc histories"
    class Admin:
        pass

class Role(models.Model):
    name = models.ForeignKey(RoleName)
    group = models.ForeignKey(Group)
    email = models.ForeignKey(Email)
    auth = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name
    class Admin:
        pass
    