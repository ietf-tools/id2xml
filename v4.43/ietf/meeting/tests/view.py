import re
import sys
from django.test import TestCase
#from ietf.person.models import Person
from django.contrib.auth.models import User
from django.test.client import Client
from ietf.meeting.models  import TimeSlot, Session, ScheduledSession
from auths import auth_joeblow, auth_wlo, auth_ietfchair, auth_ferrel

class ViewTestCase(TestCase):
    fixtures = [ 'names.xml',  # ietf/names/fixtures/names.xml for MeetingTypeName, and TimeSlotTypeName
                 'meeting83.json',
                 'constraint83.json',
                 'workinggroups.json',
                 'groupgroup.json',
                 'person.json', 'users.json' ]

    def test_nameOfClueWg(self):
        clue_session = Session.objects.get(pk=2194)
        self.assertEqual(clue_session.short_name, "clue")

    def test_nameOfIEPG(self):
        iepg_session = Session.objects.get(pk=2288)
        self.assertEqual(iepg_session.short_name, "IEPG Meeting")

    def test_nameOfEdu1(self):
        edu1_session = Session.objects.get(pk=2274)
        self.assertEqual(edu1_session.short_name, "Tools for Creating Internet-Drafts Tutorial")

    def test_js_identifier_clue(self):
        iepg_ss = ScheduledSession.objects.get(pk=2413)
        slot = iepg_ss.timeslot
        self.assertEqual(slot.js_identifier, "252b_2012-03-27_0900")

    def test_agenda_save(self):
        from ietf.meeting.views import get_meeting
        #
        # determine that there isn't a schedule called "fred"
        mtg = get_meeting(83)
        fred = mtg.get_schedule_by_name("fred")
        self.assertIsNone(fred)
        #
        # move this session from one timeslot to another.
        self.client.post('/meeting/83/schedule/edit', {
            'savename': "fred",
            'saveas': "saveas",
            }, **auth_wlo)
        #
        # confirm that a new schedule has been created
        fred = mtg.get_schedule_by_name("fred")
        self.assertNotEqual(fred, None, "fred not found")

    def test_agenda_edit_url(self):
        from django.core.urlresolvers import reverse
        from ietf.meeting.views import edit_agenda
        url = reverse(edit_agenda,
                      args=['83', 'fred'])
        self.assertEqual(url, "/meeting/83/schedule/fred/edit")





