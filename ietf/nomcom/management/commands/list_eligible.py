# Copyright The IETF Trust 2017-2020, All Rights Reserved
# -*- coding: utf-8 -*-

import debug                            # pyflakes:ignore

import datetime
import sys

python_ver = sys.version_info
if python_ver.major == 3 and python_ver.minor < 7:
    # if you need this, pip install backports-datetime-fromisoformat
    from backports.datetime_fromisoformat import MonkeyPatch
    MonkeyPatch.patch_fromisoformat()

from django.core.management.base import BaseCommand
from django.db.models import Q, Count

from ietf.nomcom.utils import three_of_five_eligible, iab_iesg, actual_volunteers, DISQUALIFYING_ROLE_QUERY_EXPRESSION
from ietf.meeting.models import Meeting
from ietf.person.models import Person
from ietf.group.models import Role


class Command(BaseCommand):
    help = ("List nomcom eligible people using various eligibility criterea.")

    def add_arguments(self, parser):
        today = datetime.date.today()
        five_years_ago = datetime.date(today.year-5, today.month, today.day)
        three_years_ago = datetime.date(today.year-3, today.month, today.day)
        parser.add_argument('--date', dest='date', type=datetime.date.fromisoformat, action='store', help='Check eligibility as of this date')
        parser.add_argument('--summary', dest='summary', action='store_true', help='Show only summary results. Do not enumerate lists.')
        parser.add_argument('--previous_five', dest='previous_five', nargs='+', type=int, help='IETF meeting numbers to use as the previous five meetings. Ignores --date.')
        parser.add_argument('--officer_date', dest='officer_date', type=datetime.date.fromisoformat, default = three_years_ago, help='Has been a group officer after date')
        parser.add_argument('--officer_roles', dest='officer_roles', nargs='+', default=['chair','secr'], help='What roles are consider group officer roles')
        parser.add_argument('--group_types', dest='group_types', nargs='+', default=['wg'], help='What group types are considered for officer roles')
        parser.add_argument('--group_states', dest='group_states', nargs='+', default=['active'], help='What group states are considered for officer roles. Example: "active" "bof"')
        parser.add_argument('--iesg_iab_date', dest='iesg_iab_date', type=datetime.date.fromisoformat, default = five_years_ago, help="Was on the IESG or IAB since date")
        parser.add_argument('--rfc_date', dest='rfc_date', type=datetime.date.fromisoformat, default = five_years_ago, help="Was an author of some IETF stream RFCs since date")
        parser.add_argument('--rfc_count', dest='rfc_count', type=int, default = 2, help="Was an author of at least this many IETF stream rfcs")
        parser.add_argument('--file_out', dest='file_out', default = 'elig', help="Provide the base of a file name for list outputs")
        parser.add_argument('--disqualify', dest='disqualify', action='store_true', help='Disqualify people as per RFC8713 section 4.15')

    def list_report(self, list_name, list_instance, **options):
        print ("%s has %d members" % (list_name, len(list_instance)))
        if not options['summary']:
            forced_list = list(list_instance)
            forced_list.sort(key=lambda p: p.last_name() )
            if not options['file_out']:
                for person in forced_list:
                    print ("    ", person.plain_name())
            else:
                fname=options['file_out']+'.'+list_name
                fp=open(fname,"w")
                for person in forced_list:
                    fp.write (person.plain_name()+"\n")
                fp.close()

    def handle(self, *args, **options):

        date = options['date'] or datetime.date.today()

        if options['previous_five']:
            previous_five = []
            for num in options['previous_five']:
                previous_five.append(Meeting.objects.get(type_id='ietf', number=num))
            print("Using the following as the previous five meetings", previous_five)
        else:
            previous_five = None
            print ("Using the five meetings before", date)


        list1 = three_of_five_eligible(date, previous_five)

        list2 = Person.objects.filter(
                    # is currently an officer
                    Q(role__name_id__in=options['officer_roles'],
                      role__group__state_id__in=options['group_states'],
                      role__group__type_id__in=options['group_types'],
                    ) 
                    # was an officer since the given date (I think this is wrong - it looks at when roles _start_, not when roles end)
                  | Q(rolehistory__group__time__gte=options['officer_date'],
                      rolehistory__name_id__in=options['officer_roles'],
                      rolehistory__group__state_id__in=options['group_states'],
                      rolehistory__group__type_id__in=options['group_types']
                     )
        ).distinct()

                
        list3 = iab_iesg(options['iesg_iab_date'],datetime.date.today())

        list4 = Person.objects.filter(documentauthor__document__stream_id='ietf',documentauthor__document__type_id='draft').filter(
            Q (documentauthor__document__docevent__type='published_rfc', 
               documentauthor__document__docevent__time__gte=options['rfc_date']) | 
            Q (documentauthor__document__docevent__type='iesg_approved',
               documentauthor__document__docevent__time__gte=options['rfc_date'])
        ).annotate(
            document_author_count = Count('documentauthor')
        ).filter(document_author_count__gte=options['rfc_count']).distinct()

        if options['disqualify']:
            disqualified_roles=Role.objects.filter(DISQUALIFYING_ROLE_QUERY_EXPRESSION)
            disqualified_pks=list(set(disqualified_roles.values_list('person__pk',flat=True)))
            list1 = [p for p in list1 if p.pk not in disqualified_pks]
            list2 = list2.exclude(pk__in=disqualified_pks)
            list3 = list3.exclude(pk__in=disqualified_pks)
            list4 = list4.exclude(pk__in=disqualified_pks)

        union234 = set(list2) | set(list3) | set(list4)
        volunteers = actual_volunteers(date.year)
        list1_intersect_volunteers = list(set(list1) & set(volunteers))
        union234_intersect_volunteers = list(set(union234) & set(volunteers))
        list1_intersect_union234 = list(set(list1) & set(union234))
        list1_intersect_union234_intersect_volunteers = list(set(list1) & set(union234) & set(volunteers))

        self.list_report("List1", list1, **options)
        self.list_report("List2", list2, **options)
        self.list_report("List3", list3, **options)
        self.list_report("List4", list4, **options)

        self.list_report("Volunteers in "+str(date.year), volunteers, **options )

        self.list_report("union234 ", union234, **options )

        self.list_report("List1_intersect_union234 ", list1_intersect_union234, **options )
        self.list_report("List1_intersect_volunteers", list1_intersect_volunteers, **options )
        self.list_report("union234_intersect_volunteers", union234_intersect_volunteers, **options )
        self.list_report("List1_intersect_union234_intersect_volunteers", list1_intersect_union234_intersect_volunteers, **options )

