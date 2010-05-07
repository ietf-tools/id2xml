#!/usr/bin/python

# boiler plate
import os, sys

one_dir_up = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))

sys.path.insert(0, one_dir_up)

from django.core.management import setup_environ
import settings
setup_environ(settings)

# script
from django.core.serializers import serialize
from idtracker.models import *

def output(name, qs):
    try:
        f = open(os.path.join(settings.BASE_DIR, "idrfc/fixtures/%s.xml" % name), 'w')
        f.write(serialize("xml", qs, indent=4))
        f.close()
    except:
        from django.db import connection
        from pprint import pprint
        pprint(connection.queries)
        raise

output("iesglogins", IESGLogin.objects.filter(login_name="klm"))
output("status", IDStatus.objects.all())
output("substates", IDSubState.objects.all())
output("states", IDState.objects.all())
output("idinternals", IDInternal.objects.filter(draft__filename="draft-ietf-mipshop-pfmipv6"))
output("internetdrafts", InternetDraft.objects.filter(filename="draft-ietf-mipshop-pfmipv6"))
