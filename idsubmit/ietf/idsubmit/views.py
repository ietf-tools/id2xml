# Copyright The IETF Trust 2007, All Rights Reserved

import re, os, glob
from datetime import datetime, time, timedelta
import difflib

from django.shortcuts import render_to_response as render, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from django.conf import settings
from django.db.models import Q
from django.views.generic.list_detail import object_detail
from django.contrib.sites.models import Site
from models import IdSubmissionDetail, IdApprovedDetail, IdDates, SubmissionEnv
from ietf.idtracker.models import Acronym
from ietf.idsubmit.forms import IDUploadForm, SubmitterForm, AdjustForm, AuthorForm
from ietf.idsubmit.models import STATUS_CODE
from ietf.utils.mail import send_mail, send_mail_subj
from ietf.idsubmit.parser.draft_parser import DraftParser
from ietf.utils import normalize_draftname
from utils import FROM_EMAIL

# Wrappers around generic view to get a handle for {% url %}
def firsttwo(*args, **kwargs):
    return object_detail(*args, **kwargs)

def idnits(*args, **kwargs):
    return object_detail(*args, **kwargs)

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
    cut_off_time = subenv.cut_off_time
    first_cut_off_date = IdDates.objects.get(id=1).id_date
    first_cut_off_time = datetime.combine(first_cut_off_date, cut_off_time)
    first_cut_off_warning = first_cut_off_date - timedelta( days=subenv.cut_off_warn_days )
    second_cut_off_date = IdDates.objects.get(id=2).id_date
    second_cut_off_time = datetime.combine(second_cut_off_date, cut_off_time)
    ietf_monday_date = IdDates.objects.get(id=3).id_date
    context = { 'first_cut_off_time': first_cut_off_time,
                'second_cut_off_time': second_cut_off_time,
                'ietf_monday': datetime.combine(ietf_monday_date, time(0,0,0)) }
    submission = None


    if request.method == 'POST':

        # Commented out by [wiggins@concentricsky] on 1.1 update
        #post_data = request.POST.copy()
        #post_data.update(request.FILES)
        # A bug in the test client in 0.96 causes the 
        # fields to be named differently than outside test.
        #for ext in IDUploadForm.file_names.keys():
        #    if post_data.get(ext) == '' and \
        #       post_data.has_key(ext + "_file"):
        #        post_data[ext] = post_data[ext + "_file"]

        form = IDUploadForm(request.POST, request.FILES)
        if form.is_valid():
            #if not request.FILES['txt_file']['content-type'].startswith('text'):
            #    return render("idsubmit/error.html", {'error_msg':STATUS_CODE[101]}, context_instance=RequestContext(request))

            dp = DraftParser(form.get_content('txt_file'))
            if now >= first_cut_off_time and now < second_cut_off_time and dp.revision == '00':
                context['form'] = IDUploadForm()
                context['cutoff_msg'] = "first_second"
                return render ("idsubmit/upload.html", context, context_instance=RequestContext(request))

            dp.set_remote_ip(request.META.get('REMOTE_ADDR', ''))
            threshold_msg = dp.check_dos_threshold()
            if threshold_msg:
                return render("idsubmit/error.html", {'error_msg':threshold_msg}, context_instance=RequestContext(request))

            (ietfgroup,invalid_group) = dp.get_group_id()
            if invalid_group:
                return render("idsubmit/error.html",{'error_msg':'Invalid WG: %s' % invalid_group}, context_instance=RequestContext(request))
            if not ietfgroup:
                return render("idsubmit/error.html",{'error_msg':'Failed to determine IETF WG from filename, %s' % submission.filename}, context_instance=RequestContext(request))

            meta_data = dp.get_meta_data_fields()
            submission = IdSubmissionDetail.objects.create(**meta_data)
            # Display critical error message
            if submission.status_id >= 100 and submission.status_id < 200:
                return render("idsubmit/error.html",{'error_msg':STATUS_CODE[submission.status_id]}, context_instance=RequestContext(request))
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
            idnits_msg = dp.check_idnits(file_path)
            if type(idnits_msg) is dict:
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
            authors = dp.get_author_list(dp.get_authors_info())
            for author in authors:
                submission.authors.create(**author)

            previous_submissions = IdSubmissionDetail.objects.filter(title=submission.title).exclude(revision=submission.revision).order_by('-revision')
            if len(previous_submissions) > 0:
                previous_submission = previous_submissions[0]
            else:
                previous_submission = None

            return render("idsubmit/validate.html",
                {'submission'        : submission,
                 'meta_data_errors' : dp.meta_data_errors,
                 'submitter_form'   : SubmitterForm(),
                 'idnits_result'   : idnits_result,
                 'staging_url'      : settings.STAGING_URL,
                 'previous_submission': previous_submission,
                }, context_instance=RequestContext(request))
        else:
            return render ("idsubmit/upload.html",{'form':form}, context_instance=RequestContext(request))
    else:
        if now.date() >= first_cut_off_warning and now < first_cut_off_time:
            # Warn of upcoming -00 deadline
            context['cutoff_msg'] = "first_warning"
        elif now >= first_cut_off_time and now < second_cut_off_time:
            # No more -00 submission
            context['cutoff_msg'] = "first_second"
            if now.date() == second_cut_off_date:
                context['cutoff_msg'] = "second_ietf"
        elif now >= second_cut_off_time and now.date() < ietf_monday_date: 
            # complete shut down of tool
            context['date_check_err_msg'] = "second_ietf"
            return render("idsubmit/error.html", context, context_instance=RequestContext(request))
        context['form'] = IDUploadForm()
    return render ("idsubmit/upload.html", context, context_instance=RequestContext(request))

