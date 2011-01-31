import re
from django import forms
from sec.proceedings.models import *
from sec.core.models import *
from sec.groups.models import *
from django.db.models import Max
from os.path import splitext
import os
# ---------------------------------------------
# Various Select Choices Used in the forms
# ---------------------------------------------


MATERIAL_TYPE_CHOICES = (
    (1, 'Presentation'),
    (2, 'Minutes'),
    (3,'Agenda')
)
FILE_FORMAT_CHOICES = (
    (1, 'html'),
    (2, 'pdf'),
    (3,'txt')
)

SEARCH_GROUP_CHOICES_SCHEDULED = list( Acronym.objects.filter(ietfwg__meeting_scheduled__exact='YES').values_list('acronym_id','acronym').order_by('acronym'))
GROUP_CHOICES_SCHEDULED = SEARCH_GROUP_CHOICES_SCHEDULED[:] 
GROUP_CHOICES_SCHEDULED.insert(0,('0','------------------'))
GROUP_CHOICES_SCHEDULED.insert(0,('-1','Administrative Plenary'))
GROUP_CHOICES_SCHEDULED.insert(0,('-2','Technical Plenary'))


SEARCH_GROUP_CHOICES_NOT_SCHEDULED = list( Acronym.objects.filter(ietfwg__meeting_scheduled_old__exact='YES').values_list('acronym_id','acronym').order_by('acronym'))
GROUP_CHOICES_NOT_SCHEDULED = SEARCH_GROUP_CHOICES_NOT_SCHEDULED[:] 
GROUP_CHOICES_NOT_SCHEDULED.insert(0,('0','------------------'))
GROUP_CHOICES_NOT_SCHEDULED.insert(0,('-1','Administrative Plenary'))
GROUP_CHOICES_NOT_SCHEDULED.insert(0,('-2','Technical Plenary'))



IRTF_CHOICES = list(IRTF.objects.all().values_list('irtf_id','acronym').order_by('acronym'))



#-----------------------------------------------------------
#Custom functions
#----------------------------------------------------------
class DocumentField(forms.FileField):
    """A validating document upload field"""
    valid_file_extensions = ('txt','pdf','ppt','xml','pptx')
   
    def __init__(self, valid_file_extensions=None, *args, **kwargs):
        super(DocumentField, self).__init__(*args, **kwargs)
        if valid_file_extensions:
            self.valid_file_extensions = valid_file_extensions

    def clean(self, data, initial=None):
        file = super(DocumentField, self).clean(data,initial)
        if file:
            # ensure file name complies with standard format
            m = re.search(r'.*-\d{2}\.(txt|pdf|ps|xml|pptx)', file.name)
            if file and not m:
               raise forms.ValidationError('File name must be in the form base-NN.[txt|pdf|ps|xml|pptx]')
        return file

#-----------------------------------------------------------
#Forms
#----------------------------------------------------------

class MeetingForm(forms.ModelForm):
    class Meta:
       model = Meeting
       exclude=('meeting_num','time_zone','ack','agenda_html','agenda_text','future_meeting','overview1','overview2')

class ProceedingForm(forms.ModelForm):
   class Meta:
      model = Proceeding
      exclude = ('frozen')
          
class AddProceedingForm(forms.Form):
    """ 
    We don't need all the fields from Proceeding and Meeting Model in the 
    add new Meeting Form. So this particular form is creates using the 
    required fields.
    """	
    # Fields belonging to Meeting Model
    meeting_num = forms.IntegerField(required=True)
    start_date = forms.DateField()
    end_date = forms.DateField()
    city = forms.CharField(max_length=255,required=False)
    state = forms.CharField(max_length=255,required=False)
    country = forms.CharField(max_length=255,required=False)
    
    # Fields belonging to Proceeding Model
    dir_name = forms.CharField(label='Directory Name',max_length=25,required=True)
    sub_begin_date = forms.DateField(label='Submission begin date')
    sub_cut_off_date = forms.DateField(label='Submission cut off date')
    c_sub_cut_off_date = forms.DateField(label='Correction submission cut off date' )
    pr_from_date = forms.DateField( label='Progress from')
    pr_to_date = forms.DateField( label='Progress to')



