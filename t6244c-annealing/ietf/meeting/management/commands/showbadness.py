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

            fitness=0
            pr.enable()
            schedule.calc_badness()
            pr.disable()
            for ss in schedule.scheduledsession_set.all():
                if self.verbose>0 and ss.session and (self.verbose>1 or ss.badness > 0):
                    self.stdout.write('  %-16s at %24s  badness: %u\n' % (ss.session.group.acronym,
                                                                        ss.timeslot.time,
                                                                        ss.badness))
            self.stdout.write('total                                           badness: %u\n' % (schedule.badness))
            
        ps = pstats.Stats(pr)
        #ps.print_stats()
                    

            
            
