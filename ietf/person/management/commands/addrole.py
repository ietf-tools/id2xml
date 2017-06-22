"""
Create a user with a password
"""
import os
from django.core.management.base import BaseCommand, CommandError
from ietf.group.models import Role, Group
from ietf.name.models import RoleName
from ietf.person.models import Person, Email
from django.db import transaction

class Command(BaseCommand):
    help = 'Add a user to a Role'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('rolename')
        parser.add_argument('groupacronym')                
        
    def handle(self, *args, **options):
        username = options['username']
        rolename = options['rolename']
        groupacronym = options['groupacronym']

        with transaction.atomic():        
            p = Person.objects.get(user__username=username)
            rn = RoleName(slug=rolename)
            g = Group.objects.get(acronym=groupacronym)
            e = Email.objects.create(address=p.user.email,person=p)
            r = Role.objects.create(group=g,person=p,name=rn,email=e)


