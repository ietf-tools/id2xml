import re, os
from datetime import datetime, date, time, timedelta
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.template import RequestContext
from django import forms
from django.utils.html import strip_tags

from ietf.ietfauth.decorators import group_required
from ietf.idtracker.models import *
#from ietf.idrfc.idrfc_wrapper import BallotWrapper, IdWrapper, RfcWrapper
from ietf import settings
from ietf.idrfc.mails import *

class ChangeStateForm(forms.Form):
    state = forms.ModelChoiceField(IDState.objects.all(), empty_label=None, required=True)
    substate = forms.ModelChoiceField(IDSubState.objects.all(), required=False)


def add_document_comment(request, doc, text):
    user = IESGLogin.objects.get(login_name=request.user.username)
    if not 'Earlier history' in text:
        text += " by %s" % user

    c = DocumentComment()
    c.document = doc.idinternal
    c.public_flag = True
    c.version = doc.revision_display()
    c.comment_text = text
    c.created_by = user
    c.rfc_flag = doc.idinternal.rfc_flag
    c.save()

def make_last_call(request, doc):
    try:
        ballot = doc.idinternal.ballot
    except BallotInfo.DoesNotExist:
        ballot = BallotInfo()
        ballot.ballot = doc.idinternal.ballot_id
        ballot.active = False
        ballot.last_call_text = generate_last_call_announcement(request, doc)
        ballot.approval_text = generate_approval_mail(request, doc)
        ballot.ballot_writeup = render_to_string("idrfc/ballot_writeup.txt")
        ballot.save()

    send_last_call_request(request, doc, ballot)
    add_document_comment(request, doc, "Last Call was requested")
    

@group_required('Area_Director','Secretariat')
def change_state(request, name):
    doc = get_object_or_404(InternetDraft, filename=name)

    user = IESGLogin.objects.get(login_name=request.user.username)

    if request.method == 'POST':
        form = ChangeStateForm(request.POST)
        if form.is_valid():
            state = form.cleaned_data['state']
            sub_state = form.cleaned_data['substate']
            internal = doc.idinternal
            if state != internal.cur_state or sub_state != internal.cur_sub_state:
                internal.change_state(state, sub_state)

                change = u"State changed to <b>%s</b> from <b>%s</b> by <b>%s</b>" % (internal.docstate(), format_document_state(internal.prev_state, internal.prev_sub_state), user)
                
                c = DocumentComment()
                c.document = internal
                c.public_flag = True
                c.version = doc.revision_display()
                c.comment_text = change
                c.created_by = user
                c.result_state = internal.cur_state
                c.origin_state = internal.prev_state
                c.rfc_flag = internal.rfc_flag
                c.save()

                internal.event_date = date.today()
                internal.save()

                send_doc_state_changed_email(request, doc, strip_tags(change))

                if internal.cur_state.document_state_id == IDState.LAST_CALL_REQUESTED:
                    make_last_call(request, doc)

                    return render_to_response('idrfc/last_call_requested.html',
                                              dict(doc=doc),
                                              context_instance=RequestContext(request))
                
            return HttpResponseRedirect(internal.get_absolute_url())

    else:
        form = ChangeStateForm(initial=dict(state=doc.idinternal.cur_state_id,
                                            substate=doc.idinternal.cur_sub_state_id))

    next_states = IDNextState.objects.filter(cur_state=doc.idinternal.cur_state)
    
    # FIXME: go back to previous state?

    return render_to_response('idrfc/edit_state.html',
                              dict(form=form,
                                   next_states=next_states),
                              context_instance=RequestContext(request))
    
