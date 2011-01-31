from django.db import models
from sec.core.models import *
import datetime



TIME_ZONE_CHOICES = (
    (0, 'UTC'),
    (-1, 'UTC -1'),
    (-2, 'UTC -2'),
    (-3, 'UTC -3'),
    (-4, 'UTC -4 (Eastern Summer)'),
    (-5, 'UTC -5 (Eastern Winter)'),
    (-6, 'UTC -6'),
    (-7, 'UTC -7'),
    (-8, 'UTC -8 (Pacific Winter)'),
    (-9, 'UTC -9'),
    (-10, 'UTC -10 (Hawaii Winter)'),
    (-11, 'UTC -11'),
    (+12, 'UTC +12'),
    (+11, 'UTC +11'),
    (+10, 'UTC +10 (Brisbane)'),
    (+9, 'UTC +9'),
    (+8, 'UTC +8 (Perth Winter)'),
    (+7, 'UTC +7'),
    (+6, 'UTC +6'),
    (+5, 'UTC +5'),
    (+4, 'UTC +4'),
    (+3, 'UTC +3 (Moscow Winter)'),
    (+2, 'UTC +2 (Western Europe Summer'),
    (+1, 'UTC +1 (Western Europe Winter)'),
)



SLIDE_TYPE_CHOICES=(
        ('1', '(converted) HTML'),
        ('2', 'PDF'),
        ('3', 'Text'),
        ('4', 'PowerPoint -2003 (PPT)'),
        ('5', 'Microsoft Word'),
        ('6', 'PowerPoint 2007- (PPTX)'),
    )

                     

class Meeting(models.Model):
    meeting_num = models.IntegerField(primary_key=True)
    start_date = models.DateField()
    end_date = models.DateField()
    city = models.CharField(blank=True, max_length=255)
    state = models.CharField(blank=True, max_length=255)
    country = models.CharField(blank=True, max_length=255)
    time_zone = models.IntegerField(null=True, blank=True, choices=TIME_ZONE_CHOICES)
    ack = models.TextField(blank=True)
    agenda_html = models.TextField(blank=True)
    agenda_text = models.TextField(blank=True)
    future_meeting = models.TextField(blank=True)
    overview1 = models.TextField(blank=True)
    overview2 = models.TextField(blank=True)
#    def __str__(self):
#        return "%s" % (self.meeting_num)
    def __unicode__(self):
        return "%s" % (self.meeting_num)

    def get_meeting_date (self,offset):
        return self.start_date + datetime.timedelta(days=offset)
#    def num(self):
#        return self.meeting_num
    class Meta:
        db_table = 'meetings'


class Proceeding(models.Model):
    meeting_num = models.ForeignKey(Meeting, db_column='meeting_num', unique=True, primary_key=True)
    dir_name = models.CharField(blank=True, max_length=25)
    sub_begin_date = models.DateField(null=True, blank=True)
    sub_cut_off_date = models.DateField(null=True, blank=True)
    frozen = models.IntegerField(null=True, blank=True)
    c_sub_cut_off_date = models.DateField(null=True, blank=True)
    pr_from_date = models.DateField(null=True, blank=True)
    pr_to_date = models.DateField(null=True, blank=True)
#    def __str__(self):
#        return "%s" % (self.meeting_num)
    def __unicode__(self):
        return "%s" % (self.meeting_num)

    #Custom method for use in template
    def is_frozen(self):
	 if self.frozen == 1:
            return True
         else:
            return False
    class Meta:
        db_table = 'proceedings'
        ordering = ['?']        # workaround for FK primary key



class Slide(models.Model):
    id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(Meeting, db_column='meeting_num')
    group_acronym_id = models.IntegerField(null=True, blank=True)
    slide_num = models.IntegerField(null=True, blank=True)
    slide_type_id = models.IntegerField(choices=SLIDE_TYPE_CHOICES)
    slide_name = models.CharField(blank=True, max_length=255)
    irtf = models.IntegerField()
    interim = models.BooleanField()
    order_num = models.IntegerField(null=True, blank=True)
    in_q = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return "%d %s %s" % (self.meeting_id, self.group_acronym_id, self.slide_name)
    class Meta:
        db_table = 'slides'


class Minute(models.Model):
    id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(Meeting, db_column='meeting_num')
    group_acronym_id = models.IntegerField()
    filename = models.CharField(blank=True, max_length=255)
    irtf = models.IntegerField()
    interim = models.BooleanField()
    def __unicode__(self):
        return "%d %s" % (self.meeting_id, self.group_acronym_id)

    class Meta:
        db_table = 'minutes'


class WgAgenda(models.Model):
    id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(Meeting, db_column='meeting_num')
    group_acronym_id = models.IntegerField()
    filename = models.CharField(max_length=255)
    irtf = models.IntegerField()
    interim = models.BooleanField()
    
    def __unicode__(self):
        return "%d %s" % (self.meeting_id, self.group_acronym_id)

    class Meta:
        db_table = 'wg_agenda'


