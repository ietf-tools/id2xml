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
#use CGI::Application::Plugin::Session;

$host=$ENV{SCRIPT_NAME};
$devel_mode = ($host =~ /devel/)?1:0;
$test_mode = 0;
$dbname = "ietf";
$mode_text = "";
if ($devel_mode) {
  $dbname="develdb";
  $mode_text = "Development Mode";
}
init_database($dbname);
$dbh=get_dbh();
$host = $ENV{SERVER_NAME};
$devel_mode = 1 unless ($host eq "datatracker.ietf.org");
my $q = new CGI;
$style_url="https://www.ietf.org/css/base.css";
$program_name = "wg_session_manual.cgi";
$program_title = "IETF Meeting Session Request Tool - Secretariat Version";
$program_title .= " db: $dbname" if ($devel_mode);
$table_header = qq{<table cellpadding="5" cellspacing="5" border="1" width="800">
};
$table_header2 = qq{<table cellpadding="1" cellspacing="1" border="0" width="800">
};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">};
$form_header_post2 = qq{<form action="$program_name" method="POST" name="form_post2">};
$form_header_post3 = qq{<form action="$program_name" method="POST" name="form_post3">};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">};
$form_header_get = qq{<form action="$program_name" method="GET" name="form_get">};
$form_header_noname = qq{<form action="$program_name" method="GET">
};
$bc="{";
$ec="}";
$color1="#cccccc";
$color2="#eeeeee";
$agenda_email="session-request\@ietf.org";
$rUser=$ENV{REMOTE_USER};
$loginid = db_select($dbh,"select person_or_org_tag from iesg_login where login_name='$rUser'");
$loginid = db_select($dbh,"select person_or_org_tag from wg_password where login_name='$rUser'") unless $loginid;
$user_name = get_name($loginid);
$user_email=get_email($loginid);
#<link rel="stylesheet" type="text/css" href="$style_url" />
$meeting_num=db_select($dbh,"select max(meeting_num) from meetings");
my $sub_title="";
if (defined($q->param("command"))) {
  my $command=$q->param("command");
  if ($command eq "begin_session_scheduling") {
    $sub_title = ": Request New Session";
  } elsif ($command eq "edit_session_scheduling") {
    $sub_title=": Edit/Cancel Previously Requested Session";
  } elsif ($command eq "modify") {
    $sub_title = ": Request to Edit Session";
  } elsif ($command eq "confirm_new_request") {
    $sub_title=": Confirmation";
  }
}
$html_top = qq|
<link rel="stylesheet" type="text/css" href="$style_url" />
<blockquote>
<h2><center>$program_title <font color="red"><i>$mode_text</i></font></center></h2>
<i>$user_name</i> logged on. &nbsp; 
<h2>IETF $meeting_num$sub_title</h2>
<hr>

|;
$html_bottom = qq{
<hr>
</blockquote>
};


$scheduled_wg = "0,";
my @List=db_select_multiple($dbh,"select group_acronym_id from wg_meeting_sessions where meeting_num=$meeting_num ");
for my $array_ref (@List) {
  my ($group_acronym_id) = @$array_ref;
  $scheduled_wg .= "$group_acronym_id,";
}
chop($scheduled_wg);


$asterisk = "<font color=\"red\"><b>*</b></font>";
$html_body = get_html_body($q);
$dbh->disconnect();
print $q->header("text/html"),
      $q->start_html(-title=>$program_title),
      $q->p($html_top),
      $q->p($html_body),
      $q->p($html_bottom),
      $q->end_html;

exit;

