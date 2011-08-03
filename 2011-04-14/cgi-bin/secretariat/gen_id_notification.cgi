#!/usr/bin/perl -w
##########################################################################
#      Copyright © 2004 Foretec Seminars, Inc.
#
#      Program: main.cgi
#      Author : Michael Lee, Foretec Seminars, Inc
#      Last Modified Date: 9/25/2004
#
#      This Web application provides ... 
#
#####################################################
use lib '/a/www/ietf-datatracker/release';
use GEN_DBUTIL;
use GEN_UTIL;
use IETF;
use CGI;
use CGI_UTIL;

$host=$ENV{SCRIPT_NAME};
$devel_mode = ($host =~ /devel/)?1:0;
$test_mode = ($host =~ /test/)?1:0;
$dbname = "ietf";
$mode_text = "";
if ($devel_mode) {
  $dbname="develdb";
  $mode_text = "Development Mode";
} elsif ($test_mode) {
  $dbname="testdb";
  $mode_text = "Test Mode";
}
#$dbname="ietf";
init_database($dbname);

my $q = new CGI;
$cat=$q->param("cat");
$filename=$q->param("filename");
$revision=$q->param("revision");
$replaced_by_filename=$q->param("replaced_by_filename");
error($q,"Unknown Category") unless ($cat =~ /update|resurrection|replacement|withdrawn_ietf|withdrawn_submitter|extention/);
($id_document_tag,$group_acronym_id)=db_select("select id_document_tag,group_acronym_id from internet_drafts where filename='$filename'");
$in_tracker = db_select("select count(*) from id_internal where id_document_tag=$id_document_tag and rfc_flag=0");
$style_url="https://www.ietf.org/css/base.css";
$program_name = "gen_id_notification.cgi";
$program_title = "I-D Notification for $cat";
$program_title .= "<br> db: $dbname" if ($devel_mode);
$table_header = qq{<table cellpadding="5" cellspacing="5" border="0" width="800">
};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">
<input type="hidden" name="cat" value="$cat">
<input type="hidden" name="filename" value="$filename">
<input type="hidden" name="revision" value="$revision">
};
$form_header_post .= "<input type=\"hidden\" name=\"replaced_by_filename\" value=\"$replaced_by_filename\">" if my_defined($replaced_by_filename);
$form_header_post2 = qq{<form action="$program_name" method="POST" name="form_post2">};
$form_header_post3 = qq{<form action="$program_name" method="POST" name="form_post3">};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">};
$form_header_get = qq{<form action="$program_name" method="GET" name="form_get">};
$html_top = qq|
<link rel="stylesheet" type="text/css" href="$style_url" />
<h2><center>$program_title <font color="red"><i>$mode_text</i></font></center></h2>
<br><br>
|;
$html_bottom = qq{
</body>
</html>
};

$html_body = get_html_body($q);

print $q->header("text/html"),
      $q->start_html(-title=>$program_title),
      $q->p($html_top),
      $q->p($html_body),
      $q->end_html;

exit;

sub get_html_body {
   my $q = shift;
   my $command = $q->param("command");
   my $html_txt = "<blockquote>\n";
   unless (my_defined($command)) {
     $html_txt .= main_screen($q);
   } else {
     my $func = "$command(\$q)";
     $html_txt .= eval($func);
   }
   $html_txt .= qq{
</blockquote>
   $form_header_bottom
   <input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true">
   <input type="button" name="close_button" value="Close this Window" onClick="window.close();return true">
   </form>
   } if (my_defined($command) and $command ne "main_screen");
   return $html_txt;
}

