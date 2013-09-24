import django.test
import datetime
import json
from django.core.urlresolvers import reverse as urlreverse
from ietf.utils.test_utils import login_testing_unauthorized
from ietf.utils.test_data import make_test_data
from ietf.meeting.helpers import get_meeting

from ietf.meeting.models import Meeting,TimeSlot,Schedule,Session,ScheduledSession
from ietf.group.models import Group
from ietf.person.models import Person
from ietf.name.models import SessionStatusName

from ietf.group.colors import fg_group_colors,bg_group_colors

class RjSTestCase(django.test.TestCase):
    fixtures=['names']

    def test_agenda_save(self):

        url = urlreverse('ietf.meeting.views.edit_agenda',kwargs=dict(num=42))
        mtg = get_meeting(42)
        self.assertIsNone(mtg.get_schedule_by_name("fred"))
        r = self.client.post(url, { 'savename': 'fred' }) 
        self.assertEquals(r.status_code,302)
        self.assertIsNone(mtg.get_schedule_by_name("fred"))
        self.client.login(remote_user="secretary")
        self.client.post(url, { 'savename': 'fred' }) 
        self.assertIsNotNone(mtg.get_schedule_by_name("fred"))
        # TODO make sure fred has the same things that mtg.agenda has

    def test_edit_agenda_visibility(self):

        url = urlreverse('ietf.meeting.views.edit_agenda',kwargs=dict(num=42,schedule_name="pl_pub_vis"))
        self.assertEqual(self.client.get(url,REMOTE_USER='AnonymousUser').status_code, 200)
        self.assertEqual(self.client.get(url,REMOTE_USER='plain').status_code, 200)
        self.assertEqual(self.client.get(url,REMOTE_USER='secretary').status_code, 200)
        self.assertEqual(self.client.get(url,REMOTE_USER='ad').status_code, 200)

        url = urlreverse('ietf.meeting.views.edit_agenda',kwargs=dict(num=42,schedule_name="pl_pri_vis"))
        self.assertEqual(self.client.get(url,REMOTE_USER='AnonymousUser').status_code, 403)
        self.assertEqual(self.client.get(url,REMOTE_USER='plain').status_code, 200)
        self.assertEqual(self.client.get(url,REMOTE_USER='secretary').status_code, 200)
        self.assertEqual(self.client.get(url,REMOTE_USER='ad').status_code, 200)

        url = urlreverse('ietf.meeting.views.edit_agenda',kwargs=dict(num=42,schedule_name="ad_pri_vis"))
        self.assertEqual(self.client.get(url,REMOTE_USER='AnonymousUser').status_code, 403)
        self.assertEqual(self.client.get(url,REMOTE_USER='plain').status_code, 403)
        self.assertEqual(self.client.get(url,REMOTE_USER='secretary').status_code, 200)
        self.assertEqual(self.client.get(url,REMOTE_USER='ad').status_code, 200)

        url = urlreverse('ietf.meeting.views.edit_agenda',kwargs=dict(num=42,schedule_name="pl_pri_hid"))
        self.assertEqual(self.client.get(url,REMOTE_USER='AnonymousUser').status_code, 403)
        self.assertEqual(self.client.get(url,REMOTE_USER='plain').status_code, 200)
        self.assertEqual(self.client.get(url,REMOTE_USER='secretary').status_code, 200)
        self.assertEqual(self.client.get(url,REMOTE_USER='ad').status_code, 403)

    def test_update_agenda_item(self):

        #import logging
        #logging.basicConfig(filename='rjs-ajax.log', level=logging.DEBUG)
        
        mtg = Meeting.objects.get(number=42)
        schedule = Schedule.objects.get(meeting=mtg,name='pl_pri_hid')
        ts_one = TimeSlot.objects.get(meeting__number=42,location__name="Room A",name="Morning",time__day=5)
        ts_two = TimeSlot.objects.get(meeting__number=42,location__name="Room B",name="Afternoon",time__day=5)

        mars_session = Session.objects.get(meeting=mtg,group__acronym="mars")
        ss_one = ScheduledSession.objects.create(schedule=schedule,session=mars_session,timeslot=ts_one)
        ss_two = ScheduledSession.objects.create(schedule=schedule,session=None,timeslot=ts_two)
        
        #url = urlreverse('Dajaxice.ietf.meeting.ajax.update_timeslot',kwargs={})
        url = '/dajaxice/ietf.meeting.update_timeslot/'
        argv_dict=dict(argv='{"schedule_id":"%u","session_id":"%u","scheduledsession_id":"%u"}'%(schedule.pk,mars_session.pk,ss_two.pk))

        def verify_nopermission(user,expected_error,target_session):
            # Dajaxice absorbes the raise HTTP403
            r = self.client.post(url,data=argv_dict,REMOTE_USER=user)
            self.assertEqual(r.status_code,200)
            self.assertTrue(expected_error in r.content)
            ss = ScheduledSession.objects.get(pk=target_session.pk)
            self.assertEqual(ss.session,None)

        # At the moment, a plain user can't edit their own schedule, so _nobody_ can edit pl_pri_hid 
        for user in ['AnonymousUser','ietfchair','plain']:
            verify_nopermission(user,'Restricted to roles Area Director, Secretariat',ss_two)
        for user in ['ad','secretary']:
            verify_nopermission(user,'DAJAXICE_EXCEPTION',ss_two)
        
        # So, lets test whether an ad can modify his own schedule
        schedule = Schedule.objects.get(meeting=mtg,name='ad_pri_vis')
        ss_one = ScheduledSession.objects.create(schedule=schedule,session=mars_session,timeslot=ts_one)
        ss_two = ScheduledSession.objects.create(schedule=schedule,session=None,timeslot=ts_two)
        argv_dict=dict(argv='{"schedule_id":"%u","session_id":"%u","scheduledsession_id":"%u"}'%(schedule.pk,mars_session.pk,ss_two.pk))
        r = self.client.post(url,data=argv_dict,REMOTE_USER='ad')
        self.assertEqual(r.status_code,200)
        self.assertTrue('{"message": "valid"}' in r.content)
        ss_one = ScheduledSession.objects.get(pk=ss_one.pk)
        ss_two = ScheduledSession.objects.get(pk=ss_two.pk)
        self.assertEqual(ss_one.session,None)
        self.assertEqual(ss_two.session,mars_session)

        # Now, unschedule that session
        argv_dict=dict(argv='{"schedule_id":"%u","session_id":"%u","scheduledsession_id":"%u"}'%(schedule.pk,mars_session.pk,0))
        r = self.client.post(url,data=argv_dict,REMOTE_USER='ad')
        self.assertEqual(r.status_code,200)
        self.assertTrue('{"message": "valid"}' in r.content)
        ss_one = ScheduledSession.objects.get(pk=ss_one.pk)
        ss_two = ScheduledSession.objects.get(pk=ss_two.pk)
        self.assertEqual(ss_one.session,None)
        self.assertEqual(ss_two.session,None)

        # There appear to be two ways to do this (setting scheduledsession_id to 0 or not providing it)?
        # See test_wloUpdateAgendaItemtoNone. Make sure the other way does the same thing.
        ss_two.session = mars_session
        ss_two.save()
        argv_dict=dict(argv='{"schedule_id":"%u","session_id":"%u"}'%(schedule.pk,mars_session.pk))
        r = self.client.post(url,data=argv_dict,REMOTE_USER='ad')
        self.assertEqual(r.status_code,200)
        self.assertTrue('{"message": "valid"}' in r.content)
        ss_one = ScheduledSession.objects.get(pk=ss_one.pk)
        ss_two = ScheduledSession.objects.get(pk=ss_two.pk)
        self.assertEqual(ss_one.session,None)
        self.assertEqual(ss_two.session,None)
        
    def test_json_returns_not_null(self):
        mtg = Meeting.objects.get(number=42)
        mars_session = Session.objects.get(meeting=mtg,group__acronym='mars')

        # anyoneGetConflictInfo
        r = self.client.get('/meeting/42/session/%u/constraints.json'%mars_session.pk)
        self.assertIsNotNone(json.loads(r.content))
        self.assertTrue('ames' in r.content)
 
        # getMeetingInfoJson (aka getMeetingJson)
        r = self.client.get('/meeting/42.json')
        self.assertIsNotNone(json.loads(r.content))
        self.assertTrue('"name": "42"' in r.content)
        
        # getRoomJson
        room_a = mtg.room_set.get(name='Room A')
        r = self.client.get('/meeting/42/room/%s.json'%room_a.pk)
        self.assertIsNotNone(json.loads(r.content))
        self.assertTrue('Room A' in r.content)

        # getGroupInfoJson
        r = self.client.get('/group/mars.json')
        self.assertIsNotNone(json.loads(r.content))
        self.assertTrue('Martian Special Interest Group' in r.content)

        # getSlotJson
        ts = TimeSlot.objects.get(meeting=mtg,name="Morning",location__name="Room A",time__day=5)
        r = self.client.get('/meeting/42/timeslot/%s.json'%ts.pk)
        self.assertIsNotNone(json.loads(r.content))
        self.assertEqual(json.loads(r.content)['time'],'0900')

        # getAgendaJson
        r = self.client.get('/meeting/42/agendas/%s.json'%mtg.agenda.name)
        self.assertNotEqual(json.loads(r.content),None)
        self.assertTrue('official-42' in r.content)

    def test_manipulate_new_room(self):
        mtg = Meeting.objects.get(number=42)
        url = urlreverse('ietf.meeting.ajax.timeslot_roomsurl',kwargs=dict(num=42))
        args_dict = { 'name':'Room C','capacity':50 }
        self.assertEqual(self.client.post(url,args_dict,HTTP_ACCEPT="application/json").status_code,302)
        self.assertEqual(mtg.room_set.filter(name='Room C').count(),0)
        self.assertEqual(self.client.post(url,args_dict,REMOTE_USER="plain",HTTP_ACCEPT="application/json").status_code,403)
        self.assertEqual(mtg.room_set.filter(name='Room C').count(),0)
        timeslot_count = mtg.timeslot_set.all().count()
        r = self.client.post(url,args_dict,REMOTE_USER="secretary",HTTP_ACCEPT="application/json")
        self.assertEqual(r.status_code,302)
        self.assertEqual(mtg.room_set.filter(name='Room C').count(),1)
        self.assertTrue(timeslot_count != mtg.timeslot_set.all().count())
        timeslot_count = mtg.timeslot_set.all().count()
        new_url = r['Location']
        self.assertTrue('room/%s.json'%mtg.room_set.get(name='Room C').pk in new_url)
        self.assertEqual(self.client.delete(new_url,REMOTE_USER="AnonymousUser").status_code,403)
        self.assertEqual(mtg.room_set.filter(name='Room C').count(),1)
        self.assertEqual(self.client.delete(new_url,REMOTE_USER="plain").status_code,403)
        self.assertEqual(mtg.room_set.filter(name='Room C').count(),1)
        self.assertEqual(self.client.delete(new_url,REMOTE_USER="plain").status_code,403)
        r = self.client.delete(new_url,REMOTE_USER="secretary")
        self.assertEqual(r.status_code,200)
        self.assertTrue('{"error":"none"}' in r.content)
        self.assertEqual(mtg.room_set.filter(name='Room C').count(),0)
        self.assertTrue(timeslot_count != mtg.timeslot_set.all().count())

    def test_manipulate_new_slot(self):
        mtg = Meeting.objects.get(number=42)
        url = urlreverse('ietf.meeting.ajax.timeslot_slotsurl',kwargs=dict(num=42))
        args_dict = dict( type='plenary',
                          # name='Earth-shattering Kaboom!', # Well, that would be nice but AddSlotForm excludes name?
                          time='2042-03-05 20:00:00',
                          duration_hours=4,
                        )
        self.assertEqual(self.client.post(url,args_dict,HTTP_ACCEPT="application/json").status_code,302)
        #self.assertEqual(mtg.timeslot_set.filter(name__contains='Kaboom').count(),0)
        self.assertEqual(mtg.timeslot_set.filter(type__slug='plenary').count(),0)
        self.assertEqual(self.client.post(url,args_dict,REMOTE_USER="plain",HTTP_ACCEPT="application/json").status_code,403)
        self.assertEqual(mtg.timeslot_set.filter(type__slug='plenary').count(),0)
        r = self.client.post(url,args_dict,REMOTE_USER="secretary",HTTP_ACCEPT="application/json")
        self.assertEqual(r.status_code,302)
        # Need to talk about evolving the model - having 2 things spring into being here doesn't match what the api implies
        self.assertEqual(mtg.timeslot_set.filter(type__slug='plenary').count(),2)
        new_url = r['Location']
        self.assertTrue('timeslot/%s.json'%mtg.timeslot_set.filter(type__slug='plenary')[0].pk in new_url)
        self.assertEqual(self.client.delete(new_url,REMOTE_USER="AnonymousUser").status_code,403)
        self.assertEqual(mtg.timeslot_set.filter(type__slug='plenary').count(),2)
        self.assertEqual(self.client.delete(new_url,REMOTE_USER="plain").status_code,403)
        self.assertEqual(mtg.timeslot_set.filter(type__slug='plenary').count(),2)
        self.assertEqual(self.client.delete(new_url,REMOTE_USER="plain").status_code,403)
        r = self.client.delete(new_url,REMOTE_USER="secretary")
        self.assertEqual(r.status_code,200)
        self.assertTrue('{"error":"none"}' in r.content)
        self.assertEqual(mtg.timeslot_set.filter(type__slug='plenary').count(),0)
        
    def test_manipulate_new_agenda(self):
        mtg = Meeting.objects.get(number=42)
        url = urlreverse('ietf.meeting.ajax.agenda_infosurl',kwargs=dict(num=42))
        args_dict = dict( name='fakeagenda1',visible='True')
        self.assertEqual(self.client.post(url,args_dict,HTTP_ACCEPT="application/json").status_code,302)
        self.assertEqual(mtg.schedule_set.filter(name='fakeagenda1').count(),0)
        self.assertEqual(self.client.post(url,args_dict,REMOTE_USER="plain",HTTP_ACCEPT="application/json").status_code,403)
        self.assertEqual(mtg.schedule_set.filter(name='fakeagenda1').count(),0)
        r = self.client.post(url,args_dict,REMOTE_USER="secretary",HTTP_ACCEPT="application/json")
        self.assertEqual(r.status_code,302)
        self.assertEqual(mtg.schedule_set.filter(name='fakeagenda1').count(),1)
        new_url = r['Location']
        self.assertTrue('agendas/fakeagenda1.json' in new_url)

        self.assertTrue(mtg.schedule_set.get(name='fakeagenda1').visible)
        # put? (From test.api.test_updateAgendaSecretariat)
        r = self.client.put(new_url,data='visible=0',content_type='application/x-www-form-urlencoded',REMOTE_USER='secretary',HTTP_ACCEPT='application/json')
        self.assertEqual(r.status_code,200)
        self.assertFalse(mtg.schedule_set.get(name='fakeagenda1').visible)

        self.assertEqual(self.client.delete(new_url,REMOTE_USER="AnonymousUser").status_code,403)
        self.assertEqual(mtg.schedule_set.filter(name='fakeagenda1').count(),1)
        self.assertEqual(self.client.delete(new_url,REMOTE_USER="plain").status_code,403)
        self.assertEqual(mtg.schedule_set.filter(name='fakeagenda1').count(),1)
        self.assertEqual(self.client.delete(new_url,REMOTE_USER="plain").status_code,403)
        r = self.client.delete(new_url,REMOTE_USER="secretary")
        self.assertEqual(r.status_code,200)
        self.assertTrue('{"error":"none"}' in r.content)
        self.assertEqual(mtg.schedule_set.filter(name='fakeagenda1').count(),0)

    def test_set_agenda(self):
        mtg = Meeting.objects.get(number=42)
        url = '/meeting/42.json'
        self.assertEqual(self.client.post(url,data='agenda=None',content_type='application/x-www.form-urlencoded',HTTP_ACCEPT='application/json').status_code,302)
        mtg = Meeting.objects.get(pk=mtg.pk)
        self.assertNotEqual(mtg.agenda,None)
        self.assertEqual(self.client.post(url,data='agenda=None',content_type='application/x-www.form-urlencoded',HTTP_ACCEPT='application/json',REMOTE_USER='plain').status_code,403)
        mtg = Meeting.objects.get(pk=mtg.pk)
        self.assertNotEqual(mtg.agenda,None)
        self.assertEqual(self.client.post(url,data='agenda=None',content_type='application/x-www.form-urlencoded',HTTP_ACCEPT='application/json',REMOTE_USER='secretary').status_code,200)
        mtg = Meeting.objects.get(pk=mtg.pk)
        self.assertEqual(mtg.agenda,None)
        self.assertEqual(self.client.post(url,data='agenda=pl_pub_vis',content_type='application/x-www.form-urlencoded',HTTP_ACCEPT='application/json',REMOTE_USER='secretary').status_code,200)
        mtg = Meeting.objects.get(pk=mtg.pk)
        self.assertEqual(mtg.agenda,mtg.schedule_set.get(name='pl_pub_vis'))
        self.assertEqual(self.client.post(url,data='agenda=pl_pri_vis',content_type='application/x-www.form-urlencoded',HTTP_ACCEPT='application/json',REMOTE_USER='secretary').status_code,406)
        mtg = Meeting.objects.get(pk=mtg.pk)
        self.assertEqual(mtg.agenda,mtg.schedule_set.get(name='pl_pub_vis'))

    def test_readonly(self):
        mtg = Meeting.objects.get(number=42)
        schedule = mtg.agenda
        url = '/dajaxice/ietf.meeting.readonly/'
        argv_dict = {'argv':'{"meeting_num":"%s","schedule_id":"%s"}'%(mtg.number,schedule.pk)}

        r = self.client.post(url,argv_dict,HTTP_ACCEPT='application/json',REMOTE_USER='AnonymousUser')
        perm = json.loads(r.content)
        self.assertFalse(perm['secretariat'])
        self.assertTrue(perm['read_only'])
        self.assertFalse(perm['write_perm'])      

        r = self.client.post(url,argv_dict,HTTP_ACCEPT='application/json',REMOTE_USER='plain')
        perm = json.loads(r.content)
        self.assertFalse(perm['secretariat'])
        self.assertTrue(perm['read_only'])
        self.assertFalse(perm['write_perm'])      

        r = self.client.post(url,argv_dict,HTTP_ACCEPT='application/json',REMOTE_USER='ad')
        perm = json.loads(r.content)
        self.assertFalse(perm['secretariat'])
        self.assertTrue(perm['read_only'])
        self.assertTrue(perm['write_perm'])      

        r = self.client.post(url,argv_dict,HTTP_ACCEPT='application/json',REMOTE_USER='secretary')
        perm = json.loads(r.content)
        self.assertTrue(perm['secretariat'])
        self.assertFalse(perm['read_only'])
        self.assertTrue(perm['write_perm'])      

    def setUp(self):
        make_test_data()

        # Shouldn't these be in a stylesheet instead of python dicts?
        fg_group_colors['FARFUT']="#000"
        bg_group_colors['FARFUT']="#000"


