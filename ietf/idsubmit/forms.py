# Copyright The IETF Trust 2007, All Rights Reserved


# from django.utils.encoding import force_unicode # this is for current version
# from django.utils.translation import ugettext # this is for current version
from django.utils.datastructures import MultiValueDict
from django.newforms.fields import Field, EMPTY_VALUES
from django.newforms.widgets import FileInput
from django.newforms.util import ErrorList, ValidationError, flatatt
from models import IdSubmissionDetail
from ietf.idtracker.models import InternetDraft, EmailAddress, PersonOrOrgInfo, WGChair
from models import TempIdAuthors
from datetime import datetime,date
import time
from django import newforms as forms
from django.conf import settings

class SubmitterForm(forms.Form):
    fname = forms.CharField(required=True, label='Given Name : ', max_length="20")
    lname = forms.CharField(required=True, label='Family Name : ', max_length="30")
    submitter_email = forms.EmailField(required=True, label='Email Address:', max_length="50")

    def save(self, submission, param=None):
        submitter_email_address = self.clean_data['submitter_email']
        if submission.revision == '00':
            target_priority = 1
        else:
            draft = InternetDraft.objects.get(filename=submission.filename)
            target_priority = draft.id_document_tag
        #Get submitter tag
        submitter_email_object = EmailAddress.objects.filter(address=self.clean_data['submitter_email'])

        if submitter_email_object:
            person_or_org_tag = submitter_email_object[0].person_or_org
        else:
            person_or_org_tag = PersonOrOrgInfo(first_name=self.clean_data['fname'], last_name=self.clean_data['lname'], date_modified=datetime.now())
            person_or_org_tag.save()
            newEmail = EmailAddress(person_or_org=person_or_org_tag, type="INET", priority=1, address=self.clean_data['submitter_email'])
            newEmail.save()
 
        submission.submitter = person_or_org_tag
        submission.sub_email_priority = target_priority
        if submission.status_id == 5:
            submission.comment_to_sec=param['comment_to_sec']
            submission.title = param['title']
            submission.revision = param['revision']
            c = time.strptime(param['creation_date'],"%Y-%M-%d")
            submission.creation_date = date(c[0],c[1],c[2]) 
            submission.abstract = param['abstract']
            submission.txt_page_count = param['pages']
        else:
            #Checking valid submitter
            if  TempIdAuthors.objects.filter(submission=submission,email_address=self.clean_data['submitter_email']):
            #submitter is in current authors list
                valid_author = True
            elif submission.revision != '00' and EmailAddress.objects.filter(address=self.clean_data['submitter_email'],priority=target_priority):
            #submitter is in previous authors list
                valid_author = True 
            elif WGChair.objects.filter(group_acronym=submission.group,person=person_or_org_tag):
            #submitter is WG Chair
                valid_author = True 
            else:
                valid_author = False
            if valid_author:
                submission.status_id = 4 # submission.status_id
            else:
                submission.status_id = 205
        submission.save()
        return person_or_org_tag

class IDUploadForm(forms.Form):
    txt_file = forms.Field(widget=forms.FileInput, label='.txt format *')
    xml_file = forms.Field(widget=forms.FileInput, required=False, label='.xml format')
    pdf_file = forms.Field(widget=forms.FileInput, required=False, label='.pdf format')
    ps_file = forms.Field(widget=forms.FileInput, required=False, label='.ps format')

    file_names = {'txt_file':'.txt', 'xml_file':'.xml', 
                   'pdf_file':'.pdf', 'ps_file':'.ps'}
    file_ext_list = []

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
                break

            save_file = open(settings.STAGING_PATH + filename + '-' + revision + file_ext,'w')
            save_file.write(content)
            save_file.close()
            self.file_ext_list.append( file_ext )

        """
        file_content = self.clean_data['txt_file']['content']
        output_id = open(settings.STAGING_PATH+filename+'-'+revision+'.txt','w')
        output_id.write(file_content)
        output_id.close()
        """
        for extra_type in [{'file_type':'xml_file','file_ext':'.xml'}, {'file_type':'pdf_file','file_ext':'.pdf'},{'file_type':'ps_file','file_ext':'.ps'}]:
            file_type=extra_type['file_type']
            file_ext=extra_type['file_ext']
            if self.clean_data[file_type]:
                extra_file_content = self.clean_data[file_type]['content']
                extra_output_id = open(settings.STAGING_PATH+filename+'-'+revision+file_ext,'w')
                extra_output_id.write(extra_file_content)
                extra_output_id.close()
                self.file_ext_list.append( file_ext )
        return settings.STAGING_PATH+filename+'-'+revision+'.txt'

