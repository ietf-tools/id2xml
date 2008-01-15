# Copyright The IETF Trust 2007, All Rights Reserved

import re, os, glob, time
from datetime import datetime, date

from django.shortcuts import render_to_response as render, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist as ExceptionDoesNotExist
from django.http import HttpResponseRedirect
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.views.generic.list_detail import object_detail
from django.conf import settings
from models import IdSubmissionDetail, TempIdAuthors, IdApprovedDetail, IdDates
from ietf.idtracker.models import Acronym, IETFWG, InternetDraft, EmailAddress, IDAuthor, IDInternal, DocumentComment, PersonOrOrgInfo
from ietf.announcements.models import ScheduledAnnouncement
from ietf.idsubmit.forms import IDUploadForm, SubmitterForm
from ietf.idsubmit.models import STATUS_CODE, SUBMISSION_ENV
from ietf.utils.mail import send_mail
from ietf.idsubmit.announcements import ID_ACTION_ANNOUNCEMENT, MSG_BODY_SCHEDULED_ANNOUNCEMENT
from django.core.mail import BadHeaderError
from ietf.idsubmit.parser.draft_parser import DraftParser

# function parse_meta_data
# This function extract filename, revision, abstract, title, and
# author's information from the passed I-D content

def file_upload(request):
 
    form = None
    if request.POST:

        post_data = request.POST.copy()
        post_data.update(request.FILES)

        form = IDUploadForm(post_data)
        if form.is_bound and form.is_valid():
            if not request.FILES['txt_file']['content-type'].startswith('text'):
                return render("idsubmit/error.html", {'error_msg':STATUS_CODE[101]}, context_instance=RequestContext(request))

            dp = DraftParser(form.get_content('txt_file'))
            dp.set_remote_ip(request.META.get('REMOTE_ADDR'))
            threshold_msg = dp.check_dos_threshold()
            if threshold_msg:
                return render("idsubmit/error.html", {'error_msg':threshold_msg}, context_instance=RequestContext(request))

            for file_name, file_info in request.FILES.items():
                if re.match(r'^[a-z0-9-\.]+$', dp.filename):
                    if file_info['filename'][-4:].lower() not in form.file_names.values():
                        return render("idsubmit/error.html", {'error_msg':'not allowed file format'}, context_instance=RequestContext(request))
                else:
                    err_msg = "Filename contains non alpha-numeric character"
                    return render("idsubmit/error.html", {'error_msg':err_msg}, context_instance=RequestContext(request))
            if dp.status_id:
                file_type = form.save(dp.filename, dp.revision)
                file_path = settings.STAGING_PATH+dp.filename+'-'+dp.revision+'.txt'
                print file_path
                dp.set_file_type(form.file_ext_list)

                idnits_msg = dp.check_idnits(file_path)
                if type(idnits_msg).__name__=='dict':
                    if idnits_msg['error'] > 0:
                        idnits_result = True
                        dp.status_id = 203
                        dp._set_meta_data_errors('idnits', "<li>This document has " + str(idnits_msg['error']) + " idnits error(s)</li>")
                    else:
                        idnits_result = False
                else:
                    idnits_result = False

                meta_data = dp.get_meta_data_fields()

                list = IdSubmissionDetail(**meta_data)
                try:
                    submission_id=list.save()
                except AttributeError:
                    return  render("idsubmit/error.html", {'error_msg':"Data Saving Error"}, context_instance=RequestContext(request))

                current_date = date.today()
                current_hour = int(time.strftime("%H", time.localtime()))
                first_cut_off_date = IdDates.objects.get(id=1).id_date 
                second_cut_off_date = IdDates.objects.get(id=2).id_date 
                ietf_monday_date = IdDates.objects.get(id=3).id_date 
                id_date_var = { 'first_cut_off_date' : first_cut_off_date, 'second_cut_off_date' : second_cut_off_date, 'ietf_monday' : ietf_monday_date}

                if (current_date >= first_cut_off_date and current_date < second_cut_off_date):
                    if (current_date == first_cut_off_date and current_hour < 9):
                        id_date_var['date_check_err_msg'] = "first_second"
                        return render("idsubmit/error.html", id_date_var, context_instance=RequestContext(request))
                    else: # No more 00 submission
                        id_date_var['form'] = IDUploadForm()
                        id_date_var['cutoff_msg'] = "first_second"
                        return render ("idsubmit/upload.html", id_date_var, context_instance=RequestContext(request))
                elif current_date >= second_cut_off_date and current_date < ietf_monday_date:
                    if (current_date == second_cut_off_date and current_hour < 9):
                        id_date_var['form'] = IDUploadForm()
                        id_date_var['cutoff_msg'] = "second_ietf"
                        return render ("idsubmit/upload.html", id_date_var, context_instance=RequestContext(request))
                    else: #complete shut down of tool
                        id_date_var['date_check_err_msg'] = "second_ietf"
                        return render("idsubmit/error.html", id_date_var, context_instance=RequestContext(request))

                #if dp.get_group_id(dp.get_wg_id()).acronym_id == 1027:
                #    return render("idsubmit/error.html", {'error_msg':'Invalid WG ID, %s' % dp.get_wg_id()}, context_instance=RequestContext(request))
                # revision check
                if IdSubmissionDetail.objects.filter(filename__exact=dp.filename, status_id__gt=0,status_id__lt=100).exclude(submission_id=submission_id):
                    return render("idsubmit/error.html", {'error_msg':STATUS_CODE[103]}, context_instance=RequestContext(request))

                id = IdSubmissionDetail.objects.filter(filename=dp.filename, revision=dp.revision, status_id__range=(-2, 50)).exclude(submission_id=submission_id)
                if id.count() > 0:
                    return render("idsubmit/error.html", {'error_msg':'this document is already in the phase of processing'}, context_instance=RequestContext(request))

                authors_info = dp.get_author_detailInfo(dp.get_authors_info(),submission_id)
                for author_dict in authors_info:
                    author = TempIdAuthors(**author_dict)
                    try:
                        author.save()
                    except AttributeError:
                        return  render("idsubmit/error.html", {'error_msg':"Authors Data Saving Error"}, context_instance=RequestContext(request))
            file_type_list = meta_data['file_type'].split(',') 
            return render("idsubmit/validate.html",{'meta_data'        : meta_data,
                                                    'meta_data_errors' : dp.meta_data_errors,
                                                    'submission_id'    : submission_id,
                                                    'authors_info'     : authors_info,
                                                    'submitter_form'   : SubmitterForm(),
                                                    'idnits_result'   : idnits_result,
                                                    'file_type_list'  : file_type_list,
                                                    'staging_url'      : settings.STAGING_URL,
                                                    }, context_instance=RequestContext(request))
        else:
            return render("idsubmit/error.html", {'error_msg':'This is not valid data' + str(form.errors) }, context_instance=RequestContext(request))
            form = IDUploadForm()
    else:
        form = IDUploadForm()
    return render ("idsubmit/upload.html",{'form':form}, context_instance=RequestContext(request))

