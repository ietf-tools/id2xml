# Copyright The IETF Trust 2007, All Rights Reserved

from django import newforms as forms

class PreauthzForm(forms.Form):
    draft = forms.CharField()
    #FIXME: Add a multivalued selection widget for chair selection
