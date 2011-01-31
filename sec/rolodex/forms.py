import re
from django import forms
from django.core.validators import email_re
from sec.rolodex.models import PostalAddress, PhoneNumber, PersonOrOrgInfo, EmailAddress

# select widget choices
ADDRESS_TYPES = (
    ('W', 'Work'),
    ('H', 'Home'),
)

EMAIL_TYPES = (
    ('INET', 'Internet Style'),
    ('MCI', 'MCI Mail Style'),
    ('ULST', 'Unknown'),
)

PHONE_TYPES = (
    ('W', 'Work'),
    ('H', 'Home'),
    ('WF', 'Work Fax'),
    ('HF', 'Home Fax'),
)

class BulkUpdateForm (forms.Form):
    old_email = forms.EmailField(max_length=255,required=False)
    new_email = forms.EmailField(max_length=255,required=False)
    tag = forms.IntegerField(required=False,widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(BulkUpdateForm, self).__init__(*args, **kwargs)
        self.fields['old_email'].widget.attrs['readonly'] = True

class SearchForm(forms.Form):
    first_name = forms.CharField(max_length=20,required=False)
    last_name = forms.CharField(max_length=50,required=False)
    email = forms.CharField(max_length=255,required=False)
    tag = forms.IntegerField(required=False)

# ------------------------------------------------------
# ModelForms for editing existing contacts
# ------------------------------------------------------

class AddressForm(forms.ModelForm):
    class Meta:
        model = PostalAddress
        exclude = ('person_or_org',)

    # use this method to set attrs which keeps other meta info from model.  
    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields['address_type'].widget=forms.Select(choices=ADDRESS_TYPES)
        self.fields['address_priority'].widget=forms.HiddenInput()
        self.fields['address_priority'].required=False

    # function for marking "Primary" records in template
    def is_primary(self):
        try:
           priority = self.initial['address_priority']
        except KeyError:
           return False

        if priority == 1:
            return True
        else:
            return False

class EmailForm(forms.ModelForm):
    class Meta:
        model = EmailAddress
        exclude = ('person_or_org',)

    # use this method to set attrs which keeps other meta info from model.  
    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        #self.fields['type'].widget=forms.Select(choices=EMAIL_TYPES)
        self.fields['type'].widget.attrs["size"] = 10
        self.fields['address'].widget.attrs["size"] = 30
        self.fields['comment'].widget.attrs["size"] = 30
        self.fields['priority'].widget=forms.HiddenInput()
        self.fields['priority'].required=False

    # function for marking "Primary" records in template
    def is_primary(self):
        try:
           priority = self.initial['priority']
        except KeyError:
           return False

        if priority == 1:
            return True
        else:
            return False

    # Validation: don't allow an email comment without an email
    def clean(self):
        cleaned_data = self.cleaned_data
        comment = cleaned_data.get("comment")
        address = cleaned_data.get("address")

        if comment and not address:
            raise forms.ValidationError("You cannot save a email comment without a email address.")

        # Always return the full collection of cleaned data.
        return cleaned_data

class PersonForm(forms.ModelForm):
    class Meta:
        model = PersonOrOrgInfo

    # use this method to set attrs which keeps other meta info from model.  
    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        self.fields['name_prefix'].widget.attrs["size"] = 10
        self.fields['middle_initial'].widget.attrs["size"] = 2 
        self.fields['name_suffix'].widget.attrs["size"] = 10

class PhoneForm(forms.ModelForm):
    class Meta:
        model = PhoneNumber
        verbose_name_plural = "Phone Numbers"
        exclude = ('person_or_org',)

    # use this method to set attrs which keeps other meta info from model.  
    def __init__(self, *args, **kwargs):
        super(PhoneForm, self).__init__(*args, **kwargs)
        self.fields['phone_type'].widget=forms.Select(choices=PHONE_TYPES)
        self.fields['phone_priority'].widget=forms.HiddenInput()
        self.fields['phone_priority'].required=False

    # function for marking "Primary" records in template
    def is_primary(self):
        try:
           priority = self.initial['phone_priority']
        except KeyError:
           return False

        if priority == 1:
            return True
        else:
            return False

    # Validation: don't allow a phone comment whithout a phone number
    def clean(self):
        cleaned_data = self.cleaned_data
        phone_number = cleaned_data.get("phone_number")
        phone_comment = cleaned_data.get("phone_comment")

        if phone_comment and not phone_number:
            raise forms.ValidationError("You cannot save a phone comment without a phone number.")

        # Always return the full collection of cleaned data.
        return cleaned_data

# ------------------------------------------------------
# Forms for addition of new contacts
# These sublcass the regular forms, with additional
# validations
# ------------------------------------------------------

class NewPhoneForm(PhoneForm):
    def clean_phone_number(self):
        # use phone number validation expression from IPR app
	phone_re = re.compile(r'^\+?[0-9 ]*(\([0-9]+\))?[0-9 -]+( ?x ?[0-9]+)?$')
	phone_error_message = """Phone numbers may have a leading "+", and otherwise only contain numbers [0-9]; dash, period or space; parentheses, and an optional extension number indicated by 'x'."""
        cleaned_data = self.cleaned_data
        phone_number = cleaned_data.get("phone_number")

        if phone_number and not phone_re.match(phone_number):
            raise forms.ValidationError(phone_error_message)

        return phone_number

class NewEmailForm(EmailForm):
    def clean_address(self):
        cleaned_data = self.cleaned_data
        address = cleaned_data.get("address")

        if address and not email_re.match(address):
            raise forms.ValidationError("Enter a valid email address")

        return address
        
class NewAddressForm(AddressForm):
    pass

class NewPersonForm(PersonForm):
    # use this method to set attrs which keeps other meta info from model.  
    def __init__(self, *args, **kwargs):
        super(NewPersonForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required=True
        self.fields['last_name'].required=True

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
