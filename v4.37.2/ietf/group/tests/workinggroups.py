import sys
from django.test import TestCase
from ietf.group.models import Group

class WorkingGroupTestCase(TestCase):
    fixtures = [ 'workinggroups.json']

    def FindOneWg(self):
        one = Group.objects.filter(acronym = 'roll')
        self.assertIsNotNone(one)
        
    def ActiveWgGroupList(self):
        True
        
