from ietf.ipr.models import IprDocRel

def iprs_from_docs(docs,states=('posted','removed')):
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