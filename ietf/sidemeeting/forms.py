import re
from django import forms
from django.utils.translation import ugettext_lazy as _
from collections import OrderedDict
from ietf.sidemeeting import models

FIELD_NAMES = OrderedDict()
FIELD_NAMES['name'] = _("Company or Meeting Name")
FIELD_NAMES['meeting'] = _("IETF Meeting Number")
FIELD_NAMES['requested_prim_start_date'] =  _("Desired Meeting Date")
FIELD_NAMES['requested_alt_start_date'] =  _("Alternate Meeting Date")
FIELD_NAMES['requested_start_time'] =  _("Meeting Start Time")
FIELD_NAMES['requested_duration'] =  _("Duration of Meeting")
FIELD_NAMES['sidemeeting_type'] = _("Meeting Type: If IETF meeting, select appropriate Area. If external meeting, select corporate or non profit as appropriate (Room Rental Cost for certain types: $750 for 1/2 day, $1,250 for full day)")
FIELD_NAMES['group'] = _("IETF meeting area")
FIELD_NAMES['attendees'] = _("Expected Attendance ")
FIELD_NAMES['resources'] = _("Resources")
FIELD_NAMES['comments'] = _("Comments: (Note: Please do not put links in this form)")

DETAIL_NAMES = OrderedDict()
DETAIL_NAMES['name'] = _("Meeting Name")
DETAIL_NAMES['meeting'] = _("IETF Meeting Number")
DETAIL_NAMES['requested_prim_start_date'] =  _("Desired Meeting Date")
DETAIL_NAMES['requested_alt_start_date'] =  _("Alternate Meeting Date")
DETAIL_NAMES['requested_start_time'] =  _("Meeting Start Time")
DETAIL_NAMES['requested_duration'] =  _("Duration of Meeting")
DETAIL_NAMES['sidemeeting_type'] = _("Meeting Type")
DETAIL_NAMES['group'] = _("IETF meeting area")
DETAIL_NAMES['attendees'] = _("Expected Attendance ")
DETAIL_NAMES['resources'] = _("Resources")
DETAIL_NAMES['comments'] = _("Comments")


class SideMeetingForm(forms.ModelForm):

    # the constructor is being overwritten to provide a way
    # to NOT require the group field.   This field in the
    # parent class "Session" requires the field but the subclass
    # does not and it cannot be overridden without a django error
    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(SideMeetingForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        self.fields['group'].required = False
        self.fields['resources'].required = False

    def clean_name(self):
        '''Date field validator.  We can't use required on the input because
        it is a datepicker widget'''
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('Required field')
        return name
        
    def clean_attendees(self):
        '''clean '''
        name = "attendees"
        attendees = self.cleaned_data.get(name)
        if not name:
            raise forms.ValidationError('Required field')
        count = None
        try:
            count = int(attendees)
        except:
            raise forms.ValidationError('Invalid attendance' )
        if (count < 1) or (count > 1000000):
            raise forms.ValidationError('Invalid number of %s' % name  )
        
        return attendees
        
    def clean_requested_start_time(self):
        '''Date field validator.  We can't use required on the input because
        it is a datepicker widget'''
        name = 'requested_start_time'
        
        requested_start_time = re.sub('\s+','',self.cleaned_data.get(name))
        if not name:
            raise forms.ValidationError('%s is required' % name )
        pieces = requested_start_time.split(":")
        hour = None
        minutes = None
        
        try:
            hour = int(pieces[0])
        except:
           raise forms.ValidationError('Invalid start time')            
        if hour < 0 or hour > 24:
           raise forms.ValidationError('Invalid start time')
       
        if len(pieces) > 1:
            try:
               minutes = int(pieces[1])
            except:
               raise forms.ValidationError('Invalid start time')
            if minutes < 0 or minutes > 59:
               raise forms.ValidationError('Invalid start time')                                 
        if not minutes:
            minutes = 0
        requested_start_time = "%02d:%02d" % (hour, minutes)
        return requested_start_time
        
        
    class Meta:
        model = models.SideMeetingSession
        fields = FIELD_NAMES.keys()
        labels = FIELD_NAMES
        widgets = {
            'requested_prim_start_date': forms.DateInput(attrs={'class':'datepicker','placeholder':'mm/dd/yyyy'}),
            'requested_alt_start_date': forms.DateInput(attrs={'class':'datepicker','placeholder':'mm/dd/yyyy'}),
            'requested_start_time': forms.TextInput(attrs={'placeholder': 'HH:MM'}),
        }        

class SideMeetingApproveForm(forms.ModelForm):
    class Meta:
        model = models.SideMeetingSession
        fields = ('status',)        
        labels = {
            'status': _("Status"),
        }


