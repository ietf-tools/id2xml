import sys
from django.test import TestCase
from ietf.meeting.tests.ttest import AgendaTransactionalTestCase
from django.test.client import Client
from ietf.meeting.models  import TimeSlot, Session, Schedule, ScheduledSession
from ietf.meeting.models  import Constraint
from ietf.group.models    import Group
from ietf.name.models     import ConstraintName
from settings import BADNESS_CONFLICT_1,BADNESS_CONFLICT_2,BADNESS_CONFLICT_3,BADNESS_UNPLACED,BADNESS_TOOSMALL_50,BADNESS_TOOSMALL_100,BADNESS_TOOBIG,BADNESS_MUCHTOOBIG
from ietf.meeting.placement import CurrentScheduleState

class PlacementTestCase(AgendaTransactionalTestCase):
    fixtures = [ 'names.xml',  # ietf/names/fixtures/names.xml for MeetingTypeName, and TimeSlotTypeName
                 'meeting83.json',
                 'constraint83.json',
                 'workinggroups.json',
                 'empty83.json',  # a partially placed schedule
                 'person.json',
                 'users.json' ]

    def test_calculatePlacedSession1(self):
        """
        calculate the fitness for a session that has been placed (stock placement)
        """
        schedule = Schedule.objects.get(pk=24)
        mtg = schedule.meeting
        assignments = schedule.group_mapping
        dtnrg = mtg.session_set.get(group__acronym = 'dtnrg')
        self.assertNotEqual(dtnrg, None)
        self.assertNotEqual(assignments[dtnrg.group], [])
        badness = dtnrg.badness(assignments)
        self.assertEqual(badness, BADNESS_TOOBIG+BADNESS_CONFLICT_2*2)

    def test_calculatePlacedSession2(self):
        """
        calculate the fitness for a session that has been placed.
        """

        # do some setup of these slots
        schedule = Schedule.objects.get(pk=103)
        mtg = schedule.meeting
        ipsecme = mtg.session_set.get(group__acronym = 'ipsecme')
        websec  = mtg.session_set.get(group__acronym = 'websec')
        slot1   = schedule.scheduledsession_set.get(timeslot__id = 2373) # 2012-03-26 13:00 location_id=212 (242AB)
        slot2   = schedule.scheduledsession_set.get(timeslot__id = 2376) # 2012-03-26 13:00 location_id=213 (Maillot)
        slot1.session = ipsecme
        slot1.save()
        slot2.session = websec
        slot2.save()

        # now calculate badness
        assignments = schedule.group_mapping
        self.assertNotEqual(ipsecme, None)
        self.assertTrue(len(assignments[ipsecme.group]) > 0)
        badness = ipsecme.badness(assignments)
        self.assertEqual(badness, BADNESS_CONFLICT_3+BADNESS_TOOBIG)

    def test_calculateBadnessMtg83(self):
        """
        calculate the fitness for a session that has been placed.
        """

        # do some setup of these slots
        schedule = Schedule.objects.get(pk=24)
        self.assertEqual(schedule.calc_badness(), 3081200)

    def test_calculateBadnessMtg83unplaced(self):
        """
        calculate the fitness for a session that has been placed.
        """

        # do some setup of these slots
        schedule = Schedule.objects.get(pk=103)
        self.assertEqual(schedule.calc_badness(), 125001000)

    def test_calculateUnPlacedSession(self):
        """
        calculate the fitness for a session that has not been placed
        """
        schedule = Schedule.objects.get(pk=103)
        mtg = schedule.meeting
        assignments = schedule.group_mapping
        pkix = mtg.session_set.get(group__acronym = 'pkix')
        self.assertNotEqual(pkix, None)
        self.assertTrue(len(assignments[pkix.group]) == 0)
        badness = pkix.badness(assignments)
        self.assertEqual(badness, BADNESS_UNPLACED)

    def test_startPlacementSession(self):
        """
        kicks starts the placement process.
        There are 149 timeslots total.
        Says useable (empty) QS: 127.
        There are 149-127 = 22 timeslots with placements, but it's 8 unique session
                               requests, because in this dataset, two session were
                               scheduled into two timeslots.
        There are 145 session requests total.
        So there are 145-8           = 133 unplaced sessions.
        So there should be 149 + 133 = 282 slots total - 8.
        """
        sched1  = Schedule.objects.get(pk=103)
        placer1 = CurrentScheduleState(sched1)
        self.assertEqual(placer1.total_slots, 274) #, "total slots calculation")

    def test_currentScheduleStateIndex(self):
        sched1  = Schedule.objects.get(pk=103)
        placer1 = CurrentScheduleState(sched1)
        placer1.current_assignments["hello"] = "there"
        self.assertEqual(placer1["hello"], "there")
        placer1.tempdict["hello"] = "goodbye"
        self.assertEqual(placer1["hello"], "goodbye")

