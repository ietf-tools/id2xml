# Copyright The IETF Trust 2007, All Rights Reserved

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.http import HttpResponse
from ietf.wg.forms import PreauthzForm
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

 
def is_group_approver(group_name, person_id):
    """Return True if the person_id has approval rights for the group_name"""
    try:
        group = IETFWG.objects.get(group_acronym__acronym=group_name)
    except IETFWG.DoesNotExist:
        return False
    approvers = []
    approvers += [ch.person_id for ch in group.wgchair_set.all()]
    approvers += [sec.person_id for sec in group.wgsecretary_set.all()]
    approvers += [ad.person_id for ad in group.area.area.areadirector_set.all()]

    return person_id in approvers

def is_secretariat(user):
    """Return True if the user is part of the Secreteriat group"""
    if User.groups.filter(name='Secretariat'):
        return True
    else:
        return False

def approve_draft(filename, approver_id, person_id):
    """Add an approval for the filename draft"""
    # FIXME: Do database access here
    return render_to_response('wg/success.html', {'draft':filename})

@login_required
def index(request):
    """Main view for the page. This function demultiplexes the requests
    based on the request method"""
    if request.method == 'POST':
        return confirm(request)
    if request.method == 'GET':
        return send(request)

@login_required
def send(request):
    """This view will return  the form in a response"""
    form = PreauthzForm(initial={'draft':'draft-ietf-'})
    user = request.user.get_profile().person    
    return render_to_response('wg/approval.html', {'form':form, 
                                                   'user':user,
                                                   'errors':False, 
                                                   'message':None})

@login_required
def confirm(request):
    """This view handles processing of the form submissions"""
    user = request.user.get_profile().person
    form = PreauthzForm(request.POST)
    if form.is_valid():
        filename = form.clean_data['draft']
        if not filename.startswith("draft-ietf-") or not filename.islower():
            return fail(form, user, 'Not a proper name for a WG draft')
        m = re.search('(?<=draft-ietf-)[a-z0-9]+', filename)
        if not m:
            return fail(form, user, 'Invalid working group name')
        if not is_group_approver(m.group(), user.person_or_org_tag):
            return fail(form, user, 'You are not an approver for this WG')
        else:
            return approve_draft(filename, user.person_or_org_tag, user.person_or_org_tag)
    else:
        return render_to_response('wg/approval.html', {'form':form,
                                                       'user':user,
                                                       'errors':True,
                                                       'message':'Error processing the form'})

def fail(form, user, message=""):
    """This view sends a form with an embedded error message"""
    return render_to_response('wg/approval.html', {'form':form,
                                                   'user':user,
                                                   'errors':True,
                                                   'message':message})
