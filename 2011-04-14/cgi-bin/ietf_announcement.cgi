#!/usr/bin/perl
##########################################################################
# Copyright © 2004 and 2003, Foretec Seminars, Inc.
##########################################################################

use lib '/a/www/ietf-datatracker/release';
use CGI;
use GEN_UTIL;
use GEN_DBUTIL_NEW;
use IETF;
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
$program_name = "ietf_announcement.cgi";

$rUser = $ENV{REMOTE_USER};

$loginid = (my_defined($rUser)?db_select($dbh,"select id from iesg_login where login_name = '$rUser'"):$q->param("loginid"));
$user_name = get_mark_by($loginid);
$login_name = db_select($dbh,"select login_name from iesg_login where id=$loginid");
$chairid=db_select($dbh,"select a.id from iesg_login a, chairs b where chair_name='IETF' and a.person_or_org_tag=b.person_or_org_tag");
$iab_chairid=db_select($dbh,"select a.id from iesg_login a, chairs b where chair_name='IAB' and a.person_or_org_tag=b.person_or_org_tag");

$nomcom_chair=db_select($dbh,"select a.id from iesg_login a, chairs b where chair_name='NomCom' and a.person_or_org_tag=b.person_or_org_tag");

$astorisk = "<font color=\"red\"><b>*</b></font> ";
$TEST_EMAIL = "Michael Lee <mlee\@foretec.com>";
#$TEST_EMAIL = "mlee\@foretec.com amyk\@foretec.com dinaras\@foretec.com bfuller\@foretec.com sweilnau\@foretec.com";
$table_header = qq{<table cellpadding="4" cellspacing="0" border="0">
};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">
<input type="hidden" name="loginid" value="$loginid">};
$form_header_main = qq{<form action="$program_name" method="POST" name="form_main">
<input type="hidden" name="loginid" value="$loginid">};
$form_header_get = qq{<form action="$program_name" method="GET" name="form_get">
<input type="hidden" name="loginid" value="$loginid">};
$html_top = qq|
<html>
<HEAD><TITLE>IETF Announcement Sender $mode_text</title>
<STYLE TYPE="text/css">
<!--
TD {text-decoration: none; color: #000000; font: 10pt verdana;}
body {
  margin:0;
  padding:0;
  font-family: Arial, sans-serif;
  font-size: 1.0em;
  font-style: normal;
  }
th {
  padding:6px 0px 10px 30px;
  line-height:1em;
  font-size: 12px;
  color: #333;
                                                                                                   
 }
/* Links
----------------------------------------------- */
a:link, a:visited {
  border-bottom:1px dotted #69f;
  color:#36c;
  text-decoration:none;
  }
a:visited {
  border-bottom-color:#969;
  color:#36c;
  }
a:hover {
  border-bottom:1px solid #f00;
  color:#f00;
  }
a.noline:link, a.noline:visited, a.noline:hover {border-style:none;}
-->
</STYLE>
<script language="javascript">
function update_fr (selectedIndex) {
  var group_in = document.form_post.announced_from_id.options[selectedIndex].value;
  if (group_in ==99) {
    document.form_post.announced_from_value.disabled = false;
  } else {
    document.form_post.announced_from_value.disabled = true;
  }
  return true;
}
function update_to (selectedIndex) {
  var group_in = document.form_post.announced_to_id.options[selectedIndex].value;
  if (group_in ==99) {
    document.form_post.announced_to_value.disabled = false;
  } else {
    document.form_post.announced_to_value.disabled = true;
  }
  return true;
}

</script>
</head>
<body>
<center><h2><font color="blue"><b><i>ietf</i></font>Announcement</b></h2></center>
|;
$html_bottom = qq{
</body>
</html>
};

$html_body = get_html_body($q);
$dbh->disconnect();
print <<END_HTML;
Content-type: text/html
$html_top
$html_body
$html_bottom
END_HTML

sub get_html_body {
   my $q = shift;
   my $command = $q->param("command");
   my $html_txt;
   my $body_txt;
   my $user_level = db_select($dbh,"select user_level from iesg_login where id=$loginid");
   if ($user_level > 0 and ($loginid != $chairid and $loginid != $iab_chairid and $loginid != 45 and $loginid != $nomcom_chair)) {
     return qq{
This tool has not been ready for you to use yet. ($loginid)<br>
};
   }
   unless (my_defined($command)) {
     $body_txt = main_screen($q);
   } else {
     my $func = "$command(\$q)";
     $body_txt = eval($func);
   }
   $html_txt .= qq {
User <b>$user_name</b>($login_name) logged in<hr>
$body_txt
<center>
   $form_header_main
   <input type="hidden" name="command" value="main_screen">
   <input type="submit" value="Main Menu">
   <input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true">
   </form>
</center>
   };
   return $html_txt;
}

sub main_screen {
  my $q=shift;
  my $from_list ;
  my $to_list;
  my $sqlStr;
  if ($loginid == $chairid) {
    $sqlStr = "select announced_from_id,announced_from_value from announced_from where announced_from_id in (3,7,8)";
  } elsif ($loginid == $iab_chairid) {
    $sqlStr = "select announced_from_id,announced_from_value from announced_from where announced_from_id in (10,22)";
  } elsif ($loginid == 45) {
    $sqlStr = "select announced_from_id,announced_from_value from announced_from where announced_from_id in (16,17)";
  } elsif ($loginid == $nomcom_chair){
    $sqlStr = "select announced_from_id,announced_from_value from announced_from where announced_from_id in (14,21)";	
  } else {
    $sqlStr = "select announced_from_id,announced_from_value from announced_from";
  }
  my @List_from = db_select_multiple($dbh,$sqlStr);
  if ($login_name eq "bfuller" or $login_name eq "amyk") {
    $from_list = "<option value=\"98\">IETF Executive Director <exec-director\@ietf.org></option>\n";
  }
  for my $array_ref (@List_from) {
    my ($id, $val) = @$array_ref;
    $from_list .= "<option value=\"$id\">$val</option>\n";
  }

  my @List_to = db_select_multiple($dbh,"select announced_to_id,announced_to_value from announced_to");
  for my $array_ref (@List_to) {
    my ($id, $val) = @$array_ref;
    $to_list .= "<option value=\"$id\">$val</option>\n";
  }

  my $html_txt = qq{
$astorisk - required field
$form_header_post  
$table_header
<input type="hidden" name="command" value="confirm">
<tr><td><b>NomCom message?</b></td>
<td><input type="radio" name="nomcom" value="1"> Yes &nbsp; &nbsp; 
<input type="radio" name="nomcom" value="0" checked> No
</tr>
<tr bgcolor="cdcdff"><td>$astorisk To: &nbsp; &nbsp; &nbsp; </td><td>
<select name="announced_to_id" onChange="update_to(this.selectedIndex);">
$to_list
</select><br>
 OR select 'Other...' from the list and type into the form field in the format of "Name &lt;email&gt;" <br>
<input type="text" name="announced_to_value" size="55">
</td></tr>

<tr><td>$astorisk From: &nbsp; &nbsp; &nbsp; </td><td>
<select name="announced_from_id" onChange="update_fr(this.selectedIndex);">
$from_list
</select><br>
 OR select 'Other...' from the list and type into the form field in the format of "Name &lt;email&gt;" <br>
<input type="text" name="announced_from_value" size="55">
</td></tr>
<tr bgcolor="cdcdff"><td>CC: </td><td><input type="text" size="55" name="cc"> <b>(separated by a comma)</b></td></tr>
<tr><td>BCC: </td><td><input type="text" size="55" name="bcc"> <b>(separated by a comma)</b></td></tr>
<tr bgcolor="cdcdff"><td>Reply to: </td><td><input type="text" size="55" name="replyto"> <b>(separated by a comma)</b></td></tr>
<tr><td>$astorisk Subject: &nbsp; &nbsp; &nbsp;</td><td><input type="text" size="65" name="subject"></td></tr>
<tr><td colspan="2">$astorisk Announcement Text</td></tr>
<tr bgcolor="cdcdff"><td colspan="2"><textarea cols="74" rows="15" name="announcement_text"></textarea></td></tr>
<tr><td colspan="2" align="center"><br><input type="submit" value="Submit"></td></tr>

</form>
</table>
  };
  return $html_txt;
}

sub confirm {
  my $q=shift;
  my $announced_to_id=$q->param("announced_to_id");
  my $announced_from_id=$q->param("announced_from_id");
  my $cc = $q->param("cc");
  my $bcc = $q->param("bcc");
  my $replyto = $q->param("replyto");
  my $error_message = undef;
  my $subject = $q->param("subject");
  $subject = indent_text2($subject,9);
  my $nomcom = $q->param("nomcom");
  my $nomcom_msg = ($nomcom)?"<b>This is a NomCom message</b>":"";
  my $announcement_text = format_comment_text($q->param("announcement_text"),74);
  
  
  my $announced_from = ($announced_from_id == 99)?$q->param("announced_from_value"):db_select($dbh,"select announced_from_value from announced_from where announced_from_id=$announced_from_id");
  $announced_from = "IETF Executive Director <exec-director\@ietf.org>" if ($announced_from_id==98);
  my $announced_to = ($announced_to_id == 99)?$q->param("announced_to_value"):db_select($dbh,"select announced_to_value from announced_to where announced_to_id=$announced_to_id");
  $error_message = "$astorisk Please enter TO field<br>\n" unless (my_defined($announced_to));
  $error_message .= "$astorisk Please enter FROM field<br>\n" unless (my_defined($announced_from));
  $error_message .= "$astorisk Please enter SUBJECT field<br>\n" unless (my_defined($subject));
  $error_message .= "$astorisk Please enter ANNOUNCEMENT TEXT field<br>\n" unless (my_defined($announcement_text));
  return $error_message if (my_defined($error_message)); 
  ($announced_from,$announced_to,$cc,$bcc,$replyto,$subject,$announcement_text) = html_bracket($announced_from,$announced_to,$cc,$bcc,$replyto,$subject,$announcement_text);
  ($announced_from,$announced_to,$cc,$bcc,$replyto,$subject,$announcement_text) = html_dq($announced_from,$announced_to,$cc,$bcc,$replyto,$subject,$announcement_text);
  return qq{
$form_header_post
<input type="hidden" name="command" value="send_announcement">
<input type="hidden" name="announced_to_id" value="$announced_to_id">
<input type="hidden" name="announced_from_id" value="$announced_from_id">
<input type="hidden" name="announced_from" value="$announced_from">
<input type="hidden" name="announced_to" value="$announced_to">
<input type="hidden" name="cc" value="$cc">
<input type="hidden" name="bcc" value="$bcc">
<input type="hidden" name="replyto" value="$replyto">
<input type="hidden" name="subject" value="$subject">
<input type="hidden" name="announcement_text" value="$announcement_text">
<input type="hidden" name="nomcom" value="$nomcom">
$nomcom_msg
<pre>
To: $announced_to
From: $announced_from
Cc: $cc
Bcc: $bcc
Reply-to: $replyto
Subject: $subject
<br>
$announcement_text
<br>
</pre>
<input type="submit" value="Send">
</form>
};
}

sub send_announcement {
  my $q=shift;
  my $extra = "";
  my $bcc = $q->param("bcc");
  my $replyto = $q->param("replyto");
  my $announced_from_id=$q->param("announced_from_id");
  my $announced_to_id=$q->param("announced_to_id");
  my $cc = $q->param("cc");
  my $subject = $q->param("subject");
  $subject = indent_text2($subject,9);
  my $nomcom=$q->param("nomcom");
  my $announcement_text = $q->param("announcement_text");
  my $announced_from = ($announced_from_id == 99)?$q->param("announced_from"):db_select($dbh,"select announced_from_value from announced_from where announced_from_id=$announced_from_id");
  $announced_from = "IETF Executive Director <exec-director\@ietf.org>" if ($announced_from_id==98);
  my $announced_to = ($announced_to_id == 99)?$q->param("announced_to"):db_select($dbh,"select announced_to_value from announced_to where announced_to_id=$announced_to_id");
  my $announced_to_email = db_select($dbh,"select announced_to_email from announced_to where announced_to_id=$announced_to_id");
  $announced_to .= " <$announced_to_email>" unless ($announced_to_id == 99);
  ($announced_from,$announced_to,$cc,$bcc,$replyto,$subject,$announcement_text) = de_html_bracket($announced_from,$announced_to,$cc,$bcc,$replyto,$subject,$announcement_text);
  ($announced_from,$announced_to,$cc,$bcc,$replyto,$subject,$announcement_text) = de_html_dq($announced_from,$announced_to,$cc,$bcc,$replyto,$subject,$announcement_text);
  $extra .= "bcc: $bcc^" if (my_defined($bcc));
  $extra .= "reply-to: $replyto^" if (my_defined($replyto));
  chop($extra) if (my_defined($extra));
#return "<pre>$announcement_text
  if (send_mail($program_name,$user_name,$announced_to,$announced_from,$subject,$announcement_text,$cc,$extra)) {
    my $announced_by = db_select($dbh,"select person_or_org_tag from iesg_login where id=$loginid");
    ($announcement_text,$subject,$cc,$extra,$announced_from) = db_quote($announcement_text,$subject,$cc,$extra,$announced_from);
    my $nomcom_chair_id = ($nomcom)?db_select($dbh,"select id from chairs_history where chair_type_id=3 and present_chair=1"):0;
    db_update($dbh,"insert into announcements (announced_by,announced_date,announced_time,announcement_text,announced_from_id,cc,subject,extra,announced_to_id,nomcom,nomcom_chair_id,other_val) values ($announced_by,current_date,current_time,$announcement_text,$announced_from_id,$cc,$subject,$extra,$announced_to_id,$nomcom,$nomcom_chair_id,$announced_from)",$program_name,$user_name);
    return "<h2>Announcement has been successfully sent to $announced_to</h2>\n";
  } else {
    return "<h2>Failed</h2>\n";
  }
}