def adjust_form(request, submission_id):
    submission = get_object_or_404(IdSubmissionDetail, pk=submission_id)
    if submission.status_id < 0 or (submission.status_id >= 100 and submission.status_id < 200):
        return render("idsubmit/error.html",{'error_msg':"No active submission found for submission id %s" % submission_id}, context_instance=RequestContext(request))
    if request.method == 'POST':
        author_forms = []
        author_form_num = 1
        all_authors_valid = True
        while request.POST.has_key('a%d-first_name' % (author_form_num)):
            f = AuthorForm( request.POST, prefix='a%d' % author_form_num )
            author_form_num += 1
            if f.is_valid() == False:
                all_authors_valid = False
            author_forms.append(f)
        form = AdjustForm(request.POST)
        form.submission = submission
        submitter_form = SubmitterForm(request.POST)

        if form.is_valid() and submitter_form.is_valid() and all_authors_valid: # Proceed to manual post request process
            # Delete and recreate the authors list.
            submission.authors.all().delete()
            cnt = 1
            for aform in author_forms:
                # Delete this author (or empty additional author)
                if aform.clean_data['email_address'] == '':
                    continue
                submission.authors.create(
                    first_name= aform.clean_data['first_name'],
                    last_name = aform.clean_data['last_name'],
                    email_address = aform.clean_data['email_address'],
                    author_order = cnt,
                )
                cnt = cnt + 1
            submitter_form.save(submission)
            #XXX submitter_form sets status to 4 or 205.
            # We override that here since it's really manual
            # post requested.
            submission.status_id=5
            form.save()
            cc_list = set([author.email() for author in submission.authors.all()])
            cc_list.add( submission.submitter_email() )
            send_mail_subj(request,'internet-drafts@ietf.org',
                FROM_EMAIL, "idsubmit/email_manual_post_subject.txt",
                "idsubmit/email_manual_post.txt",
                {'submission':submission,
                 'file_url': os.path.join(settings.STAGING_URL,"%s-%s.txt" % (submission.filename, submission.revision)),
                 'tracker_url': "%s%s" % (request.META['HTTP_HOST'], submission.get_absolute_url())}, cc_list
            )
            return HttpResponseRedirect(submission.get_absolute_url())
    else:
        # Supply validation errors, e.g., expected version
        form = AdjustForm( submission.__dict__ )
        submitter = None
        if submission.submitter:
            submitter = {
                    'fname': submission.submitter.first_name,
                    'lname': submission.submitter.last_name,
                    'submitter_email': submission.submitter_email()[1],
                }
        submitter_form = SubmitterForm( submitter )
        author_forms = []
        anum = 1
        for author in list(submission.authors.all()) + [None, None]:
            if author:
                initial = author.__dict__
            else:
                initial = None
            author_forms.append( AuthorForm( initial=initial, prefix='a%d' % anum ) )
            anum += 1
    return render("idsubmit/adjust.html",{'form':form,
        'submitter_form':submitter_form,
        'author_forms':author_forms,
        'submission':submission,
        'staging_url':settings.STAGING_URL,
        }, context_instance=RequestContext(request))

def draft_status(request, queryset, slug=None):
    submission = None
    if 'passed_filename' in request.GET: # Search Result
        slug = request.GET['passed_filename']
    if not slug:
        return direct_to_template(request,'idsubmit/draft_search.html')
    elif re.match("\d+$", slug) : # if submission_id
        submission = get_object_or_404(IdSubmissionDetail, pk=slug)
        if submission.status_id < 200 and submission.status_id >= 100:
            return render("idsubmit/error.html",{'error_msg':"No valid history found for submission id %s" % slug}, context_instance=RequestContext(request))
    elif re.match('draft-', slug):
        # if submission name
        subm_name = normalize_draftname(slug)
        # Find a submission with:
        # (status_id > 0 and status_id < 100) or (status_id > 200)
        # which is in-progress or has a correctable meta-data error
        submissions = queryset.filter((Q(status_id__gt=0) & Q(status_id__lt=100)) | Q(status_id__gt=200), filename=subm_name).order_by('-submission_id') 

        if submissions.count() > 0:
            submission = submissions[0]
        else:
            return render("idsubmit/error.html",{'error_msg':"No valid history found for %s" % subm_name}, context_instance=RequestContext(request))
    else:
        return render("idsubmit/error.html",{'error_msg':"Unknown request"}, context_instance=RequestContext(request))

    if submission.status_id > 0 and submission.status_id < 100 :
        # Note: this tool never sets status_id to 2.
        if submission.status_id == 2: #display validate.html
            meta_data_errors = {}
            return render("idsubmit/validate.html",
                {'submission'        : submission,
                 'submitter_form'   : SubmitterForm({'lname':'','fname':'','submitter_email':''}),
                 'staging_url'      : settings.STAGING_URL,           
                 'meta_data_errors' : meta_data_errors,
                 'file_type_list'  : submission.file_type.split(',')
                }, context_instance=RequestContext(request))
    return render(
        "idsubmit/status.html",
        {
            'object': submission,
            'staging_url': settings.STAGING_URL,
        }, context_instance=RequestContext(request)
    )

