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
init_database("ietf");
$dbh=get_dbh();
my $q = new CGI;
$style_url="https://www1.ietf.org/css/base.css";
$program_name = "iesg_chairs.cgi";
$program_title = "IESG, Chairs, and Officers Information Manager";
$table_header = qq{<table cellpadding="5" cellspacing="5" border="0" width="800">
};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">};
$form_header_post2 = qq{<form action="$program_name" method="POST" name="form_post2">};
$form_header_post3 = qq{<form action="$program_name" method="POST" name="form_post3">};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">};
$form_header_get = qq{<form action="$program_name" method="GET" name="form_get">};
$TBD_area_director_id = 130;
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
$dbh->disconnect();
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
return qq{<h3>
<li> <a href="$program_name?command=edit_iesg">IESG</a></li><br>
<li> <a href="$program_name?command=edit_chairs">Chairs - IETF, IAB, NOMCOM</a></li><br>
<li> <a href="$program_name?command=edit_liaisons_members">Liaisons Members</a></li><br>
</h3>
<br><br><br><br>
};
}

sub edit_iesg {
  my $q=shift;
  my $current_meeting = db_select($dbh,"select max(meeting_num) from iesg_history");
  $current_meeting = 61 unless $current_meeting;
  my $next_meeting=$current_meeting+1;
  my $iesg_member_history = `/a/www/ietf-datatracker/release/gen_iesg_member_history.pl 1`;
  my $html_txt = qq{
<h2>Current IESG </h2>
<b>**Please click on name to replace an AD**</b><br>
$table_header
};
  my @List_area = db_select_multiple($dbh,"select a.id,first_name,last_name, name from area_directors a, areas b, person_or_org_info c, acronym d where a.area_acronym_id=b.area_acronym_id and b.status_id=1 and a.area_acronym_id=d.acronym_id and a.person_or_org_tag=c.person_or_org_tag order by last_name");
  for my $array_ref (@List_area) {
    my ($area_director_id,$first_name,$last_name,$area_name) = @$array_ref;
    $html_txt .= "<tr><td width=\"200\"><li> <a href=\"$program_name?command=replace_ad&area_director_id=$area_director_id\">$last_name, $first_name</a></li></td><td>$area_name</td></tr>\n";
  }
  $html_txt .= qq{</table>
<br>
$form_header_post
<input type="hidden" name="command" value="save_list">
<input type="hidden" name="meeting_num" value="$next_meeting">
<input type="hidden" name="action" value="save_new">
<input type="submit" value="  Save above list as an IESG as of IETF $next_meeting" onClick="return window.confirm('You are about to create a new IESG list for IETF $next_meeting');">
</form>
$form_header_post2
<input type="hidden" name="command" value="save_list"> 
<input type="hidden" name="meeting_num" value="$current_meeting">
<input type="hidden" name="action" value="update">
<input type="submit" value="  Save above list as an IESG as of IETF $current_meeting" onClick="return window.confirm('You are about replace IESG list for IETF $current_meeting with the list above');">
</form>
$iesg_member_history
<br>
};
  return $html_txt;
}
sub replace_ad {
  my $q=shift;
  my $area_director_id=$q->param("area_director_id");
  my ($person_or_org_tag,$area_name) = db_select($dbh,"select person_or_org_tag,name from area_directors, acronym where id=$area_director_id and area_acronym_id=acronym_id");
  my $name=get_name($person_or_org_tag);
  return qq{
<h2>Relpacing $area_name Director, <i>$name</i>:</h2> 
$form_header_post
<input type="hidden" name="command" value="add_new_member">
<input type="hidden" name="return_function" value="confirm_replace_ad">
<input type="hidden" name="area_director_id" value="$area_director_id">
<b>Enter First Name and Last Name</b>:
<input type="text" name="first_name" size="25"> &nbsp;
<input type="text" name="last_name" size="25"> &nbsp;
<input type="submit" value=" Next Step ">
<br></form>
};
}
sub confirm_replace_ad {
  my $q=shift;
  my $new_person_or_org_tag=$q->param("person_or_org_tag");
  my $area_director_id=$q->param("area_director_id");
  my ($old_person_or_org_tag,$area_name) = db_select($dbh,"select person_or_org_tag,name from area_directors, acronym where id=$area_director_id and area_acronym_id=acronym_id");
  my $old_name=get_name($old_person_or_org_tag);
  my $new_name=get_name($new_person_or_org_tag);
  return qq{
<h2>Relpacing $area_name Director, <i>$old_name</i> with:</h2>
$form_header_post
<input type="hidden" name="command" value="do_replace_ad">
<input type="hidden" name="area_director_id" value="$area_director_id">
<input type="hidden" name="person_or_org_tag" value="$new_person_or_org_tag">
<h2>$new_name</h2>
<b>How do you like to re-assign Area Advisor for those Working Groups of which Area Advisor is not in service any more?</b><br>
&nbsp; &nbsp; &nbsp; <input type="radio" name="aa_option" value="0"> Assign <b>"TBD"</b><br>
&nbsp; &nbsp; &nbsp; <input type="radio" name="aa_option" value="1"> Assign <b>"$new_name"</b><br>
<input type="submit" value=" Replace Area Director ">
<br></form>
};
}

