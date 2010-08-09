# Copyright The IETF Trust 2007, All Rights Reserved


# from django.utils.encoding import force_unicode # this is for current version
# from django.utils.translation import ugettext # this is for current version
from models import STATUS_CODE
from ietf.idtracker.models import InternetDraft, EmailAddress, PersonOrOrgInfo
import os
from django import forms
from django.conf import settings
from ietf.idsubmit.parser.draft_parser import check_creation_date
from ietf.utils import log

class AuthorForm(forms.Form):
    """An Internet Draft Author, to put into TempIdAuthors."""
    first_name = forms.CharField(required=False, label='Given Name', max_length=20)
    last_name = forms.CharField(required=False, label='Family Name', max_length=30)
    email_address = forms.EmailField(required=False, label='Email Address', max_length=255)
    # Either all are required, or none are, to delete (think core=True in admin)
    def clean(self):
        # If any keys are missing, then field validation failed, so
        # we can't add anything.
        for field in ['first_name', 'last_name', 'email_address']:
            if not self.cleaned_data.has_key( field ):
                return self.cleaned_data
        if self.cleaned_data['first_name'] + self.cleaned_data['last_name'] + self.cleaned_data['email_address'] == '':
            # Empty, so valid.
            return self.cleaned_data
        if self.cleaned_data['first_name'] != '' and self.cleaned_data['last_name'] != '' and self.cleaned_data['email_address'] != '':
            # All supplied, so valid.
            return self.cleaned_data
        if self.cleaned_data['first_name'] == '':
            raise forms.ValidationError('Given Name is required')
        if self.cleaned_data['last_name'] == '':
            raise forms.ValidationError('Family Name is required')
        if self.cleaned_data['email_address'] == '':
            raise forms.ValidationError('Email Address is required')
        raise forms.ValidationError('Neither valid nor invalid?')

class SubmitterForm(forms.Form):
    fname = forms.CharField(required=True, label='Given Name : ', max_length=20)
    lname = forms.CharField(required=True, label='Family Name : ', max_length=30)
    submitter_email = forms.EmailField(required=True, label='Email Address:', max_length=255)
    def save(self, submission):
        submitter_email_address = self.cleaned_data['submitter_email']
        person = PersonOrOrgInfo.objects.get_or_create(
            first_name=self.cleaned_data['fname'],
            last_name=self.cleaned_data['lname'],
            created_by="IDST",
        )
        person = person[0] # get_or_create returns a tuple (object, boolean_was_created) [wiggins@concentricsky]
        person.add_email_address(submitter_email_address, type='INET')

        # The priority can either be:
        # - An I-D tag, because this is the address used for that I-D
        # - A small integer (e.g., 1), because this address is not on
        #   file (yet?), either because I'm a new author or because
        #   this is a new document.
        # We make sure that the address that the submitter provided
        # matches; it's easy to accidentally use a different address
        # than the submitter identified themselves as which results
        # in very confusing behavior (e.g., "I said I was foo@example.com
        # but it sent the confirmation email to bar@example.net")
        email = None
        try:
            email = person.emailaddress_set.get(type='INET', address=submitter_email_address)
        except EmailAddress.DoesNotExist:
            pass
	try:
	    draft = InternetDraft.objects.get(filename=submission.filename)
	    try:
		email = person.emailaddress_set.get(type='I-D', priority=draft.id_document_tag, address=submitter_email_address)
	    except EmailAddress.DoesNotExist:
		pass
	except InternetDraft.DoesNotExist:
	    pass

        if email:
            target_priority = email.priority
        else:
            # Default to priority=1, which we assume exists for every user.
            log( 'Could not find priority for person %d email %s' % ( person.person_or_org_tag, submitter_email_address ) )
            target_priority = 1

        submission.submitter = person
        submission.sub_email_priority = target_priority
        if submission.valid_submitter(submitter_email_address):
            submission.status_id = 4
        else:
            submission.status_id = 205
        submission.save()

class AdjustForm(forms.Form):
    title = forms.CharField(required=True, label='Title : ', max_length="255", widget=forms.TextInput(attrs={'size':65}))
    revision = forms.CharField(required=True, label='Version : ', max_length="3", widget=forms.TextInput(attrs={'size':3}))
    creation_date = forms.DateField(required=True, label='Creation Date : ')
    txt_page_count = forms.CharField(required=True, label='Pages : ', max_length="25", widget=forms.TextInput(attrs={'size':25}))
    abstract = forms.CharField(required=True, label='Abstract : ', widget=forms.Textarea(attrs={'rows':4, 'cols':72,}))
    comment_to_sec = forms.CharField(required=False, label='Comment to the Secretariat: ', widget=forms.Textarea(attrs={'rows':4, 'cols':72,}))

    def clean_revision(self):
        revision = self.cleaned_data['revision']
        expected_revision = self.submission.invalid_version
        if not expected_revision == int(revision):
            raise forms.ValidationError("%s (Version -%02d is expected)" % (STATUS_CODE[201], expected_revision))
        return revision
    def clean_creation_date(self):
        creation_date = self.cleaned_data['creation_date']
        if not check_creation_date(creation_date):
            raise forms.ValidationError(STATUS_CODE[204])
        return creation_date
    def save(self):
        self.submission.comment_to_sec = self.cleaned_data['comment_to_sec']
        self.submission.title = self.cleaned_data['title']
        self.submission.revision = self.cleaned_data['revision']
        self.submission.creation_date = self.cleaned_data['creation_date']
        self.submission.abstract = self.cleaned_data['abstract']
        self.submission.txt_page_count = self.cleaned_data['txt_page_count']
        self.submission.save()

class IDUploadForm(forms.Form):
    txt_file = forms.Field(widget=forms.FileInput, label='.txt format *')
    xml_file = forms.Field(widget=forms.FileInput, required=False, label='.xml format')
    pdf_file = forms.Field(widget=forms.FileInput, required=False, label='.pdf format')
    ps_file = forms.Field(widget=forms.FileInput, required=False, label='.ps format')

    file_names = {'txt_file':'.txt', 'xml_file':'.xml', 'pdf_file':'.pdf', 'ps_file':'.ps'}
    file_ext_list = []
# Need to check valid file extension for extra files
    #def clean_xml_file(self):
    #def clean_pdf_file(self):
    #def clean_ps_file(self):
            #for file_name, file_info in request.FILES.items():
            #    if re.match(r'^[a-z0-9-\.]+$', dp.filename):
            #        file_ext = ".%s" % file_info['filename'].split('.')[1]
            #        if file_ext.lower() not in form.file_names.values():
            #            return render("idsubmit/error.html", {'error_msg':'not allowed file format - %s' % file_ext.lower()}, context_instance=RequestContext(request))
            #    else:
            #        err_msg = "Filename contains non alpha-numeric character"
    def get_content(self, file_type):
        cached_content = getattr(self, 'cached_content', None)
        if cached_content is None:
                self.cached_content = self.cleaned_data[file_type].read()
        return self.cached_content

    def save(self, filename, revision):
        self.file_ext_list = []
        for file_name, file_ext in self.file_names.items():
            if self.cleaned_data[file_name]:
                content = self.get_content(file_name)
            else:
                continue
            file_path = "%s-%s%s" % (os.path.join(settings.STAGING_PATH,filename), revision, file_ext)
            try:
                save_file = open(file_path,'w')
                save_file.write(content)
                save_file.close()
                self.file_ext_list.append( file_ext )
            except IOError:
                #XXX hiding this makes this error hard to debug
                return False
        return True
