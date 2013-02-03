import sys
from django.test import TestCase
from django.test.client import Client

class AgendaInfoTestCase(TestCase):
    fixtures = [ 'names.xml',  # for MeetingTypeName
                 'meeting83.json',
                 'workinggroups.json',
                 'person.json', 'users.json' ]

    def test_AgendaInfo(self):
        from ietf.meeting.views import agenda_info
        num = '83'
        timeslots, update, meeting, venue, ads, plenaryw_agenda, plenaryt_agenda = agenda_info(num)
        # I think that "timeslots" here, is unique times, not actually
        # the timeslots array itself.
        self.assertEqual(len(timeslots),26)
        self.assertEqual(meeting.number,'83')
        self.assertEqual(venue.meeting_num, "83")
        self.assertEqual(len(ads), 0)

    def test_AgendaInfoNotFound(self):
        from django.http import Http404
        from ietf.meeting.views import agenda_info
        num = '83b'
        # should raise an exception.
        try:
            timeslots, update, meeting, venue, ads, plenaryw_agenda, plenaryt_agenda = agenda_info(num)
            False
        except Http404:
            pass


        
        
