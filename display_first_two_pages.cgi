#!/usr/bin/perl -w

#############################################################################
#      Program: display_idnit.cgi
#
#      Author : Shailendra Singh Rathore
#
#      Last Modified Date: 2/14/2007
#
#      This application displays the ouptput given by Henrik's tool(IDNIT message)
#############################################################################

use lib '/a/www/ietf-datatracker/release/';
use CGI(':standard');
use DBI;
use GEN_UTIL;
use GEN_DBUTIL_NEW;
use CGI_UTIL;
use IETF;

$script_loc=$ENV{SCRIPT_NAME};
$http_host=$ENV{HTTP_HOST};
$devel_mode = ($script_loc =~ /devel/)?1:0;
$qa_mode = 0;
$dbname = "ietf";
$query = new CGI;

if ($devel_mode) 
{
	$qa_mode = ($http_host =~ /datatracker/)?1:0;
	$rUser = $ENV{REMOTE_USER};
	$dbname=($qa_mode)?"ietf_qa":"test_idst";
	$title_text = ($qa_mode)?"QA Mode":"Development Mode";
}
#Connecting to the database

init_database($dbname);
$dbh = get_dbh();

$sub_id=$query->param("submission_id");
error_idst ($query,"Possible SQL injection detected.") if check_sql_injection ($sub_id);
my $count=db_select($dbh,"select count(submission_id) from id_submission_detail where submission_id=$sub_id");
if (!$sub_id or !$count) #If submission id is not found
{
  error_idst($query,"Invalid Submission ID.<br>");
  exit;
}

$first_two_pages = db_select($dbh,"select first_two_pages from id_submission_detail where submission_id='$sub_id'");
$first_two_pages = CGI::escapeHTML($first_two_pages);
print $query->header();
print <<HTML;
<html><!-- InstanceBegin template="Templates/IETF_Main.dwt" codeOutsideHTMLIsLocked="false" -->
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<!-- InstanceBeginEditable name="doctitle" -->
<title>Collect Meta-Data</title>
<!-- InstanceEndEditable -->
<!-- InstanceBeginEditable name="head" -->
<!-- InstanceEndEditable -->
</head>
<body>
				<!-- Body content starts-->
	 			<div align="left">
	 				<center>
	 					<table border="0" width="657" vspace="0">
	 						<tr valign="top">
								<td height="550" width="651">
   								  <!-- InstanceBeginEditable name="Body text" -->
									<form>
										<table border="0">
											<tr>
												<td><pre>$first_two_pages</pre></td>
											</tr>
											<tr>
												<td>
												</td>
											</tr>
										</table>
									</form>
									<!-- InstanceEndEditable -->							
								</td>
	 						</tr>
					  </table>
					</center>
				</div>
				<!-- Body content ends-->
				
</body>
<!-- InstanceEnd --></html>
HTML
$dbh->disconnect();
