# Copyright The IETF Trust 2007, All Rights Reserved
import datetime
import json
from email.utils import parseaddr
from functools import partial, wraps

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse as urlreverse
from django.core.validators import validate_email, ValidationError
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from ietf.group.models import Group
from ietf.liaisons.models import LiaisonStatement, LiaisonStatementState, LiaisonStatementEvent, LiaisonStatementFromGroup
from ietf.liaisons.accounts import (get_person_for_user, can_add_outgoing_liaison,
                                    can_add_incoming_liaison, 
                                    is_ietfchair, is_iabchair, is_iab_executive_director,
                                    can_edit_liaison, is_secretariat)
from ietf.liaisons.forms import (liaison_form_factory, liaison_from_form_factory,
    SearchLiaisonForm, FromGroupForm, IncomingFromGroupForm, BaseFromGroupFormSet)
from ietf.liaisons.utils import IETFHM, can_submit_liaison_required, approvable_liaison_statements
from ietf.liaisons.mails import notify_pending_by_email, send_liaison_by_email
from ietf.liaisons.fields import select2_id_liaison_json, select2_id_group_json


# -------------------------------------------------
# Helper Functions
# -------------------------------------------------
def _can_take_care(liaison, user):
    if not liaison.deadline or liaison.action_taken:
        return False

    if user.is_authenticated():
        if is_secretariat(user):
            return True
        else:
            return _find_person_in_emails(liaison, get_person_for_user(user))
    return False

def _find_person_in_emails(liaison, person):
    if not person:
        return False

    emails = ','.join(e for e in [liaison.cc, liaison.to_contact, liaison.to_name,
                                  liaison.reply_to, liaison.response_contact,
                                  liaison.technical_contact] if e)
    for email in emails.split(','):
        name, addr = parseaddr(email)
        try:
            validate_email(addr)
        except ValidationError:
            continue

        if person.email_set.filter(address=addr):
            return True
        elif addr in ('chair@ietf.org', 'iesg@ietf.org') and is_ietfchair(person):
            return True
        elif addr in ('iab@iab.org', 'iab-chair@iab.org') and is_iabchair(person):
            return True
        elif addr in ('execd@iab.org', ) and is_iab_executive_director(person):
            return True

    return False

def get_details_tabs(stmt, selected):
    return [
        t + (t[0].lower() == selected.lower(),)
        for t in [
        ('Statement', urlreverse('liaison_detail', kwargs={ 'object_id': stmt.pk })),
        ('History', urlreverse('liaison_history', kwargs={ 'object_id': stmt.pk }))
    ]]

def normalize_sort(request):
    sort = request.GET.get('sort', "")
    if sort not in ('submitted', 'deadline', 'title', 'to_name', 'from_name'):
        sort = "submitted"

    # reverse dates
    order_by = "-" + sort if sort in ("submitted", "deadline") else sort

    return sort, order_by

# -------------------------------------------------
# Ajax Functions
# -------------------------------------------------
'''@can_submit_liaison_required
def ajax_get_liaison_info(request):
    person = get_person_for_user(request.user)

    to_entity_id = request.GET.get('to_entity_id', None)
    from_entity_id = request.GET.get('from_entity_id', None)

    result = {'poc': [], 'cc': [], 'needs_approval': False, 'post_only': False, 'full_list': []}

    to_error = 'Invalid TO entity id'
    if to_entity_id:
        to_entity = IETFHM.get_entity_by_key(to_entity_id)
        if to_entity:
            to_error = ''

    from_error = 'Invalid FROM entity id'
    if from_entity_id:
        from_entity = IETFHM.get_entity_by_key(from_entity_id)
        if from_entity:
            from_error = ''

    if to_error or from_error:
        result.update({'error': '\n'.join([to_error, from_error])})
    else:
        result.update({'error': False,
                       'cc': ([i.email() for i in to_entity.get_cc(person=person)] +
                              [i.email() for i in from_entity.get_from_cc(person=person)]),
                       'poc': [i.email() for i in to_entity.get_poc()],
                       'needs_approval': from_entity.needs_approval(person=person),
                       'post_only': from_entity.post_only(person=person, user=request.user)})
        if is_secretariat(request.user):
            full_list = [(i.pk, i.email()) for i in set(from_entity.full_user_list())]
            full_list.sort(key=lambda x: x[1])
            full_list = [(person.pk, person.email())] + full_list
            result.update({'full_list': full_list})

    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type='text/javascript')
'''

