# Copyright The IETF Trust 2007, All Rights Reserved

import re, os, glob
from datetime import datetime, date, time

from django.shortcuts import render_to_response as render, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core.exceptions import ObjectDoesNotExist as ExceptionDoesNotExist
from django.http import HttpResponseRedirect
from django.http import HttpResponsePermanentRedirect
from django.views.generic.simple import direct_to_template
from django.conf import settings
from models import IdSubmissionDetail, TempIdAuthors, IdApprovedDetail, IdDates, SubmissionEnv
from ietf.idtracker.models import IETFWG, InternetDraft, EmailAddress, IDAuthor, IDInternal, DocumentComment, PersonOrOrgInfo
from ietf.announcements.models import ScheduledAnnouncement
from ietf.idsubmit.forms import IDUploadForm, SubmitterForm, AdjustForm
from ietf.idsubmit.models import STATUS_CODE
from ietf.utils.mail import send_mail
from django.core.mail import BadHeaderError
from ietf.idsubmit.parser.draft_parser import DraftParser
from ietf.utils import normalize_draftname
import subprocess

def check_setting(request):
    error_str = []
    try:
        checking = settings.TARGET_PATH_FTP1
    except:
        error_str.append("Not Found: Remote path to FTP server 1, TARGET_PATH_FTP1")
    try:
        checking = settings.TARGET_PATH_WEB1
    except:
        error_str.append("Not Found: Remote WEB server 1, TARGET_PATH_WEB1")
    try:
        checking = settings.SSH_KEY_PATH
    except:
        error_str.append("Not Found: Path to ssh key, SSH_KEY_PATH")
    try:
        checking = settings.STAGING_PATH
    except:
        error_str.append("Not Found: Path to staging location, STAGING_PATH")
    try:
        checking = settings.STAGING_URL
    except:
        error_str.append("Not Found: URL of staging location, STAGING_URL")
    if error_str:
        if settings.SERVER_MODE == 'production':
            error_msg = "Application has not been set up properly. Please use the email address below to report this problem"
        else:
            error_msg = '<br>'.join(error_str)
        return error_msg
    return False

