##########################################################################
# Copyright © 2003 and 2002, Foretec Seminars, Inc.
##########################################################################

package IETF;
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(get_name get_email get_intended_status_value get_filename_set add_document_comment get_mark_by get_iesg_select_list get_state_list get_telechat_date_list get_ad_option_str update_comment_log get_option_str generate_error_log update_state notify_state_update get_area_option_str get_sub_state get_sub_state_select is_unique_comment email_to_AD get_ballot_list get_ballot_list_text get_company decrease_revision get_replaced_by_info get_replaces_info get_offset_date get_day_name get_name_from add_session_activity get_hour_val get_session_info get_session_info_text get_cochairs_email get_ad_email_list add_wg_proceedings_activity extra_contact_form error_idst);

use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL;

$LOG_PATH = "/a/www/ietf-datatracker/logs";
$MAX_LENGTH = 40;
$table_header = qq{<table cellpadding="1" cellspacing="1" border="0">
};
$table_header2 = qq{<table cellpadding="1" cellspacing="1" border="0" width="800">
};
$color1="#cccccc";
$color2="#eeeeee";
$STYLE_DEF = "{padding:2px;border-width:1px;border-style:solid;border-color:305076}";
$font_color1 = qq{<font color="000000" face="arial" size="3">};
$font_color2 = qq{<font color="333366" face="arial" size="2">};
$font_color3 = qq{<font color="305076" face="arial" size="3">};

sub error_idst {
  my ($q,$reason,$submission_id)=@_;
  my ($sidebar,$topbar,$bottombar) = db_select("select side_bar_html,top_bar_html,bottom_bar_html  from id_submission_env");
  if (my_defined($submission_id)) {
    $topbar =~ s/##submission_id##/$submission_id/;
  } else {
    $topbar =~ s/\?submission_id=##submission_id##//;
  }
  my $body=qq{
<table height="598" width="858" border="0">
<tr valign="top">
$sidebar
$topbar
<h1>Error</h1>
<p>Your request was not processed due to the following error(s):</p>
<i>$reason</i>
<br><br><br>
$bottombar
</td></tr></table>
};
  print $q->header("text/html"),
        $q->start_html("Error"),
        $body,
        $q->end_html;
  exit;
}

                                                                                
sub extra_contact_form {
  my $remote_program=shift;
  my $remote_command=shift;
  my $ipr_id=shift;
  return qq{
<form name="ipr_contact_form" action="$remote_program" method="post">
<input type="hidden" name="command" value="$remote_command">
<input type="hidden" name="extra_contact_exist" value="yes">
<input type="hidden" name="ipr_id" value="$ipr_id">
  <table border="0" cellpadding="4" cellspacing="0" style="$STYLE_DEF" width="710">
    <tr>
    <td bgcolor="AAAAAA" colspan=2>$font_color2<strong>Contact Information for Submitter of this Update. </strong></font>
    <font color="#FFFFFF">(<strong><small> Required field</small></strong><font color="red"> * </font> )</font></td></tr>
    <tr>
    <td bgcolor="DDDDDD" width="15%">$font_color1<small>Name :</small></font></td>     <td bgcolor="DDDDDD">$font_color1<small><input type="text" onkeypress="return handleEnter(this, event)" name="update_name"  size="25" ></small></font><font color="red"> *</font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Title :</small></font></td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="update_title" size="80" ></td></tr>
    <tr>     <td bgcolor="DDDDDD">$font_color1<small>Department :</small></font></td>
    <td bgcolor="DDDDDD"><input type="text" onkeypress="return handleEnter(this, event)" name="update_department" size="80" ></td></tr>     <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Address1 :</small></font></td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="update_address1" size="80" > <font color="red"> *</font></td></tr>
    <tr>
    <td bgcolor="DDDDDD">$font_color1<small>Address2 :</small></font></td>     <td bgcolor="DDDDDD"><input type="text" onkeypress="return handleEnter(this, event)" name="update_address2" size="80" ></td></tr>
    <tr>     <td bgcolor="EBEBEB">$font_color1<small>Telephone :</small></font></td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="update_telephone" size="25" ><font color="red"> *</font></td></tr>     <tr>
    <td bgcolor="DDDDDD">$font_color1<small>Fax :</small></font></td>
    <td bgcolor="DDDDDD"><input type="text" onkeypress="return handleEnter(this, event)" name="update_fax" size="25" ></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Email :</small></font></td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="update_email" size="35" ><font color="red"> *</font></td></tr>  </table>
                                                                                
<input type="checkbox" name="update_auth">
<b>I am authorized to update this IPR disclosure, and I understand that notification of this update will be provided to the submitter of the original IPR disclosure and to the Patent Holder's Contact.</b><br><br>
<input type="submit" value="Submit"> &nbsp; <input type="button" value="Cancel" onClick="history.go(-1);return true;"><br>
</form>
};
}
                                                                                

sub get_ad_email_list {
  my $group_acronym_id=shift;
  my ($area_name,$area_acronym_id) = db_select("select name,acronym_id from area_group a, acronym b where group_acronym_id=$group_acronym_id and area_acronym_id=acronym_id");
  my $ad_email_list = "";
  my @adList=db_select_multiple("select person_or_org_tag from area_directors where area_acronym_id=$area_acronym_id");
  for my $array_ref (@adList) {
    my ($person_or_org_tag) = @$array_ref;
    my $email = get_email($person_or_org_tag);
    $ad_email_list .= "$email,";
  }
  chop($ad_email_list);
  if ($group_acronym_id < 50) { #IRTF
    my $irtf_chair_id=db_select("select person_or_org_tag from chairs where chair_name='IRTF'");
    $ad_email_list = get_email($irtf_chair_id);
  }
  return $ad_email_list;
}

