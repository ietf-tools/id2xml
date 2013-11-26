from django.core.management.base import BaseCommand
from django.core import serializers
from optparse import make_option
from django.utils import formats
import sys

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--format', default='json', dest='format',
            help='Specifies the output serialization format for fixtures.'),
        make_option('--sql_v4', action='store_true', default='False', dest='sql_v4',
            help='Output the schedule in pre-4.7 format as a series of UPDATE statements'),
        make_option('--indent', default=None, dest='indent', type='int',
            help='Specifies the indent level to use when pretty-printing output'),
    #    make_option('--schedulename', action='store',  dest='schedulename', default=False,
    #        help='Tells Django to stop running the test suite after first failed test.')
    )
    help = 'Saves the scheduled information for a named schedule in JSON format'
    args = 'meetingname [owner] schedname'

    def handle(self, *labels, **options):
        from django.conf import settings
        from django.test.utils import get_runner

        meetingname = labels[0]
        schedname   = labels[1]

        from ietf.meeting.helpers import get_meeting,get_schedule

        fixture_format = options.get('format','json')
        indent = options.get('indent', 2)
        sql_v4 = options.get('sql_v4', False)
        meeting = get_meeting(meetingname)
        schedule = get_schedule(meeting, schedname)

        scheduledsessions = schedule.scheduledsession_set.all()

        # cribbed from django/core/management/commands/dumpdata.py

        if sql_v4:
            for ss in scheduledsessions:
                session = ss.session
                timeslot= ss.timeslot
                if session:
                    print "UPDATE meeting_session SET timeslot_id = %u WHERE session.id = %u;" % (timeslot.id, session.id)
                from django.utils import dateformat
                from django.utils.dateformat import format
                print "UPDATE meeting_timeslot SET time='%s', duration = %u WHERE timeslot.id = %u;" % (format(timeslot.time, "Y-m-d ")+dateformat.time_format(timeslot.time,"H:i"), timeslot.duration.seconds, timeslot.id)
        else:
            # Check that the serialization format exists; this is a shortcut to
            # avoid collating all the objects and _then_ failing.
            if fixture_format not in serializers.get_public_serializer_formats():
                raise CommandError("Unknown serialization format: %s" % fixture_format)

            return serializers.serialize(fixture_format, scheduledsessions, indent=indent,
                                         use_natural_keys=True)