sub do_replace_ad {
  my $q=shift;
  my $person_or_org_tag=$q->param("person_or_org_tag");
  my $area_director_id=$q->param("area_director_id");
  unless (defined($q->param("aa_option"))) {
    return qq{<h1>Error:</h1>
<h3>Please select <i>Re-Assigning Area Advisor</i> option</h3>
};
  }
  my $aa_option = $q->param("aa_option");
  db_update($dbh,"update area_directors set person_or_org_tag=$person_or_org_tag where id=$area_director_id");
  unless ($aa_option) { # TBD for Area Advisors
    db_update($dbh,"update groups_ietf set area_director_id=$TBD_area_director_id where area_director_id=$area_director_id");
  }
  return edit_iesg();
}

sub save_list {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $action=$q->param("action");
  if ($action eq "update") {
    db_update($dbh,"delete from iesg_history where meeting_num=$meeting_num");
  }
  my @List_area = db_select_multiple($dbh,"select a.person_or_org_tag, acronym_id from area_directors a, areas b, acronym d where a.area_acronym_id=b.area_acronym_id and b.status_id=1 and a.area_acronym_id=d.acronym_id");
  for my $array_ref (@List_area) {
    my ($person_or_org_tag,$area_acronym_id) = @$array_ref;
    db_update($dbh,"insert into iesg_history values (null,$meeting_num,$area_acronym_id,$person_or_org_tag)");
  }
  return edit_iesg();
}
 
sub edit_chairs {
  my $q=shift;
  my $ietf_chair_list = get_chair_list(1);
  my $iab_chair_list = get_chair_list(2);
  my $nomcom_chair_list = get_chair_list(3);
  return qq{
<h2>Add New Chair</h2>
$form_header_post
<input type="hidden" name="command" value="add_new_member">
<input type="hidden" name="return_function" value="add_new_chair">
<b>Enter First Name and Last Name</b>: 
<input type="text" name="first_name" size="25"> &nbsp; 
<input type="text" name="last_name" size="25"> &nbsp; 
<input type="submit" value=" Next Step ">
<br></form>
<hr width="300" align="left">
<h2>Chairs History</h2>
<b>**Click on the person to <font color="red">DELETE</font></b><br>
$table_header
<tr><th width="200">IETF</th><th width="200">IAB</th><th width="200">NOMCOM</th></tr>
<tr valign="top"><td>$ietf_chair_list</td>
<td>$iab_chair_list</td>
<td>$nomcom_chair_list</td></tr>
</table>
<br><br><br><br>
};
}

sub get_chair_list {
  my $chair_type_id=shift;
  my $html_txt = "";
  my @List = db_select_multiple($dbh,"select id,present_chair, person_or_org_tag,start_year,end_year from chairs_history where chair_type_id=$chair_type_id order by present_chair desc, end_year desc");
  for my $array_ref (@List) {
    my ($id,$present_chair,$person_or_org_tag,$start_year,$end_year) = @$array_ref;
    $end_year = "PRESENT" if ($present_chair);
    my $name=get_name($person_or_org_tag);
    $html_txt .= "<a href=\"$program_name?command=delete_member&id=$id&table_name=chairs_history\" onClick=\"return window.confirm('You are about to delete this chair');\"><b>$name</b></a> $start_year - $end_year<br><br>\n";
  }
  return $html_txt;
}
sub delete_member {
  my $q=shift;
  my $id=$q->param("id");
  my $table_name=$q->param("table_name");
  db_update($dbh,"delete from $table_name where id=$id");
  return edit_chairs();
}

