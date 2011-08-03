#!/usr/bin/perl
##########################################################################
# Copyright © 2004 and 2003, Foretec Seminars, Inc.
##########################################################################
use lib '/a/www/ietf-datatracker/release';
use GEN_DBUTIL;
use GEN_UTIL;
use IETF;
use CGI;
$host=$ENV{SCRIPT_NAME};
$devel_mode = ($host =~ /devel/)?1:0;
$test_mode = ($host =~ /test/)?1:0;
$dbname = "ietf";
$mode_text = "";
if ($devel_mode) {
  $dbname="develdb";
  $mode_text = "Development Mode db: $dbname";
} elsif ($test_mode) {
  $dbname="testdb";
  $mode_text = "Test Mode db: $dbname";
}
init_database($dbname);

my $q = new CGI;
$style_url="https://datatracker.ietf.org/documents/telechat.css";
$SOURCE_DIR = "/a/www/ietf-datatracker/release";
$program_name = "itelechat.cgi";
$host = $ENV{HTTP_HOST};
$devel_mode = 1 if ($host =~ /mlee/ or $host =~ /localhost/);
$mode_text = ($devel_mode==1)?"DEVEL MODE db: $dbname":"";
$rUser = $ENV{REMOTE_USER};
$loginid = db_select("select id from iesg_login where login_name = '$rUser'");
$loginid = $q->param("loginid") unless ($loginid);
$program_title = "iTelechat v1.0 $mode_text";
$user_name=get_mark_by($loginid);

$table_header = qq{<table cellpadding="0" cellspacing="0" border="0" width="100%">
};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">
<input type="hidden" name="loginid" value="$loginid">};
$form_header_get = qq{<form action="$program_name" method="GET" name="form_get">
<input type="hidden" name="loginid" value="$loginid">};
$white_img = "/images/white_space.gif";
$border_color="2222aa";
$table_color="royalblue";
$main_font_color="000088";
$main_font_face="arial";
$main_menu_button = get_main_menu_button($q);
$no_agenda_selected = "<blockquote><h4>Please select a telechat to display the agenda here</h4></blockquote>";
$thin_border = qq{<tr bgcolor="$border_color" height="2"><td></td></tr>};
$html_top = qq|
<link rel="stylesheet" type="text/css" href="$style_url" />
<font face="Arial">
<center><h1><font color="red" face="times"><b><i>i</i></font><font color="black">Telechat</font></b></h1></center>
|;
$html_bottom = qq{
</font>
};

$html_body = get_html_body($q);

print $q->header("text/html"),
      $q->start_html(-title=>$program_title),
      $q->p($html_top),
      $q->p($html_body),
      $q->end_html;
                                                                                                               

sub get_main_menu_button {
  my $q=shift;
  my $telechat_date = $q->param("telechat_date") if (defined($q));
  my $telechat_date_call = "";
  $telechat_date_call = qq{<input type="hidden" name="telechat_date" value="$telechat_date">} if (my_defined($telechat_date));
  return qq{
<br><br><br>
$table_header
$form_header_post
$thin_border
$telechat_date_call
<input type="hidden" name="command" value="main_menu">
<tr width="100"><td bgcolor="ffffff"  align="center">
<input type="submit" value=" Main Screen ">
</td></tr>
</form>
</table>
};
}

sub get_telechat_date_select_html {
  my $is_new=shift;
  if ($is_new) {
    my @List = db_select_multiple("select telechat_date from telechat");
    my $telechat_date_list = "";
    for $array_ref (@List) {
      my ($date) = @$array_ref;
      $telechat_date_list .= "'$date',";
    }
    if (my_defined($telechat_date_list)) {
      chop($telechat_date_list);
      my $ret_val = "";
      my $date1 = db_select("select date1 from telechat_dates where date1 not in ($telechat_date_list)");
      my $date2 = db_select("select date2 from telechat_dates where date2 not in ($telechat_date_list)");
      my $date3 = db_select("select date3 from telechat_dates where date3 not in ($telechat_date_list)");
      my $date4 = db_select("select date4 from telechat_dates where date4 not in ($telechat_date_list)");
      $ret_val .= "<option value=\"$date1\">$date1</option>\n" if ($date1);
      $ret_val .= "<option value=\"$date2\">$date2</option>\n" if ($date2);
      $ret_val .= "<option value=\"$date3\">$date3</option>\n" if ($date3);
      $ret_val .= "<option value=\"$date4\">$date4</option>\n" if ($date4);
      return $ret_val;
    } else {
      my ($date1,$date2,$date3,$date4) = db_select("select date1,date2,date3,date4 from telechat_dates");
      return qq{
  <option value="$date1">$date1</option>
  <option value="$date2">$date2</option>
  <option value="$date3">$date3</option>
  <option value="$date4">$date4</option>
};
    }
  } else {
    my $ret_val = "";
    my @List = db_select_multiple("select telechat_date from telechat order by telechat_date DESC");
    for $array_ref (@List) {
      my ($date) = @$array_ref;
      $ret_val .= "<option value=\"$date\">$date</option>\n";
    }
    return $ret_val;
  }
}


sub get_html_body {
   my $q = shift;
   my $command = $q->param("command");
   return draw_screen(get_main_content(main_menu($q))) unless defined($command);
   my $func = "$command(\$q)";
   my $body_content = eval($func);
   my $main_content = get_main_content($body_content,$q);
   my $html_txt = draw_screen($main_content,$q);
   
   $html_txt .= qq {
   $form_header
   <input type="hidden" name="command" value="main_menu">
   <input type="hidden" name="loginid" value="$loginid">
   <input type="submit" value=" Main Screen ">
   <input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true">
   </form>
   };
   return $html_txt;
}

sub main_menu {
  my $q = shift;
  my $html_txt = qq{
    <br><br><br><h3>Welcome to the <font color="red" face="times"><i>i</i></font><font color="black">Telechat</font>,<br>
    the IESG Teleconference Moderator's Tool </h3></br><br><br>
<center><b>
<a href="$program_name?command=old_telechat">[ Old Telechat ]</a> 
<a href="$program_name?command=new_telechat"> [ New Telechat ]</a><br>
</b></center>
<br><br><br><br>
};
  return $html_txt;
}

