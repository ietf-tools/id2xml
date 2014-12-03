
def iprs_from_docs(aliases,**kwargs):
    """Returns a list of IPRs related to doc aliases"""
    iprdocrels = []
    for alias in aliases:
        if alias.document.ipr(**kwargs):
            iprdocrels += alias.document.ipr(**kwargs)
    return list(set([i.disclosure for i in iprdocrels]))
    
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