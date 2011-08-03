#!/usr/bin/perl
##########################################################################
#      Copyright (c) 2006 Neustar Secretariat Services, Inc.
#
#      Program: 
#      Author : Michael Lee, Neustar Secretariat Services
#      Last Modified Date: 12/1/2006
#
#      This Web application provides ... 
#
#####################################################
use lib '/a/www/ietf-datatracker/release';
use GEN_DBUTIL_NEW;
use GEN_UTIL;
use IETF;
use CGI;
use CGI_UTIL;

$script_loc=$ENV{SCRIPT_NAME};
$http_host=$ENV{HTTP_HOST};
$devel_mode = ($script_loc =~ /devel/)?1:0;
$qa_mode = 0;
$dbname = "ietf";
my $q = new CGI;

if ($devel_mode) {
  $qa_mode = ($http_host =~ /datatracker/)?1:0;
  $dbname=($qa_mode)?"ietf_qa":"test_idst";
  $mode_text = ($qa_mode)?"QA Mode":"Development Mode";
}
init_database($dbname);
$dbh = get_dbh();

$style_url="http://www.ietf.org/css/base.css";
$program_name = "wg_init_rev_approval.cgi";
$program_title = "IETF Internet-Draft Initial Version Approval Tracker";
$program_title .= " $mode_text db: $dbname" if ($devel_mode);
$table_header = qq{<table cellpadding="1" cellspacing="1" border="0">
};
$table_header2 = qq{<table cellpadding="1" cellspacing="1" border="0" width="800">
};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">};
$form_header_post2 = qq{<form action="$program_name" method="POST" name="form_post2">};
$form_header_post3 = qq{<form action="$program_name" method="POST" name="form_post3">};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">};
$form_header_get = qq{<form action="$program_name" method="GET">};
$form_header_noname = qq{<form action="$program_name" method="GET">
};
$bc="{";
$ec="}";
$color1="#cccccc";
$color2="#eeeeee";
$rUser=$ENV{REMOTE_USER};
$loginid = db_select_secure($dbh,"select person_or_org_tag from iesg_login where login_name=?",$rUser) unless $loginid;
$loginid = db_select_secure($dbh,"select person_or_org_tag from wg_password where login_name=?",$rUser) unless $loginid;
$user_name=get_name($loginid);
$user_email=get_email($loginid);
error ($q,"Invalid User, $rUser") unless $loginid;
$html_top = qq|
<link rel="stylesheet" type="text/css" href="$style_url" />
<blockquote>
<h2><center>$program_title <font color="red"><i>$mode_text</i></font></center></h2>
<i>$user_name</i> logged on
<hr>

|;
$html_bottom = qq{
<hr>
<li>If you require assistance in using this tool, or wish to report a bug, then please send a message to <a href="mailto:ietf-action\@ietf.org">ietf-action\@ietf.org</a>.</li>

</blockquote>
};

$asterisk = "<font color=\"red\"><b>*</b></font>";
$html_body = get_html_body($q);
print $q->header("text/html"),
      $q->start_html(-title=>$program_title),
      $q->p($html_top),
      $q->p($html_body),
      $q->p($html_bottom),
      $q->end_html;

$dbh->disconnect();
exit;

sub get_html_body {
   my $q = shift;
   my $command = $q->param("command");
   my $html_txt = "";
  if (defined($q->param("from_auto_post"))) {
    my $submission_id=$q->param("submission_id");
    my $filename=db_select_secure($dbh,"select filename from id_submission_detail where submission_id=?",$submission_id);
    return main_screen("The initial version approval for $filename from $user_name has been recorded.<br>\n");
  }
   unless (my_defined($command)) {
     $html_txt .= main_screen();
   } else {
     $command =~ m/^([a-zA-Z0-9\._]+)$/ or error($q, "Bad data in first argument");
     $command = $1;       # Assign untainted data

     my $func = "$command(\$q)";
     $html_txt .= eval($func);
   }
   return $html_txt;
}

