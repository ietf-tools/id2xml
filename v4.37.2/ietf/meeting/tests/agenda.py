import sys
from django.test import TestCase
from django.test.client import Client

class AgendaInfoTestCase(TestCase):
    fixtures = [ 'meeting85.json', 'workinggroups.json', 'person.json', 'users.json' ]

    def test_AgendaInfo(self):
        from ietf.meeting.views import agenda_info
        num = 85
        timeslots, update, meeting, venue, ads, plenaryw_agenda, plenaryt_agenda = agenda_info(num)
        self.assertEqual(len(timeslots),99)
        self.assertEqual(update, "foo")
        self.assertEqual(meeting.number, 85)
        self.assertEqual(venue, "Atlanta")
        self.assertEqual(len(ads), 11)
        self.assertEqual(plenaryw_agenda, "IAB")
        self.assertEqual(plenaryt_agenda, "IESG")

        
        
