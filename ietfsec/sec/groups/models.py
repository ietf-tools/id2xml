from django.db import models
from django.conf import settings
#from sec.core.models import Acronym, PersonOrOrgInfo, IETFWG
from sec.core.models import *

import os

# area_acronym_id is used as a foreign key to both areas or acronym tables
# (see selectareaallshort.cfm and selectsecondaryareas.cfm)
# group_acronym_id is a foreign key to groups_ietf.group_acronym_id (see selectgroupcurrentprimaryarea.cfm)

class WGAWP(models.Model):
    id = models.AutoField(primary_key=True, db_column='area_ID')
    #name = models.CharField(max_length=50, db_column='area_Name')
    # For WGs, this is the WG acronym; for areas, it's the area name.
    name = models.ForeignKey(Acronym, to_field='acronym', db_column='area_Name')
    url = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=50, blank=True)
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.description)
    class Meta:
        ordering = ['name']
        verbose_name = "Area/WG URL"
        db_table = "wg_www_pages"
        # this is required to prevent tests from trying to create the table twice
        managed = False

