# Copyright (C) 2009 Nokia Corporation and/or its subsidiary(-ies).
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

from django.http import HttpResponse, HttpResponsePermanentRedirect, HttpResponseForbidden, Http404
from django.views.generic.list_detail import object_list
from django.db.models import Q
from django.http import Http404
from django.template import RequestContext, loader, Context
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.html import escape
from django.views.generic.list_detail import object_detail
from ietf.idtracker.models import Acronym, IETFWG, InternetDraft, Rfc, IDInternal, BallotInfo, IESGComment, IESGDiscuss, Area, Position, IESGLogin
from ietf.docs.forms import SearchForm
from ietf.idindex.models import alphabet, orgs, orgs_dict
from ietf.utils import orl, flattenl, normalize_draftname
from ietf.idtracker.forms import IDSearch
from ietf.docs.models import RfcIndex, DraftVersions
from django.template.defaultfilters import truncatewords_html
from ietf.idtracker.templatetags.ietf_filters import format_textarea, fill
import re
from ietf.docs.document_object import create_document_object, JsonResponse, BALLOT_ACTIVE_STATES, Document
from django.utils import simplejson
from ietf.iesg.views import get_doc_section
from ietf.iesg.models import TelechatDates
from ietf.docs.markup_draft import markup_draft
from ietf.settings import INTERNET_DRAFT_PATH

def search_query(query):
    drafts = query['activeDrafts'] or query['oldDrafts']
    if (not drafts) and (not query['rfcs']):
        return []

    # Start by search InternetDrafts
    idresults = []
    rfcresults = []
    MAX = 500
    maxReached = False

    prefix = ""
    q_objs = []
    if query['ad'] or query['state'] or query['subState']:
        prefix = "draft__"
    if query['ad']:
        q_objs.append(Q(job_owner=query['ad']))
    if query['state']:
        q_objs.append(Q(cur_state=query['state']))
    if query['subState']:
        q_objs.append(Q(cur_sub_state=query['subState']))
    
    if query['filename']:
        q_objs.append(Q(**{prefix+"filename__icontains":query['filename']})|Q(**{prefix+"title__icontains":query['filename']}))
    if query['author']:
        q_objs.append(Q(**{prefix+"authors__person__last_name__icontains":query['author']}))
    if query['group']:
        q_objs.append(Q(**{prefix+"group__acronym":query['group']}))
    if query['area']:
        q_objs.append(Q(**{prefix+"group__ietfwg__areagroup__area":query['area']}))
    if (not query['rfcs']) and query['activeDrafts'] and (not query['oldDrafts']):
        q_objs.append(Q(**{prefix+"status":1}))
    elif query['rfcs'] and query['activeDrafts'] and (not query['oldDrafts']):
        q_objs.append(Q(**{prefix+"status":1})|Q(**{prefix+"status":3}))
    elif query['rfcs'] and (not drafts):
        q_objs.append(Q(**{prefix+"status":3}))
    if prefix:
        q_objs.append(Q(rfc_flag=0))
        matches = IDInternal.objects.filter(*q_objs)
    else:
        matches = InternetDraft.objects.filter(*q_objs)
    if not query['activeDrafts']:
        matches = matches.exclude(Q(**{prefix+"status":1}))
    if not query['rfcs']:
        matches = matches.exclude(Q(**{prefix+"status":3}))
    if prefix:
        matches = [id.draft for id in matches[:MAX]]
    else:
        matches = matches[:MAX]
    if len(matches) == MAX:
        maxReached = True
    for id in matches:
        if id.status.status == 'RFC':
            rfcresults.append([id.rfc_number, id, None, None])
        else:
            idresults.append([id])

    # Next, search RFCs
    if query['rfcs'] and not (query['ad'] or query['state'] or query['subState'] or query['area']):
        q_objs = []
        searchRfcIndex = True
        if query['filename']:
            r = re.compile("^\s*(?:RFC)?\s*(\d+)\s*$", re.IGNORECASE)
            m = r.match(query['filename'])
            if m:
                q_objs.append(Q(rfc_number__contains=m.group(1))|Q(title__icontains=query['filename']))
            else:
                q_objs.append(Q(title__icontains=query['filename']))
        # We prefer searching RfcIndex, but it doesn't have group info
        if query['group']:
            searchRfcIndex = False
            q_objs.append(Q(group_acronym=query['group']))
        if query['area']:
            # TODO: not implemented yet
            pass
        if query['author'] and searchRfcIndex:
            q_objs.append(Q(authors__icontains=query['author']))
        elif query['author']:
            q_objs.append(Q(authors__person__last_name__icontains=query['author']))
        if searchRfcIndex:
            matches = RfcIndex.objects.filter(*q_objs)[:MAX]
        else:
            matches = Rfc.objects.filter(*q_objs)[:MAX]
        if len(matches) == MAX:
            maxReached = True
        for rfc in matches:
            found = False
            for r2 in rfcresults:
                if r2[0] == rfc.rfc_number:
                    if searchRfcIndex:
                        r2[3] = rfc
                    else:
                        r2[2] = rfc
                    found = True
            if not found:
                if searchRfcIndex:
                    rfcresults.append([rfc.rfc_number, None, None, rfc])
                else:
                    rfcresults.append([rfc.rfc_number, None, rfc, None])
                    
    # Find missing InternetDraft objects
    for r in rfcresults:
        if not r[1]:
            ids = InternetDraft.objects.filter(rfc_number=r[0])
            if len(ids) >= 1:
                r[1] = ids[0]
        if not r[1] and r[3] and r[3].draft:
            ids = InternetDraft.objects.filter(filename=r[3].draft)
            if len(ids) >= 1:
                r[1] = ids[0]

    # Finally, find missing RFC objects
    for r in rfcresults:
        if not r[2]:
            rfcs = Rfc.objects.filter(rfc_number=r[0])
            if len(rfcs) >= 1:
                r[2] = rfcs[0]
        if not r[3]:
            rfcs = RfcIndex.objects.filter(rfc_number=r[0])
            if len(rfcs) >= 1:
                r[3] = rfcs[0]

    results = []
    for res in idresults+rfcresults:
        if len(res)==1:
            doc = Document(draft=res[0])
        else:
            doc = Document(draft=res[1], rfc=res[2], rfcIndex=res[3])
        results.append(doc)
    results.sort(key=lambda obj: obj.friendlyGroupSort)
    meta = {}
    if maxReached:
        meta['max'] = MAX
    return (results,meta)

