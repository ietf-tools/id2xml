import sys
from django.test import TestCase
from django.test.client import Client
from ietf.meeting.models  import TimeSlot, Session

class AgendaInfoTestCase(TestCase):
    fixtures = [ 'names.xml',  # ietf/names/fixtures/names.xml for MeetingTypeName, and TimeSlotTypeName
                 'meeting83.json',
                 'workinggroups.json',
                 'person.json', 'users.json' ]

    def test_AgendaInfo(self):
        from ietf.meeting.views import agenda_info
        num = '83'
        timeslots, scheduledsessions, update, meeting, venue, ads, plenaryw_agenda, plenaryt_agenda = agenda_info(num)
        # I think that "timeslots" here, is unique times, not actually
        # the timeslots array itself.
        self.assertEqual(len(timeslots),26)
        self.assertEqual(meeting.number,'83')
        self.assertEqual(venue.meeting_num, "83")
        self.assertEqual(len(ads), 0)

    def test_AgendaInfoReturnsSortedTimeSlots(self):
        from ietf.meeting.views import agenda_info
        num = '83'
        timeslots, scheduledsessions, update, meeting, venue, ads, plenaryw_agenda, plenaryt_agenda = agenda_info(num)
        for slotnum in range(0,len(timeslots)-1):
            # debug
            #sys.stdout.write("%d: %s vs %d: %s\n" % (timeslots[slotnum].pk,
            #                                         timeslots[slotnum].time,
            #                                         timeslots[slotnum+1].pk,
            #                                         timeslots[slotnum+1].time))
            self.assertTrue(timeslots[slotnum].time < timeslots[slotnum+1].time)

    def test_AgendaInfoNotFound(self):
        from django.http import Http404
        from ietf.meeting.views import agenda_info
        num = '83b'
        try:
            timeslots, scheduledsessions, update, meeting, venue, ads, plenaryw_agenda, plenaryt_agenda = agenda_info(num)
            # fail!!!
            self.assertFalse(True)
        except Http404:
            pass
            

    def test_TimeSlotHasRegistrationInfo(self):
        # find the registration slot, and confirm that it can find the registration
        regslot = TimeSlot.objects.get(pk=2900)
        self.assertEqual(regslot.type.slug, "reg")
        slot1 = TimeSlot.objects.get(pk=2371)  # "name": "Morning Session I"
        self.assertEqual(slot1.registration(), regslot)

    def test_DoNotGetSchedule(self):
        from django.http import Http404
        num = '83'
        from ietf.meeting.views import get_meeting, get_schedule
        meeting = get_meeting(num)
        try:
            na = get_schedule(meeting, "none:83")
        except Http404:
            False

    def test_GetSchedule(self):
        num = '83'
        from ietf.meeting.views import get_meeting, get_schedule
        meeting = get_meeting(num)
        na = get_schedule(meeting, "mtg:83")
        self.assertIsNotNone(na)

    def test_sessionstr(self):
        num = '83'
        from ietf.meeting.views import get_meeting
        meeting = get_meeting(num)
        session1= Session.objects.get(pk=2157)
        self.assertEqual(session1.__unicode__(), u"IETF-83: pkix 0900")

    def test_sessionstr_interim(self):
        """
        Need a fixture for a meeting that is interim
        """
        pass

    def test_AgendaInfoNamedSlotSessionsByArea(self):
        from ietf.meeting.views import agenda_info
        num = '83'
        timeslots, scheduledsessions, update, meeting, venue, ads, plenaryw_agenda, plenaryt_agenda = agenda_info(num)
        for slot in timeslots:
            for ss in slot.scheduledsessions_by_area:
                self.assertIsNotNone(ss)
                self.assertIsNotNone(ss["area"])
                self.assertIsNotNone(ss["info"])

    def test_AgendaInfoNamedSlotSessionsByArea(self):
        from ietf.meeting.views import agenda_info
        num = '83'
        timeslots, scheduledsessions, update, meeting, venue, ads, plenaryw_agenda, plenaryt_agenda = agenda_info(num)
        # the third timeslot should be 1300-1450 on Sunday March 25.
        # it should have three things:
        #1300-1450  Tools for Creating Internet-Drafts Tutorial - 241
        #1300-1450  Newcomers' Orientation - 252B
        #1300-1450  Meetecho Tutorial for Participants and WG Chairs - 252A
        #import pdb
        #pdb.set_trace()
        slot3 = timeslots[2]
        self.assertEqual(slot3.time_desc, "1300-1450")
        events = slot3.scheduledsessions_at_same_time
        self.assertEqual(len(events), 3)
        

        
