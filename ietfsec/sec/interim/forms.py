from django import forms
from models import *
import os

class MeetingForm(forms.Form):
    date = forms.DateField(help_text="(YYYY-MM-DD Format, please)")
    group_acronym_id = forms.CharField(widget=forms.HiddenInput())
    
    def clean(self):
        super(MeetingForm, self).clean()
        cleaned_data = self.cleaned_data
        # need to use get() here, if the date field isn't valid it won't exist
        date = cleaned_data.get('date','')
        group_acronym_id = cleaned_data["group_acronym_id"]
        qs = InterimMeeting.objects.filter(meeting_date=date,group_acronym_id=group_acronym_id)
        if qs:
            raise forms.ValidationError('A meeting already exists for this date.')
        return cleaned_data
        
class SlideModelForm(forms.ModelForm):
    class Meta:
        model = InterimFile
        exclude = ('slide_num')

    def __init__(self, *args, **kwargs):
        super(SlideModelForm, self).__init__(*args, **kwargs)
        self.fields['file_type_id'].widget.choices = InterimFile.FILE_TYPE_CHOICES
        self.fields['file_type_id'].label = 'Material Type'
        self.fields['title'].help_text = 'For presentations only'
        self.fields['title'].label = 'Name of Presentation'
        self.fields['order_num'].widget = forms.HiddenInput()
        self.fields['meeting'].widget = forms.HiddenInput()

    def clean_file(self):
        prohibited_extensions = ('.exe','.py','.pyc','.php','.cgi','.com')
        valid_extensions = ('.htm','.html','.pdf','.txt','.ppt','.doc','.pptx','.wav','avi','.mp3')
        file = self.cleaned_data['file']
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in valid_extensions:
            raise forms.ValidationError('ERROR: only these types allowed: %s' % ','.join(valid_extensions))
        return file

    def clean(self):
        super(SlideModelForm, self).clean()
        # if no file is supplied need to return error before attempting checks below
        if self.errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        order = self.cleaned_data['order_num']
        meeting = self.cleaned_data['meeting']
        file = self.cleaned_data['file']
        type = self.cleaned_data['file_type_id']
        title = self.cleaned_data['title']
        if type == InterimFile.SLIDE_FILE_TYPE and not title:
            raise forms.ValidationError('Name of Presentation is required')
        if InterimFile.objects.filter(meeting=meeting,file__endswith='/' + file.name):
            raise forms.ValidationError('Uploaded material with filename: %s already exists' % file.name)
        if type in (InterimFile.AGENDA_FILE_TYPE, InterimFile.MINUTES_FILE_TYPE):
            if os.path.splitext(file.name)[1].lower() != '.txt':
                raise forms.ValidationError('Minutes and Agenda files must be text files (.txt)')
             
        return cleaned_data
        
    def save(self, *args, **kwargs):
        # for minutes and agenda types order_num = Null
        #slide = super(SlideModelForm, self).save(*args, commit=False, **kwargs)
        slide = super(SlideModelForm, self).save(commit=False)
        if slide.file_type_id in (InterimFile.AGENDA_FILE_TYPE, InterimFile.MINUTES_FILE_TYPE):
            slide.order_num = None
        slide.save()
        return slide
    

class EditSlideForm(forms.ModelForm):
    class Meta:
        model = InterimFile
        fields = ('title',)

