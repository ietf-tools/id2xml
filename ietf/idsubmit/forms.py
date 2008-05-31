# Copyright The IETF Trust 2007, All Rights Reserved


# from django.utils.encoding import force_unicode # this is for current version
# from django.utils.translation import ugettext # this is for current version
from models import IdSubmissionDetail, STATUS_CODE
from ietf.idtracker.models import InternetDraft, EmailAddress, PersonOrOrgInfo, WGChair
from models import TempIdAuthors
from datetime import datetime,date
import os
from django import newforms as forms
from django.conf import settings
from ietf.idsubmit.parser.draft_parser import check_creation_date

class AuthorForm(forms.Form):
    """An Internet Draft Author, to put into TempIdAuthors."""
    first_name = forms.CharField(required=False, label='Given Name', max_length=20)
    last_name = forms.CharField(required=False, label='Family Name', max_length=30)
    email = forms.EmailField(required=False, label='Email Address', max_length=255)
    # Either all are required, or none are, to delete (think core=True in admin)
    def clean(self):
        if self.clean_data['first_name'] + self.clean_data['last_name'] + self.clean_data['email'] == '':
            # Empty, so valid.
            return self.clean_data
        if self.clean_data['first_name'] != '' and self.clean_data['last_name'] != '' and self.clean_data['email'] != '':
            # All supplied, so valid.
            return self.clean_data
        if self.clean_data['first_name'] == '':
            raise forms.ValidationError('Given Name is required')
        if self.clean_data['last_name'] == '':
            raise forms.ValidationError('Family Name is required')
        if self.clean_data['email'] == '':
            raise forms.ValidationError('Email Address is required')
        raise forms.ValidationError('Neither valid nor invalid?')

class SubmitterForm(forms.Form):
    fname = forms.CharField(required=True, label='Given Name : ', max_length=20)
    lname = forms.CharField(required=True, label='Family Name : ', max_length=30)
    submitter_email = forms.EmailField(required=True, label='Email Address:', max_length=255)
    def save(self, submission):
        submitter_email_address = self.clean_data['submitter_email']
        if submission.revision == '00':
            target_priority = 1
        else:
            draft = InternetDraft.objects.get(filename=submission.filename)
            target_priority = draft.id_document_tag
        #Get submitter tag
        submitter_email_object = EmailAddress.objects.filter(address=submitter_email_address)

        if submitter_email_object:
            person_or_org = submitter_email_object[0].person_or_org
        else:
            person_or_org = PersonOrOrgInfo(first_name=self.clean_data['fname'], last_name=self.clean_data['lname'], date_modified=datetime.now(), modified_by="IDST", created_by="IDST")
            person_or_org.save()
            newEmail = EmailAddress(person_or_org=person_or_org, type="INET", priority=1, address=submitter_email_address)
            newEmail.save()

        submission.submitter = person_or_org
        submission.sub_email_priority = target_priority
        if submission.valid_submitter(submitter_email_address):
            submission.status_id = 4
        else:
            submission.status_id = 205
        submission.save()
        return person_or_org

class AdjustForm(forms.Form):
    title = forms.CharField(required=True, label='Title : ', max_length="255", widget=forms.TextInput(attrs={'size':65}))
    revision = forms.CharField(required=True, label='Version : ', max_length="3", widget=forms.TextInput(attrs={'size':3}))
    creation_date = forms.DateField(required=True, label='Creation Date : ')
    txt_page_count = forms.CharField(required=True, label='Pages : ', max_length="25", widget=forms.TextInput(attrs={'size':25}))
    abstract = forms.CharField(required=True, label='Abstract : ', widget=forms.Textarea(attrs={'rows':4, 'cols':72,}))
    comment_to_sec = forms.CharField(required=False, label='Comment to the Secretariat: ', widget=forms.Textarea(attrs={'rows':4, 'cols':72,}))

    def clean_revision(self):
        revision = self.clean_data['revision']
        expected_revision = self.submission.invalid_version
        if not expected_revision == int(revision):
            raise forms.ValidationError("%s (Version -%02d is expected)" % (STATUS_CODE[201], expected_revision))
        return revision
    def clean_creation_date(self):
        creation_date = self.clean_data['creation_date']
        if not check_creation_date(creation_date):
            raise forms.ValidationError(STATUS_CODE[204])
        return creation_date
    def save(self):
        self.submission.comment_to_sec = self.clean_data['comment_to_sec']
        self.submission.title = self.clean_data['title']
        self.submission.revision = self.clean_data['revision']
        self.submission.creation_date = self.clean_data['creation_date']
        self.submission.abstract = self.clean_data['abstract']
        self.submission.txt_page_count = self.clean_data['txt_page_count']
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
        return self.clean_data[file_type]['content']

    def save(self, filename, revision):
        self.file_ext_list = []
        for file_name, file_ext in self.file_names.items():
            if self.clean_data[file_name]:
                content = self.clean_data[file_name]['content']
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
