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
use GEN_DBUTIL_NEW;
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
init_database($dbname);
$dbh=get_dbh();
my $q = new CGI;
$style_url="https://www1.ietf.org/css/base.css";
$program_name = "message_scheduler.cgi";
$program_title = "IETF Secretariat Message Scheduler";
$program_title .= " db: $dbname" if ($devel_mode);
$current_user = $ENV{REMOTE_USER};
$current_user = $q->param("current_user") unless my_defined($current_user);
$table_header = qq{<table cellpadding="3" cellspacing="3" border="0" width="800" bgcolor="#cccccc">
};
$form_header_post = qq{<form action="$program_name" method="POST">
<input type="hidden" name="current_user" value="$current_user">
};
$form_header_post2 = qq{<form action="$program_name" method="POST" name="form_post2">};
$form_header_post3 = qq{<form action="$program_name" method="POST" name="form_post3">};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">
<input type="hidden" name="current_user" value="$current_user">
};
$form_header_get = qq{<form action="$program_name" method="GET" name="form_get">};
$asterisk = "<font color=\"red\"><b>*</b></font>";
$html_top = qq|
<link rel="stylesheet" type="text/css" href="$style_url" />
<h2><center>$program_title <font color="red"><i>$mode_text</i></font></center></h2>
Login: $current_user
<br><br>
|;
$html_bottom = qq{
</body>
</html>
};

$html_body = get_html_body($q);
$dbh->disconnect();
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
   <input type="hidden" name="command" value="main_screen">
   <input type="submit" value="Main Menu">
   <input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true">
   </form>
   } if (my_defined($command) and $command ne "main_screen");
   return $html_txt;
}

