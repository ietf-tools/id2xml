#!/usr/bin/perl
##########################################################################
#      Copyright © 2004 Foretec Seminars, Inc.
#
#      Program: proceeding_manager.cgi
#      Author : Sunny Lee, Foretec Seminars, Inc
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

use constant BUFFER_SIZE => 16_384;
use constant MAX_FILE_SIZE => 20_971_520; # 20 MB Max file size
use constant MAX_OPEN_TRIES => 100;
$CGI::DISABLE_UPLOADS = 0;
$CGI::POST_MAX = MAX_FILE_SIZE;

$host=$ENV{SCRIPT_NAME};
$devel_mode = ($host =~ /devel/)?1:0;
$test_mode = ($host =~ /test/)?1:0;
$host=$ENV{SERVER_NAME};
$onsite_mode = ($host eq "onsite.ietf.org")?1:0;
#$testing_group = ",geopriv,v6ops,ipv6,mip4,mipshop,ippm,kitten,mobike,sipping,manet,pce,";
$testing_groups = "'v6ops','ipv6','mip4','mipshop','ippm','kitten','mobike','sipping','manet','pce'";
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
$rUser=$ENV{REMOTE_USER};
$loginid=db_select($dbh,"select person_or_org_tag from iesg_login where login_name = '$rUser'");
$loginid=db_select($dbh,"select person_or_org_tag from wg_password where login_name = '$rUser'") unless $loginid;
$loginid=db_select($dbh,"select a.person_or_org_tag from email_addresses a, wg_password b where email_address like '%$rUser' and a.person_or_org_tag=b.person_or_org_tag") unless $loginid;
error($q,"Unknown User - $rUser, $loginid") unless $loginid;
$group_acronym_id_list = get_group_acronym_id_list();
$is_testers = db_select($dbh,"select count(*) from acronym a, g_chairs b where group_acronym_id=acronym_id and person_or_org_tag=$loginid and acronym in ($testing_groups)");
$is_wg_chair = db_select($dbh,"select count(a.group_acronym_id) from groups_ietf a, g_chairs b where b.person_or_org_tag=$loginid and a.group_acronym_id=b.group_acronym_id and a.status_id=1");
$is_wg_chair = db_select($dbh,"select count(a.group_acronym_id) from groups_ietf a, g_secretaries b where b.person_or_org_tag=$loginid and a.group_acronym_id=b.group_acronym_id and a.status_id=1") unless $is_wg_chair;
$wg_chair_name=get_name($loginid);
@Chairs = db_select_multiple($dbh,"select person_or_org_tag from chairs where chair_name in ('IETF','IAB','IAB Executive Director')");
$ietf_iab_chairs = "";
$is_ietf_iab_chair = 0;
for my $array_ref (@Chairs) {
my ($person_or_org_tag) = @$array_ref;
$is_ietf_iab_chair = 1 if ($person_or_org_tag == $loginid);
}
#$is_ietf_iab_chair = ($ietf_iab_chairs =~ /$loginid/)?1:0;
#$is_ietf_iab_chair = 1 if ($loginid == 105651);
$is_tut_resp=db_select($dbh,"select is_tut_resp from wg_password where person_or_org_tag=$loginid");
#$is_tut_resp=1 if ($loginid == 105651);
$is_irtf_chair=db_select($dbh,"select irtf_id from wg_password where person_or_org_tag=$loginid");

$program_name = "wg_proceedings.cgi";


#$host_name = "mlee-desktop"; #DEPLOY - Disable
$host_name = "www.ietf.org"; #DEPLOY - Enable
$host_name = "datatracker.ietf.org" if ($devel_mode);
#$host_name="onsite.ietf.org" if ($onsite_mode);
$preliminary_url = ($devel_mode)?"https://$host_name/public/meeting_materials_devel.cgi":"https://datatracker.ietf.org/public/meeting_materials.cgi";
$program_title = "IETF Meeting Materials Manager";
$program_title .= " db: $dbname" if ($devel_mode);
$style_url="https://www.ietf.org/css/base.css";
$proceeding_dir = "proceedings";
$web_dir = "/a/www/www6s/$proceeding_dir";
$table_header = qq{<table cellpadding="0" cellspacing="0" border="0">
};

$meeting_num=$q->param("meeting_num") or 0;
my $meeting_num1 = db_select($dbh,"select min(meeting_num) from proceedings where frozen=0");
my $meeting_num2 = db_select($dbh,"select max(meeting_num) from proceedings where frozen=0");
#$meeting_num=64 unless $is_testers; ####To be deleted after 9/19/2005####
unless ($meeting_num) {
  if ($meeting_num1 != $meeting_num2) {
    my $cut_off=db_select($dbh,"select c_sub_cut_off_date from proceedings where meeting_num=$meeting_num1");
    my $c_days = db_select($dbh,"select to_days(current_date)");
    my $cut_off_date_days=db_select($dbh,"select to_days('$cut_off')");
    my $is_over = ($c_days > $cut_off_date_days)?1:0;
    $meeting_num=($c_days > $cut_off_date_days)?$meeting_num2:0;

  } else {
    $meeting_num=$meeting_num2;
    my $cut_off_date = db_select($dbh,"select c_sub_cut_off_date from proceedings where meeting_num=$meeting_num");
    my $c_days = db_select($dbh,"select to_days(current_date)");
    my $cut_off_date_days=db_select($dbh,"select to_days('$cut_off_date')");
    my $is_over = ($c_days > $cut_off_date_days)?1:0;
    $cut_off_date = convert_date($cut_off_date,5);
    error($q,"The Proceedings Management tool is now closed for IETF $meeting_num.<br>The cut off date of Submission Corrections was $cut_off_date") if $is_over;
  }
} else {
  my $frozen=db_select($dbh,"select frozen from proceedings where meeting_num=$meeting_num");
  my $meeting_exist=db_select($dbh,"select count(*) from proceedings where meeting_num=$meeting_num");
  error($q,"You can't upload meeting materials for IETF $meeting_num at this moment") if ($frozen or !$meeting_exist);
}

