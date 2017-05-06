
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
from ietf.sidemeeting import models

class SideMeetingForm(forms.ModelForm):
    name = forms.CharField(label='Company or Meeting Name: (required)', max_length=256)
    email = forms.EmailField(label='Your Name: (required)')
    phone = forms.CharField(label='Your Phone: (required)', max_length=256)
    mtgnum = forms.CharField(label='IETF Meeting Number: (required) IETF XX (digits only please)', max_length=256)
    mtgdate = forms.DateField(label='Desired Meeting Date: (required) field with (mm/dd/yyyy)')
    altmtgdate = forms.DateField(label='Alternate Meeting Date: (optional)  field with (mm/dd/yyyy)')
    days = forms.IntegerField(label='Number of Days: (required)', max_value=14)
    mtgtype = forms.CharField(label='Meeting Type', max_length=256)
    addcontact = forms.CharField(label='Additional Contact Name: (optional)', max_length=256)
    addemail = forms.EmailField(label='Additional Contact Email: (optional)')    
    addphone = forms.CharField(label='Additional Contact Phone: (remove)', max_length=256)
    attendance = forms.IntegerField(label='Expected Attendance: (required)', max_value=100000)
    mtgstart = forms.DateTimeField(label='Meeting Start Time: (required) open field with (hh:mm)')
    mtgend = forms.DateTimeField(label='Meeting Start Time: (required) open field with (hh:mm)')
    roomconfig = forms.CharField(label='Room Configuration: (optional) Can we still include a link to the diagram that is currently in the form?    ', max_length=256)    
    speakerphone = forms.BooleanField(label="Speakerphone Requested? ($150 fee) - required with drop down defaulting to no")
    projector = forms.BooleanField(label="LCD Projector Requested? ($350 fee) - required with drop down defaulting to no")
    food = forms.BooleanField(label="Food/Beverage Requested? Coordination Fee: $200 per service - required with drop down defaulting to no")
    comments = forms.CharField(label="Comments: (Note: Please do not put links in this form)", widget=forms.Textarea)

    
    
    class Meta:
        model = models.SideMeeting
        fields = ['name']
    
