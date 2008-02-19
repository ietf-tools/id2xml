# Copyright The IETF Trust 2007, All Rights Reserved

from django import newforms as forms
from models import IESGLogin, IDStatus, Area, IDState, IDSubState, IDIntendedStatus,TelechatDates, InternetDraft, IDState, IDSubState
TELECHAT_DATE_CHOICES = (
    (TelechatDates.objects.get(id=1).date1,TelechatDates.objects.get(id=1).date1),
    (TelechatDates.objects.get(id=1).date2,TelechatDates.objects.get(id=1).date2),
    (TelechatDates.objects.get(id=1).date3,TelechatDates.objects.get(id=1).date3),
    (TelechatDates.objects.get(id=1).date4,TelechatDates.objects.get(id=1).date4),
)
TELECHAT_DATE_BALLOT_SEARCH_CHOICES = (
    ('any', 'Any future telechat'),
    ('all', 'All telechat'),
    (TelechatDates.objects.get(id=1).date1,TelechatDates.objects.get(id=1).date1),
    (TelechatDates.objects.get(id=1).date2,TelechatDates.objects.get(id=1).date2),
    (TelechatDates.objects.get(id=1).date3,TelechatDates.objects.get(id=1).date3),
    (TelechatDates.objects.get(id=1).date4,TelechatDates.objects.get(id=1).date4),
)
POSITION_CHOICES = (
    ('','--All/Any'),
    ('no_record','No Record'),
    ('yes_col','Yes'),
    ('no_col','No Objection'),
    ('discuss','Discuss'),
    ('abstain','Abstain'),
    ('recuse','Recuse'),
) 
class IDSearch(forms.Form):
    search_job_owner = forms.ChoiceField(choices=(), required=False)
    search_group_acronym = forms.CharField(widget=forms.TextInput(attrs={'size': 6, 'maxlength': 10}), required=False)
    search_status_id = forms.ModelChoiceField(IDStatus.objects.all(), empty_label="--All", required=False)
    search_area_acronym = forms.ModelChoiceField(Area.objects.filter(status=Area.ACTIVE), empty_label="--All/Any", required=False)
    search_cur_state = forms.ModelChoiceField(IDState.objects.all(), empty_label="--All/Any", required=False)
    sub_state_id = forms.ChoiceField(choices=(), required=False)
    search_filename = forms.CharField(widget=forms.TextInput(attrs={'size': 15, 'maxlength': 60}), required=False)
    search_rfcnumber = forms.IntegerField(widget=forms.TextInput(attrs={'size': 5, 'maxlength': 60}), required=False)
    def __init__(self, *args, **kwargs):
        super(IDSearch, self).__init__(*args, **kwargs)
	self.fields['search_job_owner'].choices = [('', '--All/Any')] + [(ad.id, "%s, %s" % (ad.last_name, ad.first_name)) for ad in IESGLogin.objects.filter(user_level=1).order_by('last_name')] + [('-99', '------------------')] + [(ad.id, "%s, %s" % (ad.last_name, ad.first_name)) for ad in IESGLogin.objects.filter(user_level=2).order_by('last_name')]
	self.fields['sub_state_id'].choices = [('', '--All Substates'), ('0', 'None')] + [(state.sub_state_id, state.sub_state) for state in IDSubState.objects.all()]

class BallotSearch(forms.Form):
    telechat_date = forms.ChoiceField(choices=TELECHAT_DATE_BALLOT_SEARCH_CHOICES)
    position = forms.ChoiceField(choices=POSITION_CHOICES)

class IDDetail(forms.Form):
    intended_status = forms.ModelChoiceField(IDIntendedStatus.objects.all())
    agenda = forms.BooleanField(required=False)
    telechat_date = forms.ChoiceField(choices=TELECHAT_DATE_CHOICES,required=False)
    job_owner = forms.ModelChoiceField(IESGLogin.objects.filter(user_level=1).order_by('last_name'))
    status_date = forms.DateField(widget=forms.TextInput(attrs={'size': 15, 'maxlength': 60}), required=False)
    note = forms.CharField(widget=forms.Textarea(attrs={'rows':3, 'cols':72,}), required=False)
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows':10, 'cols':72,}), required=False)
    public_flag = forms.BooleanField()
    state_change_notice_to = forms.CharField(widget=forms.TextInput(attrs={'size': 55, 'maxlength': 255}), required=False)
    next_state = forms.ModelChoiceField(IDState.objects.all(), required=False, empty_label="---Select Next State") 
    next_sub_state = forms.ModelChoiceField(IDSubState.objects.all(), required=False, empty_label="---Select Sub State") 
    def save(self,idinternal,request,LoginObj=None, ballot=None):
        import datetime
        internet_draft = idinternal.draft 
        internet_draft.intended_status = self.clean_data['intended_status']
        internet_draft.save()
        idinternal.agenda = self.clean_data['agenda']
        tdates = self.clean_data['telechat_date'].split('-')
        idinternal.telechat_date = datetime.date(int(tdates[0]),int(tdates[1]),int(tdates[2]))
        idinternal.job_owner = self.clean_data['job_owner']
        idinternal.status_date = self.clean_data['status_date']
        idinternal.note = self.clean_data['note']
        idinternal.state_change_notice_to = self.clean_data['state_change_notice_to']
        if self.clean_data['next_state']:
            idinternal.change_state(self.clean_data['next_state'], self.clean_data['next_sub_state'],LoginObj)
        elif self.clean_data['next_sub_state']:
            idinternal.change_state(idinternal.cur_state, self.clean_data['next_sub_state'],LoginObj,change_sub_only=True)
        elif "next_state_button" in request.POST:
            idinternal.change_state(IDState.objects.get(state= request.POST['next_state_button']), None, LoginObj)
        elif 'back_to_previous' in request.POST:
            idinternal.change_state(idinternal.prev_state, idinternal.prev_sub_state,LoginObj)
        if self.clean_data['comment']:
            idinternal.add_comment(self.clean_data['comment'],False,LoginObj,self.clean_data['public_flag'],ballot)
        idinternal.save()
        
class EmailFeedback(forms.Form):
    category = forms.CharField(widget=forms.HiddenInput())
    name = forms.CharField(label='Your Name')
    email = forms.EmailField(label='Your Email')
    subject = forms.CharField(widget=forms.TextInput(attrs={'size': 72}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'cols': 70}))
    def clean_category(self):
	value = self.clean_data.get('category', 'bugs')
	if value not in ('bugs', 'discuss'):
	    raise forms.ValidationError, 'Unknown category, try "discuss" or "bugs".'
	return value