sub get_cochairs_email {
  my $group_acronym_id=shift;
  my $person_or_org_tag=shift;
  my $cochairs_email="";
  my @List=($group_acronym_id < 50)?db_select_multiple("select person_or_org_tag from irtf_chairs where irtf_id=$group_acronym_id and person_or_org_tag <> $person_or_org_tag"):db_select_multiple("select person_or_org_tag from g_chairs where group_acronym_id = $group_acronym_id and person_or_org_tag <> $person_or_org_tag");
  for my $array_ref (@List) {
    my ($tag) = @$array_ref;
    my $email=get_email($tag);
    $cochairs_email .= "$email,";
  }
  chop($cochairs_email) if my_defined($cochairs_email);
  return $cochairs_email;
}

sub get_session_info_text {
  my $session_id=shift;
  my ($group_acronym_id,$irtf,$num_session,$length_session1,$length_session2,$length_session3,$number_attendee,$conflict1,$conflict2,$conflict3,$conflict_other,$special_req,$requested_by) = db_select("select group_acronym_id,irtf,num_session,length_session1,length_session2,length_session3,number_attendee,conflict1,conflict2,conflict3,conflict_other,special_req,requested_by from wg_meeting_sessions where session_id=$session_id");
  my $wg_name=($irtf)?db_select("select irtf_acronym from irtf where irtf_id=$group_acronym_id"):db_select("select acronym from acronym where acronym_id=$group_acronym_id");
  my $requester_name=get_name($requested_by);
  my $area_name = ($irtf)?"":db_select("select name from area_group a, acronym b where group_acronym_id=$group_acronym_id and area_acronym_id=acronym_id");
  my $length1=get_hour_val($length_session1);
  my $length2=get_hour_val($length_session2);
  my $length3=get_hour_val($length_session3);
  $special_req=format_textarea($special_req);
  my $conflicts_list = "";
  $conflicts_list .= "\n  First Priority: $conflict1" if my_defined($conflict1);
  $conflicts_list .= "\n  Second Priority: $conflict2" if my_defined($conflict2);
  $conflicts_list .= "\n  Third Priority: $conflict3" if my_defined($conflict3);
  $conflicts_list .= "\n  BOF or IRTF Session: $conflict_other" if my_defined($conflict_other);
  $num_session++ if ($length_session3);

  my $session_info_text = qq{
---------------------------------------------------------
Working Group Name: $wg_name
Area Name: $area_name
Session Requester: $requester_name

Number of Sessions: $num_session
Length of Session(s):  $length1
                       $length2
                       $length3
Number of Attendees: $number_attendee
Conflicts to Avoid:$conflicts_list

Special Requests:
  $special_req
---------------------------------------------------------
};

  return $session_info_text;
}

sub get_session_info {
  my $session_id=shift;
  my $from_approval=shift;
  $from_approval = 0 unless defined($from_approval);
  my $header=($from_approval)?"<font color=\"red\"><b>":"";
  my $extra1 = ($from_approval)?"<font color=\"red\"><b> &nbsp; &nbsp; ***Your approval is required for third session***</b></font>":"";
  my ($group_acronym_id,$irtf,$num_session,$length_session1,$length_session2,$length_session3,$number_attendee,$conflict1,$conflict2,$conflict3,$conflict_other,$special_req,$meeting_num) = db_select("select group_acronym_id,irtf,num_session,length_session1,length_session2,length_session3,number_attendee,conflict1,conflict2,conflict3,conflict_other,special_req,meeting_num from wg_meeting_sessions where session_id=$session_id");
  $special_req=format_textarea($special_req);
  $conflict_other=format_textarea($conflict_other);
  $num_session++ if $length_session3;
  my ($acronym,$name)=db_select("select acronym,name from acronym where acronym_id=$group_acronym_id");
  my ($area_name,$area_acronym) = db_select("select name,acronym from area_group a, acronym b where group_acronym_id=$group_acronym_id and area_acronym_id=acronym_id");
  if ($irtf) {
    ($acronym,$name) = db_select("select irtf_acronym,irtf_name from irtf where irtf_id=$group_acronym_id");
    $area_name="IRTF";
    $area_acronym="IRTF";
  }
  my $html_txt = qq{<h3>Requested Information</h3>
$table_header2
<Tr bgcolor="$color1"><td width="200">Working Group Name: </td><td>$name ($acronym)</td></tr>
<tr bgcolor="$color2"><td>Area Name: </td><td>$area_name ($area_acronym)</td></tr>
<Tr bgcolor="$color1"><td>Number of Sessions Requested: </td><td>$num_session $extra1</td></tr>
};
for (my $loop=1;$loop<=$num_session;$loop++) {
  my $length=eval("\$length_session$loop");
  my $hours = ($length<2)?"hour":"hours";
  $length="1.5" if ($length == 2);
  $length="2" if ($length == 3);
  $length="2.5" if ($length == 4);
  my $pre=($loop==3)?$header:"";
  $html_txt .= qq{
<tr bgcolor="$color2"><td>$pre Length of Session $loop: </td><td>$pre $length $hours</td></tr>
};
}
$html_txt .= qq{<tr bgcolor="$color1"><td>Number of Attendees: </td><td>$number_attendee</td></tr>
};
my $next_color=$color2;
if (my_defined($conflict1)) {
  my $conflict_specific = qq{<table border="0"><Tr><Td>First Priority:</td><td>$conflict1</td></tr>
};
  $conflict_specific .= "<tr><td>Second Priority:</td><td>$conflict2</td></tr>\n" if (my_defined($conflict2));
  $conflict_specific .= "<tr><td>Third Priority:</td><td>$conflict3</td></tr>\n" if (my_defined($conflict3));
  $conflict_specific .= "<tr><td>BOF or IRTF Sessions:</td><td>$conflict_other</td></tr>\n" if (my_defined($conflict_other));
  $conflict_specific .= "</table>\n";
  $html_txt .= qq{<tr bgcolor="$color2"><td>Conflicts to Avoid:</td>
<td>$conflict_specific</td></tr>
};
  $next_color=$color1;
}

  my $other_wg_list="";
  my @otherWGList=db_select_multiple("select group_acronym_id from session_conflicts where meeting_num=$meeting_num and conflict_gid=$group_acronym_id group by group_acronym_id");

  for my $array_ref (@otherWGList) {
    my ($group_acronym_id)=@$array_ref;
    my $name=db_select("select acronym from acronym where acronym_id=$group_acronym_id");
    $other_wg_list.="$name, ";
  }
  if (my_defined($other_wg_list)) {
    chop($other_wg_list);chop($other_wg_list);
    $html_txt .= qq{<Tr bgcolor="$next_color"><td valign="top" width="180">Other WGs that included $acronym in their conflict lists:</td><td>$other_wg_list</td></tr>
};
    $next_color=$color2;
  }

$html_txt .= qq{
<Tr bgcolor="$next_color"><td valign="top">Special Requests:</td><td>$special_req</td></tr>} if my_defined($special_req);
$html_txt .= qq{
</table>
};
  return $html_txt;
}