def search_results(request, json=False):
    form = SearchForm(request.REQUEST)
    if not form.is_valid():
        return HttpResponse("form not valid?", mimetype="text/plain")
    (results,meta) = search_query(form.clean_data)
    if json or (('json' in request.REQUEST) and request.REQUEST['json']):
        return JsonResponse(request, results)
    else:
        return render_to_response('docs/search_results.html', {'docs':results, 'meta':meta}, context_instance=RequestContext(request, {}, [ad_id_processor]))

def search_main(request):
    form = SearchForm()
    return render_to_response('docs/search_main.html', {'form':form})

def iesg_select_ad(request):
    ads = [{"adId":ad.id, "adName":"%s %s" % (ad.first_name, ad.last_name)} for ad in IESGLogin.objects.filter(user_level=1).order_by('last_name')]
    return render_to_response("docs/iesg_select_ad.html", {'ads':ads})

def iesg_main(request):
    x = ad_id_processor(request)
    if not x["adId"]:
        return iesg_select_ad(request)
    form = SearchForm()
    return render_to_response('docs/iesg_main.html', {'form':form})

def show_rfc(request, rfcNumber):
    f = open("/www/tools.ietf.org/html/rfc"+str(rfcNumber)+".html")
    try:
        content = f.read()
        #i = content.index("<pre>")
        #j = content.index("</pre>")
        #content = content[i:j]
        return HttpResponse(content)
        #return render_to_response('docs/view_rfc.html', {'htmlContent':content });
    finally:
        f.close()

def show_doc(request, name):
    name = normalize_draftname(name)
    r = re.compile("^rfc([0-9]+)$")
    m = r.match(name)
    if m:
        return show_rfc(request, int(m.group(1)))
    r = re.compile("^draft-[-A-Za-z0-9]+$")
    if not r.match(name):
        raise Http404
    id = get_object_or_404(InternetDraft, filename=name)
    doc = Document(draft=id)
    info = {}
    if doc.draftName.startswith("draft-iab-"):
        stream = " (IAB document)"
    elif doc.draftName.startswith("draft-irtf-"):
        stream = " (IRTF document)"
    elif 'rfcEditorSubmission' in doc.__dict__ and doc.rfcEditorSubmission:
        stream = " (Independent submission via RFC Editor)"
    elif doc.group:
        stream = " ("+doc.group.upper()+" WG document)"
    else:
        stream = " (Individual document)"

    if id.status.status == "Active":
        info['type'] = "Active Internet-Draft"+stream
    else:
        info['type'] = "Old Internet-Draft"+stream
    if id.revision != "00":
        info['prevRevision'] = ("%02d" % (int(id.revision)-1))
    info['contentPresent'] = False
    content1 = None
    content2 = None
    if id.status.status == "Active":
        info['contentActive'] = True
        try:
            f = open(INTERNET_DRAFT_PATH+name+"-"+id.revision+".txt")
            content = f.read()
            (content1, content2) = markup_draft(content)
            info['contentPresent'] = True
        except IOError:
            content1 = "Error - can't find "+name+"-"+id.revision+".txt"
        finally:
            if f:
                f.close()
    else:
        info['contentActive'] = False
            
    return render_to_response('docs/view_id.html', {'content1':content1,
                                                    'content2':content2,
                                                    'id':id, 'info':info,
                                                    'doc':doc});


