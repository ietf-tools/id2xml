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
init_database("ietf");

my $q = new CGI;
$style_url="https://www1.ietf.org/css/base.css";
$program_name = "nomcom.cgi";
$rUser = $ENV{REMOTE_USER};
$loginid = (my_defined($rUser)?db_select("select id from iesg_login where login_name = '$rUser'"):$q->param("loginid"));
$user_name = get_mark_by($loginid);
$login_name = db_select("select login_name from iesg_login where id=$loginid");

$program_title = "NOMCOM Members and Web Page Contents Manager";
$table_header = qq{<table cellpadding="5" cellspacing="5" border="0" width="800">
};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">
<input type="hidden" name="loginid" value="$loginid">
};
$form_header_post2 = qq{<form action="$program_name" method="POST" name="form_post2">
<input type="hidden" name="loginid" value="$loginid">
};
$form_header_post3 = qq{<form action="$program_name" method="POST" name="form_post3">
<input type="hidden" name="loginid" value="$loginid">
};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">
<input type="hidden" name="loginid" value="$loginid">
};
$form_header_get = qq{<form action="$program_name" method="GET" name="form_get">
<input type="hidden" name="loginid" value="$loginid">
};
$html_top = qq|
<link rel="stylesheet" type="text/css" href="$style_url" />
<h2><center>$program_title</center></h2>
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
   my $html_txt = qq{
User <b>$user_name</b>($login_name) logged in<hr>
<blockquote>};
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
return qq{<h3>
<li> <a href="$program_name?command=members">Edit NOMCOM Members</a></li><br>
<li> <a href="$program_name?command=add_message">Add NomCom Message</a></li><br>
</h3>
<br><br><br><br>
};
}

sub add_message {
  my $q=shift;
  my $from_list ;
  my $to_list;
  my $sqlStr;
  if ($loginid == 27) {
    $sqlStr = "select announced_from_id,announced_from_value from announced_from where announced_from_id in (9,10)";
  } else {
    $sqlStr = "select announced_from_id,announced_from_value from announced_from";
  }
  my @List_from = db_select_multiple($sqlStr);
  if ($login_name eq "bfuller") {
    $from_list = "<option value=\"99\">IETF Executive Director</option>\n";
  }
  for my $array_ref (@List_from) {
    my ($id, $val) = @$array_ref;
    if ($id==14) {
      $from_list .= "<option value=\"$id\" selected>$val</option>\n";
    } else {
      $from_list .= "<option value=\"$id\">$val</option>\n";
    }
  }
                                                                                                                 
  my @List_to = db_select_multiple("select announced_to_id,announced_to_value from announced_to");
  for my $array_ref (@List_to) {
    my ($id, $val) = @$array_ref;
    $to_list .= "<option value=\"$id\">$val</option>\n";
  }
                                                                                                                 
  my $html_txt = qq|
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

$form_header_post
$table_header
<input type="hidden" name="command" value="confirm">
<tr bgcolor="cdcdff"><td>To: &nbsp; &nbsp; &nbsp; </td><td>
<select name="announced_to_id" onChange="update_to(this.selectedIndex);">
$to_list
</select><br>
 OR select 'Other...' from the list and type into the form field in the format of "Name &lt;email&gt;" <br>
<input type="text" name="announced_to_value" size="55" disabled>
</td></tr>
                                                                                                                 
<tr><td>From: &nbsp; &nbsp; &nbsp; </td><td>
<select name="announced_from_id" onChange="update_fr(this.selectedIndex);">
$from_list
</select><br>
 OR select 'Other...' from the list and type into the form field in the format of "Name &lt;email&gt;" <br>
<input type="text" name="announced_from_value" size="55" disabled>
</td></tr>
<tr><td>Announced Date: </td><td><input type="text" name="announced_date" size="10"> <b>yyyy-mm-dd</b></td></tr>
<tr><td>Subject: &nbsp; &nbsp; &nbsp;</td><td><input type="text" size="65" name="subject"></td></tr>
<tr><td colspan="2">Announcement Text</td></tr>
<tr bgcolor="cdcdff"><td colspan="2"><textarea cols="80" rows="15" name="announcement_text"></textarea></td></tr><tr><td colspan="2" align="center"><br><input type="submit" value="Submit"></td></tr>
                                                                                                                 
</form>
</table>
  |;
  return $html_txt;

}

