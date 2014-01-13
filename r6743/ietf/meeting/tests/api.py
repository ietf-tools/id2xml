import base64
import sys, datetime
from django.test              import Client
from ietf.utils import TestCase

from ietf.person.models import Person
from django.contrib.auth.models import User
from ietf.meeting.models  import TimeSlot, Session, ScheduledSession, Meeting, Room
from ietf.ietfauth.decorators import has_role
from auths import auth_joeblow, auth_wlo, auth_ietfchair, auth_ferrel
from django.utils import simplejson as json
from ietf.meeting.helpers import get_meeting
from ietf.meeting.ajax import agenda_update

import debug

class ApiTestCase(TestCase):
    # See ietf.utils.test_utils.TestCase for the use of perma_fixtures vs. fixtures
    perma_fixtures = [ 'names.xml',  # ietf/names/fixtures/names.xml for MeetingTypeName, and TimeSlotTypeName
                 'meeting83.json',
                 'constraint83.json',
                 'workinggroups.json',
                 'groupgroup.json',
                 'person.json', 'users.json' ]

    def setup_pkix_on_friday(self):
        m83 = get_meeting(83)
        o83 = m83.agenda
        room = m83.room_set.get(name="252A")

        # look for ScheduledSession with Session=/Timeslot
        ss_list = o83.scheduledsession_set.filter(session__group__acronym = "pkix",
                                                          timeslot__time = "2012-03-30 12:30:00")
        self.assertEqual(len(ss_list), 0)

        ts_one = m83.timeslot_set.get(time = "2012-03-30 12:30:00", location=room)
        pkix   = m83.session_set.get(group__acronym = "pkix")
        self.assertNotEqual(ts_one, None)
        self.assertNotEqual(pkix, None)
        return m83, o83, pkix, ts_one

    def check_pkix_on_friday(self, o83):
        # look for ScheduledSession with Session=/Timeslot: (should not be one)
        ss_list = o83.scheduledsession_set.filter(session__group__acronym = "pkix",
                                                  timeslot__time = "2012-03-30 12:30:00")
        return ss_list

    def test_noAuthenticationCreateScheduledSession(self):
        m83, o83, pkix, ts_one = self.setup_pkix_on_friday()

        # try to create a new scheduledsession item without any authorization
        self.client.post("/meeting/%s/schedule/%s/sessions.json" % (m83.number, o83.name),
                         '{"session_id":"%u", "timeslot_id": "%u"}' % (pkix.id, ts_one.id),
                         content_type="text/json")

        ss_list = self.check_pkix_on_friday(o83)
        self.assertEqual(len(ss_list), 0)

    def test_noAuthorizationCreateScheduledSession(self):
        m83, o83, pkix, ts_one = self.setup_pkix_on_friday()
        # create a new scheduledsession item, but without authorization.
        self.client.post("/meeting/%s/schedule/%s/sessions.json" % (m83.number, o83.name),
                         '{"session_id":"%u", "timeslot_id": "%u"}' % (pkix.id, ts_one.id),
                         content_type="text/json",
                         **auth_ferrel)

        ss_list = self.check_pkix_on_friday(o83)
        self.assertEqual(len(ss_list), 0)

    def test_wloCreateScheduledSession(self):
        m83, o83, pkix, ts_one = self.setup_pkix_on_friday()
        # create a new scheduledsesesion item, with authorization
        self.client.post("/meeting/%s/schedule/%s/sessions.json" % (m83.number, o83.name),
                         '{"session_id":"%u", "timeslot_id": "%u"}' % (pkix.id, ts_one.id),
                         content_type="text/json",
                         **auth_wlo)

        ss_list = self.check_pkix_on_friday(o83)
        self.assertEqual(len(ss_list), 1)

    def test_wloDeleteScheduledSession(self):
        # this is pkix on Monday
        ss_pkix = ScheduledSession.objects.get(pk=2371)
        o83 = ss_pkix.schedule
        m83 = o83.meeting

        # create a new scheduledsesesion item, with authorization
        self.client.delete("/meeting/%s/schedule/%s/session/%u.json" % (m83.number, o83.name, ss_pkix.pk),
                           **auth_wlo)

        ss_list = ScheduledSession.objects.filter(pk=2371)
        self.assertEqual(len(ss_list), 0)

    def test_anyoneGetConflictInfo(self):
        s2157 = Session.objects.get(pk=2157)

        # confirm that a constraint json is generated properly
        resp = self.client.get('/meeting/83/session/2157/constraints.json')
        conflicts = json.loads(resp.content)
        self.assertNotEqual(conflicts, None)

    def test_anyoneGetTimeslotInfo(self):
        resp = self.client.get('/meeting/83/timeslots.json')
        m83timeslots = json.loads(resp.content)
        self.assertNotEqual(m83timeslots, None)

    def test_anyoneGetSessionInfo(self):
        resp = self.client.get('/meeting/83/sessions.json')
        m83sessions = json.loads(resp.content)
        self.assertNotEqual(m83sessions, None)

    def test_anyoneGetScheduledSessionInfo(self):
        resp = self.client.get('/meeting/83/schedule/mtg_83/sessions.json')
        m83ss = json.loads(resp.content)
        self.assertNotEqual(m83ss, None)

    def test_conflictInfoIncludesPeople(self):
        mtg83 = get_meeting(83)
        clue83 = mtg83.session_set.filter(group__acronym='clue')[0]

        # retrive some json that shows the conflict for this session.
        resp = self.client.get("/meeting/83/session/%u/constraints.json" % (clue83.pk))
        conflicts = json.loads(resp.content)
        self.assertNotEqual(conflicts, None)
        self.assertEqual(len(conflicts), 39)

    def test_getMeetingInfoJson(self):
        resp = self.client.get('/meeting/83.json')
        mtginfo = json.loads(resp.content)
        self.assertNotEqual(mtginfo, None)

    def test_getRoomJson(self):
        mtg83 = get_meeting(83)
        rm243 = mtg83.room_set.get(name = '243')

        resp = self.client.get('/meeting/83/room/%s.json' % rm243.pk)
        rm243json = json.loads(resp.content)
        self.assertNotEqual(rm243json, None)

    def test_createNewRoomNonSecretariat(self):
        mtg83 = get_meeting(83)
        rm221 = mtg83.room_set.filter(name = '221')
        self.assertEqual(len(rm221), 0)

        # try to create a new room.
        self.client.post('/meeting/83/rooms', {
                'name' : '221',
                'capacity': 50,
            }, **auth_joeblow)

        # see that in fact the room was not created
        rm221 = mtg83.room_set.filter(name = '221')
        self.assertEqual(len(rm221), 0)

    def test_createNewRoomSecretariat(self):
        mtg83 = get_meeting(83)
        rm221 = mtg83.room_set.filter(name = '221')
        self.assertEqual(len(rm221), 0)

        timeslots = mtg83.timeslot_set.all()
        timeslot_initial_len = len(timeslots)
        self.assertTrue(timeslot_initial_len>0)

        extra_headers = auth_wlo
        extra_headers['HTTP_ACCEPT']='text/json'

        # try to create a new room
        self.client.post('/meeting/83/rooms', {
                'name' : '221',
                'capacity': 50,
            }, **extra_headers)

        # see that in fact wlo can create a new room.
        rm221 = mtg83.room_set.filter(name = '221')
        self.assertEqual(len(rm221), 1)

        timeslots = mtg83.timeslot_set.all()
        timeslot_final_len = len(timeslots)
        self.assertEqual((timeslot_final_len - timeslot_initial_len), 26)

    def test_deleteNewRoomSecretariat(self):
        mtg83 = get_meeting(83)
        rm243 = mtg83.room_set.get(name = '243')
        slotcount = len(rm243.timeslot_set.all())
        self.assertNotEqual(rm243, None)

        timeslots = mtg83.timeslot_set.all()
        timeslot_initial_len = len(timeslots)
        self.assertTrue(timeslot_initial_len>0)

        # try to delete a new room
        self.client.delete('/meeting/83/room/%s.json' % (rm243.pk), **auth_wlo)

        # see that in fact wlo can delete an existing room.
        rm243 = mtg83.room_set.filter(name = '243')
        self.assertEqual(len(rm243), 0)

        timeslots = mtg83.timeslot_set.all()
        timeslot_final_len = len(timeslots)
        self.assertEqual((timeslot_final_len-timeslot_initial_len), -slotcount)

    def test_getGroupInfoJson(self):
        resp = self.client.get('/group/pkix.json')
        #print "json: %s" % (resp.content)
        mtginfo = json.loads(resp.content)
        self.assertNotEqual(mtginfo, None)

    def test_getPersonInfoJson(self):
        # 491 is Adrian Ferrel, an AD
        af = User.objects.filter(pk = 491)[0]
        person = af.person
        resp = self.client.get('/person/%u.json' % (person.pk))
        #print "json: %s" % (resp.content)
        pinfo = json.loads(resp.content)
        self.assertNotEqual(pinfo, None)

    def test_getSlotJson(self):
        mtg83 = get_meeting(83)
        slot0 = mtg83.timeslot_set.all()[0]

        resp = self.client.get('/meeting/83/timeslot/%s.json' % slot0.pk)
        slot0json = json.loads(resp.content)
        self.assertNotEqual(slot0json, None)

    def test_createNewSlotNonSecretariat(self):
        mtg83 = get_meeting(83)
        slot23 = mtg83.timeslot_set.filter(time=datetime.date(year=2012,month=3,day=23))
        self.assertEqual(len(slot23), 0)

        # try to create a new room.
        resp = self.client.post('/meeting/83/timeslots', {
                'type' : 'plenary',
                'name' : 'Workshop on Smart Object Security',
                'time' : '2012-03-23',
                'duration_days' : 0,
                'duration_hours': 8,
                'duration_minutes' : 0,
                'duration_seconds' : 0,
            }, **auth_joeblow)

        self.assertEqual(resp.status_code, 403)
        # see that in fact the room was not created
        slot23 = mtg83.timeslot_set.filter(time=datetime.date(year=2012,month=3,day=23))
        self.assertEqual(len(slot23), 0)

    def test_createNewSlotSecretariat(self):
        mtg83 = get_meeting(83)
        slot23 = mtg83.timeslot_set.filter(time=datetime.date(year=2012,month=3,day=23))
        self.assertEqual(len(slot23), 0)

        extra_headers = auth_wlo
        extra_headers['HTTP_ACCEPT']='text/json'

        # try to create a new room.
        resp = self.client.post('/meeting/83/timeslots', {
                'type' : 'plenary',
                'name' : 'Workshop on Smart Object Security',
                'time' : '2012-03-23',
                'duration': '08:00:00',
            }, **extra_headers)
        self.assertEqual(resp.status_code, 302)

        # see that in fact wlo can create a new timeslot
        mtg83 = get_meeting(83)
        slot23 = mtg83.timeslot_set.filter(time=datetime.date(year=2012,month=3,day=23))
        self.assertEqual(len(slot23), 11)

    def test_deleteNewSlotSecretariat(self):
        mtg83 = get_meeting(83)
        slot0 = mtg83.timeslot_set.all()[0]

        # try to delete a new room
        self.client.delete('/meeting/83/timeslot/%s.json' % (slot0.pk), **auth_wlo)

        # see that in fact wlo can delete an existing room.
        slot0n = mtg83.timeslot_set.filter(pk = slot0.pk)
        self.assertEqual(len(slot0n), 0)

    #
    # AGENDA API
    #
    def test_getAgendaJson(self):
        mtg83 = get_meeting(83)
        a83   = mtg83.agenda

        resp = self.client.get('/meeting/83/agendas/%s.json' % a83.name)
        a83json = json.loads(resp.content)
        self.assertNotEqual(a83json, None)

    def test_createNewAgendaNonSecretariat(self):
        mtg83 = get_meeting(83)

        # try to create a new agenda
        resp = self.client.post('/meeting/83/agendas', {
                'type' : 'plenary',
                'name' : 'Workshop on Smart Object Security',
                'time' : '2012-03-23',
                'duration_days' : 0,
                'duration_hours': 8,
                'duration_minutes' : 0,
                'duration_seconds' : 0,
            }, **auth_joeblow)

        self.assertEqual(resp.status_code, 403)
        # see that in fact the room was not created
        slot23 = mtg83.timeslot_set.filter(time=datetime.date(year=2012,month=3,day=23))
        self.assertEqual(len(slot23), 0)

    def test_createNewAgendaSecretariat(self):
        mtg83 = get_meeting(83)
        a83   = mtg83.agenda

        extra_headers = auth_wlo
        extra_headers['HTTP_ACCEPT']='text/json'

        # try to create a new agenda
        resp = self.client.post('/meeting/83/agendas', {
                'name' : 'fakeagenda1',
            }, **extra_headers)

        self.assertEqual(resp.status_code, 302)

        # see that in fact wlo can create a new timeslot
        mtg83 = get_meeting(83)
        n83 = mtg83.schedule_set.filter(name='fakeagenda1')
        self.assertNotEqual(n83, None)

    def test_updateAgendaSecretariat(self):
        mtg83 = get_meeting(83)
        a83   = mtg83.agenda
        self.assertTrue(a83.visible)

        extra_headers = auth_wlo
        extra_headers['HTTP_ACCEPT']='application/json'

        # try to edit an existing agenda
        resp = self.client.put('/meeting/83/agendas/%s.json' % (a83.name),
                               data='visible=0',
                               content_type="application/x-www-form-urlencoded",
                               **extra_headers)

        self.assertEqual(resp.status_code, 200)

        # see that in fact the visible attribute changed.
        mtg83 = get_meeting(83)
        a83   = mtg83.agenda
        self.assertFalse(a83.visible)

    def test_adrianCanNotEditSecretariatAgenda(self):
        mtg83 = get_meeting(83)
        a83   = mtg83.agenda
        self.assertTrue(a83.visible)
        oldname = a83.name

        extra_headers = auth_ferrel
        extra_headers['HTTP_ACCEPT']='application/json'

        # try to edit an existing agenda
        resp = self.client.put('/meeting/83/agendas/%s.json' % (a83.name),
                               data='visible=0&name=fred',
                               content_type="application/x-www-form-urlencoded",
                               **extra_headers)

        self.assertEqual(resp.status_code, 401)

        # see that in fact the visible attribute did not change.
        mtg83 = get_meeting(83)
        a83   = mtg83.agenda
        self.assertTrue(a83.visible)
        self.assertEqual(a83.name, oldname)

    def test_deleteAgendaSecretariat(self):
        mtg83 = get_meeting(83)
        a83   = mtg83.agenda
        self.assertNotEqual(a83, None)

        # try to delete an agenda
        resp = self.client.delete('/meeting/83/agendas/%s.json' % (a83.name), **auth_wlo)
        self.assertEqual(resp.status_code, 200)

        # see that in fact wlo can delete an existing room.
        mtg83 = get_meeting(83)
        a83c = mtg83.schedule_set.filter(pk = a83.pk).count()
        self.assertEqual(a83c, 0)
        self.assertEqual(mtg83.agenda, None)

    #
    # MEETING API
    #
    def test_getMeetingJson(self):
        resp = self.client.get('/meeting/83.json')
        m83json = json.loads(resp.content)
        self.assertNotEqual(m83json, None)

    def test_setMeetingAgendaNonSecretariat(self):
        mtg83 = get_meeting(83)
        self.assertNotEqual(mtg83.agenda, None)

        # try to create a new agenda
        resp = self.client.put('/meeting/83.json',
                               data="agenda=None",
                               content_type="application/x-www-form-urlencoded",
                               **auth_joeblow)

        self.assertEqual(resp.status_code, 403)
        self.assertNotEqual(mtg83.agenda, None)

    def test_setMeetingAgendaNoneSecretariat(self):
        mtg83 = get_meeting(83)
        self.assertNotEqual(mtg83.agenda, None)

        extra_headers = auth_wlo
        extra_headers['HTTP_ACCEPT']='application/json'

        # try to create a new agenda
        resp = self.client.post('/meeting/83.json',
                                data="agenda=None",
                                content_type="application/x-www-form-urlencoded",
                                **extra_headers)
        self.assertEqual(resp.status_code, 200)

        # new to reload the object
        mtg83 = get_meeting(83)
        self.assertEqual(mtg83.agenda, None)

    def test_setMeetingAgendaSecretariatPublic(self):
        mtg83 = get_meeting(83)
        new_sched = mtg83.schedule_set.create(name="funny",
                                              meeting=mtg83,
                                              public=True,
                                              owner=mtg83.agenda.owner)
        self.assertNotEqual(mtg83.agenda, new_sched)

        extra_headers = auth_wlo
        extra_headers['HTTP_ACCEPT']='text/json'

        # try to create a new agenda
        resp = self.client.put('/meeting/83.json',
                               data="agenda=%s" % new_sched.name,
                               content_type="application/x-www-form-urlencoded",
                               **extra_headers)
        self.assertEqual(resp.status_code, 200)

        # new to reload the object
        mtg83 = get_meeting(83)
        self.assertEqual(mtg83.agenda, new_sched)
        from django.core import mail
        self.assertEquals(len(mail.outbox), 1)

    def test_setNonPublicMeetingAgendaSecretariat(self):
        mtg83 = get_meeting(83)
        new_sched = mtg83.schedule_set.create(name="funny",
                                              meeting=mtg83,
                                              public=False,
                                              owner=mtg83.agenda.owner)
        self.assertNotEqual(mtg83.agenda, new_sched)

        extra_headers = auth_wlo
        extra_headers['HTTP_ACCEPT']='text/json'

        # try to create a new agenda
        resp = self.client.put('/meeting/83.json',
                               data="agenda=%s" % new_sched.name,
                               content_type="application/x-www-form-urlencoded",
                               **extra_headers)
        self.assertEqual(resp.status_code, 406)

        # new to reload the object
        mtg83 = get_meeting(83)
        self.assertNotEqual(mtg83.agenda, new_sched)

    def test_wlo_isSecretariatCanEditSched24(self):
        extra_headers = auth_wlo
        extra_headers['HTTP_ACCEPT']='text/json'

        # check that wlo
        resp = self.client.post('/dajaxice/ietf.meeting.readonly/', {
            'argv': '{"meeting_num":"83","schedule_id":"24"}'
            }, **extra_headers)

        m83perm = json.loads(resp.content)
        self.assertEqual(m83perm['secretariat'], True)
        self.assertEqual(m83perm['owner_href'],  "http://testserver/person/108757.json")
        self.assertEqual(m83perm['read_only'],   False)
        self.assertEqual(m83perm['write_perm'],  True)

    def test_joeblow_isNonUserCanNotSave(self):
        extra_headers = auth_joeblow
        extra_headers['HTTP_ACCEPT']='text/json'

        # check that wlo
        resp = self.client.post('/dajaxice/ietf.meeting.readonly/', {
            'argv': '{"meeting_num":"83","schedule_id":"24"}'
            }, **extra_headers)

        m83perm = json.loads(resp.content)
        self.assertEqual(m83perm['secretariat'], False)
        self.assertEqual(m83perm['owner_href'],  "http://testserver/person/108757.json")
        self.assertEqual(m83perm['read_only'],   True)
        self.assertEqual(m83perm['write_perm'],  False)

    def test_af_IsReadOnlySched24(self):
        """
        This test case validates that despite being an AD, and having a login, a schedule
        that does not belong to him will be marked as readonly.
        """
        extra_headers = auth_ferrel
        extra_headers['HTTP_ACCEPT']='text/json'

        resp = self.client.post('/dajaxice/ietf.meeting.readonly/', {
            'argv': '{"meeting_num":"83","schedule_id":"24"}'
            }, **extra_headers)

        m83perm = json.loads(resp.content)
        self.assertEqual(m83perm['secretariat'], False)
        self.assertEqual(m83perm['owner_href'],  "http://testserver/person/108757.json")
        self.assertEqual(m83perm['read_only'],   True)
        self.assertEqual(m83perm['write_perm'],  True)
        self.assertEqual(resp.status_code, 200)

    def test_wlo_isNonUserCanNotSave(self):
        extra_headers = auth_joeblow
        extra_headers['HTTP_ACCEPT']='text/json'

        # check that wlo
        resp = self.client.post('/dajaxice/ietf.meeting.readonly/', {
            'argv': '{"meeting_num":"83","schedule_id":"24"}'
            }, **extra_headers)

        m83perm = json.loads(resp.content)
        self.assertEqual(m83perm['secretariat'], False)
        self.assertEqual(m83perm['owner_href'],  "http://testserver/person/108757.json")
        self.assertEqual(m83perm['read_only'],   True)
        self.assertEqual(m83perm['write_perm'],  False)

    def test_setMeetingAgendaSecretariat(self):
        mtg83 = get_meeting(83)
        new_sched = mtg83.schedule_set.create(name="funny",
                                              meeting=mtg83,
                                              owner=mtg83.agenda.owner)
        self.assertNotEqual(mtg83.agenda, new_sched)

        extra_headers = auth_wlo
        extra_headers['HTTP_ACCEPT']='text/json'

        # try to create a new agenda
        resp = self.client.put('/meeting/83.json',
                               data="agenda=%s" % new_sched.name,
                               content_type="application/x-www-form-urlencoded",
                               **extra_headers)
        self.assertEqual(resp.status_code, 200)

        # new to reload the object
        mtg83 = get_meeting(83)
        self.assertEqual(mtg83.agenda, new_sched)

    def test_noAuthenticationUpdatePinned(self):
        ss_one = ScheduledSession.objects.get(pk=2371)

        # confirm that it has old timeslot value
        self.assertEqual(ss_one.pinned, False)

        # pin this session to this location
        self.client.post('/dajaxice/ietf.meeting.update_timeslot_pinned/', {
            'argv': '{"schedule_id":"%u", "scheduledsession_id":"%u", "pinned":"%u"}' % (ss_one.schedule.id, ss_one.id, 1)
            })

        # confirm that without login, it does not have new value
        ss_one = ScheduledSession.objects.get(pk=2371)
        self.assertEqual(ss_one.pinned, False)

    def test_authenticationUpdatePinned(self):
        ss_one = ScheduledSession.objects.get(pk=2371)

        # confirm that it has old timeslot value
        self.assertEqual(ss_one.pinned, False)

        extra_headers = auth_wlo
        extra_headers['HTTP_ACCEPT']='text/json'

        # pin this session to this location
        self.client.post('/dajaxice/ietf.meeting.update_timeslot_pinned/', {
            'argv': '{"schedule_id":"%u", "scheduledsession_id":"%u", "pinned":"%u"}' % (ss_one.schedule.id, ss_one.id, 1)
            }, **extra_headers)

        # confirm that without login, it does not have new value
        ss_one = ScheduledSession.objects.get(pk=2371)
        self.assertEqual(ss_one.pinned, True)

    def test_wlo_canChangeTimeSlotPurpose(self):
        extra_headers = auth_wlo
        extra_headers['HTTP_ACCEPT']='text/json'
        ts_one = TimeSlot.objects.get(pk=2371)
        self.assertEqual(ts_one.type_id, "session")

        # check that wlo can update a timeslot purpose
        resp = self.client.post('/dajaxice/ietf.meeting.update_timeslot_purpose/', {
            'argv': '{"meeting_num":"83", "timeslot_id": "%u", "purpose":"plenary"}' % (ts_one.pk)
            }, **extra_headers)

        ts_one_json = json.loads(resp.content)
        self.assertEqual(ts_one_json['roomtype'], "plenary")

        ts_one = TimeSlot.objects.get(pk=2371)
        self.assertEqual(ts_one.type_id, "plenary")

    def test_wlo_canAddTimeSlot(self):
        extra_headers = auth_wlo
        extra_headers['HTTP_ACCEPT']='text/json'
        ts_one = TimeSlot.objects.get(pk=2371)
        self.assertEqual(ts_one.type_id, "session")

        roomPk = ts_one.location.pk

        # check that wlo can create a timeslot where none existed before.
        resp = self.client.post('/dajaxice/ietf.meeting.update_timeslot_purpose/', {
                'argv': '{"meeting_num":"83", "timeslot_id": "0", "purpose":"plenary", "room_id":"%u", "time":"2012-03-25 09:00:00", "duration":"3600" }' % (roomPk)
            }, **extra_headers)
        ts_one_json = json.loads(resp.content)
        self.assertEqual(ts_one_json['roomtype'], "plenary")

    def test_avtcore_spans_two_slots(self):
        m83 = get_meeting(83)
        o83 = m83.agenda

        avtcore_ss = o83.scheduledsession_set.filter(session__group__acronym = "avtcore")
        self.assertEqual(len(avtcore_ss), 2)

        avtcore_ss0 = avtcore_ss[0]
        avtcore_ss1 = avtcore_ss[1]
        # check avtcore's second sessionscheduled replies with an extendedfrom attribute
        resp = self.client.get('/meeting/83/schedule/%s/session/%u.json' % (o83.name, avtcore_ss1.pk))
        avtcore_json = json.loads(resp.content)
        self.assertEqual(avtcore_json['extendedfrom_id'], avtcore_ss0.pk)

        # check avtcore's first session replies without an extendedfrom attribute
        resp = self.client.get('/meeting/83/schedule/%s/session/%u.json' % (o83.name, avtcore_ss0.pk))
        avtcore_json = json.loads(resp.content)
        self.assertFalse("extendedfrom_id" in avtcore_json)

    # different test: ccamp has two sessions, but one of them spans two slots.
    def test_ccamp_spans_one_slots(self):
        m83 = get_meeting(83)
        o83 = m83.agenda

        ccamp_ss = o83.scheduledsession_set.filter(session__group__acronym = "ccamp").order_by("timeslot__time")
        self.assertEqual(len(ccamp_ss), 3)

        ccamp_ss0 = ccamp_ss[0]
        # check ccamp's session replies without an extendedfrom attribute
        resp = self.client.get('/meeting/83/schedule/%s/session/%u.json' % (o83.name, ccamp_ss0.pk))
        ccamp_json = json.loads(resp.content)
        self.assertFalse("extendedfrom_id" in ccamp_json)

        ccamp_ss1 = ccamp_ss[1]
        # check ccamp's session replies with an extendedfrom attribute
        resp = self.client.get('/meeting/83/schedule/%s/session/%u.json' % (o83.name, ccamp_ss1.pk))
        ccamp_json = json.loads(resp.content)
        self.assertTrue("extendedfrom_id" in ccamp_json)

        ccamp_ss2 = ccamp_ss[2]
        # check ccamp's session replies without an extendedfrom attribute
        resp = self.client.get('/meeting/83/schedule/%s/session/%u.json' % (o83.name, ccamp_ss2.pk))
        ccamp_json = json.loads(resp.content)
        self.assertFalse("extendedfrom_id" in ccamp_json)

    # negative test against a session that has two actual session requests
    # which are not extended versions of each other.
    def test_ccamp_spans_one_slots(self):
        m83 = get_meeting(83)
        o83 = m83.agenda

        core_ss = o83.scheduledsession_set.filter(session__group__acronym = "core")
        self.assertEqual(len(core_ss), 2)

        core_ss0 = core_ss[0]
        # check core's session replies without an extendedfrom attribute
        resp = self.client.get('/meeting/83/schedule/%s/session/%u.json' % (o83.name, core_ss0.pk))
        core_json = json.loads(resp.content)
        self.assertFalse("extendedfrom_id" in core_json)

        core_ss1 = core_ss[1]
        # check core's session replies without an extendedfrom attribute
        resp = self.client.get('/meeting/83/schedule/%s/session/%u.json' % (o83.name, core_ss1.pk))
        core_json = json.loads(resp.content)
        self.assertFalse("extendedfrom_id" in core_json)