def view_comments(request, name):
    name = normalize_draftname(name)
    id = get_object_or_404(IDInternal, draft__filename=name)
    results = []
    commentNumber = 0
    for comment in id.public_comments():
        info = {}
        r = re.compile(r'^(.*) by (?:<b>)?([A-Z]\w+ [A-Z]\w+)(?:</b>)?$')
        m = r.match(comment.comment_text)
        if m:
            info['text'] = m.group(1)
            info['by'] = m.group(2)
        else:
            info['text'] = comment.comment_text
            info['by'] = comment.get_username()
        info['textSnippet'] = truncatewords_html(format_textarea(fill(info['text'], 80)), 25)
        info['snipped'] = info['textSnippet'][-3:] == "..."
        info['commentNumber'] = commentNumber
        commentNumber = commentNumber + 1
        results.append({'comment':comment, 'info':info})
    return render_to_response('docs/comments.html', {'comments':results})
        
def view_ballot(request, name):
    name = normalize_draftname(name)
    id = get_object_or_404(IDInternal, draft__filename=name)
    try:
        if not id.ballot.ballot_issued:
            raise Http404
    except BallotInfo.DoesNotExist:
        raise Http404

    doc = Document(draft=id)
    positions = list(doc.ballotPositions)
    position_values = ["Discuss", "Yes", "No Objection", "Abstain", "Recuse", None]
    positions.sort(key=lambda p: str(position_values.index(p['position']))+p['adName'].split()[-1])
    #position_values[-1] = "No Record"

    return render_to_response('docs/ballot.html', {'positions':positions, 'positionValues':position_values, 'doc':doc})
        
def view_writeup(request, name):
    name = normalize_draftname(name)
    id = get_object_or_404(IDInternal, draft__filename=name)
    try:
        if not id.ballot.ballot_issued:
            raise Http404
    except BallotInfo.DoesNotExist:
        raise Http404
    
    return render_to_response('docs/writeup.html', {'approvalText':id.ballot.approval_text, 'ballotWriteup':id.ballot.ballot_writeup})

def view_versions(request, name):
    name = normalize_draftname(name)
    draft = get_object_or_404(InternetDraft, filename=name)

    ov = []
    ov.append({"draftName":draft.filename, "revision":draft.revision, "revisionDate":draft.revision_date})
    for d in [draft]+list(draft.replaces_set.all()):
        for v in DraftVersions.objects.filter(filename=d.filename).order_by('-revision'):
            if (d.filename == draft.filename) and (draft.revision == v.revision):
                continue
            ov.append({"draftName":d.filename, "revision":v.revision, "revisionDate":v.revision_date})
    
    return render_to_response('docs/versions.html', {'versions':ov})
        
def view_data_json(request, name):
    name = normalize_draftname(name)
    id = get_object_or_404(InternetDraft, filename=name)
    doc = Document(draft=id)
    return JsonResponse(request, doc)


def get_agenda_docs(date):
    matches = IDInternal.objects.filter(telechat_date=date,primary_flag=1,agenda=1)
    idmatches = matches.filter(rfc_flag=0).order_by('ballot_id')
    rfcmatches = matches.filter(rfc_flag=1).order_by('ballot_id')
    res = {}
    for id in list(idmatches)+list(rfcmatches):
        section_key = "s"+get_doc_section(id)
        if section_key not in res:
            res[section_key] = []
        if id.note:
            id.note = str(id.note).replace("\240","&nbsp;")
        res[section_key].append(Document(draft=id))
    return res
    #TODO: Does not handle rfcs properly, create_document_object
    #expects also rfc= argument

def ad_id_processor(request):
    if "adId" in request.COOKIES:
        adId = int(request.COOKIES["adId"])
        if adId > 0:
            return {"adId":adId}
    return {"adId":None}

def telechat_docs(request):
    dates = TelechatDates.objects.all()[0]
    if "adId" in request.COOKIES:
        adId = int(request.COOKIES["adId"])
        if adId <= 0:
            adId = None
    else:
        adId = None
    telechats = []
    for date in (dates.date1,dates.date2,dates.date3,dates.date4):
        docs = get_agenda_docs(date)
        telechats.append({'date':str(date), 'docs':docs})
    return render_to_response('docs/telechat_docs.html', {'telechats':telechats}, context_instance=RequestContext(request, {}, [ad_id_processor]))

def discusses(request):
    ad_id = 111 #int(request.REQUEST['ad'])
    positions = Position.objects.filter(ad=ad_id).filter(discuss=1)
    res = []
    for p in positions:
        try:
            draft = p.ballot.drafts.filter(primary_flag=1).filter(cur_state__state__in=BALLOT_ACTIVE_STATES)
            if len(draft) > 0:
                doc = Document(draft=draft[0])
                res.append(doc)
        except IDInternal.DoesNotExist:
            pass
    return render_to_response('docs/discusses.html', {'docs':res}, context_instance=RequestContext(request, {}, [ad_id_processor]))