sub get_html_body {
   my $q = shift;
   my $command = $q->param("command");
   my $html_txt = "";
   unless (my_defined($command)) {
     $html_txt .= main_screen($q);
   } else {
     $command="begin_session_scheduling" if ($command eq "modify");
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
  my @List=db_select_multiple($dbh,"select group_acronym_id,acronym from groups_ietf, acronym where group_acronym_id=acronym_id and status_id=1 and group_acronym_id not in (select group_acronym_id from wg_meeting_sessions where meeting_num=$meeting_num) order by acronym");
  my @List2=db_select_multiple($dbh,"select irtf_id,irtf_acronym from irtf where irtf_id not in (select group_acronym_id from wg_meeting_sessions where meeting_num=$meeting_num) order by irtf_acronym");
  push @List, @List2;
  my $group_options=""; 
  for my $array_ref (@List) { 
    my ($group_acronym_id,$acronym) = @$array_ref; 
    $group_options .= "<option value=\"$group_acronym_id\">$acronym</option>\n"; 
  }

  my $scheduled_groups = "";
#  my @List_scheduled=db_select_multiple($dbh,"select acronym, a.group_acronym_id from groups_ietf a, acronym b, g_chairs c where a.group_acronym_id=b.acronym_id and a.group_acronym_id=c.group_acronym_id and status_id=1 and c.person_or_org_tag=$loginid and a.group_acronym_id in ($scheduled_wg)");

  my @List_scheduled =db_select_multiple($dbh,"select acronym, a.group_acronym_id from groups_ietf a, acronym b where a.group_acronym_id=b.acronym_id and status_id=1 and a.group_acronym_id in ($scheduled_wg)");

  my @List_irtf2 = db_select_multiple($dbh,"select irtf_acronym,a.irtf_id from irtf a where a.irtf_id in ($scheduled_wg)");

  push @List_scheduled,@List_irtf2 if ($#List_irtf2 > -1);
  $scheduled_groups = "<i>NONE</i>\n" if ($#List_scheduled < 0);
  for my $array_ref (@List_scheduled) {
    my ($acronym,$group_acronym_id) = @$array_ref;
    my $session_id = db_select($dbh,"select session_id from wg_meeting_sessions where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id ");
    my ($status_id,$status) = db_select($dbh,"select a.status_id, status from session_status a, wg_meeting_sessions b where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and a.status_id=b.status_id ");
    my ($ts_status_id,$ts_status) = db_select($dbh,"select a.status_id, status from session_status a, wg_meeting_sessions b where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and a.status_id=b.ts_status_id ");
    $status = "First Two Sessions:$status, Third Session:$ts_status" if ($ts_status_id);
    $scheduled_groups .= qq{<li> <a href="$program_name?command=edit_session_scheduling&gid=$group_acronym_id&sid=$session_id">$acronym</a> - $status</li>
};
  }


  return qq{
<li><h3>Create New Session Request</h3>
$form_header_get
<input type="hidden" name="command" value="begin_session_scheduling">
<select name="gid"><option value="0">Select WG/BOF/RG</option>
$group_options
</select> &nbsp; &nbsp; 
 <input type="submit" value=" Proceed ">
<li><h3>Edit/Cancel Previously Requested Session</h3></li>
<input type="hidden" name="command" value="edit_session_scheduling">
$scheduled_groups
</form>
<br><br>
};
}

sub get_length_option_list {
  my $selected_id=shift;
  my $ret_val = "";
  my @List=db_select_multiple($dbh,"select hour_id,hour_desc from meeting_hours");
  for my $array_ref (@List) {
    my ($hour_id,$hour_desc)=@$array_ref;
    $ret_val .= "<option  value=\"$hour_id\"";
    $ret_val .= "selected" if ($hour_id==$selected_id);
    $ret_val .=">$hour_desc</option>\n";
  }
  return $ret_val;
}

sub begin_session_scheduling {
  my $q=shift;
  my $group_acronym_id=$q->param("gid");
  my $num_session=0;
  my $length_session1=0;
  my $length_session2=0;
  my $length_session3=0;
  my $conflict1="";
  my $conflict2="";
  my $conflict3="";
  my $number_attendee=0;
  my $special_req="";
  my $conflict_other_q=""; 
  my $is_new=1;
  my $reset_button="";
  my $irtf=($group_acronym_id < 50)?1:0;
  if (defined($q->param("sid"))) {
    my $session_id=$q->param("sid");
    ($group_acronym_id,$irtf,$num_session,$length_session1,$length_session2,$length_session3,$number_attendee,$conflict1,$conflict2,$conflict3,$conflict_other,$special_req) = db_select($dbh,"select group_acronym_id,irtf,num_session,length_session1,length_session2,length_session3,number_attendee,conflict1,conflict2,conflict3,conflict_other,special_req from wg_meeting_sessions where session_id=$session_id");
    $is_new=0;
    $reset_button="<br><input type=\"reset\" value=\" Reset the form \" onClick=\"resetfieldstat();\">";
  }
  my $group_type_id=db_select($dbh,"select group_type_id from groups_ietf where group_acronym_id=$group_acronym_id");
  my $checked = ($length_session3)?"checked":"";
  my $prev_third_session = ($length_session3)?1:0;
  eval("\$num_session_selected$num_session = \"selected\"");
  my $length_option_list1=get_length_option_list($length_session1);
  my $length_option_list2=get_length_option_list($length_session2);
  my $length_option_list3=get_length_option_list($length_session3);
  my ($acronym,$name)=db_select($dbh,"select acronym,name from acronym where acronym_id=$group_acronym_id");
  my ($area_name,$area_acronym) = db_select($dbh,"select name,acronym from area_group a, acronym b where group_acronym_id=$group_acronym_id and area_acronym_id=acronym_id");
  if ($irtf) {
    ($acronym,$name) = db_select($dbh,"select irtf_acronym, irtf_name from irtf where irtf_id=$group_acronym_id");
    $area_name="IRTF";
    $area_acronym="IRTF";
  }
  my @otherWGList=db_select_multiple($dbh,"select group_acronym_id from session_conflicts where meeting_num=$meeting_num and conflict_gid=$group_acronym_id group by group_acronym_id");
  my $other_wg_list="";
  for my $array_ref (@otherWGList) {
    my ($group_acronym_id)=@$array_ref;
    my $name=db_select($dbh,"select acronym from acronym where acronym_id=$group_acronym_id");
    $other_wg_list.="$name, ";
  }
  if (my_defined($other_wg_list)) {
    chop($other_wg_list);chop($other_wg_list);
  } else {
    $other_wg_list = "<i>None so far</i>";
  }
  my $wg_option_list="";
  my @wgList=db_select_multiple($dbh,"select acronym from acronym a, groups_ietf b where group_type_id in (1,4) and status_id=1 and group_acronym_id=acronym_id order by acronym");
  for my $array_ref (@wgList) {
    my ($value) = @$array_ref;
    $wg_option_list .= qq{<option value="$value">$value</option>
};
  }
  my $additional_session_form = ($group_type_id==1)?qq{
<tr bgcolor="$color2" valign="top"><td>Additional Session Request:</td><td><input type="checkbox" name="third_session" $checked onClick="if (document.form_post.num_session.selectedIndex < 2) $bc alert('Cannot use this field - Number of Session is not set to 2'); return false; $ec else $bc if (this.checked==true) $bc document.form_post.length_session3.disabled=false; $ec else $bc document.form_post.length_session3.value=0;document.form_post.length_session3.disabled=true; $ec $ec"> Check this box to request an additional session.<br>
Additional slot may be available after agenda scheduling has closed and with the approval of an Area Director.<br>
Length of third session: <select name="length_session3" onClick="if (check_third_session()) $bc this.disabled=true;$ec"><option value="0">--Please select</option>
$length_option_list3
</select></td></tr>
}:"";
  return qq{
<script language="javascript">
function resetfieldstat () $bc
  if (document.form_post.prev_num_session.value > 0) $bc
    document.form_post.length_session1.disabled=false;
  $ec
  if (document.form_post.prev_num_session.value > 1) $bc
    document.form_post.length_session2.disabled=false;
  $ec
  if (document.form_post.prev_third_session.value > 0) $bc
    document.form_post.length_session3.disabled=false;
  $ec
  return 1;
$ec

function stat_ls (val)$bc
  if (val == 0) $bc
    document.form_post.length_session1.disabled = true;
    document.form_post.length_session2.disabled = true;
    document.form_post.length_session3.disabled = true;
    document.form_post.length_session1.value = 0;
    document.form_post.length_session2.value = 0;
    document.form_post.length_session3.value = 0;
    document.form_post.third_session.checked=false;
  $ec
  if (val == 1) $bc
    document.form_post.length_session1.disabled = false;
    document.form_post.length_session2.disabled = true;
    document.form_post.length_session3.disabled = true;
    document.form_post.length_session2.value = 0;
    document.form_post.length_session3.value = 0;
    document.form_post.third_session.checked=false;
  $ec
  if (val == 2) $bc
    document.form_post.length_session1.disabled = false;
    document.form_post.length_session2.disabled = false;
  $ec
$ec

function check_num_session (val) $bc
  if (document.form_post.num_session.value < val) $bc
    alert("Please change the value in the Number of Sessions to use this field");
    document.form_post.num_session.focused = true;
    return true;
  $ec
  return false;
$ec

function check_third_session () $bc
  if (document.form_post.third_session.checked == false) $bc

    return true;
  $ec
  return false;
$ec
function handleconflictfield (val) $bc
  if (val==1) $bc
    if (document.form_post.conflict1.value.length > 0) $bc
       document.form_post.conflict2.disabled=false;
       if (document.form_post.conflict2.value.length > 0) $bc
         document.form_post.conflict3.disabled=false;
       $ec
       return 1;
    $ec else $bc
       if (document.form_post.conflict2.value.length > 0 || document.form_post.conflict3.value.length > 0) $bc
         alert("Second and Third Conflicts to Avoid fields are being disabled");
         document.form_post.conflict2.disabled=true;   
         document.form_post.conflict3.disabled=true;   
         return 0;
       $ec
    $ec
  $ec else $bc
    if (document.form_post.conflict2.value.length > 0) $bc
       document.form_post.conflict3.disabled=false;
       return 1;
    $ec else $bc
       if (document.form_post.conflict3.value.length > 0) $bc
         alert("Third Conflicts to Avoid field is being disabled");
         document.form_post.conflict3.disabled=true;   
         return 0;
       $ec
    $ec
  $ec
  return 1; 
$ec
function delete_last1 () $bc
  var b = document.form_post.conflict1.value;
  var temp = new Array();
  temp = b.split(' ');
  temp.pop();
  b = temp.join(' ');
  document.form_post.conflict1.value = b;
  document.form_post.wg_selector1.selectedIndex=0;
$ec
function delete_last2 () $bc
  var b = document.form_post.conflict2.value;
  var temp = new Array();
  temp = b.split(' ');
  temp.pop();
  b = temp.join(' ');
  document.form_post.conflict2.value = b;
  document.form_post.wg_selector2.selectedIndex=0;
$ec
function delete_last3 () $bc
  var b = document.form_post.conflict3.value;
  var temp = new Array();
  temp = b.split(' ');
  temp.pop();
  b = temp.join(' ');
  document.form_post.conflict3.value = b;
  document.form_post.wg_selector3.selectedIndex=0;
$ec

function check_prior_conflict(val) $bc
  if (val == 2) $bc
    if (document.form_post.conflict1.value=="") $bc 
      alert("Please specify your First Priority prior to using this field");
      document.form_post.conflict2.disabled=true;
      document.form_post.conflict3.disabled=true;
      document.form_post.wg_selector1.focus();
      return 0;
    $ec
  $ec
  else  $bc
    if (document.form_post.conflict2.value=="" && document.form_post.conflict1.value=="") $bc 
      alert("Please specify your First and Second Priority prior to using this field");
      document.form_post.conflict3.disabled=true;
      document.form_post.wg_selector1.focus();
      return 0;
    $ec else $bc
       if (document.form_post.conflict2.value=="") $bc
         alert("Please specify your Second Priority prior to using this field");
         document.form_post.conflict3.disabled=true;
         document.form_post.wg_selector2.focus();
         return 0;
       $ec
    $ec
  $ec

  return 1;
$ec
</script>
$form_header_post
<input type="hidden" name="gid" value="$group_acronym_id">
<input type="hidden" name="command" value="confirm_new_request">
<input type="hidden" name="is_new" value="$is_new">
<input type="hidden" name="prev_num_session" value="$num_session">
<input type="hidden" name="prev_third_session" value="$prev_third_session">
<input type="hidden" name="irtf" value="$irtf">
$asterisk Required field.
$table_header2
<tr bgcolor="$color1"><td width="200">Working Group Name: </td><td>$name ($acronym)</td></tr>
<tr bgcolor="$color2"><td>Area Name: </td><td>$area_name ($area_acronym)</td></tr>
<tr bgcolor="$color1"><td>Number of Sessions: $asterisk </td><td><select name="num_session" onChange="stat_ls(this.selectedIndex);">
<option value="0">--Please select</option>
<option value="1" $num_session_selected1>1</option>
<option value="2" $num_session_selected2>2</option>
</select></td></tr>
<tr bgcolor="$color2"><td>Length of Session 1: $asterisk </td><td><select name="length_session1" onClick="if (check_num_session(1)) $bc this.disabled=true;$ec"><option value="0">--Please select</option>
$length_option_list1
</select></td></tr>
<tr bgcolor="$color2"><td>Length of Session 2: $asterisk </td><td><select name="length_session2" onClick="if (check_num_session(2)) $bc this.disabled=true; $ec"><option value="0">--Please select</option>
$length_option_list2
</select></td></tr>
$additional_session_form
<tr bgcolor="$color1"><td>Number of Attendees: $asterisk </td><td><input type="text" name="number_attendee" size="5" value="$number_attendee"></td></tr>
<tr bgcolor="$color2"><td valign="top">Conflicts to Avoid:</td>
<td>
  <table border="0">
    <tr><td colspan="2">Other WGs that included $acronym in their conflict lists:</td><td>$other_wg_list</td></tr>
    <tr bgcolor="$color1"><td rowspan="3" valign="top" width="220">WG Sessions:<br>You may select multiple WGs within each priority</td><td width="320">First Priority: </td>
<td>
<select name="wg_selector1" onChange="document.form_post.conflict1.value=document.form_post.conflict1.value + ' ' + this.options[this.selectedIndex].value; return handleconflictfield(1);"><option value="">--Select WG(s)</option>
$wg_option_list
</select>
<input type="button" value="Delete the last entry" onClick="delete_last1(); return handleconflictfield(1);"><br>
<input type="text" name="conflict1" size="55" value="$conflict1" onchange="return handleconflictfield(1);" >
</td></tr>
    <tr bgcolor="$color1"><td>Second Priority: </td><td>
<select name="wg_selector2" onClick="return check_prior_conflict(2);"  onChange="document.form_post.conflict2.value=document.form_post.conflict2.value + ' ' + this.options[this.selectedIndex].value; return handleconflictfield(2);"><option value="">--Select WG(s)</option>
$wg_option_list
</select>
<input type="button" value="Delete the last entry" onClick="delete_last2(); return handleconflictfield(2);"><br>

<input type="text" name="conflict2" size="55" value="$conflict2" onchange="return handleconflictfield(2);"></td></tr>
    <tr bgcolor="$color1"><td>Third Priority: </td><td>
<select name="wg_selector3" onClick="return check_prior_conflict(3);" onChange="document.form_post.conflict3.value=document.form_post.conflict3.value + ' ' + this.options[this.selectedIndex].value; return handleconflictfield(3);"><option value="">--Select WG(s)</option>

$wg_option_list
</select>
<input type="button" value="Delete the last entry" onClick="delete_last3(); return handleconflictfield(3);"><br>

<input type="text" name="conflict3" size="55" value="$conflict3" ></td></tr>
    <tr><td colspan="2">BOF or IRTF Sessions:<br>(Please enter free-form text) </td><td><textarea name="conflict_other" rows="3" cols="40">$conflict_other</textarea></td></tr>
  </table>
</td></tr>
<Tr bgcolor="$color1"><td valign="top">Special Requests:<br />
&nbsp;<br />
i.e. WebEx (state reason needed), restrictions on meeting times/days, etc.
</td>
<td><textarea name="special_req" cols="65" rows="6">$special_req</textarea></td></tr>
</table>
<input type="submit" value="Continue to Confirmation Page">
$reset_button
</form>
};

}

sub not_meeting_request {
  my $q=shift;
  my $group_acronym_id=$q->param("gid");
  db_update($dbh,"insert into not_meeting_groups (group_acronym_id,meeting_num) values ($group_acronym_id,$meeting_num)");
  add_session_activity($group_acronym_id,"A message was sent to notify not having a session at IETF $meeting_num",$meeting_num,$loginid);
  my $ad_email_list=get_ad_email_list($group_acronym_id);
  my $cochairs_email=get_cochairs_email($group_acronym_id,$loginid);
  my $cc_list="$ad_email_list,$cochairs_email,$user_email";
  my $cc_list_html=html_bracket($cc_list);
  my $group_name=uc(db_select($dbh,"select acronym from acronym where acronym_id=$group_acronym_id"));
  my $subject="$group_name-Not having a session at IETF $meeting_num";
  my $from = "IETF Meeting Session Request Tool <session_request_developers\@ietf.org>";
  my $to="session-request\@ietf.org";
  my $msg= qq{$user_name, a chair of the $group_name working group, indicated that 
the $group_name working group does not plan to hold a session at IETF $meeting_num.

This message was generated and sent by the IETF Meeting Session Request Tool.

}; 
  if ($devel_mode) {
    my $demo_msg= qq{
<html><body>
<link rel="stylesheet" type="text/css" href="https://www1.ietf.org/css/base.css" />
<b>Demo version of this tool does NOT actually send this request to the recipients.<br>
Rather, the actual email body (including mail header) is displayed below.<br>
In production mode, you will not see this screen.</b>
<hr>
<pre>
From: $from
To: $to
Cc: $cc_list_html
Subject: $subject

$msg
</pre>
<hr>
$form_header_post2
<input type="submit" name="submit" value="Users First Screen">
</form>
  </body></html>
};
print $q->header("text/html"),
      $q->start_html(-title=>"Demo Message"),
      $q->p($demo_msg),
      $q->end_html;
    exit;
  } else {
    send_mail($program_name,$user_name,$to,$from,$subject,$msg,$cc_list);
  }

  return qq{
<h2>A message was sent to notify not having a session at IETF $meeting_num</h2>
};
}

sub detect_errors {
  my $q=shift;
  my $group_acronym_id=$q->param("gid");
  my $num_session=$q->param("num_session");
  my $length_session1=(defined($q->param("length_session1")))?$q->param("length_session1"):0;
  my $length_session2=(defined($q->param("length_session2")))?$q->param("length_session2"):0;
  my $length_session3=(defined($q->param("length_session3")))?$q->param("length_session3"):0;
  my $conflict1=$q->param("conflict1");
  my $conflict2=$q->param("conflict2");
  my $conflict3=$q->param("conflict3");
  my $conflict_other=$q->param("conflict_other");
  my $number_attendee=$q->param("number_attendee");
  my $total_num_length = 0;
  $total_num_length++ if ($length_session1 > 0);
  $total_num_length++ if ($length_session2 > 0);
  my $error_message="";
  $error_message .= "<Li> Unselected Number of Sessions</li>" unless $num_session; 
  $error_message .= "<Li> Unselected Length of Session</li>" unless ($num_session == $total_num_length); 
  $error_message .= "<Li> Zero Number of Attendees</li>" unless $number_attendee; 
  #$error_message .= "<Li> Zero Number of Attendees</li>" unless my_defined($number_attendee); 
  $error_message .= "<Li> Non-Numeric value entered for Number of Attendees</li>" unless ($number_attendee=~/\d+/ or !my_defined($number_attendee));
  if (defined($q->param("third_session"))) {
    if ($num_session < 2) {
      $error_message .= "<li> You must select two sessions to request third session</li>";
    } else {
      $error_message .= "<li> Unselected Length of third session</li>" unless $length_session3;
    }
  }
  my $invalid_wg = "";
  if (my_defined($conflict1)) {
    my $check=check_wg_acronym($conflict1);
    $invalid_wg .= "$check," if my_defined($check);
  }
  if (my_defined($conflict2)) {
    my $check=check_wg_acronym($conflict2);
    $invalid_wg .= "$check," if my_defined($check);
  }  
  if (my_defined($conflict3)) {
    my $check=check_wg_acronym($conflict3);
    $invalid_wg .= "$check," if my_defined($check);
  }
  chop ($invalid_wg) if my_defined($invalid_wg);
  $error_message .= "<Li> Invalid Working Group acronym - $invalid_wg</li><br>\n" if my_defined($invalid_wg);
  return $error_message;
}


sub confirm_new_request {
  my $q=shift;
  my $group_acronym_id=$q->param("gid");
  my $num_session=$q->param("num_session");
  my $is_new=$q->param("is_new");
  my $length_session1=(defined($q->param("length_session1")))?$q->param("length_session1"):0;
  my $length_session2=(defined($q->param("length_session2")))?$q->param("length_session2"):0;
  my $length_session3=(defined($q->param("length_session3")))?$q->param("length_session3"):0;
  my $conflict1=$q->param("conflict1");
  my $conflict2=$q->param("conflict2");
  my $conflict3=$q->param("conflict3");
  my $conflict_other=$q->param("conflict_other");
  my $special_req=$q->param("special_req");
  my $number_attendee=$q->param("number_attendee");
  my $irtf=$q->param("irtf");
  my $error_message=detect_errors($q);
  error ($q,"<UL>$error_message</UL>") if my_defined($error_message);
  my $conflict_other_q=db_quote($conflict_other);
  my $special_req_q=db_quote($special_req);
  db_update($dbh,"insert into wg_meeting_sessions_temp (group_acronym_id,irtf,num_session,length_session1,length_session2,length_session3,conflict1,conflict2,conflict3,conflict_other,number_attendee,special_req) values ($group_acronym_id,$irtf,$num_session,$length_session1,$length_session2,$length_session3,'$conflict1','$conflict2','$conflict3',$conflict_other_q,$number_attendee,$special_req_q)");
  my $temp_id=db_select($dbh,"select max(temp_id) from wg_meeting_sessions_temp");
  my ($acronym,$name)=db_select($dbh,"select acronym,name from acronym where acronym_id=$group_acronym_id");
  my ($area_name,$area_acronym) = db_select($dbh,"select name,acronym from area_group a, acronym b where group_acronym_id=$group_acronym_id and area_acronym_id=acronym_id");
  if ($irtf) {
    ($acronym,$name) = db_select($dbh,"select irtf_acronym, irtf_name from irtf where irtf_id=$group_acronym_id");
    $area_name="IRTF";
    $area_acronym="IRTF";
  }
  $num_session++ if ($length_session3);
  my $html_txt = qq{
$form_header_post
<input type="hidden" name="command" value="submit_request">
<input type="hidden" name="temp_id" value="$temp_id">
<input type="hidden" name="is_new" value="$is_new">
$table_header2
<Tr bgcolor="$color1"><td>Working Group Name: </td><td>$name ($acronym)</td></tr>
<tr bgcolor="$color2"><td>Area Name: </td><td>$area_name ($area_acronym)</td></tr>
<Tr bgcolor="$color1"><td>Number of Sessions: </td><td>$num_session</td></tr>
};
for (my $loop=1;$loop<=$num_session;$loop++) {
  my $hour_id=eval("\$length_session$loop");
  my $length=get_hour_val($hour_id);
  $html_txt .= qq{
<tr bgcolor="$color2"><td>Length of Session $loop: </td><td>$length</td></tr>
};
}
#$html_txt .= qq{
#<tr bgcolor="$color2"><td>Length of Session 3: </td><td>$length_session3 $hours</td></tr>
#} if ($length_session3);
$html_txt .= qq{<tr bgcolor="$color1"><td>Number of Attendees: </td><td>$number_attendee</td></tr>
};
if (my_defined($conflict1)) {
  my $conflict_specific = qq{<table border="0"><Tr><Td>First Priority:</td><td>$conflict1</td></tr>
};
  $conflict_specific .= "<tr><td>Second Priority:</td><td>$conflict2</td></tr>\n" if (my_defined($conflict2));
  $conflict_specific .= "<tr><td>Third Priority:</td><td>$conflict3</td></tr>\n" if (my_defined($conflict3));
  if (my_defined($conflict_other)) {
    $conflict_other = format_textarea($conflict_other);
    $conflict_specific .= "<tr><td>Other:</td><td>$conflict_other</td></tr>\n";
  }
  $conflict_specific .= "</table>\n";
  $html_txt .= qq{<tr bgcolor="$color2"><td>Conflicts to Avoid:</td>
<td>$conflict_specific</td></tr>
};
}
$special_req = format_textarea($special_req); 
$html_txt .= qq{
<Tr><td vlign="top">Special Requests:</td><Td>$special_req</td></tr>
</table>
};
my $ts_status_id = 0;
$ts_status_id = db_select($dbh,"select ts_status_id from wg_meeting_sessions where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num") unless $is_new;
if ($length_session3 and $ts_status_id == 0) {
  $html_txt .= qq{<b>Note: Your request for a third session must be approved by an area director before being submitted to the IETF Secretariat. 
</b> 
<br>
<input type="submit" value="Send this request to the IETF Secretariat and the $area_name Directors for third session approval">
};
} else {
  $html_txt .= qq{
<input type="submit" value=" Save this request ">
};
}

$html_txt .= qq{
</form>
<br><br>
};
  return $html_txt;
}

sub submit_request {
  my $q=shift;
  my $temp_id=$q->param("temp_id");
  my $is_new=$q->param("is_new");
  my ($group_acronym_id,$irtf,$num_session,$length_session1,$length_session2,$length_session3,$number_attendee,$conflict1,$conflict2,$conflict3,$conflict_other,$special_req) = db_select($dbh,"select group_acronym_id,irtf,num_session,length_session1,length_session2,length_session3,number_attendee,conflict1,conflict2,conflict3,conflict_other,special_req from wg_meeting_sessions_temp where temp_id=$temp_id");
  my $exist = db_select($dbh,"select count(*) from wg_meeting_sessions where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num");
  error ($q,"Sessions for this working group have already been requested once.") if ($exist and $is_new);
  my ($area_name,$area_acronym) = db_select($dbh,"select name,acronym from area_group a, acronym b where group_acronym_id=$group_acronym_id and area_acronym_id=acronym_id");
  my $conflict_other_q=db_quote($conflict_other);
  my $special_req_q=db_quote($special_req);
  $irtf=0 unless my_defined($irtf);

  if ($is_new) {
    db_update($dbh,"insert into wg_meeting_sessions (meeting_num,group_acronym_id,irtf,num_session,length_session1,length_session2,length_session3,conflict1,conflict2,conflict3,conflict_other,special_req,number_attendee,approval_ad,status_id,requested_date,requested_by,last_modified_date) values ($meeting_num,$group_acronym_id,$irtf,$num_session,$length_session1,$length_session2,$length_session3,'$conflict1','$conflict2','$conflict3',$conflict_other_q,$special_req_q,$number_attendee,0,1,current_date,$loginid,current_date)");
    db_update($dbh,"update groups_ietf set meeting_scheduled='YES' where group_acronym_id=$group_acronym_id");
  } else {
    my $session_id=db_select($dbh,"select session_id from wg_meeting_sessions where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num");
    db_update($dbh,"update wg_meeting_sessions set irtf=$irtf,num_session=$num_session,length_session1=$length_session1,length_session2=$length_session2,length_session3=$length_session3,conflict1='$conflict1',conflict2='$conflict2',conflict3='$conflict3',conflict_other=$conflict_other_q,number_attendee=$number_attendee, special_req=$special_req_q where session_id=$session_id");
    db_update($dbh,"delete from session_conflicts where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num");
  }
  my ($session_id,$ts_status_id)=db_select($dbh,"select session_id,ts_status_id from wg_meeting_sessions where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num");
  my $status_text = "the IETF Secretariat to be scheduled";
  my $need_approval=0;
  if ($length_session3 and $ts_status_id==0) {
    $status_text = "the $area_name Directors for approval";
    $need_approval=1;
    db_update($dbh,"update wg_meeting_sessions set ts_status_id=2 where session_id=$session_id");
  }
  db_update($dbh,"update wg_meeting_sessions set ts_status_id=0 where session_id=$session_id") if ($length_session3 == 0 and $ts_status_id > 0);
  my $full_conflict = $conflict1;
  $full_conflict .= " $conflict2" if my_defined($conflict2);
  $full_conflict .= " $conflict3" if my_defined($conflict3);
  $full_conflict =~ s/,/ /g;
  if (my_defined($full_conflict)) {
    my @wgList = split ' ',$full_conflict;
    for my $array_ref (@wgList) {
      my $conflict_gid=db_select($dbh,"select acronym_id from acronym where acronym='$array_ref'");
      db_update($dbh,"insert into session_conflicts (group_acronym_id,conflict_gid,meeting_num) values ($group_acronym_id,$conflict_gid,$meeting_num)");
    }

  }  
  my $activity_text = ($is_new)?"New session was requested":"Updated session was requested";
  add_session_activity($group_acronym_id,$activity_text,$meeting_num,$loginid);
  db_update($dbh,"delete from not_meeting_groups where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num");
  #if (send_notification($session_id,$is_new,$need_approval)) {
    return qq{
<h2>The new request has been saved.</h2>
};
  #}
}

sub check_wg_acronym {
  my $wg_list = shift;
  $wg_list =~ s/,/ /g;
  my $invalid_acronym = "";
  my @List = split ' ',$wg_list;
  for my $array_ref (@List) {
    my $valid=db_select($dbh,"select count(group_acronym_id) from groups_ietf a, acronym b where b.acronym='$array_ref' and a.group_acronym_id=b.acronym_id and status_id=1");
    $invalid_acronym .= "$array_ref," unless ($valid);
  }
  chop($invalid_acronym) if my_defined($invalid_acronym);
  return $invalid_acronym;
}

sub edit_session_scheduling {
  my $q=shift;
  my $group_acronym_id=$q->param("gid");
  my $session_id=$q->param("sid");
  my $session_info=get_session_info($session_id);
  my $activities_log=get_session_activities_log($group_acronym_id);
  return qq{
$session_info
$activities_log
$table_header2
<tr><td width="100">
$form_header_get
<input type="hidden" name="command" value="modify">
<input type="hidden" name="sid" value="$session_id">
<input type="submit" value=" Edit this Request ">
</form>
</td>
<td>
$form_header_post3
<input type="hidden" name="command" value="cancel">
<input type="hidden" name="gid" value="$group_acronym_id">
<input type="hidden" name="sid" value="$session_id">
<input type="submit" value=" Cancel this Request " onClick="return window.confirm('Do you really want to cancel this session?');">
</form>
</td></tr></table>
};

}





sub cancel {
  my $q=shift;
  my $group_acronym_id=$q->param("gid");
  my $session_id=$q->param("sid");
  my ($acronym,$name)=db_select($dbh,"select acronym,name from acronym where acronym_id=$group_acronym_id");
  send_notification($session_id,2);
  db_update($dbh,"delete from session_conflicts where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num");
  db_update($dbh,"delete from wg_meeting_sessions where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num");
  db_update($dbh,"update groups_ietf set meeting_scheduled='NO' where group_acronym_id=$group_acronym_id"); 
  add_session_activity($group_acronym_id,"Session was cancelled",$meeting_num,$loginid);
  return qq{<h2>The request to cancel a session of  <i>$acronym</i> for IETF $meeting_num is now submitted.</h2>
<b>This working group is now removed from the main page of your MMM account.</b>

};
}


sub get_session_activities_log {
  my $group_acronym_id=shift;
  my @List=db_select_multiple($dbh,"select activity,act_date,act_time,act_by from session_request_activities where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num order by id desc");
  return "" if ($#List < 0);
  my $ret_val="<h3>Activities Log</h3>\n$table_header2\n<tr bgcolor=\"$color1\"><td width=\"90\">Date</td><td width=\"90\">Time</td><td>Action</td><td>Name</td></tr>\n";
  for my $array_ref (@List) {
    my ($activity,$date,$time,$act_by) = @$array_ref;
    my $name=get_name($act_by);
    $ret_val .= "<tr bgcolor=\"$color2\"><td>$date</td><td>$time</td><td>$activity</td><td>$name</td></tr>\n";
  }

  $ret_val .= "</table>\n";
  return $ret_val;
}
  
