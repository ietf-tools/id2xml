# Copyright The IETF Trust 2007, All Rights Reserved

import os

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse as urlreverse
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response as render, get_object_or_404, redirect
from django.template import RequestContext

from ietf.doc.models import DocAlias
from ietf.ipr.forms import HolderIprDisclosureForm, GenericIprDisclosureForm, ThirdPartyIprDisclosureForm, DraftForm, RfcForm, SearchForm
from ietf.ipr.models import IprDisclosureStateName, IprDisclosureBase, HolderIprDisclosure, GenericIprDisclosure, ThirdPartyIprDisclosure, IprDocRel, IprDocAlias, IprLicenseTypeName, SELECT_CHOICES, LICENSE_CHOICES, RelatedIpr
from ietf.ipr.models import IprDetail # delete me
#from ietf.ipr.related import related_docs
from ietf.ipr.view_sections import section_list_for_ipr
from ietf.name.models import DocRelationshipName
from ietf.person.models import Person
from ietf.utils.draft_search import normalize_draftname

# ----------------------------------------------------------------
# Globals
# ----------------------------------------------------------------
# maps string type or ipr model class to corresponding edit form
ipr_form_mapping = { 'specific':HolderIprDisclosureForm,
                     'generic':GenericIprDisclosureForm,
                     'third-party':ThirdPartyIprDisclosureForm,
                     'HolderIprDisclosure':HolderIprDisclosureForm,
                     'GenericIprDisclosure':GenericIprDisclosureForm,
                     'ThirdPartyIprDisclosure':ThirdPartyIprDisclosureForm }
                         
# ----------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------
def get_genitive(name):
    """Return the genitive form of name"""
    return name + "'" if name.endswith('s') else name + "'s"

def get_ipr_summary(disclosure):
    """Return IPR related document names as a string"""
    ipr = []
    for doc in disclosure.docs.all():
        if doc.name.startswith('rfc'):
            ipr.append('RFC {}'.format(doc.name[3:]))
        else:
            ipr.append(doc.name)
    
    if disclosure.other_designations:
        ipr.append(disclosure.other_designations)

    if len(ipr) == 1:
        ipr = ipr[0]
    elif len(ipr) == 2:
        ipr = " and ".join(ipr)
    else:
        ipr = ", ".join(ipr[:-1]) + ", and " + ipr[-1]

    return ipr

def related_docs(alias):
    """Returns list of related documents"""
    results = list(alias.document.docalias_set.all())
    
    rels = alias.document.all_relations_that_doc(['replaces','obs'])

    for rel in rels:
        rel_aliases = list(rel.target.document.docalias_set.all())
        
        for x in rel_aliases:
            x.related = rel
            x.relation = rel.relationship.revname
        results += rel_aliases 
    return list(set(results))
    
def set_disclosure_title(disclosure):
    """Set the title of the disclosure"""
    ipr_summary = get_ipr_summary(disclosure)

    if disclosure.get_classname() == 'HolderIprDisclosure':
        title = get_genitive(disclosure.holder_legal_name) + ' Statement about IPR related to {}'.format(ipr_summary)
    elif disclosure.get_classname() == 'GenericIprDisclosure':
        title = get_genitive(disclosure.holder_legal_name) + ' General License Statement'
    elif disclosure.get_classname() == 'ThirdPartyIprDisclosure':
        title = get_genitive(disclosure.ietfer_name) + ' Statement about IPR related to {} belonging to {}'.format(ipr_summary,disclsoure.holder_legal_name)
    
    # truncate for db
    if len(title) > 255:
        title = title[:252] + "..."
    disclosure.title = title

# ----------------------------------------------------------------
# Views
# ----------------------------------------------------------------

def about(request):
    return render("ipr/disclosure.html", {}, context_instance=RequestContext(request))

