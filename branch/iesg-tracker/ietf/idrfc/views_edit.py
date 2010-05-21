# views for editing the metadata on Internet Drafts

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
#from ietf.idrfc.idrfc_wrapper import BallotWrapper, IdWrapper, RfcWrapper
from ietf import settings
from ietf.idrfc.mails import *

def add_document_comment(request, doc, text, include_by=True, ballot=None):
    login = IESGLogin.objects.get(login_name=request.user.username)
    if include_by:
        text += " by %s" % login

    c = DocumentComment()
    c.document = doc.idinternal
    c.public_flag = True
    c.version = doc.revision_display()
    c.comment_text = text
    c.created_by = login
    if ballot:
        c.ballot = ballot
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

def log_state_changed(request, doc, by):
    change = u"State changed to <b>%s</b> from <b>%s</b> by <b>%s</b>" % (
        doc.idinternal.docstate(),
        format_document_state(doc.idinternal.prev_state, doc.
                              idinternal.prev_sub_state),
        by)

    c = DocumentComment()
    c.document = doc.idinternal
    c.public_flag = True
    c.version = doc.revision_display()
    c.comment_text = change
    c.created_by = by
    c.result_state = doc.idinternal.cur_state
    c.origin_state = doc.idinternal.prev_state
    c.rfc_flag = doc.idinternal.rfc_flag
    c.save()

    email_state_changed(request, doc, strip_tags(change))

    return change

    
class ChangeStateForm(forms.Form):
    state = forms.ModelChoiceField(IDState.objects.all(), empty_label=None, required=True)
    substate = forms.ModelChoiceField(IDSubState.objects.all(), required=False)

@group_required('Area_Director','Secretariat')
def change_state(request, name):
    """Change state of Internet Draft, notifying parties as necessary
    and logging the change as a comment."""
    doc = get_object_or_404(InternetDraft, filename=name)
    if not doc.idinternal or doc.status.status == "Expired":
        raise Http404()

    login = IESGLogin.objects.get(login_name=request.user.username)

    if request.method == 'POST':
        form = ChangeStateForm(request.POST)
        if form.is_valid():
            state = form.cleaned_data['state']
            sub_state = form.cleaned_data['substate']
            internal = doc.idinternal
            if state != internal.cur_state or sub_state != internal.cur_sub_state:
                internal.change_state(state, sub_state)
                internal.event_date = date.today()
                internal.mark_by = login
                internal.save()

                change = log_state_changed(request, doc, login)
                email_owner(request, doc, internal.job_owner, login, change)

                if internal.cur_state.document_state_id == IDState.LAST_CALL_REQUESTED:
                    make_last_call(request, doc)

                    return render_to_response('idrfc/last_call_requested.html',
                                              dict(doc=doc),
                                              context_instance=RequestContext(request))
                
            return HttpResponseRedirect(internal.get_absolute_url())

    else:
        init = dict(state=doc.idinternal.cur_state_id,
                    substate=doc.idinternal.cur_sub_state_id)
        form = ChangeStateForm(initial=init)

    next_states = IDNextState.objects.filter(cur_state=doc.idinternal.cur_state)
    prev_state_formatted = format_document_state(doc.idinternal.prev_state,
                                                 doc.idinternal.prev_sub_state)

    return render_to_response('idrfc/change_state.html',
                              dict(form=form,
                                   doc=doc,
                                   prev_state_formatted=prev_state_formatted,
                                   next_states=next_states),
                              context_instance=RequestContext(request))

def dehtmlify_textarea_text(s):
    return s.replace("<br>", "\n").replace("<b>", "").replace("</b>", "").replace("  ", " ")

def parse_date(s):
    return date(*tuple(int(x) for x in s.split('-')))

