
from django import forms
from django.utils.translation import ugettext_lazy as _
from collections import OrderedDict
from ietf.sidemeeting import models

FIELD_NAMES = OrderedDict()
FIELD_NAMES['name'] = _("Company or Meeting Name")
FIELD_NAMES['meeting'] = _("IETF Meeting Number")
FIELD_NAMES['requested_prim_start_time'] =  _("Desired Meeting Date: field with (mm/dd/yyyy)")
FIELD_NAMES['requested_alt_start_time'] =  _("Alternate Meeting Date: field with (mm/dd/yyyy)")
FIELD_NAMES['requested_duration'] =  _("Duration of Meeting")
FIELD_NAMES['sidemeeting_type'] = _("Meeting Type: If IETF meeting, select appropriate Area. If external meeting, select corporate or non profit as appropriate (Room Rental Cost for certain types: $750 for 1/2 day, $1,250 for full day)")
FIELD_NAMES['group'] = _("IETF meeting area")
FIELD_NAMES['attendees'] = _("Expected Attendance ")
FIELD_NAMES['resources'] = _("Resources")
FIELD_NAMES['comments'] = _("Comments: (Note: Please do not put links in this form)")

DETAIL_NAMES = OrderedDict()
DETAIL_NAMES['name'] = _("Meeting Name")
DETAIL_NAMES['meeting'] = _("IETF Meeting Number")
DETAIL_NAMES['requested_prim_start_time'] =  _("Desired Meeting Date")
DETAIL_NAMES['requested_alt_start_time'] =  _("Alternate Meeting Date")
DETAIL_NAMES['requested_duration'] =  _("Duration of Meeting")
DETAIL_NAMES['sidemeeting_type'] = _("Meeting Type")
DETAIL_NAMES['group'] = _("IETF meeting area")
DETAIL_NAMES['attendees'] = _("Expected Attendance ")
DETAIL_NAMES['resources'] = _("Resources")
DETAIL_NAMES['comments'] = _("Comments")


class SideMeetingForm(forms.ModelForm):
    class Meta:
        model = models.SideMeetingSession
        fields = FIELD_NAMES.keys()
        labels = FIELD_NAMES
        widgets = {
            'requested_prim_start_time': forms.DateInput(attrs={'class':'datepicker'}),
            'requested_alt_start_time': forms.DateInput(attrs={'class':'datepicker'})
        }        
        

class SideMeetingApproveForm(forms.ModelForm):
    class Meta:
        model = models.SideMeetingSession
        fields = ('status',)        
        labels = {
            'status': _("Status"),
        }

class SideMeetingTypeNameForm(forms.ModelForm):
    class Meta:
        model = models.SideMeetingTypeName
        fields = ('name',)
        labels = {
            'name': _("Session Type:"),
        }        
        


