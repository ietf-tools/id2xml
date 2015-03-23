import sys
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from django.template.loader import render_to_string

from ietf.doc.models import Document, DocAlias

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
        aliases = DocAlias.objects.filter(name__startswith='rfc')
        # aliases = DocAlias.objects.filter(name='rfc11')
        print("Document count: %s" % aliases.count())
        bibxmldir = os.path.join(settings.BIBXML_BASE_PATH, 'bibxml')
        rfcdir = '/www/tools.ietf.org/rfc'
        isApril1 = False
        if not os.path.exists(bibxmldir):
            os.makedirs(bibxmldir)
        for alias in aliases:
            doc = alias.document
            num = alias.name[3:]
            num4 = "%04d" % (int(num))
            rfcfiletxt = os.path.join(rfcdir, 'rfc%d.txt' % (int(num)))
            try:
                rfcsizetxt = os.stat(rfcfiletxt).st_size
            except:
                rfcsizetxt = 0
            rfcfilepdf = os.path.join(rfcdir, 'rfc%d.pdf' % (int(num)))
            try:
                rfcsizepdf = os.stat(rfcfilepdf).st_size
            except:
                rfcsizepdf = 0
            rfcfileps = os.path.join(rfcdir, 'rfc%d.ps' % (int(num)))
            try:
                rfcsizeps = os.stat(rfcfileps).st_size
            except:
                rfcsizeps = 0
            ref_text = render_to_string('doc/bibxml.xml', {
                    'doc': doc, 'doc_bibtype':'rfc', 'alias': alias, 'num': num, 'num4': num4,
                    'rfcsizetxt': rfcsizetxt, 'rfcsizepdf': rfcsizepdf, 'rfcsizeps': rfcsizeps,
                    'isApril1': isApril1
                    })
            ref_file_name = os.path.join(bibxmldir, 'reference.RFC.%04d.xml' % (int(num), ))
            write(ref_file_name, ref_text)