sub main_screen {
  my @List_from = db_select_multiple($dbh,"select announced_from_id,announced_from_value from announced_from");
  my $from_list ;
  my $to_list;
  for my $array_ref (@List_from) {
    my ($id, $val) = @$array_ref;
    $from_list .= "<option value=\"$id\">$val</option>\n";
  }
                                                                                                    
  my @List_to = db_select_multiple($dbh,"select announced_to_id,announced_to_value from announced_to order by announced_to_id desc");
  for my $array_ref (@List_to) {
    my ($id, $val) = @$array_ref;
    $to_list .= "<option value=\"$id\">$val</option>\n";
  }
  my $current_scheduled = "";
  my @currentList = db_select_multiple($dbh,"select subject,scheduled_by,to_be_sent_date,to_be_sent_time,id,note from scheduled_announcements where mail_sent=0 order by to_be_sent_date,to_be_sent_time");
  for my $array_ref (@currentList) {
    my ($subject,$scheduled_by,$to_be_sent_date,$to_be_sent_time,$id,$note) = @$array_ref;
    $to_be_sent_date = "Next Rsync" if ($to_be_sent_date eq "0000-00-00"  or $to_be_sent_date eq "");
    $to_be_sent_time = "Next Rsync" unless my_defined($to_be_sent_time); 
    $current_scheduled .= qq{<tr><td><li> <a href="$program_name?command=view_detail&id=$id">$subject</a></td><td>$scheduled_by</td><td>$to_be_sent_date</td><td>$to_be_sent_time</td><td><font color="red"><b>$note</b></font></td></tr>
};
  }
  return qq{
<h2>Add a new message to be scheduled</h2>
$form_header_post
<input type="hidden" name="command" value="confirm">
$table_header
<tr><td colspan="2"><b>DATE AND TIME ARE RECOMMENDED!  PLEASE DO NOT LEAVE BLANK!</b></td></tr>
<tr>
  <td>To be sent date (yyyy-mm-dd)</td>
  <td><input type="text" name="to_be_sent_date" size="25" value=""></td>
</tr>
<tr>
  <td>To be sent time (hh:mm) Pacific time</td>
  <td><input type="text" name="to_be_sent_time" size="25" value=""></td>
</tr>
<tr><td colspan="2"><hr></td></tr>
<tr>
  <td>From</td>
  <td><select name="from_id">$from_list</select></td>
</tr>
<tr>
  <td>Other From</td>
  <td><input type="text" name="other_from" size="50" value=""></td>
</tr>
<tr>
  <td>To</td>
  <td><select name="to_id">$to_list</select></td>
</tr>
<tr>
  <td>Other To</td>
  <td><input type="text" name="other_to" size="50" value=""></td>
</tr>
<tr>
  <td>Cc</td>
  <td><input type="text" name="cc_val" size="50" value=""></td>
</tr>
<tr><td>BCC: </td><td><input type="text" size="55" name="bcc_val"> <b>(separated by a comma)</b></td></tr>
<tr>
  <td>Reply To</td>
  <td><input type="text" name="replyto" size="50" value=""></td>
</tr>
<tr>
  <td>Subject</td>
  <td><input type="text" name="subject" size="50" value=""></td>
</tr>
<tr valign="top">
  <td>Message</td>
  <td><textarea name="body" rows="15" cols="74"></textarea></td>
</tr>
</table>
<input type="submit" value=" Submit "><br>
</form>
<hr>
<h2>Currently Scheduled Messages</h2>
<table border=0>
<tr><td width="350"><b>Message Subject</td><td width="110"><b>Scheduled by</td>
<td width="120"><b>To be sent date</td><td width="120"><b>To be sent time</td><td></td></tr>
$current_scheduled
</table>
<hr>
<h2><a href="$program_name?command=sent_messages&recent=1">Recent Sent Messages</a></h2>
<h2><a href="$program_name?command=sent_messages">All Sent Messages</a></h2>

<br><br>
};
}
sub sent_messages {
  my $q=shift;
  my $sent_list = "";
  my $extra="";
  if (defined($q->param("recent"))) {
    my $from_date=db_select($dbh,"select date_add(current_date, interval -5 day)");
    $extra = " and actual_sent_date > '$from_date' ";
  }
  my @sentList = db_select_multiple($dbh,"select subject,scheduled_by,actual_sent_date,actual_sent_time,id,note from scheduled_announcements where mail_sent=1 $extra order by actual_sent_date desc,actual_sent_time desc");
  for my $array_ref (@sentList) {
    my ($subject,$scheduled_by,$actual_sent_date,$actual_sent_time,$id,$note) = @$array_ref;
    $sent_list .= qq{<tr><td><li> <a href="$program_name?command=view_detail&id=$id">$subject</a></td><td>$scheduled_by</td><td>$actual_sent_date</td><td>$actual_sent_time</td><td><font color="red"><b>$note</b></font></td></tr>
};
  }

  return qq{
<h2>Sent Messages</h2>
<table border=0>
<tr><td width="350"><b>Message Subject</td><td width="110"><b>Scheduled by</td>
<td width="120"><b>Actual sent date</td><td width="120"><b>Actual sent time</td><td></td></tr>
$sent_list
</table>
                                                                                                 
<br><br>
};
}

