#!/usr/bin/perl -w

#############################################################################
#      Program: status.cgi
#
#      Author : Shailendra Singh Rathore
#
#      Last Modified Date: 2/15/2007
#
#      This application displays error and warning pages. 
#############################################################################


use lib '/a/www/ietf-datatracker/release/';
use CGI(':standard');
use DBI;
use GEN_UTIL;
use GEN_DBUTIL_NEW;
use IETF;
use CGI_UTIL;

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
                                                                                     
$user_email = ($devel_mode)?db_select($dbh,"select email_address from email_addresses a, iesg_login b where login_name='$rUser' and a.person_or_org_tag=b.person_or_org_tag and email_priority=1"):"";

$program_name="status.cgi";
$tr_bgcolor="#ddddff";
$error_color="#ffaaaa";
$extra_error_msg="";
$passed_filename="";
$sql_injection_warning="Possible SQL Injection detected.";
@results = db_select($dbh,"select side_bar_html,top_bar_html,bottom_bar_html  from id_submission_env");     
$sidebar = $results[0];
$topbar = $results[1];
$bottombar = $results[2];
$topbar =~ s/<a href="status.+>Status<\/a>/<a href="status.cgi">Status<\/a>/;

#Check if any parameter is being sent through a query string

if (length ($ENV{'QUERY_STRING'}) > 0)
{
  $buffer = $ENV{'QUERY_STRING'};
  @pairs = split(/&/, $buffer);
  foreach $pair (@pairs)
  {
    ($name, $value) = split(/=/, $pair);
    $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
    $passed_filename = $name if ($name =~ /^draft-/);
  }
}
$passed_filename=$query->param("passed_filename") if defined($query->param("passed_filename"));
error_idst ($query,$sql_injection_warning) if check_sql_injection ($passed_filename);
if (my_defined($passed_filename))
{
  $passed_filename =~ s/\.txt$//g;
  $passed_filename =~ s/-\d\d$//g;
  $sub_id=db_select($dbh,"select submission_id from id_submission_detail where filename='$passed_filename' and status_id > -3 order by submission_id desc");
        error_idst ($query,"No valid history found for $passed_filename.<br>\nPlease go back to <a href=\"upload.cgi\">Upload Page</a> and re-submit your draft.<br>") unless $sub_id;

}else{
  $sub_id = $query->param("submission_id");
  error_idst ($query,$sql_injection_warning) if check_sql_injection ($sub_id);
  unless (my_defined($sub_id)) {
     print $query->header("text/html");
     print $query->start_html();
     print qq{<table border="0" height="598">
<tr valign="top"><td>$sidebar</td>
<td>$topbar
<form action="status.cgi" method="get">
Please enter the filename of the Internet-Draft who's status you wish to view: <br><br>

<input type="text" name="passed_filename" size="25" value="draft-">
<br>
<br>
<input type="submit" value="Find Status">
</form>
<br>
<b>Please note that the Status page only displays the status of an Internet-Draft whose posting is still in progress or an Internet-Draft that has been successfully posted.</b>

<br><br><br>
$bottombar
</td></tr></table>
</body>
</html>
};
     exit;
  }
}
$sql = "select status_id,filename,revision,submission_date,id_document_name,creation_date,txt_page_count,abstract,group_acronym_id,submitter_tag,temp_id_document_tag,comment_to_sec,filesize,file_type,sub_email_priority,invalid_version,idnits_failed from id_submission_detail where submission_id='$sub_id'";
@results = db_select($dbh,$sql);
                                                                                             
$status_id = $results[0];
unless (defined($query->param("redirect"))) {
  print $query->redirect(-uri => "validate.cgi?submission_id=$sub_id") if ($status_id == 6 or $status_id==2);
  print $query->redirect(-uri => "check.cgi?submission_id=$sub_id") if ($status_id == 1);
}
$filename = $results[1];
$revision = $results[2];
$submission_date = $results[3];
$id_document_name = $results[4];
$creation_date = $results[5];
$creation_date = "" if ($creation_date eq "0000-00-00");
$nop = $results[6];
$abstract = $results[7];
$group_acronym_id = $results[8];
$group_acronym=($group_acronym_id==1027)?"Individual Submission":db_select($dbh,"select acronym from acronym where acronym_id=$group_acronym_id");
$group_acronym="" unless $group_acronym;
$submitter_tag = $results[9];
$id_document_tag = $results[10];
$comment_to_sec=$results[11];
$filesize = $results[12];
$file_type=$results[13];
$sub_email_priority=$results[14];
$invalid_version=$results[15];
$idnits_failed=$results[16];
#$idnits_line=($idnits_failed)?"come here
$file_type=~s/\.txt//;
$file_type=~s/^,//;
my @temp=split ',',$file_type;

