# Copyright The IETF Trust 2007, All Rights Reserved

MSG_BODY_SCHEDULED_ANNOUNCEMENT = """New version (-##revision##) has been submitted for ##filename##-##revision##.txt.
http://www.ietf.org/internet-drafts/%(filename)s-%(revision)s.txt
##msg##

IETF Secretariat.
"""

ID_ACTION_ANNOUNCEMENT="""--NextPart

A New Internet-Draft is available from the on-line Internet-Drafts directories.##wgMail##

	Title           : ##id_document_name##
	Author(s)       : ##authors##
	Filename        : ##filename##-##revision##.txt
	Pages           : ##txt_page_count##
	Date            : ##revision_date##

##abstract##

A URL for this Internet-Draft is:
http://www.ietf.org/internet-drafts/##filename##-##revision##.txt

To remove yourself from the I-D Announcement list, send a message to
i-d-announce-request@ietf.org with the word unsubscribe in the body of 
the message.
You can also visit https://www1.ietf.org/mailman/listinfo/I-D-announce
to change your subscription settings.

Internet-Drafts are also available by anonymous FTP. Login with the 
username "anonymous" and a password of your e-mail address. After 
logging in, type "cd internet-drafts" and then
	"get ##filename##-##revision##.txt".

A list of Internet-Drafts directories can be found in
http://www.ietf.org/shadow.html
or ftp://ftp.ietf.org/ietf/1shadow-sites.txt

Internet-Drafts can also be obtained by e-mail.

Send a message to:
	mailserv@ietf.org.
In the body type:
	"FILE /internet-drafts/##filename##-##revision##.txt".

NOTE:   The mail server at ietf.org can return the document in
	MIME-encoded form by using the "mpack" utility.  To use this
	feature, insert the command "ENCODING mime" before the "FILE"
	command.  To decode the response(s), you will need "munpack" or
	a MIME-compliant mail reader.  Different MIME-compliant mail readers
	exhibit different behavior, especially when dealing with
	"multipart" MIME messages (i.e. documents which have been split
	up into multiple messages), so check your local documentation on
	how to manipulate these messages.

Below is the data which will enable a MIME compliant mail reader
implementation to automatically retrieve the ASCII version of the
Internet-Draft.

--NextPart
Content-Type: Multipart/Alternative; Boundary="OtherAccess"

--OtherAccess
Content-Type: Message/External-body;
	access-type="mail-server";
	server="mailserv@ietf.org"

Content-Type: text/plain
Content-ID:     <##current_date####current_time##.I-D@ietf.org>

ENCODING mime
FILE /internet-drafts/##filename##-##revision##.txt

--OtherAccess
Content-Type: Message/External-body;
	name="##filename##-##revision##.txt";
	site="ftp.ietf.org";
	access-type="anon-ftp";
	directory="internet-drafts"

Content-Type: text/plain
Content-ID:     <##current_date####current_time##.I-D\@ietf.org>

--OtherAccess--

--NextPart--
"""
