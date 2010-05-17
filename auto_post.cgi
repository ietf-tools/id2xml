#!/usr/bin/perl
##########################################################################
#      Copyright (c) 2006 Neustar Secretariat Services, Inc.
#
#      Program: Automated I-D Posting Tool
#      Author : Sang-Hee Lee, Neustar Secretariat Services
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

$host=$ENV{SCRIPT_NAME};
$remote=$ENV{REMOTE_HOST};
$http_host=$ENV{HTTP_HOST};
$devel_mode = ($host =~ /devel/)?1:0;
$qa_mode=0;
$dbname = "ietf";
$mode_text = "";
$tool_url=($devel_mode)?"/cgi-bin/devel/public/idst":"/idst";
$wg_tool_url=($devel_mode)?"/cgi-bin/devel/wg/wg_init_rev_approval.cgi":"/cgi-bin/wg/wg_init_rev_approval.cgi";
$sec_tool_url=($devel_mode)?"/cgi-bin/devel/secretariat/init_rev_approval.cgi":"/cgi-bin/secretariat/init_rev_approval.cgi";
if ($devel_mode) {
  $qa_mode = ($http_host =~ /datatracker/)?1:0;
  $rUser = $ENV{REMOTE_USER};
  $dbname=($qa_mode)?"ietf_qa":"test_idst";
  $mode_text = ($qa_mode)?"QA Mode":"Development Mode";
}
init_database($dbname);
$dbh = get_dbh();
$q = new CGI;
$first_cutoff=0;
### Check Cut Off dates ###
my $c_days = db_select($dbh,"select to_days(current_date)");
my $first_cut_off_days = db_select($dbh,"select to_days(id_date) from id_dates where id=1");
my $second_cut_off_days = db_select($dbh,"select to_days(id_date) from id_dates where id=2");
my $ietf_monday_days = db_select($dbh,"select to_days(id_date) from id_dates where id=3");
my $first_cut_off = db_select($dbh,"select id_date from id_dates where id=1");
my $second_cut_off = db_select($dbh,"select id_date from id_dates where id=2");
my $ietf_monday = db_select($dbh,"select id_date from id_dates where id=3");
my $c_hour = db_select($dbh,"select hour(current_time)");
my $temp_num = 0;
if ($c_days >= $first_cut_off_days and $c_days < $second_cut_off_days) { # First cut off
  if ($c_days == $first_cut_off_days and $c_hour < 17) { #Still OK
    $cutoff_msg = "The pre-meeting cutoff date for new documents (i.e., version -00 Internet-Drafts) is $first_cut_off at 5 PM (ET). You will not be able to submit a new document after this time until $ietf_monday, at midnight";
  } else { # No more 00 submission
    $cutoff_msg = "The pre-meeting cutoff date for new documents (i.e., version -00 Internet-Drafts) was $first_cut_off at 5 PM (ET). You will not be able to submit a new document until $ietf_monday, at midnight.<br>You can still submit a version -01 or higher Internet-Draft until 5 PM (ET), $second_cut_off.";
    $first_cutoff=1;
  }
} elsif ($c_days >= $second_cut_off_days and $c_days < $ietf_monday_days) { # Second cut off
  if ($c_days == $second_cut_off_days and $c_hour < 17) { #No 00, ok for update
    $cutoff_msg="The pre-meeting cutoff date for new documents (i.e., version -00 Internet-Drafts) was $first_cut_off at 5 PM (ET). You will not be able to submit a new document until $ietf_monday, at midnight.<br>The I-D submission tool will be shut down at 5 PM (ET) today, and reopened at midnight (ET), $ietf_monday";
    $first_cutoff=1;
  } else { #complete shut down of tool
    error_idst($q,"The cut off time for the I-D submission was 5 PM (ET), $second_cut_off.<br>The I-D submission tool will be reopened at midnight, $ietf_monday");
  }
}
$cutoff_msg = "<p><b>$cutoff_msg</b></p>\n" if (my_defined($cutoff_msg));

### End Check Cut Off dates ###

$user_email = ($devel_mode)?db_select($dbh,"select email_address from email_addresses a, iesg_login b where login_name='$rUser' and a.person_or_org_tag=b.person_or_org_tag and email_priority=1"):"";

#$q = new CGI;
$style_url="https://www1.ietf.org/css/base.css";
$program_name = "auto_post.cgi";
$program_title = "IETF Internet-Draft Submission Tool";
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
$sql_injection_warning="Possible SQL Injection detected.";
$html_body = get_html_body();
print $q->header("text/html"),
      $q->start_html(-title=>$program_title),
      $q->p($html_body),
      $q->end_html;

