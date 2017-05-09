
elements = """
Request An Additional Meeting
Please use the form below to request use of IETF meeting space if the intended purpose of your meeting is one of the following: corporate, affiliate organization, Bar BOF or a community work group. Your request will be forwarded to the appropriate person for review. For more information, please see the IETF meeting policy.

Company or Meeting Name: (required)
Your Name: (required)
Your Email: (required)
Your Phone: (required)
IETF Meeting Number: (required) IETF XX (digits only please)
Desired Meeting Date: (required) field with (mm/dd/yyyy)
Alternate Meeting Date: (optional)  field with (mm/dd/yyyy)
Number of Days: (required)
Meeting Type: 
If IETF meeting, select appropriate Area. 
If external meeting, select corporate or non profit as appropriate (Room Rental Cost for certain types: $750 for 1/2 day, $1,250 for full day) (required with same drop down menu as it is now in ARO)
Additional Contact Name: (optional)
Additional Contact Email: (optional)
Additional Contact Phone: (remove)
Expected Attendance: (required)

Meeting Start Time: (required) open field with (hh:mm)

Meeting End Time: (required) open field with (hh:mm)

Room Configuration: (optional) Can we still include a link to the diagram that is currently in the form?

Speakerphone Requested? ($150 fee) - required with drop down defaulting to no

LCD Projector Requested? ($350 fee) - required with drop down defaulting to no

Food/Beverage Requested? Coordination Fee: $200 per service - required with drop down defaulting to no

Comments: 
(Note: Please do not put links in this form)
"""

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
        

