from django.test import TestCase
from models import FromBodies

class GeneralTest(TestCase):

    def test_home(self):
        response = self.client.get('/',REMOTE_USER='rcross')
        self.failUnlessEqual(response.status_code, 200)

class LiaisonTest(TestCase):
    fixtures = [ 'from_bodies.json',
                 'iesglogin.json',
                 'PersonOrOrgInfo.json' ]

    def test_url(self):
        response = self.client.get('/liaison/',REMOTE_USER='rcross')
        self.failUnlessEqual(response.status_code, 200)

    def test_post_valid(self):
        "POST good data to view"
        post_data = { 'name' : 'Test Name' }
        response = self.client.post('/liaison/', post_data, follow=True,REMOTE_USER='rcross')
        self.assertRedirects(response, '/liaison/')
        self.assertContains(response, 'added successfully')

    def test_post_invalid(self):
        post_data = { 'name' : 'Bad$@Name' }
        response = self.client.post('/liaison/', post_data,REMOTE_USER='rcross')
        self.failUnlessEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'name', 'Enter a valid name.')

    def test_post_dupe(self):
        post_data = { 'name' : '3GPP' }
        response = self.client.post('/liaison/', post_data,REMOTE_USER='rcross')
        self.failUnlessEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'name', 'This name already exists!')