$dbh->disconnect();
exit;

sub get_html_body {
   my $command = $q->param("command");
   my $submission_id=$q->param("submission_id");
   error_idst ($q,$sql_injection_warning) if check_sql_injection ($command,$submission_id);
   my $html_txt = "";
   unless (my_defined($command)) {
     $html_txt .= main_screen();
   } else {
     return sub_error (110,$submission_id) unless ($remote eq "stiedprstage1" or $remote eq "datatracker.ietf.org");
     my $func = "$command()";
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
  my $auth_key=$q->param("auth_key");
  my $submission_id=$q->param("submission_id");
  error_idst ($q,$sql_injection_warning) if check_sql_injection ($submission_id);
  my $status_id=db_select($dbh,"select status_id from id_submission_detail where submission_id=$submission_id");
  #return sub_error(107,$submission_id) unless ($status_id==4 or $status_id == 11);
  return sub_error(107,$submission_id) if ($status_id < 0 or $status_id > 100);
  my $matched=db_select_secure($dbh,"select count(*) from id_submission_detail where submission_id=$submission_id and auth_key=?",$auth_key);
  return sub_error (105,$submission_id) unless $matched;
  #Check WG Init version approval
  $sql = "select filename,submitter_tag,auth_key,group_acronym_id,revision,sub_email_priority from id_submission_detail where submission_id = ?";
  ($filename,$submitter_tag,$auth_key,$group_acronym_id,$revision,$sub_email_priority) = db_select_secure ($dbh,$sql,$submission_id);
  $sub_email_priority=1 unless my_defined($sub_email_priority);
  $sql = "select approved_status from id_approved_detail where filename='$filename'";
  $approved_status = db_select($dbh,$sql);
  if ($approved_status == 1 or $revision ne "00" or $group_acronym_id == 1027) {
    return populate_sec_table($submission_id); 
  } else {  #WG Init approval needed. Send messages to all WG chairs.
    db_update($dbh,"update id_submission_detail set status_id=10 where submission_id=$submission_id");
    my $submitter_name=get_name($submitter_tag);
    my $submitter_email=get_email($submitter_tag);
    my $group_acronym=db_select($dbh,"select acronym from acronym where acronym_id=$group_acronym_id");
    $msg = db_select($dbh,"select id_approval_request_msg from id_submission_env");
    $msg =~ s/##submitter_name##/$submitter_name/g;
    $msg =~ s/##submitter_email##/$submitter_email/g;
    $msg =~ s/##filename##/$filename/g;
    my $email="$group_acronym-chairs\@tools.ietf.org";
    $to_email=($devel_mode)?$user_email:$email;
    $from="IETF I-D Submission Tool <idsubmission\@ietf.org>";
    $subject="Initial Version Approval Request for $filename";
    if ($qa_mode or !$devel_mode) {
      send_mail($program_name,"IDST",$to_email,$from,$subject,$msg);
      return qq{
<i>Processing...</i>
<script language="javascript">
window.location="$tool_url/status.cgi?submission_id=$submission_id";
</script>
};

    } else {
      print $q->header("text/html");
      print $q->start_html();
      print qq{
<pre>
$msg
</pre>
<a href="$tool_url/status.cgi?submission_id=$submission_id">Status</a><br>
</body>
</html>
};
      exit;
    }
  }
}

sub populate_sec_table {
  my $submission_id=shift;
  my ($id_document_tag,$id_document_name,$group_acronym_id,$filename,$revision,$revision_date,$file_type,$txt_page_count,$abstract) = db_select($dbh,"select temp_id_document_tag,id_document_name,group_acronym_id,filename,revision,submission_date,file_type,txt_page_count,abstract from id_submission_detail where submission_id=$submission_id");
  my $id_document_key=uc($id_document_name);
  ($id_document_name,$id_document_key,$filename,$revision,$revision_date,$file_type,$abstract) = db_quote($id_document_name,$id_document_key,$filename,$revision,$revision_date,$file_type,$abstract);
  if ($revision eq "'00'") { #Insert new record into the table
    my $exist=db_select($dbh,"select count(id_document_tag) from internet_drafts where filename=$filename");
    error ($q,"There is a Unique Key Violation occurred during this process") if $exist;
    db_update($dbh,"insert into internet_drafts (id_document_name,id_document_key,group_acronym_id,filename,revision,revision_date,file_type,txt_page_count,abstract,status_id,intended_status_id,start_date,last_modified_date) values ($id_document_name,$id_document_key,$group_acronym_id,$filename,$revision,$revision_date,$file_type,$txt_page_count,$abstract,1,8,current_date,current_date)");  
   $id_document_tag=db_select($dbh,"select max(id_document_tag) from internet_drafts");
  } else { # Update the table
#error($q,,"update internet_drafts set id_document_name=$id_document_name, id_document_key=$id_document_key,revision=$revision,revision_date=$revision_date,file_type=$file_type,txt_page_count=$txt_page_count,abstract=$abstract,status_id=1,expired_tombstone=0, last_modified_date=current_date where id_document_tag=$id_document_tag");
    db_update($dbh,"update internet_drafts set id_document_name=$id_document_name, id_document_key=$id_document_key,revision=$revision,revision_date=$revision_date,file_type=$file_type,txt_page_count=$txt_page_count,abstract=$abstract,status_id=1,expired_tombstone=0, last_modified_date=current_date where id_document_tag=$id_document_tag");

  db_update($dbh,"delete from id_authors where id_document_tag=$id_document_tag");
  db_update($dbh,"delete from email_addresses where email_priority=$id_document_tag");
  }
  my @List_authors=db_select_multiple($dbh,"select first_name,last_name,email_address,author_order from temp_id_authors where submission_id=$submission_id");
  for my $array_ref (@List_authors) {
    my ($first_name,$last_name,$email_address,$author_order) = @$array_ref;
    ($first_name,$last_name,$email_address) = db_quote($first_name,$last_name,$email_address);
    my $person_or_org_tag=db_select($dbh,"select person_or_org_tag from email_addresses where email_address=$email_address");
    unless ($person_or_org_tag) {  # Email address does not exist. create new person_or_org_tag
      db_update($dbh,"insert into person_or_org_info (first_name,first_name_key,last_name,last_name_key,date_modified,date_created,modified_by,created_by) values ($first_name,$first_name,$last_name,$last_name,current_date,current_date,'IDST','IDST')");
      $person_or_org_tag=db_select($dbh,"select max(person_or_org_tag) from person_or_org_info");
      db_update($dbh,"insert into email_addresses (person_or_org_tag,email_type,email_priority,email_address) values ($person_or_org_tag,'Primary',1,$email_address)");
    }

    db_update($dbh,"insert into email_addresses (person_or_org_tag,email_type,email_priority,email_address) values ($person_or_org_tag,'I-D',$id_document_tag,$email_address)");
    db_update($dbh,"insert into id_authors (id_document_tag,person_or_org_tag,author_order) values ($id_document_tag,$person_or_org_tag,$author_order)");
  }
  db_update($dbh,"update id_submission_detail set status_id=7 where submission_id=$submission_id");
  return schedule_id_announcement($submission_id); 
}

sub schedule_id_announcement {
  my $submission_id=shift;
  my ($id_document_tag,$id_document_name,$filename,$revision,$txt_page_count,$revision_date,$abstract,$group_acronym_id)=db_select($dbh,"select temp_id_document_tag,id_document_name,filename,revision,txt_page_count,submission_date,abstract,group_acronym_id from id_submission_detail where submission_id=$submission_id");
  $abstract = format_comment_text($abstract,74);
  my @List_authors=db_select_multiple($dbh,"select first_name, last_name from temp_id_authors where submission_id=$submission_id order by author_order");
  my $num_authors=$#List_authors + 1;
  my $authors="";
  my $wgMail="";
  for my $array_ref (@List_authors) {
    my ($first_name,$last_name) = @$array_ref;
    $first_name = uc(substr($first_name,0,1));
    $authors .= "$first_name. $last_name, ";
    if ($num_authors >2) {
      $authors .= "et al.";
      last;
    }
  }
  if ($num_authors < 3) {
    chop($authors);
    chop($authors);
  }
  $cc_val="";
  unless ($group_acronym_id==1027) {
    my $group_name=db_select($dbh,"select name from acronym where acronym_id=$group_acronym_id");
    $cc_val=db_select($dbh,"select email_address from groups_ietf where group_acronym_id=$group_acronym_id");
    $wgMail = "\nThis draft is a work item of the $group_name Working Group of the IETF.\n";
  }
  my ($current_date,$current_time) = db_select($dbh,"select current_date,current_time");
  $current_time =~ s/://g;
  my $body = db_select($dbh,"select id_action_announcement from id_submission_env");
  $body =~ s/\^\^\^/\t/g;
  $body =~ s/##id_document_name##/$id_document_name/g;
  $body =~ s/##authors##/$authors/g;
  $body =~ s/##filename##/$filename/g;
  $body =~ s/##revision##/$revision/g;
  $body =~ s/##txt_page_count##/$txt_page_count/g;
  $body =~ s/##revision_date##/$revision_date/g;
  $body =~ s/##current_date##/$current_date/g;
  $body =~ s/##current_time##/$current_time/g;
  $body =~ s/##abstract##/$abstract/g;
  $body =~ s/##wgMail##/$wgMail/g;
  my $body_q=db_quote($body);
  $content_type = "Multipart/Mixed; Boundary=\"NextPart\"";
  #db_update($dbh,"insert into scheduled_announcements (scheduled_by,to_be_sent_date,to_be_sent_time,scheduled_date,scheduled_time,subject,to_val,from_val,cc_val,body) values ('IDST',current_date,'00:00',current_date,current_time,'I-D Action:$filename-$revision.txt','michael.lee\@neustar.biz','Internet-Drafts\@ietf.org','',$body_q)");
  db_update($dbh,"insert into scheduled_announcements (scheduled_by,to_be_sent_date,to_be_sent_time,scheduled_date,scheduled_time,subject,to_val,from_val,cc_val,body,content_type) values ('IDST',current_date,'00:00',current_date,current_time,'I-D Action:$filename-$revision.txt','i-d-announce\@ietf.org','Internet-Drafts\@ietf.org','$cc_val',$body_q,'$content_type')");
  db_update($dbh,"update id_submission_detail set status_id=8 where submission_id=$submission_id");
  my $tracked=db_select($dbh,"select count(*) from id_internal where id_document_tag=$id_document_tag and rfc_flag=0 and cur_state < 100"); # cur_state 100 is a new state that to change a existing ID Tracker document back to 'ID Exist' state
  schedule_new_version_notification($submission_id) if ($tracked);
  return sync_docs($submission_id);

}

sub schedule_new_version_notification {
  my $submission_id=shift;
  my ($id_document_tag,$id_document_name,$filename,$revision,$txt_page_count,$revision_date,$abstract,$group_acronym_id)=db_select($dbh,"select temp_id_document_tag,id_document_name,filename,revision,txt_page_count,submission_date,abstract,group_acronym_id from id_submission_detail where submission_id=$submission_id");
  my $sendTo = db_select($dbh,"select state_change_notice_to from id_internal where id_document_tag=$id_document_tag and rfc_flag=0");
  $sendTo .= ",";
  $sendTo .= db_select($dbh,"select email_address from email_addresses a, id_internal b, iesg_login c where b.id_document_tag=$id_document_tag and rfc_flag=0 and b.job_owner=c.id and c.person_or_org_tag = a.person_or_org_tag and a.email_priority=1");
  my @List_discuss=db_select_multiple($dbh,"select email_address from email_addresses a, ballots b, id_internal c,iesg_login d where c.id_document_tag=$id_document_tag and c.ballot_id=b.ballot_id and b.ad_id=d.id and d.person_or_org_tag=a.person_or_org_tag and a.email_priority=1 and b.discuss =1 and d.user_level=1");
  for my $array_ref (@List_discuss) {
    my ($email) = @$array_ref;
    $sendTo .= ",$email";
  }
  my $msg="";
#Add comment to ID Tracker
  db_update($dbh,"insert into document_comments (document_id,rfc_flag,public_flag,comment_date,comment_time,version,comment_text) values ($id_document_tag,0,1,current_date,current_time,'$revision','New version available')");

  my $cur_sub_state_id=db_select($dbh,"select cur_sub_state_id from id_internal where id_document_tag=$id_document_tag and rfc_flag=0");
  if ($cur_sub_state_id == 5) {
    $msg="Sub state has been changed to AD Follow up from New Id Needed";
    db_update($dbh,"insert into document_comments (document_id,rfc_flag,public_flag,comment_date,comment_time,version,comment_text) values ($id_document_tag,0,1,current_date,current_time,'$revision','$msg')");
    db_update($dbh,"update id_internal set cur_sub_state_id=2,prev_sub_state_id=5 where id_document_tag=$id_document_tag and rfc_flag=0");
  }

  my $body = qq{New version (-$revision) has been submitted for $filename-$revision.txt.
http://www.ietf.org/internet-drafts/$filename-$revision.txt
$msg

Diff from previous version:
http://tools.ietf.org/rfcdiff?url2=$filename-$revision

IETF Secretariat.
};
  $body=db_quote($body);
  db_update($dbh,"insert into scheduled_announcements (scheduled_by,to_be_sent_date,to_be_sent_time,scheduled_date,scheduled_time,subject,to_val,from_val,cc_val,body) values ('IDST',current_date,'00:00',current_date,current_time,'New Version Notification - $filename-$revision.txt','$sendTo','Internet-Draft\@ietf.org','',$body)");
  db_update($dbh,"update id_submission_detail set status_id=9 where submission_id=$submission_id");
  return 1;
}

sub sync_docs {
  my $submission_id=shift;
  my ($filename,$revision) = db_select($dbh,"select filename,revision from id_submission_detail where submission_id=$submission_id");
  my ($staging_path,$target_path_web,$target_path_ftp)=db_select($dbh,"select staging_path,target_path_web,target_path_ftp from id_submission_env");
    system "cp $staging_path/$filename-$revision.*  $target_path_web/";
  unlink while (<$staging_path/$filename-$revision.*>);
  db_update($dbh,"update id_submission_detail set status_id=-1 where submission_id=$submission_id");
  return notify_all_authors($submission_id);
}

sub notify_all_authors {
  my $submission_id=shift;
  ($submitter_tag,$sub_email_priority,$filename,$revision,$group_acronym_id,$id_document_name,$creation_date,$nop,$last_updated_date,$abstract,$comment_to_sec)=db_select($dbh,"select submitter_tag,sub_email_priority,filename,revision,group_acronym_id,id_document_name,creation_date,txt_page_count,last_updated_date,abstract,comment_to_sec from id_submission_detail where submission_id=$submission_id");
  my $cc_email="";
  if ($group_acronym_id==1027) {
    $group_acronym="Independent Submission";
  } else {
    $group_acronym = db_select($dbh,"select acronym from acronym where acronym_id=$group_acronym_id");
    #$cc_email = db_select($dbh,"select email_address from groups_ietf where group_acronym_id=$group_acronym_id");
    #$cc_email .= "," if my_defined($cc_email);
  }
  my $comment_to_sec_text = (my_defined($comment_to_sec))?"\nComment:\n$comment_to_sec":"";
  my $submitter_email=get_email($submitter_tag,$sub_email_priority);
  my $submitter_name=get_name($submitter_tag);
  my @List=db_select_multiple($dbh,"select email_address from temp_id_authors where submission_id=$submission_id");
  for my $array_ref (@List) {
    my ($email)=@$array_ref;
    $cc_email .= "$email,";
  }
  $cc_email =~ s/$submitter_email,//;
  $cc_email =~ s/,$//;
  $to_email=($devel_mode)?$user_email:$submitter_email;
  $from="IETF I-D Submission Tool <idsubmission\@ietf.org>";
  $subject="New Version Notification for $filename-$revision";
  $msg=qq{
A new version of I-D, $filename-$revision.txt has been successfully submitted by $submitter_name and posted to the IETF repository.

Filename:\t $filename
Revision:\t $revision
Title:\t\t $id_document_name
Creation_date:\t $creation_date
WG ID:\t\t $group_acronym
Number_of_pages: $nop

Abstract:
$abstract
                                                                                  
$comment_to_sec_text

The IETF Secretariat.

};
  if ($devel_mode) {
    $msg = qq{<Only for testing>
Following message will be sent to $submitter_name and cc'ed to $cc_email
</Only for testing>
$msg
};
    $cc_email="";
  }
  send_mail($program_name,"IDST",$to_email,$from,$subject,$msg,$cc_email)  if ($qa_mode or !$devel_mode);
  if (defined($q->param("from_wg"))) {
    print $q->redirect("$wg_tool_url?from_auto_post=1&submission_id=$submission_id");
    exit;
  }
  if (defined($q->param("from_sec"))) {
    print $q->redirect("$sec_tool_url?from_auto_post=1&submission_id=$submission_id");
    exit;
  }
  return qq{
<i>Processing...</i>
<script language="javascript">
window.location="$tool_url/status.cgi?submission_id=$submission_id";
</script>
};

}

sub sub_error {
  my $error_code=shift;
  my $submission_id=shift;
  db_update($dbh,"update id_submission_detail set status_id=$error_code where submission_id=$submission_id");
 return qq{
<i>Processing...</i>
<script language="javascript">
window.location="$tool_url/status.cgi?submission_id=$submission_id";
</script>
};

}