def file_upload(request):
    error_msg = check_setting(request)
    if error_msg:
        return render("idsubmit/error.html", {'error_msg':error_msg, 'critical_error':True}, context_instance=RequestContext(request))
    now = datetime.now()
    subenv = SubmissionEnv.objects.all()[0]
    cut_off_time = time(subenv.cut_off_time,0,0)
    first_cut_off_date = IdDates.objects.get(id=1).id_date
    first_cut_off_time=datetime.combine(first_cut_off_date, cut_off_time)
    second_cut_off_date = IdDates.objects.get(id=2).id_date
    second_cut_off_time=datetime.combine(second_cut_off_date, cut_off_time)
    ietf_monday_date = IdDates.objects.get(id=3).id_date
    id_date_var = { 'first_cut_off_date' : first_cut_off_date, 'second_cut_off_date' : second_cut_off_date, 'ietf_monday' : ietf_monday_date, 'cut_off_time': subenv.cut_off_time}
    submission = None
    if request.POST:

        post_data = request.POST.copy()
        post_data.update(request.FILES)

        form = IDUploadForm(post_data)
        if form.is_bound and form.is_valid():
            if not request.FILES['txt_file']['content-type'].startswith('text'):
                return render("idsubmit/error.html", {'error_msg':STATUS_CODE[101]}, context_instance=RequestContext(request))

            dp = DraftParser(form.get_content('txt_file'))
            if now >= first_cut_off_time and now < second_cut_off_time and dp.revision == '00':
                id_date_var['form'] = IDUploadForm()
                id_date_var['cutoff_msg'] = "first_second"
                id_date_var['cut_off_time'] = subenv.cut_off_time
                return render ("idsubmit/upload.html", id_date_var, context_instance=RequestContext(request))
            dp.set_remote_ip(request.META.get('REMOTE_ADDR'))
            threshold_msg = dp.check_dos_threshold()
            if threshold_msg:
                return render("idsubmit/error.html", {'error_msg':threshold_msg}, context_instance=RequestContext(request))
            meta_data = dp.get_meta_data_fields()
            submission = IdSubmissionDetail(**meta_data)
            try:
                submission.save()
            except:
                return  render("idsubmit/error.html", {'error_msg':"Data Saving Error"}, context_instance=RequestContext(request))
            # Display critical error message
            if submission.status_id >= 100 and submission.status_id < 200:
                return render("idsubmit/error.html",{'error_msg':STATUS_CODE[submission.status_id]}, context_instance=RequestContext(request))
            (ietfgroup,invalid_group) = dp.get_group_id()
            if invalid_group:
                return render("idsubmit/error.html",{'error_msg':'Invalid WG: %s' % invalid_group}, context_instance=RequestContext(request))
            if not ietfgroup:
                return render("idsubmit/error.html",{'error_msg':'Failed to determine IETF WG from filename, %s' % submission.filename}, context_instance=RequestContext(request))
            submission.group = ietfgroup
            submission.save()
            # Checking existing submission
            if IdSubmissionDetail.objects.filter(filename__exact=dp.filename, status_id__gt=0,status_id__lt=100).exclude(submission_id=submission.submission_id).count():
                submission.status_id = 103
                submission.save()
                return render("idsubmit/error.html", {'error_msg':STATUS_CODE[103],'filename':submission.filename}, context_instance=RequestContext(request))
            # All the critical errors are checked. It's ok to save the file now
            if not form.save(submission.filename, submission.revision):
                return render("idsubmit/error.html", {'error_msg':'There was an error on saving documents'}, context_instance=RequestContext(request))
            submission.set_file_type(form.file_ext_list)
            file_path = "%s-%s.txt" % (os.path.join(settings.STAGING_PATH,dp.filename), dp.revision)
            #idnits checking
            #print "before checking idnits..."
            idnits_msg = dp.check_idnits(file_path)
            #print "after checking idnits..."
            if type(idnits_msg).__name__=='dict':
                submission.idnits_message = idnits_msg['message']
                if idnits_msg['error'] > 0:
                    idnits_result = True
                    submission.status_id = 203
                    submission.warning_message = "%s\n%s" % ("<li>This document has " + str(idnits_msg['error']) + " idnits error(s)</li>", submission.warning_message)
                else:
                    idnits_result = False
            else:
                return render("idsubmit/error.html", {'error_msg':idnits_msg}, context_instance=RequestContext(request))
            submission.save()
            authors_info = dp.get_author_detailInfo(dp.get_authors_info(),submission.submission_id)
            for author_dict in authors_info:
                author = TempIdAuthors(**author_dict)
                try:
                    author.save()
                except :
                    return  render("idsubmit/error.html", {'error_msg':"Authors Data Saving Error"}, context_instance=RequestContext(request))

            return render("idsubmit/validate.html",
                {'submission'        : submission, 
                 'meta_data_errors' : dp.meta_data_errors,
                 'authors_info'     : authors_info,
                 'submitter_form'   : SubmitterForm(),
                 'idnits_result'   : idnits_result,
                 'file_type_list'  : submission.get_file_type_list(),
                 'staging_url'      : settings.STAGING_URL,
                }, context_instance=RequestContext(request))
        else:
            return render ("idsubmit/upload.html",{'form':form}, context_instance=RequestContext(request))
    else:
        if now >= first_cut_off_time and now < second_cut_off_time:
        # No more 00 submission
            id_date_var['form'] = IDUploadForm()
            id_date_var['cutoff_msg'] = "first_second"
            if now.date() == second_cut_off_date:
                id_date_var['cutoff_msg'] = "second_ietf"
            return render ("idsubmit/upload.html", id_date_var, context_instance=RequestContext(request))
        elif now >= second_cut_off_time and now.date() < ietf_monday_date: 
        #complete shut down of tool
            id_date_var['date_check_err_msg'] = "second_ietf"
            return render("idsubmit/error.html", id_date_var, context_instance=RequestContext(request))
        form = IDUploadForm()
    return render ("idsubmit/upload.html",{'form':form}, context_instance=RequestContext(request))

