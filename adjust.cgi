#!/usr/bin/perl -w

#############################################################################
#   Program: adjust.cgi
#
#   Author : Shailendra Singh Rathore
#
#   Last Modified Date: 2/15/2007
#
#   This application displays the metadata extracted from the uploaded Internet Draft
#   and allows users to modify it.
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
$tr_bgcolor="#ddddff";                                  
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
                                  
$user_email = ($devel_mode)?db_select($dbh,"select email_address from email_addresses a, iesg_login b where login_name='$rUser' and a.person_or_org_tag=b.person_or_org_tag and email_priority=1"):"";

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
$error_flag = $in{'error_flag'};
$sub_id=$query->param("submission_id");
error_idst ($query,"Possible SQL Injection detected.") if ($sub_id =~ /\D/);
#If error message flag value is true, reload the current page and display the error message 

if ($error_flag) 
{
  $error_msg = db_select($dbh,"select error_message from id_submission_detail where submission_id=$sub_id");
     print_html($error_msg);
     exit;
}

$status_id=db_select($dbh,"select status_id from id_submission_detail where submission_id=$sub_id");

#Check the status id range

if ($status_id < 0 or ($status_id > 99 and $status_id < 200)) 
{
  error_idst ($query,"This submission is not in active state of I-D submission process.<br>\nPlease go back to <a href=\"upload.cgi\">Upload Page</a> and re-submit your draft.<br>");
  exit;
}

$program_name = "adjust.cgi";
$submitter_lname = $query->param("lname");
$submitter_fname = $query->param("fname");
$submitter_email = $query->param("submitter_email");
#$creation_date = $query->param("creation_date");
$adjust = $query->param("adjust");
$sub_id = $query->param("submission_id");


#Cancle button for the development mode
$cancel_button = qq{<form action="status.cgi" method="get">
<input type="hidden" name="submission_id" value="$sub_id">
<input type="hidden" name="cancel" value="1">
Cancel this submission: <input type="submit" value="Cancel" onClick="return window.confirm('Do you really want to cancel this submission?');">
</form>
};


#Check the values for buttons (adjust and post)

