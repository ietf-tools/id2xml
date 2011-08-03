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

if ($devel_mode) {
  $qa_mode = ($http_host =~ /datatracker/)?1:0;
  $rUser = $ENV{REMOTE_USER};
  $dbname=($qa_mode)?"ietf_qa":"test_idst";
  $mode_text = ($qa_mode)?"QA Mode":"Development Mode";
}
init_database($dbname);
$dbh = get_dbh();
my $q = new CGI;
$style_url="https://www1.ietf.org/css/base.css";
$program_name = "init_rev_approval.cgi";
$program_title = "IETF Internet-Draft Initial Revision Approval Tracker";
$program_title .= " db: $dbname" if ($devel_mode);
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
$loginid = db_select($dbh,"select person_or_org_tag from iesg_login where login_name='$rUser'") unless $loginid;
$user_name=get_name($loginid);
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
     my $func = "$command(\$q)";
     $html_txt .= eval($func);
   }
   $html_txt .= qq{
$form_header_bottom
<input type="submit" value=" User's First Screen ">
</form>
} if (my_defined($command));
   return $html_txt;
}

sub main_screen {
  my $msg=shift;
  my $wg_list = get_active_wg_list();
  $approved_list="<table border=\"1\">\n<tr bgcolor=\"#bbbbbb\" align=\"center\"><td><b>Filename</b></td><td><b>Approved Date</b></td><td><b>Approved by</b></td><td><b>Recorded by</b></td></tr>";
  my @List=db_select_multiple_secure($dbh,"select filename,approved_date,approved_person_tag,recorded_by from id_approved_detail order by filename");
  for my $array_ref (@List) {
   my ($filename,$approved_date,$tag,$recorded) = @$array_ref;
   my $name=get_name($tag);
   my $recorder=get_name($recorded);
   $approved_list .= "<tr><td>$filename</td><td>$approved_date</td><Td>$name</td><td>$recorder</td></tr>\n";
  }
  $approved_list .= "</table>\n";
  return qq{
<font color="red"><pre>$msg</pre></font><br><br>
$form_header_post
<input type="hidden" name="command" value="get_chairs">
Enter Filename: <input type="text" name="filename" size="25"><br><br>
Select Group: <select name="wg"><option value="">Select WG</option>
$wg_list
</select> <b>*Selecting a WG from this list will override WG acronym part from filename*</b>
<br>
<input type="submit" value="Submit"><br>
</form>
<H3>Approved Documents</H3>
$approved_list
};

}

sub get_active_wg_list {
  my @List=db_select_multiple($dbh,"select acronym,group_acronym_id from acronym a, groups_ietf b where acronym_id=group_acronym_id and status_id=1 order by acronym");
  my $ret_val="";
  for my $array_ref (@List) {
    my ($group_acronym,$group_acronym_id) = @$array_ref;
    $ret_val .= "<option value=\"$group_acronym_id-$group_acronym\">$group_acronym</option>\n";
  }
  return $ret_val;
}



sub get_chairs {
  my $q=shift;
  my $wg_acronym="";
  my $wg_acronym_id="";
  my $filename=$q->param("filename");
  my ($approved_person_or_org_tag,$approved_date,$recorded_by)=db_select($dbh,"select approved_person_tag,approved_date,recorded_by from id_approved_detail where filename='$filename'");
  if (my_defined($approved_date)) {
    my $approved_name=get_name($approved_person_or_org_tag);
    my $recorder=get_name($recorded_by);
    error($q,"$filename has already been approved by $approved_name, recorded by $recorder on $approved_date");
  }
  if (my_defined($q->param("wg"))) {
    ($wg_acronym_id,$wg_acronym)=split "-",$q->param("wg");
  } else {
    my @idpart=split "-",$filename;
    $wg_acronym=$idpart[2];
    $wg_acronym_id = db_select($dbh,"select acronym_id from acronym a, groups_ietf b where acronym_id=group_acronym_id and status_id=1 and acronym='$wg_acronym'");
    error ($q,"Invalid WG, $wg_acronym") unless $wg_acronym_id;
  }
  my $approval_list="";
  my @List=db_select_multiple($dbh,"select person_or_org_tag from g_chairs where group_acronym_id=$wg_acronym_id");
  for my $array_ref (@List) {
    my ($chair_id) = @$array_ref;
    my $chair_name=get_name($chair_id);
    $approval_list .= qq{
<input type="radio" name="chair_id" value="$chair_id"> $chair_name <br>
};
  }


  return qq{
$form_header_post
<input type="hidden" name="command" value="record_approval">
<input type="hidden" name="filename" value="$filename">
Please select approving WG chair of $wg_acronym:<br>
$approval_list
<br>
<input type="submit" value="Submit"><br>
</form>

};

}

sub record_approval {
  my $q=shift;
  my $chair_id=$q->param("chair_id");
  my $filename=$q->param("filename");
  my $chair_name=get_name($chair_id);
  db_update($dbh,"insert into id_approved_detail (filename,approved_person_tag,approved_date,recorded_by,approved_status) values ('$filename',$chair_id,current_date,$loginid,1)");
  my ($submitter_tag,$submission_id,$auth_key)=db_select($dbh,"select submitter_tag,submission_id,auth_key from id_submission_detail where filename='$filename' and status_id=10");
  my $msg="";
  if ($submitter_tag) {
    $email=get_email($submitter_tag);
    $msg=db_select($dbh,"select init_rev_approved_msg from id_submission_env");
    $msg =~ s/##filename##/$filename/g;
    $msg =~ s/##approver##/$chair_name/g;
    my $auth_msg=db_select($dbh,"select submitter_auth_msg from id_submission_env");
    $auth_msg=~ s/##auth_key##/$auth_key/g;
    $auth_msg=~ s/##submission_id##/$submission_id/g;
    $msg .= $auth_msg; 
    $from = "IETF Secretariat <ietf-secretariat-reply\@ietf.org>";
    $cc="";
    if ($devel_mode) {
      $msg = qq{*** Only for Testing ***
Following message will be sent to the submitter:

From: $from
To: $email
Cc: $cc
Subject: Initial Version of $filename was approved

$msg
};
    }
    #send_mail($program_name,"INIT APPROVAL TOOL",$email,$msg,$from,$cc);
    db_update($dbh,"update id_submission_detail set status_id=11, last_updated_date=current_date,last_updated_time=current_time where submission_id=$submission_id");
    print $q->redirect("/idst-pub/auto_post.cgi?auth_key=$auth_key&submission_id=$submission_id&from_sec=1");
    #use following line with django ported
    #print $q->redirect("https://datatracker.ietf.org/idsubmit/verify/$submission_id/$auth_key/sec/");
  }
  return main_screen("The initial version approval for $filename from $chair_name has been recorded\n$msg");
}