def adjust_form(request, submission_id,queryset):
    submission = get_object_or_404(IdSubmissionDetail, pk=submission_id)
    if submission.status_id < 0 or (submission.status_id >= 100 and submission.status_id < 200):
        return render("idsubmit/error.html",{'error_msg':"No valid history found for submission id %s" % submission_id}, context_instance=RequestContext(request))
    args = request.POST.copy()
    if args.get('from_validation'):
        args['submission_id'] = submission_id
        args['title'] = submission.title
        args['revision']=submission.revision
        args['creation_date']=submission.creation_date
        args['txt_page_count']=submission.txt_page_count
        args['abstract']=submission.abstract
        args['comment_to_sec']=submission.comment_to_sec
        if submission.submitter:
            args['fname'] = submission.submitter.first_name
            args['lname'] = submission.submitter.last_name
            args['submitter_email'] = \
                submission.submitter.emailaddress_set.get(priority=1).address
    file_type_list = submission.file_type.split(',')
    # process temp authors
    form = AdjustForm(args)
    authors_first_name = request.POST.getlist('author_first_name')
    authors_last_name  = request.POST.getlist('author_last_name')
    authors_email      = request.POST.getlist('author_email')
    if authors_email:
        TempIdAuthors.objects.filter(submission=submission).delete()
        authors = []
        cnt = 0 
        for email in authors_email:
            if email:
                tempidauthors = TempIdAuthors(
                    first_name=authors_first_name[cnt],
                    last_name = authors_last_name[cnt],
                    email_address = email,
                    author_order = cnt+1,
                    submission = submission,
                )
                tempidauthors.save()
            cnt = cnt + 1
    if form.is_valid(): # Proceed to manual post request process
        submission.status_id=5
        if form.save(submission, param=args):
            from_email = 'ID Submission Tool <idsubmission@ietf.org>'
            subject = 'Manual Posting Requested for %s-%s' % (submission.filename, submission.revision)
            cc_list = list()
            authors_list = TempIdAuthors.objects.filter(submission=submission).exclude(email_address=args['submitter_email'])
            for author_info in authors_list:
                cc_list.append(author_info.email_address)
            try:
                send_mail(request,[args['submitter_email']],
                    from_email,subject,
                    "idsubmit/email_manual_post.txt",
                    {'submission':submission,
                     'authors_list':TempIdAuthors.objects.filter(submission=submission),
                     'file_url': os.path.join(settings.STAGING_URL,"%s-%s.txt" % (submission.filename, submission.revision)),
                     'tracker_url': "%s%s" % (request.META['HTTP_HOST'], submission.get_absolute_url())}, cc_list
                )
            except BadHeaderError:
                return render("idsubmit/error.html",{'error_msg':"Invalid header found."}, context_instance=RequestContext(request))
            return HttpResponseRedirect(submission.get_absolute_url())
        else:
            return render("idsubmit/error.html",{'error_msg':"Error occurred while processing Manual Post request."}, context_instance=RequestContext(request))

    else: # redisplay the form
        return render ("idsubmit/adjust.html",{'form':form,
            'submission':submission,
            'submission_id':submission_id,
            'authors':TempIdAuthors.objects.filter(submission__exact=submission_id).order_by('author_order'),
            'staging_url':settings.STAGING_URL,
            'file_type_list':file_type_list,
            }, context_instance=RequestContext(request))