if ($adjust)
{
  #adjust clicked
  print_html();
}else{
  #post clicked
#  if(!check_valid_date($creation_date)) #if creation date is invlaid
#  {
#    print $query->redirect(-uri => "validate.cgi?submission_id=$sub_id&error_flag=1");
#    exit;
#  }
#  $sql = "update id_submission_detail set creation_date='$creation_date' where submission_id= '$sub_id'";
#  db_update($dbh,$sql);
  if(!submitter_info_check_update($submitter_lname,$submitter_fname,$submitter_email)) #If submitter information is invalid
  {
    print $query->redirect(-uri => "validate.cgi?submission_id=$sub_id&error_flag=1");
    exit;
  }
  $status_id = 0;
  $sql = "update id_submission_detail set status_id='$status_id' where submission_id= '$sub_id'";
  db_update($dbh,$sql);
  #Checking WG Init version has been moved to auto_post.cgi to authenticate the submitter first
  #section 4.1 starts here

  $sql = "select filename,submitter_tag,auth_key,group_acronym_id,revision,sub_email_priority from id_submission_detail where submission_id = '$sub_id'";
  @results = db_select($dbh,$sql);
  $filename = $results[0];
  $submitter_tag = $results[1];
  $auth_key = $results[2];
  $group_acronym_id=$results[3];
  $revision=$results[4];
  $sub_email_priority=$results[5];
  $sub_email_priority=1 unless my_defined($sub_email_priority);
#  $sql = "select approved_status from id_approved_detail where filename='$filename'";
#  $approved_status = db_select($dbh,$sql);
#  if ($approved_status == 1 or $revision ne "00" or $group_acronym_id == 1027)
#  {
    #proceed to section 4.2 'Authenticate Submitter';

    $submitter_name = get_name($submitter_tag);
    if (!$submitter_name) # Not a valid submitter
    {
   $status_id = 205;
   $sql ="update id_submission_detail set status_id = '$status_id' where submission_id='$sub_id'";
   db_update($dbh,$sql);
   print $query->redirect(-uri => "status.cgi?submission_id=$sub_id&redirect=1");
   exit;
    }
       my $exp_date=db_select($dbh,"select date_add(current_date, interval 3 day)");
    $submitter_email = get_email($submitter_tag,$sub_email_priority);
    $sql = "select submitter_auth_msg from id_submission_env";
    $sub_auth_msg = db_select($dbh,$sql);
    $sub_auth_msg =~ s/##auth_key##/$auth_key/;
    $sub_auth_msg =~ s/##submission_id##/$sub_id/;
       $sub_auth_msg =~ s/##exp_date##/$exp_date/;
    #Send a message to submitter

    my $to_email=($devel_mode)?$user_email:$submitter_email;
    $from = "IETF I-D Submission Tool <idsubmission\@ietf.org>";
    $subject="I-D Submitter Authentication for $filename";

    $status_id = 4;
    $sql = "update id_submission_detail set status_id='$status_id' where submission_id= '$sub_id'";
    db_update($dbh,$sql);
       if ($qa_mode or !$devel_mode) {
         send_mail($program_name,"IDST",$to_email,$from,$subject,$sub_auth_msg);
   print $query->redirect(-uri => "status.cgi?submission_id=$sub_id&redirect=1");
   exit;
       } else {
print $query->header("text/html");
print $query->start_html();
         print qq{
<pre>
$sub_auth_msg
</pre>
<a href="status.cgi?submission_id=$sub_id&redirect=1">Status</a><br>
</body>
</html>
};
         exit; 
       } 
#     }else{ #Initial Version Approval Required
#   $status_id = 3;
#   $sql = "update id_submission_detail set status_id='$status_id' where submission_id= '$sub_id'";
#   db_update($dbh,$sql);
#   print $query->redirect(-uri => "status.cgi?submission_id=$sub_id&redirect=1");
#   exit;
#     }
}

################################
# Function Name:
# Function Description:
# Input Parameters:
#   param1: 
# Output: 
# Commented by: Shailendra Singh 
# Commented date: 2/00/07
#################################

#Function to dispaly the HTML page