sub get_hour_val {
  my $hour_id=shift;
  my $ret_val = db_select("select hour_desc from meeting_hours where hour_id=$hour_id");
  $ret_val = "" unless $ret_val;
  return $ret_val;
}

sub add_session_activity {
  my $group_acronym_id=shift;
  my $activity_text=shift;
  my $meeting_num=shift;
  my $loginid=shift;
  $activity_text = db_quote($activity_text);
  db_update("insert into session_request_activities (group_acronym_id,meeting_num,activity,act_date,act_time,act_by) values ($group_acronym_id,$meeting_num,$activity_text,current_date,current_time,$loginid)");
  return 1;
}

sub add_wg_proceedings_activity {
  my $group_acronym_id=shift;
  my $activity_text=shift;
  my $meeting_num=shift;
  my $loginid=shift;
  $activity_text = db_quote($activity_text);
  db_update("insert into wg_proceedings_activities (group_acronym_id,meeting_num,activity,act_date,act_time,act_by) values ($group_acronym_id,$meeting_num,$activity_text,current_date,current_time,$loginid)");
  return 1;
}



sub get_name_from {
  my $from_id = shift;
  my $name_from = db_select("select body_name from from_bodies where from_id=$from_id");
  return $name_from if ($name_from ne "0");
  my $is_area = db_select("select count(*) from areas where area_acronym_id=$from_id");
  $name_from = uc(db_select("select acronym from acronym where acronym_id=$from_id"));
  $name_from = ($is_area)?"IETF $name_from AREA":"IETF $name_from WG";
  return $name_from;
}

sub get_offset_date {
  my $from_date=shift;
  my $plus_minus=shift;
  my $offset=shift;
  my $date_unit=shift;
  return "Unknown" unless my_defined($date_unit);
  return "Unknown" unless ($date_unit =~ /day|month|year/);
  if ($plus_minus eq "+") {
    return db_select("select date_add('$from_date', interval $offset $date_unit)");
  } elsif ($plus_minus eq "-") {
    return db_select("select date_sub('$from_date', interval $offset $date_unit)");
  } else {
    return "Unknown";
  }
  return "Unknown";
}

sub get_day_name {
  my $target_date=shift;
  return db_select("select dayname('$target_date')");
}


sub get_replaced_by_info {
  my $status_value=shift;
  my $dTag=shift;
  my $tracker_type=shift;
  my $is_result_list=shift or 0;
  return "" unless $dTag;
  return "" unless my_defined($dTag);
  my $pre_fix = ($is_result_list)?"<br> &nbsp; &nbsp;&nbsp; ":"<br>";
  if ($status_value eq "Replaced") {
     my $replaced_by_id = db_select("select replaced_by from internet_drafts where id_document_tag=$dTag");
     my $replaced_by_filename = db_select("select filename from internet_drafts where id_document_tag=$replaced_by_id");
     my $in_tracker = db_select("select count(id_document_tag) from id_internal where id_document_tag=$replaced_by_id and rfc_flag=0");
     my $cgi_name = ($tracker_type eq "iesg")?"idtracker.cgi":"pidtracker.cgi";
     if ($is_result_list and $tracker_type eq "iesg") {
         $cgi_name .= "?command=search_list&search_job_owner=0&search_group_acronym=&search_status_id=&search_cur_state=&sub_state_id=6&search_filename=$replaced_by_filename&search_rfcnumber=&search_area_acronym=&note=&search_button=SEARCH";
         $status_value = "${pre_fix}Replaced by <a href=\"$cgi_name\">$replaced_by_filename</a>";
     } elsif ($in_tracker) {
       if ($is_result_list) {
         $cgi_name .= "?command=search_list&search_job_owner=0&search_group_acronym=&search_status_id=&search_cur_state=&sub_state_id=6&search_filename=$replaced_by_filename&search_rfcnumber=&search_area_acronym=&note=&search_button=SEARCH";  
       } else {
         $cgi_name .= "?command=view_id&dTag=$replaced_by_id&rfc_flag=0";
       }
       $status_value = "${pre_fix}Replaced by <a href=\"$cgi_name\">$replaced_by_filename</a>";
     } else {
       $status_value = "${pre_fix}Replaced by $replaced_by_filename";
     }
     return $status_value;
  }
  return "";
}