sub draw_screen {
  my $body_content = shift;
  my $q=shift;
  my $agenda_html = $no_agenda_selected;
  my $telechat_date = $q->param("telechat_date") if (defined($q));
  my $telechat_id=get_telechat_id($telechat_date);
  db_update("update telechat set mi_frozen=1 where telechat_id=$telechat_id") if (defined($q) and defined($q->param("freeze_mi")));
  $agenda_html = `$SOURCE_DIR/gen_agenda_mini.pl $program_name show_detail $telechat_date` if (my_defined($telechat_date));
  my $main_content = get_main_content($body_content,$q);
  return qq{
$table_header
<tr bgcolor="$border_color" valign="top">
  <td colspan="3" height="2">
  </td>
</tr>
<tr valign="top">
  <td bgcolor="$table_color" width="260">
    <center><font color="white"><h3>Agenda</h3></center>
    <font size="-1">$agenda_html</font></font>
    <br><br><br><br><br><br><br><br><br><br><br><br><br><br>
    <br><br><br><br><br><br><br><br><br><br><br><br><br><br>
  </td>
  <td bgcolor="$border_color" width="2"></td>
  <td>$body_content
  </td>
</tr>
                                                                                                   
</table>

};
}
sub get_menu_bar {
  my $telechat_date=shift;
  my $telechat_id=get_telechat_id($telechat_date);
  my $telechat_date_call="&telechat_date=$telechat_date";
  my $agenda_item_id = db_select("select min(agenda_item_id) from agenda_items where telechat_id=$telechat_id");
  return qq{
<tr bgcolor="$table_color">
  <td><font size="2"><b>
    <a href="$program_name?command=roll_call$telechat_date_call"> [ Roll Call ] </a> <img src="$white_img" width="22" height="1"> |
    <a href="$program_name?command=bash_agenda$telechat_date_call"> [ Bash Agenda ] </a> <img src="$white_img" width="2" height="1"> |
    <a href="$program_name?command=minute_approval$telechat_date_call"> [ Minute Approval ] </a> <img src="$white_img" width="9" height="1"> |
    <a href="$program_name?command=action_item$telechat_date_call"> [ Action Items ] </a> <br>
    <a href="$program_name?command=show_detail$telechat_date_call&agenda_item_id=$agenda_item_id"> [ Main Agenda ] </a> |
    <a href="$program_name?command=iab_news$telechat_date_call"> [ IAB News ] </a> <img src="$white_img" width=20" height="1"> |
    <a href="$program_name?command=management_issue$telechat_date_call"> [ Management Issues ] </a> | 
    <a href="$program_name?command=wg_news$telechat_date_call"> [ Working Group News ] </a> 
    </b></font>
  </td>
</tr>
$thin_border
};
}

sub get_main_content {
  my $body_content = shift;
  my $q=shift;
  my $telechat_date=$q->param("telechat_date") if (defined($q));
  my $msg = "";
  $msg = $q->param("msg") if (defined($q));
  my $menu_bar = "";
  $menu_bar = get_menu_bar($telechat_date) if (my_defined($telechat_date));
  my $date_bar = "";
  $date_bar = get_date_bar($telechat_date,$msg) if (my_defined($telechat_date));
  my $html_txt = qq{
$table_header
$menu_bar
<tr bgcolor="ffffff">
  <td>
$date_bar
    <blockquote>
    <div id="main_col">
    <font color="$main_font_color" face="$main_font_face">
    $body_content
    </font>
    </div>
    </blockquote>
    $main_menu_button
  </td>
</tr>
</table>
};
  return $html_txt;
}

sub new_telechat {
  my $q=shift;
  my $telechat_date_list = get_telechat_date_select_html(1);
  return qq{<br>
$form_header_post
<input type="hidden" name="command" value="create_telechat">
Select the Date: <select name="telechat_date">
$telechat_date_list
</select>
<input type="submit" value=" Create Telechat ">
</form>
<br>

};
}

sub old_telechat {
  my $q=shift;
  my $telechat_date_list = get_telechat_date_select_html(0);
  return qq{<br>
$form_header_post
<input type="hidden" name="command" value="retrieve_telechat">
<input type="hidden" name="msg" value="***Telechat has been retrieved successfully***">
Select the Date: <select name="telechat_date">
$telechat_date_list
</select>
<input type="submit" value=" Retrieve Telechat ">
</form>
<br>
};
}
sub retrieve_telechat {
  $q=shift;
  my $telechat_date = $q->param("telechat_date");
  my $telechat_id = get_telechat_id($telechat_date);
  my $frozen = db_select("select frozen from telechat where telechat_id=$telechat_id");
  system "$SOURCE_DIR/gen_agenda_item_table.pl $telechat_date" unless ($frozen);

  return roll_call($q);
}

sub create_telechat {
  my $q=shift;
  my $telechat_date = $q->param("telechat_date");
  return "Error on creating a new telechat" unless db_update("insert into telechat (telechat_date) values ('$telechat_date')");
  my $telechat_id = db_select("select max(telechat_id) from telechat");
  my @List = db_select_multiple("select person_or_org_tag from telechat_users");
  for $array_ref (@List) {
    my ($person_or_org_tag) = @$array_ref;
    db_update("insert into roll_call values ($telechat_id,$person_or_org_tag,1,0)");
    db_update("insert into bash_agenda values ($telechat_id,'',0,'')");
  }
  system "$SOURCE_DIR/gen_agenda_item_table.pl $telechat_date";

  $q->param(msg=>"***New Telechat session was created successfully***");
  return roll_call($q);

}

sub view_telechat {
  my $q=shift;
  my $telechat_date = $q->param("telechat_date");
  my $html_txt = qq{
<h3>Click the menu button displayed above to navigate the sections</h3>
};
  return $html_txt;
}
sub freeze_telechat {
  my $q=shift;
  my $telechat_date = $q->param("telechat_date");
  my $telechat_id  = db_select("select telechat_id from telechat where telechat_date='$telechat_date'");
  db_update("update telechat set frozen = 1 where telechat_id=$telechat_id");
  return roll_call($q);
}

sub get_date_bar {
  my $telechat_date = shift;
  my $msg = shift;
  my $telechat_id  = db_select("select telechat_id from telechat where telechat_date='$telechat_date'");
  my $frozen = db_select("select frozen from telechat where telechat_id=$telechat_id");
  my $freeze_button = ($frozen)?"<td><b>This is a frozen Telechat</b></td>":qq{<td>$form_header_post <input type="hidden" name="command" value="freeze_telechat">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="msg" value="***This telechat is now frozen***">
<input type="submit" value="Freeze this telechat">
</form></td>};
  return qq{
$table_header
<tr bgcolor="ccccff"><td>
<font size="-1"><b>
ID: $telechat_id TELECHAT DATE: $telechat_date &nbsp; &nbsp; &nbsp; <font color="red">$msg</font>
</b></font>
</td>
$freeze_button
</form></td>
</tr>
$thin_border
</table>
<br><br>
};
                                                                                                    
}

sub roll_call {
  my $q=shift;
  my $telechat_date = $q->param("telechat_date");
  my $telechat_id  = db_select("select telechat_id from telechat where telechat_date='$telechat_date'");
  my $sqlStr_absent = qq{select first_name, last_name
from telechat_users a, person_or_org_info b, roll_call c
where a.person_or_org_tag = b.person_or_org_tag
and a.person_or_org_tag = c.person_or_org_tag
and attended = 0 and telechat_id=$telechat_id
order by last_name, first_name
};
  my @List_absent = db_select_multiple($sqlStr_absent);
  my $absentees = "";
  for $array_ref (@List_absent) {
    my ($first_name,$last_name) = @$array_ref;
    $absentees .= "$first_name $last_name <br>\n";
  }
  $absentees = qq{"The following people have sent in regrets for this teleconference"<br><br>
<b>
$absentees
</b>
<br>
} if (my_defined($absentees));
  my $sqlStr = qq{select a.person_or_org_tag, first_name, last_name, affiliated_org
from telechat_users a, person_or_org_info b
where a.person_or_org_tag = b.person_or_org_tag
order by last_name, first_name
};
  my $user_list = "";
  my @List = db_select_multiple($sqlStr);
  for $array_ref (@List) {
    my ($person_or_org_tag,$first_name,$last_name,$affiliated_org) = @$array_ref;
    my $sqlStr = "select attended from roll_call where person_or_org_tag=$person_or_org_tag and telechat_id=$telechat_id";
    my $checked = numtocheck(db_select($sqlStr));
    $user_list .= "<li><input type=\"checkbox\" name=\"$person_or_org_tag\" $checked> $first_name $last_name / $affiliated_org</li>\n";
  }
  my $temp_attendee_list = "";
  my @tempList = db_select_multiple("select last_name,first_name,affiliation from temp_telechat_attendees where telechat_id=$telechat_id");
  for my $array_ref (@tempList) {
    my ($last_name,$first_name,$affiliation) = @$array_ref;
    $temp_attendee_list .= "$first_name $last_name / $affiliation<br>\n";
  }
  my $html_txt = qq{
  <h3>Roll Call</h3>
$absentees
<h3>Check the box for whom is attending this telechat and click update button</h3>
  $form_header_post
  <input type="hidden" name="command" value="update_roll_call">
  <input type="hidden" name="telechat_id" value="$telechat_id">
  <input type="hidden" name="telechat_date" value="$telechat_date">
  $user_list
  <BR>
  <input type="submit" value=" Update ">
  </form>
<br>
  <h3>Guest Attendee</h3>
  $form_header_post
  <input type="hidden" name="command" value="add_temp_attendee">
  <input type="hidden" name="telechat_id" value="$telechat_id">
  <input type="hidden" name="telechat_date" value="$telechat_date">
  <b>First Name: <input type="text" name="first_name" size="25"> 
  Last Name: <input type="text" name="last_name" size="25"><br>
  Affiliation: <input type="text" name="affiliation" size="35"></b> 
  <input type="submit" value=" Add this attendee to this Telechat "><br>
  </form>
  <h3>Current Temp Attendee(s)</h3>
$temp_attendee_list
};
  return $html_txt;
}