sub add_new_chair {
  my $q=shift;
  my $person_or_org_tag=$q->param("person_or_org_tag");
  my $name=get_name($person_or_org_tag);
  return qq{
<h3>Complete the following information for new chair, <i>$name</i></h3>
$form_header_post
<input type="hidden" name="command" value="confirm_add_chair">
<input type="hidden" name="person_or_org_tag" value="$person_or_org_tag">
$table_header
<tr><td width="300"><b>Select Chair Type: </td>
<td><select name="chair_type_id">
<option value="0"></option>
<option value="1">IETF</option>
<option value="2">IAB</option>
<option value="3">NOMCOM</option>
</select>
</td>
</tr>
<tr><td><b>Is $name a present chair? </b></td>
<td><b>YES</b> <input type="radio" name="present_chair" value="1"> &nbsp; 
<b>NO</b> <input type="radio" name="present_chair" value="0">
</td></tr>
<tr><td><b>Start Year: </b></td><td><input type="text" name="start_year" size="6"></td></tr>
<tr><td><b>End Year (if not a present chair): </b></td><td><input type="text" name="end_year" size="6"></td></tr>
</table>
<input type="submit" value=" Next Step ">
</form>
};
}

sub confirm_add_chair {
  my $q=shift;
  my $person_or_org_tag=$q->param("person_or_org_tag");
  my $chair_type_id=$q->param("chair_type_id");
  my $present_chair=$q->param("present_chair");
  my $start_year = $q->param("start_year");
  my $end_year=$q->param("end_year");
  my $chair_type_name=get_chair_type_name($chair_type_id);
  my $present_chair_value = ($present_chair)?"YES":"NO";
  $end_year = 0 unless (my_defined($end_year));
  my $name=get_name($person_or_org_tag);
  return qq{
<h3>Confirm the following information for new chair, <i>$name</i>.</h3>
$form_header_post
<input type="hidden" name="command" value="do_add_new_chair">
<input type="hidden" name="chair_type_id" value="$chair_type_id">
<input type="hidden" name="present_chair" value="$present_chair">
<input type="hidden" name="person_or_org_tag" value="$person_or_org_tag">
<input type="hidden" name="start_year" value="$start_year">
<input type="hidden" name="end_year" value="$end_year">
$table_header
<tr><td width="300"><b>Chair Type: </b></td><td><b>$chair_type_name</b></td></tr>
<tr><td width="300"><b>Present Chair? </b></td><td><b>$present_chair_value</b></td></tr>
<tr><td width="300"><b>Start Year: </b></td><td><b>$start_year</b></td></tr>
<tr><td width="300"><b>End Year: </b></td><td><b>$end_year</b></td></tr>
</table><br>
<input type="submit" value="Add this Chair"><br>
</form>
}
}

sub do_add_new_chair {
  my $q=shift;
  my $person_or_org_tag=$q->param("person_or_org_tag");
  my $chair_type_id=$q->param("chair_type_id");
  my $present_chair=$q->param("present_chair");
  my $start_year = $q->param("start_year");
  my $end_year=$q->param("end_year");
  if ($present_chair) {
    db_update($dbh,"update chairs_history set present_chair=0,end_year=$start_year where chair_type_id=$chair_type_id and present_chair=1");
    my $chair_type_name=get_chair_type_name($chair_type_id);
    db_update($dbh,"update chairs set person_or_org_tag=$person_or_org_tag where chair_name='$chair_type_name'");
  }
  db_update($dbh,"insert into chairs_history (chair_type_id,present_chair,person_or_org_tag,start_year,end_year) values ($chair_type_id,$present_chair,$person_or_org_tag,$start_year,$end_year)");
  my $new_chair_name=get_name($person_or_org_tag);
  my $new_chair_email=get_email($person_or_org_tag);
  if ($chair_type_id == 1) {
    db_update($dbh,"update announced_from set announced_from_value='$new_chair_name <$new_chair_email>' where announced_from_id=7");
  } elsif ($chair_type_id == 2) {
    db_update($dbh,"update announced_from set announced_from_value='$new_chair_name <$new_chair_email>' where announced_from_id=9");
  } elsif ($chair_type_id == 3) {
    db_update($dbh,"update announced_from set announced_from_value='$new_chair_name <$new_chair_email>' where announced_from_id=18");
  }

  return edit_chairs();
}
sub get_chair_type_name {
  my $chair_type_id=shift;
  if ($chair_type_id == 1) {
    return "IETF";
  } elsif ($chair_type_id == 2) {
    return "IAB";
  } elsif ($chair_type_id == 3) {
    return "NOMCOM";
  } 
  return "UNKNOWN";
}