@can_submit_liaison_required
def ajax_get_liaison_info(request):
    person = get_person_for_user(request.user)

    to_entity_id = request.GET.get('to_entity_id', None)
    from_entity_id = request.GET.get('from_entity_id', None)
    to_entity = None
    from_entity = None
    
    result = {'poc': [], 'cc': [], 'needs_approval': False, 'post_only': False, 'full_list': []}

    def convert_identity(id):
        '''Convert Group ID to legacy [group type]_[group id]'''
        if not id:
            return id
        try:
            group = Group.objects.get(pk=id)
            if group.type_id in ('sdo','wg','area'):
                return '{}_{}'.format(group.type_id,id)
        except ObjectDoesNotExist:
            pass
        return id
    
    # convert identities
    to_entity_id = convert_identity(to_entity_id)
    from_entity_id = convert_identity(from_entity_id)
                
    to_error = 'Invalid TO entity id'
    if to_entity_id:
        to_entity = IETFHM.get_entity_by_key(to_entity_id)
        if to_entity:
            to_error = ''

    from_error = 'Invalid FROM entity id'
    if from_entity_id:
        from_entity = IETFHM.get_entity_by_key(from_entity_id)
        if from_entity:
            from_error = ''

    if to_error and from_error:
        result.update({'error': '\n'.join([to_error, from_error])})
    else:
        cc = []
        poc = []
        needs_approval = True
        post_only = False
        
        if from_entity:
            cc.extend([i.email() for i in from_entity.get_from_cc(person=person)])
            needs_approval = from_entity.needs_approval(person=person)
            post_only = from_entity.post_only(person=person, user=request.user)
        if to_entity:
            cc.extend([i.email() for i in to_entity.get_cc(person=person)])
            poc.extend([i.email() for i in to_entity.get_poc()])
            
        result.update({'error': False,
                       'cc': cc,
                       'poc': poc,
                       'needs_approval': needs_approval,
                       'post_only': post_only})
        if is_secretariat(request.user):
            #full_list = [(r.email.pk, r.email.formatted_email()) for r in set(from_entity.full_user_list())]
            full_list = [(r.email.pk, '{} &lt;{}&gt;'.format(r.person.plain_name(),r.email.address)) for r in set(from_entity.full_user_list())]
            full_list.sort(key=lambda x: x[1])
            #full_list = [(person.pk, person.email())] + full_list
            result.update({'full_list': full_list})


    json_result = json.dumps(result)
    return HttpResponse(json_result, content_type='text/javascript')
    
def ajax_select2_search_liaison_statements(request):
    q = [w.strip() for w in request.GET.get('q', '').split() if w.strip()]

    if not q:
        objs = LiaisonStatement.objects.none()
    else:
        qs = LiaisonStatement.objects.exclude(approved=None).all()

        for t in q:
            qs = qs.filter(title__icontains=t)

        objs = qs.distinct().order_by("-id")[:20]

    return HttpResponse(select2_id_liaison_json(objs), content_type='application/json')

def ajax_select2_search_groups(request, group_type):
    q = [w.strip() for w in request.GET.get('q', '').split() if w.strip()]

    if not q:
        objs = Group.objects.none()
    else:
        if group_type == 'internal':
            qs = Group.objects.filter(type='wg')
        elif group_type == 'external':
            qs = Group.objects.filter(type='sdo')

        for t in q:
            qs = qs.filter(acronym__icontains=t)

        objs = qs.distinct().order_by("acronym")[:20]

    return HttpResponse(select2_id_group_json(objs), content_type='application/json')
    
def ajax_liaison_list(request):
    liaisons = SearchLiaisonForm().get_results()

    return render_to_response('liaisons/liaison_table.html', {
        "liaisons": liaisons,
    }, context_instance=RequestContext(request))

# -------------------------------------------------
# View Functions
# -------------------------------------------------

@can_submit_liaison_required
def add_liaison(request, liaison=None):

    # 1 to show initially plus the template
    from_group_form = liaison_from_form_factory(request, data=request.POST.copy(),liaison=liaison)
    FromGroupFormset = inlineformset_factory(LiaisonStatement, LiaisonStatementFromGroup, form=from_group_form, formset=BaseFromGroupFormSet, can_delete=True, extra=1+1)
    FromGroupFormset.form = wraps(from_group_form)(partial(from_group_form,user=request.user))
    instance = liaison if liaison else LiaisonStatement()
    
    if request.method == 'POST':
        form = liaison_form_factory(request, data=request.POST.copy(),
                                    files = request.FILES, liaison=liaison)
        formset = FromGroupFormset(request.POST, instance=instance)
        
        if form.is_valid() and formset.is_valid():
            liaison = form.save(request=request)
            formset = FromGroupFormset(request.POST, instance=liaison)
            formset.save()
            
            # notifications
            if request.POST.get('send', False):
                if not liaison.state.slug == 'approved':
                    notify_pending_by_email(request, liaison)
                else:
                    send_liaison_by_email(request, liaison)
            
            return redirect('liaison_list')
        #else:
        #    assert False, (form.errors, formset.errors, formset.non_form_errors())
            
    else:
        form = liaison_form_factory(request, liaison=liaison)
        formset = FromGroupFormset(instance=instance)
        #assert False, (form.fields['organization'].widget.attrs,
        #    form.fields['organization'].widget.render('name','value'))
        
    return render_to_response(
        'liaisons/edit.html',
        {'form': form,
         'formset': formset,
         'liaison': liaison},
        context_instance=RequestContext(request),
    )