sub confirm {
  my $q=shift;
  my $announced_to_id=$q->param("announced_to_id");
  my $announced_from_id=$q->param("announced_from_id");
  my $error_message = undef;
  my $announced_date = $q->param("announced_date");
  my $subject = $q->param("subject");
  $subject =~ s/</&lt;/g;
  $subject =~ s/>/&gt;/g;
  $subject = indent_text2($subject,9);
  my $announcement_text = format_comment_text($q->param("announcement_text"));
  my $announcement_text2 = $announcement_text;
  $announcement_text =~ s/</&lt;/g;
  $announcement_text =~ s/>/&gt;/g;
  $announcement_text2 =~ s/"/^/g;
  my $announced_from = ($announced_from_id == 99)?$q->param("announced_from_value"):db_select("select announced_from_value from announced_from where announced_from_id=$announced_from_id");   my $announced_to = ($announced_to_id == 99)?$q->param("announced_to_value"):db_select("select announced_to_value from announced_to where announced_to_id=$announced_to_id");   
  $error_message = "Please enter TO field<br>\n" unless (my_defined($announced_to));
  $error_message .= "Please enter FROM field<br>\n" unless (my_defined($announced_from));
  $error_message .= "Please enter SUBJECT field<br>\n" unless (my_defined($subject));
  $error_message .= "Please enter ANNOUNCEMENT TEXT field<br>\n" unless (my_defined($announcement_text));
  $error_message .= "Please enter ANNOUNCED DATE field<br>\n" unless (my_defined($announced_date));
  if ($announced_date =~ /(\d\d\d\d-\d{1,2}-\d{1,2})/) {
    $announced_date = $1;
  } else {
    $error_message .= "Invalid format of ANNOUNCED DATE<br>\n" if (my_defined($announced_date));
  }
  return $error_message if (my_defined($error_message));
  return qq{
$form_header_post
<input type="hidden" name="command" value="save_announcement">
<input type="hidden" name="announced_to_id" value="$announced_to_id">
<input type="hidden" name="announced_from_id" value="$announced_from_id">
<input type="hidden" name="announced_from" value="$announced_from">
<input type="hidden" name="subject" value="$subject">
<input type="hidden" name="announced_date" value="$announced_date">
<input type="hidden" name="announcement_text" value="$announcement_text2">
<pre>
To: $announced_to
From: $announced_from
Date: $announced_date
Subject: $subject
<br>
$announcement_text
<br>
</pre>
<input type="submit" value="Save">
</form>
};
}
sub save_announcement {
  my $q=shift;
  my $announced_from_id=$q->param("announced_from_id");
  my $announced_from=$q->param("announced_from");
  my $announced_to_id=$q->param("announced_to_id");
  my $announced_date = $q->param("announced_date");
  my $subject = $q->param("subject");
  $subject =~ s/&lt;/</g;
  $subject =~ s/&gt;/>/g;
  $subject = indent_text2($subject,9);
  my $nomcom=1;
  my $announcement_text = $q->param("announcement_text");
  $announcement_text =~ s/&lt;/</g;
  $announcement_text =~ s/&gt;/>/g;
  $announcement_text =~ s/\^/"/g;
#return "<pre>$announcement_text</pre>";
  ($announcement_text,$subject) = db_quote($announcement_text,$subject);
  my $nomcom_chair_id = ($nomcom)?db_select("select id from chairs_history where chair_type_id=3 and present_chair=1"):0;
  my $announced_by = db_select("select person_or_org_tag from iesg_login where id=$loginid");
  db_update("insert into announcements (announced_by,announced_date,announced_time,announcement_text,announced_from_id,subject,announced_to_id,nomcom,nomcom_chair_id,manualy_added,other_val) values ($announced_by,'$announced_date',current_time,$announcement_text,$announced_from_id,$subject,$announced_to_id,$nomcom,$nomcom_chair_id,1,'$announced_from')",$program_name,$user_name);
  return "<h2>Announcement has been successfully saved</h2>\n";
}

sub members {
  my @List = db_select_multiple("select id,person_or_org_tag,start_year,end_year from chairs_history where chair_type_id=3 order by start_year desc");
  my $list_html = "";
  for my $array_ref (@List) {
    my ($id,$person_or_org_tag,$start_year,$end_year) = @$array_ref;
    my $name = get_name($person_or_org_tag);
    $list_html .= qq{<li> <b><a href="$program_name?command=edit_members&id=$id">$start_year-$end_year $name</a></b></li><br>
};
  }
  return qq{
<h2>Click a link below to edit members of selected year</h2>
<hr>
$list_html
<br><br>
};
}

sub edit_members {
  my $q=shift;
  my $id=$q->param("id");
  my $exist = db_select("select count(chair_id) from nomcom_members where chair_id=$id");
  my $voting_members = ($exist)?db_select("select voting_members from nomcom_members where chair_id=$id"):"";
  my $non_voting_members = ($exist)?db_select("select non_voting_members from nomcom_members where chair_id=$id"):"";
  my ($start_year,$end_year) = db_select("select start_year,end_year from chairs_history where id=$id and chair_type_id=3");
  return qq{
<h2>NOMCOM Members $start_year - $end_year</h2>
<hr>
$form_header_post
<input type="hidden" name="command" value="do_edit_members">
<input type="hidden" name="id" value="$id">
<h3>Voting Members</h3>
<textarea name="voting_members" cols="80" rows="15">$voting_members</textarea><br>
<h3>Non Voting Members</h3>
<textarea name="non_voting_members" cols="80" rows="7">$non_voting_members</textarea><br>
<br>
<input type="submit" value=" Submit ">
</form>
<br>

};
}

sub do_edit_members {
  my $q=shift;
  my $id=$q->param("id");
  my $voting_members = db_quote($q->param("voting_members"));
  my $non_voting_members = db_quote($q->param("non_voting_members"));
  my $exist = db_select("select count(chair_id) from nomcom_members where chair_id=$id");
  if ($exist) {
    db_update("update nomcom_members set voting_members=$voting_members, non_voting_members=$non_voting_members where chair_id=$id");
  } else {
    db_update("insert into nomcom_members (chair_id,voting_members,non_voting_members) values ($id,$voting_members,$non_voting_members)");
  }
  return members();
}