def history(request, id):
    """Show the history for a specific IPR disclosure"""
    ipr = get_object_or_404(IprDisclosureBase, id=id).get_child()
    events = ipr.iprevent_set.all().order_by("-time", "-id").select_related("by")
    tabs = [('Disclosure','disclosure',urlreverse('ipr_show',kwargs={'id':id}),True),
            ('History','history',urlreverse('ipr_history',kwargs={'id':id}),True)]

    return render("ipr/details_history.html",  {
        'events':events,
        'ipr': ipr,
        'tabs':tabs,
        'selected':'history'},
        context_instance=RequestContext(request)
    )

def iprs_for_drafts_txt(request):
    docipr = {}

    for o in IprDocRel.objects.filter(disclosure__state='posted').select_related('document'):
        name = o.document.name
        if name.startswith("rfc"):
            name = name.upper()

        if not name in docipr:
            docipr[name] = []

        docipr[name].append(o.disclosure_id)

    lines = [ u"# Machine-readable list of IPR disclosures by draft name" ]
    for name, iprs in docipr.iteritems():
        lines.append(name + "\t" + "\t".join(unicode(ipr_id) for ipr_id in sorted(iprs)))

    return HttpResponse("\n".join(lines), content_type="text/plain")

def new(request, type):
    """Submit a new IPR Disclosure"""
    
    DraftFormset = inlineformset_factory(IprDisclosureBase, IprDocRel, form=DraftForm, can_delete=False, extra=1)
    RfcFormset = inlineformset_factory(IprDisclosureBase, IprDocRel, form=RfcForm, can_delete=False, extra=1)
    
    if request.method == 'POST':
        form = ipr_form_mapping[type](request.POST)
        draft_formset = DraftFormset(request.POST, instance=IprDisclosureBase(), prefix='draft')
        rfc_formset = RfcFormset(request.POST, instance=IprDisclosureBase(), prefix='rfc')
        if form.is_valid() and draft_formset.is_valid() and rfc_formset.is_valid(): 
            disclosure = form.save(commit=False)
            disclosure.by = request.user.person
            disclosure.state = IprDisclosureStateName.objects.get(slug='pending')
            disclosure.save()
            
            draft_formset = DraftFormset(request.POST, instance=disclosure, prefix='draft')
            draft_formset.save()
            rfc_formset = RfcFormset(request.POST, instance=disclosure, prefix='rfc')
            rfc_formset.save()

            set_disclosure_title(disclosure)
            disclosure.save()
            
            # send email notification
            # TODO
            
            return render("ipr/submitted.html", context_instance=RequestContext(request))
    else:
        form = ipr_form_mapping[type]()
        disclosure = IprDisclosureBase()    # dummy disclosure for inlineformset
        draft_formset = DraftFormset(instance=disclosure, prefix='draft')
        rfc_formset = RfcFormset(instance=disclosure, prefix='rfc')
        
    return render("ipr/details_edit.html",  {
        'form': form,
        'draft_formset':draft_formset,
        'rfc_formset':rfc_formset},
        context_instance=RequestContext(request)
    )

def show(request, id):
    ipr = get_object_or_404(IprDisclosureBase, id=id).get_child()
    
    if ipr.state.slug == 'removed':
        return render("ipr/removed.html",  {
            'ipr': ipr},
            context_instance=RequestContext(request)
        )
        
    tabs = [('Disclosure','disclosure',urlreverse('ipr_show',kwargs={'id':id}),True),
            ('History','history',urlreverse('ipr_history',kwargs={'id':id}),True)]

    return render("ipr/details_view.html",  {
        'ipr': ipr,
        'tabs':tabs,
        'selected':'disclosure',
        'section_list': section_list_for_ipr(ipr)},
        context_instance=RequestContext(request)
    )

