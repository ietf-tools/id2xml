from django.db import models
from sec.core.models import Acronym, Area, AreaDirector, AreaStatus, IESGLogin, PersonOrOrgInfo, TelechatUser
from sec.groups.models import IETFWG

class AreaWGAWP(models.Model):
    id = models.AutoField(primary_key=True, db_column='area_ID')
    #name = models.CharField(max_length=50, db_column='area_Name')
    # For WGs, this is the WG acronym; for areas, it's the area name.
    name = models.ForeignKey(Acronym, to_field='name', db_column='area_Name')
    url = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=50, blank=True)
    def __unicode__(self):
        return u'%s (%s)' % (self.name, self.description)
    class Meta:
        ordering = ['name']
        verbose_name = "Area/WG URL"
        db_table = "wg_www_pages"
