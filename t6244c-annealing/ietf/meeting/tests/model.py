import sys
from django.test import TestCase
from ietf.meeting.tests.ttest import AgendaTransactionalTestCase
from django.test.client   import Client
from ietf.meeting.models  import TimeSlot, Session, Schedule, ScheduledSession
from ietf.meeting.models  import Constraint
from ietf.group.models    import Group
from ietf.name.models     import ConstraintName

class ModelTestCase(AgendaTransactionalTestCase):
    fixtures = [ 'names.xml',  # ietf/names/fixtures/names.xml for MeetingTypeName, and TimeSlotTypeName
                 'meeting83.json',
                 'constraint83.json',
                 'workinggroups.json',
                 'empty83.json',  # a partially placed schedule
                 'person.json',
                 'users.json' ]

    def test_ScheduleAllSessions(self):
        """
        return the list of all sessions that want to meet
        """
        mtg83 = Meeting.objects.get(number=83)
        wanttomeet = mtg83.sessions_that_can_meet
        self.assertEqual(len(wanttomeet), 144)

    def test_ScheduleAllSessions(self):
        """
        return the list of scheduled sessions, and sessions that have not been scheduled.
        """
        schedule = Schedule.objects.get(pk=103)
        assignments = schedule.group_mapping
        assigned = 0
        unassigned = 0
        for g,r in assignments.items():
            if len(r)>0:
                assigned += len(r)
            else:
                unassigned += 1
        self.assertEqual(assigned,   22)
        self.assertEqual(unassigned, 113)
        self.assertEqual(len(schedule.meeting.session_set.all()), 150)

    def test_orderingOfConstaints(self):
        """
        test if Constraints order properly
        """
        schedule = Schedule.objects.get(pk=103)
        mtg = schedule.meeting
        group1   = Group.objects.get(acronym='pkix')
        group2   = Group.objects.get(acronym='ipsecme')
        conflict = ConstraintName.objects.get(slug="conflict", )
        conflic2 = ConstraintName.objects.get(slug="conflic2")
        conflic3 = ConstraintName.objects.get(slug="conflic3")
        c1 = Constraint.objects.create(name=conflict, meeting=mtg, source=group1, target=group2)
        c2 = Constraint.objects.create(name=conflic2, meeting=mtg, source=group1, target=group2)
        c3 = Constraint.objects.create(name=conflic3, meeting=mtg, source=group1, target=group2)
        self.assertTrue(c1 < c2)
        self.assertTrue(c2 < c3)
        self.assertTrue(c1 < c3)