def draft_status(request, queryset, slug=None):
    submission = None
    if 'passed_filename' in request.GET: # Search Result
        passed_filename = request.GET['passed_filename']
        id_list = queryset.filter(filename=passed_filename, status_id__gt =  -3, status_id__lt = 100).order_by('-submission_id')
        if not id_list.count():
            return render("idsubmit/error.html",{'error_msg':"No valid history found for %s" % passed_filename}, context_instance=RequestContext(request))
        submission = id_list[0]
    elif not slug:
        return direct_to_template(request,'idsubmit/draft_search.html')
    elif re.compile("^\d+$").findall(slug) : # if submission_id
        submission = get_object_or_404(IdSubmissionDetail, pk=slug)
        if submission.status_id < 200 and submission.status_id >= 100:
            return render("idsubmit/error.html",{'error_msg':"No valid history found for submission id %s" % slug}, context_instance=RequestContext(request))
    elif re.compile('^(draft-.+)').findall(slug) :
        # if submission name
        subm_name = normalize_draftname(slug)
        submissions = queryset.filter(filename__exact=subm_name,status_id__gt=-3, status_id__lt=100).order_by('-submission_id') 

        if submissions.count() > 0 :
            submission = submissions[0]
        else:
            return render("idsubmit/error.html",{'error_msg':"No valid history found for %s" % subm_name}, context_instance=RequestContext(request))
    else:
        return render("idsubmit/error.html",{'error_msg':"Unknown request"}, context_instance=RequestContext(request))

    if submission.status_id > 200:
        meta_error = 1
    else:
        meta_error = 0
    if submission.status_id > 0 and submission.status_id < 100 :
        can_be_canceled = 1
        if submission.status_id == 2: #display validate.html
            meta_data_errors = {}
            return render("idsubmit/validate.html",
                {'submission'        : submission,
                 'authors_info'     : TempIdAuthors.objects.filter(submission__exact=submission.submission_id).order_by('author_order'),
                 'submitter_form'   : SubmitterForm({'lname':'','fname':'','submitter_email':''}),
                 'staging_url'      : settings.STAGING_URL,           
                 'meta_data_errors' : meta_data_errors,
                 'file_type_list'  : submission.file_type.split(',')
                }, context_instance=RequestContext(request))
    else:
        can_be_canceled = 0
    return render(
        "idsubmit/status.html",
        {
            'object': submission,
            'authors': TempIdAuthors.objects.filter(
                    submission__exact=submission.submission_id).order_by('author_order'),
            'status_msg': STATUS_CODE[submission.status_id],
            'staging_url':settings.STAGING_URL,
            'meta_error': meta_error,
            'file_type_list':submission.get_file_type_list(),
            'can_be_canceled': can_be_canceled,
            'posted': submission.status_id == -1 or submission.status_id == -2,
        }, context_instance=RequestContext(request)
    )

def trigger_auto_post(request,submission_id,queryset):
    args = request.POST.copy()
    submission = get_object_or_404(IdSubmissionDetail,pk=submission_id)
    msg = ''
    submitterForm = SubmitterForm(args)
    if submitterForm.is_bound and submitterForm.is_valid():
        submitter = submitterForm.save(submission)
        if submission.status_id > 0 and submission.status_id < 100:
            send_mail(request, [submitter.email()], \
                    "IETF I-D Submission Tool <idsubmission@ietf.org>", \
                    "I-D Submitter Authentication for %s" % submission.filename, \
                    "idsubmit/email_submitter_auth.txt", {'submission_id':submission_id, 'auth_key':submission.auth_key,'url':request.META['HTTP_HOST']})            
        return HttpResponseRedirect(submission.get_absolute_url())
    else:
        meta_data_errors = {}
        return render("idsubmit/validate.html",
            {'submission'        : submission,
             'authors_info'     : TempIdAuthors.objects.filter(submission__exact=submission.submission_id).order_by('author_order'),
             'submitter_form'   : SubmitterForm(args),
             'staging_url'      : settings.STAGING_URL,
             'meta_data_errors' : meta_data_errors,
             'file_type_list'  : submission.file_type.split(','),
            }, context_instance=RequestContext(request))