def trigger_auto_post(request,submission_id):
    submission = get_object_or_404(IdSubmissionDetail,pk=submission_id)
    msg = ''
    submitterForm = SubmitterForm(request.POST)
    if submitterForm.is_valid():
        submitterForm.save(submission)
        if submission.status_id > 0 and submission.status_id < 100:
            send_mail(request, [submission.submitter_email()], \
                    FROM_EMAIL, \
                    "I-D Submitter Authentication for %s" % submission.filename, \
                    "idsubmit/email_submitter_auth.txt", {'site':Site.objects.get_current(), 'submission_id':submission_id, 'auth_key':submission.auth_key}, toUser=True)            
        return HttpResponseRedirect(submission.get_absolute_url())
    else:
        meta_data_errors = {}
        return render("idsubmit/validate.html",
            {'submission'        : submission,
             'submitter_form'   : submitterForm,
             'staging_url'      : settings.STAGING_URL,
             'meta_data_errors' : meta_data_errors,
            }, context_instance=RequestContext(request))

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

    try :
        approved_status = IdApprovedDetail.objects.get(filename=submission.filename).approved_status
    except IdApprovedDetail.DoesNotExist :
        approved_status = None

    if approved_status == 1 or submission.revision != "00" or submission.group_id == Acronym.NONE :
        try:
            submission.approved()
        except IdSubmissionDetail.ApprovalError, e:
            return render("idsubmit/error.html",{'error_msg':e}, context_instance=RequestContext(request))

    else :
        submission.status_id = 10

        # get submitter's name and email address
        (submitter_name, submitter_email) = submission.submitter.email()

        toaddr = "%s-chairs@tools.ietf.org" % (str(submission.group), )
        send_mail(
            request,
            [toaddr],
            FROM_EMAIL,
            "Initial Version Approval Request for %s" % (submission.filename, ),
            "idsubmit/email_init_rev_approval.txt",{'submitter_name':submitter_name,'submitter_email':submitter_email,'filename':submission.filename,'site':Site.objects.get_current()}
        )

        submission.save()

    # redirect the page to /idsubmit/status/<submission_id>
    return HttpResponseRedirect(submission.get_absolute_url())

def cancel_draft (request, submission_id):
    # get submission
    submission = get_object_or_404(IdSubmissionDetail, pk=submission_id)
    if submission.status_id < 0:
        return render("idsubmit/error.html", {'error_msg':'This document is not in valid state and cannot be canceled', 'filename':submission.filename}, context_instance=RequestContext(request))
    # delete the document(s)
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
    try:
        os.rename(path_orig, path_cancelled)
    except OSError:
        # Maybe the file got garbage-collected already.
        pass

    # remove all sub document.
    for i in glob.glob("%s.*" % path_orig_sub):
        os.remove(i)
    # to notify 'cancel' to the submitter and authors.
    if submission.status_id > 0 and submission.status_id < 100 :
        to_email = [i.email() for i in submission.authors.all() if i.email_address.strip()]

        send_mail_subj(
            request,
            to_email,
            FROM_EMAIL,
            "idsubmit/email_cancel_subject.txt",
            "idsubmit/email_cancel.txt",{ 'submission': submission,
                'remote_ip' : request.META.get("REMOTE_ADDR") },
            toUser=True
        )
    # if everything is OK, change the status_id to -4
    submission.status_id = -4
    submission.save()
    return render(
        "idsubmit/status.html",
        {
            'object': submission,
            'staging_url': settings.STAGING_URL,
        }, context_instance=RequestContext(request)
    )

def submission_diff(request, submission_id, previous_id):
    submission = IdSubmissionDetail.objects.get(pk=submission_id)
    previous = IdSubmissionDetail.objects.get(pk=previous_id)

    submission_name = '%s-%s.txt' % (submission.filename, submission.revision)
    submission_path = os.path.join(settings.STAGING_PATH, submission_name)
    submission_txt = open(submission_path).readlines()

    previous_name = '%s-%s.txt' % (previous.filename, previous.revision)
    previous_path = os.path.join(settings.STAGING_PATH, previous_name)
    previous_txt = open(previous_path).readlines()

    diff = list( difflib.unified_diff(previous_txt, submission_txt, previous_name, submission_name) )
    return render(
        "idsubmit/diff.html",
        {
            'submission': submission,
            'previous': previous,
            'diff': diff,
        }, context_instance=RequestContext(request)
    )
