import base64
import sys
from django.test import TestCase, Client

#from ietf.person.models import Person
from django.contrib.auth.models import User
from ietf.meeting.models  import TimeSlot, Session, ScheduledSession
from ietf.ietfauth.decorators import has_role
from auths import auth_joeblow, auth_wlo, auth_ietfchair, auth_ferrel
from django.utils import simplejson as json

class ApiTestCase(TestCase):
    fixtures = [ 'names.xml',  # ietf/names/fixtures/names.xml for MeetingTypeName, and TimeSlotTypeName
                 'meeting83.json',
                 'constraint83.json',
                 'workinggroups.json',
                 'groupgroup.json',
                 'person.json', 'users.json' ]

    def test_noAuthenticationUpdateAgendaItem(self):
        ts_one = TimeSlot.objects.get(pk=2371)
        ts_two = TimeSlot.objects.get(pk=2372)
        ss_one = ScheduledSession.objects.get(pk=2371)

        # confirm that it has old timeslot value
        self.assertEqual(ss_one.timeslot, ts_one)

        # move this session from one timeslot to another.
        self.client.post('/dajaxice/ietf.meeting.update_timeslot/', {
            'argv': '{"session_id":"2371","scheduledsession_id":"2372"}'
            })

        # confirm that without login, it does not have new value
        ss_one = ScheduledSession.objects.get(pk=2371)
        self.assertEqual(ss_one.timeslot, ts_one)

    def atest_noAuthorizationUpdateAgendaItem(self):
        ts_one = TimeSlot.objects.get(pk=2371)
        ts_two = TimeSlot.objects.get(pk=2372)
        ss_one = ScheduledSession.objects.get(pk=2371)

        # confirm that it has old timeslot value
        self.assertEqual(ss_one.timeslot, ts_one)

        self.assertTrue(0)
        # move this session from one timeslot to another.
        self.client.post('/dajaxice/ietf.meeting.update_timeslot/', {
            'argv': '{"session_id":"2371","scheduledsession_id":"2372"}}'
            })

        # confirm that without login, it does not have new value
        ss_one = ScheduledSession.objects.get(pk=2371)
        self.assertEqual(ss_one.timeslot, ts_one)


    def test_wrongAuthorizationUpdateAgendaItem(self):
        s2157 = Session.objects.get(pk=2157)
        ss_one = ScheduledSession.objects.get(pk=2371)
        ss_two = ScheduledSession.objects.get(pk=2372)

        old_two_s = ss_two.session

        # confirm that it has old timeslot value
        self.assertEqual(ss_one.session, s2157)

        # move this session from one timeslot to another.
        self.client.post('/dajaxice/ietf.meeting.update_timeslot/', {
            'argv': '{"session_id":"2157", "scheduledsession_id":"2372"}'
            }, **auth_joeblow)

        # confirm that without login, it does not have new value
        ss_one = ScheduledSession.objects.get(pk=2371)
        self.assertEqual(ss_one.session, s2157)

        # confirm that it new scheduledsession object still has no value.
        ss_two = ScheduledSession.objects.get(pk=2372)
        self.assertEqual(ss_two.session, old_two_s)

    def test_wloUpdateAgendaItem(self):
        s2157 = Session.objects.get(pk=2157)
        ss_one = ScheduledSession.objects.get(pk=2371)

        # confirm that it has old timeslot value
        self.assertEqual(ss_one.session, s2157)

        # move this session from one timeslot to another.
        self.client.post('/dajaxice/ietf.meeting.update_timeslot/', {
            'argv': '{"session_id":"2157", "scheduledsession_id":"2372"}'
            }, **auth_wlo)

        # confirm that it new scheduledsession object has new session.
        ss_two = ScheduledSession.objects.get(pk=2372)
        self.assertEqual(ss_two.session, s2157)

        # confirm that it old scheduledsession object has no session.
        ss_one = ScheduledSession.objects.get(pk=2371)
        self.assertEqual(ss_one.session, None)

    def test_chairUpdateAgendaItem(self):
        s2157 = Session.objects.get(pk=2157)
        ss_one = ScheduledSession.objects.get(pk=2371)

        # confirm that it has old timeslot value
        self.assertEqual(ss_one.session, s2157)

        # move this session from one timeslot to another.
        self.client.post('/dajaxice/ietf.meeting.update_timeslot/', {
            'argv': '{"session_id":"2157", "scheduledsession_id":"2372"}'
            }, **auth_ietfchair)

        # confirm that it new scheduledsession object has new session.
        ss_two = ScheduledSession.objects.get(pk=2372)
        self.assertEqual(ss_two.session, s2157)

        # confirm that it old scheduledsession object has no session.
        ss_one = ScheduledSession.objects.get(pk=2371)
        self.assertEqual(ss_one.session, None)


    def test_anyoneGetConflictInfo(self):
        s2157 = Session.objects.get(pk=2157)

        # move this session from one timeslot to another.
        resp = self.client.get('/meeting/83/session/2157/constraints.json')
        conflicts = json.loads(resp.content)
        self.assertNotEqual(conflicts, None)

    def test_getMeetingInfoJson(self):
        resp = self.client.get('/meeting/83.json')
        mtginfo = json.loads(resp.content)
        self.assertNotEqual(mtginfo, None)

    def atest_iesgNoAuthWloUpdateAgendaItem(self):
        ts_one = TimeSlot.objects.get(pk=2371)
        ts_two = TimeSlot.objects.get(pk=2372)
        ss_one = ScheduledSession.objects.get(pk=2371)

        # confirm that it has old timeslot value
        self.assertEqual(ss_one.timeslot, ts_one)

        self.do_auth_ietfchair
        # move this session from one timeslot to another.
        self.client.post('/dajaxice/ietf.meeting.update_timeslot/', {
            'argv': '{"session_id":"2371","scheduledsession_id":"2372"}'
            })

        self.assertTrue(0)
        # confirm that it has new timeslot value
        ss_one = ScheduledSession.objects.get(pk=2371)
        self.assertEqual(ss_one.timeslot, ts_two)

    def test_getGroupInfoJson(self):
        resp = self.client.get('/group/pkix.json')
        #print "json: %s" % (resp.content)
        mtginfo = json.loads(resp.content)
        self.assertNotNone(mtginfo)



