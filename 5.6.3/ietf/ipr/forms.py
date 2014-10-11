import email
import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder

from django import forms
from django.forms.models import BaseInlineFormSet

from ietf.doc.models import DocAlias
from ietf.group.models import Group
from ietf.ipr.fields import AutocompletedIprDisclosuresField
from ietf.ipr.models import (IprDocRel, IprDisclosureBase, HolderIprDisclosure,
    GenericIprDisclosure, ThirdPartyIprDisclosure, NonDocSpecificIprDisclosure,
    LICENSE_MAPPING, IprLicenseTypeName, IprDisclosureStateName)
from ietf.message.models import Message

# ----------------------------------------------------------------
# Globals
# ----------------------------------------------------------------
STATE_CHOICES = [ (x.slug, x.name) for x in IprDisclosureStateName.objects.all() ]
STATE_CHOICES.insert(0,('all','All States'))
# ----------------------------------------------------------------
# Base Classes
# ----------------------------------------------------------------

class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return LICENSE_MAPPING[obj.pk]

class GroupModelChoiceField(forms.ModelChoiceField):
    '''Custom ModelChoiceField that displays group acronyms as choices.'''
    def label_from_instance(self, obj):
        return obj.acronym

# ----------------------------------------------------------------
# Forms
# ----------------------------------------------------------------
class AddCommentForm(forms.Form):
    private = forms.BooleanField(required=False,help_text="If this box is checked the comment will not appear in the disclosure's public history view.")
    comment = forms.CharField(required=True, widget=forms.Textarea)

class AddEmailForm(forms.Form):
    direction = forms.ChoiceField(choices=(("incoming", "Incoming"), ("outgoing", "Outgoing")),
        widget=forms.RadioSelect)
    message = forms.CharField(required=True, widget=forms.Textarea)

    def clean_message(self):
        text = self.cleaned_data['message']
        message = email.message_from_string(text)
        for field in ('to','from','subject','date'):
            if not message[field]:
                raise forms.ValidationError('Error parsing email: {} field not found.'.format(field))
        return message

class DraftForm(forms.ModelForm):
    document = forms.CharField(widget=forms.TextInput(attrs={'class': 'draft-autocomplete'}),required=False)  # override ModelChoiceField
    
    class Meta:
        model = IprDocRel
        widgets = {
            'sections': forms.TextInput(),
        }
        help_texts = { 'sections': 'Sections' }
    
    def __init__(self, *args,**kwargs):
        super(DraftForm, self).__init__(*args,**kwargs)
        i = self.initial.get('document')
        if i:
            da = DocAlias.objects.get(pk=self.initial['document'])
            self.initial['document'] = da.name
            
    def clean_document(self):
        name = self.cleaned_data.get('document')
        try:
            alias = DocAlias.objects.get(name=name)
        except:
            raise forms.ValidationError('Invalid Document')
        return alias

class GenericDisclosureForm(forms.Form):
    """Custom ModelForm-like form to use for Generic or NonDocSpecific Iprs.
    If patent_info is submitted create a NonDocSpecificIprDisclosure object
    otherwise create a GenericIprDisclosure object."""
    compliant = forms.BooleanField(required=False)
    holder_legal_name = forms.CharField(max_length=255)
    notes = forms.CharField(max_length=255,widget=forms.Textarea,required=False)
    other_designations = forms.CharField(max_length=255,required=False)
    holder_contact_name = forms.CharField(max_length=255)
    holder_contact_email = forms.EmailField()
    holder_contact_info = forms.CharField(max_length=255,widget=forms.Textarea,required=False)
    submitter_name = forms.CharField(max_length=255)
    submitter_email = forms.EmailField()
    patent_info = forms.CharField(max_length=255,widget=forms.Textarea,required=False)
    has_patent_pending = forms.BooleanField(required=False)
    statement = forms.CharField(max_length=255,widget=forms.Textarea,required=False)
    updates = AutocompletedIprDisclosuresField(required=False)
    
    def save(self, *args, **kwargs):
        # super(GenericDisclosureForm, self).save(*args,*kwargs)
        if self.cleaned_data.get('patent_info'):
            obj = NonDocSpecificIprDisclosure(**self.cleaned_data)
        else:
            nargs = self.cleaned_data.copy()
            del nargs['patent_info']
            del nargs['has_patent_pending']
            obj = GenericIprDisclosure(**nargs)
        
        if kwargs.get('commit',True):
            obj.save()
        
        return obj

