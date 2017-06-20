"""
testcases
1) createview
2) updateview
3) list
4) approve
5)

ownership ability to use views



"""
from copy import copy
from ietf.utils.test_utils import unicontent
from django.urls import reverse as urlreverse
from django.test import TestCase
from ietf.group.factories import GroupFactory, GroupEventFactory
from ietf.person.factories import PersonFactory
#from ietf.sidemeeting.factories import SideMeetingSessionFactory
from django.contrib.auth.models import User
from ietf.group.models import Role, Group
from ietf.name.models import RoleName
from ietf.person.models import Person, Email
from ietf.meeting.forms_sidemeeting import SideMeetingApproveForm, SideMeetingForm
from ietf.meeting.test_data import make_meeting_test_data
from ietf.meeting.models import ResourceAssociation, SideMeetingSession, SideMeetingTypeName

import datetime as dt

#from selenium import webdriver


class SideMeetingFormTestCase(TestCase):
    def setUp(self):
        #        self.driver = webdriver.Firefox()

        # definition of core objects required by the form
        self.meeting = make_meeting_test_data()
        self.resources = ResourceAssociation.objects.all()[0:2]
        self.sidemeeting_type = SideMeetingTypeName.objects.create(
            slug="ietf", name="IETF")
        self.group = Group.objects.get(acronym="secretariat")

        self.username = "django"
        self.user = User.objects.create_user(
            self.username, password=self.username, email="django@amsl.com")

        # data for the form
        self.data = {
            'attendees': '23',
            'comments': 'test ABC',
            'group': str(self.group.id),
            'meeting': str(self.meeting.id),
            'name': 'ABC',
            'requested_alt_start_date': '06/28/2017',
            'requested_duration': '00:00:00',
            'requested_prim_start_date': '06/13/2017',
            'requested_start_time': '2',
            'resources': [r.id for r in self.resources],
            'sidemeeting_type': str(self.sidemeeting_type.slug)
        }

    def test_valid_form(self):
        form = SideMeetingForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_empty_name(self):
        data = copy(self.data)
        data["name"] = ""
        form = SideMeetingForm(data=data)
        actual = form.errors['name']
        expected = [u'Required field']
        self.assertEqual(actual, expected)

    def test_attendees_is_integer(self):
        data = copy(self.data)
        data["attendees"] = "nope"
        form = SideMeetingForm(data=data)
        actual = form.errors['attendees']
        expected = [u'Enter a whole number.']
        self.assertEqual(actual, expected)

    def test_attendees_below_range(self):
        data = copy(self.data)
        data["attendees"] = "0"
        form = SideMeetingForm(data=data)
        actual = form.errors['attendees']
        expected = [u'Invalid number of attendees']
        self.assertEqual(actual, expected)

    def test_attendees_above_range(self):
        data = copy(self.data)
        data["attendees"] = "1000001"
        form = SideMeetingForm(data=data)
        actual = form.errors['attendees']
        expected = [u'Invalid number of attendees']
        self.assertEqual(actual, expected)

    def test_requested_start_time_bad_format(self):
        data = copy(self.data)
        data["requested_start_time"] = "badns"
        form = SideMeetingForm(data=data)
        actual = form.errors['requested_start_time']
        expected = [u'Invalid start time']
        self.assertEqual(actual, expected)

    def test_requested_start_time_hours_too_low(self):
        data = copy(self.data)
        data["requested_start_time"] = "-1"
        form = SideMeetingForm(data=data)
        actual = form.errors['requested_start_time']
        expected = [u'Invalid start time']
        self.assertEqual(actual, expected)

    def test_requested_start_time_hours_too_high(self):
        data = copy(self.data)
        data["requested_start_time"] = "25"
        form = SideMeetingForm(data=data)
        actual = form.errors['requested_start_time']
        expected = [u'Invalid start time']
        self.assertEqual(actual, expected)

    def test_requested_start_time_bad_minutes(self):
        data = copy(self.data)
        data["requested_start_time"] = "20:bd"
        form = SideMeetingForm(data=data)
        actual = form.errors['requested_start_time']
        expected = [u'Invalid start time']
        self.assertEqual(actual, expected)

    def test_requested_start_time_minutes_too_low(self):
        data = copy(self.data)
        data["requested_start_time"] = "20:-1"
        form = SideMeetingForm(data=data)
        actual = form.errors['requested_start_time']
        expected = [u'Invalid start time']
        self.assertEqual(actual, expected)

    def test_requested_start_time_minutes_too_high(self):
        data = copy(self.data)
        data["requested_start_time"] = "20:99"
        form = SideMeetingForm(data=data)
        actual = form.errors['requested_start_time']
        expected = [u'Invalid start time']
        self.assertEqual(actual, expected)

    def test_requested_start_time_whitespace_ok(self):
        data = copy(self.data)
        data["requested_start_time"] = "2:	32 "
        form = SideMeetingForm(data=data)
        self.assertTrue(form.is_valid())


class ApproveSideMeetingTestCase(TestCase):
    # def test_can_approve_sidemeeting_request(self):
    #     # PASS
    #     r = RoleName(slug="secr",name="Secretary")
    #     # FAIL
    #     assertFalse(sidemeeting.type.slug, "sidemeeting")
    #     # PASS
    #     assertTrue(group.type.slug="wg" and group.parent.role_set.filter(name='ad', person=person))
    #     # PASS
    #     assertTrue(group.type.slug == 'rg' and group.parent.role_set.filter(name='chair', person=person))

    def setUp(self):
        self.url = "/sidemeeting/approve/"
        self.sidemeeting_pk_bad = "999999999999999"

    def test_secretary(self):
        # make sure url fails for a bad sidemeeting pk
        r = self.client.get(self.url + self.sidemeeting_pk_bad)
        self.assertNotEqual(r.status_code, 200)
