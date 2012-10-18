# Copyright The IETF Trust 2007, All Rights Reserved

from django import newforms as forms
from ietf.announcements.models import AnnouncedFrom, AnnouncedTo

class SendForm(forms.Form):

    def __init__(self, request, *args, **kwargs):
        # Set default value False when supported
        self.nomcom = forms.BooleanField(label='NonCom message?', widget=forms.RadioSelect(choices=((True, 'Yes'), (False, 'No'))))

        sender_choices = ((announced_from.email, announced_from.announced_from) for announced_from in AnnouncedFrom.objects.all())
        #sender_choices.extend((None, 'Otherhellip'))
        sender = forms.EmailField(widget=forms.Select(choices=sender_choices))

        self.sender_other = forms.EmailField(label='From')

        # Use MultiEmailField when supported
        recipeint_choices = ((announced_to.email, announced_to.announced_to) for announced_to in AnnouncedTo.objects.all())
        #recipeint_choices.extend((None, 'Otherhellip'))
        recipeint = forms.EmailField(widget=forms.Select(choices=sender_choices))

        recipient_other = forms.EmailField(label='To')

        cc = forms.EmailField(help_text='Separated by a comma.', required=False)
        bcc = forms.EmailField(help_text='Separated by a comma.', required=False)
        reply_to = forms.EmailField(help_text='Separated by a comma.', required=False)
        subject = forms.CharField()

        # Use forms.TextField when supported
        body = forms.CharField(widget=forms.Textarea(attrs={ 'class': 'form-textarea resizable', 'rows': 20, 'cols': 60 }))

        super(forms.Form, self).__init__(*args, **kwargs)
