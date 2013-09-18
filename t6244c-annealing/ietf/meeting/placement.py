#  FILE: ietf/meeting/placement.py
#
# Copyright (c) 2013, The IETF Trust. See ../../../LICENSE.
#
# This file contains a model that encapsulates the progress of the automatic placer.
# Each step of placement is stored as a row in a table, not because this is necessary,
# but because it helps to debug things.
#
# A production run of the placer would do the same work, but simply not save anything.
#

import sys
import datetime

from django.db           import models
from settings import BADNESS_UNPLACED, BADNESS_TOOSMALL_50, BADNESS_TOOSMALL_100, BADNESS_TOOBIG, BADNESS_MUCHTOOBIG
from ietf.meeting.models import Schedule, ScheduledSession,TimeSlot,Room

class FakeScheduledSession:
    """
    This model provides a fake (not-backed by database) N:M relationship between
    Session and TimeSlot, but in this case TimeSlot is always None, because the
    Session is not scheduled.
    """
    timeslot = None
    session  = models.ForeignKey('Session', null=True, default=None, help_text=u"Scheduled session")
    schedule = models.ForeignKey('Schedule', null=False, blank=False, help_text=u"Who made this agenda")
    extendedfrom = models.ForeignKey('ScheduledSession', null=True, default=None, help_text=u"Timeslot this session is an extension of")
    modified = models.DateTimeField(default=datetime.datetime.now)
    notes    = models.TextField(blank=True)
    badness  = models.IntegerField(default=0, blank=True, null=True)

    # this is a copy of ScheduledSession's methods... This is DUCK TYPING.
    def __unicode__(self):
        return u"%s [%s<->%s]" % (self.schedule, self.session, self.timeslot)

    def __str__(self):
        return self.__unicode__()

    @property
    def room_name(self):
        return "noroom"

    @property
    def special_agenda_note(self):
        return self.session.agenda_note if self.session else ""

    @property
    def acronym(self):
        if self.session and self.session.group:
            return self.session.group.acronym

    @property
    def slot_to_the_right(self):
        return None

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
        return self.session.name

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
        return None

    @property
    def area_name(self):
        if self.session and self.session.group and self.session.group.acronym == "edu":
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

    @property
    def slottype(self):
        return ""

    @property
    def empty_str(self):
        # return JS happy value
        if self.session:
            return "False"
        else:
            return "True"

    def json_dict(self, selfurl):
        ss = dict()
        ss['scheduledsession_id'] = self.id
        #ss['href']          = self.url(sitefqdn)
        ss['empty'] =  self.empty_str
        ss['timeslot_id'] = self.timeslot.id
        if self.session:
            ss['session_id']  = self.session.id
        ss['room'] = slugify(self.timeslot.location)
        ss['roomtype'] = self.timeslot.type.slug
        ss["time"]     = date_format(self.timeslot.time, 'Hi')
        ss["date"]     = time_format(self.timeslot.time, 'Y-m-d')
        ss["domid"]    = self.timeslot.js_identifier
        return ss


# this object maintains the current state of the placement tool.
# the assignments hash says where the sessions would go.
class CurrentScheduleState:
    current_assignments = {}
    available_slots = []
    total_slots     = 0

    def __init__(self, schedule):
        # initialize available_slots with the places that a session can go based upon the
        # scheduledsession objects of the provided schedule.
        # for each session which is not initially scheduled, also create a scheduledsession
        # that has a session, but no timeslot.
        useableslots_qs      = schedule.scheduledsession_set.filter(timeslot__type = "session")
        print "useable qs: %u\n" % (useableslots_qs.count())
        num_useable_slots    = 0

        # turn into an array for use in algorithm.
        for x in useableslots_qs.all():
            print "real slot: %s" % (x)
            self.available_slots.append(x)
            num_useable_slots = num_useable_slots + 1

        self.total_slots = num_useable_slots

        self.current_assignments,sessions,total,scheduled = schedule.group_session_mapping
        print "sessions: %u, %u" % (len(sessions),self.total_slots)

        for session,location in sessions.iteritems():
            print "session: %s location: %s" % (session, location)
            if location == None:
                fs = FakeScheduledSession()
                fs.session  = session
                fs.schedule = schedule
                self.available_slots.append(fs)
                print "  fake session: %s" % (fs)
                self.total_slots = self.total_slots + 1
            else:
                print "  no fake slot"
        print "unscheduled sessions: %u\n" % (self.total_slots)

class AutomaticScheduleStep(models.Model):
    schedule   = models.ForeignKey('Schedule', null=False, blank=False, help_text=u"Who made this agenda")
    session    = models.ForeignKey('Session', null=True, default=None, help_text=u"Scheduled session involved")
    moved_from = models.ForeignKey('ScheduledSession', related_name="+", null=True, default=None, help_text=u"Where session was")
    moved_to   = models.ForeignKey('ScheduledSession', related_name="+", null=True, default=None, help_text=u"Where session went")
    stepnum    = models.IntegerField(default=0, blank=True, null=True)