def adjust_form(request, submission_id_or_name):
    submission = IdSubmissionDetail.objects.get(submission_id=submission_id_or_name)
    warning_list = ['title', 'abstract', 'author', 'revision', 'filename', 'version', 'creation', 'group']
    meta_data_errors = {}
    for warning in warning_list:
        if re.search(warning, submission.warning_message.lower()):
            meta_data_errors[warning] = True
            print warning
        else:
            print warning + ' : No Match'
    args = request.GET.copy()
    if submission.submitter:
        args['fname'] = submission.submitter.first_name
        args['lname'] = submission.submitter.last_name
        args['submitter_email'] = \
            submission.submitter.emailaddress_set.get(priority=1).address
    file_type_list = submission.file_type.split(',')
    return object_detail(request, queryset=IdSubmissionDetail.objects.all(),
                                  object_id=submission_id_or_name,
                                  template_name="idsubmit/adjust.html",
                                  template_object_name='object',
                                  extra_context={'authors': TempIdAuthors.objects.filter(submission__exact=submission_id_or_name),
                                                 'submitter_form': SubmitterForm(args),
                                                 'staging_url':settings.STAGING_URL,
                                                 'file_type_list':file_type_list,
                                                 'meta_data_errors':meta_data_errors})
def draft_status(request, submission_id_or_name):

    submission = None
    if re.compile("^\d+$").findall(submission_id_or_name) : # if submission_id
        submission = get_object_or_404(IdSubmissionDetail, pk=submission_id_or_name)
    elif re.compile('^(draft-.+)').findall(submission_id_or_name) :
        # if submission name
        subm_name = re.sub('(-\d\d\.?(txt)?|/)$', '', submission_id_or_name)
        submissions = IdSubmissionDetail.objects.filter(filename__exact=subm_name).order_by('-submission_id') 

        if submissions.count() > 0 :
            submission = submissions[0]
        else:
            return render("idsubmit/error.html",{'error_msg':"Unknown filename"}, context_instance=RequestContext(request))
    else:
        return render("idsubmit/error.html",{'error_msg':"Unknown request"}, context_instance=RequestContext(request))

    if submission is None :
        return render("idsubmit/error.html",{'error_msg':"This submission is not found"}, context_instance=RequestContext(request))
    if submission.status_id > 200:
        meta_error = 1
    else:
        meta_error = 0
    if submission.status_id > 0 and submission.status_id < 100 :
        can_be_canceled = 1
        if submission.status_id == 2: #display validate.html
            meta_data_errors = {}
            return render("idsubmit/validate.html",{'meta_data'        : submission,
                               'submission_id'    : submission.submission_id,
                               'authors_info'     : TempIdAuthors.objects.filter(submission__exact=submission.submission_id).order_by('author_order'),
                               'submitter_form'   : SubmitterForm(),
                               'staging_url'      : settings.STAGING_URL,           
                               'meta_data_errors' : meta_data_errors,
                          }, context_instance=RequestContext(request))
    else:
        can_be_canceled = 0
    file_type_list = submission.file_type.split(',')
    if settings.SERVER_MODE == "production":
        doc_url = "http://www.ietf.org/internet-drafts"
    else:
        doc_url = settings.STAGING_URL
    return render(
        "idsubmit/status.html",
        {
            'object': submission,
            'authors': TempIdAuthors.objects.filter(
                    submission__exact=submission.submission_id).order_by('author_order'),
            'status_msg': STATUS_CODE[submission.status_id],
            'staging_url':doc_url,
            'meta_error': meta_error,
            'file_type_list':file_type_list,
            'can_be_canceled': can_be_canceled
        }, context_instance=RequestContext(request)
    )

