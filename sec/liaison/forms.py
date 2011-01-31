import re
from django import forms
from models import FromBodies

class FromBodiesForm(forms.Form):
    name = forms.CharField(max_length=35)

    def clean_name(self):
        # get name, strip leading and trailing spaces
        name = self.cleaned_data.get('name', '').strip()
        # ensure name doesn't already exist in the table, case insensitive
        if FromBodies.objects.filter(body_name__iexact=name).count() > 0:
            raise forms.ValidationError("This name already exists!")
        # check for invalid characters
        r1 = re.compile(r'[\w\-\.\/ ]+$')
        if not r1.match(name):
            # raise forms.ValidationError("Only alphanumeric characters and '-', '.', '/' are allowed!") 
            raise forms.ValidationError("Enter a valid name.") 
        return name