sub main_screen {
  return qq{
$form_header_post
<input type="hidden" name="command" value="gen_notification">
$table_header
<tr><td width="150">Name and Email of Requestor: </td>
<td><input type="text" name="requestor" size="65" value="&#34;Name&#34; <Email Address>"></td</tr>
<tr><td>Other for Cc list:<br>One per line </td>
<td><textarea name="cc_list" rows="5" cols="50"></textarea></td></tr>
</table>
<br>
<input type="submit" value="Schedule the Notification">
</form>
<br><Br>
};
}
sub add_to_email_list {
  my $person_or_org_tag = shift;
  my $email_list=shift;
  my $requestor=shift;
  my $email=get_email($person_or_org_tag);
  my $name=get_name($person_or_org_tag);
  $email_list .= "\"$name\" <$email>, " unless ($email_list =~ /$email/ or $requestor =~ /$email/);
  return $email_list;
}
sub get_cc_list {
  my $requestor=shift;
  my $sent_cc_list=shift;
  #$sent_cc_list =~ s/ //g;
  $sent_cc_list =~ s/\n/,/g;
  my @List = db_select_multiple("select person_or_org_tag from id_authors where id_document_tag=$id_document_tag");
  my $email_list = $sent_cc_list;;
  $email_list.="," if my_defined($email_list);
  for my $array_ref (@List) { #get authors
    my ($person_or_org_tag) = @$array_ref;
    $email_list = add_to_email_list($person_or_org_tag,$email_list,$requestor);
  } 
  if ($group_acronym_id != 1027) { #WG submission
    my @List_wg=db_select_multiple("select person_or_org_tag from g_chairs where group_acronym_id=$group_acronym_id");
    for my $array_ref (@List_wg) { #get wg chairs
      my ($person_or_org_tag) = @$array_ref;
      $email_list = add_to_email_list($person_or_org_tag,$email_list,$requestor);
    }
    my $wg_advisor = db_select("select person_or_org_tag from area_directors a, groups_ietf b where group_acronym_id=$group_acronym_id and area_director_id=id");
    $email_list = add_to_email_list($wg_advisor,$email_list,$requestor);
    if ($in_tracker) {
      my $shepherding_ad = db_select("select person_or_org_tag from iesg_login a, id_internal b where b.id_document_tag=$id_document_tag and job_owner=id");
      $email_list = add_to_email_list($shepherding_ad,$email_list,$requestor);
      my $state_change_notice_to = db_select("select state_change_notice_to from id_internal where id_document_tag=$id_document_tag");
      if (my_defined($state_change_notice_to)) { #get state_change_notice_to field
        my @temp = split ',',$state_change_notice_to;
        for (@temp) {
          s/ //g;
          $email_list .= "$_, " unless ($email_list =~ /$_/);
        }
      }
     }
  }
  chop($email_list);
  #chop($email_list);
  return $email_list;
}
sub gen_notification {
  my $q=shift;
  my $requestor=$q->param("requestor");
  my $sent_cc_list=$q->param("cc_list");
  my $cc_list = get_cc_list($requestor,$sent_cc_list);


  my $message = "Empty Message";
  my $subject = "Empty Subject";
  my $expired_date = db_select("select date_add(current_date,interval 185 day)");
  $expired_date = convert_date($expired_date,5);
  if ($cat eq "update") {
    $subject = "Posting of $filename-$revision.txt";
    $message = "As you requested, $filename-$revision.txt, an updated version of an expired Internet-Drafts, has been posted.  The draft will expire on $expired_date unless it is replaced by an updated version, or the Secretariat has been notified that the document is under official review by the IESG or has been passed to the IRSG or RFC Editor for review and/or publication as an RFC.";
  } elsif ($cat eq "replacement") {
    $revision = decrease_revision($revision);
    my ($rp_tag,$rp_revision) = db_select("select id_document_tag,revision from internet_drafts where filename='$replaced_by_filename'");
    $subject = "Replacement of $filename-$revision.txt with $replaced_by_filename-$rp_revision.txt";
    unless ($rp_revision) {
      $message = "Invalid Replaced by filename, $replaced_by_filename<br>select revision from internet_drafts where filename='$replaced_by_filename'";
    } else {
      my $rp_in_tracker = db_select("select count(*) from id_internal where id_document_tag=$rp_tag and rfc_flag=0");
      if ($in_tracker and $rp_in_tracker == 0) {
## Add replacing I-D to the ID Tracker in the state of CUR_STATE ##
        my $cur_state=db_select("select cur_state from id_internal where id_document_tag=$id_document_tag and rfc_flag=0");
        my $cur_state_name=db_select("select document_state_val from ref_doc_states_new where document_state_id = $id_document_tag");
        my $ballot_id=db_select("select max(ballot_id) from id_internal");
        $ballot_id++;
        my ($group_flag,$token_name,$token_email,$email_display,$agenda,$assigned_to,$mark_by,$job_owner,$area_acronym_id,$state_change_notice_to,$dnp,$dnp_date,$noproblem) = db_select("select group_flag,token_name,token_email,email_display,agenda,assigned_to,mark_by,job_owner,area_acronym_id,state_change_notice_to,dnp,dnp_date,noproblem");
        ($token_name,$token_email,$email_display,$assigned_to,$state_change_notice_to) = db_quote($token_name,$token_email,$email_display,$assigned_to,$state_change_notice_to);
        db_update("insert into id_document_tag,rfc_flag,ballot_id,primary_flag,group_flag,token_name,token_email,email_display,agenda,assigned_to,mark_by,job_owner,area_acronym_id,state_change_notice_to,dnp,dnp_date,noproblem,event_date) values ($rp_tag,0,$ballot_id,1,$group_flag,$token_name,$token_email,$email_display,$agenda,$assigned_to,$mark_by,$job_owner,$area_acronym_id,$state_change_notice_to,$dnp,'$dnp_date',$noproblem,CURRENT_DATE)");
        add_document_comment(0,$rp_tag,"Draft Added by the IESG Secretary in state $cur_state_name. ",0);
        add_document_comment(0,$rp_tag,"Earlier history may be found in the Comment Log for <a href=\"/public/pidtracker.cgi?command=view_id&dTag=$id_document_tag&rfc_flag=0\">$filename</a>.",0);
        $message = qq{As you requested, $filename-$revision.txt has been marked as replaced by $replaced_by_filename-$rp_revision.txt in the IETF Internet-Drafts database.
The I-D Tracker state of $filename-$revision.txt has been changed from "$cur_state_name" to "Dead." $replaced_by_filename-$rp_revision.txt has been added to the I-D Tracker in state "$cur_state_name."
};
      } else {
        $message = "As you requested, $filename-$revision.txt has been marked as replaced by $replaced_by_filename-$rp_revision.txt in the IETF Internet-Drafts database.";
      }
    }
  } elsif ($cat eq "withdrawn_submitter") {
    $revision = decrease_revision($revision);
    $subject = "Withdrawal of $filename-$revision.txt";
    $message = "As you requested, $filename-$revision.txt has been marked as withdrawn by the submitter in the IETF Internet-Drafts database.";
    if ($in_tracker) {
      my $cur_state=db_select("select cur_state from id_internal where id_document_tag=$id_document_tag and rfc_flag=0");
      my $cur_state_name=db_select("select document_state_val from ref_doc_states_new where document_state_id = $id_document_tag");
      $msg .= " The I-D Tracker state has been changed from \"$cur_state_name\" to \"Dead.\" ";
    }
  } elsif ($cat eq "withdrawn_ietf") {
    $revision = decrease_revision($revision);
    $subject = "Withdrawal of $filename-$revision.txt";
    $message = "As you requested, $filename-$revision.txt has been marked as withdrawn by the IETF in the IETF Internet-Drafts database.";
    if ($in_tracker) {
      my $cur_state=db_select("select cur_state from id_internal where id_document_tag=$id_document_tag and rfc_flag=0");
      my $cur_state_name=db_select("select document_state_val from ref_doc_states_new where document_state_id = $id_document_tag");
      $msg .= " The I-D Tracker state has been changed from \"$cur_state_name\" to \"Dead.\" ";
    }
  } elsif ($cat eq "resurrection") {
    $subject = "Resurrection of $filename-$revision.txt";
    $message = "As you requested, $filename-$revision.txt has been resurrected.  The draft will expire on $expired_date unless it is replaced by an updated version, or the Secretariat has been notified that the document is under official review by the IESG or has been passed to the IRSG or RFC Editor for review and/or publication as an RFC.";
  } elsif ($cat eq "extention") {
    $subject = "Extension of Expiration Date for $filename-$revision.txt";
    $message = "As you requested, the expiration date for $filename-$revision.txt has been extended. The draft will expire on $expired_date unless it is replaced by an updated version, or the Secretariat has been notified that the document is under official review by the IESG or has been passed to the IRSG or RFC Editor for review and/or publication as an RFC.";
  } else {
    error($q,"Wrong Option");
  }
  $message .= "\n\nThe IETF Secretariat.\n\n";
  $message = format_comment_text($message);
  #schedule notification here
  my ($subject_q,$to_val,$cc_val,$body) = db_quote($subject,$requestor,$cc_list,$message);
  $to_val =~ s/;/,/g;
  $cc_val =~ s/;/,/g;
  db_update("insert into scheduled_announcements (scheduled_by,scheduled_date,scheduled_time,subject,to_val,from_val,cc_val,body,first_q) values ('IETFDEV',current_date,current_time,$subject_q,$to_val,'IETF Secretariat <ietf-secretariat-reply\@ietf.org>',$cc_val,$body,1)");
  my $dir_name = ($devel_mode)?"devel":"secretariat";
  my $id=db_select("select max(id) from scheduled_announcements");
  ($requestor,$cc_list) = html_bracket($requestor,$cc_list);
  $cc_list =~ s/,/\n/g;
  return qq{<pre>
To: $requestor
Cc: $cc_list
Subject: $subject

$message

</pre>
<br>
<a href="https://datatracker.ietf.org/cgi-bin/$dir_name/message_scheduler.cgi?command=view_detail&id=$id">View/Edit Message</a><br>
};
}

 