sub confirm {
  my $q=shift;
  my $error_message = "";
  my $to_id=$q->param("to_id");
  my $from_id=$q->param("from_id");
  my $cc_val=$q->param("cc_val");
  my $bcc_val=$q->param("bcc_val");
  my $subject=$q->param("subject");
  my $body=$q->param("body");
  my $replyto=$q->param("replyto");
  my $to_be_sent_date=$q->param("to_be_sent_date");
  my $to_be_sent_time=$q->param("to_be_sent_time");
  my $to_val=($to_id == 99)?$q->param("other_to"):db_select($dbh,"select announced_to_email from announced_to where announced_to_id=$to_id");
  my $from_val=($from_id == 99)?$q->param("other_from"):db_select($dbh,"select announced_from_value from announced_from where announced_from_id=$from_id");
  $error_message .= "Blank <b>From Email Address</b><br>\n" unless my_defined($from_val);
  $error_message .= "Invalid <b>To Email Address</b><br>\n" unless is_valid_email($to_val);
  $error_message .= "Blank <b>Subject</b><br>\n" unless my_defined($subject);
  $error_message .= "Empty <b>Message Body</b><br>\n" unless my_defined($body);
  error ($q,$error_message) if my_defined($error_message);
  $body = format_comment_text($body,74);
  my ($to_be_sent_date_q,$to_be_sent_time_q,$subject_q,$to_val_q,$from_val_q,$cc_val_q,$body_q,$bcc_val_q) = db_quote($to_be_sent_date,$to_be_sent_time,$subject,$to_val,$from_val,$cc_val,$body,$bcc_val);
  db_update($dbh,"insert into scheduled_announcements_temp (to_be_sent_date,to_be_sent_time,subject,to_val,from_val,cc_val,body,replyto,bcc_val) values ($to_be_sent_date_q,$to_be_sent_time_q,$subject_q,$to_val_q,$from_val_q,$cc_val_q,$body_q,'$replyto',$bcc_val_q)");
  $to_be_sent_date = "Next Rsync" unless my_defined($to_be_sent_date);
  $to_be_sent_time = "Next Rsync" unless my_defined($to_be_sent_time);
  $cc_val = "Not entered" unless my_defined($cc_val);
  $bcc_val = "Not entered" unless my_defined($bcc_val);
  my $temp_id=db_select($dbh,"select max(id) from scheduled_announcements_temp");
  return qq{
<h2>Confirmation</h2>
$form_header_post
<input type="hidden" name="command" value="do_add">
<input type="hidden" name="temp_id" value="$temp_id">
$table_header
<tr>
  <td>To be sent date</td>
  <td>$to_be_sent_date</td>
</tr>
<tr>
  <td>To be sent time</td>
  <td>$to_be_sent_time</td>
</tr>
<tr>
  <td>From</td>
  <td>$from_val</td>
</tr>
<tr>
  <td>To</td>
  <td>$to_val</td>
</tr>
<tr>
  <td>Cc</td>
  <td>$cc_val</td>
</tr>
<tr>
  <td>Bcc</td>
  <td>$bcc_val</td>
</tr>

<tr>
  <td>Reply To</td>
  <td>$replyto</td>
</tr>
<tr>
  <td>Subject</td>
  <td>$subject</td>
</tr>
<tr>
  <td>Message</td>
  <td><pre>$body</pre></td>
</tr>
</table>
<input type="submit" value=" Submit ">
</form>
<br><br>
};
}

sub do_add {
  my $q=shift;
  my $temp_id=$q->param("temp_id");
  my ($to_be_sent_date,$to_be_sent_time,$subject,$to_val,$from_val,$cc_val,$body,$replyto,$bcc_val) = db_select($dbh,"select to_be_sent_date,to_be_sent_time,subject,to_val,from_val,cc_val,body,replyto,bcc_val from scheduled_announcements_temp where id=$temp_id");
  ($replyto,$to_be_sent_date,$to_be_sent_time,$subject,$to_val,$from_val,$cc_val,$body,$bcc_val) = db_quote($replyto,$to_be_sent_date,$to_be_sent_time,$subject,$to_val,$from_val,$cc_val,$body,$bcc_val);
  my $first_q = (my_defined($to_sent_time) and my_defined($to_sent_date))?0:1;
  db_update($dbh,"insert into scheduled_announcements (to_be_sent_date,to_be_sent_time,scheduled_by,scheduled_date,scheduled_time,subject,to_val,from_val,cc_val,body,first_q,replyto,bcc_val) values ($to_be_sent_date,$to_be_sent_time,'$current_user',current_date,current_time,$subject,$to_val,$from_val,$cc_val,$body,$first_q,$replyto,$bcc_val)");
  return qq{
<h2>A new message has been scheduled successfully</h2>
<a href="$program_name">Back to first screen</a>
<br><br>
};


}

