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
from django.db.models import Q 
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

# base data
base = []
    
area_directors = AreaDirector.objects.all()
broken_logins = ('bthorson', 'members', 'iab')

base.extend(area_directors)
base.extend(PersonOrOrgInfo.objects.filter(areadirector__in=area_directors))
base.extend(IESGLogin.objects.filter(Q(login_name="klm") | Q(person__in=[a.person for a in area_directors])).exclude(login_name__in=broken_logins))
base.extend(IDStatus.objects.all())
base.extend(IDIntendedStatus.objects.all())
base.extend(IDSubState.objects.all())
base.extend(IDState.objects.all())
base.extend(WGType.objects.all())

output("base", base)


# specific draft
d = InternetDraft.objects.get(filename="draft-ietf-mipshop-pfmipv6")
draftdata = [d, d.idinternal, d.group, d.group.ietfwg]
ags = AreaGroup.objects.filter(group__exact=d.group.ietfwg.group_acronym)
draftdata.extend(ags)
draftdata.extend([a.area for a in ags])
draftdata.extend([a.area.area_acronym for a in ags])
output("draft", draftdata)
