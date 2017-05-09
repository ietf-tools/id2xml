
from django import forms
from django.utils.translation import ugettext_lazy as _
from ietf.sidemeeting import models



class SideMeetingForm(forms.ModelForm):
    class Meta:
        model = models.SideMeeting
        fields = ('mtgname', 'name', 'email', 'phone', 'mtg', 'mtgdate', 'altmtgdate', 'days', 'mtgtype', 'addcontact', 'addemail', 'attendance', 'mtgstart', 'mtgend', 'roomconfig', 'speakerphone', 'projector', 'food', 'comments')
        labels = {
            'mtgname': _("Company or Meeting Name:"),
            'name': _("Your Name:"),            
            'email': _("Your Email:"),
            'phone': _("Your Phone:"),
            'mtg': _("IETF Meeting Number: IETF XX (digits only please)"),
            'mtgdate': _("Desired Meeting Date: field with (mm/dd/yyyy)"),
            'altmtgdate': _("Alternate Meeting Date: field with (mm/dd/yyyy)"),
            'days': _("Number of Days:"),
            'mtgtype': _("Meeting Type: If IETF meeting, select appropriate Area. If external meeting, select corporate or non profit as appropriate (Room Rental Cost for certain types: $750 for 1/2 day, $1,250 for full day)"),
            'addcontact': _("Additional Contact Name: "),
            'addemail': _("Additional Contact Email: "),
            'attendance': _("Expected Attendance: "),
            'mtgstart': _("Meeting Start Time:"),
            'mtgend': _("Meeting Start Time:"),
            'roomconfig': _("Room Configuration:"),
            'speakerphone': _("Speakerphone Requested? ($150 fee)"),
            'projector': _("LCD Projector Requested? ($350 fee)"),
            'food': _("Food/Beverage Requested? Coordination Fee: $200 per service"),
            'comments': _("Comments: (Note: Please do not put links in this form)"),
        }        
        

