#!/usr/bin/env python
# Copyright The IETF Trust 2010, All Rights Reserved

import unittest
import mail
from django.conf import settings

mail.test_mode = True

class MailDestinationTest(unittest.TestCase):
    def testSendMailText(self):
	mail.empty_outbox()
	mail.send_mail_text(None, [ 'a', 'b' ], None, 'Subject', 'body', cc=[ 'c', 'd' ],
			extra={ 'Extra1': 'Value1', 'Extra2': 'Value2' }, toUser=False,
			bcc='e')
	(result, to, txt) = mail.outbox[ 0 ]
	# add_headers must have added what we needed:
	self.assertNotEquals( result[ 'Message-ID' ], None )
	self.assertNotEquals( result[ 'Date' ], None )
	self.assertEquals( result[ 'From' ], settings.DEFAULT_FROM_EMAIL )
	# The arguments should have come through
	self.assertEquals( result[ 'To' ], 'a, b' )
	self.assertEquals( result[ 'Subject' ], 'Subject' )
	self.assertEquals( result[ 'Cc' ], 'c, d' )
	self.assertEquals( result[ 'Extra1' ], 'Value1' )
	self.assertEquals( result[ 'Extra2' ], 'Value2' )
	self.assertTrue( txt.endswith( 'body' ) )
	# make sure that Bcc worked
	self.assertTrue( 'e' in to )

	# Also test that archiving is done.
	self.assertTrue( len( mail.outbox ) == 2 )
	(archive, to, txt) = mail.outbox[ 1 ]
	self.assertEquals( archive[ 'Subject' ], '[Django development] Subject' )

	mail.empty_outbox()
	# Another test, just testing that a well-formed "From:" makes it through.
	test_from = "The person the email is from <person@email.exmaple.com>"
	mail.send_mail_text(None, [ 'a' ], test_from, 'Subject', 'body')
	(result, to, txt) = mail.outbox[ 0 ]
	self.assertEqual( result[ 'From' ], test_from )

	mail.empty_outbox()
	# This should be the same result due to formataddr
	# Also check the use of formataddr in the To header.
	mail.send_mail_text(None, [ ('a', 'a@a.example.com'), 'b <b@b.example.com>' ], ( 'The person the email is from', 'person@email.exmaple.com' ), 'Subject', 'body', cc=[ 'd@d.example.com', ('e', 'e@e.example.com' ) ])
	(result, to, txt) = mail.outbox[ 0 ]
	self.assertEqual( result[ 'From' ], test_from )
	self.assertEqual( result[ 'To' ], 'a <a@a.example.com>, b <b@b.example.com>' )
	self.assertEqual( result[ 'Cc' ], 'd@d.example.com, e <e@e.example.com>' )
	self.assertEqual( to, [ 'a@a.example.com', 'b@b.example.com', 'd@d.example.com', 'e@e.example.com' ] )

    def testSendMailSubj( self ):
	mail.empty_outbox()
	mail.send_mail_subj( None, 'a@a.example.com', None,
				'test/mail_subject.txt', 'test/mail_body.txt',
				{ 'value': 'one', 'thing': 'two',
				  'unsafe': '<>&'} )
	(result, to, txt) = mail.outbox[ 0 ]
	self.assertEqual( result[ 'Subject' ], 'you can have <>& in your context' )
	# In the test environment, we get base64-encoded ASCII.  In the real environment,
	# we don't seem to.  We'd like to test this.
	#self.assertTrue( 'template one rendered with a good two' in txt )

    def testSendMail( self ):
	mail.empty_outbox()
	mail.send_mail( None, 'a@a.example.com', None, 'Subject', 'test/mail_body.txt',
				{ 'value': 'one', 'thing': 'two' } )
	(result, to, txt) = mail.outbox[ 0 ]
	self.assertEqual( result[ 'Subject' ], 'Subject' )
	# In the test environment, we get base64-encoded ASCII.  In the real environment,
	# we don't seem to.  We'd like to test this.
	#self.assertTrue( 'template one rendered with a good two' in txt )

    def testSendMailPreformatted( self ):
	mail.empty_outbox()
	mail.send_mail_preformatted( None, '''From: me@here.example.com
To: Joe Blow <joe@a.example.com>, fred@b.example.com
Subject: Hello, what do you know?
Cc: d@d.example.com
Bcc: x@x.example.com

body body body''' )
	(result, to, txt) = mail.outbox[ 0 ]
	self.assertEqual( result[ 'From' ], 'me@here.example.com' )
	self.assertEqual( result[ 'To' ], 'Joe Blow <joe@a.example.com>, fred@b.example.com' )
	self.assertEqual( result[ 'Subject' ], 'Hello, what do you know?' )
	self.assertEqual( result[ 'Cc' ], 'd@d.example.com' )
	self.assertTrue( txt.endswith( 'body body body' ) )
	self.assertEqual( set( to ), set( [ 'joe@a.example.com', 'fred@b.example.com', 'd@d.example.com', 'x@x.example.com' ] ) )

if __name__ == '__main__':
    unittest.main()
