# Copyright The IETF Trust 2020, All Rights Reserved
# -*- coding: utf-8 -*-
import copy

from ietf.group.factories import GroupFactory
from ietf.group.models import Group
from ietf.meeting.factories import SessionFactory, MeetingFactory
from ietf.meeting.helpers import (tag_assignments_with_filter_keywords, AgendaFilterOrganizer,
                                  filter_keywords_for_session)
from ietf.meeting.test_data import make_meeting_test_data
from ietf.utils.test_utils import TestCase


class HelpersTests(TestCase):
    def do_test_tag_assignments_with_filter_keywords(self, bof=False, historic=None):
        """Assignments should be tagged properly
        
        The historic param can be None, group, or parent, to specify whether to test
        with no historic_group, a historic_group but no historic_parent, or both.
        """
        meeting_types = ['regular', 'plenary']
        group_state_id = 'bof' if bof else 'active'
        group = GroupFactory(state_id=group_state_id)
        historic_group = GroupFactory(state_id=group_state_id)
        historic_parent = GroupFactory(type_id='area')

        if historic == 'parent':
            historic_group.historic_parent = historic_parent

        # Create meeting and sessions
        meeting = MeetingFactory()
        for meeting_type in meeting_types:
            sess = SessionFactory(group=group, meeting=meeting, type_id=meeting_type)
            ts = sess.timeslotassignments.first().timeslot
            ts.type = sess.type
            ts.save()

        # Create an office hours session in the group's area (i.e., parent). This is not
        # currently really needed, but will protect against areas and groups diverging
        # in a way that breaks keywording.
        office_hours = SessionFactory(
            name='some office hours',
            group=group.parent,
            meeting=meeting,
            type_id='other'
        )
        ts = office_hours.timeslotassignments.first().timeslot
        ts.type = office_hours.type
        ts.save()

        assignments = meeting.schedule.assignments.all()
        orig_num_assignments = len(assignments)

        # Set up historic groups if needed
        if historic:
            for a in assignments:
                if a.session != office_hours:
                    a.session.historic_group = historic_group

        # Execute the method under test
        tag_assignments_with_filter_keywords(assignments)

        # Assert expected results
        self.assertEqual(len(assignments), orig_num_assignments, 'Should not change number of assignments')

        if historic:
            expected_group = historic_group
            expected_area = historic_parent if historic == 'parent' else historic_group.parent
        else:
            expected_group = group
            expected_area = group.parent

        for assignment in assignments:
            expected_filter_keywords = {assignment.timeslot.type.slug, assignment.session.type.slug}

            if assignment.session == office_hours:
                expected_filter_keywords.update([
                    group.parent.acronym,
                    'officehours',
                    'someofficehours',
                ])
            else:
                expected_filter_keywords.update([
                    expected_group.acronym,
                    expected_area.acronym
                ])
                if bof:
                    expected_filter_keywords.add('bof')
                token = assignment.session.docname_token_only_for_multiple()
                if token is not None:
                    expected_filter_keywords.update([expected_group.acronym + "-" + token])

            self.assertCountEqual(
                assignment.filter_keywords,
                expected_filter_keywords,
                'Assignment has incorrect filter keywords'
            )

    def test_tag_assignments_with_filter_keywords(self):
        self.do_test_tag_assignments_with_filter_keywords()
        self.do_test_tag_assignments_with_filter_keywords(historic='group')
        self.do_test_tag_assignments_with_filter_keywords(historic='parent')
        self.do_test_tag_assignments_with_filter_keywords(bof=True)
        self.do_test_tag_assignments_with_filter_keywords(bof=True, historic='group')
        self.do_test_tag_assignments_with_filter_keywords(bof=True, historic='parent')