sub main_screen {
  my $msg=shift;
  $msg = qq{<font color="red"><pre>$msg</pre></font><hr>
<h3>You can approve additional initial version documents</h3>
} if my_defined($msg);
  $approved_list="<table border=\"1\">\n<tr bgcolor=\"#bbbbbb\" align=\"center\"><td><b>Filename</b></td><td><b>Approved Date</b></td></tr>";
  my @List=db_select_multiple_secure($dbh,"select filename,approved_date from id_approved_detail where approved_person_tag=?",$loginid);
  for my $array_ref (@List) {
   my ($filename,$approved_date) = @$array_ref;
   $approved_list .= "<tr><td>$filename</td><td>$approved_date</td></tr>\n";
  }
  $approved_list .= "</table>\n";
  return qq{
$msg
$form_header_get
<input type="hidden" name="command" value="record_approval">
Enter Filename: <input type="text" name="filename" size="25"><br><br>
<br>
<input type="submit" value="Approve This Internet-Draft"><br>
</form>
<H3>Approved Documents</H3>
$approved_list
};

}

sub record_approval {
  my $q=shift;
  my $filename=$q->param("filename");
  $filename =~ s/\.txt$//;
  $filename =~ s/-\d+$//;
  my ($approved_person_or_org_tag,$approved_date,$recorded_by)=db_select_secure($dbh,"select approved_person_tag,approved_date,recorded_by from id_approved_detail where filename=?",$filename);
  if (my_defined($approved_date)) {
    my $approved_name=get_name($approved_person_or_org_tag);
    my $recorder=get_name($recorded_by);
    return main_screen("$filename has already been approved by $approved_name, and recorded by $recorder on $approved_date"); 
  }
  my @idpart=split "-",$filename;
  if ($filename =~ /draft-ietf-krb-wg-/) {
    $wg_acronym="krb-wg";
  } else {
    $wg_acronym=$idpart[2];
  }
  $wg_acronym_id = db_select_secure($dbh,"select acronym_id from acronym a, groups_ietf b where acronym_id=group_acronym_id and status_id=1 and acronym=?",$wg_acronym);
  error ($q,"Invalid WG, $wg_acronym") unless $wg_acronym_id;
  #$devel_mode=0;
  unless ($devel_mode) {
    my $is_valid_chair=db_select_secure($dbh,"select count(*) from g_chairs where group_acronym_id=? and person_or_org_tag=?",$wg_acronym_id,$loginid);
    error ($q,"$user_name is not a chair of working group, $wg_acronym") unless $is_valid_chair;
  }
  db_update_secure($dbh,"insert into id_approved_detail (filename,approved_person_tag,approved_date,recorded_by,approved_status) values (?,?,current_date,?,1)",$filename,$loginid,$loginid);
  my ($submitter_tag,$submission_id,$auth_key)=db_select_secure($dbh,"select submitter_tag,submission_id,auth_key from id_submission_detail where status_id=10 and filename=?",$filename);
  my $msg="";
  my $dis_msg="";
  if ($submitter_tag) {
    $email=get_email($submitter_tag);
    $msg=db_select($dbh,"select init_rev_approved_msg from id_submission_env");
    $msg =~ s/##filename##/$filename/g;
    $msg =~ s/##approver##/$user_name/g;
    $from = "IETF Secretariat <ietf-secretariat-reply\@ietf.org>";
    $cc="";
    $subject = "Initial Version of $filename was approved";
    if ($devel_mode and !$qa_mode) {
      $dis_msg = qq{*** Only for Testing ***
Following message will be sent to the submitter:

From: $from
To: $email
Cc: $cc
Subject: $subject 

$msg
};
    }
    $to_email=($devel_mode)?$user_email:$email;
    send_mail($program_name,"WG INIT APPROVAL TOOL",$to_email,$from,$subject,$msg,$cc) if ($qa_mode or !$devel_mode);
     db_update_secure($dbh,"update id_submission_detail set status_id=11, last_updated_date=current_date,last_updated_time=current_time where submission_id=?",$submission_id);
    $url = ($devel_mode)?"/cgi-bin/devel/public":"/idst";
    print $q->redirect("$url/auto_post.cgi?auth_key=$auth_key&submission_id=$submission_id&from_wg=1");
    #use following line with django ported
    #print $q->redirect("https://datatracker.ietf.org/idsubmit/verify/$submission_id/$auth_key/wg/");
    exit;
  }
  return main_screen("The initial version approval for $filename from $user_name has been recorded.\n$dis_msg");
}


