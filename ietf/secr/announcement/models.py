from django.db import models

from ietf.name.models import RoleName
from ietf.group.models import Group

class AnnouncementFrom(models.Model):
    name = models.ForeignKey(RoleName)
    group = models.ForeignKey(Group)
    address = models.EmailField()

    def __unicode__(self):
        return self.address