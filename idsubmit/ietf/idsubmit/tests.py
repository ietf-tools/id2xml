from django.test import TestCase, Client
from django.template.loader import render_to_string
from models import IdDates, SubmissionEnv, IdSubmissionDetail
from ietf.idtracker.models import InternetDraft
from ietf.utils import mail
import datetime
import tempfile

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
	s.cut_off_warn_days = 7
	s.save()

    def testTotalCutoff(self):
	self.setUpDates( 7 )
	r = self.c.get('/idsubmit/upload/')
	self.assertEqual( r.template[0].name , 'idsubmit/error.html' )
	self.assertEqual( r.context[0]['date_check_err_msg'] , 'second_ietf' )
	self.setUpDates( 7, before=True )
	r = self.c.get('/idsubmit/upload/')
	self.assertEqual( r.template[0].name , 'idsubmit/upload.html' )
	self.assertEqual( r.context[0]['cutoff_msg'] , 'second_ietf' )
	self.setUpDates( 8, before=True )
	r = self.c.get('/idsubmit/upload/')
	self.assertEqual( r.template[0].name , 'idsubmit/upload.html' )
	self.assertEqual( r.context[0]['cutoff_msg'] , 'first_second' )
	self.setUpDates( 1 )
	r = self.c.get('/idsubmit/upload/')
	self.assertEqual( r.template[0].name , 'idsubmit/error.html' )
	self.assertEqual( r.context[0]['date_check_err_msg'] , 'second_ietf' )
	self.setUpDates( 0 )
	r = self.c.get('/idsubmit/upload/')
	self.assertEqual( r.template[0].name , 'idsubmit/upload.html' )
	self.assert_( not r.context[0].has_key('cutoff_msg') )

    def test00Cutoff( self ):
	self.setUpDates( 22 )
	r = self.c.get('/idsubmit/upload/')
	self.assertEqual( r.template[0].name , 'idsubmit/upload.html' )
	assert not r.context[0].has_key( 'cutoff_msg' )
	self.setUpDates( 21 )
	r = self.c.get('/idsubmit/upload/')
	self.assertEqual( r.template[0].name , 'idsubmit/upload.html' )
	self.assertEqual( r.context[0]['cutoff_msg'] , 'first_warning' )
	self.setUpDates( 14, before=True )
	r = self.c.get('/idsubmit/upload/')
	self.assertEqual( r.template[0].name , 'idsubmit/upload.html' )
	self.assertEqual( r.context[0]['cutoff_msg'] , 'first_warning' )
	self.setUpDates( 14 )
	r = self.c.get('/idsubmit/upload/')
	self.assertEqual( r.template[0].name , 'idsubmit/upload.html' )
	self.assertEqual( r.context[0]['cutoff_msg'] , 'first_second' )

def submit_upload( file, xmlFile=None, pdfFile=None, psFile=None, client=None ):
    if client is None:
        client = Client()
    upload_args = { 'txt_file': file }
    if xmlFile is not None:
        upload_args['xml_file'] = xmlFile
    if pdfFile is not None:
        upload_args['pdf_file'] = pdfFile
    if psFile is not None:
        upload_args['ps_file'] = psFile
    r = client.post('/idsubmit/upload/', upload_args)
    file.close()
    if xmlFile is not None:
        xmlFile.close()
    if pdfFile is not None:
        pdfFile.close()
    if psFile is not None:
        psFile.close()
    return r

def submit_auto_post( submission_id, first_name, last_name, email_address, client=None ):
    if client is None:
        client = Client()
    url = '/idsubmit/auto_post/%d/' % submission_id
    form = { 'fname': first_name,
             'lname': last_name,
             'submitter_email': email_address }
    return client.post( url, form )

def submit_verification( submission_id, auth_key, client=None ):
    if client is None:
        client = Client()
    url = '/idsubmit/verify/%d/%s/' % ( submission_id, auth_key )
    return client.get( url )

def render_to_tempfile( template, context ):
    '''Render a template to a temporary file, and return a file object pointing
    to the beginning of the file.  The temporary file will be deleted automatically
    (see tempfile.TemporaryFile) and does not have a directory entry on the
    filesystem.'''
    f = tempfile.TemporaryFile()
    f.write( render_to_string( template, context ) )
    f.seek( 0 )
    return f

class IndividualTestCase(TestCase):
    fixtures = [ 'test_infrastructure', 'testsubmit', 'wgtest' ]

    def setUp(self):
	self.c = Client()

    def testIndividualSubmission(self):
        txt = render_to_tempfile( "idsubmit/test/idst-test-individual.txt", {} )
        # dunno what CWD is, otherwise
        # xml = open( "test/idst-test-individual.xml" )
        r = submit_upload( txt, client=self.c )
        #print [t.name for t in r.template]
        #print r
        # assert that the right template was used
	self.assertEqual( r.template[0].name , 'idsubmit/validate.html' )
        # assert that the auto_post form is there
        self.failUnless( 'action="/idsubmit/auto_post/' in str(r) )
        # check that the note about metadata
        # is not present
        self.failIf( 'idsubmit/sec_note.html' in [ t.name for t in r.template ] )
        # get the IDSubmissionDetail, assert that the author is right
        d = IdSubmissionDetail.objects.get(pk=1)
        self.assertEqual( d.authors.count(), 1)
        a = d.authors.all()[0]
        self.assertEqual( a.first_name, 'Anon' )
        self.assertEqual( a.last_name, 'Mous' )
        self.assertEqual( a.email_address, 'anon@example.com' )

        # 2. Identify submitter, submit to auto_post
        #
	#XXX Move this to ietf.tests.TestCase?
	mail.empty_outbox()
        r = submit_auto_post( d.submission_id, a.first_name, a.last_name, a.email_address, client=self.c )
        # assert that r is a redirect
        self.assertEqual( r.status_code, 302 )
        # assert that the email challenge "went out" and looks correct
        self.failUnless( '/idsubmit/verify/%d/%s/' % ( d.submission_id, d.auth_key ) in str(mail.outbox[0]) )
        #
        # 3. Respond to "emailed" challenge
        r = submit_verification( d.submission_id, d.auth_key )
	# Another redirect
	self.assertEqual( r.status_code, 302 )
	# Make sure that the two email messages
	# at least got rendered
	templates = [ t.name for t in r.template ]
	for t in ( 'idsubmit/i-d_action.txt', 'idsubmit/email_posted_notice.txt' ):
	    self.failUnless( t in templates )
        #
        # Check that the InternetDraft database is updated
	try:
	    id = InternetDraft.objects.get( filename=d.filename )
	except InternetDraft.DoesNotExist:
	    self.fail( msg='no InternetDraft' )
	self.assertEqual( id.authors.count(), 1 )
	self.assertEqual( str( id.authors.all()[0].person ), 'Anon Mous' )
        # Check that the new I-D email goes out

        # variation: 2. pick an invalid submitter, check that auto_post
        # returns an error.


# Tests to write:
# Submit a 1-page document
# Submit a gzip file
# Submit various types of abstract formatting
# Submit a successful document all the way through
# * Individual
# * WG without -00 approval
# * WG with -00 approval
# * Document with idinternal record but no discusses
# * Document with discusses
# -00 preapproval tool tests:
# * Preapproving before submission
# * Approving an in-progress submission
# * Approving as a user that doesn't have permission