sub update_roll_call {
  my $q=shift;
  my $telechat_id = $q->param("telechat_id");
  my $result_msg="***ERROR: Updating Attendees List was not successful***";
  db_update ("update roll_call set attended=0 where telechat_id=$telechat_id");
  my $error = 0;
  foreach ($q->param) {
    if (/^\d/) {
      my $person_or_org_tag = $_;
      if (db_select("select count(*) from roll_call where person_or_org_tag=$person_or_org_tag and telechat_id=$telechat_id")) {
        $error=1 unless (db_update("update roll_call set attended=1 where person_or_org_tag=$person_or_org_tag and telechat_id=$telechat_id"));
      } else {
        $error=1 unless (db_update("insert into roll_call values ($telechat_id,$person_or_org_tag,1,1)"));
      }
    }
  }
  if ($error) {
    $result_msg= "***Attendees list was NOT updated successfully***";
  } else {
    $result_msg= "***Attendees list was updated successfully***";
  }
  $q->param(msg => $result_msg);
  return roll_call($q);
}

sub add_temp_attendee {
  my $q=shift;
  my $telechat_id = $q->param("telechat_id");
  my $first_name = db_quote($q->param("first_name"));
  my $last_name = db_quote($q->param("last_name"));
  my $affiliation = db_quote($q->param("affiliation"));
  my $result_msg="***ERROR: Adding Temp Attendees was not successful***";
  my $error = (db_update("insert into temp_telechat_attendees (telechat_id,last_name,first_name,affiliation) values ($telechat_id,$last_name,$first_name,$affiliation)") == 0)?1:0;
  if ($error) {
    $result_msg= "***ERROR: Temp Attendee was NOT added successfully***";
  } else {
    $result_msg= "***Temp Attendee was added successfully***";
  }
  $q->param(msg => $result_msg);
  return roll_call($q);
}

sub get_old_position {
  my $ballot_id=shift;
  my $ad_id=shift;
  return "yes" if (db_select("select count(ballot_id) from ballots where ballot_id=$ballot_id and ad_id=$ad_id and yes_col = 1"));
  return "no" if (db_select("select count(ballot_id) from ballots where ballot_id=$ballot_id and ad_id=$ad_id and no_col=1"));
  return "discuss" if (db_select("select count(ballot_id) from ballots where ballot_id=$ballot_id and ad_id=$ad_id and discuss=1"));
  return "abstain" if (db_select("select count(ballot_id) from ballots where ballot_id=$ballot_id and ad_id=$ad_id and abstain=1"));
  return "recuse" if (db_select("select count(ballot_id) from ballots where ballot_id=$ballot_id and ad_id=$ad_id and recuse=1"));
  return "error";
}

sub update_all_votes {
  my $q=shift;
  my $telechat_date=$q->param("telechat_date");
  my $telechat_id=get_telechat_id($telechat_date);
  my $ballot_id=$q->param("ballot_id");
  foreach ($q->param) {
    if (/^\d/) {
      my $ad_id = $_;
      my $col_name = $q->param("$ad_id");
      my $new_position = $col_name;
      $new_position =~ s/_col//g;
      my $exists = db_select("select count(ad_id) from ballots where ballot_id=$ballot_id and ad_id=$ad_id");
      my $ad_name = get_mark_by($ad_id);
      if ($exists) {
        my $old_position = get_old_position($ballot_id,$ad_id);
        unless ($new_position eq $old_position) {
          my $existing_discuss = db_select("select discuss from ballots where ballot_id=$ballot_id and ad_id=$ad_id");
          db_update("update ballots set yes_col=0,no_col=0,discuss=0,abstain=0,recuse=0 where ballot_id=$ballot_id and ad_id=$ad_id");
          db_update ("update ballots set discuss=-1 where ballot_id=$ballot_id and ad_id=$ad_id") if ($existing_discuss != 0);
          db_update("update ballots set $col_name = 1 where ballot_id=$ballot_id and ad_id=$ad_id");
          $new_position=format_position($new_position);
          $old_position=format_position($old_position);
          my $comment_text = "[Ballot Position Update] Position for $ad_name has been changed to $new_position from $old_position";
          add_document_comment(999,$ballot_id,$comment_text,1);
        }
      } else {
        db_update("insert into ballots values (null,$ballot_id,$ad_id,0,0,0,0,0,0)");
        db_update("update ballots set $col_name = 1 where ballot_id=$ballot_id and ad_id=$ad_id");
        $new_position = "No Objection" if ($new_position eq "no");
        my $comment_text = "[Ballot Position Update] New position, $new_position, has been recorded for $ad_name";
        add_document_comment(999,$ballot_id,$comment_text,1);
      }
    }
  }
  $q->param('msg'=>"Ballot Positions were updated");
  return show_detail($q);
}

sub format_position {
  my $pos=shift;
  if ($pos eq "yes") {
    return "Yes";
  } elsif ($pos eq "no") {
    return "No Objection";
  } elsif ($pos eq "discuss") {
    return "Discuss";
  } elsif ($pos eq "abstain") {
    return "Abstain";
  } elsif ($pos eq "recuse") {
    return "Recuse";
  } else {
    return $pos;
  }
  return $pos;
}

