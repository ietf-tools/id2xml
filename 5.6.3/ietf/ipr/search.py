# Copyright The IETF Trust 2007, All Rights Reserved

import codecs
import re
import os.path

from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response as render
from django.template import RequestContext
from django.conf import settings

from ietf.ipr.models import IprDocAlias, IprDetail # remove
from ietf.ipr.models import IprDocRel, IprDisclosureBase
from ietf.ipr.related import related_docs
from ietf.utils.draft_search import normalize_draftname
from ietf.group.models import Group
from ietf.doc.models import DocAlias

def iprs_from_docs(docs):
    iprs = []
    for doc in docs:
        disclosures = [ x.disclosure for x in IprDocRel.objects.filter(document=doc, disclosure__state__in=('posted','removed')) ]
        doc.iprs = None
        if disclosures:
            doc.iprs = disclosures
            iprs += disclosures
    iprs = list(set(iprs))
    return iprs, docs

def patent_file_search(url, q):
    if url:
        fname = url.split("/")[-1]
        fpath = os.path.join(settings.IPR_DOCUMENT_PATH, fname)
        #print "*** Checking file", fpath
        if os.path.isfile(fpath):
            #print "*** Found file", fpath            
            file = codecs.open(fpath, mode='r', encoding='utf-8', errors='replace')
            text = file.read()
            file.close
            return q in text
    return False

def search(request):
    wgs = Group.objects.filter(type="wg").select_related().order_by("acronym")

    search_type = request.GET.get("option")
    if search_type:
        docid = request.GET.get("id") or request.GET.get("id_document_tag") or ""
        initial = {}
        iprs = docs = doc = None
        q = ""
        for key, value in request.GET.items():
            if key.endswith("search"):
                q = value

        if q or docid:
            # Search by RFC number or draft-identifier
            # Document list with IPRs
            if search_type in ["document_search", "rfc_search"]:
                doc = q

                if docid:
                    start = DocAlias.objects.filter(name=docid)
                else:
                    if search_type == "document_search":
                        q = normalize_draftname(q)
                        start = DocAlias.objects.filter(name__contains=q, name__startswith="draft")
                    elif search_type == "rfc_search":
                        start = DocAlias.objects.filter(name="rfc%s" % q.lstrip("0"))

                if len(start) == 1:
                    first = start[0]
                    doc = str(first)
                    docs = related_docs(first)
                    iprs, docs = iprs_from_docs(docs)
                    template = "ipr/search_doc_result.html"
                elif start:
                    docs = start
                    template = "ipr/search_doc_list.html"
                else:
                    template = "ipr/search_doc_result.html"

            # Search by legal name
            # IPR list with documents
            elif search_type == "patent_search":
                iprs = IprDisclosureBase.objects.filter(holder_legal_name__icontains=q, state_id__in=('posted','removed'))
                template = "ipr/search_holder_result.html"
                
            # Search by patents field or content of emails for patent numbers
            # IPR list with documents
            elif search_type == "patent_info_search":
                iprs = IprDisclosureBase.objects.filter(state_id__in=('posted','removed'))
                iprs = iprs.filter(Q(holderiprdisclosure__patent_info__icontains=q) |
                                   Q(thirdpartyiprdisclosure__patent_info__icontains=q) |
                                   Q(nondocspecificiprdisclosure__patent_info__icontains=q))
                template = "ipr/search_patent_result.html"

            # Search by wg acronym
            # Document list with IPRs
            elif search_type == "wg_search":
                docs = list(DocAlias.objects.filter(document__group__acronym=q))
                related = []
                for doc in docs:
                    doc.product_of_this_wg = True
                    related += related_docs(doc)
                iprs, docs = iprs_from_docs(list(set(docs+related)))
                docs = [ doc for doc in docs if doc.iprs ]
                template = "ipr/search_wg_result.html"
                
            # Search by rfc and id title
            # Document list with IPRs
            elif search_type == "title_search":
                docs = list(DocAlias.objects.filter(document__title__icontains=q))
                related = []
                for doc in docs:
                    related += related_docs(doc)
                iprs, docs = iprs_from_docs(list(set(docs+related)))
                docs = [ doc for doc in docs if doc.iprs ]
                template = "ipr/search_doctitle_result.html"

            # Search by title of IPR disclosure
            # IPR list with documents
            elif search_type == "ipr_title_search":
                initial['ipr_title_search'] = q
                iprs = IprDisclosureBase.objects.filter(title__icontains=q, state_id__in=('posted','removed'))
                template = "ipr/search_iprtitle_result.html"

            else:
                raise Http404("Unexpected search type in IPR query: %s" % search_type)
                
            # sort and render response
            iprs = [ ipr for ipr in iprs if not ipr.updated_by.all() ]
            iprs = sorted(iprs, key=lambda x: (x.submitted_date,x.id), reverse=True)
            docs = sorted(docs, key=lambda x: max([ipr.submitted_date for ipr in x.iprs]), reverse=True)
            return render(template, {
                "q": q,
                "iprs": iprs,
                "docs": docs,
                "doc": doc,
                "initial": initial},
                context_instance=RequestContext(request)
            )
                                  
        return HttpResponseRedirect(request.path)

    return render("ipr/search.html", {"wgs": wgs}, context_instance=RequestContext(request))
