#!/usr/bin/perl -w

#############################################################################
#      Program: validate.cgi
#
#      Author : Shailendra Singh Rathore
#
#      Last Modified Date: 2/15/2007
#
#      This application extracts the metadata from the uploaded Internet Draft 
#      and displays it on the HTML page
#############################################################################

use lib '/a/www/ietf-datatracker/release/';
use CGI(':standard');
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
$tr_bgcolor="#ddddff";
$rev_color=$tr_bgcolor;
$wg_color=$tr_bgcolor;
$nop_color=$tr_bgcolor;
$abstract_color=$tr_bgcolor;
$title_color=$tr_bgcolor;
$creation_date_color=$tr_bgcolor;
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
                                                                                     


$flag = 0;
$index = 0;
$k = 0;
$terminator = 0;
$error_color="#ffaaaa";
#Check if any parameter is being sent through a query string

if (length ($ENV{'QUERY_STRING'}) > 0)
{
	$buffer = $ENV{'QUERY_STRING'};
	@pairs = split(/&/, $buffer);
	foreach $pair (@pairs)
	{
		($name, $value) = split(/=/, $pair);
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
		$in{$name} = $value;
	}
}

$sub_id = $in{'submission_id'};
error_idst ($query,"Possible SQL Injection detected.") if check_sql_injection ($sub_id);
#$error_flag = $in{'error_flag'};

#Cancle button for the development mode

#$cancel_button = ($devel_mode)?qq{<form action="status.cgi" method="get">
$cancel_button = qq{<form action="status.cgi" method="get" name="aform">
<input type="hidden" name="submission_id" value="$sub_id">
<input type="hidden" name="cancel" value="1">
<input type="hidden" name="redirect" value="1">
Cancel this submission: <input type="submit" value="Cancel" onClick="return window.confirm('Do you really want to cancel this submission?');">
</form> 
};

#If submission id is not found
if (!$sub_id)
{
	error_idst ($query,"Unknown Request");
	exit;
}

$sql = "select status_id from id_submission_detail where submission_id=$sub_id";
$status_id = db_select($dbh,$sql);


#date as per the MYSQL date format

