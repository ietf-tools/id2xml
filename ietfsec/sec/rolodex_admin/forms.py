import re
from django import forms
from sec.rolodex_admin.models import PostalAddress, PhoneNumber, PersonOrOrgInfo, EmailAddress

# select widget choices
PHONE_TYPES = (
    ('W', 'Work'),
    ('H', 'Home'),
    ('WF', 'Work Fax'),
    ('HF', 'Home Fax'),
)

EMAIL_TYPES = (
    ('INET', 'Internet Style'),
    ('MCI', 'MCI Mail Style'),
    ('ULST', 'Unknown'),
)

ADDRESS_TYPES = (
    ('W', 'Work'),
    ('H', 'Home'),
)

class AddressForm(forms.ModelForm):
    class Meta:
        model = PostalAddress
        exclude = ('address_priority',)

    # use this method to set attrs which keeps other meta info from model.  
    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields['address_type'].widget=forms.Select(choices=ADDRESS_TYPES)

class PhoneForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        verbose_name_plural = "Phone Numbers"

    # use this method to set attrs which keeps other meta info from model.  
    def __init__(self, *args, **kwargs):
        super(PhoneForm, self).__init__(*args, **kwargs)
        self.fields['phone_type'].widget=forms.Select(choices=PHONE_TYPES)
        #self.fields['phone_priority'].widget=forms.HiddenInput()
        #self.fields['phone_priority'].required=False
        self.fields['person_or_org'].widget=forms.HiddenInput()

    # Validation: don't allow a phone comment whithout a phone number
    def clean(self):
        cleaned_data = self.cleaned_data
        phone_number = cleaned_data.get("phone_number")
        phone_comment = cleaned_data.get("phone_comment")

        if phone_comment and not phone_number:
            raise forms.ValidationError("You cannot save a phone comment without a phone number.")

        # Always return the full collection of cleaned data.
        return cleaned_data

class EmailForm(forms.ModelForm):
    class Meta:
        model = EmailAddress
        exclude = ('person_or_org', 'priority',)

    # use this method to set attrs which keeps other meta info from model.  
    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        self.fields['type'].widget=forms.Select(choices=EMAIL_TYPES)
        # need to allow blank address so empty email on add_proceed won't cause validation error
        self.fields['address'].required=False

    # Validation: don't allow an email comment without an email
    def clean(self):
        cleaned_data = self.cleaned_data
        comment = cleaned_data.get("comment")
        address = cleaned_data.get("address")

        if comment and not address:
            raise forms.ValidationError("You cannot save an email comment without an email address.")

        # Always return the full collection of cleaned data.
        return cleaned_data

class NameForm(forms.ModelForm):
    class Meta:
        model = PersonOrOrgInfo

    def clean_first_name(self):
        # get name, strip leading and trailing spaces
        name = self.cleaned_data.get('first_name', '').strip()
        # check for invalid characters
        r1 = re.compile(r'[a-zA-Z\-\.\(\) ]+$')
        if not r1.match(name):
            raise forms.ValidationError("Enter a valid name. (only letters,period,hyphen,paren allowed)") 
        return name

    def clean_last_name(self):
        # get name, strip leading and trailing spaces
        name = self.cleaned_data.get('last_name', '').strip()
        # check for invalid characters
        r1 = re.compile(r'[a-zA-Z\-\.\(\) ]+$')
        if not r1.match(name):
            raise forms.ValidationError("Enter a valid name. (only letters,period,hyphen,paren allowed)") 
        return name

    def clean_name_prefix(self):
        # get name, strip leading and trailing spaces
        name = self.cleaned_data.get('name_prefix', '').strip()
        # check for invalid characters
        r1 = re.compile(r'[a-zA-Z\-\. ]+$')
        if name and not r1.match(name):
            raise forms.ValidationError("Enter a valid name. (only letters,period,hyphen allowed)") 
        return name

    def clean_name_suffix(self):
        # get name, strip leading and trailing spaces
        name = self.cleaned_data.get('name_suffix', '').strip()
        # check for invalid characters
        r1 = re.compile(r'[a-zA-Z\-\. ]+$')
        if name and not r1.match(name):
            raise forms.ValidationError("Enter a valid name. (only letters,period,hyphen allowed)") 
        return name

    def clean_middle_initial(self):
        # get name, strip leading and trailing spaces
        name = self.cleaned_data.get('middle_initial', '').strip()
        # check for invalid characters
        r1 = re.compile(r'[a-zA-Z\. ]+$')
        if name and not r1.match(name):
            raise forms.ValidationError("Enter a valid name. (only letters,period allowed)") 
        return name