sub get_replaces_info {
  my $dTag=shift;
  my $tracker_type=shift;
  my $is_result_list=shift or 0;
  return "" unless $dTag;
  return "" unless my_defined($dTag);
  my $pre_fix = ($is_result_list)?"<br> &nbsp; &nbsp;&nbsp; ":"<br>";
  my @List = db_select_multiple("select id_document_tag,filename from internet_drafts where replaced_by=$dTag");
  if ($#List > -1) {
    my $ret_val = "${pre_fix}Replaces ";
    for my $array_ref (@List) {
      my ($replaced_id,$replaced_filename) = @$array_ref;
      my $in_tracker = db_select("select count(id_document_tag) from id_internal where id_document_tag=$replaced_id and rfc_flag=0");
      my $cgi_name = ($tracker_type eq "iesg")?"idtracker.cgi":"pidtracker.cgi";
      if ($is_result_list and $tracker_type eq "iesg") {
          $cgi_name .= "?command=search_list&search_job_owner=0&search_group_acronym=&search_status_id=5&search_cur_state=&sub_state_id=6&search_filename=$replaced_filename&search_rfcnumber=&search_area_acronym=&note=&search_button=SEARCH";
          $ret_val .= "<a href=\"$cgi_name\">$replaced_filename</a>,";
      } elsif ($in_tracker) {
        if ($is_result_list) {
          $cgi_name .= "?command=search_list&search_job_owner=0&search_group_acronym=&search_status_id=5&search_cur_state=&sub_state_id=6&search_filename=$replaced_filename&search_rfcnumber=&search_area_acronym=&note=&search_button=SEARCH";
        } else {
          $cgi_name .= "?command=view_id&dTag=$replaced_id&rfc_flag=0";
        }
        $ret_val .= "<a href=\"$cgi_name\">$replaced_filename</a>,";
      } else {
        $ret_val .= "$replaced_filename,";
      }
    }
    chop($ret_val);
    return $ret_val;
  }
  return "";
}

sub decrease_revision {
  my $revision = shift;
  if ($revision > 0) {
    $revision--;
    $revision = "0$revision" if ($revision < 10);
  }
  return $revision;
}

sub get_ballot_list_text {
  my $agenda_item_id=shift;
  my $ballot_id = shift;
  my $agenda_cat_id=shift;
  my $hd_space = shift;
  my $item_num = shift;
  my $total_num = shift;
  my $ret_val = "";
  my $count_txt = (defined($item_num))?"-$item_num of $total_num":"";
  my @List = db_select_multiple("select id_document_tag, rfc_flag from id_internal where ballot_id=$ballot_id order by primary_flag");
  for $array_ref (@List) {
    my ($id_document_tag,$rfc_flag) = @$array_ref;
    my ($id_name,$id_title,$id_status) = db_select("select filename,id_document_name,status_value from internet_drafts a,id_intended_status b where id_document_tag=$id_document_tag and a.intended_status_id=b.intended_status_id");
    $id_name = "rfc$id_document_tag" if ($rfc_flag);
    $ret_val .= qq{$hd_space $id_name $count_txt
$id_title ($id_status)
};
  }
  return $ret_val;

}
sub get_ballot_list {
  my $agenda_item_id=shift;
  my $ballot_id = shift;
  my $agenda_cat_id=shift;
  my $hd_space = shift;
  my $telechat_date = shift;
  my $command_name=shift;
  my $ret_val = "";
  my @List = db_select_multiple("select id_document_tag, rfc_flag from id_internal where ballot_id=$ballot_id order by primary_flag");
  for $array_ref (@List) {
    my ($id_document_tag,$rfc_flag) = @$array_ref;
    my $id_name = db_select("select filename from internet_drafts where id_document_tag=$id_document_tag");
    $id_name = "rfc$id_document_tag" if ($rfc_flag);
    if (length($id_name) > $MAX_LENGTH) {
      $id_name = substr($id_name,0,$MAX_LENGTH);
      $id_name .= "...";
    }
    $ret_val .= qq{$gap $hd_space <a href="$program_name?command=$command_name&agenda_item_id=$agenda_item_id&telechat_date=$telechat_date">$id_name</a><br>
};
  }
  return $ret_val;
}
                                                                                         


###########################################################
#  
# Function is_unique_comment
# Parameters:
#   $log_text - text of comment to be tested
#   $document_id - Document Id of current draft
# return: 1 if unique comment
#         0 if duplicate comment exists
#  
###########################################################
sub is_unique_comment { 
   my ($log_txt,$document_id,$is_ballot) = @_;
   return 1;  #Disable this function since the algorithm is not proper to use
   return 1 unless (my_defined($log_txt));
   $log_txt = db_quote($log_txt); 
   my $additional_where = "";
   if (defined($is_ballot) and $is_ballot == 1) {
    $additional_where = " and ballot=1";
   }
   my $sqlStr = "select count(*) from document_comments where created_by = $loginid AND comment_text = $log_txt AND document_id = $document_id $additional_where";
   my $count = db_select($sqlStr);
   return 0 if ($count > 0); #There is same comment already existed
   return 1;
}