$manual_post = $query->param("manual_post");
$init_approve_requested=$query->param("init_approve_requested");
#If manual post is requested
@stg_env = db_select($dbh,"select staging_path,staging_url,current_manual_proc_date from id_submission_env");
$stg_path = $stg_env[0];
$stg_url = $stg_env[1];
$rev_color=($status_id==201)?$error_color:$tr_bgcolor;
$wg_color=$tr_bgcolor;
$title_color=$tr_bgcolor;
$nop_color=$tr_bgcolor;
$creation_date_color=$tr_bgcolor;
$abstract_color=$tr_bgcolor;
if ($status_id==-1 or $status_id==-2) {
  $stg_url="http://www.ietf.org/internet-drafts";
  $stg_url.="/idst-test" if ($devel_mode);
}
$other_format_docs="";
for my $file_ext (@temp) {   $other_format_docs .= " &nbsp; &nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href=\"$stg_url/$filename-$revision$file_ext\">$filename-$revision$file_ext</a><br>\n";
}
$num_author=db_select($dbh,"select count(*) from temp_id_authors where submission_id=$sub_id");
switch_color($id_document_name,$revision,$creation_date,$nop,$abstract,$group_acronym_id,$num_author,$invalid_version);
$cancel=$query->param("cancel");
if ($cancel) 
{
    my $to_notify_cancel=($status_id > -3 and $status_id < 100)?1:0;
    db_update($dbh,"update id_submission_detail set status_id=-4 where submission_id=$sub_id");
    system "mv $stg_path/$filename-$revision.txt $stg_path/$filename-$revision-$sub_id-cancelled.txt";
    unlink while (<$stg_path/$filename-$revision.*>);
    $status_id=-4;
    if ($to_notify_cancel) {
      my $remote_ip = $ENV{REMOTE_ADDR};
# Need to populate $to_list with authors and submitter's email
      my $to_list ="";
      my @List = db_select_multiple($dbh,"select email_address from temp_id_authors where submission_id=$sub_id");
      for my $array_ref (@List) {
        my ($email)=@$array_ref;
        $to_list .= "$email," if ($email =~ /@/);
      }
      chop($to_list) if my_defined($to_list);
      $to = ($devel_mode)?$user_email:$to_list;
      $from="IETF I-D Submission Tool <idsubmission\@ietf.org>";
      $subject = "Submission of $filename-$revision has been Cancelled";
      $msg = qq{This message is to notify you that submission of an Internet-Draft, $filename-$revision, has just been cancelled by a user whose computer has an IP address of $remote_ip.

The IETF Secretariat.
};
      #$msg = indent_text2($msg,0,73);
    #send a notice to submitter and authors or a document that was just cancelled
      if ($qa_mode or !$devel_mode) { #send message
          send_mail($program_name,"IDST",$to,$from,$subject,$msg);
      } else { #Development mode, don't send, just display
print $query->header("text/html");
print $query->start_html();
print qq{
Following message would be sent to the authors to notify cancellation: <br>
To: $to_list<br>
Subject: $subject<br><br>
<pre>
$msg
</pre>
<a href="status.cgi?submission_id=$sub_id">Status</a><br>
</body>
</html>};
exit;
      }
    }
}

#$cancel_button = ($devel_mode and !$cancel)?qq{<form action="status.cgi" method="get">
$cancel_button = (!$cancel and $status_id > -1)?qq{<form action="status.cgi" method="get">
<input type="hidden" name="submission_id" value="$sub_id">
<input type="hidden" name="cancel" value="1">
Cancel this submission: <input type="submit" value="Cancel" onClick="return window.confirm('Do you really want to cancel this submission?');">
</form>
}:"";