sub print_html
{
  my $warning_msg = shift;
  my @results = db_select($dbh,"select side_bar_html,top_bar_html,bottom_bar_html  from id_submission_env");
  my $sidebar = $results[0];
  my $topbar = $results[1];
     $topbar =~ s/##submission_id##/$sub_id/g;
  my $bottombar = $results[2];
  my $msg="<p><font face=Arial size=4 color=#F20000><strong>$warning_msg</strong></font></p>";
  my $sql = "select filename,revision,submission_date,id_document_name,txt_page_count,abstract,creation_date,comment_to_sec,group_acronym_id,filesize,submitter_tag from id_submission_detail where submission_id='$sub_id'";
  @results1 = db_select($dbh,$sql);
  $filename = $results1[0];
  $revision = $results1[1];
  $submission_date = $results1[2];
  $id_document_name = $results1[3];
     $id_document_name=~s/"/&quot;/g;
  $nop = $results1[4];
  $abstract = $results1[5];
     $abstract =~ s/"/&quot;/g;
  $creation_date = $results1[6];
  $comment = $results1[7];
     $group_acronym_id=$results1[8];
     $filesize=$results1[9];
     $submitter_tag=$results1[10];
     
     if (my_defined($submitter_tag)) {
    ($submitter_lname,$submitter_fname) = db_select($dbh,"select last_name,first_name from person_or_org_info where person_or_org_tag=$submitter_tag");
    $submitter_email=get_email($submitter_tag);
     }
     $group_acronym=($group_acronym_id==1027)?"Individual Submission":db_select($dbh,"select acronym from acronym where acronym_id=$group_acronym_id");
  if($creation_date=~ /^$/ or $creation_date =~ /0000-00-00/)
  {
    $creation_date = "yyyy-mm-dd";
  }

  $stg_url = db_select($dbh,"select staging_url from id_submission_env");
     $author_button="";
  @authors = db_select_multiple($dbh,"select last_name,first_name,email_address from temp_id_authors where submission_id=$sub_id order by author_order");
     $num_auth_row=$#authors+2;
     $ex_auth_num=$#authors+1;
  $k=0;
  for ($i=0; $i<=$num_auth_row; $i++)
  {
    $j=0;
    $auth_no = $k +1;
    if ($authors[$i][$j] eq "")
    {
   $authors[$i][$j] = "\"\" ";
   $authors[$i][$j+1] = "\"\" ";
   $authors[$i][$j+2] = "\"\" ";
    }
    $auth_list[$k] = "<tr bgcolor=\"$tr_bgcolor\"><td align=left><font face=Arial size=2><strong>".$auth_no.":</strong></font></td><td align=left><input type=text size=20  value =$authors[$i][$j+1] name=f$auth_no></td><td align=left><input type=text size=20 value =$authors[$i][$j] name=l$auth_no></td><td align=left><input type=text size=40 value =$authors[$i][$j+2] name=e$auth_no></td></tr>\n";
    $k++;
    $button_label = substr($authors[$i][$j+1],0,1) . ". $authors[$i][$j]";
    $author_button .= qq{<input type="button" name="ab$auth_no" value="$button_label" onClick="document.aform.lname.value='$authors[$i][$j]';document.aform.fname.value='$authors[$i][$j+1]';document.aform.submitter_email.value='$authors[$i][$j+2]';">} if ($i < $ex_auth_num);
  }
  $max_interval=db_select($dbh,"select max_interval from id_submission_env");
  print $query->header();
print <<HTML;
<html><!-- InstanceBegin template="Templates/IETF_Main.dwt" codeOutsideHTMLIsLocked="false" -->
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<!-- InstanceBeginEditable name="doctitle" -->
<title>Adjust Meta-Data $title_text</title>
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
         <p>
        <font face="Arial" size="4">
          <strong>Adjust External Meta-Data</strong>
        </font>
         </p>
         <form action="status.cgi" method="post" name="aform">
         <input type="hidden" name="submission_id" value="$sub_id">
         <input type="hidden" name="redirect" value="1">
         <p><strong>Document: </strong><a href="$stg_url/$filename-$revision.txt">$filename <a href="display_first_two_pages.cgi?submission_id=$sub_id">[View First Two Pages]</a></a>
        <table border="0">
            <tr>
           <td><font face="Arial" size="2">Submission Date:</font></td><td>$submission_date</td>
            </tr>
            <tr>
           <td><font face="Arial" size="2">WG ID:</font></td><td>$group_acronym</td>
            </tr>
            <tr>
           <td><font face="Arial" size="2">File Size:</font></td><td>$filesize</td>
            </tr>
          </table>
         </p>
        <hr>
         <table border="0" width="700">
        <tr>
          <td ><font face="Arial" size="2"><strong>Adjust Data:</strong></font></td>
          </tr>
          <tr bgcolor="$tr_bgcolor">
            <td><font face="Arial" size="2">Title:</font></td><td><input type="text" size="65" name="title" value="$id_document_name"></font></td>
          </tr>
          <tr bgcolor="$tr_bgcolor">
            <td><font face="Arial" size="2">Version:</font></td><td><input type="text" size="3" name="revision" value="$revision"></td></font>
          </tr>
          <tr bgcolor="$tr_bgcolor">
            <td><font face="Arial" size="2">Creation Date:</font></td><td><input type="text" size="25" name="creation_date" value="$creation_date"></td></font>          </tr>
          <tr bgcolor="$tr_bgcolor">
            <td><font face="Arial" size="2">Pages:</font></td><td><input type="text" size="25" name="nop" value="$nop"></td></font>
          </tr>
          <tr bgcolor="$tr_bgcolor">
            <td valign="top"><font face="Arial" size="2">Abstract:</font></td><td><textarea cols="72" rows="4" name="abstract">$abstract</textarea></td></font>
          </tr>
          <tr bgcolor="$tr_bgcolor">
            <td><font face="Arial" size="2">Submitter:</font></td><td>If you are one of the authors, then please click a button by your name to automatically fill in the submitter's information as requested below.  Otherwise, Please manually enter your information.<br>
$author_button
          </td></font>
          </tr>
          <tr bgcolor="$tr_bgcolor">
            <td><font face="Arial" size="2">Given Name:</font></td>
            <td><input type="text" size="25" name="fname" value="$submitter_fname"></td></font>
          </tr>
          <tr bgcolor="$tr_bgcolor">
            <td><font face="Arial" size="2">Family Name:</font></td>
            <td><input type="text" size="25" name="lname" value="$submitter_lname"></td></font>
          </tr>
          <tr bgcolor="$tr_bgcolor">
            <td><font face="Arial" size="2">Email Address:</font></td><td><input type="text" size="45" value="$submitter_email" name="submitter_email"></td></font>
          </tr>
          <tr bgcolor="$tr_bgcolor">
            <td><font face="Arial" size="2">Comments to the Secretariat:</font></td><td><textarea cols="72" rows="4" name="comment_to_sec" value=$comment></textarea></td>
          </tr>
        </table>
        <hr>
        <p><font face="Arial" size="2">Authors</font>
          <table border="0" width="700">
            <tr bgcolor="$tr_bgcolor">
           <td align="center">&nbsp;</td>
           <td align="center" width="150"><font face="Arial" size="2"><strong>Given Name</strong></font></td>
           <td align="center" width="150"><font face="Arial" size="2"><strong>Family Name</strong></font></td>
           <td align="center"><font face="Arial" size="2"><strong>Email</strong></font></td>
            </tr>
HTML
print @auth_list;
print <<HTML;
          </table>
<p>
<input type="submit" align="middle" value="Submit for manual posting" name="manual_post">
        </p>
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
print <<HTML;
    </td>
  </tr>
  </table>
</body>
<!-- InstanceEnd --></html>
HTML
}

