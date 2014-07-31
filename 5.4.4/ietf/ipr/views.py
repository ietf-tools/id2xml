# Copyright The IETF Trust 2007, All Rights Reserved

import os

from django.shortcuts import render_to_response as render, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.urlresolvers import reverse as urlreverse

from ietf.ipr.models import IprDisclosureBase, IprDetail, IprDocAlias, IprLicenseTypeName, SELECT_CHOICES, LICENSE_CHOICES
from ietf.ipr.view_sections import section_list_for_ipr

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

def showlist(request):
    disclosures = IprDetail.objects.all().prefetch_related("updates__updated", "updated_by__ipr")
    generic_disclosures  = disclosures.filter(status__in=[1,3], generic=1)
    specific_disclosures = disclosures.filter(status__in=[1,3], generic=0, third_party=0)
    thirdpty_disclosures = disclosures.filter(status__in=[1,3], generic=0, third_party=1)

    return render("ipr/list.html",
        {
            'generic_disclosures' : generic_disclosures.order_by(* ['-submitted_date', ] ),
            'specific_disclosures': specific_disclosures.order_by(* ['-submitted_date', ] ),
            'thirdpty_disclosures': thirdpty_disclosures.order_by(* ['-submitted_date', ] ),
        }, context_instance=RequestContext(request) )

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