def manual_post(request):
    param = request.POST.copy()
    param['filename'] = IdSubmissionDetail.objects.get(submission_id=param['submission_id']).filename
    authors_first_name = request.POST.getlist('author_first_name')
    authors_last_name  = request.POST.getlist('author_last_name')
    authors_email      = request.POST.getlist('author_email')
    param['authors'] = []
    cnt = 0
    for email in authors_email:
        if email:
            param['authors'].append( {'author_email': email,
                                  'author_first_name': authors_first_name[cnt],
                                  'author_last_name': authors_last_name[cnt]} )
        cnt = cnt + 1
    subject = 'Manual Posting Requested for ' + param['filename'] + '-' + param['revision']
    from_email = 'ID Submission Tool <idsubmission@ietf.org>'
    submitter = SubmitterForm(param)
    if submitter.is_bound and submitter.is_valid():
        try:
            submission = IdSubmissionDetail.objects.get(submission_id=param['submission_id'])
        except IdSubmissionDetail.DoesNotExist:
            return False
        submission.status_id=5
        if submitter.save(submission, param):
            cc_list = list();
            for author_info in TempIdAuthors.objects.filter(submission=submission).exclude(email_address=param['submitter_email']):
                cc_list.append(author_info.email_address)
            try:
                send_mail(request,[param['submitter_email']],from_email,subject,
                  "idsubmit/email_manual_post.txt",{'meta_data':param, 'cc':cc_list},
                  cc_list
                )
            except BadHeaderError:
                return render("idsubmit/error.html",{'error_msg':"Invalid header found."}, context_instance=RequestContext(request))
            return HttpResponseRedirect('/idsubmit/status/' + param['submission_id'])
        else:
            return render("idsubmit/error.html",{'error_msg':"The submitter information is not properly saved"}, context_instance=RequestContext(request))