$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">
<input type="hidden" name="meeting_num" value="$meeting_num">
};
$form_header_noname = qq{<form action="$program_name" method="POST">
<input type="hidden" name="meeting_num" value="$meeting_num">
};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">
};
$form_header_get = qq{<form action="$program_name" method="GET" name="form_get">
<input type="hidden" name="meeting_num" value="$meeting_num">
};
$form_header_upload = qq{<form action="$program_name" method="POST" ENCTYPE="multipart/form-data" name="upload_form">
<input type="hidden" name="meeting_num" value="$meeting_num">
};
$SOURCE_DIR="/a/www/ietf-datatracker/release/PROCEEDINGS";
$first_slide = "sld1.htm";
$html_top = qq|
<link rel="stylesheet" type="text/css" href="$style_url" />
<blockquote>
<h2><center>$program_title</center></h2>
$wg_chair_name logged in 
<br><br>
|;
$html_bottom = qq{
</blockquote>
<BR><BR>
<hr>
<ul><font color="#800000"><b>PLEASE NOTE: It has come to our attention that some versions of Internet Explorer cause this system to fail to accept meeting uploads.  If you experience problems uploading, please use Firefox until this problem is corrected.</b> (Posted by Glen Barney, AMS IT Director)</font><br></ul>
<hr>
<ul>
<li><a href="http://www.ietf.org/instructions/meeting_materials_tool.html">Description of this Tool</a></li>
<li><a href="password_manager.cgi">Change my login information</a></li>
<li>If you require assistance in using this tool, or wish to report a bug, then please send a message to <a href="mailto:ietf-action\@ietf.org">ietf-action\@ietf.org</a>.</li>
<li>To submit your materials via email, please send agendas to <a href="mailto:agenda\@ietf.org">agenda\@ietf.org</a> and minutes/presentation slides to <a href="mailto:proceedings\@ietf.org">proceedings\@ietf.org</a>.</li>

</ul>
};
$meeting_scheduled_field = ($meeting_num==$meeting_num2)?"meeting_scheduled":"meeting_scheduled_old";
$html_body = get_html_body($q);
$dbh->disconnect();
print $q->header("text/html"),
	$q->start_html(-title=>$program_title),
	$q->p($html_top),
	$q->p($html_body),
	$q->p($html_bottom),
	$q->end_html;
exit;