sub view_detail {
  my $q=shift;
  my $id=$q->param("id");
  my ($mail_sent,$to_be_sent_date,$to_be_sent_time,$scheduled_by,$scheduled_date,$scheduled_time,$subject,$to_val,$from_val,$cc_val,$body,$actual_sent_date,$actual_sent_time,$replyto,$bcc_val) = db_select($dbh,"select mail_sent,to_be_sent_date,to_be_sent_time,scheduled_by,scheduled_date,scheduled_time,subject,to_val,from_val,cc_val,body,actual_sent_date,actual_sent_time,replyto,bcc_val from scheduled_announcements where id=$id");
  $to_be_sent_date = "Next Rsync" if ($to_be_sent_date eq "0000-00-00" or $to_be_sent_date eq "");
  $to_be_sent_time = "Next Rsync" unless my_defined($to_be_sent_time);
  $cc_val = "<i>Not Entered</i>" unless my_defined($cc_val);
  $bcc_val = "<i>Not Entered</i>" unless my_defined($bcc_val);
  ($subject,$to_val,$from_val,$cc_val,$body,$replyto,$bcc_val) = html_bracket($subject,$to_val,$from_val,$cc_val,$body,$replyto,$bcc_val);
  my $html_txt=qq{
<h2>View Detail: <i>$subject</i></h2>
$table_header
<tr>
  <td width="120">To be sent date</td><td>$to_be_sent_date</td>
</tr>
<tr>
  <td>To be sent time</td><td>$to_be_sent_time</td>
</tr>
<tr>
  <td>Scheduled by</td><td>$scheduled_by at $scheduled_time on $scheduled_date</td>
</tr>
<tr><td colspan="2"><hr></td></tr>
<tr><td>From</td><td>$from_val</td></tr>
<tr><td>To</td><td>$to_val</td></tr>
<tr><td>Cc</td><td>$cc_val</td></tr>
<tr><td>Bcc</td><td>$bcc_val</td></tr>
<tr><td>Reply To</td><td>$replyto</td></tr>
<tr><td valign="top">Message</td><td><pre>$body</pre></td></tr>
};
  if ($mail_sent) {
    $html_txt .= qq{<tr><td>Actual Sent</td><td>Sent at $actual_sent_time on $actual_sent_date</td></tr>
</table><br>
};
  } else {
    $html_txt .= qq{<tr>
<td align="center" colspan="2">
$table_header
<tr><td>
$form_header_post
<input type="hidden" name="command" value="edit">
<input type="hidden" name="id" value="$id">
<input type="submit" value= " Edit ">
</form> 
    </td>
    <td>
$form_header_post
<input type="hidden" name="command" value="send_now">
<input type="hidden" name="id" value="$id">
<input type="submit" value= " Send Now " onClick="return window.confirm('Are you sure?');">
</form>
</td>
<td>
$form_header_post
<input type="hidden" name="command" value="mark_as_sent">
<input type="hidden" name="id" value="$id">
<input type="submit" name="mark_sent" value= " Mark as Sent " onClick="return window.confirm('Are you sure?');">
<input type="submit" name="mark_delete" value= " Delete " onClick="return window.confirm('Are you sure?');">
</form>
</td></tr>

</table>
</td></tr></table><br>
};
  }
  return $html_txt;
}
sub edit {
  my $q=shift;
  my $id=$q->param("id");
  my ($to_be_sent_date,$to_be_sent_time,$subject,$to_val,$from_val,$cc_val,$body,$replyto,$bcc_val) = db_select($dbh,"select to_be_sent_date,to_be_sent_time,subject,to_val,from_val,cc_val,body,replyto,bcc_val from scheduled_announcements where id=$id"); 

  return qq{
$form_header_post
$table_header
<input type="hidden" name="command" value="do_edit">
<input type="hidden" name="id" value="$id">
<tr><td>To be sent date<br>(yyyy-mm-dd)</td><td><input type="text" name="to_be_sent_date" value="$to_be_sent_date">
</tr>
<tr><td>To be sent time<br>(hh:mm)</td><td><input type="text" name="to_be_sent_time" value="$to_be_sent_time"></tr>
<tr><td>From</td><td><input type="text" name="from_val" value="$from_val" size="95"></tr>
<tr><td>To</td><td><input type="text" name="to_val" value="$to_val" size="95"></tr>
<tr><td>Cc</td><td><input type="text" name="cc_val" value="$cc_val" size="95"></tr>
<tr><td>Cc</td><td><input type="text" name="bcc_val" value="$bcc_val" size="95"></tr>
<tr><td>Reply To</td><td><input type="text" name="replyto" value="$replyto" size="95"></tr>
<tr><td>Subject</td><td><input type="text" name="subject" value="$subject" size="95"></tr>
<tr><td>Message</td><td><textarea name="body" cols="72" rows="10">$body</textarea></td>
</tr></table>
<input type="submit" value="Submit"><input type="reset" value="Reset">
</form>
<br><br>
};
}