class MeetingRoom(models.Model):
    room_id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(Meeting, db_column='meeting_num')
    room_name = models.CharField(max_length=255)
    def __unicode__(self):
        return "[%d] %s" % (self.meeting_id, self.room_name)
    class Meta:
        db_table = 'meeting_rooms'


class SessionName(models.Model):
    session_name_id = models.AutoField(primary_key=True)
    session_name = models.CharField(blank=True, max_length=255)
    def __unicode__(self):
        return self.session_name
    class Meta:
        db_table = 'session_names'


class MeetingTime(models.Model):
    time_id = models.AutoField(primary_key=True)
    time_desc = models.CharField(max_length=100)
    meeting = models.ForeignKey(Meeting, db_column='meeting_num')
    day_id = models.IntegerField()
    session_name = models.ForeignKey(SessionName,null=True)
    def __unicode__(self):
        return "[%d] |%s| %s" % (self.meeting_id, (self.meeting.start_date + datetime.timedelta(self.day_id)).strftime('%A'), self.time_desc)
    class Meta:
        db_table = 'meeting_times'



class WgMeetingSession(models.Model):
    session_id = models.AutoField(primary_key=True)
    meeting = models.ForeignKey(Meeting, db_column='meeting_num')
    group_acronym_id = models.IntegerField()
    irtf = models.NullBooleanField()
    num_session = models.IntegerField()
    length_session1 = models.CharField(blank=True, max_length=100)
    length_session2 = models.CharField(blank=True, max_length=100)
    length_session3 = models.CharField(blank=True, max_length=100)
    conflict1 = models.CharField(blank=True, max_length=255)
    conflict2 = models.CharField(blank=True, max_length=255)
    conflict3 = models.CharField(blank=True, max_length=255)
    conflict_other = models.TextField(blank=True)
    special_req = models.TextField(blank=True)
    number_attendee = models.IntegerField(null=True, blank=True)
    approval_ad = models.IntegerField(null=True, blank=True)
    status_id = models.IntegerField(null=True, blank=True)
    ts_status_id = models.IntegerField(null=True, blank=True)
    requested_date = models.DateField(null=True, blank=True)
    approved_date = models.DateField(null=True, blank=True)
    requested_by = models.ForeignKey(PersonOrOrgInfo, db_column='requested_by')
    scheduled_date = models.DateField(null=True, blank=True)
    last_modified_date = models.DateField(null=True, blank=True)
    ad_comments = models.TextField(blank=True,null=True)
    sched_room_id1 = models.ForeignKey(MeetingRoom, db_column='sched_room_id1', null=True, blank=True, related_name='here1')
    sched_time_id1 = models.ForeignKey(MeetingTime, db_column='sched_time_id1', null=True, blank=True, related_name='now1')
    sched_date1 = models.DateField(null=True, blank=True)
    sched_room_id2 = models.ForeignKey(MeetingRoom, db_column='sched_room_id2', null=True, blank=True, related_name='here2')
    sched_time_id2 = models.ForeignKey(MeetingTime, db_column='sched_time_id2', null=True, blank=True, related_name='now2')
    sched_date2 = models.DateField(null=True, blank=True)
    sched_room_id3 = models.ForeignKey(MeetingRoom, db_column='sched_room_id3', null=True, blank=True, related_name='here3')
    sched_time_id3 = models.ForeignKey(MeetingTime, db_column='sched_time_id3', null=True, blank=True, related_name='now3')
    sched_date3 = models.DateField(null=True, blank=True)
    special_agenda_note = models.CharField(blank=True, max_length=255)
    combined_room_id1 = models.ForeignKey(MeetingRoom, db_column='combined_room_id1', null=True, blank=True, related_name='here4')
    combined_time_id1 = models.ForeignKey(MeetingTime, db_column='combined_time_id1', null=True, blank=True, related_name='now4')
    combined_room_id2 = models.ForeignKey(MeetingRoom, db_column='combined_room_id2', null=True, blank=True, related_name='here5')
    combined_time_id2 = models.ForeignKey(MeetingTime, db_column='combined_time_id2', null=True, blank=True, related_name='now5')

    def __unicode__(self):
        return "%s %s " %(self.group_acronym_id,self.meeting)



    class Meta:
        db_table = 'wg_meeting_sessions'


class IRTF(models.Model):
    irtf_id = models.AutoField(primary_key=True)
    acronym = models.CharField(blank=True, max_length=25, db_column='irtf_acronym')
    name = models.CharField(blank=True, max_length=255, db_column='irtf_name')
    charter_text = models.TextField(blank=True,null=True)
    meeting_scheduled = models.BooleanField(blank=True)
    def __str__(self):
        return self.acronym
    class Meta:
        db_table = 'irtf'
        verbose_name="IRTF Research Group"









































