def trigger_auto_post(request):
    args = request.GET.copy()
    if args.has_key('submission_id'):
        submission_id = args['submission_id']
    else:
        render("idsubmit/error.html",{'error_msg':"submission_id is not found"}, context_instance=RequestContext(request))
    if args.has_key('fname') and len(args['fname']):
        fname = ['fname']
    else:
        return render("idsubmit/error.html",{'error_msg':"Submitter's First Name is not found"}, context_instance=RequestContext(request))
    if args.has_key('lname') and len(args['lname']): lname = args['lname']
    else: return render("idsubmit/error.html",{'error_msg':"Submitter's Last Name is not found"}, context_instance=RequestContext(request))
    if args.has_key('submitter_email') and len(args['submitter_email']): submitter_email = args['submitter_email']
    else: return render("idsubmit/error.html",{'error_msg':"Submitter's Email Address is not found"}, context_instance=RequestContext(request))
    msg = ''

    try:
        submission = IdSubmissionDetail.objects.get(submission_id=submission_id)
    except IdSubmissionDetail.DoesNotExist:
        return render("idsubmit/error.html",{'error_msg':"There is a problem to get the Submitter's information"}, context_instance=RequestContext(request))

    submitterForm = SubmitterForm(args)
    if submitterForm.is_bound and submitterForm.is_valid():
        submitter = submitterForm.save(submission)
        if submission.status_id > 0 and submission.status_id < 100:
            send_mail(request, [submitter_email], \
                    "IETF I-D Submission Tool <idsubmission@ietf.org>", \
                    "I-D Submitter Authentication for %s" % submission.filename, \
                    "idsubmit/email_submitter_auth.txt", {'submission_id':submission_id, 'auth_key':submission.auth_key,'url':request.META['HTTP_HOST']})            
        return HttpResponseRedirect('/idsubmit/status/' + args['submission_id'])

def sync_docs (request, submission) :
    # sync docs with remote server.
    command = "sh %(BASE_DIR)s/idsubmit/sync_docs.sh --staging_path=%(staging_path)s --target_path_web=%(target_path_web)s --target_path_ftp=%(target_path_ftp)s --revision=%(revision)s --filename=%(filename)s --is_development=%(is_development)s" % {
        "filename" : submission.filename,
        "revision": submission.revision,
        "staging_path" : settings.STAGING_PATH,
        "target_path_web" : settings.TARGET_PATH_WEB,
        "target_path_ftp" : settings.TARGET_PATH_FTP,
        "BASE_DIR" : settings.BASE_DIR,
        "is_development" : (settings.SERVER_MODE == "production") and "0" or "1",

    }
    if settings.SERVER_MODE == "production" :
        try :
            os.system(command)
        except OSError:
            return False

    # remove files.
    try :
        [os.remove(i) for i in glob.glob("%s/%s-%s.*" % (settings.STAGING_PATH,submission.filename,submission.revision))]
    except :
        pass

    return True