def liaison_history(request, object_id):
    """Show the history for a specific liaison statement"""
    liaison = get_object_or_404(LiaisonStatement, id=object_id)
    events = liaison.liaisonstatementevent_set.all().order_by("-time", "-id").select_related("by")
    #if not has_role(request.user, "Secretariat"):
    #    events = events.exclude(type='private_comment')

    return render(request, "liaisons/detail_history.html",  {
        'events':events,
        'liaison': liaison,
        'tabs': get_details_tabs(liaison, 'History'),
        'selected_tab_entry':'history'
    })

def liaison_list(request):
    if request.GET.get('search', None):
        form = SearchLiaisonForm(data=request.GET)
        if form.is_valid():
            result = form.get_results()
    else:
        #form = SearchLiaisonForm()
        #result = form.get_results()
        sort, order_by = normalize_sort(request)
        # TODO fix order by
        #result = LiaisonStatement.objects.filter(state='approved').order_by(order_by)
        result = LiaisonStatement.objects.filter(state='approved')

        # perform sort
        if sort == 'submitted':
            result = sorted(result, key=lambda a: a.submitted, reverse=True)
        if sort == 'from_name':
            result = sorted(result, key=lambda a: a.from_groups_display)
        if sort == 'to_name':
            result = sorted(result, key=lambda a: a.to_groups_display)
        if sort == 'deadline':
            result = result.order_by('-deadline')
        if sort == 'title':
            result = result.order_by('title')
            
    liaisons = result

    can_send_outgoing = can_add_outgoing_liaison(request.user)
    can_send_incoming = can_add_incoming_liaison(request.user)

    approvable = approvable_liaison_statements(request.user).count()

    return render_to_response('liaisons/overview.html', {
        "liaisons": liaisons,
        "can_manage": approvable or can_send_incoming or can_send_outgoing,
        "approvable": approvable,
        "can_send_incoming": can_send_incoming,
        "can_send_outgoing": can_send_outgoing,
        "with_search": False,
        "sort": sort,
        #"form": form,
    }, context_instance=RequestContext(request))

@can_submit_liaison_required
def liaison_approval_list(request):
    liaisons = approvable_liaison_statements(request.user).order_by("-id")

    return render_to_response('liaisons/approval_list.html', {
        "liaisons": liaisons,
    }, context_instance=RequestContext(request))


@can_submit_liaison_required
def liaison_approval_detail(request, object_id):
    liaison = get_object_or_404(approvable_liaison_statements(request.user), pk=object_id)

    if request.method == 'POST' and (request.POST.get('approved') or request.POST.get('dead')):
        if request.POST.get('approved'):
            state = LiaisonStatementState.objects.get(slug='approved')
            event_type_id = 'approved'
        elif request.POST.get('dead'):
            state = LiaisonStatementState.objects.get(slug='dead')
            event_type_id = 'killed'
            
        liaison.state = state
        liaison.save()
        
        # create event
        LiaisonStatementEvent.objects.create(
            type_id = event_type_id,
            by = request.user.person,
            statement = liaison,
            desc = 'Statement {}'.format(event_type_id.capitalize()),
        )

        # TODO: send mail on killed?
        if request.POST.get('approved'):
            send_liaison_by_email(request, liaison)
        
        return redirect('liaison_list')

    relations_by = [i.target for i in liaison.source_of_set.filter(target__state__slug='approved')]
    relations_to = [i.source for i in liaison.target_of_set.filter(source__state__slug='approved')]

    return render_to_response('liaisons/approval_detail.html', {
        "liaison": liaison,
        "relations_to": relations_to,
        "relations_by": relations_by,
        "is_approving": True,
    }, context_instance=RequestContext(request))

def liaison_detail(request, object_id):
    liaison = get_object_or_404(LiaisonStatement.objects.filter(state__slug='approved'), pk=object_id)
    can_edit = request.user.is_authenticated() and can_edit_liaison(request.user, liaison)
    can_take_care = _can_take_care(liaison, request.user)

    if request.method == 'POST' and request.POST.get('do_action_taken', None) and can_take_care:
        liaison.tags.remove('required')
        liaison.tags.add('taken')
        can_take_care = False

    relations_by = [i.target for i in liaison.source_of_set.filter(target__state__slug='approved')]
    relations_to = [i.source for i in liaison.target_of_set.filter(source__state__slug='approved')]

    return render_to_response("liaisons/detail.html", {
        "liaison": liaison,
        'tabs': get_details_tabs(liaison, 'Statement'),
        "can_edit": can_edit,
        "can_take_care": can_take_care,
        "relations_to": relations_to,
        "relations_by": relations_by,
    }, context_instance=RequestContext(request))

def liaison_edit(request, object_id):
    liaison = get_object_or_404(LiaisonStatement, pk=object_id)
    if not (request.user.is_authenticated() and can_edit_liaison(request.user, liaison)):
        return HttpResponseForbidden('You do not have permission to edit this liaison statement')
    return add_liaison(request, liaison=liaison)
