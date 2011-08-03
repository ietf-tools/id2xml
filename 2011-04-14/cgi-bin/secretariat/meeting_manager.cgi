#!/usr/bin/perl -w
##########################################################################
#      Copyright © 2004 Foretec Seminars, Inc.
#
#      Program: proceeding_manager.cgi
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
use CGI_UTIL;
use CGI;
$host=$ENV{SCRIPT_NAME};
$devel_mode = ($host =~ /devel/)?1:0;
$test_mode = ($host =~ /test/)?1:0;
$dbname = "ietf";
$mode_text = "";
if ($devel_mode) {
#  $dbname="develdb";
  $mode_text = "Development Mode";
} elsif ($test_mode) {
  $dbname="testdb";
  $mode_text = "Test Mode";
}
init_database($dbname);
$dbh=get_dbh();
my $q = new CGI;
$view_agenda_url = ($devel_mode)?"http://stiedprstage1/devel/public/meeting_agenda_html.cgi":"https://datatracker.ietf.org/public/meeting_agenda_html.cgi";
@days=('Saturday','Sunday','Monday','Tuesday','Wednesday','Thursday','Friday');
$rUser=$ENV{REMOTE_USER};
$loginid = db_select($dbh,"select person_or_org_tag from iesg_login where login_name='$rUser'");
$style_url="https://www1.ietf.org/css/base.css";
$program_name = "meeting_manager.cgi";
$program_title = "IETF Meeting Manager$mode_text";
$table_header = qq{<table cellpadding="0" cellspacing="0" border="0">
};
$table_header2 = qq{<table cellpadding="0" cellspacing="0" border="0" width="1000">
};
$form_header_noname = qq{<form action="$program_name" method="POST">};
$form_header_selectog = qq{<form action="$program_name#wg_list" method="POST">};
$form_header_ref = qq{<form action="$program_name#wg_list" method="POST">};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">};
$form_header_post2 = qq{<form action="$program_name" method="POST" name="form_post2">};
$form_header_post3 = qq{<form action="$program_name" method="POST" name="form_post3">};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">};
$form_header_get = qq{<form action="$program_name" method="GET" name="form_get">};
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
   $meeting_num=$q->param("meeting_num");
   $html_txt .= qq{
</blockquote>
   $form_header_get
   <input type="hidden" name="command" value="retrieve_meeting">
   <input type="hidden" name="meeting_num" value="$meeting_num">
   <input type="submit" value="Main Menu">
   <input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true">
   </form>
   } if (my_defined($command) and $command ne "main_screen" and $command ne "retrieve_meeting");
   return $html_txt;
}

sub main_screen {
  my $meeting_list = "";
  my @List=db_select_multiple($dbh,"select meeting_num from meetings order by meeting_num");
  for my $array_ref (@List) {
    my ($meeting_num) = @$array_ref;
    $meeting_list .= "<option value=\"$meeting_num\">$meeting_num</option>\n";
  }
  return qq{
<h2>Main Menu</h2>
<li> <a href="$program_name?command=create_new_meeting_pre">Create New Meeting</a></br>
$form_header_get
<input type="hidden" name="command" value="retrieve_meeting">
<li> <select name="meeting_num"><option value="0">--Select Past Meeting</option>
$meeting_list
</select> <input type="submit" value=" Retrieve "></form>
<br><br><br><br>
};
}

sub create_new_meeting_pre {
  my $q=shift;
  return qq{
<h3>Create New IETF Meeting: Step 1</h3>
$form_header_post
<input type="hidden" name="command" value="create_new_meeting">
<ul><li> Enter IETF Meeting Number: <input type="text" name="meeting_num" size="4"></li></ul>
<input type="submit" value = " Proceed ">
</form><br><br><br>
};
}
                                                                                                                 
sub create_new_meeting {
  my $q=shift;
  my $meeting_num = $q->param("meeting_num");
  my $meeting_exist = db_select($dbh,"select count(*) from meetings where meeting_num=$meeting_num");
  my $meeting_info = "";
  if ($meeting_exist) {
    my ($start_date,$end_date,$city,$state,$country) = db_select($dbh,"select start_date,end_date,city,state,country from  meetings where meeting_num=$meeting_num");
    $meeting_info = qq{
<font color="red"><h3>This meeting has already been created</h3></font>
$table_header
<tr><td>Meeting Start Date: </td><td>$start_date</td></tr>
<tr><td>Meeting End Date: </td><td>$end_date</td></tr>
<tr><td>Meeting City: </td><td>$city</td></tr>
<tr><td>Meeting State: </td><td>$state</td></tr>
<tr><td>Meeting Country: </td><td>$country</td></tr>
</table>
};
  } else {
    $meeting_info = qq{
$table_header
<tr><td>Meeting Start Date: </td><td><input type="text" name="start_date" size="10"></td></tr>
<tr><td>Meeting End Date: </td><td><input type="text" name="end_date" size="10"></td></tr>
<tr><td>Meeting City: </td><td><input type="text" name="city" size="25"></td></tr>
<tr><td>Meeting State: </td><td><input type="text" name="state" size="25"></td></tr>
<tr><td>Meeting Country: </td><td><input type="text" name="country" size="25"></td></tr>
</table>
<input type="submit" value=" Proceed "><br>
</form>
};
  }
  my $html_txt = "<h3>Create New IETF Meeting: Step 2</h3>\n";
  $html_txt .= qq{
$form_header_post
<input type="hidden" name="command" value="create_new_confirm">
<input type="hidden" name="meeting_num" value="$meeting_num">
<h4>IETF Meeting $meeting_num</h4>
$meeting_info
                                                                                                                 
};
  return $html_txt;
}

sub create_new_confirm {
  my $q=shift;
  my $meeting_num =$q->param("meeting_num");
  my $start_date = $q->param("start_date");
  my $end_date = $q->param("end_date");
  my $city = $q->param("city");
  my $state=$q->param("state");
  my $country = $q->param("country");
  $meeting_info = qq{
<input type="hidden" name="start_date" value="$start_date">
<input type="hidden" name="end_date" value="$end_date">
<input type="hidden" name="city" value="$city">
<input type="hidden" name="state" value="$state">
<input type="hidden" name="country" value="$country">
$table_header
<tr><td>Meeting Start Date: </td><td>$start_date</td></tr>
<tr><td>Meeting End Date: </td><td>$end_date</td></tr>
<tr><td>Meeting City: </td><td>$city</td></tr>
<tr><td>Meeting State: </td><td>$state</td></tr>
<tr><td>Meeting Country: </td><td>$country</td></tr>
</table>
};
  my $html_txt = "<h3>Create New IETF Meeting: Step 3 - Confirmation</h3>\n";
  $html_txt .= qq{
$form_header_post
<input type="hidden" name="command" value="do_create_new">
<input type="hidden" name="meeting_num" value="$meeting_num">
<h4>IETF Meeting $meeting_num</h4>
$meeting_info
<input type="submit" value=" Proceed "><br>
</form>
};
  return $html_txt;
}
sub do_create_new {
  my $q=shift;
  my $meeting_num =$q->param("meeting_num");
  my $start_date = $q->param("start_date");
  my $end_date = $q->param("end_date");
  my $city = db_quote($q->param("city"));
  my $state=db_quote($q->param("state"));
  my $country = db_quote($q->param("country"));
  db_update($dbh,"insert into meetings (meeting_num,start_date,end_date,city,state,country) values ($meeting_num,'$start_date','$end_date',$city,$state,$country)");
  return qq{
Meeting was created successfuly<br>
};
}

