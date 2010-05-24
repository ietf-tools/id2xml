# ballot management (voting, commenting, ...) for IESG members

import re, os
from datetime import datetime, date, time, timedelta
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse as urlreverse
from django.template.loader import render_to_string
from django.template import RequestContext
from django import forms
from django.utils.html import strip_tags

from ietf.utils.mail import send_mail_text
from ietf.ietfauth.decorators import group_required
from ietf.idtracker.templatetags.ietf_filters import in_group
from ietf.idtracker.models import *
from ietf.iesg.models import *
from ietf import settings
from ietf.idrfc.mails import *
from ietf.idrfc.utils import *


BALLOT_CHOICES = (("yes", "Yes"),
                  ("noobj", "No Objection"),
                  ("discuss", "Discuss"),
                  ("abstain", "Abstain"),
                  ("recuse", "Recuse"),
                  ("", "No Record"),
                  )

def position_to_ballot_choice(position):
    for v, label in BALLOT_CHOICES:
        if v and getattr(position, v):
            return v
    return ""

def position_label(position_value):
    return dict(BALLOT_CHOICES).get(position_value, "")

def get_ballot_info(ballot, area_director):
    pos = Position.objects.filter(ballot=ballot, ad=area_director)
    pos = pos[0] if pos else None
    
    discuss = IESGDiscuss.objects.filter(ballot=ballot, ad=area_director)
    discuss = discuss[0] if discuss else None
    
    comment = IESGComment.objects.filter(ballot=ballot, ad=area_director)
    comment = comment[0] if comment else None
    
    return (pos, discuss, comment)

class EditPositionForm(forms.Form):
    position = forms.ChoiceField(choices=BALLOT_CHOICES, widget=forms.RadioSelect)
    discuss_text = forms.CharField(required=False, widget=forms.Textarea)
    comment_text = forms.CharField(required=False, widget=forms.Textarea)

@group_required('Area_Director','Secretariat')
def edit_position(request, name):
    """Vote and edit discuss and comment on Internet Draft as Area Director."""
    doc = get_object_or_404(InternetDraft, filename=name)
    if not doc.idinternal:
        raise Http404()

    login = IESGLogin.objects.get(login_name=request.user.username)

    pos, discuss, comment = get_ballot_info(doc.idinternal.ballot, login)

    if request.method == 'POST':
        form = EditPositionForm(request.POST)
        if form.is_valid():
            # save the vote
            clean = form.cleaned_data
            vote = clean['position']
            if pos:
                # mark discuss as cleared (quirk from old system)
                if pos.discuss:
                    pos.discuss = -1
            else:
                pos = Position(ballot=doc.idinternal.ballot, ad=login)
                pos.discuss = 0
                
            old_vote = position_to_ballot_choice(pos)
            
            pos.yes = pos.noobj = pos.abstain = pos.recuse = 0
            if vote:
                setattr(pos, vote, 1)

            if pos.id:
                pos.save()
                if vote != old_vote:
                    add_document_comment(request, doc, "[Ballot Position Update] Position for %s has been changed to %s from %s" % (pos.ad, position_label(vote), position_label(old_vote)))
            elif vote:
                pos.save()
                add_document_comment(request, doc, "[Ballot Position Update] New position, %s, has been recorded" % position_label(vote))

            # save discuss
            if (discuss and clean['discuss_text'] != discuss.text) or (clean['discuss_text'] and not discuss):
                if not discuss:
                    discuss = IESGDiscuss(ballot=doc.idinternal.ballot, ad=login)

                discuss.text = clean['discuss_text']
                discuss.date = date.today()
                discuss.revision = doc.revision_display()
                discuss.active = True
                discuss.save()

                if discuss.text:
                    add_document_comment(request, doc, discuss.text,
                                         ballot=DocumentComment.BALLOT_DISCUSS)

            if pos.discuss < 1:
                IESGDiscuss.objects.filter(ballot=doc.idinternal.ballot, ad=pos.ad).update(active=False)

            # similar for comment (could share code with discuss, but
            # it's maybe better to coalesce them in the model instead
            # than doing a clever hack here)
            if (comment and clean['comment_text'] != comment.text) or (clean['comment_text'] and not comment):
                if not comment:
                    comment = IESGComment(ballot=doc.idinternal.ballot, ad=login)

                comment.text = clean['comment_text']
                comment.date = date.today()
                comment.revision = doc.revision_display()
                comment.active = True
                comment.save()

                if comment.text:
                    add_document_comment(request, doc, comment.text,
                                         ballot=DocumentComment.BALLOT_COMMENT)
            
            doc.idinternal.event_date = date.today()
            doc.idinternal.save()
            if request.POST.get("send_mail"):
                return HttpResponseRedirect(urlreverse("doc_send_ballot_comment", kwargs=dict(name=doc.filename)))
            else:
                return HttpResponseRedirect(doc.idinternal.get_absolute_url())
    else:
        initial = {}
        if pos:
            initial['position'] = position_to_ballot_choice(pos)

        if discuss:
            initial['discuss_text'] = discuss.text

        if comment:
            initial['comment_text'] = comment.text
            
        form = EditPositionForm(initial=initial)
  
    return render_to_response('idrfc/edit_position.html',
                              dict(doc=doc,
                                   form=form,
                                   discuss=discuss,
                                   comment=comment),
                              context_instance=RequestContext(request))