sub show_detail {
  my $q=shift;
  my $telechat_date=$q->param("telechat_date");
  my $telechat_id=get_telechat_id($telechat_date);
  my $agenda_item_id=$q->param("agenda_item_id");
  my $max_item_id = db_select("select max(agenda_item_id) from agenda_items where telechat_id=$telechat_id");
  my $min_item_id = db_select("select min(agenda_item_id) from agenda_items where telechat_id=$telechat_id");
  my $prev_item_id = ($agenda_item_id == $min_item_id)?0:$agenda_item_id-1;
  my $next_item_id = ($agenda_item_id == $max_item_id)?0:$agenda_item_id+1;
  my $prev_button = qq{<a href="$program_name?command=show_detail&telechat_date=$telechat_date&agenda_item_id=$prev_item_id">&lt;&lt; Previous Item</a>};
  my $next_button = qq{<a href="$program_name?command=show_detail&telechat_date=$telechat_date&agenda_item_id=$next_item_id">Next Item &gt;&gt;</a>};
  $prev_button = "" unless ($prev_item_id);
  $next_button = "" unless ($next_item_id);
  my ($ballot_id,$group_acronym_id,$agenda_cat_id,$item_num,$total_num) = db_select("select ballot_id,group_acronym_id,agenda_cat_id,item_num,total_num from agenda_items where agenda_item_id=$agenda_item_id");
  my $ad_id = db_select("select job_owner from id_internal where ballot_id=$ballot_id and primary_flag=1");
  my $wg_name = "";
  unless ($ballot_id) {  # WG Action
    $ad_id = db_select("select id from iesg_login a, group_internal b where b.group_acronym_id=$group_acronym_id and b.token_name=a.first_name");
    my ($acronym,$name) = db_select("select acronym,name from acronym where acronym_id=$group_acronym_id");
    $wg_name = "$name ($acronym)";
  }
  my $token_name = get_mark_by($ad_id);
  #my $token_name = ($ballot_id>0)?get_mark_by($ad_id):db_select("select token_name from group_internal where group_acronym_id=$group_acronym_id");
  #my $wg_name = ($group_acronym_id>0)?db_select("select acronym from acronym where acronym_id=$group_acronym_id"):"";
  $wg_name = "<b>WG Name: $wg_name</B><br>" if (my_defined($wg_name));
  my $header = db_select("select agenda_cat_value from agenda_cat where agenda_cat_id=$agenda_cat_id");
  $header =~ s/\n/<br>/g;
  my $filename_set = get_filename_set($ballot_id,4);
  my $num_discuss = db_select("select count(*) from ballots a, iesg_login b, telechat_users c where ballot_id=$ballot_id and discuss=1 and a.ad_id=b.id and b.person_or_org_tag=c.person_or_org_tag and is_iesg=1");
  my $num_iesg = db_select("select count(*) from telechat_users where is_iesg=1");
  my $num_voted = db_select("select count(*) from ballots a,telechat_users b, iesg_login c where ballot_id=$ballot_id and is_iesg=1 and a.ad_id=c.id and c.person_or_org_tag=b.person_or_org_tag");
  my $num_open_position = $num_iesg - $num_voted;
  my $html_txt = qq{<a name="top"></a>
$prev_button $next_button
  <h3>$header</h3><b>$item_num of $total_num<br>$filename_set</b> <a href="#writeup">Ballot Writeup</a><br>
$wg_name
};
  if ($header =~ /For Action/) {
    my $iesg_list = get_iesg_select_list($ad_id);
    $html_txt .= qq{
<font size=+2 color="red">"Brian, would you like to start the discussion on assigning it?"</font>
$form_header_post
<input type="hidden" name="command" value="update_item_status">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="agenda_item_id" value="$agenda_item_id">
<select name="new_assign">$iesg_list</select>
<br><br>
<input type="submit" value=" ASSIGN ">
</form>
<br>
}
  } else {
    $html_txt .= qq{
Token: $token_name
<br>
};
    my $checked_0 = "";
    my $checked_1 = "";
    my $checked_2 = "";
    my $checked_3 = "";
    my $checked_4 = "";
    my ($agenda_item_status_id,$iana_note,$other_note) = db_select("select agenda_item_status_id,iana_note,other_note from agenda_items where agenda_item_id=$agenda_item_id");
    eval("\$checked_$agenda_item_status_id = \"checked\"");
    my $wg_or_ind = ($header =~ /Individual/)?"an individual":"a working group";
    my ($note_draft_by,$agenda_note_cat_id) = db_select("select note_draft_by,agenda_note_cat_id from agenda_items where agenda_item_id=$agenda_item_id");
    my $option1_selected = ($agenda_note_cat_id==1)?"selected":"";
    my $option2_selected = ($agenda_note_cat_id==2)?"selected":"";
    my $option3_selected = ($agenda_note_cat_id==3)?"selected":"";
    $note_draft_by = $ad_id unless ($note_draft_by > 0);
    my $iesg_list = get_iesg_select_list($note_draft_by);
    my $state_list = get_state_list(20);
    my $sub_state_list = get_sub_state_select(-2);
    $html_txt .=qq{
Number of Open Positions: $num_open_position
<br><br>
<font size=+1 color="green">"Would you like to state a position?"</font>
$table_header
<tr><th></th><th align="center" width="100">Yes</th><th align="center" width="100">No Objection</th><th align="center" width="100">Discuss</th><th align="center" width="100">Abstain</th><th align="center" width="100">Recuse</th>
$form_header_post
<input type="hidden" name="command" value="update_all_votes">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="agenda_item_id" value="$agenda_item_id">
};
      my $sqlStr = qq{select first_name,last_name, attended, a.person_or_org_tag
from telechat_users a,person_or_org_info b, roll_call c
where b.person_or_org_tag=c.person_or_org_tag and b.person_or_org_tag=a.person_or_org_tag and
c.telechat_id=$telechat_id and a.is_iesg=1
order by b.last_name};
      my @List = db_select_multiple($sqlStr);
      for $array_ref (@List) {
        my ($first_name,$last_name,$attended,$person_or_org_tag) = @$array_ref;
        my ($yes_col,$no_col,$discuss,$abstain,$recuse,$ad_id) = db_select("select yes_col,no_col,discuss,abstain,recuse,ad_id from ballots a, iesg_login b where b.person_or_org_tag=$person_or_org_tag and b.id=a.ad_id and ballot_id = $ballot_id");
        $ad_id = db_select("select id from iesg_login where person_or_org_tag=$person_or_org_tag") unless defined($ad_id);
        my ($yes_checked,$no_checked,$discuss_checked,$abstain_checked,$recuse_checked);
        $yes_checked = "checked" if ($yes_col);
        $no_checked = "checked" if ($no_col);
        $discuss_checked = "checked" if ($discuss==1);
        $abstain_checked = "checked" if ($abstain);
        $recuse_checked = "checked" if ($recuse);
        my $bg_color="ffffff";
        unless ($attended) {
          $bg_color="777777";
        } elsif (($yes_col + $no_col + $abstain + $recuse == 0) and ($discuss != 1)) { #No Position
          $bg_color="00dd00";
        } elsif ($discuss == 1) { #Discuss position
          $bg_color="ff0000";
        }
        $html_txt .= qq{<tr bgcolor="#$bg_color"><td>$first_name $last_name</td>
<td align="center"><input type="radio" name="$ad_id" value="yes_col" $yes_checked> </td>
<td align="center"><input type="radio" name="$ad_id" value="no_col" $no_checked> </td>
<td align="center"><input type="radio" name="$ad_id" value="discuss" $discuss_checked></td>
<td align="center"><input type="radio" name="$ad_id" value="abstain" $abstain_checked></td>
<td align="center"><input type="radio" name="$ad_id" value="recuse" $recuse_checked></td>
</tr>
};
      }
      $html_txt .= "<tr><td colspan=\"6\"><input type=\"submit\" value=\"Update\"></td></tr></form></table>\n";
                                                                                          
      if ($num_discuss >0) {
        my $is_are = ($num_discuss==1)?"is":"are";
        my $discuss_text = ($num_discuss==1)?"discuss":"discusses";
        my $them_or_it = ($num_discuss==1)?"it":"them";
        my @temp = split ' ',$token_name;
        my $ad_name = $temp[0];
        $html_txt .= qq{
<br><b>*<font size=+1 color="red">"$ad_name, There $is_are $discuss_text in the tracker on this draft.  Do we need to talk about $them_or_it now?"</b></font><br><br>
};
      }

    if ($header =~ /Protocol/) { # Protocol Action
      $html_txt .= qq{
$form_header_post
<input type="hidden" name="command" value="update_item_status">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="agenda_item_id" value="$agenda_item_id">
                                                                                                                 
<b>* The document</b><br>
<input type="radio" name="agenda_item_status_id" value="1" $checked_1>
"Remains under discussion by the IESG"
<select name="next_state_id">$state_list</select>$sub_state_list</select><br>
&nbsp; &nbsp; &nbsp; IANA Note: <textarea name="iana_note" cols="80" rows="3">$iana_note</textarea><br>
<input type="radio" name="agenda_item_status_id" value="2" $checked_2>
Has been approved by the IESG. The Secretariat will send $wg_or_ind submission Protocol Action announcement.<br>
<input type="radio" name="agenda_item_status_id" value="3" $checked_3>
Needs Note that includes the
<select name="agenda_note_cat_id"><option value="0"></option>
<option value="1" $option1_selected>IRTF or RFC Editor's Note</option>
<option value="2" $option2_selected>IESG Note</option>
<option value="3" $option3_selected>Other Note</option>
</select> to be drafted by <select name="note_draft_by">$iesg_list</select><br>
&nbsp; &nbsp; &nbsp; Other Note: <textarea name="other_note" cols="80" rows="3">$other_note</textarea>
<br>
<input type="submit" value="Update">
</form>
                                                                                                                 
};
    } elsif ($header =~ /Document Action/) { # Document Action
      my $info_exp = ($filename_set =~ /Informational/)?"Informational":"Experimental";
      unless ($header =~ /Via RFC/) {#Via AD submission
        $html_txt .= qq{<br>
<font size=+1 color="red">"Does anyone have an objection to this document being published as an $info_exp RFC?"</font><br>
};
      $html_txt .= qq{
$form_header_post
<input type="hidden" name="command" value="update_item_status">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="agenda_item_id" value="$agenda_item_id">

<input type="radio" name="agenda_item_status_id" value="2" $checked_2>
No. The Secretariat will send $wg_or_ind submission Document Action announcement.<br>
<input type="radio" name="agenda_item_status_id" value="3" $checked_3>
No but it needs a note. The secretariat will send $wg_or_ind submission Document Action announcement that includes the
<select name="agenda_note_cat_id"><option value="0"></option>
<option value="1" $option1_selected>IRTF or RFC Editor's Note</option>
<option value="2" $option2_selected>IESG Note</option>
<option value="3" $option3_selected>Other Note</option>
</select> to be provided by <select name="note_draft_by">$iesg_list</select><br>
&nbsp; &nbsp; &nbsp; Other Note: <textarea name="other_note" cols="80" rows="3">$other_note</textarea>
<br>
<input type="radio" name="agenda_item_status_id" value="1" $checked_1>
Yes. 
<select name="next_state_id">$state_list</select>$sub_state_list</select><br>
&nbsp; &nbsp; &nbsp; Any other notes the moderators need to make: <textarea name="iana_note" cols="80" rows="3">$iana_note</textarea><br>

<input type="submit" value=" UPDATE "><br></form>                                                                                                               
};
      } else { # Via RFC Editor
        $html_txt .= qq{<br>
<font size=+1 color="red">"Does anyone have an objection to the IRSG or RFC Editor publishing this document as an $info_exp RFC?"</font><br>
};
      $html_txt .= qq{
$form_header_post
<input type="hidden" name="command" value="update_item_status">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="agenda_item_id" value="$agenda_item_id">
<input type="hidden" name="agenda_note_cat_id" value="1">                                                                                                                 
<input type="radio" name="agenda_item_status_id" value="2" $checked_2>
No; the document is APPROVED.  The Secretariat will send a standard "no problem" message to the IRTF or RFC Editor.<br>
<input type="radio" name="agenda_item_status_id" value="3" $checked_3>
No, but it needs a note;the document is APPROVED. The secretariat will send a "no problem" meesage to the IRTF or RFC Editor that includes the note to be drafted by <select name="note_draft_by">$iesg_list</select><br>
<br>
<input type="radio" name="agenda_item_status_id" value="1" $checked_1>
Yes; the document is NOT APPROVED. "The Secretariat will send the standard "Do Not Publish" message to the IRTF or RFC Editor.
<input type="hidden" name="next_state_id" value="34">
<input type="hidden" name="sub_state_id" value="0">
<input type="hidden" name="iana_note" value="">
<br>
<input type="radio" name="agenda_item_status_id" value="4" $checked_4>
Yes, but the IESG wants to clarify why the document is NOT APPROVED. The secretariat will send a "Do Not Publish" meesage that includes additional text clarifying the IESG's position to the IRTF or RFC Editor. <select name="note_draft_by2">$iesg_list</select> will draft the additional text.
<input type="hidden" name="next_state_id2" value="33">


<br><br>
<input type="submit" value=" UPDATE "><br></form>                                                                                                                  
};

      }
    } # End of Document Action 
     else { #WG Action
       my ($agenda_cat_id,$wg_action_status,$wg_action_status_sub) = db_select("select agenda_cat_id,wg_action_status,wg_action_status_sub from agenda_items where agenda_item_id=$agenda_item_id");
       $html_txt .= qq{
$form_header_post
<input type="hidden" name="command" value="update_wg_status">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="agenda_item_id" value="$agenda_item_id">
};
       my $checked_1 = "";
       my $checked_2 = "";
       my $checked_3 = "";
       my $wg_sub_checked_1 = "";
       my $wg_sub_checked_2 = "";
       my $wg_sub_checked_3 = "";
       eval ("\$checked_$wg_action_status = \"checked\"");
       eval ("\$wg_sub_checked_$wg_action_status_sub = \"checked\"");
       if ($agenda_cat_id == 16) { #WG Creation, Proposed for IETF Review
         $html_txt .= qq{<br>
<b>Does anyone have an objection to the creation for this working group being sent for EXTERNAL REVIEW?</b><br><br>
<input type="radio" name="wg_action_status" value="1" $checked_1> External Review APPROVED; "The Secretariat will send a Working Group Review announcement with a copy to new-work and place it back on the agenda for the next telechat."<br><br>
<input type="radio" name="wg_action_status" value="2" $checked_2> External Review NOT APPROVED;
<blockquote>
<input type="radio" name="wg_action_status_sub" value="1" $wg_sub_checked_1> The Secretariat will wait for instructions from <select name="note_draft_by">$iesg_list</select><br>
<input type="radio" name="wg_action_status_sub" value="2" $wg_sub_checked_2> The IESG decides the document needs more thime in INTERNAL REVIEW.  The Secreatriat will put it back on the agenda for the next teleconference in the same category.<br>
<input type="radio" name="wg_action_status_sub" value="3" $wg_sub_checked_3> The IESG has made changes since the charter was seen in INTERNAL REVIEW, and decides to send it back to INTERNAL REVIEW the charter again.
</blockquote>
};
       } elsif ($agenda_cat_id == 17) { #WG Creation, Proposed for IETF Approval
         $html_txt .= qq{<input type="hidden" name="wg_action_status_sub" value="0">
<br>
<b>Does anyone have an objection to the creation of this working group?</b><br><br>
<input type="radio" name="wg_action_status" value="1" $checked_1> No, charter for the new working group is APPROVED, "The Secretariat will send a Working Group Action announcement."<br><br>
<input type="radio" name="wg_action_status" value="2" $checked_2> Yes, the charter is NOT APPROVED; The charter needs more work, or the IESG decides to shelve formation of the working group.  "The Secretariat will await further instruction from <select name="note_draft_by">$iesg_list</select> regarding the creation of the new working group."
<br><br>
};

       } elsif ($agenda_cat_id == 18) { #WG Rechartering, Proposed for IETF Review
         my $wg_acronym = $wg_name;
         $wg_acronym =~ s/WG Name://;
         $html_txt .= qq{<input type="hidden" name="wg_action_status_sub" value="0">
<input type="hidden" name="note_draft_by" value="0">
<br>
<b>Does anyone have an objection with just making the changed to the charter?</b><br><br>
<input type="radio" name="wg_action_status" value="1" $checked_1> No Objection; "The Secretariat will send a Working Group Action: RECHARTER announcement."
<br>
<input type="radio" name="wg_action_status" value="2" $checked_2> Yes; Charter must go for EXTERNAL REVIEW; "The Secretariat will send a Working Group Review: RECHARTER announcement, with a copy to new-work. The Secretariat will place it back on the agenda for the next telechat."
<br>
<input type="radio" name="wg_action_status" value="3" $checked_3> Yes; the IESG decides not to go forward with rechartering the working group; "The Secretariat will await further instruction regarding the charter of $wg_acronym
<br>


};
       } elsif ($agenda_cat_id == 19) { #WG Rechartering, Proposed for IETF Approval
         $html_txt .= qq{<input type="hidden" name="wg_action_status_sub" value="0">
<br>
<b>Does anyone have an objection to the rechartering of this working group?</b><br><br>
<input type="radio" name="wg_action_status" value="1" $checked_1> No, recharter for the working group is APPROVED, "The Secretariat will send a Working Group Action: RECHARTER announcement."<br><br>
<input type="radio" name="wg_action_status" value="2" $checked_2> Yes, the charter is NOT APPROVED; The charter needs more work, or the IESG decides to shelve formation of the working group.  "The Secretariat will await further instruction from <select name="note_draft_by">$iesg_list</select> regarding the rechartering of this working group."<br><br>
};
       } else { #Unknown
         $html_txt .= "<h2>Unknown Error</h2>\n";
       }
       $html_txt .= qq{
<br><br>
<input type="submit" value=" Update WG Action Status ">
</form><br><br>
};
    } # End WG Action
  }
  my $ballot_writeup = db_select("select ballot_writeup from ballot_info where ballot_id=$ballot_id");
  $html_txt .= qq{<br><br>
<a name="writeup">Ballot Writeup</a>
<pre>
$ballot_writeup
</pre><br>
<a href="#top">Go back to Top</a>
};
  return $html_txt;
}

