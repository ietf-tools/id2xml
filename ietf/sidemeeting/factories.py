import factory
import random

import ietf.sidemeeting.models as sm_models
from ietf.meeting.factories import MeetingFactory
from ietf.group.factories import GroupFactory
from ietf.person.factories import PersonFactory
import datetime as dt


class SideMeetingTypeNameFactory(factory.DjangoModelFactory):
    class Meta:
        model = sm_models.SideMeetingTypeName

    slug = "ietf"
    name = "IETF"


class SideMeetingSessionFactory(factory.DjangoModelFactory):
    class Meta:
        model = sm_models.SideMeetingSession

    meeting = factory.SubFactory(MeetingFactory)
    type_id = 'sidemeeting'
    group = factory.SubFactory(GroupFactory)
    requested_by = factory.SubFactory(PersonFactory)
    status_id = 'sched'
    requested_start_time = '2'
    sidemeeting_type = factory.SubFactory(SideMeetingTypeNameFactory)
