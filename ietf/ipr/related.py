# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf import settings
from django.db.models import Q
from ietf.idtracker.models import InternetDraft, Rfc
from ietf.doc.models import DocAlias
from ietf.ipr.models import IprDraftProxy

inverse = {
            'updates': 'is_updated_by',
            'is_updated_by': 'updates',
            'obsoletes': 'is_obsoleted_by',
            'is_obsoleted_by': 'obsoletes',
            'replaces': 'is_replaced_by',
            'is_replaced_by': 'replaces',            
            'is_rfc_of': 'is_draft_of',
            'is_draft_of': 'is_rfc_of',
        }

display_relation = {
            'updates':          'that updated',
            'is_updated_by':    'that was updated by',
            'obsoletes':        'that obsoleted',
            'is_obsoleted_by':  'that was obsoleted by',
            'replaces':         'that replaced',
            'is_replaced_by':   'that was replaced by',
            'is_rfc_of':        'which came from',
            'is_draft_of':      'that was published as',
        }

def set_related(obj, rel, target):
    #print obj, rel, target
    # remember only the first relationship we find.
    if not hasattr(obj, "related"):
        obj.related = target
        obj.relation = display_relation[rel]
    return obj

def set_relation(first, rel, second):
    set_related(first, rel, second)
    set_related(second, inverse[rel], first)

def related_docs(alias, _):
    from ietf.doc.proxy import DraftLikeDocAlias
    results = [x for x in DraftLikeDocAlias.objects.filter(document=alias.document)]
    rels = alias.document.all_relations_that_doc(['replaces','obs'])
    for rel in rels:
        res = DraftLikeDocAlias.objects.get(name=rel.target.document.name,document=rel.target.document)
        rel_aliases = [res] + list(DraftLikeDocAlias.objects.filter(document=res.document)) 
        for x in rel_aliases:
            x.related = DraftLikeDocAlias.objects.get(name=rel.source.name,document=rel.source)
            x.relation = rel.relationship.revname
        results += rel_aliases 
    return list(set(results))
# THAT IS TERRIBLE - REDO THAT not using doc.proxy

def old_related_docs(alias, _):
    """Get related document aliases to given alias through depth-first search."""
    from ietf.doc.models import RelatedDocument
    from ietf.doc.proxy import DraftLikeDocAlias

    mapping = dict(
        updates='that updated',
        obs='that obsoleted',
        replaces='that replaced',
        )
    inverse_mapping = dict(
        updates='that was updated by',
        obs='that was obsoleted by',
        replaces='that was replaced by',
        )
    
    res = [ alias ]
    remaining = [ alias ]
    while remaining:
        a = remaining.pop()
        related = RelatedDocument.objects.filter(relationship__in=mapping.keys()).filter(Q(source=a.document) | Q(target=a))
        for r in related:
            if r.source == a.document:
                found = DraftLikeDocAlias.objects.filter(pk=r.target_id)
                inverse = True
            else:
                found = DraftLikeDocAlias.objects.filter(document=r.source)
                inverse = False

            for x in found:
                if not x in res:
                    x.related = a
                    x.relation = (inverse_mapping if inverse else mapping)[r.relationship_id]
                    res.append(x)
                    remaining.append(x)

        # there's one more source of relatedness, a draft can have been published
        aliases = DraftLikeDocAlias.objects.filter(document=a.document).exclude(pk__in=[x.pk for x in res])
        for oa in aliases:
            rel = None
            if a.name.startswith("rfc") and oa.name.startswith("draft"):
                rel = "that was published as"
            elif a.name.startswith("draft") and oa.name.startswith("rfc"):
                rel = "which came from"

            if rel:
                oa.related = a
                oa.relation = rel
                res.append(oa)
                remaining.append(oa)

    return res