sub update_wg_status {
  my $q=shift;
  my $agenda_item_id = $q->param("agenda_item_id");
  my $wg_action_status = $q->param("wg_action_status");
  my $note_draft_by = ($wg_action_status==2)?$q->param("note_draft_by"):0;
  my $wg_action_status_sub = ($wg_action_status==2)?$q->param("wg_action_status_sub"):0;
  db_update("update agenda_items set wg_action_status=$wg_action_status,note_draft_by=$note_draft_by,wg_action_status_sub=$wg_action_status_sub where agenda_item_id=$agenda_item_id",$program_name,$user_name);
  $q->param('msg'=>"WG Action Status was updated");
  return show_detail($q);
}

sub update_item_status {
  my $q=shift;
  my $agenda_item_status_id = $q->param("agenda_item_status_id");
  my $agenda_item_id =  (defined($q->param("agenda_item_id")))?$q->param("agenda_item_id"):0;
  if ($agenda_item_id > 0) {
    my $ballot_id = db_select("select ballot_id from agenda_items where agenda_item_id=$agenda_item_id");
    my $filename = get_filename_set($ballot_id,2);
    my ($ad_id,$id_document_tag,$rfc_flag) = db_select("select job_owner,id_document_tag,rfc_flag from id_internal where ballot_id=$ballot_id and primary_flag=1");
    if (defined($q->param("new_assign"))) {
      my $job_owner=$q->param("new_assign");
      db_update("update id_internal set job_owner=$job_owner where ballot_id=$ballot_id");
    } else {
      db_update("update agenda_items set agenda_item_status_id=$agenda_item_status_id where agenda_item_id = $agenda_item_id");
      my $url="https://datatracker.ietf.org/cgi-bin/idtracker.cgi?command=view_id&dTag=$id_document_tag&rfc_flag=$rfc_flag&ballot_id=$ballot_id";
      if ($agenda_item_status_id == 1) {
        my $next_state_id = $q->param("next_state_id");
        my $next_sub_state_id=$q->param("sub_state_id");
        my $iana_note = db_quote($q->param("iana_note"));
        update_state($ballot_id,$next_state_id,$next_sub_state_id,$test_mode,$devel_mode,$loginid);
        email_to_AD($filename,"","",$ad_id,$url,$test_mode,$devel_mode,$loginid);
        db_update("update agenda_items set iana_note=$iana_note where agenda_item_id=$agenda_item_id");
      } elsif ($agenda_item_status_id == 2) {
        update_state($ballot_id,27,0,$test_mode,$devel_mode,$loginid);
        email_to_AD($filename,"","",$ad_id,$url,$test_mode,$devel_mode,$loginid);
      } elsif ($agenda_item_status_id == 3) {
        my $agenda_note_cat_id = $q->param("agenda_note_cat_id");
        my $note_draft_by = $q->param("note_draft_by");
        my $other_note = db_quote($q->param("other_note"));
        db_update("update agenda_items set agenda_note_cat_id=$agenda_note_cat_id,note_draft_by=$note_draft_by,other_note=$other_note where agenda_item_id=$agenda_item_id");
      } elsif ($agenda_item_status_id == 4) {
        my $note_draft_by = $q->param("note_draft_by2");
        db_update("update agenda_items set note_draft_by=$note_draft_by where agenda_item_id=$agenda_item_id");
        my $next_state_id = $q->param("next_state_id2");
        my $next_sub_state_id=0;
        update_state($ballot_id,$next_state_id,$next_sub_state_id,$test_mode,$devel_mode,$loginid);
        email_to_AD($filename,"","",$ad_id,$url,$test_mode,$devel_mode,$loginid);
      } else {
        return "<h2>Please select one of the radio boxes</h2>";
      }
    }
  }
  $q->param('msg'=>"Agenda Item status was updated");
  return show_detail($q);
}