sub retrieve_meeting {
  my $q=shift;
  my $meeting_num = $q->param("meeting_num");
  my ($start_date,$end_date,$city,$state,$country) = db_select($dbh,"select start_date,end_date,city,state,country from meetings where meeting_num=$meeting_num");
  my $wg_list = "";
  my @List = db_select_multiple($dbh,"select acronym_id,acronym from acronym a, groups_ietf b where a.acronym_id=b.group_acronym_id and b.status_id=1 order by acronym");
  for my $array_ref (@List) {
    my ($group_acronym_id,$group_acronym) = @$array_ref;
    $wg_list .= "<option value=\"$group_acronym_id\">$group_acronym</option>\n";
  }
  my $current_interim_list = "<blockquote>\n";
  my @List_interim = db_select_multiple($dbh,"select id,group_acronym_id,name,meeting_date from acronym a, interim_info b where a.acronym_id=b.group_acronym_id and b.meeting_num=$meeting_num");
  $current_interim_list .= "<i>None registered</i>" if ($#List_interim < 0);
  for my $array_ref (@List_interim) {
    my ($id,$group_acronym_id,$group_name,$meeting_date) = @$array_ref;
    $current_interim_list .= qq{<a href="$program_name?command=edit_interim&meeting_num=$meeting_num&group_acronym_id=$group_acronym_id">$group_name - $meeting_date</a> <a href="$program_name?command=delete_interim&id=$id&meeting_num=$meeting_num" onclick="return window.confirm('Do you really want to delete this Interim Meeting Info?')">[Delete]</a><br>
};
  }
  $current_interim_list .= "</blockquote>\n";
  return qq{
<center><h2>IETF $meeting_num</h2></center>
<table width="950" border="0">
<tr valign="top"><td>
<h2><li> Basic Information </h2>
$form_header_post
$table_header
<input type="hidden" name="command" value="update_meeting_info">
<input type="hidden" name="meeting_num" value="$meeting_num">
<tr><td align="left" valign="top"><b>Meeting Start Date: &nbsp; </b></td>
<td><input type="text" name="start_date" value="$start_date" size="25"><br><br></td></tr>
<tr><td align="left" valign="top"><b>Meeting End Date:</b></td>
<td><input type="text" name="end_date" value="$end_date" size="25"><br><br></td></tr>
<tr><td align="left" valign="top"><b>Meeting City:</b></td>
<td><input type="text" name="city" value="$city" size="25"><br><br></td></tr>
<tr><td align="left" valign="top"><b>Meeting State:</b></td>
<td><input type="text" name="state" value="$state" size="25"><br><br></td></tr>
<tr><td align="left" valign="top"><b>Meeting Country:</b></td>
<td><input type="text" name="country" value="$country" size="25"><br><br></td></tr>
</table>
<input type="submit" value=" UPDATE BASIC INFORMATION">
</form>
</li>
<br><br>
$form_header_get
<input type="hidden" name="command" value="session_scheduling">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="submit" value="  Schedule WG Sessions  ">
</form>
</td>
<td>
<h2><li> Additional Information</h2>
<blockquote>
<a href="$program_name?command=edit_additional&cat=ack&meeting_num=$meeting_num">Edit Acknowledgement</a><br><br>
<!---
<a href="$program_name?command=edit_additional&cat=agenda_html&meeting_num=$meeting_num"><font color="#cccccc">Edit Agenda HTML</font></a><br><br>
<a href="$program_name?command=edit_additional&cat=agenda_text&meeting_num=$meeting_num"><font color="#cccccc">Edit Agenda TEXT</font></a><br><br>
--->
<a href="$program_name?command=edit_overview&meeting_num=$meeting_num">Edit IETF Overview</a><br><br>
<a href="$program_name?command=edit_additional&cat=future_meeting&meeting_num=$meeting_num">Edit Future Meetings</a><br><br>
<a href="$program_name?command=edit_irtf&meeting_num=$meeting_num">Edit IRTF Home Page in HTML</a><br><br>
</blockquote>
</li>
</td>
<td>
<h2><li> Interim Meeting Info</h2>
$form_header_post
<input type="hidden" name="command" value="add_new_interim">
<input type="hidden" name="meeting_num" value="$meeting_num">
<select name="group_acronym_id"><option value="0">--Select WG</option>
$wg_list
</select> &nbsp; &nbsp; 
<input type="submit" value= " Add New Interim Meeting "><br>
</form>
<h3>Edit current list</h3>
$current_interim_list
</li>
</td></tr></table>
<br><br>
$form_header_noname
<input type="hidden" name="command" value="main_screen">
<input type="submit" value=" Back to the First Screen to select other meeting or create a new meeting ">
</form><br><br>
};
}

sub delete_interim {
  my $q=shift;
  my $id=$q->param("id");
  db_update($dbh,"delete from interim_info where id=$id");
  return retrieve_meeting($q);
}

sub update_meeting_info {
  my $q=shift;
  my ($start_date,$end_date,$city,$state,$country) = db_quote($q->param("start_date"),$q->param("end_date"),$q->param("city"),$q->param("state"),$q->param("country"));
  my $meeting_num=$q->param("meeting_num");
  db_update($dbh,"update meetings set start_date=$start_date,end_date=$end_date,city=$city,state=$state,country=$country where meeting_num=$meeting_num");
  return retrieve_meeting($q);
}

sub edit_additional {
  my $q=shift;
  my $cat=$q->param("cat");
  my $meeting_num=$q->param("meeting_num");
  my $text_val = db_select($dbh,"select $cat from meetings where meeting_num=$meeting_num");
  my $header="";
  if ($cat eq "ack") {
    $header="Acknowledgement";
  } elsif ($cat eq "agenda_html") {
    $header="Agenda in HTML";
  } elsif ($cat eq "agenda_text") {
    $header="Agenda in TEXT";
  } elsif ($cat eq "future_meeting") {
    $header="Future Meetings";
  } else {
    return "Error";
  }
  return qq{
<h2><li>Edit $header</h2>
$form_header_post
<input type="hidden" name="command" value="do_edit_additional">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="cat" value="$cat">
<textarea name="text_val" rows="25" cols="80">
$text_val
</textarea><br><br>
<input type="submit" value=" EDIT ">
</form><br><br></li>
};
}

sub do_edit_additional {
  my $q=shift;
  my $cat=$q->param("cat");
  my $meeting_num=$q->param("meeting_num");
  my $text_val = db_quote($q->param("text_val"));
  if ($cat eq "agenda_html") {
    $text_val =~ s/(<a href="\/ietf\/\S+">)(.*)(<\/a>)/$2/g;
    $text_val =~ s/http:\/\/www.ietf.org\/meetings\/agenda_\d\d.txt/agenda.txt/g;
  }
  db_update($dbh,"update meetings set $cat=$text_val where meeting_num=$meeting_num");
  return retrieve_meeting($q);
}

sub edit_overview {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $text_val1 = db_select($dbh,"select info_text from general_info where info_name='overview1'");
  my $text_val2 = db_select($dbh,"select info_text from general_info where info_name='overview2'");
  return qq{
<h2><li>Edit IETF Over View</h2>
$form_header_post
<input type="hidden" name="command" value="do_edit_overview">
<input type="hidden" name="meeting_num" value="$meeting_num">
<b>Over View Part 1 (in HTML): </b><br>
<textarea name="text_val1" rows="25" cols="80">
$text_val1
</textarea><br><br>
<b>Over View Part 2 (in HTML): </b><br>
<textarea name="text_val2" rows="25" cols="80">
$text_val2
</textarea><br><br>
<input type="submit" value=" EDIT ">
</form><br><br></li>
};
}

sub do_edit_overview {
  my $q=shift;
  my $text_val1 = db_quote($q->param("text_val1"));
  my $text_val2 = db_quote($q->param("text_val2"));
  db_update($dbh,"update general_info set info_text=$text_val1 where info_name='overview1'");
  db_update($dbh,"update general_info set info_text=$text_val2 where info_name='overview2'");
  return retrieve_meeting($q);
}

sub edit_irtf {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $text_val = db_select($dbh,"select info_text from general_info where info_name='irtf'");
  return qq{
<h2><li>Edit IRTF Home Page in HTML</h2>
$form_header_post
<input type="hidden" name="command" value="do_edit_irtf">
<input type="hidden" name="meeting_num" value="$meeting_num">
<textarea name="text_val" rows="25" cols="80">
$text_val
</textarea><br><br>
<input type="submit" value=" EDIT ">
</form><br><br></li>
};
}
                                                                                                               
sub do_edit_irtf {
  my $q=shift;
  my $text_val = db_quote($q->param("text_val"));
  db_update($dbh,"update general_info set info_text=$text_val where info_name='irtf'");
  return retrieve_meeting($q);
}
sub add_new_interim {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $group_acronym_id=$q->param("group_acronym_id");
  my $group_acronym=db_select($dbh,"select acronym from acronym where acronym_id=$group_acronym_id");
  my $exist = db_select($dbh,"select count(*) from interim_info where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id");
  return "<i><b>Interim Information for WG, $group_acronym was already registered for IETF $meeting_num</b></i>" if ($exist);
  return qq{
<h2><li>Enter Information  about <font color="red">$group_acronym</font> Interim meeting</h2>
$form_header_post
<input type="hidden" name="command" value="do_add_new_interim">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="group_acronym_id" value="$group_acronym_id">
<b>Meeting Date: </b> <input type="text" name="meeting_date" size="25"><br><br>
<b>Message text: </b> <br>
<textarea name="message_body" rows="25" cols="80">
</textarea><br><br>
<input type="submit" value=" ADD ">
</form><br><br></li>

};
}

sub do_add_new_interim {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $group_acronym_id=$q->param("group_acronym_id");
  my $meeting_date = db_quote($q->param("meeting_date"));
  my $message_body = db_quote($q->param("message_body"));
  db_update($dbh,"insert into interim_info (meeting_num,group_acronym_id,meeting_date,message_body) values ($meeting_num,$group_acronym_id,$meeting_date,$message_body)");
  return retrieve_meeting($q);
}

sub edit_interim {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $group_acronym_id=$q->param("group_acronym_id");
  my $group_acronym=db_select($dbh,"select acronym from acronym where acronym_id=$group_acronym_id");
  my ($meeting_date,$message_body) = db_select($dbh,"select meeting_date,message_body from interim_info where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id");
  return "<i><b>Interim Information for WG, $group_acronym was already registered for IETF $meeting_num</b></i>" if ($exist);
  return qq{
<h2><li>Enter Information  about <font color="red">$group_acronym</font> Interim meeting</h2>
$form_header_post
<input type="hidden" name="command" value="do_edit_interim">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="group_acronym_id" value="$group_acronym_id">
<b>Meeting Date: </b> <input type="text" name="meeting_date" value="$meeting_date" size="25"><br><br>
<b>Message text: </b> <br>
<textarea name="message_body" rows="25" cols="80">
$message_body
</textarea><br><br>
<input type="submit" value=" UPDATE ">
</form><br><br></li>
                                                                                                               
};
}
                                                                                                               
sub do_edit_interim {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $group_acronym_id=$q->param("group_acronym_id");
  my $meeting_date = db_quote($q->param("meeting_date"));
  my $message_body = db_quote($q->param("message_body"));
  db_update($dbh,"update interim_info set meeting_date=$meeting_date, message_body=$message_body where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id");
  return retrieve_meeting($q);
}
sub delete_room {
  my $q=shift;
  my $room_id=$q->param("room_id");
  my $exist=db_select($dbh,"select count(*) from wg_meeting_sessions where sched_room_id1=$room_id or sched_room_id2=$room_id or sched_room_id3=$room_id");
  error($q,"This room slot cannot be deleted. Already assigned to some session");
  db_update($dbh,"delete from meeting_rooms where room_id=$room_id") if $exist;
  return session_scheduling($q);
}
sub update_room {
  my $q=shift;
  my $room_id=$q->param("room_id");
  my $meeting_num=$q->param("meeting_num");
  my $room_name=db_select($dbh,"select room_name from meeting_rooms where room_id=$room_id");
  return qq{$form_header_post
<input type="hidden" name="command" value="do_update_room">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="room_id" value="$room_id">
<input type="text" name="room_name" value="$room_name" size="40">
<input type="submit" value="Update this Room">
<br>
</form>
};
}

sub do_update_room {
  my $q=shift;
  my $room_id=$q->param("room_id");
  my $room_name=db_quote($q->param("room_name"));
  db_update($dbh,"update meeting_rooms set room_name=$room_name where room_id=$room_id");
  db_update($dbh,"update switches set val=1,updated_date=current_date,updated_time=current_time where name='agenda_updated'");
  return session_scheduling($q);
}

sub update_time {
  my $q=shift;
  my $time_id=$q->param("time_id");
  my $meeting_num=$q->param("meeting_num");
  my ($time_desc,$day_id,$session_name_id)=db_select($dbh,"select time_desc,day_id,session_name_id from meeting_times where time_id=$time_id");
  my $session_name_option="";
  my $day_option="";
  my @List1=db_select_multiple($dbh,"select session_name_id,session_name from session_names");
  for my $array_ref (@List1) {
    my ($session_name_id_o,$session_name)=@$array_ref;
    my $selected=($session_name_id==$session_name_id_o)?"selected":"";
    $session_name_option .= "<option value=\"$session_name_id_o\" $selected>$session_name</option>\n";
  } 
  for (my $loop=-1;$loop<6;$loop++) {
    my $selected=($loop==$day_id)?"selected":"";
    $day_option .= "<option value=\"$loop\" $selected>$days[$loop+1]</option>\n";

  }
  return qq{
$form_header_post
<input type="hidden" name="command" value="do_update_time">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="time_id" value="$time_id">
<input type="text" name="time_desc" value="$time_desc" size="25">
<select name="session_name_id"><option value="0">--</option>
$session_name_option
</select>
<select name="day_id">
$day_option
</select>
<input type="submit" value="Update this Time Slot">
</form>
<br>
};
}

sub do_update_time {
  my $q=shift;
  my $time_id=$q->param("time_id");
  my $session_name_id=$q->param("session_name_id");
  my $day_id=$q->param("day_id");
  my $time_desc=db_quote($q->param("time_desc"));
  db_update($dbh,"update meeting_times set time_desc=$time_desc,day_id=$day_id,session_name_id=$session_name_id where time_id=$time_id");
  db_update($dbh,"update switches set val=1,updated_date=current_date,updated_time=current_time where name='agenda_updated'");
  return session_scheduling($q);
}


sub add_meeting_room {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $room_name=db_quote($q->param("room_name"));
  db_update($dbh,"insert into meeting_rooms (meeting_num,room_name) values ($meeting_num,$room_name)");
  return session_scheduling($q);
}
sub delete_time {
  my $q=shift;
  my $time_id=$q->param("time_id");
  my $exist=db_select($dbh,"select count(*) from wg_meeting_sessions where sched_time_id1=$time_id or sched_time_id2=$time_id or sched_time_id3=$time_id");
  error($q,"This time slot cannot be deleted. Already assigned to some session") if $exist;
  db_update($dbh,"delete from meeting_times where time_id=$time_id");
  return session_scheduling($q);
}
                                                                                           
sub add_meeting_time {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $time_desc=db_quote($q->param("time_desc"));
  my $day_id=$q->param("day_id");
  my $session_name_id=$q->param("session_name_id");
  db_update($dbh,"insert into meeting_times (meeting_num,time_desc,day_id,session_name_id) values ($meeting_num,$time_desc,$day_id,$session_name_id)");
  return session_scheduling($q);
}

sub add_tut {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  return qq{
<h2>Add New Tutorial/Saturday Session</h2>
$table_header
$form_header_post
<input type="hidden" name="command" value="do_add_tut">
<input type="hidden" name="meeting_num" value="$meeting_num">
<tr><td>Session Name (e.g., Security Tutorial): </td>
<td><input type="text" name="name" size="50"></td></tr>
<tr><td>Session Acronym (e.g., sectut): </td>
<td><input type="text" name="acronym" size="20"></td></tr>
<tr><td colspan="2"><input type="submit" value="Add This"></td></tr>
</form>
</table>
<br><br>
};
}

sub do_add_tut{
  my $q=shift;
  my $name=$q->param("name");
  my $acronym=$q->param("acronym");
  error ($q,"Name is missing") unless (my_defined($name));
  error ($q,"acronym is missing") unless (my_defined($acronym));
  error ($q,"Existing acronym") if (db_select($dbh,"select count(*) from acronym where acronym='$acronym'"));
  my $name_key=uc($name);
  my $acronym_id=db_select($dbh,"select min(acronym_id) from acronym");
  $acronym_id--;
  ($acronym,$name,$name_key) = db_quote($acronym,$name,$name_key);
  db_update($dbh,"insert into acronym (acronym_id,acronym,name,name_key) values ($acronym_id,$acronym,$name,$name_key)");
  db_update($dbh,"update switches set val=1,updated_date=current_date,updated_time=current_time where name='agenda_updated'");
  return session_scheduling($q);
}

sub session_scheduling {
  my $q=shift;
  my $meeting_num = $q->param("meeting_num");
  my $scheduled_group_ids = "0,";
  my $rooms_list ="<h3>Current Rooms</h3>\n";
  my $times_list ="<h3>Current Times</h3>\n";
  my @List_rooms = db_select_multiple($dbh,"select room_id,room_name from meeting_rooms where meeting_num=$meeting_num order by room_name");
  for my $array_ref (@List_rooms) {
    my ($room_id,$room_name)=@$array_ref;
    $rooms_list .= qq{<li> $room_name <a href="$program_name?command=update_room&room_id=$room_id&meeting_num=$meeting_num">[Update]</a>  <a href="$program_name?command=delete_room&room_id=$room_id&meeting_num=$meeting_num" onClick="return window.confirm('Are You Sure?');">[Delete]</a></li>
};
  }
  my @List_times = db_select_multiple($dbh,"select time_id,time_desc,day_id,session_name_id from meeting_times where meeting_num=$meeting_num order by day_id,session_name_id,time_desc");
  for my $array_ref (@List_times) {
    my ($time_id,$time_desc,$day_id,$session_name_id)=@$array_ref;
    my $session_name=db_select($dbh,"select session_name from session_names where session_name_id=$session_name_id");
    $session_name="" unless ($session_name);
    $times_list .= qq{<li> $days[$day_id+1] $session_name $time_desc <a href="$program_name?command=update_time&time_id=$time_id&meeting_num=$meeting_num">[Update]</a> <a href="$program_name?command=delete_time&time_id=$time_id&meeting_num=$meeting_num" onClick="return window.confirm('Are You Sure?');">[Delete]</a></li>
};
  }
  my @List_session_names=db_select_multiple($dbh,"select session_name_id, session_name from session_names");
  my $session_name_select="<select name=\"session_name_id\"><option value=\"0\">--</option>\n";
  for my $array_ref (@List_session_names) {
    my ($id,$val)=@$array_ref;
    $session_name_select .= "<option value=\"$id\">$val</option>\n";
  }
  $session_name_select .= "</select>";
  my $session_day_select=qq{<select name=\"day_id\">
<option value="-1">Saturday</option>
<option value="0">Sunday</option>
<option value="1">Monday</option>
<option value="2">Tuesday</option>
<option value="3">Wednesday</option>
<option value="4">Thursday</option>
<option value="5">Friday</option>
</select>
};
  my $ireg_col=db_select($dbh,"select name from non_session_ref where id=1");
  my $cb_col=db_select($dbh,"select name from non_session_ref where id=2");
  my $b_col=db_select($dbh,"select name from non_session_ref where id=3");
  my $fb_col=db_select($dbh,"select name from non_session_ref where id=6");
  my $arb_col=db_select($dbh,"select name from non_session_ref where id=4");
  my $arb_col_mt=$arb_col;
  $arb_col_mt =~ s/ and Snack//g;
  my $arb_col2=db_select($dbh,"select name from non_session_ref where id=5");
  my $reg_sun=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and day_id=0 and non_session_ref_id=1");
  my $reg_mon=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and day_id=1 and non_session_ref_id=1");
  my $reg_tue=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and day_id=2 and non_session_ref_id=1");
  my $reg_wed=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and day_id=3 and non_session_ref_id=1");
  my $reg_thu=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and day_id=4 and non_session_ref_id=1");
  my $reg_fri=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and day_id=5 and non_session_ref_id=1");
  my $break=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=3");
  my $fbreak=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=6");
  my $cbreak=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=2");
  my $arbreak_mon=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=4 and day_id=1");
  my $arbreak_tue=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=4 and day_id=2");
  my $arbreak_wed=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=4 and day_id=3");
  my $arbreak_thu=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=4 and day_id=4");
  my $arbreak_mon2=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=5 and day_id=1");
  my $arbreak_tue2=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=5 and day_id=2");
  my $arbreak_wed2=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=5 and day_id=3");
  my $arbreak_thu2=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=5 and day_id=4");

  my ($reg_area_name,$break_area_name) = db_select($dbh,"select reg_area_name,break_area_name from meeting_venues where meeting_num=$meeting_num");
  my @List_scheduled=db_select_multiple($dbh,"select group_acronym_id, acronym from wg_meeting_sessions a, acronym b where meeting_num=$meeting_num and group_acronym_id=acronym_id and a.status_id=4  order by acronym");
  my @List_scheduled_irtf=db_select_multiple($dbh,"select group_acronym_id, irtf_acronym from wg_meeting_sessions a, irtf b where meeting_num=$meeting_num and group_acronym_id=irtf_id and a.status_id=4  order by irtf_acronym");
  push @List_scheduled, @List_scheduled_irtf;
  for my $array_ref (@List_scheduled) {
    my ($group_acronym_id,$acronym) = @$array_ref;
    my $irtf = ($group_acronym_id > 0 and $group_acronym_id < 30)?1:0;
    my $bof=(db_select($dbh,"select count(*) from groups_ietf where group_acronym_id=$group_acronym_id and group_type_id=3"))?1:0;
    $scheduled_session .= qq{<li> <a href="$program_name?command=set_session&meeting_num=$meeting_num&group_acronym_id=$group_acronym_id&irtf=$irtf&bof=$bof">$acronym</a></li>
};
    $scheduled_group_ids .= "$group_acronym_id,";
  }
  chop ($scheduled_group_ids);
  my $html_txt = qq{
<h2>IETF $meeting_num: Session Schedule</h2>
<a href="$view_agenda_url?meeting_num=$meeting_num">View Agenda</a><br>
<a href="#wg_list">Requested WG Sessions and Other Sessions</a>
<hr>
$table_header2
<tr valign="top"><td>
<h3>Meeting Rooms</h3>
$form_header_noname
<input type="hidden" name="command" value="add_meeting_room">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="text" name="room_name" size="25">
<input type="submit" value=" add this room ">
<br>
</form>
$rooms_list
</td>
<td>
<h3>Meeting Times (i.e., 0900 - 1130)</h3>
$form_header_noname
<input type="hidden" name="command" value="add_meeting_time">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="text" name="time_desc" size="25">
$session_name_select
$session_day_select
<input type="submit" value=" add this time ">
<br>
</form>
$times_list

</td>
</tr>
<tr valign="top"><td>
<h3>Non-Session Items Times (i.e., 0900 - 1130)</h3>
$form_header_get
<input type="hidden" name="command" value="set_non_session">
<input type="hidden" name="meeting_num" value="$meeting_num">
<table>
<tr><td width="350">* $ireg_col Sunday: </td><td><input type="text" name="reg_sun" size="10" value="$reg_sun"></td></tr>
<tr><td>* $ireg_col Monday: </td><td><input type="text" name="reg_mon" size="10" value="$reg_mon"></td></tr>
<tr><td>* $ireg_col Tuesday: </td><td><input type="text" name="reg_tue" size="10" value="$reg_tue"></td></tr>
<tr><td>* $ireg_col Wednesday: </td><td><input type="text" name="reg_wed" size="10" value="$reg_wed"></td></tr>
<tr><td>* $ireg_col Thursday: </td><td><input type="text" name="reg_thu" size="10" value="$reg_thu"></td></tr>
<tr><td>* $ireg_col Friday: </td><td><input type="text" name="reg_fri" size="10" value="$reg_fri"></td></tr>
<tr><td>* $b_col: </td><td><input type="text" name="break" size="10" value="$break"></td></tr>
<tr><td>* $fb_col: </td><td><input type="text" name="fbreak" size="10" value="$fbreak"></td></tr>
<tr><td>* $cb_col: </td><td><input type="text" name="cbreak" size="10" value="$cbreak"></td></tr>
<tr><td>* $arb_col_mt Monday: </td><td><input type="text" name="arbreak_mon" size="10" value="$arbreak_mon"></td></tr>
<tr><td>* $arb_col_mt Tuesday: </td><td><input type="text" name="arbreak_tue" size="10" value="$arbreak_tue"></td></tr>
<tr><td>* $arb_col Wednesday: </td><td><input type="text" name="arbreak_wed" size="10" value="$arbreak_wed"></td></tr>
<tr><td>* $arb_col Thursday: </td><td><input type="text" name="arbreak_thu" size="10" value="$arbreak_thu"></td></tr>
<tr><td>* $arb_col2 Monday: </td><td><input type="text" name="arbreak_mon2" size="10" value="$arbreak_mon2"></td></tr>
<tr><td>* $arb_col2 Tuesday: </td><td><input type="text" name="arbreak_tue2" size="10" value="$arbreak_tue2"></td></tr>
<tr><td>* $arb_col2 Wednesday: </td><td><input type="text" name="arbreak_wed2" size="10" value="$arbreak_wed2"></td></tr>
<tr><td>* $arb_col2 Thursday: </td><td><input type="text" name="arbreak_thu2" size="10" value="$arbreak_thu2"></td></tr>

</table>
<br>
<input type="submit" value="Add/Update">
</form>
</td>
<td>
<h3>Meeting Venue</h3>
$form_header_get
<input type="hidden" name="command" value="set_break_area">
<input type="hidden" name="meeting_num" value="$meeting_num">
<table>
<tr><td>* Registration Area: </td><td><input type="text" name="reg_area_name" value="$reg_area_name" size="50"></td></tr>
<tr><td>* Break Area: </td><td><input type="text" name="break_area_name" value="$break_area_name" size="50"></td></tr>
</table>
<input type="submit" value="Submit"><br>
</form>
</td>

</tr>
<tr><td colspan="2"><a name="wg_list"></a>
<h3>Requested WG Sessions and Other Sessions</h3>
<b>Step 1:<b><br><br>
$table_header
<tr valign="top">
 $form_header_get
<input type="hidden" name="command" value="set_session">
<input type="hidden" name="meeting_num" value="$meeting_num">
<td width="300">
<select name="group_acronym_id">
<option value="0">--Select WG Group</option>
};
  my @List = db_select_multiple($dbh,"select acronym,group_acronym_id from acronym a, wg_meeting_sessions b where a.acronym_id = b.group_acronym_id and status_id in (1,2,3) and meeting_num=$meeting_num ");
  for my $array_ref (@List) {
    my ($acronym,$group_acronym_id) = @$array_ref;
    $html_txt .= "<option value=\"$group_acronym_id\">$acronym</option>\n";   }
  $html_txt .= qq{</select> <input type="submit" value=" Proceed "><br>
<a href="wg_session_manual.cgi">Create/Edit a new session request</a>
</td></form>
$form_header_get
<input type="hidden" name="command" value="set_session">
<input type="hidden" name="meeting_num" value="$meeting_num">
<td width="320">
<select name="group_acronym_id"> <option value="0">--Select Plenary/Training/Saturday Session </option>
<option value="-1">Wednesday Plenary</option>
<option value="-2">Thursday Plenary</option>
<option value="-99">---------------------------</option>
};
  my @List3 = db_select_multiple($dbh,"select name,acronym_id from acronym where acronym_id < -2 and acronym_id not in ($scheduled_group_ids)");
  for my $array_ref (@List3) {
    my ($acronym,$acronym_id) = @$array_ref;
    $html_txt .= "<option value=\"$acronym_id\">$acronym</option>\n";
  }
  my @List_bof=db_select_multiple($dbh,"select acronym_id,acronym from acronym a, groups_ietf b where group_type_id=3 and status_id=1 and group_acronym_id=acronym_id and acronym_id not in ($scheduled_group_ids) order by acronym");
  my $bof_option_list="";
  for my $array_ref (@List_bof) {
    my ($id,$bof)=@$array_ref;
    $bof_option_list .= "<option value=\"$id\">$bof</option>\n";
  }                                                                               
  $html_txt .= qq{
</select>
<input type="submit" value=" Proceed "></form><br>
<a href="$program_name?command=add_tut&meeting_num=$meeting_num">Add a New Tutorial/Saturday Session</a>
</td>
$form_header_get
<input type="hidden" name="command" value="set_session">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="bof" value="1">
<Td width="300">
<select name="group_acronym_id">
<option value="0">--Select BOF </option>
$bof_option_list
</select>
<input type="submit" value=" Proceed ">
</td></form>
$form_header_get
<input type="hidden" name="command" value="set_session">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="irtf" value="1">
<td width="300">
<select name="group_acronym_id">
<option value="0">--Select IRTF Group </option>
};
  my @List2 = db_select_multiple($dbh,"select irtf_acronym,irtf_id from irtf, wg_meeting_sessions where irtf_id=group_acronym_id and status_id=1  order by irtf_acronym");
  for my $array_ref (@List2) {
    my ($irtf_acronym,$irtf_id) = @$array_ref;
    $html_txt .= "<option value=\"$irtf_id\">$irtf_acronym</option>\n";
  }
  $html_txt .= qq{
</select>
<input type="submit" value=" Proceed ">
</form></td></tr></table>
<h3>Scheduled WG Sessions and Other Sessions</h3>
<a href="$view_agenda_url?meeting_num=$meeting_num">View Agenda</a><br>
<ul>
$scheduled_session
</ul>
</td>
</tr>
</table>
};
  return $html_txt;
}

sub set_break_area {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $break_area_name=db_quote($q->param("break_area_name"));
  my $reg_area_name=db_quote($q->param("reg_area_name"));
  my $exist=db_select($dbh,"select count(*) from meeting_venues where meeting_num=$meeting_num");
  my $sqlStr = ($exist)?"update meeting_venues set break_area_name=$break_area_name, reg_area_name=$reg_area_name where meeting_num=$meeting_num":"insert into meeting_venues (meeting_num,break_area_name,reg_area_name) values ($meeting_num,$break_area_name,$reg_area_name)";
  db_update ($dbh,$sqlStr);
  return session_scheduling($q);
}

sub set_non_session {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $reg_sun=$q->param("reg_sun");
  my $reg_mon=$q->param("reg_mon");
  my $reg_tue=$q->param("reg_tue");
  my $reg_wed=$q->param("reg_wed");
  my $reg_thu=$q->param("reg_thu");
  my $reg_fri=$q->param("reg_fri");
  my $break=$q->param("break");
  my $fbreak=$q->param("fbreak");
  my $cbreak=$q->param("cbreak");
  my $arbreak_mon=$q->param("arbreak_mon");
  my $arbreak_tue=$q->param("arbreak_tue");
  my $arbreak_wed=$q->param("arbreak_wed");
  my $arbreak_thu=$q->param("arbreak_thu");
  my $arbreak_mon2=$q->param("arbreak_mon2");
  my $arbreak_tue2=$q->param("arbreak_tue2");
  my $arbreak_wed2=$q->param("arbreak_wed2");
  my $arbreak_thu2=$q->param("arbreak_thu2");

  ## Sunday Registration Hours ##
  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and day_id = 0 and non_session_ref_id=1")) {
    db_update($dbh,"update non_session set time_desc='$reg_sun' where meeting_num=$meeting_num and day_id=0 and non_session_ref_id=1");
  } else {
    db_update($dbh,"insert into non_session (day_id,non_session_ref_id,meeting_num,time_desc) values (0,1,$meeting_num,'$reg_sun')");
  }
  ## Monday Registration Hours ##
  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and day_id = 1 and non_session_ref_id=1")) {
    db_update($dbh,"update non_session set time_desc='$reg_mon' where meeting_num=$meeting_num and day_id=1 and non_session_ref_id=1");
  } else {
    db_update($dbh,"insert into non_session (day_id,non_session_ref_id,meeting_num,time_desc) values (1,1,$meeting_num,'$reg_mon')"); 
  } 
  ## Tuesday Registration Hours ##
  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and day_id = 2 and non_session_ref_id=1")) {
    db_update($dbh,"update non_session set time_desc='$reg_tue' where meeting_num=$meeting_num and day_id=2 and non_session_ref_id=1");
  } else {
    db_update($dbh,"insert into non_session (day_id,non_session_ref_id,meeting_num,time_desc) values (2,1,$meeting_num,'$reg_tue')");
  }
  ## Wednesday Registration Hours ##
  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and day_id = 3 and non_session_ref_id=1")) {
    db_update($dbh,"update non_session set time_desc='$reg_wed' where meeting_num=$meeting_num and day_id=3 and non_session_ref_id=1");
  } else {
    db_update($dbh,"insert into non_session (day_id,non_session_ref_id,meeting_num,time_desc) values (3,1,$meeting_num,'$reg_wed')");
  }
  ## Thursday Registration Hours ##
  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and day_id = 4 and non_session_ref_id=1")) {
    db_update($dbh,"update non_session set time_desc='$reg_thu' where meeting_num=$meeting_num and day_id=4 and non_session_ref_id=1");
  } else {
    db_update($dbh,"insert into non_session (day_id,non_session_ref_id,meeting_num,time_desc) values (4,1,$meeting_num,'$reg_thu')");
  }
  ## Friday Registration Hours ##
  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and day_id = 5 and non_session_ref_id=1")) {
    db_update($dbh,"update non_session set time_desc='$reg_fri' where meeting_num=$meeting_num and day_id=5 and non_session_ref_id=1");
  } else {
    db_update($dbh,"insert into non_session (day_id,non_session_ref_id,meeting_num,time_desc) values (5,1,$meeting_num,'$reg_fri')");
  }
  ## Break Hours ##
  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and non_session_ref_id=3")) {
    db_update($dbh,"update non_session set time_desc='$break' where meeting_num=$meeting_num and non_session_ref_id=3");
  } else {
    db_update($dbh,"insert into non_session (non_session_ref_id,meeting_num,time_desc) values (3,$meeting_num,'$break')");
  }
  ## Firday Break Hours ##
  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and non_session_ref_id=6")) {
    db_update($dbh,"update non_session set time_desc='$fbreak' where meeting_num=$meeting_num and non_session_ref_id=6");
  } else {
    db_update($dbh,"insert into non_session (non_session_ref_id,meeting_num,time_desc) values (6,$meeting_num,'$fbreak')");
  }

  ## Continental Breakfast Hours ##
  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and non_session_ref_id=2")) {
    db_update($dbh,"update non_session set time_desc='$cbreak' where meeting_num=$meeting_num and non_session_ref_id=2");
  } else {
    db_update($dbh,"insert into non_session (non_session_ref_id,meeting_num,time_desc) values (2,$meeting_num,'$cbreak')");
  }
  ## Afternoon Refresment Break I Hours ##
  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and non_session_ref_id=4 and day_id=1")) {
    db_update($dbh,"update non_session set time_desc='$arbreak_mon' where meeting_num=$meeting_num and non_session_ref_id=4 and day_id=1");
  } else { 
    db_update($dbh,"insert into non_session (non_session_ref_id,meeting_num,time_desc,day_id) values (4,$meeting_num,'$arbreak_mon',1)");
  }

  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and non_session_ref_id=4 and day_id=2")) {
    db_update($dbh,"update non_session set time_desc='$arbreak_tue' where meeting_num=$meeting_num and non_session_ref_id=4 and day_id=2");
  } else { 
    db_update($dbh,"insert into non_session (non_session_ref_id,meeting_num,time_desc,day_id) values (4,$meeting_num,'$arbreak_tue',2)");
  }

  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and non_session_ref_id=4 and day_id=3")) {
    db_update($dbh,"update non_session set time_desc='$arbreak_wed' where meeting_num=$meeting_num and non_session_ref_id=4 and day_id=3");
  } else { 
    db_update($dbh,"insert into non_session (non_session_ref_id,meeting_num,time_desc,day_id) values (4,$meeting_num,'$arbreak_wed',3)");
  }

  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and non_session_ref_id=4 and day_id=4")) {
    db_update($dbh,"update non_session set time_desc='$arbreak_thu' where meeting_num=$meeting_num and non_session_ref_id=4 and day_id=4");
  } else { 
    db_update($dbh,"insert into non_session (non_session_ref_id,meeting_num,time_desc,day_id) values (4,$meeting_num,'$arbreak_thu',4)");
  }


  ## Afternoon Refresment Break II Hours ##
  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and non_session_ref_id=5 and day_id=1")) {
    db_update($dbh,"update non_session set time_desc='$arbreak_mon2' where meeting_num=$meeting_num and non_session_ref_id=5 and day_id=1");
  } else {  
    db_update($dbh,"insert into non_session (non_session_ref_id,meeting_num,time_desc,day_id) values (5,$meeting_num,'$arbreak_mon2',1)");
  } 
 
  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and non_session_ref_id=5 and day_id=2")) {
    db_update($dbh,"update non_session set time_desc='$arbreak_tue2' where meeting_num=$meeting_num and non_session_ref_id=5 and day_id=2");
  } else {  
    db_update($dbh,"insert into non_session (non_session_ref_id,meeting_num,time_desc,day_id) values (5,$meeting_num,'$arbreak_tue2',2)");
  } 
 
  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and non_session_ref_id=5 and day_id=3")) {
    db_update($dbh,"update non_session set time_desc='$arbreak_wed2' where meeting_num=$meeting_num and non_session_ref_id=5 and day_id=3");
  } else {  
    db_update($dbh,"insert into non_session (non_session_ref_id,meeting_num,time_desc,day_id) values (5,$meeting_num,'$arbreak_wed2',3)");
  } 
 
  if (db_select($dbh,"select count(non_session_id) from non_session where meeting_num=$meeting_num and non_session_ref_id=5 and day_id=4")) {
    db_update($dbh,"update non_session set time_desc='$arbreak_thu2' where meeting_num=$meeting_num and non_session_ref_id=5 and day_id=4");
  } else {  
    db_update($dbh,"insert into non_session (non_session_ref_id,meeting_num,time_desc,day_id) values (5,$meeting_num,'$arbreak_thu2',4)");
  } 
 

  return session_scheduling($q);

}
 

