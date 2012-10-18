# Copyright The IETF Trust 2007, All Rights Reserved

from django import newforms as forms
from ietf.idtracker.models import IDState, IDStatus, IETFWG
from ietf.idindex.models import orgs
from ietf.utils import normalize_draftname

import datetime

# days_to_expire is a magic number that's supposed to be the number of days until a draft expires
# The value is imported into forms.py in addition to being used here

days_to_expire = 183

def fastforward_to_expiry(tmpdate):
    if (tmpdate != None):
	return tmpdate - datetime.timedelta(days_to_expire)
    else:
	return None

class DateFieldWithErrorPrompt(forms.DateField):
    def clean(self, value):
	try:
	    return super(DateFieldWithErrorPrompt, self).clean(value)
	except forms.ValidationError, err:
	    raise forms.ValidationError(err.messages+["Expected format: YYYY-MM-DD"])

class IDIndexSearchForm(forms.Form):
    within_choices= [
	  ('','All/Any'),
	  ('7','+/- 1 week'),
	  ('31','+/- 1 month'),
	  ('90', '+/- 3 months'),
    ]
    filename = forms.CharField(max_length=100, label='Filename (Full or Partial):', widget=forms.TextInput(attrs={'size': 30}), required=False)
    id_tracker_state_id = forms.ChoiceField(label='I-D Tracker State:', required=False)
    wg_id = forms.ChoiceField(label='Working Group:', required=False)
    other_group = forms.ChoiceField(choices=[('', 'All/Any')] + [(org['key'], org['name']) for org in orgs], label='Other Group:', required=False)
    status_id = forms.ChoiceField(label='I-D Status:', required=False)
    sub_after_date  = DateFieldWithErrorPrompt(label='Submitted After', required=False)
    exp_after_date  = DateFieldWithErrorPrompt(label='Expires After', required=False)
    sub_before_date = DateFieldWithErrorPrompt(label='Submitted Before', required=False)
    exp_before_date = DateFieldWithErrorPrompt(label='Expires Before', required=False)
    sub_within_date = forms.ChoiceField(choices=within_choices, label='Submitted Within', required=False)
    exp_within_date = forms.ChoiceField(choices=within_choices, label='Expires Within', required=False)
    last_name = forms.CharField(max_length=50, required=False)
    first_name = forms.CharField(max_length=50, required=False)

    def __init__(self, *args, **kwargs):
	super(IDIndexSearchForm, self).__init__(*args, **kwargs)
	self.fields['id_tracker_state_id'].choices = [('', 'All/Any')] + IDState.choices()
	self.fields['wg_id'].choices = [('', 'All/Any')] + IETFWG.choices()
	self.fields['status_id'].choices = [('', 'All/Any')] + [(status.status_id, status.status) for status in IDStatus.objects.all()]

    def clean_filename(self):
	return normalize_draftname(self.clean_data.get('filename'))

    def clean_exp_before_date(self):
	return fastforward_to_expiry(self.clean_data.get('exp_before_date'))

    def clean_exp_after_date(self):
	return fastforward_to_expiry(self.clean_data.get('exp_after_date'))
