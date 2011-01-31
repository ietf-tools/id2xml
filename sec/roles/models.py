from django.db import models
from sec.core.models import Area, AreaDirector, AreaStatus, PersonOrOrgInfo

class Role(models.Model):
    '''This table is named 'chairs' in the database, as its original
    role was to store "who are IETF, IAB and IRTF chairs?".  It has
    since expanded to store roles, such as "IAB Exec Dir" and "IAD",
    so the model is renamed.
    '''
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    role_name = models.CharField(max_length=25, db_column='chair_name')

    # Role values
    IETF_CHAIR            = 1
    IAB_CHAIR             = 2
    NOMCOM_CHAIR          = 3
    IAB_EXCUTIVE_DIRECTOR = 4
    IRTF_CHAIR            = 5
    IAD_CHAIR             = 6

    # This __str__ makes it odd to use as a ForeignKey.
    def __unicode__(self):
        return "%s (%s)" % (self.person, self.role())
    def role(self):
        if self.role_name in ('IETF', 'IAB', 'IRTF', 'NomCom'):
            return "%s Chair" % self.role_name
        else:
            return self.role_name
    class Meta:
        db_table = 'chairs'

class ChairsHistory(models.Model):
    chair_type = models.ForeignKey(Role)
    present_chair = models.BooleanField()
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)
    def __unicode__(self):
        return str(self.person)
    # custom method for use in template
    def is_present(self):
        if self.present_chair == 1:
            return True
        else:
            return False
    class Meta:
        db_table = 'chairs_history'

# This model is from introspect not IETF legacy
class LiaisonsMembers(models.Model):
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    affiliation = models.CharField(max_length=75, blank=True)
    class Meta:
        db_table = u'liaisons_members'

class IESGHistory(models.Model):
    # in reality this field is a reference (fk) to a meeting object
    # but we are using an integer to simplify things
    # meeting = models.ForeignKey(Meeting, db_column='meeting_num')
    meeting = models.IntegerField(db_column='meeting_num')
    area = models.ForeignKey(Area, db_column='area_acronym_id')
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    def __unicode__(self):
        return "%s (%s)" % (self.person,self.area)
    class Meta:
        db_table = 'iesg_history'
