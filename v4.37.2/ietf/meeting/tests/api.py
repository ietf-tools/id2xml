import sys
from django.test import TestCase
from django.test.client import Client
from ietf.meeting.models  import TimeSlot, Session, ScheduledSession

class ApiTestCase(TestCase):
    fixtures = [ 'names.xml',  # ietf/names/fixtures/names.xml for MeetingTypeName, and TimeSlotTypeName
                 'meeting83.json',
                 'workinggroups.json',
                 'person.json', 'users.json' ]

    def test_UpdateAgendaItem(self):
        ts_one = TimeSlot.objects.get(pk=2371)
        ts_two = TimeSlot.objects.get(pk=2372)
        ss_one = ScheduledSession.objects.get(pk=2371)

        # confirm that it has old timeslot value
        self.assertEqual(ss_one.timeslot, ts_one)

        import logging
        logging.debug("calling post")
        
        # move this session from one timeslot to another.
        self.client.post('/dajaxice/ietf.meeting.update_timeslot/', {
            'argv': '{"new_event":{"session_id":"2371","timeslot_id":"2372"}}'
            })

        # confirm that it has new timeslot value
        ss_one = ScheduledSession.objects.get(pk=2371)
        self.assertEqual(ss_one.timeslot, ts_two)

