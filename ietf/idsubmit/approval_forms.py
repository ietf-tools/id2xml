# Copyright The IETF Trust 2007, All Rights Reserved

from django import newforms as forms

class PreauthzForm(forms.Form):
    draft = forms.CharField()
    def clean_draft(self):
        draft = self.clean_data['draft']
        if not draft.startswith("draft-ietf-"):
            raise forms.ValidationError("Filename must start with draft-ietf-")
        if not draft.islower():
            raise forms.ValidationError("Filename must be all lowercase.")
        # XXX Come to think of it, maybe we should have an 1id-guidelines
        # filename is valid checker.  Are there any other forms that
        # want a filename for a -00?
        return draft

class PickApprover(forms.Form):
    """
    When instantiating, supply a list of person objects in approvers=
    """
    approver = forms.ChoiceField(choices=(
	('', '-- Pick an approver from the list below'),
    ))
    def __init__(self, approvers, *args, **kwargs):
	super(PickApprover, self).__init__(*args, **kwargs)
	self.fields['approver'].choices = [('', '-- Pick an approver from the list below')] + [(person.person_or_org_tag, str(person)) for person in approvers]
    def clean_approver(self):
        approver = self.clean_data['approver']
        if approver == '':
            return forms.ValidationError('You must pick an approver.')
        return approver