class EditInfoForm(forms.Form):
    intended_status = forms.ModelChoiceField(IDIntendedStatus.objects.all(), empty_label=None, required=True)
    status_date = forms.DateField(required=False)
    group = forms.ModelChoiceField(Acronym.objects.filter(area__status=Area.ACTIVE), label="Area acronym", required=False)
    via_rfc_editor = forms.BooleanField(required=False, label="Via IRTF or RFC Editor")
    job_owner = forms.ModelChoiceField(IESGLogin.objects.filter(user_level__in=(1, 2)).order_by('user_level', 'last_name'), label="Responsible AD", empty_label=None, required=True)
    state_change_notice_to = forms.CharField(max_length=255, label="Notice emails", help_text="Separate email addresses with commas", required=False)
    note = forms.CharField(widget=forms.Textarea, label="IESG note", required=False)
    telechat_date = forms.TypedChoiceField(coerce=parse_date, empty_value=None, required=False)
    returning_item = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        # separate active ADs from inactive
        choices = []
        objects = IESGLogin.objects.in_bulk([t[0] for t in self.fields['job_owner'].choices])
        separated = False
        for t in self.fields['job_owner'].choices:
            if objects[t[0]].user_level != 1 and not separated:
                choices.append(("", "----------------"))
                separated = True
            choices.append(t)
        self.fields['job_owner'].choices = choices
        
        # telechat choices
        today = date.today()
        dates = TelechatDates.objects.all()[0].dates()
        init = self.fields['telechat_date'].initial
        if init and init not in dates:
            dates.insert(0, init)

        choices = [(d, d.strftime("%Y-%m-%d")) for d in dates]
        choices.insert(0, ("", "(not on agenda)"))

        self.fields['telechat_date'].choices = choices

        # returning item is rendered non-standard
        self.standard_fields = [x for x in self.visible_fields() if x.name not in ('returning_item',)]
    
    def clean_status_date(self):
        d = self.cleaned_data['status_date']
        if d:
            if d < date.today():
                raise forms.ValidationError("Date must not be in the past.")
            if d >= date.today() + timedelta(days=365 * 2):
                raise forms.ValidationError("Date must be within two years.")
        
        return d

    def clean_note(self):
        # note is stored munged in the database
        return self.cleaned_data['note'].replace('\n', '<br>').replace('\r', '').replace('  ', '&nbsp; ')


@group_required('Area_Director','Secretariat')
def edit_info(request, name):
    """Edit various Internet Draft attributes, notifying parties as
    necessary and logging changes as document comments."""
    doc = get_object_or_404(InternetDraft, filename=name)
    if not doc.idinternal or doc.status.status == "Expired":
        raise Http404()

    login = IESGLogin.objects.get(login_name=request.user.username)

    initial_telechat_date = doc.idinternal.telechat_date if doc.idinternal.agenda else None

    if request.method == 'POST':
        form = EditInfoForm(request.POST,
                            initial=dict(telechat_date=initial_telechat_date,
                                         group=doc.group_id))
        if form.is_valid():
            changes = []
            r = form.cleaned_data
            entry = "%s has been changed to <b>%s</b> from <b>%s</b>"
            orig_job_owner = doc.idinternal.job_owner

            # update various attributes, we need to keep track of what
            # we're doing
            
            if r['intended_status'] != doc.intended_status:
                changes.append(entry % ("Intended Status",
                                        r['intended_status'],
                                        doc.intended_status))
                doc.intended_status = r['intended_status']

            if r['status_date'] != doc.idinternal.status_date:
                changes.append(entry % ("Status date",
                                        r['status_date'],
                                        doc.idinternal.status_date))
                doc.idinternal.status_date = r['status_date']

            if 'group' in r and r['group'] and r['group'] != doc.group and doc.group_id == Acronym.INDIVIDUAL_SUBMITTER:
                changes.append(entry % ("Area acronym", r['group'], doc.group))
                doc.group = r['group']
                
            if r['job_owner'] != doc.idinternal.job_owner:
                changes.append(entry % ("Responsible AD",
                                        r['job_owner'],
                                        doc.idinternal.job_owner))
                doc.idinternal.job_owner = r['job_owner']

            if r['state_change_notice_to'] != doc.idinternal.state_change_notice_to:
                changes.append(entry % ("State Change Notice email list",
                                        r['state_change_notice_to'],
                                        doc.idinternal.state_change_notice_to))
                doc.idinternal.state_change_notice_to = r['state_change_notice_to']

            # coalesce some of the changes into one comment, mail them below
            if changes:
                add_document_comment(request, doc, "<br>".join(changes))

            # handle note (for some reason the old Perl code didn't
            # include that in the changes)
            if r['note'] != doc.idinternal.note:
                if not r['note']:
                    if doc.idinternal.note:
                        add_document_comment(request, doc, "Note field has been cleared")
                else:
                    if doc.idinternal.note:
                        add_document_comment(request, doc, "[Note]: changed to '%s'" % r['note'])
                    else:
                        add_document_comment(request, doc, "[Note]: '%s' added" % r['note'])
                    
                doc.idinternal.note = r['note']

            on_agenda = bool(r['telechat_date'])

            returning_item_changed = False
            if doc.idinternal.returning_item != bool(r['returning_item']):
                doc.idinternal.returning_item = bool(r['returning_item'])
                returning_item_changed = True

            # auto-update returning item
            if (not returning_item_changed and
                on_agenda and doc.idinternal.agenda
                and r['telechat_date'] != doc.idinternal.telechat_date):
                doc.idinternal.returning_item = True

            # update agenda
            if doc.idinternal.agenda != on_agenda:
                if on_agenda:
                    add_document_comment(request, doc,
                                         "Placed on agenda for telechat - %s" % r['telechat_date'])
                else:
                    add_document_comment(request, doc,
                                         "Removed from agenda for telechat")
                doc.idinternal.agenda = on_agenda
            elif on_agenda and r['telechat_date'] != doc.idinternal.telechat_date:
                add_document_comment(request, doc, entry %
                                     ("Telechat date",
                                      r['telechat_date'],
                                      doc.idinternal.telechat_date))
                doc.idinternal.telechat_date = r['telechat_date']

            if in_group(request.user, 'Secretariat'):
                doc.idinternal.via_rfc_editor = bool(r['via_rfc_editor'])

            doc.idinternal.email_display = str(doc.idinternal.job_owner)
            doc.idinternal.token_name = str(doc.idinternal.job_owner)
            doc.idinternal.token_email = doc.idinternal.job_owner.person.email()[1]
            doc.idinternal.mark_by = login
            doc.idinternal.event_date = date.today()

            if changes:
                email_owner(request, doc, orig_job_owner, login, "\n".join(changes))
            doc.idinternal.save()
            doc.save()
            return HttpResponseRedirect(doc.idinternal.get_absolute_url())
    else:
        init = dict(intended_status=doc.intended_status_id,
                    status_date=doc.idinternal.status_date,
                    group=doc.group_id,
                    job_owner=doc.idinternal.job_owner_id,
                    state_change_notice_to=doc.idinternal.state_change_notice_to,
                    note=dehtmlify_textarea_text(doc.idinternal.note),
                    telechat_date=initial_telechat_date,
                    returning_item=doc.idinternal.returning_item,
                    )
        form = EditInfoForm(initial=init)

    if not in_group(request.user, 'Secretariat'):
        form.standard_fields = [x for x in form.standard_fields if x.name != "via_rfc_editor"]
        
    if doc.group_id != Acronym.INDIVIDUAL_SUBMITTER:
        # show group only if none has been assigned yet
        form.standard_fields = [x for x in form.standard_fields if x.name != "group"]
        
    return render_to_response('idrfc/edit_info.html',
                              dict(form=form,
                                   user=request.user,
                                   login=login),
                              context_instance=RequestContext(request))