def showlist(request):
    #disclosures = IprDetail.objects.all().prefetch_related("updates__updated", "updated_by__ipr")
    #generic_disclosures  = disclosures.filter(status__in=[1,3], generic=1)
    #specific_disclosures = disclosures.filter(status__in=[1,3], generic=0, third_party=0)
    #thirdpty_disclosures = disclosures.filter(status__in=[1,3], generic=0, third_party=1)
    
    # note submitted date_causes extra db hits
    generic_disclosures = GenericIprDisclosure.objects.filter(state__in=('posted','removed')).prefetch_related('relatedipr_source_set__target','relatedipr_target_set__source')
    specific_disclosures = HolderIprDisclosure.objects.filter(state__in=('posted','removed')).prefetch_related('relatedipr_source_set__target','relatedipr_target_set__source')
    thirdpty_disclosures = ThirdPartyIprDisclosure.objects.filter(state__in=('posted','removed')).prefetch_related('relatedipr_source_set__target','relatedipr_target_set__source')
    
    gd = sorted(generic_disclosures, key=lambda x: x.submitted_date,reverse=True)
    sd = sorted(specific_disclosures, key=lambda x: x.submitted_date,reverse=True)
    td = sorted(thirdpty_disclosures, key=lambda x: x.submitted_date,reverse=True)
    
    return render("ipr/list.html", {
            'generic_disclosures' : gd,
            'specific_disclosures': sd,
            'thirdpty_disclosures': td}, 
            context_instance=RequestContext(request)
    )

def update(request, id):
    """Update disclosure.  Clones the existing disclosure and allows edit of attributes"""
    base = get_object_or_404(IprDisclosureBase, id=id)
    ipr = base.get_child()
    
    #ipr.pk = None   # clone object
    
    DraftFormset = inlineformset_factory(IprDisclosureBase, IprDocRel, form=DraftForm, can_delete=False, extra=1)
    RfcFormset = inlineformset_factory(IprDisclosureBase, IprDocRel, form=RfcForm, can_delete=False, extra=1)
    
    if request.method == 'POST':
        form = ipr_form_mapping[ipr.get_classname()](request.POST)
        #draft_formset = DraftFormset(request.POST, instance=IprDisclosureBase(), prefix='draft')
        #rfc_formset = RfcFormset(request.POST, instance=IprDisclosureBase(), prefix='rfc')
        draft_formset = DraftFormset(request.POST, instance=base, prefix='draft')
        rfc_formset = RfcFormset(request.POST, instance=base, prefix='rfc')
        if form.is_valid() and draft_formset.is_valid() and rfc_formset.is_valid(): 
            disclosure = form.save(commit=False)
            if not request.user.is_anonymous():
                disclosure.by = request.user.person
            else:
                disclosure.by = Person.objects.get(name="(System)")
            disclosure.state = IprDisclosureStateName.objects.get(slug='pending')
            disclosure.save()
            
            draft_formset = DraftFormset(request.POST.copy(), instance=disclosure.get_child(), prefix='draft', save_as_new=True)
            draft_formset.save()
            rfc_formset = RfcFormset(request.POST.copy(), instance=disclosure.get_child(), prefix='rfc', save_as_new=True)
            rfc_formset.save()

            set_disclosure_title(disclosure)
            disclosure.save()
            
            # create updates relationship
            RelatedIpr.objects.create(source=disclosure,
                                      target=ipr,
                                      relationship=DocRelationshipName.objects.get(slug='updates'))
                                      
            # send email notification
            # TODO
            
            return render("ipr/submitted.html", context_instance=RequestContext(request))

    else:
        form = ipr_form_mapping[ipr.get_classname()](instance=ipr)
        draft_formset = DraftFormset(queryset=IprDocRel.objects.exclude(document__name__startswith='rfc'),instance=base, prefix='draft')
        rfc_formset = RfcFormset(queryset=IprDocRel.objects.filter(document__name__startswith='rfc'),instance=base, prefix='rfc')
        
    return render("ipr/details_edit.html",  {
        'form': form,
        'draft_formset':draft_formset,
        'rfc_formset':rfc_formset},
        context_instance=RequestContext(request)
    )