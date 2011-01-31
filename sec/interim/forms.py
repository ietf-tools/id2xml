from django import forms
from models import *
import os

SLIDE_TYPE_CHOICES = (
    ('AG', 'Agenda'),
    ('MN', 'Minutes'),
    ('MM', 'Media (audio / video file)'),
    ('PR', 'Presentation Slide'),
)

class MeetingForm(forms.Form):
    date = forms.DateField(help_text="(YYYY-MM-DD Format, please)")
    group_acronym_id = forms.CharField(widget=forms.HiddenInput())
    
    def clean(self):
        super(MeetingForm, self).clean()
        cleaned_data = self.cleaned_data
        # need to use get() here, if the date field isn't valid it won't exist
        date = cleaned_data.get('date','')
        group_acronym_id = cleaned_data["group_acronym_id"]
        qs = InterimMeeting.objects.using('interim').filter(meeting_date=date,group_acronym_id=group_acronym_id)
        if qs:
            raise forms.ValidationError('A meeting already exists for this date.')
        return cleaned_data
        
class SlideModelForm(forms.ModelForm):
    '''
    If we create a standard ModelForm (no excludes) we get Table doesn't exist errors
    because Django is trying to lookup the meeting record in the wrong database.
    So, need to exlude meeting and create a generic CharField to hold the value
    '''
    meeting = forms.CharField(widget=forms.HiddenInput())
    class Meta:
        model = Slides
        exclude = ('meeting')

    def __init__(self, *args, **kwargs):
        super(SlideModelForm, self).__init__(*args, **kwargs)
        self.fields['slide_type'].widget.choices = SLIDE_TYPE_CHOICES
        #self.fields['meeting'].widget=forms.HiddenInput()

    def clean_filename(self):
        prohibited_extensions = ('.exe','.py','.pyc','.php','.cgi','.com')
        file = self.cleaned_data["filename"]
        ext = os.path.splitext(file.name)[1].lower()
        if ext in prohibited_extensions:
            raise forms.ValidationError('These extensions are prohibited: %s' % ','.join(prohibited_extensions))
        return file

    def clean(self):
        super(SlideModelForm, self).clean()
        cleaned_data = self.cleaned_data
        order = self.cleaned_data["order_num"]
        meeting = self.cleaned_data["meeting"]
        if Slides.objects.using('interim').filter(meeting=meeting,order_num=order).count() > 0:
            raise forms.ValidationError('A slide with that order number already exists')
        return cleaned_data

class EditSlideForm(forms.ModelForm):
    class Meta:
        model = Slides
        fields = ('slidename','slide_type')

class EditSlideModelForm(SlideModelForm):
    class Meta:
        model = Slides
        exclude = ('meeting','filename')
