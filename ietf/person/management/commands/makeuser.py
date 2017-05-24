"""
Create a user with a password
"""
import os
from django.contrib.auth.models import User
from ietf.person.models import Person
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

class Command(BaseCommand):
    help = 'Create a user with a password'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('password')

        # Named (optional) arguments
        parser.add_argument(
            '--superuser',
            action='store_true',
            dest='superuser',
            default=False,
            help='Specify if this is a superuser',
        )        
        
    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        superuser = None
        if options['superuser']:
            superuser = options['superuser']

        with transaction.atomic():
            user = User(username=str(username))
            user.set_password(str(password))
            if superuser:
                user.is_superuser = True
                user.is_staff = True

            user.save()
            p = Person(user=user,name=user.username)
            p.save()
