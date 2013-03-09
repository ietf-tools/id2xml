#!/usr/bin/env python

from ietf import settings
from django.core import management
management.setup_environ(settings)

from ietf.doc.models import Document, DocAlias, RelatedDocument
from ietf.name.models import DocRelationshipName
from ietf.utils import draft
import os, re

def populate_refs( filename ):
    text = draft._gettext(filename)
    doc = draft.Draft(text, filename)

    docname = os.path.basename( filename )
    docname = re.sub( '\.txt$', '', docname )
    docname = re.sub( '-\d+$', '', docname )

    try:
	docAlias = DocAlias.objects.get( name=docname )
    except DocAlias.DoesNotExist, e:
	return { 'errors': [ e ] }
    # Delete the existing references.
    docAlias.document.related.filter( relateddocument__relationship__name__startswith='ref' ).delete()

    refs = doc.get_refs()

    warnings = []
    for ( ref, refType ) in refs.iteritems():
	refdoc = DocAlias.objects.filter( name=ref )
	count = refdoc.count()
	if count != 1:
	    warnings.append( "Found %d documents looking for %s" % ( count, ref ) )
	    continue
	relation = RelatedDocument( source=docAlias.document, target=refdoc[ 0 ],
				    relationship=DocRelationshipName.objects.get( slug='ref%s' % refType ) )
	relation.save()

    return { 'warnings': warnings }


def _main(files):
    for filename in files:
	ret = populate_refs( filename )
	if ret.get( 'warnings' ):
	    for warning in ret[ 'warnings' ]:
		print filename, 'Warning:', warning
	if ret.get( 'errors' ):
	    for error in ret[ 'errors' ]:
		print filename, 'Error:', error

if __name__ == "__main__":
    import sys
    _main( sys.argv[ 1: ] )