@group_required('Area_Director','Secretariat')
def request_resurrect(request, name):
    """Request resurrect of expired Internet Draft."""
    doc = get_object_or_404(InternetDraft, filename=name)
    if not doc.idinternal or doc.status.status != "Expired":
        raise Http404()

    login = IESGLogin.objects.get(login_name=request.user.username)

    if request.method == 'POST':
        email_resurrect_requested(request, doc, login)
        add_document_comment(request, doc, "Resurrection was requested")
        doc.idinternal.resurrect_requested_by = login
        doc.idinternal.save()
        return HttpResponseRedirect(doc.idinternal.get_absolute_url())
  
    return render_to_response('idrfc/request_resurrect.html',
                              dict(doc=doc),
                              context_instance=RequestContext(request))

class AddCommentForm(forms.Form):
    comment = forms.CharField(required=True, widget=forms.Textarea)

@group_required('Area_Director','Secretariat')
def add_comment(request, name):
    """Add comment to Internet Draft."""
    doc = get_object_or_404(InternetDraft, filename=name)
    if not doc.idinternal:
        raise Http404()

    login = IESGLogin.objects.get(login_name=request.user.username)

    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        if form.is_valid():
            c = form.cleaned_data['comment']
            add_document_comment(request, doc, c, include_by=False)
            email_owner(request, doc, doc.idinternal.job_owner, login,
                        "A new comment added by %s" % login)
            return HttpResponseRedirect(doc.idinternal.get_absolute_url())
    else:
        form = AddCommentForm()
  
    return render_to_response('idrfc/add_comment.html',
                              dict(doc=doc,
                                   form=form),
                              context_instance=RequestContext(request))

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
    """Vote and edit discuss and comment on Internet Draft for area director."""
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

