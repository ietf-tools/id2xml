from django.db import models
from django.db import connection
from sec.core.models import CustomManager, PersonOrOrgInfo, EmailAddress, PostalAddress, Area, AreaDirector

# Changes
# fixed person_or_org_info:affiliation error handling


class PhoneNumber(models.Model):
    person_or_org = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag')
    phone_type = models.CharField(max_length=3,default='W')
    phone_priority = models.IntegerField(default='1')
    phone_number = models.CharField(blank=True, max_length=255)
    phone_comment = models.CharField(blank=True, max_length=255)
    def __unicode__(self):
        return self.phone_number
    class Meta:
        db_table = 'phone_numbers'
        verbose_name_plural = "Phone Numbers"
        #unique_together = (('phone_priority', 'person_or_org'), )
    # override save function to handle 'phone_priority'
    def save(self):
        # set priority, number of existing items + 1
        self.phone_priority = PhoneNumber.objects.filter(person_or_org=self.person_or_org).count() + 1
        super(PhoneNumber, self).save()