sub action_item {
  my $q=shift;
  my $telechat_date = $q->param("telechat_date") if (defined($q));
  my $html_txt = "<h3>Action Items List</h3>\n";
  my @List = db_select_multiple("select * from outstanding_tasks order by task_status_id, item_txt");
  for $array_ref (@List) {
    my ($id,$item_txt,$task_status_id,$last_updated_date) = @$array_ref;
    my $item_status_select_list = get_item_status_select_list($task_status_id);
    $html_txt .= qq{$form_header_post
<input type="hidden" name="command" value="update_outstanding_task">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="id" value="$id">
<input type="text" name="item_txt" value="$item_txt" size="65">
<select name="task_status_id">$item_status_select_list</select>
<font size="-2">$last_updated_date</font>
<input type="submit" value="EDIT">
</form>
};
  }
  my $item_status_select_list = get_item_status_select_list(1);
  $html_txt .= "<hr>\n<h3>Add new item</h3>\n$form_header_post<input type=\"hidden\" name=\"command\" value=\"do_add_new_action_item\">\n<input type=\"hidden\" name=\"telechat_date\" value=\"$telechat_date\"><input type=\"text\" name=\"item_txt\" size=\"65\"><select name=\"task_status_id\">$item_status_select_list</select><input type=\"submit\" value=\" Add this item \"></form>";
  return $html_txt;
}

