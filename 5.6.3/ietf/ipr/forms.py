import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder

from django import forms
from django.forms.models import BaseInlineFormSet

from ietf.doc.models import DocAlias
from ietf.group.models import Group
from ietf.ipr.fields import AutocompletedIprDisclosuresField
from ietf.ipr.models import IprDocRel, IprDisclosureBase, HolderIprDisclosure, GenericIprDisclosure, ThirdPartyIprDisclosure, NonDocSpecificIprDisclosure, LICENSE_MAPPING, IprLicenseTypeName
from ietf.message.models import Message

# ----------------------------------------------------------------
# Create base forms from models
# ----------------------------------------------------------------

phone_re = re.compile(r'^\+?[0-9 ]*(\([0-9]+\))?[0-9 -]+( ?x ?[0-9]+)?$')
phone_error_message = """Phone numbers may have a leading "+", and otherwise only contain numbers [0-9]; dash, period or space; parentheses, and an optional extension number indicated by 'x'."""

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
class HolderIprDisclosureForm(forms.ModelForm):
    licensing = CustomModelChoiceField(IprLicenseTypeName.objects.all(),widget=forms.RadioSelect,empty_label=None)
    updates = AutocompletedIprDisclosuresField(required=False)
    
    def __init__(self,*args,**kwargs):
        super(HolderIprDisclosureForm, self).__init__(*args,**kwargs)
        self.fields['licensing'].initial='noselect'
        self.fields['compliant'].widget.attrs['class'] = 'hidden'
        
    class Meta:
        model = HolderIprDisclosure
        exclude = [ 'by','docs','state','rel' ]

    def clean(self):
        super(HolderIprDisclosureForm, self).clean()
        cleaned_data = self.cleaned_data
        
        # ensure a contribution is specified
        if not self.data.get('draft-0-document') and not self.data.get('rfc-0-document') and not cleaned_data.get('other_designations'):
            raise forms.ValidationError('You need to specify a contribution in Section IV')
        
        return cleaned_data

class GenericIprDisclosureForm(forms.ModelForm):
    updates = AutocompletedIprDisclosuresField(required=False)
    # dummy fields, these are only here because NonDoc and Generic use the same input form
    patent_info = forms.CharField(max_length=255,widget=forms.Textarea)
    
    class Meta:
        model = GenericIprDisclosure
        exclude = [ 'by','docs','state','rel' ]
        
class GenericDisclosureForm(forms.Form):
    """Custom ModelForm-like form to use for Generic or NonDocSpecific Iprs.
    If patent_info is submitted create a NonDocSpecificIprDisclosure object
    otherwise create a GenericIprDisclosure object."""
    compliant = forms.BooleanField(required=False)
    holder_legal_name = forms.CharField(max_length=255)
    notes = forms.CharField(max_length=255,widget=forms.Textarea,required=False)
    other_designations = forms.CharField(max_length=255,required=False)
    holder_contact_name = forms.CharField(max_length=255)
    holder_contact_info = forms.CharField(max_length=255)
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
            del narge['has_patent_pending']
            obj = GenericIprDisclosure(**nargs)
        
        if kwargs.get('commit',True):
            obj.save()
        
        return obj
        
class MessageModelForm(forms.ModelForm):
    class Meta:
        model = Message
        exclude = ['time','by','content_type','related_groups','related_docs']
        
class ThirdPartyIprDisclosureForm(forms.ModelForm):
    updates = AutocompletedIprDisclosuresField(required=False)
    
    class Meta:
        model = ThirdPartyIprDisclosure
        exclude = [ 'by','docs','state','rel' ]

class NonDocSpecificIprDisclosureForm(forms.ModelForm):
    updates = AutocompletedIprDisclosuresField(required=False)
    
    class Meta:
        model = ThirdPartyIprDisclosure
        exclude = [ 'by','docs','state','rel' ]
        
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

class RfcForm(DraftForm):
    class Meta(DraftForm.Meta):
        exclude = ('revisions',)

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