$current_date = get_current_date(1);
@dt = split(/\//,$current_date);
$last_updated_date = join '/',($dt[2],$dt[0],$dt[1]);

$current_time = get_current_time();
$status_id = 6;
$parse_error=0;


$sql = "select staging_path,staging_url from id_submission_env";
@results = db_select($dbh,$sql);
$stg_path = $results[0];
$stg_url  = $results[1];
$sql = "select filename,id_document_name,revision,submission_date,warning_message,group_acronym_id,filesize,file_type,invalid_version,idnits_failed from id_submission_detail where submission_id = '$sub_id'";
@result = db_select($dbh,$sql);
$filename = $result[0];
#$id_document_name = $result[1];
$revision = $result[2];
$submission_date = $result[3];
$warning_message=$result[4];
$group_acronym_id=$result[5];
$group_acronym=($group_acronym_id==1027)?"Individual Submission":db_select($dbh,"select acronym from acronym where acronym_id=$group_acronym_id");
unless ($group_acronym_id) {
  $wg_color=$error_color;
  $group_acronym="";
  $parse_error=1;
}

$filesize=$result[6];
$file_type=$result[7];
$file_type=~s/\.txt//;
$file_type=~s/^,//;
my @temp=split ',',$file_type;
$other_format_docs="";
for my $file_ext (@temp) {
  $other_format_docs .= " &nbsp; &nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href=\"$stg_url/$filename-$revision$file_ext\">$filename-$revision$file_ext</a><br>\n";
}
$invalid_version=$result[8];
$idnits_failed=$result[9];
$draft = $stg_path."$filename-$revision.txt";
open (FH , "$draft") || error_idst ($query, "Can't open $draft<br>\nPlease go back to <a href=\"upload.cgi\">Upload Page</a> and re-submit your draft.<br>\n");

@id_text = <FH>;

for ($i= 0; $i <= $#id_text; $i++)
{
	#Counting the initial blanks
	if ($id_text[$i] =~ /^\s+status of this \w+/i)
	{
		$space_flag = 1;
		$pr_length = length($id_text[$i]);
		$id_text[$i] =~ s/^\s+//g;
		$cr_length = length($id_text[$i]);
		$no_of_spaces = $pr_length - $cr_length;
	}
	if ($space_flag ==1 )
	{
		$id_text[$i] =~ s/^\s{$no_of_spaces}//g;
	}

	################Extracting "PAGE NUMBER" from the Internet Draft###########
        if ($id_text[$i] =~ /\[Page\s+([0-9]+)\]/)
        {
                $nop = $1;
        }
	############Extracting "AUTHOR INFO" from the Internet Draft###############
        $author_button="";
	if ( $id_text[$i] =~ /(Author|\d. Editor)[']?[s]?[']?\s*Address[es]*[:]*\s*$/i .. $id_text[$i] =~/ooOOooOOoo/ ) 
	{
		next if ($id_text[$i] =~ /(Author|\d. Editor)[']?[s]?[']?\s*Address[es]*\s*$/i);
                $id_text[$i] =~ s/ \w\. / /;
                $id_text[$i] =~ s/,.+//;
                $id_text[$i] =~ s/ [a-zA-z] / /;
                $id_text[$i] =~ s/\(.*\)//;
                $id_text[$i] =~ s/([a-zA-Z]+) ([a-zA-Z]+) ([a-zA-Z]+)/$1 $3/;
		if ($id_text[$i] =~ /^\s*([a-z]+|[a-z]+-[a-z]+)\s+([Le ]*[a-z]+|[a-z]+-[a-z]+)\s(\(.+)*$/i .. $id_text[$i] =~/[\w.-]+\@.*/)
		{
			if ( defined ( $1 && $2 ) and !my_defined($fname)  )
			{
				$fname = $1;
				$lname = $2;
			}
			if ($id_text[$i] =~ /(\S+\@\S+)/ and $id_text[$i] !~ /ietf-ipr/ )
			{
                                my $email=$1;
                                $email =~ s/mailto://;
				$authors[$k+2] = $email;
                                my $author_id = db_select_secure($dbh,"select person_or_org_tag from email_addresses where email_address=?",$email);
                                if ($author_id) {
                                    ($fname,$lname)=db_select($dbh,"select first_name,last_name from person_or_org_info where person_or_org_tag=$author_id");
                                }
                                $authors[$k] = $fname;
                                $authors[$k+1] = $lname;
				$k = $k +3;
                                $fname = "";
                                $lname = "";
			}
		}
	}
}
if ($revision > 99 or !my_defined($revision)) {
  $parse_error=1;
  $revision="";
  $rev_color=$error_color;
}

# Re-extracting Creation Date - Michael Lee
$_ = `head -30 $draft`;
s/rfc \d\d\d\d//i;
s/rfc\d\d\d\d//i;
s/expires:\s*\d*\s*[A-Za-z]+\s*\d*[,]?\s*[1920]+\d\d//i;
s/expiration date:\s*\d*\s*[A-Za-z]+\s*\d*[,]?\s*[1920]+\d\d//i;
/\s*(\d*\s{0,1}[A-Za-z]+\s*\d*[,]?\s+[1920]+\d\d)/;
$creation_date = $1;
# Re-extracting Abstract - Michael Lee

$_ = `cat $draft`;
s/\r//g;
s/\f//g;

## Parsing First Two Pages and Title ##

$draft_text = $_;
s/\[Page/\[page/g;
my @temp_draft=split "page 2";
$first_two_pages=$temp_draft[0];
$first_two_pages.= "page 2]";
$first_two_pages_q=$first_two_pages;
$draft_text = $_;
s/\[Page/\[page/g;
@temp_draft=split "page 5";
$first_five_pages=$temp_draft[0];
unless (my_defined($id_document_name)) {
  $_=$first_two_pages;
  s/\r//g;
  /(\s*\n\s*\n)((.+\n){1,3})(\s+<?draft-\S+\s*\n)/;
  $id_document_name=$2;
  $id_document_name =~ s/\s{2,}/ /g;

}

#Use cases for unusual title extract
unless (my_defined($id_document_name)) {
  $_ = $first_two_pages;
  s/\r//g;
  /(\s*\n\s*\n)(.+\n|.+\n.+\n)(\s*status of this memo\s*\n)/i;
  $id_document_name=$2;
  $id_document_name =~ s/\s{2,}/ /g;
}

## End Use cases ##

unless (my_defined($id_document_name)) {
  $id_document_name="";
  $parse_error=1;
  $title_color=$error_color;
}

$_ = $first_five_pages;
## Removing page separators ##
s/\n+.*\[Page \d{1,3}\]\n{1,4}internet(-| )draft.*\d\d\d\d\n{1,}//gi; 
s/\n+.*\[Page \d{1,3}\]\s*\n{1,4}internet(-| )draft.*\d\d\d\d\s*\n{1,}//gi;
s/\n.*\[Page i{1,3}\]\n{1,4}internet(-| )draft.*\d\d\d\d\n{1,}//gi; 
#s/\n+.+\[page \d+\].*\n//gi;
$draft_text = $_;
$abstract = $draft_text;
/(Abstract\s*\n+)([\s|\S]+)(table of contents)/i;
$abstract = $2;
unless (my_defined($abstract))
{
        $_ = $draft_text;
        /(Abstract\s*\n+)([.|\s|\S]+)(\s*Status of this Memo)/i;
        $abstract = $2;
}

unless (my_defined($abstract))
{
        $_ = $draft_text;
        /(Abstract\s*\n+)([\s|\S]+)(\s*Conventions Used in this Document)/i;
        $abstract = $2;
}

unless (my_defined($abstract))
{
        $_ = $draft_text;
        /(Abstract\s*\n+)([\s|\S]+)(\s*Editorial Note)/i;
        $abstract = $2;
}

unless (my_defined($abstract))
{
        $_ = $draft_text;
        /(Abstract\s*\n+)(( {3,}.+\n+)+)/i;
        $abstract = $2;
}

unless (my_defined($abstract))
{
        $_ = $draft_text;
        /(Abstract\s*\n+)([\s|\S]+)(\d[.]\s+Introduction)/i;
        $abstract = $2;
}

unless (my_defined($abstract))
{
        $_ = $draft_text;
        /(Abstract\s*\n+)([\s|\S]+)(\d translation)/i;
        $abstract = $2;
}

unless (my_defined($abstract))
{
        $_ = $draft_text;
        /(Abstract\n+)([\s|\S]+)(\n\s+Contents)/i;
        $abstract = $2;
}

unless (my_defined($abstract))
{
        $_ = $draft_text;
        /(Abstract\n+)([\s|\S]+)(\n\s*0. meta information on this)/i;
        $abstract = $2;
}
## Removing Additional Lines from Abstract ##
                                                                                  
$abstract =~ s/\n\s*requirements language\n[\s|\S]+$//i;
$abstract =~ s/\s{2,}contents\s*$//i;
$abstract =~ s/\n\s*intended status[\s|\S]+$//i;
$abstract =~ s/\n\s*key words[\s|\S]+$//i;
$abstract =~ s/\n(\d\.)*\s*conventions used in this document[\s|\S]+$//i;
$abstract =~ s/\n\s*changes since[\s|\S]+$//i;
$abstract =~ s/\n\s*terminology[\s|\S]+$//i;
$abstract =~ s/\d\.\s*introduction[\s|\S]+$//i;
$abstract =~ s/\n\s*editorial note[\s|\S]+$//i;
$abstract =~ s/\n\s*status of this memo[\s|\S]+$//i;
$abstract =~ s/\n+$//;


unless (my_defined($abstract)) {
  $parse_error=1;
  $abstract_color=$error_color;
}
$creation_date = trim($creation_date);
$creation_date = format_creation_date($creation_date);
$nop = trim($nop);
$id_document_name= trim($id_document_name);
$abstract =~ s/\n+$//g;
$abstract =~ s/^\n+//g;
#$abstract =~ s/\n\s+/\n/g;
$abstract =~ s/^\s+//g;
$abstract =~ s/\n   /\n/g;
$abstract =~ s/   /\n/g;

#error ($query,$abstract);
($abstract_q,$id_document_name_q,$first_two_pages_q) = db_quote($abstract,$id_document_name,$first_two_pages_q);
$sql = "update id_submission_detail set status_id='$status_id',last_updated_date='$last_updated_date',last_updated_time='$current_time',txt_page_count='$nop',abstract=$abstract_q,id_document_name=$id_document_name_q, creation_date='$creation_date',first_two_pages=$first_two_pages_q where submission_id = '$sub_id'" ;
db_update($dbh,$sql);
author_info_update(@authors);
unless (my_defined($nop)) {
  $nop="<i>Not Found</i>";
  $parse_error=1;
  $nop_color=$error_color;
}
$extra_error_msg="";
#switch_color($id_document_name,$revision,$creation_date,$nop,$abstract,$#authors);

$id_document_name = "<i>Not Found</i>" unless my_defined($id_document_name);
$abstract="Not Found" unless my_defined($abstract);
#$error_msg = db_select($dbh,"select error_message from id_submission_detail where submission_id=$sub_id");
$not="";
if ($idnits_failed) # IDNITs are not validated
{
        $not = " NOT";
	$status_id = 203;
	db_update($dbh,"update id_submission_detail set status_id='$status_id' where submission_id='$sub_id'");
	#print $query->redirect(-uri => "status.cgi?submission_id=$sub_id&redirect=1");
	#exit;
}

if ($invalid_version) #Invalid revision number
{
	#$status_id = 206;
        $rev_color=$error_color;
        $invalid_version = "0$invalid_version" if ($invalid_version < 10);
        $extra_error_msg .= "<li> Invalid Version Number. (Version $invalid_version is expected.)</li>\n";
	#db_update($dbh,"update id_submission_detail set status_id='$status_id' where submission_id='$sub_id'");
	#print $query->redirect(-uri => "status.cgi?submission_id=$sub_id&redirect=1");
	#exit;
}
switch_color($id_document_name,$revision,$creation_date,$nop,$abstract,$#authors);

$k=0;
for ($i=0; $i<=$#authors; $i=$i+3)
{
	$auth_no = $k +1;
        $button_label = substr($authors[$i],0,1) . ". $authors[$i+1]";
	$list[$k] = "<tr bgcolor=\"$tr_bgcolor\"><td>&nbsp; &nbsp; Author ".$auth_no.":</td> <td>".$authors[$i]." ".$authors[$i+1]." (".$authors[$i+2]." )</td></tr>";
        $author_button .= qq{<input type="button" name="ab$auth_no" value="$button_label" onClick="document.adj_form.lname.value='$authors[$i+1]';document.adj_form.fname.value='$authors[$i]';document.adj_form.submitter_email.value='$authors[$i+2]';">};
	$k++;
}
$list[$k] = "<tr bgcolor=\"$error_color\"><td colspan=\"2\"> &nbsp; &nbsp; <i>NOT FOUND</i></tr></td>\n" unless $k;
db_update($dbh,"update id_submission_detail set status_id=206 where submission_id=$sub_id") if ($parse_error);
#if ($error_flag)
#{
#	$error_msg = db_select($dbh,"select error_message from id_submission_detail where submission_id=$sub_id");
#	print_html($error_msg);
#	exit;
#}
print_html();

#Function to dispaly the HTML page

sub print_html
{
	my $warning_msg = shift;
        if (my_defined($warning_msg)) {
          my $error_message=qq{$warning_msg.<br>
Please use the back button on your browser to return to the previous screen, correct the meta-data, and resubmit the Internet-Draft.<br><br><br>
$cancel_button
};
          error_idst ($query,$error_message);
          exit;
        }
	$idnit_msg = "<a href=\"display_idnit.cgi?submission_id=$sub_id\">(View IDNITS Results)</a>";
	my @results = db_select($dbh,"select side_bar_html,top_bar_html,bottom_bar_html  from id_submission_env");
	my $sidebar = $results[0];
	my $topbar = $results[1];
	$topbar =~ s/##submission_id##/$sub_id/g;
	my $bottombar = $results[2];

	my $msg = "<p><font face=Arial size=4 color=#F20000><strong>$warning_msg</strong></font></p>";

	if($creation_date =~ /^$/)
	{
		$date_msg = "<font face=Arial color=#F20000><strong>(Not found)</strong></font>";
	}

	$max_interval=db_select($dbh,"select max_interval from id_submission_env");
	print $query->header();
print <<HTML;
<html><!-- InstanceBegin template="Templates/IETF_Main.dwt" codeOutsideHTMLIsLocked="false" -->
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<!-- InstanceBeginEditable name="doctitle" -->
<title>Collect Meta-Data $title_text</title>
<!-- InstanceEndEditable -->
<!-- InstanceBeginEditable name="head" -->
<!-- InstanceEndEditable -->
<script language="javascript">
limit=$max_interval;// time limit in seconds
limit=limit * 60000;
function timer()
{
	setTimeout('window.location="timeout.cgi?submission_id=$sub_id"',limit);
}
</script>
</head>
<body onLoad="timer();">
  <table height="598" border="0">
    <tr>
HTML
print $sidebar;
print $topbar;
print $msg;
print <<HTML;
        <!-- Body content starts-->
         <div align="left">
           <center>
             <table border="0" vspace="0">
               <tr valign="top">
                <td height="550" >
                     <!-- InstanceBeginEditable name="Body text" -->
                  <form action="adjust.cgi" method="post" enctype="multipart/form-data" name="adj_form">
<input type="hidden" name="submission_id" value="$sub_id">
                  <p>
                    <font face="Arial" size="4">
                      <strong>Check Page</strong>
                    </font>
                  </p>
<p>Your draft has$not been verified to meet IDNITS requirements. $idnit_msg</p>
$extra_error_msg
<p><strong>Meta-Data from the Draft.</strong></p>
<b>$warning_message</b>
</font>
<table border="0" width="650" id="metadatadraft">
<tr bgcolor="$tr_bgcolor">
  <td width="110"><font face="Arial" size="2">Document:</font></td>
<td><a href="$stg_url/$filename-$revision.txt">$filename</a> <a href="display_first_two_pages.cgi?submission_id=$sub_id">[View First Two Pages]</a><br>$other_format_docs</td>
</tr>
<tr bgcolor="$rev_color">
                        <td width="110"><font face="Arial" size="2">Version:</font></td>
                        <td>$revision </td></font>                      </tr>
                      <tr bgcolor="$tr_bgcolor">
                        <td><font face="Arial" size="2">Submission Date:</font></td>
                        <td>$submission_date</td></font>                      </tr>
                      <tr bgcolor="$title_color">
                        <td><font face="Arial" size="2">Title:</font></td>
                         <td>$id_document_name</td></font>                      </tr>
                    <tr bgcolor="$wg_color">
                      <td><font face="Arial" size="2">WG ID:</font></td><td>$group_acronym</td></font>
                    </tr>
                    <tr bgcolor="$tr_bgcolor">
                      <td><font face="Arial" size="2">File Size:</font></td><td>$filesize</td></font>
                    </tr>
                    <tr bgcolor="$creation_date_color">
                      <td><font face="Arial" size="2">Creation Date:</font></td><td>$creation_date</td></font>
                    </tr>

HTML
print_authors(@list);
$abstract = CGI::escapeHTML($abstract);
$abstract=~s/\n/<br>\n/g;
print <<HTML;
                      <tr bgcolor="$nop_color">
                        <td><font face="Arial" size="2">Pages:</font></td>
                         <td>$nop</td></font>                      </tr>
                      <tr bgcolor="$abstract_color" valign="top">
                        <td><font face="Arial" size="2">Abstract:</font></td>
                         <td>$abstract</td>
                         </font>
                      </tr>
                      <tr>
                        <td colspan="2"><input type="submit" value="Adjust Meta-Data" name="adjust"> <font face="Arial" size="2">(Leads to manual post by the Secretariat)</font></td>
                      </tr>
HTML
unless ($parse_error or $idnits_failed) {
  print qq{
                      <tr><td colspan="2"><hr></td></tr>
                      <tr><td colspan="2"><h3>Please edit the following meta-data before proceeding to Auto-Post</h3></td></tr>
                    </table>
                      <font face="Arial" size="2">Submitter Information.</font><br>
                    <table border="0" width="650">
  <tr><td colspan="2">
If you are one of the authors of this document, then please click the button with your name on it to automatically fill in the submitter information as requested below.  Otherwise, please manually enter your information.<br>
$author_button
  </td></tr>
                      <tr bgcolor="$tr_bgcolor">
                        <td><font face="Arial" size="2">Given Name:</font></td><td><input type="text" size="25" name="fname"></td>
                      </tr>
                      <tr bgcolor="$tr_bgcolor">
                        <td width="110"><font face="Arial" size="2">Family Name:</font></td>
                        <td><input type="text" size="25" name="lname"></td>
                      </tr>
                      <tr bgcolor="$tr_bgcolor">
                        <td><font face="Arial" size="2">Email Address:</font></td><td><input type="text" size="40" name="submitter_email"></td>
                      </tr>
                    </table>
       <input type="submit" value="Post Now" name ="Post">
};
#} else {
#  print qq{
#                      <tr><td colspan="2"><hr></td></tr>
#                    </table>
#
#                    <font face="Arial" size="2"><b>Submitter Information</b></font>
#                  <table border="0" width="650">
#                    <tr bgcolor="$tr_bgcolor">
#                      <td width="100"><font face="Arial" size="2">Last Name:</font></td>
#                      <td >$submitter_lname</td>
#                    </tr>
#                    <tr bgcolor="$tr_bgcolor">
#                      <td><font face="Arial" size="2">First Name:</font></td><td>$submitter_fname</td>
#                    </tr>
#                    <tr bgcolor="$tr_bgcolor">
#                      <td><font face="Arial" size="2">Email Address:</font></td><td>$submitter_email</td>
#                    </tr>
#                  </table>
#};
}

print <<HTML;
<input name="submission_id" type="hidden" value="$sub_id">
                  </form>
                  <!-- InstanceEndEditable -->              
                </td>
               </tr>
            </table>
          </center>
        </div>
$cancel_button
        <!-- Body content ends-->
HTML
print $bottombar;
print <<HTML
       </td>
     </tr>
  </table>
</body>
<!-- InstanceEnd --></html>
HTML
}

###############################################
# Function Name: trim
# Function Description: removes trailing spaces
# Input Parameters:
#   param1: text string
# Output:i string
# Commented by: Shailendra Singh
# Commented date: 2/15/07
###############################################


sub switch_color {
  my ($id_document_name,$revision,$creation_date,$nop,$abstract,$num_authors) = @_;
  unless (my_defined($revision)) {
    $rev_color=$error_color;
    $extra_error_msg .= "<li> Version field is empty.</li>\n";
  }
  if (my_defined($revision) and $revision !~ /\d\d/) {
    $rev_color=$error_color;
    $extra_error_msg .= "<li> Version field is not in NN format.</li>\n";
  }
  if (my_defined($revision) and $revision > 99) {
    $rev_color=$error_color;
    $extra_error_msg .= "<li> Version cannot be larger than 99.</li>\n";
  }
  unless (my_defined($id_document_name)) {
    $title_color=$error_color;
    $extra_error_msg .= "<li> Title field is empty.</li>\n";
  }
                                                                                             
  unless (my_defined($creation_date)) {
    $creation_date_color=$error_color;
    $extra_error_msg .= "<li> Creation Date field is empty or the creation date is not in a proper format.</li>\n";
  } 
  unless (my_defined($abstract)) {
    $abstract_color=$error_color;
    $extra_error_msg .= "<li> Abstract field is empty.</li>\n";
  }
  unless (check_valid_date($creation_date)) {
    $creation_date_color=$error_color;
    $extra_error_msg .= "<li> Creation Date must be within 3 days of submission date.</li>\n" if my_defined($creation_date);
  }
  unless (my_defined($nop)) {
    $nop_color=$error_color;
    $extra_error_msg .= "<li> Pages field is empty.</li>\n";
  }
  if (my_defined($nop) and $nop =~ /\D/) {
    $nop_color=$error_color;    $extra_error_msg .= "<li> Pages is not in numeric format.</li>\n";  
  }                                                                                             
  $extra_error_msg .= "<li> The I-D Submission tool could not find the authors' information</li>\n" if ($num_authors< 0);

  if (my_defined($extra_error_msg)) {
    $parse_error=1;
    $extra_error_msg = qq{<b>Meta-data errors:</b>
<ul>
$extra_error_msg
</ul>
<table border="0" width="650"><tr><td>
Please make sure that your Internet-Draft includes all of the required
meta-data in the proper format.
<br><br>
If your Internet-Draft *does* include all of the required meta-data in
the proper format, and if the error(s) identified above are due to the
failure of the tool to extract the meta-data correctly, then please use
the 'Adjust Meta-Data' button below, which will take you to the 'Adjust
Screen' where you can correct the improperly extracted meta-data.  You
will then be able to submit your Internet-Draft to the Secretariat for
manual posting.
<br><br>
If your Internet-Draft *does not* include all of the required meta-datain the proper format, then please cancel this submission, update your
Internet-Draft, and resubmit it.
<br><br>
NOTE: The Secretariat will NOT add any meta-data to your Internet-Draft
or edit the meta-data.  An Internet-Draft that does not include all of the required meta-data in the proper format WILL be returned to the
submitter.</td></tr></table>
};
  }
                                                                                             
  return 1;
}

sub check_valid_date {
  $creation_date = shift;
  if ($creation_date =~ /(\d\d\d\d)[-\/,:;~#]+(\d[\d]?)[-\/,:;~#]+(\d[\d]?)/)  {
    my $year = $1;
    my $month = $2;
    my $day = $3;
    if (($year != 0000) and ($month > 0 and $month <=12) and ($day > 0 and $day<=31))    {
       $submission_date = db_select($dbh,"select submission_date from id_submission_detail where submission_id=$sub_id");
       $current_sub_day = db_select($dbh,"select to_days(date_add('$submission_date',interval 3 day))");
       $previous_sub_day = db_select($dbh,"select to_days(date_sub('$submission_date',interval 3 day))");
       $creation_sub_day = db_select($dbh,"select to_days('$creation_date')");
       if (($creation_sub_day >= $previous_sub_day) && ($creation_sub_day <= $current_sub_day))      {
         return 1;
       } else {
         return 0;     
       }
    }
  }
  return 0;
}

sub trim
{
	my $string = shift;
	$string =~ s/^\s+//;
	$string =~ s/\s+$//;
	$string =~ s/\s+/ /g;
	$string =~ s/\n+/ /g;
	return $string;
}

###############################################################
# Function Name: author_info_update
# Function Description: Updates draft author detail in database
# Input Parameters:
#   param1: list of authors (an array)
# Output: None
# Commented by: Shailendra Singh
# Commented date: 2/15/07
###############################################################

sub author_info_update
{
	@authors = @_;
	$auth_order = 1;

	$sql = "select temp_id_document_tag from id_submission_detail where submission_id='$sub_id'";
	$id_document_tag = db_select($dbh,$sql);

	$sql = "delete from temp_id_authors where submission_id=$sub_id";
	db_update($dbh,$sql);

	for ($i=0; $i<=$#authors; $i=$i+3)
	{
		if ($authors[$i] !~ /^$/)
		{
			$sql = "insert into temp_id_authors(id_document_tag,first_name,last_name,email_address,author_order,submission_id)values($id_document_tag,'$authors[$i]','$authors[$i+1]','$authors[$i+2]',$auth_order,$sub_id)";
			db_update($dbh,$sql);
			$auth_order++;
		}
	}
}

##########################################################
# Function Name: print_authors
# Function Description: prints the elements of given array
# Input Parameters:
#   param1: an array
# Output: None
# Commented by: Shailendra Singh
# Commented date: 2/15/07
##########################################################

sub print_authors
{
	@list = @_;
	print "<tr bgcolor=\"$tr_bgcolor\"><td colspan=\"2\">Author(s) Information:</td></tr>\n";
        if ($#list > -1) {
  	  for ($i=0; $i<=$#list;$i++)
	  {
                  $_ = $list[$i];
                  #s/<input type="radio" .*;">//g if $parse_error;
		  print $_,"\n";
	  }
          #print qq{<tr bgcolor="$tr_bgcolor"><td colspan="2">If you are one of the authors above, then please click a radio button by your name to automatically fill in the submitter's information as requested below.  Otherwise, Please manually enter your information.</td></tr>} unless $parse_error;
        } else {
          $parse_error=1;
          print qq{<tr bgcolor="$error_color"><td colspan="2">&nbsp; &nbsp; <i>Not Found</i></td></tr>
};
        }
}

##########################################################
# Function Name: format_creation_date 
# Function Description:
# Input Parameters:
#   param1: 
# Output: 
# Commented by: 
# Commented date: 2/00/07
##########################################################



sub format_creation_date 
{
	my $input_date=shift;
        return "" unless my_defined($input_date);
	$input_date =lc($input_date);
	my $format_date = "";
	$_ = $input_date;
	if (/(\d\d\d\d)/) 
	{
		$format_date = "$1-";
	} else {
		return "";
	}

	$_=$input_date;
	if (/jan/) 
	{
		$format_date .= "1-";
	} elsif (/feb/) {
		$format_date .= "2-";
	} elsif (/mar/) {
		$format_date .= "3-";
	} elsif (/apr/) {
		$format_date .= "4-";
	} elsif (/may/) {
		$format_date .= "5-";
	} elsif (/jun/) {
		$format_date .= "6-";
	} elsif (/jul/) {
		$format_date .= "7-";
	} elsif (/aug/) {
		$format_date .= "8-";
	} elsif (/sep/) {
		$format_date .= "9-";
	} elsif (/oct/) {
		$format_date .= "10-";
	} elsif (/nov/) {
		$format_date .= "11-";
	} elsif (/dec/) {
		$format_date .= "12-";
	} else {
		return "";
	}


	$_ = $input_date;
	s/\d\d\d\d//;

	if (/(\d+)/) 
	{
		$format_date .= "$1";
	} else {
		return "";
	}
	return $format_date;
}
$dbh->disconnect();