def verify_key(request, submission_id, auth_key, from_wg_or_sec=None):

    subm = get_object_or_404(IdSubmissionDetail, pk=submission_id)

    now = datetime.now()

    if subm.auth_key != auth_key : # check 'auth_key'
        return render("idsubmit/error.html",{'error_msg':"Auth key is invalid"}, context_instance=RequestContext(request))

    if subm.status_id not in (4, 11, ) :
        # return status value 107, "Error - Draft is not in an appropriate
        # status for the requested page"
        return render("idsubmit/error.html",{'error_msg':STATUS_CODE[107]}, context_instance=RequestContext(request))

    if subm.sub_email_priority is None :
        subm.sub_email_priority = 1

    approved_status = None
    if subm.filename is not None :
        try :
            approved_status = IdApprovedDetail.objects.get(filename=subm.filename).approved_status
        except ExceptionDoesNotExist :
            pass

    if approved_status == 1 or subm.revision != "00" or subm.group_id == 1027 :
        # populate table

        if subm.revision == "00" :
            # if the draft file alreay existed, error will be occured.
            if InternetDraft.objects.filter(filename__exact=subm.filename).count() > 0 :
                return render("idsubmit/error.html",{'error_msg':"00 revision of this document already exists"}, context_instance=RequestContext(request))

            internet_draft = InternetDraft(
                title=subm.title,
                id_document_key=subm.title.upper(),
                group=subm.group,
                filename=subm.filename,
                revision=subm.revision,
                revision_date=subm.submission_date,
                file_type=subm.file_type,
                txt_page_count=subm.txt_page_count,
                abstract=subm.abstract,
                status_id=1,
                intended_status_id=8,
                start_date=now,
                last_modified_date=now,
                review_by_rfc_editor=False,
                expired_tombstone=False,
            )

            internet_draft.save()
        # get the id_document_tag what was just created for the new
        # recorde
        else : # Existing version; update the existing record using new values
            try :
                internet_draft = InternetDraft.objects.get(filename=subm.filename)
            except ExceptionDoesNotExist :
                return render("idsubmit/error.html",{'error_msg':"The previous submission of this document cannot be found"}, context_instance=RequestContext(request))
            else :
                try :
                    IDAuthor.objects.filter(document=internet_draft).delete()
                    EmailAddress.objects.filter(priority=internet_draft.id_document_tag).delete()
                    kwargs = subm.__dict__.copy()
                    kwargs.update({"revision_date" : subm.submission_date, "last_modified_date" : now })
                    internet_draft.title=subm.title
                    internet_draft.revision=subm.revision
                    internet_draft.revision_date=subm.submission_date
                    internet_draft.file_type=subm.file_type
                    internet_draft.txt_page_count=subm.txt_page_count
                    internet_draft.abstract=subm.abstract
                    internet_draft.last_modified_date=now
                    internet_draft.save()
                except :
                    return render("idsubmit/error.html",{'error_msg':"There was a problem updating the Internet-Drafts database"}, context_instance=RequestContext(request))

        authors_names = list()
        for author_info in TempIdAuthors.objects.filter(submission=subm) :
            email_address = EmailAddress.objects.filter(address=author_info.email_address)
            if email_address.count() > 0 :
                person_or_org_tag = email_address[0].person_or_org
            else :
                person_or_org_tag = PersonOrOrgInfo(
                    first_name=author_info.first_name,
                    last_name=author_info.last_name,
                    date_modified=now,
                )
                person_or_org_tag.save()

                EmailAddress(
                    person_or_org=person_or_org_tag,
                    type="Primary",
                    priority=1
                ).save()

            IDAuthor(
                document=internet_draft,
                person=person_or_org_tag,
            ).save()

            EmailAddress(
                person_or_org=person_or_org_tag,
                type="I-D",
                priority=internet_draft.id_document_tag
            ).save()

            # gathering author's names
            authors_names.append("%s. %s" % (author_info.first_name, author_info.last_name))

        subm.status_id = 7

        #################################################
        # Schedule I-D Announcement:
        # <Please read auto_post.cgi, sub schedule_id_announcement>
        cc_val = ""
        wgMail = str()
        # if group_acronym_id is 'Individual Submissions'
        if subm.group_id != 1027 :
            #subm.group.name
            cc_val = IETFWG.objects.get(pk=subm.group_id).email_address
            wgMail = "\nThis draft is a work item of the %(group_name)s Working Group of the IETF.\n" % {"group_name" : subm.group.name}
        ann = ID_ACTION_ANNOUNCEMENT
        body = ann.replace("^^^", "\t"
        ).replace("##id_document_name##", subm.title
        ).replace("##authors##",    ", ".join(authors_names)
        ).replace("##filename##",       subm.filename
        ).replace("##revision##",       subm.revision
        ).replace("##txt_page_count##", str(subm.txt_page_count)
        ).replace("##revision_date##",  str(subm.submission_date)
        ).replace("##current_date##",   now.strftime("%F")
        ).replace("##current_time##",   now.strftime("%T")
        ).replace("##abstract##",       subm.abstract
        ).replace("##wgMail##",     wgMail
        )

        scheduled_announcement = ScheduledAnnouncement(
            mail_sent =    False,
            scheduled_by =     "IDST",
            to_be_sent_date =  now,
            to_be_sent_time =  "00:00",
            scheduled_date =   now,
            scheduled_time =   now,
            subject =      "I-D Action:%s-%s.txt" % (subm.filename,subm.revision),
            to_val =       "i-d-announce@ietf.org",
            from_val =     "Internet-Drafts@ietf.org",
            cc_val =       cc_val,
            body =         body,
            content_type =     "Multipart/Mixed; Boundary=\"NextPart\"",
        ).save()

        subm.status_id = 8

        temp_id_document_tag = InternetDraft.objects.get(filename=subm.filename).id_document_tag
        if IDInternal.objects.filter(draft=temp_id_document_tag).filter(rfc_flag=0).extra(where=["cur_state < 100", ]) :
            #################################################
            # Schedule New Version Notification:
            # <Please read auto_post.cgi, sub
            # schedule_new_version_notification>

            # Add comment to ID Tracker
            document_comments = DocumentComment(
                document_id =  temp_id_document_tag,
                rfc_flag =     0,
                public_flag =  1,
                date = now,
                time = now,
                version =      subm.revision,
                comment_text = "New version available",
            ).save()

            id_internal = IDInternal.objects.filter(draft=temp_id_document_tag).filter(rfc_flag=0)[0]
            msg = ""
            if id_internal.cur_sub_state_id == 5 :
                msg = "Sub state has been changed to AD Follow up from New Id Needed"
                document_comments = DocumentComment(
                    document_id =  temp_id_document_tag,
                    rfc_flag =     0,
                    public_flag =  1,
                    date = now,
                    time = now,
                    version =      subm.revision,
                    comment_text = msg,
                ).save()

                id_internal.cur_sub_state_id = 2
                id_internal.prev_sub_state_id = 5
                id_internal.save()

            kwargs = subm.__dict__.copy()
            kwargs.update({"temp_id_document_tag" : temp_id_document_tag, })

            new_version_notify = MSG_BODY_SCHEDULED_ANNOUNCEMENT
            body = new_version_notify.replace("##filename##", subm.filename
            ).replace("##revision##", subm.revision
            ).replace("##msg##", msg 
            )
            send_to = list()
            send_to.append(id_internal.state_change_notice_to)

            #needs to be improved without using cursor object
            cursor = connection.cursor()
            # Django model does not handle the complex join query well, so use this.
            cursor.execute("select email_address from email_addresses a, id_internal b, iesg_login c where b.id_document_tag=%(temp_id_document_tag)s and rfc_flag=0 and b.job_owner=c.id and c.person_or_org_tag = a.person_or_org_tag and a.email_priority=1" % kwargs)
            __email_address = cursor.fetchone()
            if __email_address is not None and __email_address[0] not in send_to :
                send_to.append(__email_address[0])

            cursor.execute("select email_address from email_addresses a, ballots b, id_internal c,iesg_login d where c.id_document_tag=%(temp_id_document_tag)s and c.ballot_id=b.ballot_id and b.ad_id=d.id and d.person_or_org_tag=a.person_or_org_tag and a.email_priority=1 and b.discuss =1 and d.user_level=1" % kwargs)

            while True :
                __email_address = cursor.fetchone()
                if __email_address is None :
                    break
                if __email_address[0] in send_to :
                    continue

                send_to.append(__email_address[0])

            scheduled_announcement = ScheduledAnnouncement(
                mail_sent = False,
                scheduled_by =     "IDST",
                to_be_sent_date =  now,
                to_be_sent_time =  "00:00",
                scheduled_date =   now,
                scheduled_time =   now,
                subject =      "New Version Notification - %(filename)s-%(revision)s.txt" % kwargs,
                to_val =       ",".join([str(eb) for eb in send_to if eb is not None]),
                from_val =     "Internet-Drafts@ietf.org",
                cc_val =       cc_val,
                body =         body,
            ).save()

            subm.status_id = 9

        #################################################
        # Copy Document(s) to production servers:
        # <Please read auto_post.cgi, sub sync_docs>
        try :
            sync_docs(request, subm)
        except OSError :
            return render("idsubmit/error.html",{'error_msg':"There was a problem occurred while posting the document to the public server"}, context_instance=RequestContext(request))

        subm.status_id = -1

        # Notify All Authors:
        # <Please read auto_post.cgi, sub notify_all_authors>

        cc_email = list()
        if subm.group_id == 1027 :
            group_acronym = "Independent Submission"
        else :
            group_acronym = subm.group.name
            #removed cc'ing WG email address by request
            #cc_email.append(IETFWG.objects.get(group_acronym=subm.group).email_address)

        subm.comment_to_sec = subm.comment_to_sec and "\nComment:\n%s" % subm.comment_to_sec or ""

        try :
            (submitter_name, submitter_email, ) = subm.submitter.email()
        except :
            # for debuggin in development mode.
            if settings.SERVER_MODE == "production" :
                raise
            else :
                submitter_name = ""
                submitter_email = ""

        for author_info in TempIdAuthors.objects.filter(submission=subm).exclude(email_address=submitter_email) :
            if not author_info.email_address.strip() and submitter_email == author_info.email_address :
                continue

            if author_info.email_address not in cc_email :
                cc_email.append(author_info.email_address)

        to_email = submitter_email
        send_mail(
            request,
            to_email,
            "IETF I-D Submission Tool <idsubmission@ietf.org>",
            "New Version Notification for %s-%s" % (subm.filename,subm.revision),
            "idsubmit/email_posted_notice.txt", {'subm':subm, 'submitter_nam':submitter_name},
            cc_email
        )
        subm.save()

        if from_wg_or_sec == "wg" :
            return HttpResponsePermanentRedirect("https://datatracker.ietf.org/cgi-bin/wg/wg_init_rev_approval.cgi?from_auto_post=1&submission_id=%s" % (subm.submission_id, ))
        elif from_wg_or_sec == "sec" :
            return HttpResponsePermanentRedirect("https://datatracker.ietf.org/cgi-bin/secretariat/init_rev_approval.cgi?from_auto_post=1&submission_id=%s" % (subm.submission_id, ))
        else : # redirect to /idsubmit/status/<filename>
            return HttpResponsePermanentRedirect("/idsubmit/status/%s" % (subm.filename, ))

    else :
        # set the status_id to 10
        subm.status_id = 10

        # get submitter's name and email address
        (submitter_name, submitter_email) = subm.submitter.email()

        # get acronym from acronym where acronym_id=group_acronym_id
        # get id_approval_request_msg from announcement_template
        #id_approval_request_msg = announcement_template.id_approval_request_msg.replace("##submitter_name##", submitter_name).replace("##submitter_email##", submitter_email).replace("##filename##", subm.filename)
        # send a message to '<acronym>-chairs@tools.ietf.org' from 'IETF
        # I-D Submission Tool <idst-developers@ietf.org>,
        # subject:Initial Version Approval Request or <filename>
        toaddr = "%s-chairs@tools.ietf.org" % (str(subm.group), )
        send_mail(
            request,
            [toaddr],
            "IETF I-D Submission Tool <idst-developers@ietf.org>",
            "Initial Version Approval Request or %s" % (subm.filename, ),
            "idsubmit/email_init_rev_approval.txt",{'submitter_name':submitter_name,'submitter_email':submitter_email,'filename':subm.filename} 
        )

        subm.save()

        # redirect the page to /idsubmit/status/<submission_id>
        return HttpResponsePermanentRedirect("/idsubmit/status/%d" % (subm.submission_id, ))

