import re
from django import forms
from sec.areas.models import *
from sec.core.forms import BaseAWPForm

# select widget choices
#STATUS_TYPES = tuple(AreaStatus.objects.values_list('status_id', 'status_value'))
# per requirements, do not include "Unknown" in status select choices
STATUS_CHOICES = (
    (1, 'Active'),
    (2, 'Concluded')
)

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        exclude = ('extra_email_addresses', 'area_coordinator_tag')

    # use this method to set attrs which keeps other meta info from model.  
    def __init__(self, *args, **kwargs):
        super(AreaForm, self).__init__(*args, **kwargs)
        self.fields['status'].widget=forms.Select(choices=STATUS_CHOICES)
        self.fields['comments'].widget.attrs['rows'] = 2

    # Validation: status and conclude_date must agree
    def clean(self):
        super(AreaForm, self).clean()
        cleaned_data = self.cleaned_data
        concluded_date = cleaned_data.get('concluded_date')
        status = cleaned_data.get('status')
        concluded_status_object = AreaStatus.objects.get(status_id=2)

        if concluded_date and status != concluded_status_object:
            raise forms.ValidationError('Concluded Date set but status is %s' % (status.status_value))

        if status == concluded_status_object and not concluded_date:
            raise forms.ValidationError('Status is Concluded but Concluded Date not set.')

        # Always return the full collection of cleaned data.
        return cleaned_data

class AcronymForm(forms.ModelForm):
    ''' Due to constraints in the underlying database design we cannot change the Area(Acronym) name
        if External Web Pages are defined, because they key off the name field?!  To change the name
        all external web pages need to be removed first, than re-added.  '''

    class Meta:
        model = Acronym

    # in order to preserve field uniqueness checks you must call the parent class's clean() method
    # when overriding clean() on a ModelForm 
    def clean(self):
        super(AcronymForm, self).clean()
        qs = AreaWGAWP.objects.filter(name=self.instance.name)
        if ('name' in self.changed_data) and qs:
            raise forms.ValidationError("Due to DB contraints you cannot change the Area name if External Web Pages are defined.  You must delete them first.") 
        return self.cleaned_data 

    # we set "unique" property in model to prevent dupes

class AddAreaForm(forms.Form):
    acronym = forms.CharField(max_length=12,required=True)
    name = forms.CharField(max_length=80,required=True)
    status = forms.IntegerField(widget=forms.Select(choices=STATUS_CHOICES),required=True)
    start_date = forms.DateField()
    comments = forms.CharField(widget=forms.Textarea(attrs={'rows':'1'}),required=False)

    def clean_acronym(self):
        # get name, strip leading and trailing spaces
        name = self.cleaned_data.get('acronym', '').strip()
        # check for invalid characters
        r1 = re.compile(r'[a-zA-Z\-\. ]+$')
        if name and not r1.match(name):
            raise forms.ValidationError("Enter a valid acronym (only letters,period,hyphen allowed)") 
        # ensure doesn't already exist
        if Acronym.objects.filter(acronym=name):
            raise forms.ValidationError("This acronym already exists.  Enter a unique one.") 
        return name

# for use with Add view, Model Form doesn't work because we don't know the parent model(acronym)
# when initial screen is displayed
class AWPAddForm(forms.Form):
    url = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'size':'40'}))
    description = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'size':'40'}))
 
    # Validation: url without description and vice-versa 
    def clean(self):
        super(AWPAddForm, self).clean()
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')
        description = cleaned_data.get('description')

        if (url and not description) or (description and not url):
            raise forms.ValidationError('You must fill out URL and Description')

        # Always return the full collection of cleaned data.
        return cleaned_data

class AWPForm(BaseAWPForm):
    class Meta:
        model = AreaWGAWP

class AreaDirectorForm(forms.Form):
    ad_name = forms.CharField(max_length=100,label='Name',help_text="To see a list of people type the first name, or last name, or both.")
    login = forms.EmailField(max_length=75,help_text="This should be the person's primary email address.")

    # set css class=name-autocomplete for name field (to provide select list)
    def __init__(self, *args, **kwargs):
        super(AreaDirectorForm, self).__init__(*args, **kwargs)
        self.fields['ad_name'].widget.attrs['class'] = 'name-autocomplete'

    def clean_ad_name(self):
        name = self.cleaned_data.get('ad_name', '')
        # check for tag within parenthesis to ensure name was selected from the list 
        m = re.search(r'(\d+)', name)
        if name and not m:
            raise forms.ValidationError("You must select an entry from the list!") 
        return name
