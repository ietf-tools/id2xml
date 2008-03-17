# Copyright The IETF Trust 2007, All Rights Reserved


# from django.utils.encoding import force_unicode # this is for current version
# from django.utils.translation import ugettext # this is for current version
from django.utils.datastructures import MultiValueDict
from django.newforms.fields import Field, EMPTY_VALUES
from django.newforms.widgets import FileInput
from django.newforms.util import ErrorList, ValidationError, flatatt
from models import IdSubmissionDetail, STATUS_CODE
from ietf.idtracker.models import InternetDraft, EmailAddress, PersonOrOrgInfo, WGChair
from models import TempIdAuthors
from datetime import datetime,date
import time
import os
from django import newforms as forms
from django.conf import settings
from ietf.idsubmit.parser.draft_parser import check_creation_date
class SubmitterForm(forms.Form):
    fname = forms.CharField(required=True, label='Given Name : ', max_length="20")
    lname = forms.CharField(required=True, label='Family Name : ', max_length="30")
    submitter_email = forms.EmailField(required=True, label='Email Address:', max_length="50")
    # getting submitter's information need to be written as separate function so that it can be also used by AdjustForm.save
    def save(self, submission):
        submitter_email_address = self.clean_data['submitter_email']
        if submission.revision == '00':
            target_priority = 1
        else:
            draft = InternetDraft.objects.get(filename=submission.filename)
            target_priority = draft.id_document_tag
        #Get submitter tag
        submitter_email_object = EmailAddress.objects.filter(address=self.clean_data['submitter_email'])

        if submitter_email_object:
            person_or_org = submitter_email_object[0].person_or_org
        else:
            person_or_org = PersonOrOrgInfo(first_name=self.clean_data['fname'], last_name=self.clean_data['lname'], date_modified=datetime.now())
            person_or_org.save()
            newEmail = EmailAddress(person_or_org=person_or_org, type="INET", priority=1, address=self.clean_data['submitter_email'])
            newEmail.save()

        submission.submitter = person_or_org
        submission.sub_email_priority = target_priority
        #Checking valid submitter
        if  TempIdAuthors.objects.filter(submission=submission,email_address=self.clean_data['submitter_email']):
        #submitter is in current authors list
            valid_author = True
        elif submission.revision != '00' and EmailAddress.objects.filter(address=self.clean_data['submitter_email'],priority=target_priority):
        #submitter is in previous authors list
            valid_author = True
        elif WGChair.objects.filter(group_acronym=submission.group,person=person_or_org):
        #submitter is WG Chair
            valid_author = True
        else:
            valid_author = False
        if valid_author:
            submission.status_id = 4 # submission.status_id
        else:
            submission.status_id = 205
        submission.save()
        return person_or_org
class AdjustForm(forms.Form):
    submission_id = forms.CharField(required=True, widget=forms.HiddenInput(attrs={'type':'hidden'}))
    title = forms.CharField(required=True, label='Title : ', max_length="255", widget=forms.TextInput(attrs={'size':65}))
    revision = forms.CharField(required=True, label='Version : ', max_length="3", widget=forms.TextInput(attrs={'size':3}))
    creation_date = forms.CharField(required=True, label='Creation Date : ', max_length="25", widget=forms.TextInput(attrs={'size':25}))
    txt_page_count = forms.CharField(required=True, label='Page : ', max_length="25", widget=forms.TextInput(attrs={'size':25}))
    abstract = forms.CharField(required=True, label='Abstract : ', widget=forms.Textarea(attrs={'rows':4, 'cols':72,}))
    fname = forms.CharField(required=True, label='Given Name : ', max_length="20")
    lname = forms.CharField(required=True, label='Family Name : ', max_length="30")
    submitter_email = forms.EmailField(required=True, label='Email Address:', max_length="50")
    comment_to_sec = forms.CharField(required=False, label='Comment to the Secretariat: ', widget=forms.Textarea(attrs={'rows':4, 'cols':72,}))

    def clean_revision(self):
        expected_revision = IdSubmissionDetail.objects.get(pk=self.clean_data['submission_id']).invalid_version
        if not expected_revision == int(self.clean_data['revision']):
            raise forms.ValidationError, "%s(Version %s is expected)" % (STATUS_CODE[201], str(expected_revision).zfill(2))
    def clean_creation_date(self):
        cdate = self.clean_data['creation_date'].split('-')
        if not check_creation_date(date(int(cdate[0]),int(cdate[1]),int(cdate[2]))):
            raise forms.ValidationError, STATUS_CODE[204]
    def save(self, submission, param=None):
        submitter_email_address = self.clean_data['submitter_email']
        if submission.revision == '00':
            target_priority = 1
        else:
            try:
                draft = InternetDraft.objects.get(filename=submission.filename)
                target_priority = draft.id_document_tag
            except InternetDraft.DoesNotExist:
               target_priority = 1
        #Get submitter tag
        submitter_email_object = EmailAddress.objects.filter(address=self.clean_data['submitter_email'])

        if submitter_email_object:
            person_or_org = submitter_email_object[0].person_or_org
        else:
            person_or_org = PersonOrOrgInfo(first_name=self.clean_data['fname'], last_name=self.clean_data['lname'], date_modified=datetime.now())
            person_or_org.save()
            newEmail = EmailAddress(person_or_org=person_or_org, type="INET", priority=1, address=self.clean_data['submitter_email'])
            newEmail.save()
 
        submission.submitter = person_or_org
        submission.sub_email_priority = target_priority
        submission.comment_to_sec=param['comment_to_sec']
        submission.title = param['title']
        submission.revision = param['revision']
        cdate = param['creation_date'].split('-')
        submission.creation_date = date(int(cdate[0]),int(cdate[1]),int(cdate[2])) 
        submission.abstract = param['abstract']
        submission.txt_page_count = param['txt_page_count']
        submission.save()
        return True 

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
    def get_content(self, txt_file):
        return self.clean_data[txt_file]['content']
        # return self.cleaned_data[txt_file].content # this is for current version

    def save(self, filename, revision):
        self.file_ext_list = []
        for file_name, file_ext in self.file_names.items():
            try:
                content = self.clean_data[file_name]['content']
                # content = self.cleaned_data[file_name].content # this is for current version
            # except AttributeError: # this is for current version
            except TypeError:
                continue
            file_path = "%s-%s%s" % (os.path.join(settings.STAGING_PATH,filename), revision, file_ext)
            try:
                save_file = open(file_path,'w')
                save_file.write(content)
                save_file.close()
                self.file_ext_list.append( file_ext )
            except IOError:
                return False
        return True