class IprDisclosureFormBase(forms.ModelForm):
    """Base form for Holder and ThirdParty disclosures"""
    updates = AutocompletedIprDisclosuresField(required=False)
    same_as_above = forms.BooleanField(required=False)
    
    def __init__(self,*args,**kwargs):
        super(IprDisclosureFormBase, self).__init__(*args,**kwargs)
        self.fields['submitter_name'].required = False
        self.fields['submitter_email'].required = False
        self.fields['compliant'].initial = True
    
    class Meta:
        """This will be overridden"""
        model = IprDisclosureBase
        
    def clean(self):
        super(IprDisclosureFormBase, self).clean()
        cleaned_data = self.cleaned_data
        
        # ensure a contribution is specified
        if not self.data.get('draft-0-document') and not self.data.get('rfc-0-document') and not cleaned_data.get('other_designations'):
            raise forms.ValidationError('You need to specify a contribution in Section IV')
        
        # if same_as_above not checked require submitted
        if not self.cleaned_data.get('same_as_above'):
            if not ( self.cleaned_data.get('submitter_name') and self.cleaned_data.get('submitter_email') ):
                raise forms.ValidationError('Submitter information must be provided in section VII')
        
        return cleaned_data
    
    def save(self, *args, **kwargs):
        obj = super(IprDisclosureFormBase, self).save(*args,commit=False)
        if self.cleaned_data.get('same_as_above') == True:
            obj.submitter_name = obj.holder_contact_name
            obj.submitter_email = obj.holder_contact_email
        if kwargs.get('commit',True):
            obj.save()
        
        return obj
        
class HolderIprDisclosureForm(IprDisclosureFormBase):
    licensing = CustomModelChoiceField(IprLicenseTypeName.objects.all(),
        widget=forms.RadioSelect,empty_label=None,initial='noselect')
    
    class Meta:
        model = HolderIprDisclosure
        exclude = [ 'by','docs','state','rel' ]

class MessageModelForm(forms.ModelForm):
    response_due = forms.DateField(required=False,help_text='The date which a response is due')
    
    class Meta:
        model = Message
        fields = ['to','frm','cc','bcc','reply_to','subject','body']
        exclude = ['time','by','content_type','related_groups','related_docs']
    
    def __init__(self, *args, **kwargs):
        super(MessageModelForm, self).__init__(*args, **kwargs)
        self.fields['frm'].label='From'
        self.fields['frm'].widget.attrs['readonly'] = True
        self.fields['reply_to'].widget.attrs['readonly'] = True

class NotifyForm(forms.Form):
    type = forms.CharField(widget=forms.HiddenInput)
    text = forms.CharField(widget=forms.Textarea)
    
class RfcForm(DraftForm):
    class Meta(DraftForm.Meta):
        exclude = ('revisions',)

class ThirdPartyIprDisclosureForm(IprDisclosureFormBase):
    class Meta:
        model = ThirdPartyIprDisclosure
        exclude = [ 'by','docs','state','rel' ]

class SearchForm(forms.Form):
    state =    forms.MultipleChoiceField(choices=STATE_CHOICES,widget=forms.CheckboxSelectMultiple,required=False)
    draft =    forms.CharField(max_length=128,required=False)
    rfc =      forms.IntegerField(required=False)
    holder =   forms.CharField(max_length=128,required=False)
    patent =   forms.CharField(max_length=128,required=False)
    group =    GroupModelChoiceField(label="Working group name",queryset=Group.objects.filter(type='wg').order_by('acronym'),required=False)
    doctitle = forms.CharField(max_length=128,required=False)
    iprtitle = forms.CharField(max_length=128,required=False)

class StateForm(forms.Form):
    state = forms.ModelChoiceField(queryset=IprDisclosureStateName.objects,label="New State",empty_label=None)
    private = forms.BooleanField(required=False,help_text="If this box is checked the comment will not appear in the disclosure's public history view.")
    comment = forms.CharField(required=False, widget=forms.Textarea)
'''
class SearchForm(forms.Form):
    draft_name = forms.CharField(
        label='I-D name (draft-...):',
        required=False)
    rfc_number = forms.IntegerField(
        label='RFC Number:',
        required=False)
    holder_legal_name = forms.CharField(
        label='Name of patent owner/applicant:',
        required=False)
    patent_info = forms.CharField(
        label='Characters in patent information:',
        required=False)
    group = GroupModelChoiceField(
        label='Working group:',
        queryset=Group.objects.filter(type='wg',state='active').order_by('acronym'),
        required=False)
    document_title = forms.CharField(
        label='Words in document title:',
        required=False)
    title = forms.CharField(
        label='Words in IPR disclosure title:',
        required=False)
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Document Search',
                'draft_name',
                'rfc_number'
            ),
            Fieldset(
                'Keyword Search',
                'holder_legal_name',
                'patent_info',
                'group',
                'document_title',
                'title'
            ),
            ButtonHolder(
                Submit('submit', 'Submit', css_class='button white')
            )
        )
        #self.helper.form_id = 'id-exampleForm'
        #self.helper.form_class = 'blueForms'
        #self.helper.form_method = 'post'
        #self.helper.form_action = 'submit_survey'
        #self.helper.add_input(Submit('submit', 'Submit'))
        super(SearchForm, self).__init__(*args, **kwargs)
'''