# old meeting models can be found in ../proceedings/models.py

import pytz, datetime

from django.db import models
from django.conf import settings
from timedeltafield import TimedeltaField

from ietf.group.models import Group
from ietf.person.models import Person
from ietf.doc.models import Document
from ietf.name.models import MeetingTypeName, TimeSlotTypeName, SessionStatusName, ConstraintName

countries = pytz.country_names.items()
countries.sort(lambda x,y: cmp(x[1], y[1]))

timezones = [(name, name) for name in pytz.common_timezones]
timezones.sort()

class Meeting(models.Model):
    # number is either the number for IETF meetings, or some other
    # identifier for interim meetings/IESG retreats/liaison summits/...
    number = models.CharField(unique=True, max_length=64)
    type = models.ForeignKey(MeetingTypeName)
    # Date is useful when generating a set of timeslot for this meeting, but
    # is not used to determine date for timeslot instances thereafter, as
    # they have their own datetime field.
    date = models.DateField()           
    city = models.CharField(blank=True, max_length=255)
    country = models.CharField(blank=True, max_length=2, choices=countries)
    # We can't derive time-zone from country, as there are some that have
    # more than one timezone, and the pytz module doesn't provide timezone
    # lookup information for all relevant city/country combinations.
    time_zone = models.CharField(blank=True, max_length=255, choices=timezones)
    venue_name = models.CharField(blank=True, max_length=255)
    venue_addr = models.TextField(blank=True)
    break_area = models.CharField(blank=True, max_length=255)
    reg_area = models.CharField(blank=True, max_length=255)
    agenda_note = models.TextField(blank=True, help_text="Text in this field will be placed at the top of the html agenda page for the meeting.  HTML can be used, but will not validated.")
    agenda     = models.ForeignKey('Schedule',null=True,blank=True, related_name='+')

    def __unicode__(self):
        if self.type_id == "ietf":
            return "IETF-%s" % (self.number)
        else:
            return self.number

    def time_zone_offset(self):
        # Look at the time of 8 o'clock sunday, rather than 0h sunday, to get
        # the right time after a possible summer/winter time change.
        return pytz.timezone(self.time_zone).localize(datetime.datetime.combine(self.date, datetime.time(8, 0))).strftime("%z")

    def get_meeting_date (self,offset):
        return self.date + datetime.timedelta(days=offset)

    def end_date(self):
        return self.get_meeting_date(5)

    @classmethod
    def get_first_cut_off(cls):
        date = cls.objects.all().filter(type="ietf").order_by('-date')[0].date
        offset = datetime.timedelta(days=settings.FIRST_CUTOFF_DAYS)
        return date - offset

    @classmethod
    def get_second_cut_off(cls):
        date = cls.objects.all().filter(type="ietf").order_by('-date')[0].date
        offset = datetime.timedelta(days=settings.SECOND_CUTOFF_DAYS)
        return date - offset

    @classmethod
    def get_ietf_monday(cls):
        date = cls.objects.all().filter(type="ietf").order_by('-date')[0].date
        return date + datetime.timedelta(days=-date.weekday(), weeks=1)

    # the various dates are currently computed
    def get_submission_start_date(self):
        return self.date + datetime.timedelta(days=settings.SUBMISSION_START_DAYS)
    def get_submission_cut_off_date(self):
        return self.date + datetime.timedelta(days=settings.SUBMISSION_CUTOFF_DAYS)
    def get_submission_correction_date(self):
        return self.date + datetime.timedelta(days=settings.SUBMISSION_CORRECTION_DAYS)

class Room(models.Model):
    meeting = models.ForeignKey(Meeting)
    name = models.CharField(max_length=255)
    capacity = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.name

