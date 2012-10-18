<!--  *****  Get Authors for the New Draft  ******  -->
	<CFQUERY NAME="GetAuthors" DATASOURCE="Production">
	    SELECT first_name, last_name, author_order
		  FROM id_authors, person_or_org_info
		 WHERE id_authors.id_document_tag = '#SelectIDTag.id_document_tag#'
		   AND id_authors.person_or_org_tag = person_or_org_info.person_or_org_tag

		<!---  ***** 5/2/2000 ***** --->
           ORDER BY author_order
		<!---  *******************  --->

	</CFQUERY>

	<CFSET #Authors# = "">
	<CFSET #ANDtext# = " ">

	<CFOUTPUT QUERY="GetAuthors">
		<CFIF #first_name# is not ""><CFSET #period# = "."><CFELSE><CFSET #period# = ""></CFIF>
		<CFSET #Authors# = "#Authors##ANDtext# #LEFT("#first_name#", 1)##period# #TRIM(last_name)#">
		<CFSET #ANDtext# =",">
	</CFOUTPUT>

<!---  ****  If the ID belongs to a group other than "none" display following message in the email  ****  --->
	<CFIF #TRIM(SelectGroupInfoforEmail.acronym)# is not "none">
		<CFSET #wgMail# = "This draft is a work item of the #TRIM(SelectGroupInfoforEmail.name)# Working Group of the IETF.">
	<CFELSE>
		<CFSET #wgMail# = "">
	</CFIF>


<!--  *****  Select Message Information  ******  -->
	<CFQUERY NAME="GetMessageInfo" DATASOURCE="Production">
	    SELECT *
		    FROM messages
		    WHERE message_name = 'I-D Announcement'
	</CFQUERY>

	
<CFIF #ParameterExists(DoesntExist)# is "Yes">
<!---  ****  Insert carriage returns into the abstract  ****  --->	
	<CFSET #CarriageReturn# = "
">

	<CFLOOP INDEX="LoopCount" FROM="72" TO="#LEN(abstract)#" STEP="72">
		<CFSET #abstract# = "#Insert(CarriageReturn, abstract, LoopCount)#">
	</CFLOOP>
</CFIF>
<cfset abstract3 = replace(#abstract#,'^','"',"all")>
<cfset id_document_name3 = replace(#id_document_name#,'^','"',"all")>

<!---  ****  Setup the email_address variable - must be formatted this way to appear correctly in the file  ****  --->
    <CFSET #email_address# = "">
	<CFSET #cc_address# = "">
	<CFIF #TRIM(SelectGroupInfoForEmail.email_address)# is not "">
		<CFSET #email_address# = "
Cc: #TRIM(SelectGroupInfoForEmail.email_address)#">
        <CFSET #cc_address# = "#TRIM(SelectGroupInfoForEmail.email_address)#">
	</CFIF>
	
<CFSET #message_body# = "--NextPart

A New Internet-Draft is available from the on-line Internet-Drafts 
directories.
#wgMail#

	Title		: #id_document_name3#
	Author(s)	: #TRIM(Authors)#
	Filename	: #filename#-#revision_number##file_type#
	Pages		: #txt_page_count#
	Date		: #MyDateFormat(revision_date)#
	
#abstract3#

A URL for this Internet-Draft is:
http://www.ietf.org/internet-drafts/#filename#-#revision_number#.txt

To remove yourself from the I-D Announcement list, send a message to 
i-d-announce-request@ietf.org with the word unsubscribe in the body of 
the message. 
You can also visit https://www1.ietf.org/mailman/listinfo/I-D-announce 
to change your subscription settings.

Internet-Drafts are also available by anonymous FTP. Login with the 
username ""anonymous"" and a password of your e-mail address. After 
logging in, type ""cd internet-drafts"" and then 
""get #filename#-#revision_number#.txt"".

A list of Internet-Drafts directories can be found in
http://www.ietf.org/shadow.html 
or ftp://ftp.ietf.org/ietf/1shadow-sites.txt

Internet-Drafts can also be obtained by e-mail.

Send a message to:
	mailserv@ietf.org.
In the body type:
	""FILE /internet-drafts/#filename#-#revision_number#.txt"".
	
NOTE:	The mail server at ietf.org can return the document in
	MIME-encoded form by using the ""mpack"" utility.  To use this
	feature, insert the command ""ENCODING mime"" before the ""FILE""
	command.  To decode the response(s), you will need ""munpack"" or
	a MIME-compliant mail reader.  Different MIME-compliant mail readers
	exhibit different behavior, especially when dealing with
	""multipart"" MIME messages (i.e. documents which have been split
	up into multiple messages), so check your local documentation on
	how to manipulate these messages.

Below is the data which will enable a MIME compliant mail reader
implementation to automatically retrieve the ASCII version of the
Internet-Draft.

--NextPart
Content-Type: Multipart/Alternative; Boundary=""OtherAccess""

--OtherAccess
Content-Type: Message/External-body;
	access-type=""mail-server"";
	server=""mailserv@ietf.org""

Content-Type: text/plain
Content-ID:	<#MyDateFormat(Now(), 'yyyyMMdd')##TimeFormat(Now(), 'HHmmss')#.I-D@ietf.org>

ENCODING mime
FILE /internet-drafts/#filename#-#revision_number#.txt

--OtherAccess
Content-Type: Message/External-body;
	name=""#filename#-#revision_number#.txt"";
	site=""ftp.ietf.org"";
	access-type=""anon-ftp"";
	directory=""internet-drafts""

Content-Type: text/plain
Content-ID:	<#MyDateFormat(Now(), 'yyyyMMdd')##TimeFormat(Now(), 'HHmmss')#.I-D@ietf.org>

--OtherAccess--

--NextPart--
">

  <CFQUERY name="AddScheduledAnnouncements_ID" datasource="Production">
		insert into scheduled_announcements (scheduled_by,scheduled_date,scheduled_time,subject,to_val,cc_val,from_val,body,first_q,content_type)
		values ('IETFDEV',current_date,current_time,'I-D ACTION:#filename#-#revision_number#.txt','i-d-announce@ietf.org','#cc_address#','Internet-Drafts@ietf.org','#message_body#',1,'Multipart/Mixed; Boundary="NextPart"')
  </cfquery>
  
