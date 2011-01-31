from django import forms

class BaseAWPForm(forms.ModelForm):
    '''This form isn't used directly.  When subclassed you must define the associated model'''
    # use this method to set attrs which keeps other meta info from model.  
    def __init__(self, *args, **kwargs):
        super(BaseAWPForm, self).__init__(*args, **kwargs)
        self.fields['url'].widget.attrs['size'] = 40
        self.fields['description'].widget.attrs['size'] = 40

    # Validation: url without description and vice-versa 
    def clean(self):
        super(BaseAWPForm, self).clean()
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')
        description = cleaned_data.get('description')

        if (url and not description) or (description and not url):
            raise forms.ValidationError('You must fill out URL and Description')

        # Always return the full collection of cleaned data.
        return cleaned_data