class TimeSlot(models.Model):
    """
    Everything that would appear on the meeting agenda of a meeting is
    mapped to a time slot, including breaks. Sessions are connected to
    TimeSlots during scheduling. A template function to populate a
    meeting with an appropriate set of TimeSlots is probably also
    needed.
    """
    meeting = models.ForeignKey(Meeting)
    type = models.ForeignKey(TimeSlotTypeName)
    name = models.CharField(max_length=255)
    time = models.DateTimeField()
    duration = TimedeltaField()
    location = models.ForeignKey(Room, blank=True, null=True)
    show_location = models.BooleanField(default=True, help_text="Show location in agenda")
    sessions = models.ManyToManyField('Session', related_name='slots', through='ScheduledSession', null=True, blank=True, help_text=u"Scheduled session, if any")
    modified = models.DateTimeField(default=datetime.datetime.now)

    @property
    def time_desc(self):
        return u"%s-%s" % (self.time.strftime("%H%M"), (self.time + self.duration).strftime("%H%M"))

    def meeting_date(self):
        return self.time.date()

    def registration(self):
        # below implements a object local cache
        # it tries to find a timeslot of type registration which starts at the same time as this slot
        # so that it can be shown at the top of the agenda.
        if not hasattr(self, '_reg_info'):
            try:
                self._reg_info = TimeSlot.objects.get(meeting=self.meeting, time__month=self.time.month, time__day=self.time.day, type="reg")
            except TimeSlot.DoesNotExist:
                self._reg_info = None
        return self._reg_info

    def reg_info(self):
        return (self.registration() is not None)

    def __unicode__(self):
        location = self.get_location()
        if not location:
            location = "(no location)"
            
        return u"%s: %s-%s %s, %s" % (self.meeting.number, self.time.strftime("%m-%d %H:%M"), (self.time + self.duration).strftime("%H:%M"), self.name, location)

    def end_time(self):
        return self.time + self.duration

    def get_location(self):
        location = self.location
        if location:
            location = location.name
        elif self.type_id == "reg":
            location = self.meeting.reg_area
        elif self.type_id == "break":
            location = self.meeting.break_area
                
        if not self.show_location:
            location = ""
            
        return location

    def session_name(self):
        if self.type_id not in ("session", "plenary"):
            return None
        
        class Dummy(object):
            def __unicode__(self):
                return self.session_name
        d = Dummy()
        d.session_name = self.name
        return d

    def session_for_schedule(self, schedule):
        ss = scheduledsession_set.filter(schedule=schedule).all()[0]
        if ss:
            return ss.session
        else:
            return None
 
    def scheduledsessions_at_same_time(self, agenda=None):
        if agenda is None:
            agenda = self.meeting.agenda
            
        return agenda.scheduledsession_set.filter(timeslot__time=self.time, timeslot__type__in=("session", "plenary", "other"))

    @property
    def is_plenary(self):
        return self.type_id == "plenary"
    
    @property
    def is_plenary_type(self, name, agenda=None):
        return self.scheduledsessions_at_same_time(agenda)[0].acronym == name
    
class Schedule(models.Model):
    """
    Each person may have multiple agendas saved.
    An Agenda may be made visible, which means that it will show up in
    public drop down menus, etc.  It may also be made public, which means
    that someone who knows about it by name/id would be able to reference
    it.  A non-visible, public agenda might be passed around by the
    Secretariat to IESG members for review.  Only the owner may edit the
    agenda, others may copy it
    """
    meeting  = models.ForeignKey(Meeting, null=True)
    name     = models.CharField(max_length=16, blank=False)
    owner    = models.ForeignKey(Person)
    visible  = models.BooleanField(default=True, help_text=u"Make this agenda publically available")
    public   = models.BooleanField(default=True, help_text=u"Make this agenda available to those who know about it")
    # considering copiedFrom = models.ForeignKey('Schedule', blank=True, null=True)

    def __unicode__(self):
        return u"%s:%s(%s)" % (self.meeting, self.name, self.owner)
    

class ScheduledSession(models.Model):
    """
    This model provides an N:M relationship between Session and TimeSlot.
    Each relationship is attached to the named agenda, which is owned by
    a specific person/user.
    """
    timeslot = models.ForeignKey('TimeSlot', null=False, blank=False, help_text=u"")
    session  = models.ForeignKey('Session', null=True, default=None, help_text=u"Scheduled session")
    schedule = models.ForeignKey('Schedule', null=False, blank=False, help_text=u"Who made this agenda")
    modified = models.DateTimeField(default=datetime.datetime.now)
    notes    = models.TextField(blank=True)

    def __unicode__(self):
        return u"%s [%s<->%s]" % (self.schedule, self.session, self.timeslot)

    @property
    def room_name(self):
        return self.timeslot.location.name
    
    @property
    def special_agenda_note(self):
        return self.session.agenda_note if self.session else ""

    @property
    def acronym(self):
        if self.session and self.session.group:
            return self.session.group.acronym
    
    @property
    def acronym_name(self):
        if not self.session:
            return self.notes
        if hasattr(self, "interim"):
            return self.session.group.name + " (interim)"
        elif self.session.name:
            return self.session.name
        else:
            return self.session.group.name

    @property
    def session_name(self):
        if self.timeslot.type_id not in ("session", "plenary"):
            return None
        return self.timeslot.name
        
    @property
    def area(self):
        if not self.session or not self.session.group:
            return ""
        if self.session.group.type_id == "irtf":
            return "irtf"
        if self.timeslot.type_id == "plenary":
            return "1plenary"
        if not self.session.group.parent or not self.session.group.parent.type_id in ["area","irtf"]:
            return ""
        return self.session.group.parent.acronym

    @property
    def break_info(self):
        breaks = self.schedule.scheduledsessions_set.filter(timeslot__time__month=self.timeslot.time.month, timeslot__time__day=self.timeslot.time.day, timeslot__type="break").order_by("timeslot__time")
        now = self.timeslot.time_desc[:4]
        for brk in breaks:
            if brk.time_desc[-4:] == now:
                return brk
        return None
    
    @property
    def area_name(self):
        if self.timeslot.type_id == "plenary":
            return "Plenary Sessions"
        elif self.session and self.session.group and self.session.group.acronym == "edu":
            return "Training"
        elif not self.session or not self.session.group or not self.session.group.parent or not self.session.group.parent.type_id == "area":
            return ""
        return self.session.group.parent.name

    @property
    def isWG(self):
        if not self.session or not self.session.group:
            return False
        if self.session.group.type_id == "wg" and self.session.group.state_id != "bof":
            return True

    @property
    def group_type_str(self):
        if not self.session or not self.session.group:
            return ""
        if self.session.group and self.session.group.type_id == "wg":
            if self.session.group.state_id == "bof":
                return "BOF"
            else:
                return "WG"

        return ""