sub add_new_member {
  my $q=shift;
  my $first_name=$q->param("first_name");
  my $last_name=$q->param("last_name");
  my $return_function = $q->param("return_function");
  my $area_director_id=$q->param("area_director_id") or "";
  $first_name =db_quote("$first_name%");
  $last_name =db_quote("$last_name%");
  my @List = db_select_multiple($dbh,"select person_or_org_tag from person_or_org_info where first_name like $first_name and last_name like $last_name");
  if ($#List < 0) {
    return qq{<h2>Such a person cannot be found from the IETF Rolodex database</h2>
<h3>Please use <a href="rolodex.cgi">IETF Rolodex</a> to add the person's information first and try again.</h3>
<br><br>
};
  }
  my $html_txt = qq{<h3>Please select a person from the list below</h3>
$form_header_post
<input type="hidden" name="command" value="$return_function">
<input type="hidden" name="area_director_id" value="$area_director_id">
};
  for my $array_ref (@List) {
    my ($person_or_org_tag) = @$array_ref;
    my $name=get_name($person_or_org_tag);
    my $email=get_email($person_or_org_tag);
    $html_txt .= qq{<b>$name (<i>$email</i>)</b>
<input type="radio" name="person_or_org_tag" value="$person_or_org_tag"><br>
};
  }
  $html_txt .= qq{<br>
<input type="submit" value=" Next Step ">
</form><br>
<h2>OR</h2>
<b>Go to <a href="rolodex.cgi">IETF Rolodex</a> to add new person</b><br><br>
};
                                                                                          
  return $html_txt;
}


sub edit_liaisons_members {
  my $q=shift;
  my $member_list = "";
  my @List =db_select_multiple($dbh,"select id,person_or_org_tag,affiliation from liaisons_members");
  for my $array_ref (@List) {
    my ($id,$person_or_org_tag,$affiliation) = @$array_ref;
    my $name=get_name($person_or_org_tag);
    my $company = db_select($dbh,"select affiliated_company from postal_addresses where person_or_org_tag=$person_or_org_tag and address_priority=1");
    $member_list .= "<li> <a href=\"$program_name?command=delete_member&id=$id&table_name=liaisons_members\" onClick=\"return window.confirm('You are about to delete this chair');\"><b>$name</b></a> $company - $affiliation liaison</li><br>\n";
  }
  return qq{
<h2>Add New Liaisons Member</h2>
$form_header_post
<input type="hidden" name="command" value="add_new_member">
<input type="hidden" name="return_function" value="add_new_liaisons_member">
<b>Enter First Name and Last Name</b>:
<input type="text" name="first_name" size="25"> &nbsp;
<input type="text" name="last_name" size="25"> &nbsp; 
<input type="submit" value=" Next Step ">
</form>
<hr width="300" align="left">
<h2>Current Liaisons Member</h2>
<b>**Click the person to <font color="red">DELETE</font>.</b><br><br>
$member_list
<br>
};
}

sub add_new_liaisons_member {
  my $q=shift;
  my $person_or_org_tag=$q->param("person_or_org_tag");
  my $name=get_name($person_or_org_tag);
  return qq{
<h3>Enter the name of affiliated organization (or company) for <i>$name</i></h3>
$form_header_post
<input type="hidden" name="command" value="confirm_add_new_liaisons_member">
<input type="hidden" name="person_or_org_tag" value="$person_or_org_tag">
<input type="text" name="affiliation" size="35"> &nbsp; 
<input type="submit" value=" Next Step ">
</form>
<br>
};
}

sub confirm_add_new_liaisons_member {
  my $q=shift;
  my $person_or_org_tag=$q->param("person_or_org_tag");
  my $name=get_name($person_or_org_tag);
  my $affiliation=$q->param("affiliation");
  return qq{
<h3>Please confirm the following information to add a new Liaisons Member</h3>
<b>Name: $name<br>
Affiliated Organization: $affiliation</b><br>
$form_header_post
<input type="hidden" name="command" value="do_add_new_liaisons_member">
<input type="hidden" name="person_or_org_tag" value="$person_or_org_tag">
<input type="hidden" name="affiliation" value="$affiliation">
<input type="submit" value=" Add this person ">
</form>
<br>
};
}

sub do_add_new_liaisons_member {
  my $q=shift;
  my $person_or_org_tag=$q->param("person_or_org_tag");
  my $affiliation=db_quote($q->param("affiliation"));
  db_update($dbh,"insert into liaisons_members (person_or_org_tag,affiliation) values ($person_or_org_tag,$affiliation)");
  return edit_liaisons_members();
}