########################################################
#
# Function get_area_optio_str
# Parameters:
# result: HTML text to display the options of "Area" field
#
########################################################
sub get_area_option_str {
   my $select_id = shift;
   my $with_old_ad=shift;
   $select_id = 0 unless my_defined($select_id);
   $with_old_ad=0 unless defined($with_old_ad);
   my $area_option_str = "";
   my $status_option = ($with_old_ad)?"< 3":" = 1";
   @list = db_select_multiple("select a.area_acronym_id,b.acronym from areas a,acronym b where a.area_acronym_id = b.acronym_id AND a.status_id $status_option");
   for $array_ref (@list) {
      my $selected = "";
      my ($aid,$aval) = @$array_ref;
          $selected = "selected" if ($aid == $select_id);
      $aval = rm_tr($aval);
      $area_option_str .= qq {<option value="$aid" $selected>$aval</option>
      };
   }
   return $area_option_str;
}

sub get_sub_state {
  my $id = shift;
  return rm_tr(db_select("select sub_state_val from sub_state where sub_state_id = $id"));
}

sub get_sub_state_select {
  my $default_id = shift;
  my $default_str = "None";
  my $html = qq {<select name="sub_state_id">
};
  if ($default_id == -1) {
    $html .= qq{ <option value="-1">--Select Sub State</option>
};
  }
  if ($default_id == -2) {
    $html .= qq{ <option value="0">--Select Sub State</option>
};        
  }       

  $html .= qq{
  <option value=0>$default_str</option>
};
  my @List = rm_tr(db_select_multiple("select sub_state_id,sub_state_val from sub_state order by 1"));
  for $array_ref (@List) {
    my ($id,$val) = @$array_ref;
    my $selected = "";
    $selected = "selected" if ($id == $default_id);
    $html .= "  <option value=$id $selected>$val</option>\n";
  }
  if ($default_id > -1) {
    my $max_id = db_select("select max(sub_state_id) from sub_state");
    $max_id++;
    my $selected = "";
    $selected = "selected" if ($max_id == $default_id);
    $html .= "<option value=$max_id $selected>--All Substates</option>\n";
  }
  $html .= "</select>\n";
  return $html;
}

sub email_to_AD {
   my ($filename,$id_status_log,$log_txt,$ad_id,$url,$test_mode,$devel_mode,$loginid) = @_;
   my $other_name = ($loginid)?get_mark_by($loginid):"system";
   my $sqlStr = qq{
   select email_address from email_addresses e,iesg_login i
   where i.id = $ad_id
   AND i.person_or_org_tag = e.person_or_org_tag
   AND e.email_priority = 1
   };
   my $email_address = rm_tr(db_select($sqlStr));
   $id_status_log = unformat_textarea($id_status_log) if (my_defined($id_status_log));
   $log_txt = unformat_textarea($log_txt) if (my_defined($log_txt));
   if ($id_status_log =~ /A new comment added/) {
     my @temp=split '\&',$url;
     my $dTag=$temp[1];
     $dTag =~ s/dTag=//g;
     my $id=db_select("select max(id) from document_comments where document_id=$dTag");
     $id_status_log .= "\n\n";
     $id_status_log .= db_select("select comment_text from document_comments where id=$id");
   }
     open MAIL, "| /usr/lib/sendmail -t" or return 0;
   print MAIL <<END_OF_MESSAGE;
To: $email_address
From: "DraftTracker Mail System" <iesg-secretary\@ietf.org>
Subject: $filename updated by $other_name
$X_MAIL_HEADER

Please DO NOT reply on this email.
$TEST_MESSAGE

I-D: $filename
ID Tracker URL: $url
$id_status_log
$log_txt
END_OF_MESSAGE

   close MAIL or return 0;
   mail_log($program_name,"$filename updated by $other_name",$email_address,$user_name);
   return 1;
                                                                                                                                                                                   
}

sub update_state {
  my $ballot_id=shift;
  my $new_state=shift;
  my $new_sub_state_id=shift;
  my $test_mode = shift;
  my $devel_mode = shift;
  my $loginid = shift;
  my ($dTag,$rfc_flag) = db_select("select id_document_tag,rfc_flag from id_internal where ballot_id=$ballot_id and primary_flag=1");
  my ($old_state,$old_sub_state_id) = db_select("select cur_state,cur_sub_state_id from id_internal where ballot_id = $ballot_id and primary_flag=1");
  return 0 if ($new_state == $old_state and $new_sub_state_id == $old_sub_state_id);
  my $sqlStr = qq{update id_internal
set cur_state = $new_state, cur_sub_state_id=$new_sub_state_id,
prev_state = $old_state,prev_sub_state_id = $old_sub_state_id,
event_date=CURRENT_DATE
where ballot_id = $ballot_id
};
  return 0 unless (db_update($sqlStr));
  my $old_state_name = rm_tr(db_select("select document_state_val from ref_doc_states_new where document_state_id = $old_state"));
  my $new_state_name = rm_tr(db_select("select document_state_val from ref_doc_states_new where document_state_id = $new_state"));
  my $old_sub_state_name = "";
  my $new_sub_state_name = "";
  $old_sub_state_name = "::" . rm_tr(db_select("select sub_state_val from sub_state where sub_state_id = $old_sub_state_id"))  if ($old_sub_state_id > 0);
  $new_sub_state_name = "::" . rm_tr(db_select("select sub_state_val from sub_state where sub_state_id = $new_sub_state_id"))  if ($new_sub_state_id > 0);
  my $ad_name = ($loginid>0)?get_mark_by($loginid, 1):"system";
  my $return_txt = "State Changes to <b>${new_state_name}${new_sub_state_name}</b> from <b>${old_state_name}${old_sub_state_name}</b> by <b>$ad_name</b>";
  my $comment_text = db_quote($return_txt);
  my @List = db_select_multiple("select a.id_document_tag, b.revision,status_id,expired_tombstone from id_internal a, internet_drafts b where a.ballot_id = $ballot_id and a.id_document_tag = b.id_document_tag");
  for $array_ref (@List) {
    my ($document_id,$version,$status_id,$expired_tombstone) = @$array_ref;
    $version=decrease_revision($version) if ($status_id > 1 and $expired_tombstone==0);
    $version = db_quote($version);
    update_comment_log($document_id,$version,$loginid,$new_state,$old_state,"",$comment_text);
  }
  notify_state_update($ballot_id,$comment_text,$test_mode,$devel_mode,"https://datatracker.ietf.org/public/pidtracker.cgi?command=view_id&dTag=$dTag&rfc_flag=$rfc_flag");
  return $return_txt;
}

