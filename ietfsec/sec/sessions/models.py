from django.db import models

from sec.core.models import *
#from sec.proceedings.models import Meeting, WgMeetingSession, MeetingRoom, MeetingTime, MeetingHour
#from sec.proceedings.models import *
'''
class NotMeetingGroups(models.Model):
    group = models.ForeignKey(IETFWG, db_column='group_acronym_id')
    meeting = models.ForeignKey(Meeting, db_column='meeting_num')
    #def __unicode__(self):
    #    return u"%s-%s" % (self.meeting, self.group)
    #def __string__(self):
    #    return self.group
    class Meta:
        db_table = 'not_meeting_groups'

class NotMeetingGroup(models.Model):
    group_acronym_id = models.IntegerField()
    meeting_num = models.IntegerField()
    def __unicode__(self):
        return u"%s-%s" % (self.group_acronym_id, self.meeting_num)
    class Meta:
        db_table = 'not_meeting_groups'
'''


