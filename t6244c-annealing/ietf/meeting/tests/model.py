import sys
from django.test import TestCase
from django.test.client import Client
from ietf.meeting.models  import TimeSlot, Session, Schedule

class ModelTestCase(TestCase):
    fixtures = [ 'names.xml',  # ietf/names/fixtures/names.xml for MeetingTypeName, and TimeSlotTypeName
                 'meeting83.json',
                 'constraint83.json',
                 'workinggroups.json',
                 'empty83.json',  # a partially placed schedule
                 'person.json',
                 'users.json' ]

    def test_ScheduleAllSessions(self):
        """
        return the list of scheduled sessions, and sessions that have not been scheduled.
        """
        schedule = Schedule.objects.get(pk=103)
        scheduledsessions, unscheduledsessions = schedule.sessions_split
        self.assertEqual(len(scheduledsessions), 22)
        self.assertEqual(len(unscheduledsessions), 130)
        self.assertEqual(len(schedule.meeting.session_set.all()), 150)

