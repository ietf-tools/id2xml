#!/usr/bin/env python

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ietf.settings")

from ietf.meeting.models import ScheduledSession,Session

for sname in set(ScheduledSession.objects.filter(session__meeting__number=91).values_list('schedule__name',flat=True)):
    for sess in Session.objects.filter(meeting__number=91,scheduledsession__schedule__name=sname):
        if sess.scheduledsession_set.filter(schedule__name=sname).exclude(extendedfrom__isnull=False).count()>1:
             workingset = sess.scheduledsession_set.filter(schedule__name=sname)
             print "Removing",workingset.exclude(pk=workingset.first().pk)
             workingset.exclude(pk=workingset.first().pk).delete()
