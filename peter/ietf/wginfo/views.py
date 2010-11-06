# Copyright The IETF Trust 2008, All Rights Reserved

# Portion Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved. Contact: Pasi Eronen <pasi.eronen@nokia.com>
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions 
# are met:
# 
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
# 
#  * Neither the name of the Nokia Corporation and/or its
#    subsidiary(-ies) nor the names of its contributors may be used
#    to endorse or promote products derived from this software
#    without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from ietf.idtracker.models import Area, IETFWG
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.http import HttpResponse
from ietf.idrfc.views_search import SearchForm, search_query
from ietf.idrfc.idrfc_wrapper import IdRfcWrapper, RfcWrapper, IdWrapper
from ietf.ipr.models import IprDetail
from ietf.idrfc.models import RfcIndex
from ietf.idtracker.models import InternetDraft


def wg_summary_acronym(request):
    areas = Area.active_areas()
    wgs = IETFWG.objects.filter(status=IETFWG.ACTIVE)
    return HttpResponse(loader.render_to_string('wginfo/1wg-summary-by-acronym.txt', {'area_list': areas, 'wg_list': wgs}),mimetype='text/plain; charset=UTF-8')

def wg_summary_area(request):
    wgs = IETFWG.objects.filter(status='1',start_date__isnull=False)
    return HttpResponse(loader.render_to_string('wginfo/1wg-summary.txt', {'wg_list': wgs}),mimetype='text/plain; charset=UTF-8')

def wg_charters(request):
    wgs = IETFWG.objects.filter(status='1',start_date__isnull=False)
    return HttpResponse(loader.render_to_string('wginfo/1wg-charters.txt', {'wg_list': wgs}),mimetype='text/plain; charset=UTF-8')

def wg_charters_by_acronym(request):
    wgs = IETFWG.objects.filter(status='1',start_date__isnull=False)
    return HttpResponse(loader.render_to_string('wginfo/1wg-charters-by-acronym.txt', {'wg_list': wgs}),mimetype='text/plain; charset=UTF-8')

def wg_dir(request):
    areas = Area.active_areas()
    return render_to_response('wginfo/wg-dir.html', {'areas':areas}, RequestContext(request))

def wg_documents(request, acronym):
    wg = get_object_or_404(IETFWG, group_acronym__acronym=acronym, group_type=1)
    concluded = (wg.status_id != 1)
    
    # get RFCs 
    rfcs = RfcIndex.objects.filter( wg=wg.group_acronym.acronym)
    docs = []
    for r in rfcs:
        rw = RfcWrapper(r)
        idrfc = IdRfcWrapper(None, rw)
        docs.append( idrfc )
        
    # get the WG drafts 
    drafts = InternetDraft.objects.filter( group__acronym=wg.group_acronym.acronym, status__status='Active')

    for id in drafts:
        dw = IdWrapper(id)
        d = IdRfcWrapper( dw, None)
        docs.insert(0, d)
      
    # now get the related docs
    docs_related_pruned = []
    related = InternetDraft.objects.filter( filename__contains=wg.group_acronym.acronym,  status__status='Active')
    for r in related:
        dw = IdWrapper(r)
        d = IdRfcWrapper( dw, None)
        parts = d.id.draft_name.split("-", 2);
        # canonical form draft-<name|ietf>-wg-etc
        if ( len(parts) >= 3):
            if parts[1] != "ietf" and parts[2].startswith(wg.group_acronym.acronym+"-"):
                docs_related_pruned.append(d)
 
    return render_to_response('wginfo/wg_documents.html', {'wg': wg, 'concluded':concluded, 'selected':'documents', 'docs':docs,  
                                                           'docs_related':docs_related_pruned }, RequestContext(request))

def wg_charter(request, acronym):
    wg = get_object_or_404(IETFWG, group_acronym__acronym=acronym, group_type=1)
    concluded = (wg.status_id != 1)
    return render_to_response('wginfo/wg_charter.html', {'wg': wg, 'concluded':concluded, 'selected':'charter'}, RequestContext(request))