class UploadForm(forms.Form):
    group_name = forms.CharField(label='Group Name',required=True) 
    material_type = forms.IntegerField(widget=forms.Select(choices=MATERIAL_TYPE_CHOICES),required=True)
    slide_name = forms.CharField(label='Name of Presentation',max_length=255,required=False,help_text="For presentations only")
    file_format = forms.IntegerField(widget=forms.Select(choices=FILE_FORMAT_CHOICES),required=True)
    file = forms.FileField(label='Select File')


class GroupSelectionForm(UploadForm):

       def __init__(self, *args, **kwargs):
          menu = kwargs.pop('menu',None) 
          meeting_scheduled_field =  kwargs.pop('meeting_scheduled_field',None) 
          meeting_num = kwargs.pop('meeting_num',None)
          super(GroupSelectionForm, self).__init__(*args, **kwargs)
        
	  if menu == 'group':
                if meeting_scheduled_field == 'meeting_scheduled':        
		   self.fields['group_name'].widget=forms.Select(choices=GROUP_CHOICES_SCHEDULED)
                elif  meeting_scheduled_field == 'meeting_scheduled_old':        
		   self.fields['group_name'].widget=forms.Select(choices=GROUP_CHOICES_NOT_SCHEDULED)
          elif menu == 'training':
                   ts = []
                   q = WgMeetingSession.objects.filter(meeting=meeting_num,group_acronym_id__lt=-2)
                   for item in q:
                       ts_choices = Acronym.objects.filter(acronym_id=item.group_acronym_id).values_list('acronym_id','name')
                       for e in ts_choices:
                	       ts.append(e)                       
                   self.fields['group_name'].widget=forms.Select(choices=ts) 
          elif menu == 'irtf':
                   self.fields['group_name'].widget=forms.Select(choices=IRTF_CHOICES) 
          elif menu == 'interim':
                if meeting_scheduled_field == 'meeting_scheduled':        
		   self.fields['group_name'].widget=forms.Select(choices=SEARCH_GROUP_CHOICES_SCHEDULED)
                elif  meeting_scheduled_field == 'meeting_scheduled_old':        
		   self.fields['group_name'].widget=forms.Select(choices=SEARCH_GROUP_CHOICES_NOT_SCHEDULED)

       def clean(self):
          super(GroupSelectionForm, self).clean()
          cleaned_data = self.cleaned_data
          group_acronym_id = cleaned_data.get('group_name')
          slide_type_id = cleaned_data.get('file_format')
          material_type = cleaned_data.get('material_type')
          slide_name = cleaned_data.get('slide_name')
          file_format = cleaned_data.get('file_format')
          file = cleaned_data.get('file')
          file_ext = splitext(file.name)

          if material_type == 1 and not slide_name:
             raise forms.ValidationError('PRESENTATION NAME CAN NOT BE BLANK')
         
          if material_type == 1:
             if slide_type_id == 1 and not file_ext[1] == '.zip': 
                raise forms.ValidationError('MATERIAL TYPE INVALID')
          elif ((material_type == 2) or (material_type == 3)):
             if slide_type_id == 1 and not file_ext[1] == '.html':
                raise forms.ValidationError('MATERIAL TYPE INVALID')

          if slide_type_id == 2 and not file_ext[1] == '.pdf': 
             raise forms.ValidationError('MATERIAL TYPE INVALID')

          if slide_type_id == 3 and not file_ext[1] == '.txt': 
             raise forms.ValidationError('MATERIAL TYPE INVALID')
          return cleaned_data


class UploadPresentationForm(forms.Form):
      slide_name = forms.CharField(label='Name of Presentation',max_length=255,required=False)
      file = forms.FileField(label='Select File')