sub notify_state_update {
  my $ballot_id = shift;
  my $comment_text = shift;
  my $test_mode = shift;
  my $devel_mode = shift;
  my $url = shift;
  $comment_text =~ s/<b>//g;
  $comment_text =~ s/<\/b>//g;
  my @List = db_select_multiple("select rfc_flag,a.id_document_tag,a.state_change_notice_to, b.filename from id_internal a, internet_drafts b where a.id_document_tag = b.id_document_tag and a.ballot_id = $ballot_id");
  for $array_ref (@List) {
    my ($rfc_flag,$id_document_tag,$state_change_notice_to,$filename) = @$array_ref;
    $filename = "RFC $id_document_tag" if ($rfc_flag);
    $state_change_notice_to =~ s/;/,/g;
    my $mail_body = qq{From: The IESG <iesg-secretary\@ietf.org>
To: $state_change_notice_to
Subject: ID Tracker State Update Notice: $filename
Reply-To: ietf-secretariat-reply\@ietf.org

$comment_text
ID Tracker URL: $url
};
    if (my_defined($state_change_notice_to)) {
        open MAIL, "| /usr/lib/sendmail -t" or return 0;
      print MAIL <<END_OF_MESSAGE;
$mail_body
END_OF_MESSAGE
      close MAIL;
    }
  }
}



###################################
# Function: generate_error_log
# Parameters: 
#    $error_msg - Error message 
# return: none
#    This function appends error message to $LOG_PATH/process.log,
#    then terminate the program returning some value to sendmail
#    program so a sender can receive some sort of error message.
###################################
sub generate_error_log {
   my $error_msg = shift;
   open ERROR_LOG,">>$LOG_PATH/id_tracker_error.log" or return;
   print ERROR_LOG "$error_msg\n";
   close ERROR_LOG;
   return;
}



################################################################
#
# Function : get_option_str
# Parameters:
#   $table_name : Table where the data pulled from
#   $selected_id : currently selected record id
# return : HTML text of options of SELECT tag
#
################################################################
sub get_option_str {
   my $table_name = shift;
   my $selected_id = shift;
   $selected_id = 0 unless my_defined($selected_id);
   $option_str = "";
   $sqlStr = qq{
   select * from $table_name order by 1
   };
   my @list = db_select_multiple($sqlStr);
   for $array_ref (@list) {
     my ($id,$val) = @$array_ref;
      if (defined($selected_id) and $selected_id == $id) {
         $selected = "selected";
      } else {
         $selected = "";
      }
      $option_str .= qq{
      <option value="$id" $selected>$val</option>
      };
   }
   return $option_str;
}


