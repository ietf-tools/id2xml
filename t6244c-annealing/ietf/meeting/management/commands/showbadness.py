"""
Runs the automatic placement code (simulated annealing of glass)
for a given meeting number, using a schedule given by the schedule database ID.

for help on this file:
https://docs.djangoproject.com/en/dev/howto/custom-management-commands/

"""

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import cProfile, pstats, io
import os
import sys
import gzip
import time
import csv
import codecs
from ietf.meeting.models import Schedule

class Command(BaseCommand):
    args = '<schedule-ID>'
    help = 'show current fitness evaluation'
    stderr = sys.stderr
    stdout = sys.stdout

    verbose = False
    profile = False
    permit_movement = False

    option_list = BaseCommand.option_list + (
        make_option('--profile',
            action='store_true',
            dest='profile',
            default=False,
            help='Enable verbose mode'),
        make_option('--verbose',
            action='count',
            dest='verbose',
            default=False,
            help='Enable verbose mode'),
        make_option('--replace',
            action='store_true',
            dest='permit_movement',
            default=False,
            help='Enable overwrite mode, otherwise duplicate files ignored'),
        )

    def handle(self, *labels, **options):
        self.verbose  = options.get('verbose', 1)

        pr = cProfile.Profile()
        for schedule_id in labels:
            try:
                schedule = Schedule.objects.get(pk=schedule_id)
            except Schedule.DoesNotExist:
                self.stdout.write('Schedule id#%u not found' % (schedule_id))

            from settings import BADNESS_UNPLACED
            fitness=0
            pr.enable()

            badnesses = dict()
            for session in schedule.meeting.sessions_that_can_meet.all():
                badnesses[session] = None
            schedule.calc_badness()
            for ss in schedule.scheduledsession_set.all():
                if ss.session:
                    badnesses[ss.session]=ss
            pr.disable()
            for sess,ss in badnesses.items():
                time = "unplaced"
                badness= BADNESS_UNPLACED
                if ss is not None:
                    time = ss.timeslot.time
                    badness=ss.badness
                if self.verbose>0 and (self.verbose>1 or badness > 0):
                    self.stdout.write('  %-16s at %24s  badness: %9u\n' % (sess.group.acronym,time,badness))
            self.stdout.write('total                                           badness: %9u\n' % (schedule.badness))
            
        ps = pstats.Stats(pr)
        #ps.print_stats()
                    

            
            