sub set_session {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $group_acronym_id=$q->param("group_acronym_id");
  my $irtf=(defined($q->param("irtf")))?$q->param("irtf"):0;
  my $bof=(defined($q->param("bof")))?$q->param("bof"):0;
  my $group_acronym=db_select($dbh,"select acronym from acronym where acronym_id=$group_acronym_id");
  my $requested_info="";
  my $status_id=db_select($dbh,"select status_id from groups_ietf where group_acronym_id=$group_acronym_id");
  my $schedule_form = "";
  my $num_session = 1;
  if ($irtf) {
    $status_id=1;
    $group_acronym=db_select($dbh,"select irtf_acronym from irtf where irtf_id=$group_acronym_id");
  }
  if ($status_id==1 and $bof==0) {
    my ($session_id,$status,$num_session_temp,$ts_status_id)=db_select($dbh,"select session_id,status,num_session,ts_status_id from wg_meeting_sessions a, session_status b where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num and a.status_id=b.status_id ");
    $requested_info = get_session_info($session_id);
    $requested_info .= "Session Status: $status<br>\n";
    if ($ts_status_id > 0) {
      my $status_value = db_select($dbh,"select status from session_status where status_id=$ts_status_id");
      $requested_info .= "<font color=\"red\">Third Session Status: $status_value</font><br>\n";
    }
    $num_session=$num_session_temp;
    $num_session++ if (($ts_status_id==3 or $ts_status_id==4) and $num_session_temp > 1);
  }
  my ($scheduled_date1,$scheduled_time1,$scheduled_room1,$scheduled_date2,$scheduled_time2,$scheduled_room2,$scheduled_date3,$scheduled_time3,$scheduled_room3,$special_agenda_note,$combined_room_id1,$combined_time_id1,$combined_room_id2,$combined_time_id2) = db_select($dbh,"select sched_date1,sched_time_id1,sched_room_id1,sched_date2,sched_time_id2,sched_room_id2,sched_date3,sched_time_id3,sched_room_id3,special_agenda_note,combined_room_id1,combined_time_id1,combined_room_id2,combined_time_id2 from wg_meeting_sessions where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num ");
  
  for (my $loop==0;$loop<$num_session;$loop++) {
    my $room_options="";
    my $time_options="";
    my $date_options="";
    my $id=$loop+1;
    my $start_date=db_select($dbh,"select start_date from meetings where meeting_num=$meeting_num");
    eval "\$scheduled_date=\$scheduled_date$id";
    eval "\$scheduled_time=\$scheduled_time$id";
    eval "\$scheduled_room=\$scheduled_room$id";
    eval "\$combined_time=\$combined_time_id$id";
    my $combined_checked=($combined_time)?"checked":"";
    for (my $interval=0;$interval<6;$interval++) {
      my $date=db_select($dbh,"select date_add('$start_date', interval $interval day)");
      my $day = db_select($dbh,"select dayname('$date')");
      my $selected = ($date eq $scheduled_date)?"selected":"";
      $date_options .= "<option value=\"$date\" $selected>$day, $date</option>\n";
    }
    $date_options .= "<option value=\"$scheduled_date\">$scheduled_date</option>\n";
    my @rooms=db_select_multiple($dbh,"select room_id,room_name from meeting_rooms where meeting_num=$meeting_num order by room_name");
    for my $array_ref (@rooms) {
      my ($room_id,$room_name) = @$array_ref;
      my $selected=($room_id==$scheduled_room)?"selected":"";
      $room_options .= "<option value=\"$room_id\" $selected>$room_name</option>\n";
    }
    my @times = db_select_multiple($dbh,"select time_id,time_desc,day_id,session_name_id from meeting_times where meeting_num=$meeting_num order by day_id,session_name_id");
    for my $array_ref (@times) {
      my ($time_id,$time_desc,$day_id,$session_name_id) = @$array_ref;
      my $selected = ($time_id==$scheduled_time)?"selected":"";
      my $session_name=db_select($dbh,"select session_name from session_names where session_name_id=$session_name_id");
      $session_name="" unless ($session_name);
      $time_options .= "<option value=\"$time_id\" $selected>$days[$day_id+1] $session_name $time_desc</option>\n";
    }
    $schedule_form .= qq{
<td>
  $table_header 
    <tr>
      <td colspan="2"><B>Session $id</b></td>
    </tr>
<!---
    <tr>
      <td>Date : </td><td>
        <select name="scheduled_date$id"><option value="0">--Select Date--</option>
        $date_options
        </select>
      </td>
    </tr>
--->
    <tr>
      <td>Day and Time : </td><td>
        <select name="scheduled_time$id"><option value="0">--Select Time--</option>
          $time_options
        </select>
      </td>
    </tr>
    <tr><td>Room Name: </td><td>
      <select name="scheduled_room$id"><option value="0">--Select Room--</option>
$room_options
      </select>
    </td>
  </tr>
  <tr>
    <td>Special Note from Scheduler: </td>
    <td><input type="text" value="$special_agenda_note" size="50" name="special_agenda_note"></td>
  </tr>
  <tr>
    <td>Combined with next session: </td>
    <td><input type="checkbox" $combined_checked name="combined$id"></td>
  </tr>
  </table>
</td>
};
  }

  return qq{<h2>Session Schedule for <font color="red">$group_acronym</h2></font>
$requested_info
<hr>
$form_header_noname
<input type="hidden" name="command" value="do_set_session">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="irtf" value="$irtf">
<input type="hidden" name="bof" value="$bof">
<input type="hidden" name="group_acronym_id" value="$group_acronym_id">
<input type="hidden" name="num_session" value="$num_session">
$table_header
<tr>
$schedule_form

</tr>
</table>
<br>
<b>Do NOT Notify this action: </b><input type="checkbox" name="do_not_notify"><br><br>
<input type="submit" value="Schedule this session and send out notification to the requester, ADs, and co-chairs" onClick="return window.confirm('Are you sure?');"><input type="reset">
</form>
$form_header_post
<input type="hidden" name="command" value="remove_session">
<input type="hidden" name="group_acronym_id" value="$group_acronym_id">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="submit" value="Remove this group from agenda" onClick="return window.confirm('This group will be permanently removed from the agenda and scheduling tool');">
</form>

};
}

