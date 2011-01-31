from django.db import models
from sec.core.models import PersonOrOrgInfo, Acronym
from sec.groups.models import WGChair
 
import os

# -----------------------------------
# Helper Functions
# -----------------------------------
def get_path(instance, filename):
    # A function to be used as the upload_to argument for a FileField
    # lookup the meeting and build path for file uploads
    meeting_date = instance.meeting.meeting_date
    path = os.path.join('interim',
                        meeting_date.strftime('%Y'),
                        meeting_date.strftime('%m'),
                        meeting_date.strftime('%d'),
                        instance.meeting.get_group_acronym(),
                        'slides',
                        filename
                       )
    #assert False, path
    return path

# -----------------------------------
# Models 
# -----------------------------------
class InterimMeeting(models.Model):
    # this would normally be a ForeignKey to Acronym but this 
    # table is in a different database.
    group_acronym_id = models.IntegerField()
    meeting_date = models.DateField()
    created = models.DateField()
    updated = models.DateField(auto_now=True)
    def get_group_acronym(self):
        try:
            acronym = Acronym.objects.get(acronym_id=self.group_acronym_id)
        except Acronym.DoesNotExist:
            return ''
        return acronym.acronym
    def get_group_name(self):
        try:
            acronym = Acronym.objects.get(acronym_id=self.group_acronym_id)
        except Acronym.DoesNotExist:
            return ''
        return acronym.name
    def __unicode__(self):
        return '%s:%s' % (self.group_acronym_id, self.meeting_date)
    class Meta:
        db_table = 'interim_meetings'
    
class LegacyWgPassword(models.Model):
    person = models.ForeignKey(PersonOrOrgInfo, db_column='person_or_org_tag', primary_key=True)
    password = models.CharField(blank=True, null=True,max_length=255)
    secrete_question_id = models.IntegerField(null=True, blank=True)
    secrete_answer = models.CharField(blank=True, null=True, max_length=255)
    is_tut_resp = models.IntegerField(null=True, blank=True)
    irtf_id = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True,null=True)
    login_name = models.CharField(blank=True, max_length=100)
    def __str__(self):
        return self.login_name
    class Meta:
        db_table = 'wg_password'
        ordering = ['login_name']

class Slides(models.Model):
    SLIDE_TYPE_CHOICES = (
        ('AG', 'Agenda'),
        ('MN', 'Minutes'),
        ('MM', 'Media (audio / video file)'),
        ('PR', 'Presentation Slide'),
    )
    meeting = models.ForeignKey('InterimMeeting')
    slide_type = models.CharField(max_length=255, choices = SLIDE_TYPE_CHOICES)
    slidename = models.CharField(max_length=255)
    filename = models.FileField(upload_to=get_path)
    order_num = models.IntegerField(null=True)
    def get_slide_type(self):
        return dict(self.SLIDE_TYPE_CHOICES)[self.slide_type]
    def __unicode__(self):
        return self.slidename
    class Meta:
        db_table = 'slides'