$current_manual_proc_date=$stg_env[2];
$manual_message=($status_id==5)?"It will take up to $current_manual_proc_date business days to process this Internet-Draft":"";
if ($manual_post)
{
        $manual_message = "It will take up to $current_manual_proc_date business days to process this Internet-Draft";
  $id_document_name = $query->param("title");
  $id_document_name_html = $query->param("title");
  $id_document_name =~ s/&quot;/"/g;
  $revision = $query->param("revision");
  $creation_date = $query->param("creation_date");
  $nop = $query->param("nop");
  $abstract = $query->param("abstract");
  $abstract_html = $query->param("abstract");
  $abstract =~ s/&quot;/"/g;
  $comment_to_sec = $query->param("comment_to_sec");
  $submitter_lname = $query->param("lname");
  $submitter_fname = $query->param("fname");
  $submitter_email = $query->param("submitter_email");
  my $num_authors=db_select($dbh,"select count(id) from temp_id_authors where submission_id=$sub_id");
  $num_authors += 2;
  for ($i=0; $i < $num_authors; $i++) {
    $qindex=$i+1;
    last unless my_defined($query->param("e$qindex"));
    $authors[$i][0] = $query->param("f$qindex");
    $authors[$i][1] = $query->param("l$qindex");
    $authors[$i][2] = $query->param("e$qindex");
  }
  validate_meta_data($id_document_name,$revision,$creation_date,$nop,$abstract,$authors[0][2],$submitter_lname,$submitter_fname,$submitter_email);
switch_color($id_document_name,$revision,$creation_date,$nop,$abstract,$group_acronym_id,$num_author);
my $comment_to_sec_text = (my_defined($comment_to_sec))?"\nComment:\n$comment_to_sec":"";
$meta_data_info=qq{
Filename:\t   $filename
Version:\t   $revision
Staging URL:\t   $stg_url/$filename-$revision.txt
Title:\t\t   $id_document_name
Creation_date:\t   $creation_date
WG ID:\t\t   $group_acronym
Number_of_pages: $nop
Abstract:
$abstract
};
  $sql = "update id_submission_detail set revision=?,id_document_name=?,txt_page_count=?,abstract=?,comment_to_sec=? where submission_id ='$sub_id'";
  db_update_secure($dbh,$sql,$revision,$id_document_name,$nop,$abstract,$comment_to_sec);
  $abstract=$abstract_html;
  $id_document_name=$id_document_name_html;

  $sql = "update id_submission_detail set creation_date=? where submission_id=$sub_id";
  db_update_secure($dbh,$sql,$creation_date);

  author_info_update();
  $submitter_status = submitter_info_check_update($submitter_lname,$submitter_fname,$submitter_email);
  if($submitter_status == 0) #If submitter information is invalid
  {
    print $query->redirect(-uri => "adjust.cgi?submission_id=$sub_id&error_flag=1");
    exit;
  }
  $meta_data_info .= qq{
Submitter: $submitter_fname $submitter_lname ($submitter_email)
};
  if ($submitter_status == -1) {
    $meta_data_info .= "Submitter is not found in the Authors list\n";
  }

  $status_id =5;

  $sql = "update id_submission_detail set status_id = ? where submission_id = '$sub_id'";
  db_update_secure($dbh,$sql,$status_id);

  
  $to_email=($devel_mode)?$user_email:"internet-drafts\@ietf.org";
  $from="IETF I-D Submission Tool <idsubmission\@ietf.org>";
  $subject="Manual Post Requested for $filename";
  my $author_list = "";
  my $author_email_list ="";
  for my $array_ref (@authors) 
  {
    my ($first_name,$last_name,$email_address) = @$array_ref;
    $author_list .= "$first_name $last_name, $email_address\n";
    $author_email_list .= ",$email_address" unless ($email_address eq $submitter_email);
  }
  $tool_url=($devel_mode)?"https://datatracker.ietf.org/public/devel/idst":"https://datatracker.ietf.org/idst";
  $cc_email=$submitter_email;
  $cc_email .= $author_email_list if my_defined($author_email_list);
  unless ($group_acronym_id == 1027) {
    my $wg_email = get_chairs_email($group_acronym_id);
    $cc_email .= ",$wg_email" if my_defined($wg_email);
  }
  $msg = qq{Manual Posting Requested for following Internet-Draft:

I-D Submission Tool URL: $tool_url/status.cgi?submission_id=$sub_id

$meta_data_info
Author(s):
$author_list
$comment_to_sec_text
};
  $cc_email= "" if ($devel_mode);
        #if (1) {
        if ($qa_mode or !$devel_mode) {
          send_mail($program_name,"IDST",$to_email,$from,$subject,$msg,$cc_email);
        } else {
print $query->header("text/html");
print $query->start_html();
print qq{
<pre>
$msg
</pre>
<a href="status.cgi?submission_id=$sub_id">Status</a><br>
</body>
</html>
};
exit;
       }
  ##proceed to section 6.5
}