sub get_item_status_select_list {
  my $selected_id = shift;
  my $ret_val = "";
  my @List = db_select_multiple("select task_status_id,task_status_value from task_status");
  for $array_ref (@List) {
    my ($id,$val) = @$array_ref;
    my $selected = "";
    $selected = "selected" if ($selected_id==$id);
    $ret_val .= "<option value=\"$id\" $selected>$val</option>\n";
  }
  return $ret_val;
}

sub do_add_new_action_item {
  my $q=shift;
  my $msg = "***ERROR: Adding a new action item was not successful***";
  my $item_txt = db_quote($q->param("item_txt"));
  my $task_status_id = db_quote($q->param("task_status_id"));
  my $sqlStr = qq{insert into outstanding_tasks (item_txt,task_status_id,last_updated_date)
values ($item_txt,$task_status_id,current_date)};

  $msg="***Adding a new action was successful***" if (db_update($sqlStr));
  $q->param(msg=>"$msg");
  return action_item($q);
}

sub update_outstanding_task {
  my $q=shift;
  my $msg = "***ERROR: Updating a new action item was not successful***";
  my $id=$q->param("id");
  my $item_txt = db_quote($q->param("item_txt"));
  my $task_status_id = db_quote($q->param("task_status_id"));
  my $sqlStr = qq{update outstanding_tasks set
item_txt = $item_txt,
task_status_id=$task_status_id,
last_updated_date=current_date
where id=$id};
                                                                                                    
  $msg="***Updating a new action was successful***" if (db_update($sqlStr));
  $q->param(msg=>"$msg");
  return action_item($q);
}


sub do_edit_bash_agenda {
  my ($telechat_id,$bash_agenda_txt,$change_agenda,$change_agenda_note) = @_;
  ($bash_agenda_txt,$change_agenda_note)=db_quote($bash_agenda_txt,$change_agenda_note);
  my $sqlStr = qq{update bash_agenda set
bash_agenda_txt=$bash_agenda_txt,
change_agenda=$change_agenda,
change_agenda_note=$change_agenda_note
where telechat_id=$telechat_id
};

  return db_update($sqlStr);
}

sub edit_bash_agenda {
  my $q=shift;
  my $telechat_id=$q->param("telechat_id");
  my $bash_agenda_txt=$q->param("bash_agenda_txt");
  my $change_agenda=$q->param("change_agenda");
  my $change_agenda_note=$q->param("change_agenda_note");
  if (do_edit_bash_agenda($telechat_id,$bash_agenda_txt,$change_agenda,$change_agenda_note)) {
    $q->param(msg=>"***Bash Agenda has been updated successfully***");
  } else {
    $q->param(msg=>"***ERROR: Bash Agenda was not updated successfully***");
  }


  return bash_agenda($q);
}

sub bash_agenda {
  my $q=shift;
  my $telechat_date = $q->param("telechat_date") if (defined($q));
  my $telechat_id = 0;
  $telechat_id = db_select("select telechat_id from telechat where telechat_date='$telechat_date'") if (my_defined($telechat_date));
  my ($bash_agenda_txt,$change_agenda,$change_agenda_note) = db_select("select bash_agenda_txt,change_agenda,change_agenda_note from bash_agenda where telechat_id=$telechat_id");
  my $yes_checked = "";
  my $no_checked = "checked";
  if ($change_agenda) {
    $yes_checked = "checked";
    $no_checked = "";
  }
  my $html_txt = qq{
  <h3>Bash Agenda</h3>
"Does anyone want to add anything new to the Agenda?"<br>
$form_header_post
<input type="hidden" name="command" value="edit_bash_agenda">
<input type="hidden" name="telechat_id" value="$telechat_id">
<input type="hidden" name="telechat_date" value="$telechat_date">
<textarea name="bash_agenda_txt" rows="5" cols="75">$bash_agenda_txt</textarea><br>
<br>
"Does anyone have any other changes to the agenda as it stands?"<br>
<input type="radio" name="change_agenda" value="1" $yes_checked> YES<br>
<input type="radio" name="change_agenda" value="0" $no_checked> NO<br>
<textarea name="change_agenda_note" rows="5" cols="75">$change_agenda_note</textarea><br>
<br>
<input type="submit" value=" Submit "><br>
</form>
<h3>Add new Management Issue</h3>
$form_header_post
<input type="hidden" name="command" value="add_mi">
<input type="hidden" name="telechat_id" value="$telechat_id">
<input type="hidden" name="telechat_date" value="$telechat_date">
<b>Title: </b><input type="text" name="template_title" value="$template_title" size="65"><br>
<b>Text: <textarea name="template_text" cols="80" rows="10" wrap="virtual">$template_text</textarea><br>
<b>Secretariat Note<textarea name="note" cols="80" rows="10" wrap="virtual">$note</textarea><br>
<input type="submit" value=" Submit ">
</form>
};
  return $html_txt;
}

sub add_mi {
  my $q=shift;
  my $template_text = db_quote($q->param("template_text"));
  my $template_title=db_quote($q->param("template_title"));
  my $note=db_quote($q->param("note"));
  if ($template_title eq "''") {
    $q->param('msg'=>"Adding a new Management Issue was failed: <i>No Title</i>");
    return bash_agenda($q);
  }
  db_update("insert into templates (template_text,template_title,note,template_type) values ($template_text,$template_title,$note,3)");
  $q->param('msg'=>"Adding a new Management Issue was successful");
  return bash_agenda($q);
}

sub approve_minute {
  $q=shift;
  my $last_telechat_date=$q->param("last_telechat_date");
  my $minute_approved=$q->param("minute_approved");
  my $msg="***ERROR: Updating Minute approval status was NOT successful***";
  my $sqlStr = "update telechat set minute_approved=$minute_approved where telechat_date='$last_telechat_date'";
  $msg="***Minute approval status was updated successfully***" if (db_update($sqlStr)); 
  $q->param(msg=>"$msg");
  return minute_approval($q);
}

