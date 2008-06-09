# Copyright The IETF Trust 2007, All Rights Reserved

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.http import HttpResponse
from ietf.idsubmit.approval_forms import PreauthzForm
from ietf.idtracker.models import PersonOrOrgInfo, IETFWG
import string, re


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

def approve_draft(filename, approver, person):
    """Add an approval for the filename draft"""
    # FIXME: Do database access here
    return render_to_response('idsubmit/approval_success.html', {'draft':filename})

def approval2(request):
    """ "front door" to the approval form with no prespecified draft """
    return approval(request, None)

@login_required
def approval(request, draft):
    """Main view for the page."""
    user = PersonOrOrgInfo.objects.from_django( request.user )
    if user is None:
        return fail(None, None, "Can't find your IETF user from your django user")
    print draft
    if request.method == 'POST' or draft:
        if request.method == 'POST':
            data = request.POST
        else:
            data = {'draft': draft}
        form = PreauthzForm(data)
        if form.is_valid():
            filename = form.clean_data['draft']
            # FIXME: krb-wg
            m = re.search('(?<=draft-ietf-)[a-z0-9]+', filename)
            if not m:
                return fail(form, user, 'Invalid working group name')
            wg = m.group()
            approvers = group_approvers(wg)
            if not user in approvers:
                if is_secretariat(request.user):
                    if request.POST.has_key('approver'):
                        approver_form = PickApprover(request.POST, approvers=approvers)
                        if approver_form.is_valid():
                            approver = PersonOrOrgInfo.objects.get(pk=approver_form.clean_data['approver'])
                            return approve_draft(filename, user, approver)
                    else:
                        approver_form = PickApprover(approvers=approvers)
                    return render_to_response('idsubmit/approval_pick.html',
                                                 {'form':form,
                                                  'approver_form':approver_form})
                return fail(form, user, 'You are not an approver for this WG')
            else:
                return approve_draft(filename, user, user)
    else:
        form = PreauthzForm(initial={'draft':'draft-ietf-'})
    return render_to_response('idsubmit/approval.html', {'form':form, 
                                                         'user':user})

def fail(form, user, message=""):
    """This view sends a form with an embedded error message"""
    return render_to_response('idsubmit/approval.html', {'form':form,
                                                   'user':user,
                                                   'errors':True,
                                                   'message':message})