class Constraint(models.Model):
    """
    Specifies a constraint on the scheduling.
    One type (name=conflic?) of constraint is between source WG and target WG,
           e.g. some kind of conflict.
    Another type (name=adpresent) of constraing is between source WG and
           availability of a particular Person, usually an AD.
    A third type (name=avoidday) of constraing is between source WG and
           a particular day of the week, specified in day.
    """
    meeting = models.ForeignKey(Meeting)
    source = models.ForeignKey(Group, related_name="constraint_source_set")
    target = models.ForeignKey(Group, related_name="constraint_target_set", null=True)
    person = models.ForeignKey(Person, null=True, blank=True)
    day    = models.DateTimeField(null=True, blank=True)
    name   = models.ForeignKey(ConstraintName)

    def __unicode__(self):
        return u"%s %s %s" % (self.source, self.name.name.lower(), self.target)

class Session(models.Model):
    """Session records that a group should have a session on the
    meeting (time and location is stored in a TimeSlot) - if multiple
    timeslots are needed, multiple sessions will have to be created.
    Training sessions and similar are modeled by filling in a
    responsible group (e.g. Edu team) and filling in the name."""
    meeting = models.ForeignKey(Meeting)
    name = models.CharField(blank=True, max_length=255, help_text="Name of session, in case the session has a purpose rather than just being a group meeting")
    short = models.CharField(blank=True, max_length=32, help_text="Short version of 'name' above, for use in filenames")
    group = models.ForeignKey(Group)    # The group type determines the session type.  BOFs also need to be added as a group.
    attendees = models.IntegerField(null=True, blank=True)
    agenda_note = models.CharField(blank=True, max_length=255)
    requested = models.DateTimeField(default=datetime.datetime.now)
    requested_by = models.ForeignKey(Person)
    requested_duration = TimedeltaField(default=0)
    comments = models.TextField(blank=True)
    status = models.ForeignKey(SessionStatusName)
    scheduled = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(default=datetime.datetime.now)

    materials = models.ManyToManyField(Document, blank=True)

    def agenda(self):
        try:
            return self.materials.get(type="agenda",states__type="agenda",states__slug="active")
        except Exception:
            return None

    def minutes(self):
        try:
            return self.materials.get(type="minutes",states__type="minutes",states__slug="active")
        except Exception:
            return None

    def slides(self):
        try:
            return self.materials.filter(type="slides",states__type="slides",states__slug="active").order_by("order")
        except Exception:
            return []

    def __unicode__(self):
        if self.meeting.type_id == "interim":
            return self.meeting.number

        ss0 = self.scheduledsession_set.order_by('timeslot__time')[0]
        return u"%s: %s %s" % (self.meeting, self.group.acronym, ss0.timeslot.time.strftime("%H%M") if ss0 else "(unscheduled)")

    def constraints(self):
        return Constraint.objects.filter(source=self.group, meeting=self.meeting).order_by('name__name')

    def reverse_constraints(self):
        return Constraint.objects.filter(target=self.group, meeting=self.meeting).order_by('name__name')

    def scheduledsession_for_agenda(self, schedule):
        return self.scheduledsession_set.filter(schedule=schedule)[0]

    def official_scheduledsession(self):
        return self.scheduledsession_for_agenda(self.meeting.agenda)