$sql = "select first_name,last_name from person_or_org_info where person_or_org_tag=$submitter_tag";
@results = db_select($dbh,$sql);
$submitter_fname = $results[0];
$submitter_lname = $results[1];
$sql = "select email_address from email_addresses where person_or_org_tag=$submitter_tag and email_priority=$sub_email_priority";
$submitter_email = db_select($dbh,$sql);
$submitter_lname = "" unless $submitter_lname;
$submitter_fname = "" unless $submitter_fname;
$submitter_email = "" unless $submitter_email;
$sql = "select first_name,last_name,email_address from temp_id_authors where submission_id='$sub_id' order by author_order";
@authors = db_select_multiple($dbh,$sql);
$k=0;
for ($i=0 ; $i<=$#authors; $i++)
{
  $j=0; 
  $auth_no = $k +1;
  $auth_list[$k] = "<tr bgcolor=\"$tr_bgcolor\"><td> &nbsp; &nbsp; Author ".$auth_no.":</td> <td>".$authors[$i][$j]." ".$authors[$i][$j+1]." (".$authors[$i][$j+2]." )</td></tr>";
  $k++;
}

$draft_status = db_select($dbh,"select status_value from id_submission_status where status_id=$status_id");
if ($init_approve_requested) 
{
  $wg_chair_id=$query->param("wg_chair_id");
  unless (my_defined($wg_chair_id)) 
  {
    $message="Please select one of the working group chairs";
  } else {
    $status_id=10;
    db_update($dbh,"update id_submission_detail set status_id=$status_id where submission_id=$sub_id"); 
    $draft_status = db_select($dbh,"select status_value from id_submission_status where status_id=$status_id");
    $msg = db_select($dbh,"select id_approval_request_msg from id_submission_env");
    $msg =~ s/##submitter_name##/$submitter_fname $submitter_lname/g;
    $msg =~ s/##submitter_email##/$submitter_email/g;
    $msg =~ s/##filename##/$filename/g;
    $to_email=($devel_mode)?$user_email:"$group_acronym-chairs\@tools.ietf.org";
    $from="IETF I-D Submission Tool <idsubmission\@ietf.org>";
    $subject="Initial Version Approval Request for $filename";
                if ($qa_mode or !$devel_mode) {
      send_mail($program_name,"IDST",$to_email,$from,$subject,$msg);
                } else {
print $query->header("text/html");
print $query->start_html();
print qq{
<pre>
TO: $group_acronym-chairs\@tools.ietf.org
$msg
</pre>
<a href="status.cgi?submission_id=$sub_id">Status</a><br>
</body>
</html>
};
exit;
                }
  }
}

$abstract = CGI::escapeHTML($abstract);

#Check the status id value (If initial version approval required)

if ($status_id == 3)
{
  #section 6.3
  $sql = "select person_or_org_tag from g_chairs where group_acronym_id='$group_acronym_id'";
  @results = db_select_multiple($dbh,$sql);
  my $i=0;
  for my $array_ref (@results) 
  {
    my ($person_or_org_tag)=@$array_ref;
    my $name=get_name($person_or_org_tag);
    $list[$i] = "<input type=\"radio\" name=\"wg_chair_id\" value=\"$person_or_org_tag\"> $name<br>\n";
    $i++;
  }
  print_init_ver_app($message,@list);

}elsif ($status_id == 4) #Submitter authentication requested
{
  #section 6.2
        
  $message = "An email with a submitter verification key and URL has been sent to the submitter. However, verification has not yet been received. Upon receipt of verification (clicking the link in the email), this status page will be shown with updated status information.";
  print_html($draft_status,$message);
}elsif ($status_id == -1) #Posted by the tool
{
  #section 6.1
  $message = "Your Internet-Draft has been successfully posted in IETF servers and an announcement has been sent out.";
  print_html($draft_status,$message);
}elsif ($status_id == -4) # Draft submission  has been cancelled
{
  #section 6.1
  $message = "Submission of your Internet-Draft has been cancelled.";
  print_html($draft_status,$message);
}elsif (($status_id >= 101 ) && ($status_id <= 199)) #Error range for status id
{
  #section 6.7
  error_idst ($query,$draft_status);
}elsif (($status_id >=201) && ($status_id <=299)) #Warning range for status id
{
  #section 6.6
  print_warning();
}else{
  #section 6.5
  $message = "&nbsp;" ;
  #$message .= "\n<br><pre>$msg</pre>" if $devel_mode;
  print_html($draft_status,$message);
}

sub get_chairs_email {
  my $group_acronym_id=shift;
  my $ret_val = "";
  my @List = db_select_multiple($dbh,"select person_or_org_tag from g_chairs where group_acronym_id = $group_acronym_id");
  for my $array_ref (@List) {
    my ($pID) = @$array_ref;
    my $email=get_email($pID);
    $ret_val .= "$email,";
  }
  chop($ret_val) if my_defined($ret_val);
  return $ret_val;
}

sub switch_color {
  my ($id_document_name,$revision,$creation_date,$nop,$abstract,$group_acronym_id,$num_author,$invalid_version) = @_;
  unless (my_defined($revision)) {
    $rev_color=$error_color;
    $extra_error_msg .= "<li> Version field is empty.</li>\n";
  }
  if (my_defined($revision) and $revision !~ /\d\d/) {
    $rev_color=$error_color;
    $extra_error_msg .= "<li> Version is not in NN format.</li>\n";
  }
  if (my_defined($revision) and $revision > 99) {
    $rev_color=$error_color;
    $extra_error_msg .= "<li> Version cannot be larger than 99.</li>\n";
  }
  if ($invalid_version) {
    $rev_color=$error_color;
    $extra_error_msg .= "<li> Invalid Version Number.</li>\n";
  }
  unless (my_defined($id_document_name)) {
    $title_color=$error_color;
    $extra_error_msg .= "<li> Title field is empty.</li>\n";
  }
  unless ($group_acronym_id) {
    $wg_color=$error_color;
    $extra_error_msg .= "<li> WG ID is not a valid IETF working group.</li>\n";
  }
  unless (my_defined($creation_date)) {
    $creation_date_color=$error_color;
    $extra_error_msg .= "<li> Creation Date field is empty or the creation date is not in a proper format.</li>\n";
  } 
  unless (check_valid_date($creation_date)) {
    $creation_date_color=$error_color;
    $extra_error_msg .= "<li> Creation Date must be within 3 days of submission date.</li>\n" if my_defined($creation_date); 
  }
  unless (my_defined($abstract)) {
    $abstract_color=$error_color;
    $extra_error_msg .= "<li> Abstract field is empty.</li>\n";
  }
  unless (my_defined($nop)) {
    $nop_color=$error_color;
    $extra_error_msg .= "<li> Pages field is empty.</li>\n";
  }
  if (my_defined($nop) and $nop =~ /\D/) {
    $nop_color=$error_color;
    $extra_error_msg .= "<li> Pages is not in numeric format.</li>\n";
  }
  unless ($num_author) {
    $extra_error_msg .= "<li> Authors section was not found.</li>\n";
  }
  if (my_defined($extra_error_msg)) {
    $extra_error_msg = qq{<br><br><b>Meta-data errors:</b>
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
If your Internet-Draft *does not* include all of the required meta-data
in the proper format, then please cancel this submission, update your
Internet-Draft, and resubmit it.
<br><br>
NOTE: The Secretariat will NOT add any meta-data to your Internet-Draft
or edit the meta-data.  An Internet-Draft that does not include all of
the required meta-data in the proper format WILL be returned to the
submitter.</td></tr></table>
};
  }

  return 1;
}

sub validate_meta_data {
  my ($id_document_name,$revision,$creation_date,$nop,$abstract,$author1_email,$submitter_lname,$submitter_fname,$submitter_email) = @_;
  my $error_message="";
  $error_message .= "<li> Title field is empty.\n" unless my_defined($id_document_name);
  $error_message .= "<li> Version field is empty.\n" unless my_defined($revision);
  $error_message .= "<li> Version is not in NN format.\n" if (my_defined($revision) and $revision !~ /\d\d/);
  $error_message .= "<li> Version cannot be larger than 99.\n" if (my_defined($revision) and $revision > 99);
  $error_message .= "<li> Creation Date field is empty or the creation date is not in a proper format.\n" unless my_defined($creation_date);
  $error_message .= "<li> Creation Date must be within 3 days of submission date.\n" if (!check_valid_date($creation_date) and my_defined($creation_date));
  $error_message .= "<li> Abstract field is empty.\n" unless my_defined($abstract);
  $error_message .= "<li> Pages field is empty.\n" unless my_defined($nop);
  $error_message .= "<li> Pages is not in numeric format.\n" if (my_defined($nop) and $nop =~ /\D/);
  $error_message .= "<li> Submitter's Given Name field is empty.\n" unless my_defined($submitter_fname);
  $error_message .= "<li> Submitter's Family Name field is empty.\n" unless my_defined($submitter_lname);
  $error_message .= "<li> Submitter's Email Address field is empty.\n" unless my_defined($submitter_email);
  $error_message .= "<li> Submitter's Email Address is not in valid format.\n" unless is_valid_email($submitter_email);
  $error_message .= "<li> Primary Author's Email Address field is empty.\n" unless my_defined($author1_email);
  if (my_defined($error_message)) {
    $error_message = "<ul>\n$error_message\n</ul>\n<br>Please use the back button on your browser to return to the previous screen, correct the meta-data, and resubmit the Internet-Draft.<br><br><br>\n$cancel_button";
    error_idst ($query,$error_message);
  }
  return 1;
}


#Function to display the HTML page
sub print_html
{
  $draft_status = shift;
  $message = shift;
  $filename="<a href=$stg_url/$filename-$revision.txt>$filename</a>";
  $ext_button=($status_id==6)?qq{<a href="validate.cgi?submission_id=$sub_id">[Enter External Meta-Data]</a>
}:"";
  print $query->header();
  #print $stg_path;
print <<HTML;
<html><!-- InstanceBegin template="Templates/IETF_Main.dwt" codeOutsideHTMLIsLocked="false" -->
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<!-- InstanceBeginEditable name="doctitle" -->
<title>$draft_status $title_text</title>
<!-- InstanceEndEditable -->
<!-- InstanceBeginEditable name="head" -->
<!-- InstanceEndEditable -->
</head>
<body>
  <table height="598" border="0">
    <tr>
HTML
print $sidebar;
print $topbar;
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
                      <strong>Status</strong>
                    </font>
                  </p>
                  <p>
                    <font face="Arial" size="3">
                      <strong>Draft Status: $draft_status</font> $ext_button</strong>
                  </p>
<!---
                  <p>
                      <font face="Arial" size="2">
                      <strong>Document: $filename <a href="display_first_two_pages.cgi?submission_id=$sub_id">[View First Two Pages]</a></strong><br>
$other_format_docs 
Submission ID: $sub_id
                    </font>
                  </p>
--->
                  <p>$message
$manual_message
</p>
                    <p>
                                            
                  <table border="0" width="650">
<tr bgcolor="$tr_bgcolor">
  <td width="110"><font face="Arial" size="2">Document:</font></td>
<td><a href="$stg_url/$filename-$revision.txt">$filename</a> <a href="display_first_two_pages.cgi?submission_id=$sub_id">[View First Two Pages]</a><br>$other_format_docs</td>
</tr>
                    <tr bgcolor="$tr_bgcolor">
                      <td ><font face="Arial" size="2">Version:</font></td>
                      <td >$revision</td>
                    </tr>
                    <tr bgcolor="$tr_bgcolor">
                      <td width="110"><font face="Arial" size="2">Submission Date:</font></td><td>$submission_date</td>
                      </font>
                    </tr>
                    <tr bgcolor="$tr_bgcolor">
                      <td><font face="Arial" size="2">Title:</font></td><td>$id_document_name</td></font>
                    </tr>
                    <tr bgcolor="$tr_bgcolor">
                      <td><font face="Arial" size="2">WG ID:</font></td><td>$group_acronym</td></font>
                    </tr>
                    <tr bgcolor="$tr_bgcolor">
                      <td><font face="Arial" size="2">File Size:</font></td><td>$filesize</td></font>
                    </tr>
                    <tr bgcolor="$tr_bgcolor">
                      <td><font face="Arial" size="2">Creation Date:</font></td><td>$creation_date</td></font>
                    </tr>
HTML
print_authors(@auth_list);
print <<HTML;
                    <tr bgcolor="$tr_bgcolor">
                      <td><font face="Arial" size="2">Pages:</font></td><td>$nop</td></font>
                    </tr>
                    <tr bgcolor="$tr_bgcolor" valign="top">
                      <td><font face="Arial" size="2">Abstract:</font></td><td><pre>$abstract</pre></td></font>
                    </tr>
                    <tr bgcolor="$tr_bgcolor">
                      <td><font face="Arial" size="2">Comment:</font></td><td><pre>$comment_to_sec</pre></td>
                    </tr>
                  </table>
                  </p>
                  <br>
                    <p>
                    <font face="Arial" size="2">Submitter Information.</font>
                  <table border="0" width="650">
                    <tr bgcolor="$tr_bgcolor">
                      <td><font face="Arial" size="2">Given Name:</font></td><td>$submitter_fname</td>
                    </tr>
                    <tr bgcolor="$tr_bgcolor">
                      <td width="100"><font face="Arial" size="2">Family Name:</font></td>
                      <td >$submitter_lname</td>
                    </tr>
                    <tr bgcolor="$tr_bgcolor">
                      <td><font face="Arial" size="2">Email Address:</font></td><td>$submitter_email</td>
                    </tr>
                  </table></p>
                    
                    
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



#Function to display initial version approval page

sub print_init_ver_app
{
  my $message=shift;
  @list = @_;
  $filename="<a href=$stg_url/$filename-$revision.txt>$filename</a>";
  print $query->header();
print <<HTML;
<html><!-- InstanceBegin template="Templates/IETF_Main.dwt" codeOutsideHTMLIsLocked="false" -->
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<!-- InstanceBeginEditable name="doctitle" -->
<title>Initial Version Approval $title_text</title>
<!-- InstanceEndEditable -->
<!-- InstanceBeginEditable name="head" -->
<!-- InstanceEndEditable -->
</head>
<body>
  <table height="598" border="0">
    <tr>
HTML
print $sidebar;
print $topbar;
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
<strong>Status</strong>
</font>
</p>
<b>$message</b>
<p>
<font face="Arial" size="3">
<strong>Draft Status: $draft_status</font> </strong>
</p>
<p>
<font face="Arial" size="2">
<strong>Document: $filename <a href="display_first_two_pages.cgi?submission_id=$sub_id">[View First Two Pages]</a></strong><br>
$other_format_docs
Submission ID: $sub_id
</font>
</p>
<p>
$manual_message
<p>
<font face="Arial" size="2">
Your Draft needs approval from one of the following working group chairs:

</font></p>
<form action="status.cgi" method="get">
<input type="hidden" name="init_approve_requested" value="1">
<input type="hidden" name="submission_id" value="$sub_id">
HTML
print @list;
print <<HTML;
<p>
<input type="submit" value="Send Request">
</form>
</p>
<hr>
<table border="0" width="650">
<tr bgcolor="$rev_color">
<td ><font face="Arial" size="2">Version:</font></td>
<td >$revision</td>
</tr>
<tr bgcolor="$tr_bgcolor">
<td width="110"><font face="Arial" size="2">Submission Date:</font></td><td>$submission_date</td>
</font>
</tr>
<tr bgcolor="$title_color">
<td><font face="Arial" size="2">Title:</font></td><td>$id_document_name</td></font>
</tr>
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
print_authors(@auth_list);
print <<HTML;
<tr bgcolor="$nop_color">
<td><font face="Arial" size="2">Pages:</font></td><td>$nop</td></font>
</tr>
<tr bgcolor="$abstract_color" valign="top">
<td><font face="Arial" size="2">Abstract:</font></td><td><pre>$abstract</pre></td></font>
</tr>
<tr bgcolor="$tr_bgcolor">
<td><font face="Arial" size="2">Comment:</font></td><td><pre>$comment_to_sec</pre></td>
</tr>

</table>
                  <br>
                    <p>
                    <font face="Arial" size="2">Submitter Information.</font>
                  <table border="0" width="650">
                    <tr bgcolor="$tr_bgcolor">
                      <td><font face="Arial" size="2">Given Name:</font></td><td>$submitter_fname</td>
                    </tr>
                    <tr bgcolor="$tr_bgcolor">
                      <td width="100"><font face="Arial" size="2">Family Name:</font></td>
                      <td >$submitter_lname</td>
                    </tr>
                    <tr bgcolor="$tr_bgcolor">
                      <td><font face="Arial" size="2">Email Address:</font></td><td>$submitter_email</td>
                    </tr>
                  </table></p>
                    
                    
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

#Function to display a warning page
sub print_warning
{
  if ($idnits_failed)
  {
    $msg = "<a href='display_idnit.cgi?submission_id=$sub_id' name='test'>(View IDNITS Results)</a>"; 
    if ($status_id != 203) { #Other error exists than just idnits error
      $idnits_error_msg = db_select($dbh,"select status_value from id_submission_status where status_id=203");
      $draft_status = "$draft_status / $idnits_error_msg";
    }
  }
  
  $filename="<a href=$stg_url/$filename-$revision.txt>$filename</a>";
  print $query->header();
print <<HTML;
<html><!-- InstanceBegin template="Templates/IETF_Main.dwt" codeOutsideHTMLIsLocked="false" -->
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<!-- InstanceBeginEditable name="doctitle" -->
<title>$draft_status $title_text</title>
<!-- InstanceEndEditable -->
<!-- InstanceBeginEditable name="head" -->
<!-- InstanceEndEditable -->
</head>
<body>
  <table height="598" border="0">
    <tr>
HTML
print $sidebar;
print $topbar;
print <<HTML;
<!-- Body content starts-->
<div align="left">
           <center>
             <table border="0" vspace="0">
               <tr valign="top">
                <td height="550" >
                     <!-- InstanceBeginEditable name="Body text" -->
                     <form action="adjust.cgi" method="post" enctype="multipart/form-data">
<p>
<font face="Arial" size="3">
<strong>Draft Status: $draft_status</font> $msg</strong>
</p>
<!---
                  <p>
                      <font face="Arial" size="2">
                      <strong>Document: $filename <a href="display_first_two_pages.cgi?submission_id=$sub_id">[View First Two Pages]</a></strong><br>
$other_format_docs
--->
Submission ID: $sub_id
                    </font>
                    <font face="Arial" size="2">
$extra_error_msg
                    </font>
<br>Please use "Adjust Meta-Data" button to manually submit this document to the Secretariat.
                                            
                  <table border="0" width="650">
<tr bgcolor="$tr_bgcolor">
  <td width="110"><font face="Arial" size="2">Document:</font></td>
<td><a href="$stg_url/$filename-$revision.txt">$filename</a> <a href="display_first_two_pages.cgi?submission_id=$sub_id">[View First Two Pages]</a><br>$other_format_docs</td>
</tr>
                    <tr bgcolor="$rev_color">
                      <td ><font face="Arial" size="2">Version:</font></td>
                      <td >$revision</td>
                    </tr>
                    <tr bgcolor="$tr_bgcolor">
                      <td width="110"><font face="Arial" size="2">Submission Date:</font></td><td>$submission_date</td>
                      </font>
                    </tr>
                    <tr bgcolor="$title_color">
                      <td><font face="Arial" size="2">Title:</font></td><td>$id_document_name</td></font>
                    </tr>
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
print_authors(@auth_list);
print <<HTML;
                    <tr bgcolor="$nop_color">
                      <td><font face="Arial" size="2">Pages:</font></td><td>$nop</td></font>
                    </tr>
                    <tr bgcolor="$abstract_color" valign="top">
                      <td><font face="Arial" size="2">Abstract:</font></td><td><pre>$abstract</pre></td></font>
                    </tr>
                    <tr bgcolor="$tr_bgcolor">
                      <td><font face="Arial" size="2">Comment:</font></td><td><pre>$comment_to_sec</pre></td>
                    </tr>

                  </table>
                  </p>
                  <br>
<br>
                  <table border=0>
                    <tr>
                                                                                  <td><input type="submit" value="Adjust Meta-Data" name="adjust"> <font face="Arial" size="2">(Leads to manual post by the Secretariat)</font></td>
                                                                                </tr>
                      <tr>
                        <input  name="submission_id" type="hidden"  value="$sub_id">
                      </tr>
                  </table>
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
  return 1 unless my_defined($creation_date);
  if ($creation_date =~ /(\d\d\d\d)[-\/,:;~#]+(\d[\d]?)[-\/,:;~#]+(\d[\d]?)/)
  {
    my $year = $1;
    my $month = $2;
    my $day = $3;

    if (($year != 0000) and ($month > 0 and $month <=12) and ($day > 0 and $day<=31))
    {
      $submission_date = db_select($dbh,"select submission_date from id_submission_detail where submission_id=$sub_id");
      $current_sub_day = db_select($dbh,"select to_days(date_add('$submission_date',interval 3 day))");
      $previous_sub_day = db_select($dbh,"select to_days(date_sub('$submission_date',interval 3 day))");
      $creation_sub_day = db_select($dbh,"select to_days('$creation_date')");
      if (($creation_sub_day >= $previous_sub_day) && ($creation_sub_day <= $current_sub_day))
      {
        return 1;
      }else{
        my $error_msg = "Creation date must be within 3 days of the submission date";
        return 0;
      }
    }
  }
  return 0;
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
#  @authors = @_;
  $auth_order = 1;

  $sql = "select temp_id_document_tag from id_submission_detail where submission_id='$sub_id'";
  $id_document_tag = db_select($dbh,$sql);

  $sql = "delete from temp_id_authors where submission_id=$sub_id";
  db_update($dbh,$sql);

  for my $array_ref (@authors)
  {
    my ($first_name,$last_name,$email_address) = @$array_ref;
    ($first_name,$last_name,$email_address) = db_quote($first_name,$last_name,$email_address);
    error_idst ($query,$sql_injection_warning) if check_sql_injection ($first_name,$last_name,$email_address);
    $sql = "insert into temp_id_authors(id_document_tag,first_name,last_name,email_address,author_order,submission_id)values($id_document_tag,$first_name,$last_name,$email_address,$auth_order,$sub_id)";
    db_update($dbh,$sql);
    $auth_order++;
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
  print "<tr bgcolor=\"$tr_bgcolor\"><td colspan=\"2\">Author(s) Information</td></tr>\n";
  for ($i=0; $i<=$#list; $i++)
  {
    print $list[$i],"\n";
  }
  print "<tr bgcolor=$error_color><td colspan=\"2\"> &nbsp; &nbsp; &nbsp; <i>Not Found</td></tr>\n" unless $i;
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
  if ($lname =~ /^$/)
  {
    my $error_msg = "Invalid last name";
    return 0;
  }
  if($fname =~ /^$/)
  {
    my $error_msg = "Invalid first name";
    return 0;
  }
  unless(is_valid_email($email))
  {
    my $error_msg = "Invalid email address,$email";
    return 0;
  }
  $sql = "select person_or_org_tag,email_priority from email_addresses where email_address=?";
  ($person_or_org_tag,$sub_email_priority) = db_select_secure($dbh,$sql,$email);
  if ($person_or_org_tag)
  {
    $submitter_tag = $person_or_org_tag;
    db_update($dbh,"update id_submission_detail set submitter_tag=$person_or_org_tag, sub_email_priority=$sub_email_priority where submission_id=$sub_id");
  }else{
    $sql = "insert into person_or_org_info(first_name,last_name)values(?,?)";
    db_update_secure($dbh,$sql,$fname,$lname);
    $sth = $dbh->prepare("select MAX(person_or_org_tag) as ST from person_or_org_info");
    $row=$sth->execute();
    $row=$sth->fetchrow_hashref();
    $submitter_tag= $row->{'ST'};
    $sub_email_priority=1;
    $sql = "insert into email_addresses(person_or_org_tag,email_address,email_priority)values($submitter_tag,?,$sub_email_priority)";
    db_update_secure($dbh,$sql,$email);
    $sql = "update id_submission_detail set submitter_tag = $submitter_tag where submission_id =$sub_id";
    db_update($dbh,$sql);
  }
        # Is submitter in authors' list of current document?
  $id_document_tag = db_select ($dbh,"select temp_id_document_tag from id_submission_detail where submission_id = '$sub_id'");
  # Is submitter in authors' list of previous revisions?
  my $res = db_select_secure($dbh,"select id from temp_id_authors where id_document_tag = '$id_document_tag' and email_address=?",$email);
   $res = db_select($dbh,"select count(*) from email_addresses where person_or_org_tag=$submitter_tag and email_priority=$id_document_tag") unless ($res);
   if (!$res)
   {
           unless ($group_acronym_id == 1027)
           {
                   #Is submitter a chair of WG to which the document belongs?
                  my $email_res = db_select($dbh, "select email_address from email_addresses where $submitter_tag in (select  a.person_or_org_tag from g_chairs a, id_submission_detail b where a.group_acronym_id=b.group_acronym_id and b.submission_id=$sub_id)");
                  return -1 unless ($email_res);
            }else{
                  return -1;
            }

    }

  return 1;
}

$dbh->disconnect();
