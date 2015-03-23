# import re
import sys
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from django.template.loader import render_to_string

from ietf.doc.models import Document

def write(fn, new):
    try:
        f = open(fn)
        old = f.read().decode('utf-8')
        f.close
    except IOError:
        old = ""
    if old.strip() != new.strip():
        sys.stdout.write(os.path.basename(fn)+'\n')
        f = open(fn, "wb")
        f.write(new.encode('utf-8'))
        f.close()

class Command(BaseCommand):
    help = (u'Generate draft bibxml files, for xml2rfc references')

    def handle(self, *args, **options):
        documents = Document.objects.filter(type__slug='draft')
        bibxmldir = os.path.join(settings.BIBXML_BASE_PATH, 'bibxml3')
        if not os.path.exists(bibxmldir):
            os.makedirs(bibxmldir)

        doc_count = 0
        doc_alias_count = 0
        doc_rev_count = 0
        doc_rfc_count = 0
        doc_id_count = 0
        for doc in documents:
            doc_count = doc_count + 1
            for a in doc.docalias_set.all():
                doc_alias_count = doc_alias_count + 1
                if a.name.startswith('draft-'):
                    doc_id_count = doc_id_count + 1
                    for n in range(int(doc.rev)+1):
                        doc_rev_count = doc_alias_count + 1
                        print "%s-%02d" % (a.name, n)
                        ref_text = render_to_string('doc/bibxml3.xml', {'doc': doc, 'doc_bibtype':'I-D'})
                        doc_without_draft = doc.name[6:]
                        ref_file_name = os.path.join(bibxmldir, 'reference.%s.xml' % (doc_without_draft))
                        ref_ID_file_name = os.path.join(bibxmldir, 'reference.I-D.%s.xml' % (doc_without_draft))
                        ref_rev_file_name = os.path.join(bibxmldir, 'reference.I-D.%s-%s.xml' % (doc.name, doc.rev))
                        write(ref_file_name, ref_text)
                        write(ref_ID_file_name, ref_text)
                        write(ref_rev_file_name, ref_text)
                    print "<<<< %s %s" % (doc.name, doc.rev)
                else:
                    doc_rfc_count = doc_rfc_count + 1
                    print "Skipping %s" % a.name
        print "doc_count = %d" % doc_count
        print "doc_alias_count = %d" % doc_alias_count
        print "doc_rev_count = %d" % doc_rev_count
        print "doc_rfc_count = %d" % doc_rfc_count
        print "doc_id_count = %d" % doc_id_count

#	    if not doc.name.startswith('rfc'):
#	       ref_text = render_to_string('doc/bibxml3.xml', {'doc': doc, 'doc_bibtype':'I-D'})
#               doc_without_draft = re.sub(r'^draft-', '', doc.name)
#	       ref_file_name = os.path.join(bibxmldir, 'reference.%s.xml' % (doc_without_draft))
#	       ref_rev_file_name = os.path.join(bibxmldir, 'reference.I-D.%s-%s.xml' % (doc.name, doc.rev))
#	       write(ref_file_name, ref_text)
#	       write(ref_rev_file_name, ref_text)
#            sys.stdout.write("<<<< %s %s\n" % (doc.name, doc.rev))
#            for doc2 in doc.all_relations_that('new_revision'):
#                sys.stdout.write("    >>>> %s %s\n" % (doc2.name, doc2.rev))


#           ref_text = render_to_string('doc/bibxml.xml', {'doc': doc, 'doc_bibtype':'I-D'})
#           ref_file_name = os.path.join(bibxmldir, 'reference.I-D.%s.xml' % (doc.name, ))
#           ref_rev_file_name = os.path.join(bibxmldir, 'reference.I-D.%s-%s.xml' % (doc.name, doc.rev))
#           write(ref_file_name, ref_text)
#           write(ref_rev_file_name, ref_text)
                
