"""
Runs the automatic placement code (simulated annealing of glass)
for a given meeting number, using a schedule given by the schedule database ID.

for help on this file:
https://docs.djangoproject.com/en/dev/howto/custom-management-commands/

"""

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
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
    permit_movement = False

    option_list = BaseCommand.option_list + (
        make_option('--verbose',
            action='store_true',
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

        for schedule_id in labels:
            try:
                schedule = Schedule.objects.get(pk=schedule_id)
            except Schedule.DoesNotExist:
                self.stdout.write('Schedule id#%u not found' % (schedule_id))

            fitness=0
            schedule.calc_badness()
            for ss in schedule.scheduledsession_set.all():
                if self.verbose:
                    self.stdout.write('  %-40s at %32s  badness: %u' % (ss.session.group.acronym,
                                                                        ss.timeslot.time,
                                                                        ss.badness))
            self.stdout.write('total                                                                             badness: %u' % (schedule.badness))
            
                    

            
            