sub remove_session {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $group_acronym_id=$q->param("group_acronym_id");
  db_update($dbh,"update wg_meeting_sessions set status_id=0, sched_room_id1=0, sched_room_id2=0, sched_room_id3=0,sched_time_id1=0, sched_time_id2=0, sched_time_id3=0, sched_date1=null, sched_date2=null, sched_date3=null, combined_room_id1=0, combined_time_id1=0, combined_room_id2=0, combined_time_id2=0 where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num");
  db_update($dbh,"update groups_ietf set meeting_scheduled='NO' where group_acronym_id=$group_acronym_id");
  add_session_activity($group_acronym_id,"Session was removed from agenda",$meeting_num,$loginid);
  return session_scheduling($q);
}

sub do_set_session {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $group_acronym_id=$q->param("group_acronym_id");
  my $irtf=$q->param("irtf") or 0;
  my $bof=$q->param("bof") or 0;
  my $special_agenda_note=$q->param("special_agenda_note");
  $special_agenda_note=db_quote($special_agenda_note);
  my $num_session=$q->param("num_session");
  if ($group_acronym_id < 0 or $bof) { ## BOF, Plenaries and Tutorials ##
    $num_session=1;
    db_update($dbh,"insert into wg_meeting_sessions (meeting_num,group_acronym_id,status_id) values ($meeting_num,$group_acronym_id,4)") unless db_select($dbh,"select count(session_id) from wg_meeting_sessions where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id ");
  }
  for (my $loop=0;$loop<$num_session;$loop++) {
    my $id=$loop+1;
    my $scheduled_date="";
    #my $scheduled_date=$q->param("scheduled_date$id");
    my $scheduled_time=$q->param("scheduled_time$id");
    my $scheduled_room=$q->param("scheduled_room$id");
    #$error_message .= "<li> Unseleted Meeting Date $id </li>\n" unless ($scheduled_date);
    $error_message .= "<li> Unseleted Meeting Time $id </li>\n" unless ($scheduled_time);
    $error_message .= "<li> Unseleted Meeting Room $id </li>\n" unless ($scheduled_room);
  }
  error($q,$error_message) if my_defined($error_message);
  my $third_session=($num_session==3)?1:0;
  for (my $loop=0;$loop<$num_session;$loop++) {
    my $id=$loop+1;
    my $scheduled_date=$q->param("scheduled_date$id");
    my $scheduled_time=$q->param("scheduled_time$id");
    my $scheduled_room=$q->param("scheduled_room$id");
    my $sqlStr="update wg_meeting_sessions set sched_room_id$id=$scheduled_room, sched_time_id$id=$scheduled_time, sched_date$id='$scheduled_date' where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id ";
    db_update($dbh,$sqlStr);
    if (defined($q->param("combined$id"))) {
      my $day_id = db_select($dbh,"select day_id from meeting_times where time_id=$scheduled_time");
      my @List = db_select_multiple($dbh,"select time_id from meeting_times where day_id=$day_id and meeting_num=$meeting_num order by time_desc");
      my $found=0;
      my $combined_time_id=0;
      for my $array_ref (@List) {
        my ($time_id) = @$array_ref;
        $combined_time_id = $time_id if $found;
        last if $found;
        $found=1 if ($time_id == $scheduled_time);
      }
      error($q,"There is no next session to combine") unless $combined_time_id;
#error($q,"update wg_meeting_sessions set combined_room_id$id=$scheduled_room,combined_time_id$id=$combined_time_id where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id ");
      db_update($dbh,"update wg_meeting_sessions set combined_room_id$id=$scheduled_room,combined_time_id$id=$combined_time_id where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id ");
    } else {
#error ($q,"update wg_meeting_sessions set combined_room_id$id=0,combined_time_id$id=0 where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id ");
    db_update($dbh,"update wg_meeting_sessions set combined_room_id$id=0,combined_time_id$id=0 where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id ");
    }
  }
  my $ts_status_id=db_select($dbh,"select ts_status_id from wg_meeting_sessions where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id ");
  $ts_status_id=4 if ($ts_status_id==3 and $third_session);
  db_update($dbh,"update wg_meeting_sessions set ts_status_id=$ts_status_id,status_id=4,scheduled_date=current_date,last_modified_date=current_date, special_agenda_note=$special_agenda_note where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id ");
  add_session_activity($group_acronym_id,"Session was scheduled",$meeting_num,$loginid);
  db_update($dbh,"update switches set val=1,updated_date=current_date,updated_time=current_time where name='agenda_updated'");
  return send_notification($q);
}