@group_required('Area_Director','Secretariat')
def send_ballot_comment(request, name):
    """Email Internet Draft ballot discuss/comment for area director."""
    doc = get_object_or_404(InternetDraft, filename=name)
    if not doc.idinternal:
        raise Http404()

    login = IESGLogin.objects.get(login_name=request.user.username)
    pos, discuss, comment = get_ballot_info(doc.idinternal.ballot, login)
    
    subj = []
    d = ""
    if pos and pos.discuss == 1 and discuss and discuss.text:
        d = discuss.text
        subj.append("DISCUSS")
    c = ""
    if comment and comment.text:
        c = comment.text
        subj.append("COMMENT")

    subject = "%s: %s" % (" and ".join(subj), doc.file_tag())
    body = render_to_string("idrfc/ballot_comment_mail.txt",
                            dict(discuss=d, comment=c))
    frm = u"%s <%s>" % login.person.email()
    to = "iesg@ietf.org"
        
    if request.method == 'POST':
        cc = [x.strip() for x in request.POST.get("cc", "").split(',') if x.strip()]
        if request.POST.get("cc_state_change") and doc.idinternal.state_change_notice_to:
            cc.extend(doc.idinternal.state_change_notice_to.split(','))

        send_mail_text(request, to, frm, subject, body, cc=", ".join(cc))
            
        return HttpResponseRedirect(doc.idinternal.get_absolute_url())
  
    return render_to_response('idrfc/send_ballot_comment.html',
                              dict(doc=doc,
                                   subject=subject,
                                   body=body,
                                   frm=frm,
                                   to=to,
                                   can_send=d or c),
                              context_instance=RequestContext(request))


@group_required('Area_Director','Secretariat')
def defer_ballot(request, name):
    """Signal post-pone of Internet Draft ballot, notifying relevant parties."""
    doc = get_object_or_404(InternetDraft, filename=name)
    if not doc.idinternal:
        raise Http404()

    login = IESGLogin.objects.get(login_name=request.user.username)
    telechat_date = TelechatDates.objects.all()[0].date2

    if request.method == 'POST':
        doc.idinternal.ballot.defer = True
        doc.idinternal.ballot.defer_by = login
        doc.idinternal.ballot.defer_date = date.today()
        doc.idinternal.ballot.save()
        
        doc.idinternal.change_state(IDState.objects.get(document_state_id=IDState.IESG_EVALUATION_DEFER), None)
        doc.idinternal.agenda = True
        doc.idinternal.telechat_date = telechat_date
        doc.idinternal.event_date = date.today()
        doc.idinternal.save()

        email_ballot_deferred(request, doc, login, telechat_date)
        
        log_state_changed(request, doc, login)

        return HttpResponseRedirect(doc.idinternal.get_absolute_url())
  
    return render_to_response('idrfc/defer_ballot.html',
                              dict(doc=doc,
                                   telechat_date=telechat_date),
                              context_instance=RequestContext(request))

@group_required('Area_Director','Secretariat')
def undefer_ballot(request, name):
    """Delete deferral of Internet Draft ballot."""
    doc = get_object_or_404(InternetDraft, filename=name)
    if not doc.idinternal:
        raise Http404()

    login = IESGLogin.objects.get(login_name=request.user.username)
    
    if request.method == 'POST':
        doc.idinternal.ballot.defer = False
        doc.idinternal.ballot.save()
        
        doc.idinternal.change_state(IDState.objects.get(document_state_id=IDState.IESG_EVALUATION), None)
        doc.idinternal.event_date = date.today()
        doc.idinternal.save()

        log_state_changed(request, doc, login)
        
        return HttpResponseRedirect(doc.idinternal.get_absolute_url())
  
    return render_to_response('idrfc/undefer_ballot.html',
                              dict(doc=doc),
                              context_instance=RequestContext(request))