MSG_CANCEL = """This message is to notify you that submission of an Internet-Draft, %(filename)s-%(revision)s, has just been cancelled by a user whose computer has an IP address of %(remote_ip)s.

The IETF Secretariat.
"""
SUBJECT_CANCEL = "Submission of %(filename)s-%(revision)s has been Cancelled"
FROM_EMAIL_CANCEL = "IETF I-D Submission Tool <idsubmission@ietf.org>"

def cancel_draft (request, submission_id) :
    """
    This view was ported from the cancel routine in
    'ietf/branch/legacy/idsubmit/status.cgi'.

    NOTE: The below commented parts will be removed after all the codes is verified.
    """

    # get submission
    submission = get_object_or_404(IdSubmissionDetail, pk=submission_id)
    if submission.status_id < 0 or submission.status_id > 100:
        return render("idsubmit/error.html", {'error_msg':'This document is not in valid state and cannot be canceled'}, context_instance=RequestContext(request))
    # rename the submitted document to new name with canceled tag.
    path_orig_sub = os.path.join(
        settings.STAGING_PATH,
        "%s-%s" % (submission.filename, submission.revision, ),
    )
    path_orig = os.path.join(
        settings.STAGING_PATH,
        "%s-%s.txt" % (submission.filename, submission.revision, ),
    )
    path_cancelled = os.path.join(
        settings.STAGING_PATH,
        "%s-%s-%s-cancelled.txt" % (submission.filename, submission.revision, submission.submission_id, ),
    )
    os.rename(path_orig, path_cancelled)

    # remove all sub document.
    for i in glob.glob("%s*" % path_orig_sub) :
        os.remove(i)
    # to notify 'cancel' to the submitter and authors.
    print submission.status_id
    if submission.status_id > 0 and submission.status_id < 100 :
        to_email = [i.email_address for i in TempIdAuthors.objects.filter(submission=submission) if i.email_address.strip()]
        kwargs = submission.__dict__.copy()
        kwargs.update(
            {
                "remote_ip" : request.META.get("REMOTE_ADDR")
            }
        )

        send_mail(
            request,
            to_email,
            FROM_EMAIL_CANCEL,
            SUBJECT_CANCEL % kwargs,
            "idsubmit/email_cancel.txt",{'submission':kwargs}
        )
    # if everything is OK, change the status_id to -4
    submission.status_id = -4
    submission.save()
    file_type_list = submission.file_type.split(',')
    return render(
        "idsubmit/status.html",
        {
            'object': submission,
            'authors': TempIdAuthors.objects.filter(
                    submission__exact=submission.submission_id),
            'status_msg': STATUS_CODE[submission.status_id],
            'file_type_list':file_type_list,
            'staging_url':settings.STAGING_URL
        }, context_instance=RequestContext(request)
    )


