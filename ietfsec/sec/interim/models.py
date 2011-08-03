from django.conf import settings
from django.db import models
from sec.core.models import PersonOrOrgInfo, Acronym, WGChair, WGSecretary
from urlparse import urljoin
import os

# -----------------------------------
# Helper Functions
# -----------------------------------
def get_path(instance, filename):
    # A function to be used as the upload_to argument for a FileField
    # lookup the meeting and build path for file uploads
    meeting_date = instance.meeting.meeting_date
    path = os.path.join('proceedings',
                        'interim',
                        meeting_date.strftime('%Y'),
                        meeting_date.strftime('%m'),
                        meeting_date.strftime('%d'),
                        instance.meeting.get_group_acronym(),
                        'slides',
                        filename
                       )
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
    def _get_meeting_num(self):
        return self.id
    meeting_num = property(_get_meeting_num)
    def get_group_acronym(self):
        try:
            acronym = Acronym.objects.get(acronym_id=self.group_acronym_id)
        except Acronym.DoesNotExist:
            return ''
        return acronym.acronym
    group_acronym = property(get_group_acronym)
    def get_group_name(self):
        try:
            acronym = Acronym.objects.get(acronym_id=self.group_acronym_id)
        except Acronym.DoesNotExist:
            return ''
        return acronym.name
    def get_minutes(self):
        try:
            minutes = InterimFile.objects.get(meeting=self,file_type_id=InterimFile.MINUTES_FILE_TYPE)
        except InterimFile.DoesNotExist:
            return None
        return minutes
    def get_agenda(self):
        try:
            agenda = InterimFile.objects.get(meeting=self,file_type_id=InterimFile.AGENDA_FILE_TYPE)
        except InterimFile.DoesNotExist:
            return None
        return agenda
    def slides(self):
        return InterimFile.objects.filter(meeting=self,file_type_id=InterimFile.SLIDE_FILE_TYPE).order_by('order_num')
    def max_slide_order_num(self):
        max = InterimFile.objects.filter(meeting=self.id).aggregate(models.Max('order_num'))['order_num__max']
        if max:
            return max
        else:
            return 0
    def proceedings_path(self):
        path = os.path.join(settings.MEDIA_ROOT,
                            'proceedings',
                            'interim',
                            self.meeting_date.strftime('%Y'),
                            self.meeting_date.strftime('%m'),
                            self.meeting_date.strftime('%d'),
                            self.get_group_acronym(),
                            'proceedings.html')
        return path
    def get_proceedings_url(self):
        url = "%s/proceedings/interim/%s/%s/%s/%s/proceedings.html" % (
            settings.MEDIA_URL,
            self.meeting_date.strftime('%Y'),
            self.meeting_date.strftime('%m'),
            self.meeting_date.strftime('%d'),
            self.get_group_acronym())
        return url
    proceedings_url = property(get_proceedings_url)
    def get_upload_root(self):
        path = os.path.join(settings.MEDIA_ROOT,
                            'proceedings/interim',
                            self.meeting_date.strftime('%Y'),
                            self.meeting_date.strftime('%m'),
                            self.meeting_date.strftime('%d'),
                            self.get_group_acronym())
        return path
    def __unicode__(self):
        return '%s:%s' % (self.group_acronym, self.meeting_date)
    class Meta:
        db_table = 'interim_meetings'
    
class InterimFile(models.Model):
    AGENDA_FILE_TYPE = 1
    MINUTES_FILE_TYPE = 2
    SLIDE_FILE_TYPE = 3
    FILE_TYPE_CHOICES = (
        (1, 'Agenda'),
        (2, 'Minutes'),
        (3, 'Presentation Slide'),
        #(4, 'Media (audio / video file)'),
    )
    meeting = models.ForeignKey('InterimMeeting', db_column='meeting_id')
    file_type_id = models.IntegerField(choices = FILE_TYPE_CHOICES)
    title = models.CharField(max_length=255,blank=True)
    file = models.FileField(upload_to=get_path)
    order_num = models.IntegerField(null=True)
    # not used in thie app but retained to match ietf:slides table
    # if these tools are ever merged
    slide_num = models.IntegerField(null=True, default=0)
    def get_file_type(self):
        return dict(self.FILE_TYPE_CHOICES)[self.file_type_id]
    def get_short_filename(self):
        return os.path.basename(self.file.name)
    def get_url(self):
        return "%s/%s" % (settings.MEDIA_URL,self.file)
    def __unicode__(self):
        return self.file.name
    class Meta:
        db_table = 'interim_files'

# From datatracker --------------------------
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