sub get_group_acronym_id_list {
  my $ret_val = "";
  my @List= db_select_multiple($dbh,"select a.group_acronym_id from g_chairs a, groups_ietf b where a.person_or_org_tag=$loginid and a.group_acronym_id=b.group_acronym_id");
  my @List_sec= db_select_multiple($dbh,"select a.group_acronym_id from g_secretaries a, groups_ietf b where a.person_or_org_tag=$loginid and a.group_acronym_id=b.group_acronym_id");
  push @List, @List_sec;
  return "0" if ($#List < 0);
  for my $array_ref (@List) {
    my ($id) = @$array_ref;
    $ret_val .= "$id,";
  }
  chop $ret_val;
  return $ret_val;
}

sub error {
  my ($q,$reason)=@_;
                                                                                                
  print $q->header("text/html"),
        $q->start_html("Error"),
        $q->h1("Error"),
        $q->p("Your request was not processed due to the following error ",
              "occured: "),
        $q->p($q->i($reason)),
        $q->end_html;
  exit;
}

sub get_html_body {
   my $q = shift;
   my $command = $q->param("command");
   my $html_txt;
   unless (my_defined($command)) {
     $html_txt = main_screen($q);
   } else {
     my $func = "$command(\$q)";
     $html_txt = eval($func);
   }
   $html_txt .= qq{
   $form_header_bottom
   <input type="hidden" name="command" value="main_screen">
   <input type="submit" value="Main Menu">
   <input type="hidden" name="meeting_num" value="$meeting_num">
   <input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true">
   </form>
   }  if (my_defined($command));
   return $html_txt;
}

sub main_screen {
  my $q=shift;
  #error($q,$meeting_num);
  return select_meeting($q) unless ($meeting_num > 70);
  return display_meeting($q);
}

sub select_meeting {
  my $q=shift;
  my @List=db_select_multiple($dbh,"select meeting_num from proceedings where frozen=0");
  my $options="";
  for my $array_ref (@List) {
    my ($meeting_num_opt) = @$array_ref;
    $options.="<option value=\"$meeting_num_opt\">$meeting_num_opt</option>\n";
  }
  return qq{
<h2>Please select the IETF meeting for which you want to upload your meeting materials</h2>
$form_header_bottom
<input type="hidden" name="command" value="main_screen">
<select name="meeting_num"><option value="0" selected>--Select Meeting--</option>
$options
</select>
&nbsp; &nbsp; 
<input type="submit" value=" Open this Meeting ">
</form><br><br>
};
}

sub display_meeting {
  my $q=shift;
  my $message = $q->param("message") or "";
  my $my_wg_list = "<ul>\n";
  my @List_wg=db_select_multiple($dbh,"select acronym,group_acronym_id from acronym a, groups_ietf b where $meeting_scheduled_field='YES' and b.group_acronym_id=a.acronym_id and b.group_acronym_id in ($group_acronym_id_list) order by acronym");
  for my $array_ref (@List_wg) {
    my ($acronym,$group_acronym_id) = @$array_ref;
    #if ($devel_mode) {
     #if ($testing_group =~ ",$acronym,") {
        $my_wg_list .= "<li><a href=\"$program_name?command=upload_slide_minute&group_acronym_id=$group_acronym_id&meeting_num=$meeting_num\">$acronym</a></li>\n";
 #} else {
  #$my_wg_list .= "<li>$acronym</li>\n";
  #}
  #} else {
	  #$my_wg_list .= "<li><a href=\"$program_name?command=upload_slide_minute&group_acronym_id=$group_acronym_id\">$acronym</a></li>\n";
	  #}
  }
  $my_wg_list .= "</ul>\n";
  $my_wg_list = "<blockquote><i><b>No working group or BOF sessions have been scheduled yet.</b></i></blockquote>" if ($#List_wg < 0);
  my $my_extra_list = ($is_ietf_iab_chair)?qq{<b>Plenaries</b>
<blockquote>
<li><a href="$program_name?command=upload_slide_minute&group_acronym_id=-1&meeting_num=$meeting_num">Wednesday Plenary</a></li>
<li><a href="$program_name?command=upload_slide_minute&group_acronym_id=-2&meeting_num=$meeting_num">Thursday Plenary</a></li>
</blockquote>
}:"";
  my $wg_chair_inst = ($is_wg_chair)?qq{<b>The list below includes those working groups and <b><i>approved</b></i> BOFs that are scheduled to meet at IETF $meeting_num.  You must request a session slot in order for your group(s) to appear on this list. </b><br>&nbsp;<br>
<blockquote>
-<b>To request a session slot for a working group, please use the <a href="https://datatracker.ietf.org/cgi-bin/wg/wg_session_requester.cgi">IETF Meeting Session Request Tool</a>.  To request a session slot for a BOF, please send a message to <a href="mailto:ietf-action\@ietf.org">agenda\@ietf.org</a>. 
Additional information is available at <a href="http://www.ietf.org/instructions/MTG-SLOTS.html">"Requesting Meeting Slots at IETF Meetings."</a><br>
-To upload meeting materials for a scheduled session, please click on the session name below.</b>
$my_wg_list
</blockquote>
}:"";
  if ($is_tut_resp) {
    my @List_tut=db_select_multiple($dbh,"select acronym_id,name from acronym where acronym_id in (select group_acronym_id from wg_meeting_sessions where meeting_num=$meeting_num and group_acronym_id < -2) order by name");
    $my_extra_list .= "<br><b>Trainings</b><blockquote>\n";
    for my $array_ref(@List_tut) {
      my ($acronym_id,$name) = @$array_ref;
      $my_extra_list .= "<li><a href=\"$program_name?command=upload_slide_minute&group_acronym_id=$acronym_id&meeting_num=$meeting_num\">$name Training</a></li>\n";
    }
    $my_extra_list .= "</blockquote>\n";
  }
  if ($is_irtf_chair) {
    $my_extra_list .= "<b>IRTF</b>\n<blockquote>\n";
    my @List_irtf=db_select_multiple($dbh,"select a.irtf_id,irtf_name,irtf_acronym,meeting_scheduled from irtf_chairs a, irtf b where a.irtf_id=b.irtf_id and person_or_org_tag=$loginid  order by irtf_name");
    for my $array_ref(@List_irtf) {
      my ($acronym_id,$name,$acronym,$meeting_scheduled) = @$array_ref;
#      if ($meeting_scheduled) {
        $my_extra_list .= "<li><a href=\"$program_name?command=upload_slide_minute&group_acronym_id=$acronym_id&meeting_num=$meeting_num&irtf=$acronym_id\">$name ($acronym)</a></li>\n";
#      } else {
#        $my_extra_list .= "<li>$name (No session is scheduled)</li>\n";
#      }
    }
    $my_extra_list .= "</blockquote>\n";
  }

  my $html_txt = qq{
<h2>IETF $meeting_num</h2>
$message
<hr>
<li><h3>Upload Agenda/Minutes/Presentations</h3>
$wg_chair_inst
<ul>
$my_extra_list
</ul>
</li>
<h3><li><a href="$preliminary_url?meeting_num=$meeting_num">View Meeting Materials Page</a></h3></li>
};
  return $html_txt;
}
sub order_slides {
  my $group_acronym_id=shift;
  my $irtf=shift;
  my $interim=shift;
  my @List = db_select_multiple($dbh,"select id from slides where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim order by order_num");
  my $order_num=0;
  for my $array_ref (@List) {
    my ($id) = @$array_ref;
    $order_num++;
    db_update($dbh,"update slides set order_num='$order_num' where id=$id");
  }
  return 1;
}

sub upload_slide_minute {
  my $q=shift;
  my $dir_name = db_select($dbh,"select dir_name from proceedings where meeting_num=$meeting_num");
  my $group_acronym_id=$q->param("group_acronym_id");
  my $irtf=(defined($q->param("irtf")))?$q->param("irtf"):0;
  my $interim=(defined($q->param("interim")))?$q->param("interim"):0;
  order_slides($group_acronym_id,$irtf,$interim);
  my $group_name="";
  my $group_name_short="";
  my $message = $q->param("message") or "";
  if ($group_acronym_id == 0) {
    return "Please go back and select WG/BOF/Plenary<br>";
  } elsif ($group_acronym_id == -1) {
    $group_name = "Wednesday Plenary";
    $group_name_short = "plenaryw";
  } elsif ($group_acronym_id == -2) {
    $group_name = "Thursday Plenary";
    $group_name_short = "plenaryt";
  } else {
    if ($irtf) {
      $group_name = db_select($dbh,"select irtf_acronym from irtf where irtf_id=$group_acronym_id");
    } else {
      $group_name = db_select($dbh,"select acronym from acronym where acronym_id = $group_acronym_id");
      $group_name = "i".$group_name if ($interim);
    }
    $group_name_short = $group_name;
  }
  my $agenda_filename = db_select($dbh,"select filename from wg_agenda where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim");
  my $button_name = (my_defined($agenda_filename) and $agenda_filename ne "0")?"Replace current agenda":"Upload new agenda";
  my $html_txt =qq{
$message
<h2>IETF $meeting_num: Upload Agenda/Minutes/Presentations: <font color="red">$group_name</font></h2>
<font color="red"><b>** NEW **</font> <a href="#activity_log">Activity Log</a> <font color="red">** NEW **</font></b>
<hr>
};
  if ($group_acronym_id > -3) {
    $html_txt .= qq{
<h2>Agenda</h2>
<h3>Upload New Agenda</h3>
$form_header_upload
<input type="hidden" name="command" value="upload_file">
<input type="hidden" name="group_name" value="$group_name_short">
<input type="hidden" name="group_acronym_id" value="$group_acronym_id">
<input type="hidden" name="irtf" value="$irtf">
<input type="hidden" name="interim" value="$interim">
<input type="hidden" name="slide_minute" value="3">
<table bgcolor="#eeeeee" cellpadding="3" cellspacing="0" border="0" width="600">
<tr>
    <td><ul><li><b>Select file</b><br>
Note: You can only upload agenda in html or plain text (Unix/Mac/Dos). System will not accept agenda in any other format. </li><br>
    <input type="FILE" name="file"></td>
  </tr>
  <tr><td>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp
&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp
<input type="submit" value="$button_name"></td></tr>
</form>
</table>
<h3>Current Agenda</h3>
};
    if (my_defined($agenda_filename) and $agenda_filename ne "0") {
      $html_txt .= qq{<ul><li><a href="http://$host_name/$proceeding_dir/$dir_name/agenda/$agenda_filename" TARGET="_blank">View Agenda</a> &nbsp; &nbsp; &nbsp; &nbsp; <a href="$program_name?command=delete_file&meeting_num=$meeting_num&group_acronym_id=$group_acronym_id&is_minute=2&group_name_short=$group_name_short&irtf=$irtf&interim=$interim" onclick="return confirm('Do you really want to delete this file?');"> [ DELETE ] </a></li></ul><br>
};
    } else {
      $html_txt .= qq{<ul><li><i>NONE</i></li></ul>
};
    }
    my $minute_filename = db_select($dbh,"select filename from minutes where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim");
    my $m_button_name = (my_defined($minute_filename) and $minute_filename ne "0")?"Replace current minutes":"Upload new minutes";
    $html_txt .= qq{
<hr>
<h2>Minutes</h2>
<h3>Upload New Minutes</h3>
$form_header_upload
<input type="hidden" name="command" value="upload_file">
<input type="hidden" name="group_name" value="$group_name_short">
<input type="hidden" name="group_acronym_id" value="$group_acronym_id">
<input type="hidden" name="irtf" value="$irtf">
<input type="hidden" name="interim" value="$interim">
<input type="hidden" name="slide_minute" value="2">
<table bgcolor="#eeeeee" cellpadding="3" cellspacing="0" border="0" width="600">
<tr>
    <td><ul><li><b>Select file</b><br>
Note: You can only upload minutes in html or plain text (Unix/Mac/Dos). System will not accept minutes in any other format. </li><br>
    <input type="FILE" name="file"></td>
  </tr>
  <tr><td>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp
&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp
<input type="submit" value="$m_button_name"></td></tr>
</form>
</table>

<h3>Current Minutes</h3>
};
    if (my_defined($minute_filename) and $minute_filename ne "0") {
      $html_txt .= qq{<ul><li><a href="http://$host_name/$proceeding_dir/$dir_name/minutes/$minute_filename" TARGET="_blank">View Minutes</a> &nbsp; &nbsp; &nbsp; &nbsp; <a href="$program_name?command=delete_file&meeting_num=$meeting_num&group_acronym_id=$group_acronym_id&is_minute=1&group_name_short=$group_name_short&irtf=$irtf&interim=$interim" onclick="return confirm('Do you really want to delete this file?');"> [ DELETE ] </a></li></ul><br>
};
    } else {
      $html_txt .= qq{<ul><li><i>NONE</i></li></ul>
};
    }
  }
$html_txt .= qq{
<hr>
<h2>Presentations</h2>
<h3>Upload New Presentation</h3>
$form_header_upload
<input type="hidden" name="command" value="upload_file">
<input type="hidden" name="group_name" value="$group_name_short">
<input type="hidden" name="group_acronym_id" value="$group_acronym_id">
<input type="hidden" name="irtf" value="$irtf">
<input type="hidden" name="interim" value="$interim">
<input type="hidden" name="slide_minute" value="1">
<table bgcolor="#eeeeee" cellpadding="3" cellspacing="0" border="0" width="600">
  <tr>
    <td><ul><li><b>Name of presentation</b> <br>
    <input type="text" name="slide_name" size="50" value=""></td>
  </tr>

<tr>
    <td><ul><li><b>Select file</b><br>
Note 1: You can only upload a presentation file in txt, pdf, doc, or ppt/pptx. System will not accept presentation files in any other format.
<p>Note 2: All uploaded files will be available to the public immediately on the Preliminary Page.  However, for the Proceedings, ppt/pptx files will be converted to html format and doc files will be converted to pdf format manually by the Secretariat staff.<br>
    <input type="FILE" name="file"></td>
  </tr>
  <tr><td>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp
&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp
<input type="submit" value="Upload Now"></td></tr>
</form>
</table>

<h3>Current Presentations</h3>
( <font size=+1 color=\"red\"> <b> *</b></font> - Waiting to be converted to HTML or PDF format.)<br>
$form_header_noname
<input type="hidden" name="command" value="reorder">
<input type="hidden" name="group_acronym_id" value="$group_acronym_id">
<input type="hidden" name="irtf" value="$irtf">
<input type="hidden" name="interim" value="$interim">
};
  my @List_slides = db_select_multiple($dbh,"select slide_num,slide_type_id,slide_name,order_num,id,in_q from slides where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim order by order_num");
  $html_txt .= "<ul>\n";
  for my $array_ref (@List_slides) {
    my ($slide_num,$slide_type_id,$slide_name,$order_num,$slide_id,$in_q) = @$array_ref;
    my $delete_button = qq{ &nbsp; <a href="$program_name?command=delete_file&meeting_num=$meeting_num&group_acronym_id=$group_acronym_id&is_minute=0&slide_num=$slide_num&group_name_short=$group_name_short&interim=$interim&irtf=$irtf" onclick="return confirm('Do you really want to delete this file?');"> [ DELETE ] </a>};
    my $rename_button = qq{ &nbsp; <a href="$program_name?command=rename_slide&meeting_num=$meeting_num&group_acronym_id=$group_acronym_id&slide_num=$slide_num&interim=$interim&irtf=$irtf&group_name_short=$group_name_short"> [ RENAME ] </a>};
    my $reupload_button = qq{ &nbsp; &nbsp; &nbsp; &nbsp; <a href="$program_name?command=reupload_slide&meeting_num=$meeting_num&group_acronym_id=$group_acronym_id&slide_num=$slide_num&interim=$interim&irtf=$irtf&group_name_short=$group_name_short"> [ REPLACE ] </a>};
    $html_txt .= "<li> <input type=\"text\" name=\"$slide_id\" value=\"$order_num\" size=\"1\"> \n";
    if ($in_q) {
        my $slide_type = ($slide_type_id==4)?"ppt":(($slide_type_id==6)?"pptx":"doc");
        $html_txt .= " <a href=\"http://$host_name/$proceeding_dir/$dir_name/slides/$group_name_short-$slide_num.$slide_type\">$slide_name</a> <font color=\"red\"><b>*</b></font> ";
    } else {
      if ($slide_type_id == 1) {
        $html_txt .= " <a href=\"http://$host_name/$proceeding_dir/$dir_name/slides/$group_name_short-$slide_num/$first_slide\" TARGET=\"_blank\">$slide_name</a> ";
      } elsif ($slide_type_id == 2) {
        $html_txt .= " <a href=\"http://$host_name/$proceeding_dir/$dir_name/slides/$group_name_short-$slide_num.pdf\" TARGET=\"_blank\">$slide_name</a> ";
      } elsif ($slide_type_id ==3) {
        $html_txt .= " <a href=\"http://$host_name/$proceeding_dir/$dir_name/slides/$group_name_short-$slide_num.txt\" TARGET=\"_blank\">$slide_name</a> ";
      } elsif ($slide_type_id ==4) {
        $html_txt .= " <a href=\"http://$host_name/$proceeding_dir/$dir_name/slides/$group_name_short-$slide_num.ppt\" TARGET=\"_blank\">$slide_name</a> ";
      } elsif ($slide_type_id ==5) {
        $html_txt .= " <a href=\"http://$host_name/$proceeding_dir/$dir_name/slides/$group_name_short-$slide_num.doc\" TARGET=\"_blank\">$slide_name</a> ";
      } elsif ($slide_type_id ==6) {
        $html_txt .= " <a href=\"http://$host_name/$proceeding_dir/$dir_name/slides/$group_name_short-$slide_num.pptx\" TARGET=\"_blank\">$slide_name</a> ";
      } elsif ($slide_type_id ==7) {
        $html_txt .= " <a href=\"http://$host_name/$proceeding_dir/$dir_name/slides/$group_name_short-$slide_num.wav\" TARGET=\"_blank\">$slide_name</a> ";
      } elsif ($slide_type_id ==8) {
        $html_txt .= " <a href=\"http://$host_name/$proceeding_dir/$dir_name/slides/$group_name_short-$slide_num.avi\" TARGET=\"_blank\">$slide_name</a> ";
      } elsif ($slide_type_id ==9) {
        $html_txt .= " <a href=\"http://$host_name/$proceeding_dir/$dir_name/slides/$group_name_short-$slide_num.mp3\" TARGET=\"_blank\">$slide_name</a> ";
      }
    }
    $html_txt .= " $reupload_button $rename_button $delete_button</li><br>\n";
  }
  my $reorder_instruction = "To re-order the presentations above, enter the desired order number(number, or number + letter, eg., 1a) into the box provided for each item on the list, and then click <b>RE-ORDER</b> button below.<br>";
  my $submit_button = ($#List_slides > 0)?"$reorder_instruction<input type=\"submit\" value= \" RE-ORDER \">":"";
  my $activity_log=get_wg_proceedings_activity_log($group_acronym_id,$meeting_num);
  $html_txt .= qq{
</ul>
$submit_button
</form>
<hr>
<a name="activity_log">
<h2>Activity Log</h2></a>
$activity_log
<br><br><br>
};
  return $html_txt;
}

sub get_wg_proceedings_activity_log {
  my $group_acronym_id=shift;
  my $meeting_num=shift;
$color1="#cccccc";
$color2="#eeeeee";
$table_header2 = qq{<table cellpadding="1" cellspacing="1" border="0" width="800">
};
  my $color="$color1";
  my $html_text = qq{
$table_header2
<tr bgcolor="$color"><td width="150"><b>action date (ET)</td><td width="150"><b>acted by</td><td><b>action</td></tr>
};
  my @List=db_select_multiple($dbh,"select act_date, act_time, act_by, activity from wg_proceedings_activities where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id order by act_date desc, act_time desc");
  for my $array_ref (@List) {
    my ($act_date,$act_time,$act_by,$activity) = @$array_ref;
    $color = ($color eq $color1)?$color2:$color1;
    my $act_by_name=get_name($act_by);
    $html_text .= "<tr bgcolor=\"$color\"><td>$act_date $act_time</td><td>$act_by_name</td><td>$activity</td></tr>\n";
  }   
  $html_text .= "</table>\n<br><br><br>";
  return $html_text;
}

sub reorder {
  my $q=shift;
  my $prev_order= "-1";
  foreach ($q->param) {
    if (/^\d/) {
      my $slide_id=$_;
      my $order_num = (my_defined($q->param("$slide_id")))?$q->param("$slide_id"):"99";
      error ($q,"Duplicate order number - $order_num") if ($prev_order eq $order_num);
      $prev_order=$order_num;
      $order_num=db_quote($order_num);
      db_update($dbh,"update slides set order_num=$order_num where id=$slide_id");
    }
  }
  $q->param('message'=>"Presentations have been re-ordered.");
  return upload_slide_minute($q);
}

sub upload_file {
  my $q=shift;
  $q->cgi_error and error($q,"Error transferring file: ".$q->cgi_error);
  my $file = $q->param("file")  || error ($q,"No file received.");
  my @temp = split '\.',$file;
  my $slide_type = $temp[$#temp];
  my $group_name=$q->param("group_name");
  my $group_acronym_id=$q->param("group_acronym_id");
  my $slide_minute = $q->param("slide_minute");
  my $activity_text = "";
  $slide_type = lc($slide_type);
  if ($slide_minute == 1) { #Presentation
    if ($slide_type eq "pdf") { #PDF upload
      $slide_type_id=2;
    } elsif ($slide_type eq "txt") { # TXT upload
      $slide_type_id=3;
    } elsif ($slide_type eq "ppt") { # PPT upload
      $slide_type_id=4;
    } elsif ($slide_type eq "doc") { # DOC upload
      $slide_type_id=5;
    } elsif ($slide_type eq "pptx") { # PPTX upload
      $slide_type_id=6;
    } elsif ($slide_type eq "wav") { # WAV upload
      $slide_type_id=7;
    } elsif ($slide_type eq "avi") { # AVI upload
      $slide_type_id=8;
    } elsif ($slide_type eq "mp3") { # MP3 upload
      $slide_type_id=9;
    } else { # Not allowed file type
      error ($q,"Invalid file extension - ".$slide_type);
    }
  } elsif ($slide_minute == 2 or $slide_minute == 3) { #Minutes
    if ($slide_type eq "pdf") { #PDF upload
      $slide_type_id=2;
    } elsif ($slide_type eq "html" or $slide_type eq "htm") { # HTML upload
      $slide_type_id=1;
    } elsif ($slide_type eq "txt") { #Plain text upload
      $slide_type_id=3;
    } else { # Not allowed file type
      error ($q,"Invalid file extension - ".$slide_type);
    }
  } else {
    error ($q,"Invalid file extension - ".$slide_type);
  }
  my $interim = $q->param("interim");
  my $irtf=$q->param("irtf");
  my $sqlStr="";
  my $local_dir = "";
  my $filename = $group_name;
  my $dir_name = db_select($dbh,"select dir_name from proceedings where meeting_num=$meeting_num");
  #my $minute_exist = db_select($dbh,"select count(*) from minutes where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim");
  #unless ($minute_exist) {
  #  db_update($dbh,"insert into minutes (meeting_num,group_acronym_id,filename,irtf,interim) values ($meeting_num,$group_acronym_id,'0',$irtf,$interim)");
  #}
  #my $agenda_exist = db_select($dbh,"select count(*) from wg_agenda where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim");
  #unless ($agenda_exist) {
  #  db_update($dbh,"insert into wg_agenda (meeting_num,group_acronym_id,filename,irtf,interim) values ($meeting_num,$group_acronym_id,'0',$irtf,$interim)");
  #}

  if ($slide_minute ==1) { #Upload SLide
    $local_dir = "slides";
    $slide_name=$q->param("slide_name");
    error($q,"Please enter the name of the presentation.") unless my_defined($slide_name);
    $slide_name = db_quote($slide_name);
    my $slide_num = db_select($dbh,"select max(slide_num) from slides where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim");
    unless (my_defined($slide_num)) {
      $slide_num = 0;
    } else {
      $slide_num++;
    }
    my $order_num = $slide_num+1;
    my $in_q = 0;
    if ($slide_type_id == 4 or $slide_type_id == 5 or $slide_type_id == 6) {
      $in_q = 1;
    }
    $sqlStr = "insert into slides (meeting_num,group_acronym_id,slide_num,slide_type_id,slide_name,irtf,interim,order_num,in_q) values ($meeting_num,$group_acronym_id,$slide_num,$slide_type_id,$slide_name,$irtf,$interim,'$order_num',$in_q)";
    $activity_text = "slide, $slide_name, was uploaded";
    if (defined($q->param("slide_num"))) {
      $slide_num=$q->param("slide_num");
      $sqlStr="update slides set slide_type_id=$slide_type_id,slide_name=$slide_name,in_q=$in_q where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and interim=$interim and slide_num=$slide_num";
      $activity_text = "slide, $slide_name, was re-uploaded";
    }
    $filename .= "-$slide_num.$slide_type";
  } else {#Upload Minute or Agenda
    my $training = ($group_acronym_id < -2)?1:0;
    my $table_name = ($slide_minute == 2)?"minutes":"wg_agenda";
    $local_dir = ($slide_minute == 2)?"minutes":"agenda";
    $activity_text = "$local_dir was uploaded";
    #if ($irtf or $interim or $training) {
    #  db_update($dbh,"delete from $table_name where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim");
    #  db_update($dbh,"insert into $table_name (meeting_num,group_acronym_id,filename,irtf,interim) values ($meeting_num,$group_acronym_id,'0',$irtf,$interim)");
    #}
    my $exist = db_select($dbh,"select count(*) from $table_name where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and filename <> '0' and irtf=$irtf and interim=$interim");
    $filename ="$filename.$slide_type";
    $sqlStr = ($exist)?"update $table_name set filename='$filename' where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num and irtf=$irtf and interim=$interim":"insert into $table_name (meeting_num,group_acronym_id,filename,irtf,interim) values ($meeting_num,$group_acronym_id,'$filename',$irtf,$interim)";
  }
#UPload file first
  my $fh = $q->upload("file", -override=>1);
  unless ($fh) {
    error ($q,"Invalid File - $file, $fh");
  }
  my $type=$q->uploadInfo($fh)->{'Content-Type'};
  seek($fh,0,2);
  my $size=tell($fh);
  seek($fh,0,0);
  my $buffer = "";

  open OUTPUT,">$web_dir/$dir_name/$local_dir/$filename" or error($q, "Can not open the file - $filename");

  binmode $fh;
  binmode OUTPUT;
  while (read($fh,$buffer,BUFFER_SIZE)) {
    print OUTPUT $buffer;
  }
  close OUTPUT;
#Update database here
  my $OUTPATH = "$web_dir/$dir_name/$local_dir/$filename";

 if (-e $OUTPATH) {
   db_update($dbh,$sqlStr);
   add_wg_proceedings_activity($group_acronym_id,$activity_text,$meeting_num,$loginid);
   $q->param('message'=>"File upload was successful - $size bytes.<br>DO NOT refresh this page: you will repeat the last upload action.");
 } else { 
          error($q, "Directory does not exist - $OUTPATH");
        }
 
  return upload_slide_minute($q);
}

sub reupload_slide {
  my $q=shift;
  my $group_acronym_id=$q->param("group_acronym_id");
  my $slide_num = $q->param("slide_num");
  my $interim=$q->param("interim");
  my $irtf=$q->param("irtf");
  my $group_name_short=$q->param("group_name_short");
  my $slide_name=db_select($dbh,"select slide_name from slides where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num and slide_num=$slide_num and interim=$interim");

  return qq{
<h3>Replace Presentation</h3>
$form_header_upload
<input type="hidden" name="command" value="upload_file">
<input type="hidden" name="group_name" value="$group_name_short">
<input type="hidden" name="group_acronym_id" value="$group_acronym_id">
<input type="hidden" name="slide_num" value="$slide_num">
<input type="hidden" name="irtf" value="$irtf">
<input type="hidden" name="interim" value="$interim">
<input type="hidden" name="slide_minute" value="1">
<table bgcolor="#eeeeee" cellpadding="3" cellspacing="0" border="0" width="600">
  <tr>
    <td><ul><li><b>Name of presentation</b> <br>
    <input type="text" name="slide_name" size="50" value="$slide_name"></td>
  </tr>

<tr>
    <td><ul><li><b>Select file</b><br>
Note 1: You can only upload a presentation file in txt, pdf, doc, or ppt. System will not accept presentation files in any other format.
<p>Note 2: All uploaded files will be available to the public immediately on the Preliminary Page.  However, for the Proceedings, ppt files will be converted to html format and doc files will be converted to pdf format manually by the Secretariat staff.<br>
    <input type="FILE" name="file"></td>
  </tr>
  <tr><td>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp
&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp
<input type="submit" value="Upload Now"></td></tr>
</form>
</table>
};
}

sub rename_slide {
  my $q=shift;
  my $group_acronym_id=$q->param("group_acronym_id");
  my $slide_num = $q->param("slide_num");
  my $interim=$q->param("interim");
  my $irtf=$q->param("irtf");
  my $slide_name=db_select($dbh,"select slide_name from slides where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num and slide_num=$slide_num and interim=$interim");
  return qq{
<h3>Please rename the title of the slide and click submit button</h3>
$form_header_post
<input type="hidden" name="command" value="do_rename_slide">
<input type="hidden" name="group_acronym_id" value="$group_acronym_id">
<input type="hidden" name="slide_num" value="$slide_num">
<input type="hidden" name="irtf" value="$irtf">
<input type="hidden" name="interim" value="$interim">
<input type="text" name="slide_name" value="$slide_name" size="45"> &nbsp; &nbsp; 
<input type="submit" value="Submit">
</form>
<br><br><br>
};
}

sub do_rename_slide {
  my $q=shift;
  my $group_acronym_id=$q->param("group_acronym_id");
  my $slide_num = $q->param("slide_num");
  my $slide_name=$q->param("slide_name");
  my $interim=$q->param("interim");
  my $irtf=$q->param("irtf");
  my $old_slide_name=db_select($dbh,"select slide_name from slides where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num and slide_num=$slide_num and interim=$interim");
  my $activity_text="Title of a slide was changed to $slide_name from $old_slide_name";
  $slide_name=db_quote($slide_name);
  db_update($dbh,"update slides set slide_name=$slide_name where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num and slide_num=$slide_num and interim=$interim");
  $q->param('message'=>"Presentation has been renamed.");
  add_wg_proceedings_activity($group_acronym_id,$activity_text,$meeting_num,$loginid);
  return upload_slide_minute($q);
}


sub delete_file {
  my $q=shift;
  my $group_acronym_id=$q->param("group_acronym_id");
  my $is_minute = $q->param("is_minute");
  my $irtf=$q->param("irtf");
  my $interim=$q->param("interim");
  my $sqlStr = "";
  my $deleted_file = "";
  my $activity_text = "";
  if ($is_minute) {
    my $table_name = ($is_minute==1)?"minutes":"wg_agenda";
    $deleted_file = ($is_minute==1)?"minutes/":"agenda/";
    $deleted_file .= db_select($dbh,"select filename from $table_name where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id");
    $sqlStr = "delete from $table_name where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim";
    $activity_text = ($is_minute==1)?"minutes was deleted":"agenda was deleted";
  } else {
    my $slide_num = $q->param("slide_num");
    my $group_name_short=$q->param("group_name_short");
    $deleted_file = "slides/$group_name_short-$slide_num*";
    my $slide_name = db_select($dbh,"select slide_name from slides where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and slide_num=$slide_num");
    $sqlStr = "delete from slides where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and slide_num=$slide_num";
    $activity_text = "slide, $slide_name was deleted";
  }
  my $dir_name = db_select($dbh,"select dir_name from proceedings where meeting_num=$meeting_num");

  system "rm -Rf $web_dir/$deleted_file" if db_update($dbh,$sqlStr);
  add_wg_proceedings_activity($group_acronym_id,$activity_text,$meeting_num,$loginid);
  $q->param('message'=>"File deletion was successful.");
  return upload_slide_minute($q);
}
