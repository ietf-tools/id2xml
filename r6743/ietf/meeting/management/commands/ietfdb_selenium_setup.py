from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core import serializers
from optparse import make_option
from django.utils import formats
import sys

class Command(BaseCommand):
    help = 'Setups the database for use by selenium and QUnit tests'

    def handle(self, *labels, **options):
        from django.conf import settings
        from django.test.utils import get_runner

        from ietf.meeting.helpers import get_meeting,get_schedule

        m83 = get_meeting(83)
        for schedule in m83.schedule_set.all():
            schedule.delete_schedule()

        # clear a bit more out.
        m83.session_set.all().delete()
        m83.room_set.all().delete()
        m83.timeslot_set.all().delete()
        m83.delete()

        # (re-)load data from fixtures.
        call_command('loaddata', 'meeting83')

