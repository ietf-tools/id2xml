# Copyright The IETF Trust 2007, All Rights Reserved

import codecs
import re
import os.path

from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response as render
from django.template import RequestContext
from django.conf import settings

from ietf.ietfauth.utils import has_role
from ietf.ipr.forms import SearchForm
from ietf.ipr.models import IprDocRel, IprDisclosureBase, IprDisclosureStateName
from ietf.ipr.related import related_docs
from ietf.utils.draft_search import normalize_draftname
from ietf.group.models import Group
from ietf.doc.models import DocAlias

# ----------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------
def iprs_from_docs(docs,states):
    """Returns a tuple of related iprs and original docs list"""
    iprs = []
    for doc in docs:
        disclosures = [ x.disclosure for x in IprDocRel.objects.filter(document=doc, disclosure__state__in=states) ]
        doc.iprs = None
        if disclosures:
            doc.iprs = disclosures
            iprs += disclosures
    iprs = list(set(iprs))
    return iprs, docs

# ----------------------------------------------------------------
# Views
# ----------------------------------------------------------------
def search(request):
    search_type = request.GET.get("submit")
    if search_type:
        form = SearchForm(request.GET)
        docid = request.GET.get("id") or request.GET.get("id_document_tag") or ""
        docs = doc = None
        iprs = []
        
        # set states
        states = request.GET.getlist('state',('posted',))
        if states == ['all']:
            states = IprDisclosureStateName.objects.values_list('slug',flat=True)
        
        # get query field
        q = ''
        if request.GET.get(search_type):
            q = request.GET.get(search_type)
            #assert False, (q,request.GET)

        if q or docid:
            # Search by RFC number or draft-identifier
            # Document list with IPRs
            if search_type in ["draft", "rfc"]:
                doc = q

                if docid:
                    start = DocAlias.objects.filter(name=docid)
                else:
                    if search_type == "draft":
                        q = normalize_draftname(q)
                        start = DocAlias.objects.filter(name__contains=q, name__startswith="draft")
                    elif search_type == "rfc":
                        start = DocAlias.objects.filter(name="rfc%s" % q.lstrip("0"))
                
                # one match
                if len(start) == 1:
                    #assert False, (docid,start)
                    first = start[0]
                    doc = str(first)
                    docs = related_docs(first)
                    iprs, docs = iprs_from_docs(docs,states)
                    template = "ipr/search_doc_result.html"
                # multiple matches, select just one
                elif start:
                    docs = start
                    template = "ipr/search_doc_list.html"
                # no match
                else:
                    template = "ipr/search_doc_result.html"

            # Search by legal name
            # IPR list with documents
            elif search_type == "holder":
                #assert False, (q,search_type,states)
                iprs = IprDisclosureBase.objects.filter(holder_legal_name__icontains=q, state_id__in=states)
                template = "ipr/search_holder_result.html"
                
            # Search by patents field or content of emails for patent numbers
            # IPR list with documents
            elif search_type == "patent":
                iprs = IprDisclosureBase.objects.filter(state_id__in=states)
                iprs = iprs.filter(Q(holderiprdisclosure__patent_info__icontains=q) |
                                   Q(thirdpartyiprdisclosure__patent_info__icontains=q) |
                                   Q(nondocspecificiprdisclosure__patent_info__icontains=q))
                template = "ipr/search_patent_result.html"

            # Search by wg acronym
            # Document list with IPRs
            elif search_type == "group":
                docs = list(DocAlias.objects.filter(document__group=q))
                related = []
                for doc in docs:
                    doc.product_of_this_wg = True
                    related += related_docs(doc)
                iprs, docs = iprs_from_docs(list(set(docs+related)),states)
                docs = [ doc for doc in docs if doc.iprs ]
                docs = sorted(docs, key=lambda x: max([ipr.submitted_date for ipr in x.iprs]), reverse=True)
                template = "ipr/search_wg_result.html"
                
            # Search by rfc and id title
            # Document list with IPRs
            elif search_type == "doctitle":
                docs = list(DocAlias.objects.filter(document__title__icontains=q))
                related = []
                for doc in docs:
                    related += related_docs(doc)
                iprs, docs = iprs_from_docs(list(set(docs+related)),states)
                docs = [ doc for doc in docs if doc.iprs ]
                docs = sorted(docs, key=lambda x: max([ipr.submitted_date for ipr in x.iprs]), reverse=True)
                template = "ipr/search_doctitle_result.html"

            # Search by title of IPR disclosure
            # IPR list with documents
            elif search_type == "iprtitle":
                iprs = IprDisclosureBase.objects.filter(title__icontains=q, state_id__in=states)
                template = "ipr/search_iprtitle_result.html"

            else:
                raise Http404("Unexpected search type in IPR query: %s" % search_type)
                
            # sort and render response
            iprs = [ ipr for ipr in iprs if not ipr.updated_by.all() ]
            if has_role(request.user, "Secretariat"):
                iprs = sorted(iprs, key=lambda x: (x.submitted_date,x.id), reverse=True)
                iprs = sorted(iprs, key=lambda x: x.state.order)
            else:
                iprs = sorted(iprs, key=lambda x: (x.submitted_date,x.id), reverse=True)
            
            
            return render(template, {
                "q": q,
                "iprs": iprs,
                "docs": docs,
                "doc": doc,
                "form":form},
                context_instance=RequestContext(request)
            )

        return HttpResponseRedirect(request.path)

    else:
        form = SearchForm(initial={'state':['all']})
        return render("ipr/search.html", {"form":form }, context_instance=RequestContext(request))