sub minute_approval {
  my $q=shift;
  my $telechat_date=$q->param("telechat_date");
  my ($last_telechat_date,$minute_approved) = db_select("select telechat_date,minute_approved from telechat where telechat_date < '$telechat_date' order by telechat_date DESC");
  my $yes_checked = "";
  my $no_checked = "checked";
  if ($minute_approved) {
    $yes_checked="checked";
    $no_checked="";
  }
  my $html_txt = qq{
  <h3>Minute Approval</h3>
"Does everyone agree to the minutes of the $last_telechat_date IESG Teleconference being approved?"<br>
$form_header_post
<input type="hidden" name="command" value="approve_minute">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="last_telechat_date" value="$last_telechat_date">
<input type="radio" name="minute_approved" value="0" $no_checked> Yes<br>
<input type="radio" name="minute_approved" value="1" $yes_checked> No<br>
<br><input type="submit" value="Update">
</form>
<br>
$form_header_get
<input type="hidden" name="command" value="view_minute">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="minute_telechat_date" value="$last_telechat_date">
<input type="submit" value=" View Minute  of $last_telechat_date Telechat">
</form>
<br><br>
$form_header_get
<input type="hidden" name="command" value="view_minute">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="minute_telechat_date" value="$telechat_date"> <input type="submit" value=" View Minute  of Current Telechat"> 
</form>
<br>
<h3>Document Approved since last telechat</h3>
};
my $protocol_action_list = "";
my $document_action_list = "";
my @List1 = db_select_multiple("select a.id_document_tag,filename,revision,status_value,approved_in_minute from internet_drafts a, id_intended_status b, id_internal c where a.intended_status_id=b.intended_status_id and b_approve_date >= '$last_telechat_date' and b_approve_date < '$telechat_date' and a.id_document_tag=c.id_document_tag order by filename");
for my $array_ref (@List1) {
  my ($id_document_tag,$filename,$revision,$status_value,$approved_in_minute) = @$array_ref;
  my $checked=($approved_in_minute)?"":"checked";
  if ($status_value =~ /Informational|Experimental|Historic/) {
    $document_action_list .= "<input type=\"checkbox\" name=\"$id_document_tag\" $checked> $filename-$revision.txt ($status_value)<br>\n";
  } else {
    $protocol_action_list .= "<input type=\"checkbox\" name=\"$id_document_tag\" $checked>  $filename-$revision.txt ($status_value)<br>\n"
  }
}
  $html_txt .= qq{
<font color="red"><b>Please check the box to remove from the minute</b></font><br>
$form_header_post
<input type="hidden" name="command" value="update_approved_list">
<input type="hidden" name="telechat_date" value="$telechat_date">
<li><b>Protocol Action</b><br>
$protocol_action_list
</li><br>
<li><b>Document Action</b><br>
$document_action_list
</li><br>
<input type="submit" value=" Update List ">
</form><br>
};
  return $html_txt;
}

sub update_approved_list {
  my $q=shift;
  my $telechat_id = $q->param("telechat_id");   
  my $result_msg="***ERROR: Updating Approved List was not successful***";   
  my $error = 0;
  db_update("update id_internal set approved_in_minute=1 where approved_in_minute=0");
  foreach ($q->param) {
    if (/^\d/) {
      my $id_document_tag = $_;
      $error=1 unless (db_update("update id_internal set approved_in_minute=0 where id_document_tag=$id_document_tag"));
    }
  }
  if ($error) {
    $result_msg= "***Approved list was NOT updated successfully***";
  } else {
    $result_msg= "***Approved list was updated successfully***";
  }
  $q->param(msg => $result_msg);
  return minute_approval($q);
}

sub view_minute {
  my $q=shift;
  my $minute_telechat_date = $q->param("minute_telechat_date");
  my $minute_txt = `/a/www/ietf-datatracker/release/gen_minute.pl $minute_telechat_date`;
  return qq{<h2>Minute of $minute_telechat_date Telechat</h2>
<hr>
<pre>
$minute_txt
</pre>
<br><br>
};
}

sub get_telechat_id {
  my $telechat_date=shift;
  return db_select("select telechat_id from telechat where telechat_date='$telechat_date'");
}
sub update_wg_spoken {
  my $q=shift;
  my $telechat_date=$q->param("telechat_date");
  my $telechat_id=get_telechat_id($telechat_date);
  my $msg="***Updating WG News spoken list was successful***";
  db_update("update roll_call set wg_spoken=0 where telechat_id=$telechat_id");
  foreach ($q->param) {
    if (/^\d/) {
      my $person_or_org_tag=$_;
      db_update ("update roll_call set wg_spoken=1 where telechat_id=$telechat_id and person_or_org_tag=$person_or_org_tag");
    }
  }
  $q->param(msg=>"$msg");
  return wg_news($q);
}

sub wg_news {
  my $q=shift;
  my $telechat_date=$q->param("telechat_date");
  my $telechat_id=get_telechat_id($telechat_date);
  my $wg_news_txt = db_select("select wg_news_txt from telechat where telechat_id=$telechat_id");
  my $html_txt = qq{
  <h3>Working Group News We Can Use</h3>
<pre>
$wg_news_txt
</pre>
<br>
$form_header_post
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="command" value="update_wg_spoken">
};
  my @List=db_select_multiple("select a.person_or_org_tag,wg_spoken, last_name,first_name,attended from roll_call a, person_or_org_info b, telechat_users c where a.person_or_org_tag=b.person_or_org_tag and a.person_or_org_tag=c.person_or_org_tag and c.is_iesg=1 and telechat_id=$telechat_id order by last_name");
  $html_txt .= "$table_header\n";
  for $array_ref (@List) {
    my ($person_or_org_tag,$wg_spoken,$last_name,$first_name,$attended) = @$array_ref;
    my $checked=numtocheck($wg_spoken);
    my $bg_color = ($attended)?"ffffff":"777777";
    $html_txt .= qq{<tr bgcolor="#$bg_color"><td><input type="checkbox" name="$person_or_org_tag" $checked> $first_name $last_name</td></tr>
};
  }
  $html_txt .= "\n</table><br><input type=\"submit\" value=\" Update \"></form>\n";
  return $html_txt;
}

sub iab_news {
  my $q=shift;
  my $telechat_date=$q->param("telechat_date");
  my $telechat_id=get_telechat_id($telechat_date);
  my $iab_news_txt = db_select("select iab_news_txt from telechat where telechat_id=$telechat_id");
  my $html_txt = qq{
  <h3>IAB News We Can Use</h3>
<pre>
$iab_news_txt
</pre>
<br>
Feature coming soon....
};
  return $html_txt;
}

sub update_management_issue {
  my $q=shift;
  my $discussed_status_id = $q->param("discussed_status_id");
  my $note = db_quote($q->param("note"));
  my $decision = db_quote($q->param("decision"));
  my $template_id = $q->param("template_id");
  db_update("update templates set discussed_status_id=$discussed_status_id, note=$note, decision=$decision where template_id=$template_id");
  $q->param('msg'=>"***Management Issue Discussed status was updated***");
  return management_issue($q);
}

sub management_issue {
  my $q=shift;
  my $telechat_date=$q->param("telechat_date");
  my $telechat_id=get_telechat_id($telechat_date);
  my $sqlStr = "select template_id,template_title,discussed_status_id,note,decision from templates where template_type=3";
  my $html_txt = qq{
  <h3>Management Issues</h3>
<br>};
  my @List = db_select_multiple($sqlStr);
  for $array_ref (@List) {
    my ($template_id,$template_title,$discussed_status_id,$note,$decision) = @$array_ref;
    $html_txt .= qq{
$form_header_post
<input type="hidden" name="command" value="update_management_issue">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="template_id" value="$template_id">
};

    my $checked_1="";
    my $checked_2="";
    my $checked_3="";
    my $func = "\$checked_$discussed_status_id = \"checked\"";
    eval($func);
    $html_txt .= qq{<li>$template_title</li><br>
<input type="radio" name="discussed_status_id" value="1" $checked_1> 
This management issue was discussed.<br>
<input type="radio" name="discussed_status_id" value="2" $checked_2>
This management issue was discussed and will be carried over to the next IESG teleconference.<br>
<input type="radio" name="discussed_status_id" value="3" $checked_3>
This management issue was tabled to the next teleconference.<br>
Action Item:<br>
<textarea name="note" rows="3" cols="70">$note</textarea><br><br>
Decision:<br>
<textarea name="decision" rows="3" cols="70">$decision</textarea><br><br>
<input type="submit" value=" Update ">
</form>
<hr>
};
  }
  return $html_txt;
}