def sync_docs (request, submission) :
    # sync docs with remote server.
    command = "sh %(BASE_DIR)s/idsubmit/sync_docs.sh --staging_path=%(staging_path)s --revision=%(revision)s --filename=%(filename)s --ssh_key_path=%(ssh_key_path)s --remote_web1=%(remote_web1)s --remote_ftp1=%(remote_ftp1)s" % {
        "filename" : submission.filename,
        "revision": submission.revision,
        "staging_path" : settings.STAGING_PATH,
        "BASE_DIR" : settings.BASE_DIR,
        "ssh_key_path" : settings.SSH_KEY_PATH,
        "remote_web1" : settings.TARGET_PATH_WEB1,
        "remote_ftp1" : settings.TARGET_PATH_FTP1,
    }
    # add options for extra web2 and ftp2 path
    try:
        command += " --remote_web2=%s" % settings.TARGET_PATH_WEB2
    except:
        pass
    try:
        command += " --remote_ftp2=%s" % settings.TARGET_PATH_FTP2
    except:
        pass
    try :
        p = subprocess.Popen([command], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stderr = p.stderr
        if stderr:
            errmsg = []
            for msg in stderr.readlines():
                if not 'is not a tty' in msg and not msg in errmsg:
                    errmsg.append(msg)
            if errmsg:
                errmsg_html = '<br>\n'.join(errmsg)
                return False, errmsg_html
        #os.system(command)
    except:
        return False, "<li>Failed to copy document to web server</li>"
    return True, None


def verify_key(request, submission_id, auth_key, from_wg_or_sec=None):
    submission = get_object_or_404(IdSubmissionDetail, pk=submission_id)
    now = datetime.now()
    if submission.auth_key != auth_key : # check 'auth_key'
        return render("idsubmit/error.html",{'error_msg':"Auth key is invalid"}, context_instance=RequestContext(request))
    if submission.status_id not in (4, 11, ) :
        # return status value 107, "Error - Draft is not in an appropriate
        # status for the requested page"
        return render("idsubmit/error.html",{'error_msg':STATUS_CODE[107]}, context_instance=RequestContext(request))

    if submission.sub_email_priority is None :
        submission.sub_email_priority = 1

    approved_status = None
    try :
        approved_status = IdApprovedDetail.objects.get(filename=submission.filename).approved_status
    except ExceptionDoesNotExist :
        pass

    if approved_status == 1 or submission.revision != "00" or submission.group_id == 1027 :

        # Copy Document(s) to production servers:
        try :
            (result, msg) = sync_docs(request, submission)
            if not result:
                return render("idsubmit/error.html",{'error_msg':msg}, context_instance=RequestContext(request))
        except OSError :
            return render("idsubmit/error.html",{'error_msg':"There was a problem occurred while posting the document to the public server"}, context_instance=RequestContext(request))
        # populate table

        if submission.revision == "00" :
            # if the draft file alreay existed, error will be occured.
            if InternetDraft.objects.filter(filename__exact=submission.filename).count() > 0 :
                return render("idsubmit/error.html",{'error_msg':"00 revision of this document already exists"}, context_instance=RequestContext(request))

            internet_draft = InternetDraft(
                title=submission.title,
                id_document_key=submission.title.upper(),
                group=submission.group,
                filename=submission.filename,
                revision=submission.revision,
                revision_date=submission.submission_date,
                file_type=submission.file_type,
                txt_page_count=submission.txt_page_count,
                abstract=submission.abstract,
                status_id=1,
                intended_status_id=8,
                start_date=now,
                last_modified_date=now,
                review_by_rfc_editor=False,
                expired_tombstone=False,
            )

            internet_draft.save()
        else : # Existing version; update the existing record using new values
            try :
                internet_draft = InternetDraft.objects.get(filename=submission.filename)
            except ExceptionDoesNotExist :
                return render("idsubmit/error.html",{'error_msg':"The previous submission of this document cannot be found"}, context_instance=RequestContext(request))
            else :
                try :
                    IDAuthor.objects.filter(document=internet_draft).delete()
                    EmailAddress.objects.filter(priority=internet_draft.id_document_tag).delete()
                    kwargs = submission.__dict__.copy()
                    kwargs.update({"revision_date" : submission.submission_date, "last_modified_date" : now })
                    internet_draft.title=submission.title
                    internet_draft.revision=submission.revision
                    internet_draft.revision_date=submission.submission_date
                    internet_draft.file_type=submission.file_type
                    internet_draft.txt_page_count=submission.txt_page_count
                    internet_draft.abstract=submission.abstract
                    internet_draft.last_modified_date=now
                    internet_draft.save()
                except :
                    return render("idsubmit/error.html",{'error_msg':"There was a problem updating the Internet-Drafts database"}, context_instance=RequestContext(request))

        authors_names = list()
        for author_info in TempIdAuthors.objects.filter(submission=submission) :
            email_address = EmailAddress.objects.filter(address=author_info.email_address)
            if email_address.count() > 0 :
                person_or_org = email_address[0].person_or_org
            else :
                person_or_org = PersonOrOrgInfo(
                    first_name=author_info.first_name,
                    last_name=author_info.last_name,
                    date_modified=now,
                    modified_by="IDST",
                    created_by="IDST",
                )
                person_or_org.save()

                EmailAddress(
                    person_or_org=person_or_org,
                    type="INET",
                    priority=1,
                    address=author_info.email_address,
                ).save()

            IDAuthor(
                document=internet_draft,
                person=person_or_org,
            ).save()

            EmailAddress(
                person_or_org=person_or_org,
                type="I-D",
                priority=internet_draft.id_document_tag,
                address=author_info.email_address,
            ).save()

            # gathering author's names
            authors_names.append("%s. %s" % (author_info.first_name, author_info.last_name))

        submission.status_id = 7
        submission.save()

        # Schedule I-D Announcement:
        cc_val = ""
        wgMail = str()
        # if group_acronym_id is 'Individual Submissions'
        if submission.group_id != 1027 :
            #submission.group.name
            try:
                cc_val = IETFWG.objects.get(pk=submission.group_id).email_address
            except:
                cc_val = ''
            wgMail = "\nThis draft is a work item of the %(group_name)s Working Group of the IETF.\n" % {"group_name" : submission.group.name}
        body = render_to_string("idsubmit/i-d_action.txt",
            {'submission':submission,
             'authors':", ".join(authors_names),
             'current_date':now.strftime("%F"), 
             'current_time':now.strftime("%T"),
             'wgMail':wgMail}, context_instance=RequestContext(request))
        scheduled_announcement = ScheduledAnnouncement(
            mail_sent =    False,
            scheduled_by =     "IDST",
            to_be_sent_date =  now,
            to_be_sent_time =  "00:00",
            scheduled_date =   now,
            scheduled_time =   now,
            subject =      "I-D Action:%s-%s.txt" % (submission.filename,submission.revision),
            to_val =       "i-d-announce@ietf.org",
            from_val =     "Internet-Drafts@ietf.org",
            cc_val =       cc_val,
            body =         body,
            content_type =     "Multipart/Mixed; Boundary=\"NextPart\"",
        ).save()

        submission.status_id = 8
        submission.save()
        temp_id_document_tag = InternetDraft.objects.get(filename=submission.filename).id_document_tag
        if IDInternal.objects.filter(draft=temp_id_document_tag).filter(rfc_flag=0).extra(where=["cur_state < 100", ]) :
            # Schedule New Version Notification:

            # Add comment to ID Tracker
            document_comments = DocumentComment(
                document_id =  temp_id_document_tag,
                rfc_flag =     0,
                public_flag =  1,
                date = now,
                time = now,
                version =      submission.revision,
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
                    version =      submission.revision,
                    comment_text = msg,
                ).save()

                id_internal.cur_sub_state_id = 2
                id_internal.prev_sub_state_id = 5
                id_internal.save()

            kwargs = submission.__dict__.copy()
            kwargs.update({"temp_id_document_tag" : temp_id_document_tag, })

            send_to = list()
            send_to.append(id_internal.state_change_notice_to)

            email_address = id_internal.job_owner.person.emailaddress_set.get(priority=1, type='INET').address
            if email_address not in send_to:
                send_to.append(email_address)
            discuss_positions = id_internal.ballot.positions.filter(ad__user_level = 1, discuss = 1)
            for p in discuss_positions:
                email_address = p.ad.person.emailaddress_set.get(priority=1, type='INET').address
                if email_address not in send_to:
                    send_to.append(email_address)
            scheduled_announcement = ScheduledAnnouncement(
                mail_sent = False,
                scheduled_by = "IDST",
                to_be_sent_date =  now,
                to_be_sent_time =  "00:00",
                scheduled_date =   now,
                scheduled_time =   now,
                subject = "New Version Notification - %(filename)s-%(revision)s.txt" % kwargs,
                to_val =  ",".join([str(eb) for eb in send_to if eb is not None]),
                from_val = "Internet-Drafts@ietf.org",
                cc_val =  cc_val,
                body =  render_to_string("idsubmit/new_version_notify.txt",{'submission':submission,'msg':msg}, context_instance=RequestContext(request)),
            ).save()

            submission.status_id = 9
            submission.save()

        # Notify All Authors:
        # <Please read auto_post.cgi, sub notify_all_authors>

        cc_email = list()
        if submission.group_id == 1027 :
            group_acronym = "Independent Submission"
        else :
            group_acronym = submission.group.name
            #removed cc'ing WG email address by request
            #cc_email.append(IETFWG.objects.get(group_acronym=submission.group).email_address)

        submission.comment_to_sec = submission.comment_to_sec and "\nComment:\n%s" % submission.comment_to_sec or ""

        (submitter_name, submitter_email, ) = submission.submitter.email()
        for author_info in TempIdAuthors.objects.filter(submission=submission).exclude(email_address=submitter_email) :
            if not author_info.email_address.strip() and submitter_email == author_info.email_address :
                continue

            if author_info.email_address not in cc_email :
                cc_email.append(author_info.email_address)

        to_email = submitter_email
        send_mail(
            request,
            to_email,
            "IETF I-D Submission Tool <idsubmission@ietf.org>",
            "New Version Notification for %s-%s" % (submission.filename,submission.revision),
            "idsubmit/email_posted_notice.txt", {'subm':submission, 'submitter_name':submitter_name},
            cc_email
        )
        submission.status_id = -1
        submission.save()
        # remove files.
        try :
            [os.remove(i) for i in glob.glob("%s-%s.*" % (os.path.join(settings.STAGING_PATH,submission.filename), submission.revision))]
        except :
            pass
        # redirect to wg chairs/secretariat tool if the document was just approved and posted
        if from_wg_or_sec == "wg" :
            return HttpResponsePermanentRedirect("http://%s/cgi-bin/wg/wg_init_rev_approval.cgi?from_auto_post=1&submission_id=%s" % (request.META['HTTP_HOST'], submission.submission_id, ))
        elif from_wg_or_sec == "sec" :
            return HttpResponsePermanentRedirect("http://%s/cgi-bin/secretariat/init_rev_approval.cgi?from_auto_post=1&submission_id=%s" % (request.META['HTTP_HOST'], submission.submission_id, ))
        else : # redirect to Status Page 
            return HttpResponsePermanentRedirect(submission.get_absolute_url())

    else :
        submission.status_id = 10

        # get submitter's name and email address
        (submitter_name, submitter_email) = submission.submitter.email()

        toaddr = "%s-chairs@tools.ietf.org" % (str(submission.group), )
        send_mail(
            request,
            [toaddr],
            "IETF I-D Submission Tool <idst-developers@ietf.org>",
            "Initial Version Approval Request for %s" % (submission.filename, ),
            "idsubmit/email_init_rev_approval.txt",{'submitter_name':submitter_name,'submitter_email':submitter_email,'filename':submission.filename, 'tracker_url':request.META['HTTP_HOST']} 
        )

        submission.save()

        # redirect the page to /idsubmit/status/<submission_id>
        return HttpResponsePermanentRedirect(submission.get_absolute_url())

SUBJECT_CANCEL = "Submission of %(filename)s-%(revision)s has been Cancelled"
FROM_EMAIL_CANCEL = "IETF I-D Submission Tool <idsubmission@ietf.org>"

def cancel_draft (request, submission_id) :
    # get submission
    submission = get_object_or_404(IdSubmissionDetail, pk=submission_id)
    if submission.status_id < 0:
        return render("idsubmit/error.html", {'error_msg':'This document is not in valid state and cannot be canceled'}, context_instance=RequestContext(request))
    # delete the document(s)
    path_orig_sub = os.path.join(
        settings.STAGING_PATH,
        "%s-%s" % (submission.filename, submission.revision, ),
    )
    #path_orig = os.path.join(
    #    settings.STAGING_PATH,
    #    "%s-%s.txt" % (submission.filename, submission.revision, ),
    #)
    #path_cancelled = os.path.join(
    #    settings.STAGING_PATH,
    #    "%s-%s-%s-cancelled.txt" % (submission.filename, submission.revision, submission.submission_id, ),
    #)
    #os.rename(path_orig, path_cancelled)

    # remove all sub document.
    for i in glob.glob("%s*" % path_orig_sub) :
        os.remove(i)
    # to notify 'cancel' to the submitter and authors.
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
            'authors': TempIdAuthors.objects.filter(submission__exact=submission.submission_id),
            'status_msg': STATUS_CODE[submission.status_id],
            'file_type_list':file_type_list,
            'staging_url':settings.STAGING_URL,
        }, context_instance=RequestContext(request)
    )


