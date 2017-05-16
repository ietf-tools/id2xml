
from django import forms
from django.utils.translation import ugettext_lazy as _
from ietf.sidemeeting import models


class SideMeetingForm(forms.ModelForm):
    class Meta:
        model = models.SideMeetingSession
        fields = ('name', 'meeting', 'requested_prim_start_time', 'requested_alt_start_time', 'requested_duration',  'attendance', 'resources', 'comments')
#        fields = ('name', 'meeting', 'requested_prim_start_time', 'requested_alt_start_time', 'requested_duration', 'sidemeeting_type', 'attendance', 'resources', 'comments')        
        labels = {
            'name': _("Company or Meeting Name"),
            'meeting': _("IETF Meeting Number"),
            'requested_prim_start_time': _("Desired Meeting Date: field with (mm/dd/yyyy)"),
            'requested_alt_start_time': _("Alternate Meeting Date: field with (mm/dd/yyyy)"),
            'requested_duration': _("Duration of Meeting"),            

            # 'sidemeeting_type': _("Meeting Type: If IETF meeting, select appropriate Area. If external meeting, select corporate or non profit as appropriate (Room Rental Cost for certain types: $750 for 1/2 day, $1,250 for full day)"),
            'attendance': _("Expected Attendance "),
            'resources':_("Resources"),
            'comments': _("Comments: (Note: Please do not put links in this form)"),
        }        
        

# class SideTypeNameForm(forms.ModelForm):
#     class Meta:
#         model = models.SideTypeName
#         fields = ('name',)
#         labels = {
#             'name': _("Session Type:"),
#         }        
        


