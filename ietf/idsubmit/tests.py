from django.test import TestCase, Client
from models import *
import datetime

class CutoffTestCase(TestCase):
    fixtures = [ 'testsubmit' ]

    def setUp(self):
	self.today = datetime.date.today()
	self.c = Client()

    def setUpDates(self, days, before=False):
	# date is the days until (or negative for after) the meeting;
	# we simplify things by making the -00 cutoff 2 weeks
	# before and the full cutoff 1 week before.
	date = self.today + datetime.timedelta( days=days )
	for i in range(1,4):
	    d = IdDates.objects.get(pk=i)
	    d.id_date = date - datetime.timedelta( days=7 * (3-i) )
	    #print '%s: %s' % ( d.date_name, d.id_date )
	    d.save()
	# Also set the time to be before now
	s = SubmissionEnv.objects.get(pk=1)
	if before:
	    delta = 120
	else:
	    delta = -1
	s.cut_off_time = ( datetime.datetime.now() + datetime.timedelta( seconds=delta ) ).time()
	s.save()

    def testTotalCutoff(self):
	self.setUpDates( 7 )
	r = self.c.get('/idsubmit/upload/')
	assert r.template[0].name == 'idsubmit/error.html'
	assert r.context[0]['date_check_err_msg'] == 'second_ietf'
	self.setUpDates( 7, before=True )
	r = self.c.get('/idsubmit/upload/')
	assert r.template[0].name == 'idsubmit/upload.html'
	assert r.context[0]['cutoff_msg'] == 'second_ietf'
	self.setUpDates( 8, before=True )
	r = self.c.get('/idsubmit/upload/')
	assert r.template[0].name == 'idsubmit/upload.html'
	assert r.context[0]['cutoff_msg'] == 'first_second'
	self.setUpDates( 1 )
	r = self.c.get('/idsubmit/upload/')
	assert r.template[0].name == 'idsubmit/error.html'
	assert r.context[0]['date_check_err_msg'] == 'second_ietf'
	self.setUpDates( 0 )
	r = self.c.get('/idsubmit/upload/')
	assert r.template[0].name == 'idsubmit/upload.html'
	assert not r.context[0].has_key('cutoff_msg')






