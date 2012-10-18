# Copyright The IETF Trust 2007, All Rights Reserved

import re
from django import newforms as forms
from ietf.idtracker.models import Acronym, IETFWG
from ietf.proceedings.models import MeetingHours

class MeetingSession(forms.Form):
    session_lengths = [	(hours.hour_id, hours.hour_desc) for hours in MeetingHours.objects.all().order_by('hour_id') ]

    session_id = forms.CharField(widget=forms.HiddenInput(), required=True)
    group_acronym_id = forms.CharField(widget=forms.HiddenInput(), required=True)
    num_session = forms.ChoiceField(required=True, choices=(
        ('', '--Please select--'),
        ('1', '1'),
        ('2', '2'))
    )
    length_session1 = forms.ChoiceField(choices=session_lengths, required=True)
    length_session2 = forms.ChoiceField(choices=session_lengths, required=False)
    length_session3 = forms.ChoiceField(choices=session_lengths, required=False)
    number_attendee = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'size':'5'}), required=True)
    work_groups = forms.ChoiceField(choices=[('', '--Select WG(s)')] + IETFWG.choices(), required=False)
    conflict1 = forms.CharField(max_length=85, widget=forms.TextInput(attrs={'size':'55'}), required=False)
    conflict2 = forms.CharField(max_length=85, widget=forms.TextInput(attrs={'size':'55'}), required=False)
    conflict3 = forms.CharField(max_length=85, widget=forms.TextInput(attrs={'size':'55'}), required=False)
    conflict_other = forms.CharField(max_length=85, widget=forms.Textarea(attrs={'cols':'40', 'rows': 3}), required=False)
    special_req = forms.CharField(max_length=85, widget=forms.Textarea(attrs={'cols':'65', 'rows': 6}), required=False)

    def clean_number_attendee(self):
        if self.clean_data['number_attendee'] == '0':
            raise forms.ValidationError, 'Zero Number of Attendees'

    def check_acronyms(self, acronymlist):
        bad_acronyms = []
        for acronym in acronymlist.replace(',',' ').split(' '):
            if acronym and Acronym.objects.filter(acronym=acronym).count() == 0:
                bad_acronyms.append(acronym)

        if bad_acronyms:
            raise forms.ValidationError, 'Invalid Working Group acronym in Conflicts to Avoid - %s' % ' '.join(bad_acronyms)

    def clean_conflict1(self):
        self.check_acronyms(self.clean_data['conflict1'] )       
    def clean_conflict2(self):
        self.check_acronyms(self.clean_data['conflict2'] )
    def clean_conflict3(self):
        self.check_acronyms(self.clean_data['conflict3'] )
