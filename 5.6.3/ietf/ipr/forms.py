import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder

from django import forms
from django.forms.models import BaseInlineFormSet

from ietf.doc.models import DocAlias
from ietf.group.models import Group
from ietf.ipr.fields import AutocompletedIprDisclosuresField
from ietf.ipr.models import IprDocRel, IprDisclosureBase, HolderIprDisclosure, GenericIprDisclosure, ThirdPartyIprDisclosure, LICENSE_MAPPING, IprLicenseTypeName
from ietf.ipr.models import IprDetail, IprContact, LICENSE_CHOICES # remove 

# ----------------------------------------------------------------
# Create base forms from models
# ----------------------------------------------------------------

phone_re = re.compile(r'^\+?[0-9 ]*(\([0-9]+\))?[0-9 -]+( ?x ?[0-9]+)?$')
phone_error_message = """Phone numbers may have a leading "+", and otherwise only contain numbers [0-9]; dash, period or space; parentheses, and an optional extension number indicated by 'x'."""

class BaseIprForm(forms.ModelForm):
    '''delete me'''
    licensing_option = forms.IntegerField(widget=forms.RadioSelect(choices=LICENSE_CHOICES), required=False)
    is_pending = forms.IntegerField(widget=forms.RadioSelect(choices=((1, "YES"), (2, "NO"))), required=False)
    applies_to_all = forms.IntegerField(widget=forms.RadioSelect(choices=((1, "YES"), (2, "NO"))), required=False)
    class Meta:
        model = IprDetail
        exclude = ('rfc_document', 'id_document_tag') # 'legacy_url_0','legacy_url_1','legacy_title_1','legacy_url_2','legacy_title_2')

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
    #updates = forms.CharField(max_length=32,required=False)
    updates = AutocompletedIprDisclosuresField(required=False)
    
    def __init__(self,*args,**kwargs):
        super(HolderIprDisclosureForm, self).__init__(*args,**kwargs)
        self.fields['licensing'].initial='noselect'
        self.fields['compliant'].widget.attrs['class'] = 'hidden'
        
    class Meta:
        model = HolderIprDisclosure
        exclude = [ 'by','docs','state','rel' ]
    
    #def save(self, *args, **kwargs):
    #    disclosure = super(HolderIprDisclosureForm, self).save(*args, **kwargs)
    #    # custom save stuff
    #    return disclosure
    
    def clean(self):
        super(HolderIprDisclosureForm, self).clean()
        cleaned_data = self.cleaned_data
        
        # ensure a contribution is specified
        if not self.data.get('draft-0-document') and not self.data.get('rfc-0-document') and not cleaned_data.get('other_designations'):
            raise forms.ValidationError('You need to specify a contribution in Section IV')
        
        return cleaned_data
    
    #def clean_updates(self):
    #    updates = self.cleaned_data.get('updates')
    #    objects = []
    #    if updates:
    #        pks = updates.split(',')
    #    else:
    #        return objects
    #    
    #    try:
    #        for pk in pks:
    #            obj = IprDisclosureBase.objects.get(pk=pk)
    #            objects.append(obj)
    #    except IprDisclosureBase.DoesNotExist:
    #        raise forms.ValidationError('Invalid Document')
    #    return objects
        
class GenericIprDisclosureForm(forms.ModelForm):
    class Meta:
        model = GenericIprDisclosure
        exclude = [ 'by','docs','state','rel' ]
        
class ThirdPartyIprDisclosureForm(forms.ModelForm):
    class Meta:
        model = ThirdPartyIprDisclosure
        exclude = [ 'by','docs','state','rel' ]

class IprForm(BaseIprForm):
    # delete me
    pass