class AgendaFilterOrganizerTests(TestCase):
    def test_get_filter_categories(self):
        # set up
        meeting = make_meeting_test_data()

        # create extra groups for testing
        iab = Group.objects.get(acronym='iab')
        iab_child = GroupFactory(type_id='iab', parent=iab)
        irtf = Group.objects.get(acronym='irtf')
        irtf_child = GroupFactory(parent=irtf, state_id='bof')

        # non-area group sessions
        SessionFactory(group=iab_child, meeting=meeting)
        SessionFactory(group=irtf_child, meeting=meeting)
        
        # office hours session
        SessionFactory(
            group=Group.objects.get(acronym='farfut'),
            name='FARFUT office hours',
            meeting=meeting
        )

        expected = [
            [
                # area category
                {'label': 'FARFUT', 'keyword': 'farfut', 'is_bof': False,
                 'children': [
                     {'label': 'ames', 'keyword': 'ames', 'is_bof': False},
                     {'label': 'mars', 'keyword': 'mars', 'is_bof': False},
                 ]},
            ],
            [
                # non-area category
                {'label': 'IAB', 'keyword': 'iab', 'is_bof': False,
                 'children': [
                     {'label': iab_child.acronym, 'keyword': iab_child.acronym, 'is_bof': False},
                 ]},
                {'label': 'IRTF', 'keyword': 'irtf', 'is_bof': False,
                 'children': [
                     {'label': irtf_child.acronym, 'keyword': irtf_child.acronym, 'is_bof': True},
                 ]},
            ],
            [
                # non-group category
                {'label': 'Office Hours', 'keyword': 'officehours', 'is_bof': False,
                 'children': [
                     {'label': 'FARFUT', 'keyword': 'farfutofficehours', 'is_bof': False}
                 ]},
                {'label': None, 'keyword': None,'is_bof': False,
                 'children': [
                     {'label': 'BoF', 'keyword': 'bof', 'is_bof': False},
                     {'label': 'Plenary', 'keyword': 'plenary', 'is_bof': False},
                 ]},
            ],
        ]

        # when using sessions instead of assignments, won't get timeslot-type based filters 
        expected_with_sessions = copy.deepcopy(expected)
        expected_with_sessions[-1].pop(0)  # pops 'office hours' column

        # put all the above together for single-column tests
        expected_single_category = [
            sorted(sum(expected, []), key=lambda col: col['label'] or 'zzzzz')
        ]
        expected_single_category_with_sessions = [
            sorted(sum(expected_with_sessions, []), key=lambda col: col['label'] or 'zzzzz')
        ]

        ###
        # test using sessions
        sessions = meeting.session_set.all()
        for session in sessions:
            session.filter_keywords = filter_keywords_for_session(session)

        # default
        filter_organizer = AgendaFilterOrganizer(sessions=sessions)
        self.assertEqual(filter_organizer.get_filter_categories(), expected_with_sessions)

        # single-column
        filter_organizer = AgendaFilterOrganizer(sessions=sessions, single_category=True)
        self.assertEqual(filter_organizer.get_filter_categories(), expected_single_category_with_sessions)

        ###
        # test again using assignments
        assignments = meeting.schedule.assignments.all()
        tag_assignments_with_filter_keywords(assignments)

        # default
        filter_organizer = AgendaFilterOrganizer(assignments=assignments)
        self.assertEqual(filter_organizer.get_filter_categories(), expected)

        # single-column
        filter_organizer = AgendaFilterOrganizer(assignments=assignments, single_category=True)
        self.assertEqual(filter_organizer.get_filter_categories(), expected_single_category)

    def test_get_non_area_keywords(self):
        # set up
        meeting = make_meeting_test_data()

        # create a session in a 'special' group, which should then appear in the non-area keywords
        team = GroupFactory(type_id='team')
        SessionFactory(group=team, meeting=meeting)
        
        # and a BoF
        bof = GroupFactory(state_id='bof')
        SessionFactory(group=bof, meeting=meeting)

        expected = sorted(['bof', 'plenary', team.acronym.lower()])

        ###
        # by sessions
        sessions = meeting.session_set.all()
        for session in sessions:
            session.filter_keywords = filter_keywords_for_session(session)
        filter_organizer = AgendaFilterOrganizer(sessions=sessions)
        self.assertEqual(filter_organizer.get_non_area_keywords(), expected)

        filter_organizer = AgendaFilterOrganizer(sessions=sessions, single_category=True)
        self.assertEqual(filter_organizer.get_non_area_keywords(), expected)

        ###
        # by assignments
        assignments = meeting.schedule.assignments.all()
        tag_assignments_with_filter_keywords(assignments)
        filter_organizer = AgendaFilterOrganizer(assignments=assignments)
        self.assertEqual(filter_organizer.get_non_area_keywords(), expected)

        filter_organizer = AgendaFilterOrganizer(assignments=assignments, single_category=True)
        self.assertEqual(filter_organizer.get_non_area_keywords(), expected)