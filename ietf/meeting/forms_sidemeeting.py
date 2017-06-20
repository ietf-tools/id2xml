# -*- coding: utf-8 -*-
"""
forms for the sidemeeting models
"""
import re
from collections import OrderedDict

from django import forms
from django.utils.translation import ugettext_lazy as _

from ietf.meeting.models import SideMeetingSession

# for more info on ugettext_lazy translation see:
#   https://stackoverflow.com/questions/4160770/when-should-i-use-ugettext-lazy#4164683

# FIELD NAMES is a DRY way of assigning field names to presentation names
FIELD_NAMES = OrderedDict()
FIELD_NAMES['name'] = _("Company or Meeting Name")
FIELD_NAMES['meeting'] = _("IETF Meeting Number")
FIELD_NAMES['requested_prim_start_date'] = _("Desired Meeting Date")
FIELD_NAMES['requested_alt_start_date'] = _("Alternate Meeting Date")
FIELD_NAMES['requested_start_time'] = _("Meeting Start Time")
FIELD_NAMES['requested_duration'] = _("Duration of Meeting")
FIELD_NAMES['sidemeeting_type'] = _(
    "Meeting Type: If IETF meeting, select appropriate Area. If external meeting, select corporate or non profit as appropriate (Room Rental Cost for certain types: $750 for 1/2 day, $1,250 for full day)"
)
FIELD_NAMES['group'] = _("IETF meeting area")
FIELD_NAMES['attendees'] = _("Expected Attendance ")
FIELD_NAMES['resources'] = _("Resources")
FIELD_NAMES['comments'] = _(
    "Comments: (Note: Please do not put links in this form)")

# DETAIL_NAMES is used for the detail view.
DETAIL_NAMES = OrderedDict()
DETAIL_NAMES['name'] = _("Meeting Name")
DETAIL_NAMES['meeting'] = _("IETF Meeting Number")
DETAIL_NAMES['requested_prim_start_date'] = _("Desired Meeting Date")
DETAIL_NAMES['requested_alt_start_date'] = _("Alternate Meeting Date")
DETAIL_NAMES['requested_start_time'] = _("Meeting Start Time")
DETAIL_NAMES['requested_duration'] = _("Duration of Meeting")
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

    ##############
    # Validators #
    ##############
    def clean_name(self):
        '''Make sure the name of this sidemeeting exists'''
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('Required field')
        return name

    def clean_attendees(self):
        '''clean attendees'''
        name = "attendees"
        # attendees exists
        attendees = self.cleaned_data.get(name)
        if not name:
            raise forms.ValidationError('Required field')
        count = None
        # make sure its an integer
        try:
            count = int(attendees)
        except:
            raise forms.ValidationError('Invalid attendance')
        # attendees is a reasonable number
        if (count < 1) or (count > 1000000):
            raise forms.ValidationError('Invalid number of %s' % name)

        return attendees

    def clean_requested_start_time(self):
        '''clean requested_start_time'''
        name = 'requested_start_time'

        requested_start_time = re.sub('\s+', '', self.cleaned_data.get(name))
        # requested_start_time exists
        if not requested_start_time:
            raise forms.ValidationError('%s is required' % name)

        pieces = map(unicode.strip, requested_start_time.split(":"))
        hour = None
        minutes = None
        # hour portion is an integer
        try:
            hour = int(pieces[0])
        except:
            raise forms.ValidationError('Invalid start time')

        # hour is a valid number
        if hour < 0 or hour > 24:
            raise forms.ValidationError('Invalid start time')

        if len(pieces) > 1:
            # minutes is an integer
            try:
                minutes = int(pieces[1])
            except:
                raise forms.ValidationError('Invalid start time')
            # minutes is a valid integer
            if minutes < 0 or minutes > 59:
                raise forms.ValidationError('Invalid start time')

        # format the string to be stored in the db
        if not minutes:
            minutes = 0
        requested_start_time = "%02d:%02d" % (hour, minutes)
        return requested_start_time

    class Meta:
        # standard modelform structure
        model = SideMeetingSession
        fields = FIELD_NAMES.keys()
        labels = FIELD_NAMES
        # format the appearance of these fields in the form
        widgets = {
            'requested_prim_start_date':
            forms.DateInput(
                attrs={'class': 'datepicker',
                       'placeholder': 'mm/dd/yyyy'}),
            'requested_alt_start_date':
            forms.DateInput(
                attrs={'class': 'datepicker',
                       'placeholder': 'mm/dd/yyyy'}),
            'requested_start_time':
            forms.TextInput(attrs={'placeholder': 'HH:MM'}),
        }


class SideMeetingApproveForm(forms.ModelForm):
    class Meta:
        # standard modelform structure
        model = SideMeetingSession
        fields = ('status', )
        labels = {
            'status': _("Status"),
        }