class TestDraftForm(forms.ModelForm):
    class Meta:
        model = IprDocRel
        
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
"""
class IprForm(BaseIprForm):
    holder_contact = None
    rfclist = forms.CharField(required=False)
    draftlist = forms.CharField(required=False)
    stdonly_license = forms.BooleanField(required=False)
    hold_contact_is_submitter = forms.BooleanField(required=False)
    ietf_contact_is_submitter = forms.BooleanField(required=False)
    if section_list.get("holder_contact", False):
        holder_contact = ContactForm(prefix="hold")
    if section_list.get("ietf_contact", False):
        ietf_contact = ContactForm(prefix="ietf")
    if section_list.get("submitter", False):
        submitter = ContactForm(prefix="subm")
    def __init__(self, *args, **kw):
        contact_type = {1:"holder_contact", 2:"ietf_contact", 3:"submitter"}
        contact_initial = {}
        if update:
            for contact in update.contact.all():
                contact_initial[contact_type[contact.contact_type]] = contact.__dict__
            if submitter:
                if type == "third-party":
                    contact_initial["ietf_contact"] = submitter
                else:
                    contact_initial["submitter"] = submitter
        kwnoinit = kw.copy()
        kwnoinit.pop('initial', None)
        for contact in ["holder_contact", "ietf_contact", "submitter"]:
            if section_list.get(contact, False):
                setattr(self, contact, ContactForm(prefix=contact[:4], initial=contact_initial.get(contact, {}), *args, **kwnoinit))
        rfclist_initial = ""
        if update:
            rfclist_initial = " ".join(a.doc_alias.name.upper() for a in IprDocAlias.objects.filter(doc_alias__name__startswith="rfc", ipr=update))
        self.base_fields["rfclist"] = forms.CharField(required=False, initial=rfclist_initial)
        draftlist_initial = ""
        if update:
            draftlist_initial = " ".join(a.doc_alias.name + ("-%s" % a.rev if a.rev else "") for a in IprDocAlias.objects.filter(ipr=update).exclude(doc_alias__name__startswith="rfc"))
        self.base_fields["draftlist"] = forms.CharField(required=False, initial=draftlist_initial)
        if section_list.get("holder_contact", False):
            self.base_fields["hold_contact_is_submitter"] = forms.BooleanField(required=False)
        if section_list.get("ietf_contact", False):
            self.base_fields["ietf_contact_is_submitter"] = forms.BooleanField(required=False)
        self.base_fields["stdonly_license"] = forms.BooleanField(required=False)

        BaseIprForm.__init__(self, *args, **kw)
    # Special validation code
    def clean(self):
        if section_list.get("ietf_doc", False):
            # would like to put this in rfclist to get the error
            # closer to the fields, but clean_data["draftlist"]
            # isn't set yet.
            rfclist = self.cleaned_data.get("rfclist", None)
            draftlist = self.cleaned_data.get("draftlist", None)
            other = self.cleaned_data.get("other_designations", None)
            if not rfclist and not draftlist and not other:
                raise forms.ValidationError("One of the Document fields below must be filled in")
        return self.cleaned_data
    def clean_rfclist(self):
        rfclist = self.cleaned_data.get("rfclist", None)
        if rfclist:
            rfclist = re.sub("(?i) *[,;]? *rfc[- ]?", " ", rfclist)
            rfclist = rfclist.strip().split()
            for rfc in rfclist:
                try:
                    DocAlias.objects.get(name="rfc%s" % int(rfc))
                except (DocAlias.DoesNotExist, DocAlias.MultipleObjectsReturned, ValueError):
                    raise forms.ValidationError("Unknown RFC number: %s - please correct this." % rfc)
            rfclist = " ".join(rfclist)
        return rfclist
    def clean_draftlist(self):
        draftlist = self.cleaned_data.get("draftlist", None)
        if draftlist:
            draftlist = re.sub(" *[,;] *", " ", draftlist)
            draftlist = draftlist.strip().split()
            drafts = []
            for draft in draftlist:
                if draft.endswith(".txt"):
                    draft = draft[:-4]
                if re.search("-[0-9][0-9]$", draft):
                    name = draft[:-3]
                    rev = draft[-2:]
                else:
                    name = draft
                    rev = None
                try:
                    doc = Document.objects.get(docalias__name=name)
                except (Document.DoesNotExist, Document.MultipleObjectsReturned) as e:
                    log("Exception: %s" % e)
                    raise forms.ValidationError("Unknown Internet-Draft: %s - please correct this." % name)
                if rev and doc.rev != rev:
                    raise forms.ValidationError("Unexpected revision '%s' for draft %s - the current revision is %s.  Please check this." % (rev, name, doc.rev))
                drafts.append("%s-%s" % (name, doc.rev))
            return " ".join(drafts)
        return ""
    def clean_licensing_option(self):
        licensing_option = self.cleaned_data['licensing_option']
        if section_list.get('licensing', False):
            if licensing_option in (None, ''):
                raise forms.ValidationError, 'This field is required.'
        return licensing_option
    def is_valid(self):
        if not BaseIprForm.is_valid(self):
            return False
        for contact in ["holder_contact", "ietf_contact", "submitter"]:
            if hasattr(self, contact) and getattr(self, contact) != None and not getattr(self, contact).is_valid():
                return False
        return True


class UpdateForm(BaseContactForm):
    def __init__(self, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.fields["update_auth"] = forms.BooleanField()
"""