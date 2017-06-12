"""
testcases
1) createview
2) updateview
3) list
4) approve
5)

ownership ability to use views



"""
from ietf.utils.test_utils import unicontent
from django.urls import reverse as urlreverse
from django.test import TestCase
from ietf.group.factories import GroupFactory, GroupEventFactory
from ietf.person.factories import PersonFactory
from ietf.sidemeeting.factories import SideMeetingSessionFactory
import datetime as dt


class SideMeetingTestCase(TestCase):
    def test_setup(self):
        pass

    def test_session_create(self):
        group = GroupFactory.create(type_id='ietf', state_id='active')
        # session = SideMeetingSessionFactory.create(
        #     meeting__type_id='sidemeeting',
        #     group=group,
        #     requested_prim_start_date=dt.datetime.now(),
        #     requested_alt_start_date=dt.datetime.now() + dt.timedelta(days=10),
        #     meeting__date=(dt.date.today() + dt.timedelta(days=90)))
        #attendees23commentstest ABCcsrfmiddlewaretokenTiiR7sNrXPGJc4QzdknX3oIYJ6M2FR56NtvnORFzcuMF4bLNJZhBJ8QJCfrcq5GNgroup1249meeting724nameABCrequested_alt_start_date06/28/2017requested_duration00:00:00requested_prim_start_date06/13/2017requested_start_time2resources2resources4sidemeeting_typeietf
        url = urlreverse('side-meeting-add')
        r = self.client.post(url, {'something': 'something'})