#############################################################
#
# Function : update_commment_log
# Parameters:
#   $document_id - id of current draft that this comment is belong to
#   $version - version of current docuement
#   $mark_by - Marked by
#   $cur_state - Current state of draft
#   $prev_state - Previous state of draft
#   $comment - Text of comment
#   $log_txt - Text of comment that indicates the state changes
#   $public_flag - Indicate that the current comment is private or public
# return : 0 if updating database failed
#          1 if successful 
#
#############################################################
sub update_comment_log {
   my ($document_id,$version,$mark_by,$cur_state,$prev_state,$comment,$log_txt,$public_flag,$id_status_log) = @_;
   my $rfc_flag = db_select("select rfc_flag from id_internal where id_document_tag = $document_id");
   my ($revision,$expired_tombstone,$status_id) = db_select("select revision,expired_tombstone,status_id from internet_drafts where id_document_tag=$document_id");
   $version=$revision;
   $version=decrease_revision($revision) if ($status_id > 1 and $expired_tombstone==0);
   $version = "RFC" if ($rfc_flag);
   $version=db_quote($version);
   ##################### Add log to indicate state changed ######################
   my $cur_time = db_quote(get_current_time());
   $public_flag=1 unless my_defined($public_flag);
   $public_flag=1 if ($public_flag eq "on");
   if (my_defined($log_txt) and is_unique_comment($log_txt,$document_id)) {

  # if (my_defined($log_txt)) {
      $sqlStr = qq{
       insert into document_comments
      (document_id,public_flag,comment_date,comment_time,version,comment_text,created_by,result_state,origin_state,rfc_flag)
           values
           ($document_id,$public_flag,CURRENT_DATE,$cur_time,$version,$log_txt,$mark_by,$cur_state,$prev_state,$rfc_flag)
        };
        #return $sqlStr;
        return 0 unless (db_update($sqlStr));
   }
   ##################### Add log to indicate Intended_status changed ######################
   if (my_defined($id_status_log)) {
      $id_status_log = format_textarea($id_status_log);
      $sqlStr = qq {
       insert into document_comments
      (document_id,public_flag,comment_date,comment_time,version,comment_text,created_by,result_state,origin_state,rfc_flag)
           values
           ($document_id,1,CURRENT_DATE,$cur_time,$version,$id_status_log,$mark_by,$cur_state,$prev_state,$rfc_flag)
        };
        #return $sqlStr;
        return 0 unless (db_update($sqlStr));
   }
   #################### Add Comment if any #############################
   if (my_defined($comment)) {
     $comment = db_quote($comment);
          #return $comment;
          unless (is_unique_comment($comment,$document_id)) {
             return 0;
          }
          if ($public_flag eq "on" or $public_flag==1) {
             $public_flag_val = 1;
          } else {
             $public_flag_val = 0;
          }
      $sqlStr = qq{
          insert into document_comments
          (document_id,public_flag,comment_date,comment_time,version,comment_text,created_by,result_state,origin_state,rfc_flag)
          values
          ($document_id,$public_flag_val,CURRENT_DATE,$cur_time,$version,$comment,$mark_by,$cur_state,$cur_state,$rfc_flag)
          };
          #return $sqlStr;

      return 0 unless (db_update($sqlStr));
   }
   return 1;
}


#######################################################
#
#   Function : get_ad_option_str
#   Parameters:
#      $id - record id
#   return : HTML text to display options of Area Directors
#
#######################################################
sub get_ad_option_str {
   my $id = shift;
   my $only_active=shift;
   my $ad_option_str = "";
   my $user_level_list = (defined($only_active))?"1":"1,2";
   my $separated=0;
   $sqlStr = qq{
select id, first_name,last_name,user_level from iesg_login where user_level in ($user_level_list) order by user_level,last_name
};
   my @list = db_select_multiple($sqlStr);
   for $array_ref (@list) {
     my ($pID,$first_name,$last_name,$user_level) = rm_tr(@$array_ref);
     if ($separated==0 and $user_level != 1) {
       $ad_option_str .= qq{<option value="-99">------------------</option>
};
       $separated=1;
     }
         my $selected = "";
         if (defined($id)) {
            if ($pID == $id) {
               $selected = "selected";
        }
         }
     $ad_option_str .= qq{
      <option value="$pID" $selected>$last_name, $first_name</option>
     };
   }
   return $ad_option_str;
}


sub get_telechat_date_list {
  my ($date1,$date2,$date3,$date4) = db_select("select date1,date2,date3,date4 from telechat_dates");
  return qq{
<option value="$date1">$date1</option>
<option value="$date2">$date2</option>
<option value="$date3">$date3</option>
<option value="$date4">$date4</option>
};
}
                                                                                           

sub get_iesg_select_list {
  my $selected_id=shift;
  my $extra_where=shift;
  my $table_name = "iesg_login";
  my $id="id";
  my $value1="first_name";
  my $value2="last_name";
  my $sort_by = "last_name";
  my $where_clause = "where user_level=1";
  $where_clause .= " $extra_where " if (my_defined($extra_where));
  return get_select_list($table_name,$id,$value1,$value2,$sort_by,$where_clause,$selected_id);
}

sub get_state_list {
  my $selected_id=shift;
  my $table_name = "ref_doc_states_new";
  my $id="document_state_id";
  my $value1="document_state_val";
  my $value2="";
  my $sort_by = "document_state_id";
  my $where_clause = "where 1=1";
  return get_select_list($table_name,$id,$value1,$value2,$sort_by,$where_clause,$selected_id);
}

sub get_select_list {
  my $table_name=shift;
  my $id=shift;
  my $value1=shift;
  my $value2=shift;
  my $sort_by=shift;
  my $where_clause = shift;
  my $selected_id = shift;
  $value1 .= ", $value2" if (my_defined($value2));
  my $ret_val = "";
  my $sqlStr = "Select $id, $value1 from $table_name ";
  $sqlStr .= "$where_clause " if (my_defined($where_clause)); 
  $sqlStr .= "order by $sort_by" if (my_defined($sort_by)); 
  my @List = db_select_multiple($sqlStr);
  for $array_ref (@List) {
    my ($id,$value1,$value2) = @$array_ref;
    my $selected = ($selected_id == $id)?"selected":"";
    $ret_val .= "<option value=\"$id\" $selected>$value1 $value2</option>\n";
  }
  return $ret_val;
}