sub send_notification {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $group_acronym_id=$q->param("group_acronym_id");
  my $bof=$q->param("bof");
  return qq{
<h2>Session schedule has been set</h2>
<i>No notification has been sent to anyone for this session</i>
<hr>
$form_header_ref
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="command" value="session_scheduling">
<input type="submit" value="Select Other Group"> </form>
                                                                                            
} if ($group_acronym_id < 0 or $bof);

  my $irtf=$q->param("irtf") or 0;
  my $num_session=$q->param("num_session");
  my $group_name=($irtf)?db_select($dbh,"select irtf_acronym from irtf where irtf_id=$group_acronym_id"):uc(db_select($dbh,"select acronym from acronym where acronym_id=$group_acronym_id"));
  my ($requested_by,$session_id) = db_select($dbh,"select requested_by,session_id from wg_meeting_sessions where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num ");
  my $session_info_text=get_session_info_text($session_id);
  my $cochairs_email=get_cochairs_email($group_acronym_id,$requested_by);
  my $ad_email_list=get_ad_email_list($group_acronym_id);
  my $to_name=get_name($requested_by);
  my $to_email=get_email($requested_by);
  my $from="IETF Secretariat <agenda\@ietf.org>";
  my $subject=($num_session > 1)?"$group_name - Requested sessions have been scheduled for IETF $meeting_num":"$group_name - Requested session has been scheduled for IETF $meeting_num";
  my $cc_list = "";
  $cc_list .= "$cochairs_email," if my_defined($cochairs_email);
  $cc_list .= "$ad_email_list," if my_defined($ad_email_list);
  $cc_list .= "session-request\@ietf.org";
  my $notify=(defined($q->param("do_not_notify")))?"no":"yes";
  my $session_info="";
  for (my $loop=0;$loop<$num_session;$loop++) {
    my $id=$loop+1;
    my $scheduled_date=$q->param("scheduled_date$id");
    my $scheduled_time=$q->param("scheduled_time$id");
    my $scheduled_room=$q->param("scheduled_room$id");
    my $hour_id=db_select($dbh,"select length_session$id from wg_meeting_sessions where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id ");
    my $hour=get_hour_val($hour_id);
    my ($time,$day_id,$session_name_id)=db_select($dbh,"select time_desc,day_id,session_name_id from meeting_times where time_id=$scheduled_time");
    my $dayname=$days[$day_id+1];
    my $session_name=db_select($dbh,"select session_name from session_names where session_name_id=$session_name_id");
    $session_name="" unless ($session_name);
    my $room=db_select($dbh,"select room_name from meeting_rooms where room_id=$scheduled_room");
    $session_info .= qq{$group_name Session $id ($hour)
$dayname, $session_name $time
Room Name: $room
----------------------------------------------
};
  }
  my $special_agenda_note=$q->param("special_agenda_note");
  $special_agenda_note = "Special Note: $special_agenda_note\n" if my_defined($special_agenda_note);
  my $msg = qq{Dear $to_name,

The sessions that you have requested have been scheduled.
Below is the scheduled session information followed by 
the information of sessions that you have requested.

$session_info
$special_agenda_note

Requested Information:

$session_info_text
};
  send_mail($program_name,"AGENDA",$to_email,$from,$subject,$msg,$cc_list) if ($devel_mode==0 and $notify eq "yes");
  return qq{
<h2>Session schedule has been set</h2>
<pre>
To: $to_name &lt;$to_email&gt;
Cc: $cc_list
From: IETF Secretariat &lt;agenda\@ietf.org&gt;
Subject: $subject

$msg

Notified: $notify
<hr>
$form_header_selectog
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="command" value="session_scheduling">
<input type="submit" value="Select Other Group"> </form>
                                                                                            
}; 
}