sub do_edit {
  my $q=shift;
  my $id=$q->param("id");
  my $to_be_sent_date=$q->param("to_be_sent_date");
  my $to_be_sent_time=$q->param("to_be_sent_time");
  my $subject=$q->param("subject");
  my $to_val=$q->param("to_val");
  my $from_val=$q->param("from_val");
  my $cc_val=$q->param("cc_val");
  my $bcc_val=$q->param("bcc_val");
  my $replyto=$q->param("replyto");
  my $body=$q->param("body");
  ($subject,$to_val,$from_val,$cc_val,$body,$replyto,$bcc_val) = de_html_bracket($subject,$to_val,$from_val,$cc_val,$body,$replyto,$bcc_val);
  ($subject,$to_val,$from_val,$cc_val,$body,$to_be_sent_date,$to_be_sent_time,$bcc_val) = db_quote($subject,$to_val,$from_val,$cc_val,$body,$to_be_sent_date,$to_be_sent_time,$bcc_val);
  if (db_update($dbh,"update scheduled_announcements set to_be_sent_date=$to_be_sent_date,to_be_sent_time=$to_be_sent_time,subject=$subject,to_val=$to_val,from_val=$from_val,cc_val=$cc_val,body=$body,replyto='$replyto',bcc_val=$bcc_val where id=$id")) {
    my $note=db_select($dbh,"select note from scheduled_announcements where id=$id");
    my ($current_date,$current_time) = db_select($dbh,"select current_date,current_time");
    $note .= "<br>Modified by $current_user ($current_date, $current_time)";
    $note = db_quote($note);
    db_update($dbh,"update scheduled_announcements set note=$note where id=$id");
  } else {
    error ($q,"Could not update the message");
  } 
  return view_detail($q);
}
sub mark_as_sent {
  my $q=shift;
  my $id=$q->param("id");
  my $msg="Marked as SENT by $current_user";
  $msg = "Deleted by $current_user" if defined($q->param("mark_delete"));
  db_update($dbh,"update scheduled_announcements set mail_sent=1,actual_sent_date=current_date,actual_sent_time='forced by $current_user', note='$msg' where id=$id");
  return view_detail($q);
}

sub send_now {
  my $q=shift;
  my $id=$q->param("id");
  my ($subject,$from_val,$to_val,$cc_val,$body,$content_type,$replyto,$bcc_val) = db_select($dbh,"select subject,from_val,to_val,cc_val,body,content_type,replyto,bcc_val from scheduled_announcements where id=$id");
  $to_val =~ s/;/,/g;
  $cc_val =~ s/;/,/g;
  $bcc_val =~ s/;/,/g;
  my $extra = (my_defined($replyto))?"reply-to: $replyto^":"";
  $extra .= (my_defined($bcc_val))?"bcc: $bcc_val^":"";
  $body =~ s/^\.//mg;
  my $html_txt = "";
#  $html_txt = qq{
#<pre>
#Subject: $subject
#From: $from_val
#To: $to_val
#Cc: $cc_val
#--------------------------------
#$body
#</pre>
#};
#return $html_txt;
  if (send_mail($program_name,$current_user,$to_val,$from_val,$subject,$body,$cc_val,$extra,$content_type)) {
    $html_txt = "<h2>Message has been sent successfully</h2>\n";
    db_update($dbh,"update scheduled_announcements set mail_sent=1,actual_sent_date=current_date,actual_sent_time=current_time where id=$id");
  } else {
    $html_txt = "<font color=\"red\"><h2>Unknown Error Occurred: Message was not sent</h2></font>\n";
  }
  return $html_txt;
}