sub add_document_comment {
  my ($loginid,$tag,$comment_text,$is_ballot_id) = @_;
  my $mark_by;
  if ($loginid == 999) {
    $mark_by = "IESG Secretary";
  } elsif ($loginid == 0) {
    $mark_by = "system";
  } else {
    $mark_by = get_mark_by($loginid,1);
  }
  my $rfc_flag = db_select("select rfc_flag from id_internal where id_document_tag=$tag");
  $comment_text .= " by $mark_by" unless ($comment_text =~ /Earlier history/);
  $comment_text = db_quote($comment_text);
  if ($is_ballot_id) {
    my @List = db_select_multiple("select id_document_tag,rfc_flag from id_internal where ballot_id = $tag");
    for $array_ref (@List) {
      my ($id_document_tag,$rfc_flag) = @$array_ref;
      my $version = "RFC";
      unless ($rfc_flag) {
        $version = db_select("select revision from internet_drafts where id_document_tag=$id_document_tag");
        my ($status_id,$expired_tombstone) = db_select("select status_id,expired_tombstone from internet_drafts where id_document_tag=$id_document_tag");
        $version=decrease_revision($version) if ($status_id > 1 and $expired_tombstone==0);
      }
      $version = db_quote($version);
      my $sqlStr = "insert into document_comments (document_id,public_flag,comment_date,comment_time,version,comment_text,created_by) values ($id_document_tag,1,current_date,current_time,$version,$comment_text,$loginid)";
      db_update($sqlStr);
    }
  } else {
    my ($status_id,$expired_tombstone,$version) = db_select("select status_id,expired_tombstone,revision from internet_drafts where id_document_tag=$tag");
    $version=decrease_revision($version) if ($status_id > 1 and $expired_tombstone==0);
    $version = "RFC $tag" if ($rfc_flag);
    $version=db_quote($version);
    my $sqlStr = qq{insert into document_comments (document_id,public_flag,comment_date,comment_time,version,comment_text,created_by) values ($tag,1,current_date,current_time,$version,$comment_text,$loginid)};
    db_update($sqlStr);
  }
}


############################################################
#
# Function : get_mark_by
# Parameters:
#   $loginid - login id of current user
# return : string of first name and last name pulled from iesg_login table
#
############################################################
sub get_mark_by {
   my $id = shift;
   my $reverse = shift;
   my ($fName,$lName) = rm_tr(db_select("select first_name,last_name from iesg_login where id = $id"));
   my $new_mark_by = "$fName $lName";
   $new_mark_by = "$fName $lName" if ($reverse);
   return $new_mark_by;
                                                                                            
}


sub get_name {
   my $person_or_org_tag = shift;
   my $reverse = shift;
   my ($firstname,$lastname) = rm_tr(db_select("select first_name,last_name from person_or_org_info where person_or_org_tag = $person_or_org_tag"));
   return "$lastname, $firstname" if ($reverse);
   return "$firstname $lastname";
}

sub get_email {
   my $person_or_org_tag = shift;
   my $email_priority=shift;
   $email_priority = 1 unless defined($email_priority);
   $email_priority = 1 unless ($email_priority);
   my $ret_val = rm_tr(db_select("select email_address from email_addresses where person_or_org_tag = $person_or_org_tag and email_priority=$email_priority"));

   return $ret_val;
}

sub get_company {
  my $person_or_org_tag=shift;
  my $ret_val = db_select("select affiliated_company from postal_addresses where person_or_org_tag=$person_or_org_tag and address_priority=1");
  return $ret_val;
}

sub get_intended_status_value {
  my $id = shift;
  my $draft_type = shift;
  my $table_name = "id_intended_status";
  $table_name = "rfc_intend_status" if ($draft_type eq "RFC");
  my $ret_val = rm_tr(db_select("select status_value from $table_name where intended_status_id = $id"));
  return $ret_val;
}

sub get_filename_set {
   my $ballot_id = shift;
   my $type = shift;
   my $new_line = "\n";
   $new_line = "<br>\n" if ($type == 1 or $type==4 or $type==5 or $type==6);
   $new_line = ", " if ($type == 2 or $type == 3);
   my $filename_set = "";
   my @List_file = db_select_multiple("select filename,rfc_flag,b.id_document_tag,revision, status_value from internet_drafts a, id_internal b, id_intended_status c where b.ballot_id = $ballot_id and b.id_document_tag=a.id_document_tag and a.intended_status_id = c.intended_status_id");
   for $array_ref (@List_file) {
     my ($filename,$rfc_flag,$tag,$revision,$status_value) = @$array_ref;
     my $filename2 = "";
     if ($rfc_flag) {
       if ($type == 5) {
         $filename2 = "RFC $tag";
       } else {
         $filename_set .= "RFC $tag";
       }
       $status_value = db_select("select status_value from rfcs a, rfc_intend_status b where a.rfc_number=$tag and a.intended_status_id=b.intended_status_id");
     } else {
       if ($type == 5) {
         $filename2 = "$filename-$revision.txt";
       } else {
         $filename_set .= "$filename-$revision.txt";
       }
     }
     if ($type == 3 or $type==4) {
       $status_value = full_status_value($status_value);
       $status_value =~ s/a //;
       $status_value =~ s/an //;
       $filename_set .= " to $status_value";
     }
     if ($type == 5) {
         $status_value = full_status_value($status_value);
         $status_value =~ s/a //;
         $status_value =~ s/an //;
         $filename2 .= " ($status_value)";
         $filename2 = qq{<a href="https://datatracker.ietf.org/cgi-bin/idtracker.cgi?loginid=$loginid&command=view_id&dTag=$tag&rfc_flag=$rfc_flag&ballot_id=$ballot_id">$filename2</a>
};
         $filename_set .= $filename2;
     }

     $filename_set .= $new_line;
   }
   if ($type == 2 or $type == 3) {
     chop($filename_set);
     chop($filename_set);
   }
   if ($type == 6) {
     my $name_ref=db_select("select filename from internet_drafts a, id_internal b where ballot_id=$ballot_id and primary_flag=1 and a.id_document_tag = b.id_document_tag");
     $filename_set = "<a href=\"#$name_ref\">$filename_set";
   }
   return $filename_set;
}

