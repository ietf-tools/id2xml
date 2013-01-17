import sys
from django.test import TestCase
from django.test.client import Client
from ietf.meeting.models  import TimeSlot

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

        
        
