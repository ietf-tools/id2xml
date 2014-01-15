#!/usr/bin/env python

import os
import sys

# boiler plate
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
newdir = os.path.abspath(BASE_DIR + "/../..")
sys.stderr.write("path: %s\n" % newdir)

sys.path.append(newdir)

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stderr.write("path: %s\n" % path)
if not path in sys.path:
    sys.path.insert(0, path)

for p in sys.path:
    sys.stderr.write("item: %s\n" % p)


from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Cannot find 'settings.py' or 'settings_local.py'.\nUsually these are in the directory containing %r.\n" % __file__)
    sys.exit(1)

# script
from django.core.serializers import serialize


f = open("ietf/meeting/fixtures/new83.json", 'w')

# pick all name models directly out of the module
objects = []

from ietf.meeting.models  import Meeting, ResourceAssociation
from ietf.meeting.helpers import get_meeting
m83 = get_meeting(83)

objects += m83.room_set.all()
objects += ResourceAssociation.objects.all()
#objects += m83.session_set.all()
#objects += m83.schedule_set.all()

for sched in m83.schedule_set.all():
    objects += sched.scheduledsession_set.all()

f.write(serialize("json", objects, indent=4))
f.close()