##################################################################
# Function Name: submitter_info_check_update
# Function Description: check fnd update the submitter information
# Input Parameters:
#   param1:Last name(String)
#   param2:First name(String)
#   param3:Email address(String)
# Output: true or false
# Commented by: Shailendra Singh
# Commented date: 2/15/07
##################################################################


sub submitter_info_check_update
{
  $lname = shift;
  $fname = shift;
  $email = shift;
  my $flag = 0;
     my $error_msg = "";
  $error_msg .= "<li> Submitter's last name is empty." if ($lname =~ /^$/);
  $error_msg .= "<li> Submitter's first name is empty." if($fname =~ /^$/);
     $error_msg .= "<li> Submitter's email address is empty." if ($email =~ /^$/);
  $error_msg .= "<li> Submitter's email address is not in valid email format." unless(is_valid_email($email));
     if (my_defined($error_msg)) {
    $error_msg = qq{<ul>
$error_msg
</ul>
Please use the back button on your browser to fix meta-data and resubmit.<br><br><br>
$cancel_button
};
    error_idst ($query,$error_msg);
    exit;
     }
  ($fname_q,$lname_q,$email_q) = db_quote($fname,$lname,$email);
  $sql = "select person_or_org_tag,email_priority from email_addresses where email_address=$email_q";
  ($person_or_org_tag,$email_priority) = db_select($dbh,$sql);
  if ($person_or_org_tag)
  {
    $submitter_tag = $person_or_org_tag;
    db_update($dbh,"update id_submission_detail set submitter_tag=$person_or_org_tag, sub_email_priority=$email_priority where submission_id=$sub_id");
  }else{
    $sql = "insert into person_or_org_info(first_name,last_name)values($fname_q,$lname_q)";
    db_update($dbh,$sql);
    $sth = $dbh->prepare("select MAX(person_or_org_tag) as ST from person_or_org_info");
    $row=$sth->execute();
    $row=$sth->fetchrow_hashref();
    $submitter_tag= $row->{'ST'};
       $email_priority=1;
    $sql = "insert into email_addresses(person_or_org_tag,email_address,email_priority)values($submitter_tag,$email_q,$email_priority)";
    db_update($dbh,$sql);
       db_update($dbh,"update id_submission_detail set submitter_tag=$submitter_tag, sub_email_priority=$email_priority where submission_id=$sub_id");
  }
     # Is submitter in authors' list of current document?
  $id_document_tag = db_select ($dbh,"select temp_id_document_tag from id_submission_detail where submission_id = '$sub_id'");
     # Is submitter in authors' list of previous revisions?
  my $res = db_select($dbh,"select id from temp_id_authors where id_document_tag = '$id_document_tag' and email_address='$email'");
     $res = db_select($dbh,"select count(*) from email_addresses where person_or_org_tag=$submitter_tag and email_priority=$id_document_tag") unless ($res);
  if (!$res)
  {
    unless ($group_acronym_id == 1027)
    {
            #Is submitter a chair of WG to which the document belongs?
   my $email_res = db_select($dbh, "select email_address from email_addresses where $submitter_tag in (select  a.person_or_org_tag from g_chairs a, id_submission_detail b where a.group_acronym_id=b.group_acronym_id and b.submission_id=$sub_id)");
   $flag=1 unless ($email_res);
    }else{
   $flag =1;
    }

  }
  if ($flag == 1)
  {
    $status_id = 205;
    $sql = "update id_submission_detail set status_id = '$status_id' where submission_id = '$sub_id'";
    db_update($dbh,$sql);
    print $query->redirect("status.cgi?submission_id=$sub_id&redirect=1");
    exit;
  }

  return 1;

}

