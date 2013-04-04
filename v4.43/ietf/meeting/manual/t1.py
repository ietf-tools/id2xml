from ietf.meeting.tests.view import ViewTestCase 
from django.contrib.auth.models import User
from django.test.client import Client
from ietf.meeting.models  import TimeSlot, Session, ScheduledSession
from ietf.meeting.tests.auths import auth_joeblow, auth_wlo, auth_ietfchair, auth_ferrel
from ietf.meeting.views import get_meeting

mtg = get_meeting(83)
fred = mtg.get_schedule_by_name("fred")

client = Client()
client.post('/meeting/83/agenda', {'savename': "fred",'saveas': "saveas",}, **auth_wlo)

