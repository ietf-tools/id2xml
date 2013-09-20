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

from random              import Random

from django.db           import models
from settings import BADNESS_UNPLACED, BADNESS_TOOSMALL_50, BADNESS_TOOSMALL_100, BADNESS_TOOBIG, BADNESS_MUCHTOOBIG
from ietf.meeting.models import Schedule, ScheduledSession,TimeSlot,Room

class PlacementException(Exception):
    pass

class FakeScheduledSession:
    """
    This model provides a fake (not-backed by database) N:M relationship between
    Session and TimeSlot, but in this case TimeSlot is always None, because the
    Session is not scheduled.
    """
    timeslot = models.ForeignKey('TimeSlot', null=True, blank=False, help_text=u"")
    session  = models.ForeignKey('Session', null=True, default=None, help_text=u"Scheduled session")
    schedule = models.ForeignKey('Schedule', null=False, blank=False, help_text=u"Who made this agenda")
    extendedfrom = models.ForeignKey('ScheduledSession', null=True, default=None, help_text=u"Timeslot this session is an extension of")
    modified = models.DateTimeField(default=datetime.datetime.now)
    notes    = models.TextField(blank=True)
    badness  = models.IntegerField(default=0, blank=True, null=True)

    available_slot = None
    origss         = None

    def __init__(self, schedule):
        self.timeslot = None
        self.session  = None
        self.schedule = schedule

    def fromScheduledSession(self, ss):  # or from another FakeScheduledSession
        self.session   = ss.session
        self.schedule  = ss.schedule
        self.timeslot  = ss.timeslot
        self.modified  = ss.modified
        self.origss    = ss

    def save(self):
        pass

    # this is a partial copy of ScheduledSession's methods. Prune later.
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
    schedule            = None
    meeting             = None
    recordsteps         = True

    # this maps a *group* to a list of (session,location) pairs, using FakeScheduledSession
    current_assignments = {}
    tempdict            = {}   # used when calculating badness.

    # this contains an entry for each location, and each un-location in the form of
    # (session,location) with the appropriate part None.
    available_slots = []
    sessions        = {}
    total_slots     = 0
    random_generator = None
    badness         = None
    temperature     = 1000000
    stepnum         = 0

    def __getitem__(self, key):
        if key in self.tempdict:
            return self.tempdict[key]
        return self.current_assignments[key]

    def __iter__(self):
        return self.current_assignments.__iter__()
    def iterkeys(self):
        return self.current_assignments.__iter__()

    def add_to_available_slot(self, fs):
        size = len(self.available_slots)
        self.total_slots  = size
        self.available_slots.append(fs)
        fs.available_slot = size

    def __init__(self, schedule, seed=None):
        # initialize available_slots with the places that a session can go based upon the
        # scheduledsession objects of the provided schedule.
        # for each session which is not initially scheduled, also create a scheduledsession
        # that has a session, but no timeslot.
        self.schedule        = schedule
        self.meeting         = schedule.meeting
        self.seed            = seed
        self.badness         = schedule.badness
        self.random_generator=Random()
        self.random_generator.seed(seed)
        self.temperature     = 10000000
        self.stepnum         = 1

        useableslots_qs      = schedule.qs_scheduledsessions_without_assignments.filter(timeslot__type = "session")

        count = useableslots_qs.count()
        print "useable qs: %u\n" % (count)

        # turn into an array for use in algorithm.
        for x in useableslots_qs.all():
            #print "real slot: %s" % (x)
            fs = FakeScheduledSession(self.schedule)
            fs.fromScheduledSession(x)
            self.add_to_available_slot(fs)

        #print "Starting with %u" % (self.total_slots)

        for sess in self.meeting.sessions_that_can_meet.all():
            fs = FakeScheduledSession(self.schedule)
            fs.session     = sess
            self.sessions[sess] = fs
            self.current_assignments[sess.group] = []

        #print "Then had %u" % (self.total_slots)
        # now find slots that are not empty.
        # loop here and the one for useableslots could be merged into one loop
        allschedsessions = self.schedule.qs_scheduledsessions_with_assignments.filter(timeslot__type = "session").all()
        for ss in allschedsessions:
            # do not need to check for ss.session, because filter above only returns those ones.
            sess = ss.session
            if not (sess in self.sessions):
                print "Had to create sess for %s" % (sess)
                self.sessions[sess] = FakeScheduledSession(self.schedule)
            fs = self.sessions[sess]
            #print "Updating %s from %s" % (fs, ss)
            fs.fromScheduledSession(ss)
            self.add_to_available_slot(fs)
            self.current_assignments[ss.session.group].append(fs)

            # XXX can not deal with a session in two slots yet?

        #print "Scheduled %u" % (self.total_slots)

        # now need to add entries for those slots which are currently unscheduled.
        for sess,fs in self.sessions.iteritems():
            #print "Considering sess: %s, and loc: %s" % (sess, str(fs.timeslot))
            if fs.timeslot is None:
                self.add_to_available_slot(fs)
        #print "Finished %u" % (self.total_slots)

    def pick_two_slots(self):
        slot1 = self.random_generator.choice(self.available_slots)
        slot2 = self.random_generator.choice(self.available_slots)
        tries = 100
        self.repicking = 0
        # 1) no point in picking two slots which are the same.
        # 2) no point in picking two slots which have no session (already empty)
        # 3) no point in picking two slots which are both unscheduled sessions
        # 4) limit outselves to ten tries.
        while (slot1 == slot2 or
               (slot1.session is None and slot2.session is None) or
               (slot1.timeslot is None and slot2.timeslot is None)
               ) and tries > 0:
            self.repicking = self.repicking + 1
            #print "%u: .. repicking slots, had: %s and %s" % (self.stepnum, slot1, slot2)
            slot1 = self.random_generator.choice(self.available_slots)
            slot2 = self.random_generator.choice(self.available_slots)
            tries = tries - 1
        if tries == 0:
            raise PlacementException("How can it pick the same slot ten times in a row")
        return slot1, slot2

    # this assigns a session to a particular slot.
    def assign_session(self, session, fslot, doubleup=False):
        import copy
        if session is None:
            return
        if not session in self.sessions:
            raise PlacementException("Is there a legit case where session is not in sessions here?")

        oldfs = self.sessions[session]
        # find the group mapping.
        pairs = copy.copy(self.current_assignments[session.group])
        #print "pairs is: %s" % (pairs)
        if oldfs in pairs:
            which = pairs.index(oldfs)
            pairs[which:which] = []
            #print "new pairs is: %s" % (pairs)

        self.sessions[session] = fslot
        # now fix up the other things.
        pairs.append(fslot)
        self.tempdict[session.group] = pairs

    def commit_tempdict(self):
        for key,value in self.tempdict.iteritems():
            self.current_assignments[key] = value
        self.tempdict = dict()

    def try_swap(self):
        badness     = self.badness
        slot1,slot2 = self.pick_two_slots()
        #print "start\n slot1: %s.\n slot2: %s.\n badness: %s" % (slot1, slot2,badness)
        tmp = slot1.session
        slot1.session = slot2.session
        slot2.session = tmp
        self.assign_session(slot1.session, slot1, False)
        self.assign_session(slot2.session, slot2, False)
        self.slot1 = slot1
        self.slot2 = slot2
        # self can substitute for current_assignments thanks to getitem() above.
        newbadness  = self.schedule.calc_badness1(self)
        #print "end\n slot1: %s.\n slot2: %s.\n badness: %s" % (slot1, slot2, newbadness)
        return newbadness

    def do_step(self):
        self.stepnum = self.stepnum + 1
        newbadness = self.try_swap()
        if self.badness is None:
            self.commit_tempdict
            self.badness = newbadness
            return True, 0

        change = newbadness - self.badness
        prob   = self.calc_probability(change)
        dice   = self.random_generator.random()
        if dice < prob:
            accepted_str = "accepted"
            accepted = True
            self.commit_tempdict
            self.badness = newbadness
            # save state object
        else:
            accepted_str = "rejected"
            accepted = False
            self.tempdict = dict()
        acronym1 = "none"
        if self.slot1.session is not None:
            acronym1 = self.slot1.session.group.acronym
        place1   = "none"
        if self.slot1.timeslot is not None:
            place1 = str(self.slot1.timeslot.location)

        acronym2= "none"
        if self.slot2.session is not None:
            acronym2 = self.slot2.session.group.acronym
        place2   = "none"
        if self.slot2.timeslot is not None:
            place2 = str(self.slot2.timeslot.location)
        from models import constraint_cache_uses,constraint_cache_initials
        print "%u: %s delta=%7d move dice=%.2f <=> prob=%.2f (repicking=%u)  %s => %s, %s => %s %u/%u" % (self.stepnum,
            accepted_str,
            change, dice, prob,
            self.repicking, acronym1, place1, acronym2, place2, constraint_cache_uses,constraint_cache_initials)
        # consider changing temperature.
        return accepted, change

    def calc_probability(self, change):
        import math
        return 1/(1 + math.exp(change/self.temperature))

    def do_steps(self):
        accepted, change = self.do_step()
        while  self.temperature > 0:
            accepted,change = self.do_step()
            if accepted and self.recordsteps:
                ass1 = AutomaticScheduleStep()
                ass1.schedule = self.schedule
                if self.slot1.session is not None:
                    ass1.session  = self.slot1.session
                if self.slot1.origss is not None:
                    ass1.moved_to = self.slot1.origss
                ass1.stepnum  = self.stepnum
                ass1.save()
                ass2 = AutomaticScheduleStep()
                ass2.schedule = self.schedule
                if self.slot2.session is not None:
                    ass2.session  = self.slot2.session
                if self.slot2.origss is not None:
                    ass2.moved_to = self.slot2.origss
                ass2.stepnum  = self.stepnum
                ass2.save()
            #print "%u: accepted: %s change %d temp: %d" % (self.stepnum, accepted, change, self.temperature)
        print "Finished after %u steps, badness = %u" % (self.stepnum, self.badness)


class AutomaticScheduleStep(models.Model):
    schedule   = models.ForeignKey('Schedule', null=False, blank=False, help_text=u"Who made this agenda")
    session    = models.ForeignKey('Session', null=True, default=None, help_text=u"Scheduled session involved")
    moved_from = models.ForeignKey('ScheduledSession', related_name="+", null=True, default=None, help_text=u"Where session was")
    moved_to   = models.ForeignKey('ScheduledSession', related_name="+", null=True, default=None, help_text=u"Where session went")
    stepnum    = models.IntegerField(default=0, blank=True, null=True)