###################################################################
# Function Name: check_valid_date
# Function Description: To check for the valid creation date format
# Input Parameters:
#   param1: a date string
# Output: true or false
# Commented by: Shailendra Singh
# Commented date: 2/15/07
###################################################################


sub check_valid_date
{
  $creation_date = shift;
  if ($creation_date =~ /(\d\d\d\d)[-\/,:;~#]+(\d[\d]?)[-\/,:;~#]+(\d[\d]?)/)
  {
    my $year = $1;
    my $month = $2;
    my $day = $3;

    if (($year != 0000) and ($month > 0 and $month <=12) and ($day > 0 and $day<=31))
    {
   $submission_date = db_select($dbh,"select submission_date from id_submission_detail where submission_id=$sub_id");
      $current_sub_day = db_select($dbh,"select to_days('$submission_date')");  
      $previous_sub_day = db_select($dbh,"select to_days(date_sub('$submission_date',interval 3 day))");
      $creation_sub_day = db_select($dbh,"select to_days('$creation_date')");
      if (($creation_sub_day >= $previous_sub_day) && ($creation_sub_day <= $current_sub_day))
      {
     return 1;
      }else{
     my $error_msg = "Creation date must be within 3 days of the submission date";
     my $sql = "update id_submission_detail set error_message='$error_msg' where submission_id=$sub_id";
     db_update($dbh,$sql);
     return 0;
  
   }
    }
  }
  my $error_msg = "Invalid creation date, $creation_date";
  my $sql = "update id_submission_detail set error_message='$error_msg' where submission_id=$sub_id";
  db_update($dbh,$sql);
  return 0;
}
