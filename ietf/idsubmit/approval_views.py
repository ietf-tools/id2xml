# Copyright The IETF Trust 2007, All Rights Reserved

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from ietf.idsubmit.approval_forms import PreauthzForm, PickApprover, DRAFT_WG_RE
from ietf.idtracker.models import PersonOrOrgInfo, IETFWG
from ietf.utils.mail import send_mail_subj
from views import FROM_EMAIL
from models import IdApprovedDetail, IdSubmissionDetail
import re, datetime


"""\
This component implements a pre-approval tool for initial
Internet-Draft submissions.

This tool can either be acessed by WG chairs or ADs, in which case the
approved_by and recorded_by will be the same person_id.

An I-D can also be approved by the Secreteriat, in which case the
approved_by will be one of the chairs of the WG, and the recorded_by
will be the member of the Secreteriat.
"""

 
def group_approvers(group_name):
    """Return the list of people who have approval rights for the group_name"""
    try:
        group = IETFWG.objects.get(group_acronym__acronym=group_name)
    except IETFWG.DoesNotExist:
        return []
    approvers = []
    approvers += [ch.person for ch in group.wgchair_set.all()]
    approvers += [sec.person for sec in group.wgsecretary_set.all()]
    approvers += [ad.person for ad in group.area.area.areadirector_set.all()]

    return approvers

def is_secretariat(user):
    """Return True if the user is part of the Secreteriat group"""
    if user.groups.filter(name='Secretariat').count():
        return True
    else:
        return False

def approve_draft(request, filename, approver, person):
    """Add or update an approval for the filename draft"""
    try:
        a = IdApprovedDetail.objects.get(filename=filename)
    except IdApprovedDetail.DoesNotExist:
        a = IdApprovedDetail(filename=filename)
    a.approved_status = 1
    a.approved_person = person
    a.approved_date = datetime.date.today()
    a.recorded_py = approver
    a.save()

    # Find a submission object for this filename whose status is 10
    # ('Initial Version Approval Requested')
    try:
        submission = IdSubmissionDetail.objects.get(filename=filename,
                                status_id=10)
    except IdSubmissionDetail.DoesNotExist:
        submission = None
    if submission:
        submission.status = 11
        submission.save()
        send_mail_subj(request, [ submission.submitter_email() ],
                        FROM_EMAIL, "idsubmit/email_initial_version_subject.txt",
                        "idsubmit/email_initial_version.txt",
                        {'submission':submission,
                         'approver':person})
        try:
            submission.approved()
            submission_failed = False
        except IdSubmissionDetail.ApprovalError, e:
            submission_failed = e
    return render_to_response('idsubmit/approval_success.html', {'draft':filename,
                                            'submission':submission,
                                            'submission_failed':submission_failed})

def approval2(request):
    """ "front door" to the approval form with no prespecified draft """
    return approval(request, None)

@login_required
def approval(request, draft):
    """Main view for the page."""
    user = PersonOrOrgInfo.objects.from_django( request.user )
    if user is None:
        return fail(None, None, "Can't find your IETF user from your django user")
    pending_submissions = IdSubmissionDetail.objects.filter( status_id = 10 ).order_by( '-submission_date' )
    if request.method == 'POST' or draft:
        if request.method == 'POST':
            data = request.POST
        else:
            data = {'draft': draft}
        form = PreauthzForm(data)
        if form.is_valid():
            filename = form.clean_data['draft']
            # form validation has ensured that this will match
            m = re.search(DRAFT_WG_RE, filename)
            wg = m.group()
            approvers = group_approvers(wg)
            if not user in approvers:
                if is_secretariat(request.user):
                    if request.POST.has_key('approver'):
                        approver_form = PickApprover(approvers, request.POST)
                        if approver_form.is_valid():
                            approver = PersonOrOrgInfo.objects.get(pk=approver_form.clean_data['approver'])
                            return approve_draft(request, filename, user, approver)
                    else:
                        approver_form = PickApprover(approvers=approvers)
                    return render_to_response('idsubmit/approval_pick.html',
                                                 {'form':form,
                                                  'approver_form':approver_form})
                return fail(form, user, 'You are not an approver for this WG')
            else:
                return approve_draft(request, filename, user, user)
    else:
        form = PreauthzForm(initial={'draft':'draft-ietf-'})
    return render_to_response('idsubmit/approval.html', {'form':form, 
                                                         'user':user,
                                                         'pending_submissions':pending_submissions})

def fail(form, user, message=""):
    """This view sends a form with an embedded error message"""
    return render_to_response('idsubmit/approval.html', {'form':form,
                                                   'user':user,
                                                   'errors':True,
                                                   'message':message})
