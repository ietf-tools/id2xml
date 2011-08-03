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

$meeting_num = $q->param("meeting_num");  #Receive Meeting Number as CGI parameter
my $meeting_exist = db_select($dbh,"select count(session_id) from wg_meeting_sessions where meeting_num=$meeting_num and meeting_num > 64");
error($q,"No agenda found for IETF Meeting $meeting_num.<br>") unless $meeting_exist;
$table_id=db_select($dbh,"select hit_count from meeting_agenda_count");
$table_id++;
db_update($dbh,"update meeting_agenda_count set hit_count=$table_id");
my $create_temp_table = qq{create table temp_agenda$table_id (
id int(4) primary key auto_increment,
time_desc varchar(50),
session_name varchar(255),
room_name varchar(255),
area varchar(5),
group_acronym_id int(8),
group_acronym varchar(20),
group_name varchar(255),
special_agenda_note varchar(255)
)
};
db_update($dbh,$create_temp_table);
($start_date,$end_date) = db_select($dbh,"select start_date,end_date from meetings where meeting_num=$meeting_num");
my $month_name_s=db_select($dbh,"select monthname('$start_date')");
my $month_name_e=db_select($dbh,"select monthname('$end_date')");
my $day_s = db_select($dbh,"select dayofmonth('$start_date')");
my $day_e = db_select($dbh,"select dayofmonth('$end_date')");
my $meeting_num_verbal = get_verbal_number($meeting_num,1);
my $meeting_year=db_select($dbh,"select year('$start_date')");
my $period = "$month_name_s $day_s - $month_name_e $day_e";
if ($month_name_s eq  $month_name_e) {
  $period = "$month_name_s $day_s-$day_e";
}
$dir_name=db_select($dbh,"select dir_name from proceedings where meeting_num=$meeting_num");
$program_title="Agenda of the $meeting_num_verbal IETF";
$current_date = get_current_date();
$current_time = get_current_time();
$html_top=qq{
<center>
<B><font size=+1>Agenda of the $meeting_num_verbal IETF Meeting</font><br>$period, $meeting_year</b><br>
</center>
(<a href="agenda.txt">Text Format of the Agenda</a>)<br>
<p>

*** Click on an acronym of the group to get a charter page ***<br>
*** Click on a name of the group to get a meeting agenda ***</p>
};
$html_bottom = qq{<hr>
<center><b>AREA DIRECTORS</b></center><br>
<table border="0" width="800">
};
my @List_area=db_select_multiple($dbh,"select area_acronym_id, name, acronym from areas a, acronym b where status_id=1 and area_acronym_id=acronym_id order by acronym");
for my $array_ref (@List_area) {
  my ($area_acronym_id,$name,$acronym) =@$array_ref;
  $acronym=uc($acronym);
  my $ads="";
  my @List_ad=db_select_multiple($dbh,"select first_name,last_name,affiliated_company from area_directors a, person_or_org_info b, postal_addresses c where area_acronym_id=$area_acronym_id and a.person_or_org_tag=b.person_or_org_tag and a.person_or_org_tag=c.person_or_org_tag and address_priority=1");
  for my $array_ref2 (@List_ad) {
    my ($first_name,$last_name,$company) = @$array_ref2;
    $ads .= " $first_name $last_name/$company &";
  }
  chop($ads);
  $html_bottom .= "<tr valign=\"top\"><td width=\"65\">$acronym</td><td width=\"140\">$name</td><td>$ads</td></tr>\n";
}
$html_bottom.="</table>\n";
@days=('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday');
$html_body = "";
my $cbreak_time=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=2");
my $break_time=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=3");
my ($reg_area_name,$break_area_name) = db_select($dbh,"select reg_area_name,break_area_name from meeting_venues where meeting_num=$meeting_num");
for (my $day_id=0;$day_id<6;$day_id++) {
  my $day=uc($days[$day_id]);
  my $date=db_select($dbh,"select date_add('$start_date',interval $day_id day)");
  my $format_date=format_date($date);
  $html_body .= "<b>$day, $format_date</b>\n";
  my $reg_time=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and day_id=$day_id and non_session_ref_id=1");
  db_update($dbh,"delete from temp_agenda$table_id");
  my @List_session1=db_select_multiple($dbh,"select irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_num and sched_time_id1=time_id and day_id=$day_id and a.sched_room_id1=room_id");
  my @List_session2=db_select_multiple($dbh,"select irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_num and sched_time_id2=time_id and day_id=$day_id and a.sched_room_id2=room_id");
  my @List_session3=db_select_multiple($dbh,"select irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_num and sched_time_id3=time_id and day_id=$day_id and a.sched_room_id3=room_id");
  my @List_session4=db_select_multiple($dbh,"select irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_num and combined_time_id1=time_id and day_id=$day_id and a.combined_room_id1=room_id");
  my @List_session5=db_select_multiple($dbh,"select irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_num and combined_time_id2=time_id and day_id=$day_id and a.combined_room_id2=room_id");
  push @List_session1, @List_session2;
  push @List_session1, @List_session3;
  push @List_session1, @List_session4;
  push @List_session1, @List_session5;
  for my $array_ref2 (@List_session1) {
    my ($irtf,$session_name_id,$time_desc,$group_acronym_id,$room_name,$special_agenda_note) = @$array_ref2;
    my ($group_acronym,$group_name) = db_select($dbh,"select acronym,name from acronym where acronym_id=$group_acronym_id");
    my $area_name=db_select($dbh,"select acronym from acronym a, area_group b where area_acronym_id=acronym_id and group_acronym_id=$group_acronym_id");
    if ($irtf) {
      $area_name="IRTF";
      ($group_acronym,$group_name) = db_select($dbh,"select irtf_acronym,irtf_name from irtf where irtf_id=$group_acronym_id")
    } else {
      $irtf=0;
    }
    $area_name=uc($area_name);
    my $session_name=db_select($dbh,"select session_name from session_names where session_name_id=$session_name_id");
    db_update($dbh,"insert into temp_agenda$table_id (time_desc,session_name,area,group_acronym_id,group_acronym,group_name,special_agenda_note,room_name) values ('$time_desc','$session_name','$area_name',$group_acronym_id,'$group_acronym','$group_name','$special_agenda_note','$room_name')");
  }
  unless ($day_id) { ##Sunday Session ##
    $html_body .= "<br>$reg_time IETF Registration - $reg_area_name<br>\n";
    my @List_sessions = db_select_multiple($dbh,"select time_desc,group_name,room_name,special_agenda_note from temp_agenda$table_id order by time_desc");
    for my $array_ref2 (@List_sessions) {
      my ($time_desc,$group_name,$room_name,$special_agenda_note) = @$array_ref2;
      my $name=db_select($dbh,"select name from acronym where acronym_id=$group_acronym_id");
      $html_body .= "$time_desc  $group_name - $room_name";
      $html_body .= " - <b>$special_agenda_note</b>" if my_defined($special_agenda_note);
      $html_body .= " <br>\n";
    }
  } else { 
    my $arbreak_time1=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=4 and day_id=$day_id");
    my $arbreak_time2=db_select($dbh,"select time_desc from non_session where meeting_num=$meeting_num and non_session_ref_id=5 and day_id=$day_id");
    $html_body .= "<br>$reg_time IETF Registration - $reg_area_name\n" if my_defined($reg_time);
    $html_body .= "<br>\n$cbreak_time Continental Breakfast - $break_area_name<br>\n";
    my @List_sessions=db_select_multiple($dbh,"select time_desc,group_acronym_id,session_name, room_name,special_agenda_note,area,group_name,group_acronym from temp_agenda$table_id order by time_desc, area, group_name");
    my $prev_session_name="";
    for my $array_ref2 (@List_sessions) {
      my ($time_desc,$group_acronym_id,$session_name,$room_name,$special_agenda_note,$area,$group_name,$group_acronym) = @$array_ref2;
      my $group_type_id=db_select($dbh,"select group_type_id from groups_ietf where group_acronym_id=$group_acronym_id");
      $group_name .= " BOF" if ($group_type_id==3);
      $group_name .= " WG" if ($group_type_id==1);
      my $irtf=($group_acronym_id >0 and $group_acronym_id < 30)?1:0;
      my $agenda_filename=db_select($dbh,"select filename from wg_agenda where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num and irtf=$irtf");
      $group_name = "<a href=\"http://www3.ietf.org/proceedings/$dir_name/agenda/$agenda_filename\">$group_name</a>" if ($agenda_filename);
      if ($group_acronym =~ /plenary/) {
        my $p_agenda_text = `cat /home/master-site/proceedings/$dir_name/agenda/$group_acronym.txt`;
        $p_agenda_text = "THE AGENDA HAS NOT BEEN UPLOADED YET" unless my_defined($p_agenda_text);
        $html_body .= "</table>\n";
        $html_body .= "<br>\n$arbreak_time2 Afternoon Refreshment Break - $break_area_name<br>\n" if ($prev_session_name eq "Afternoon Session II" and my_defined($arbreak_time2));
        $html_body .= qq{
<b>$time_desc $session_name - $room_name</b><br>
<pre>
$p_agenda_text
</pre>
<table>
}; 
        next;      
      }
      if ($session_name ne $prev_session_name) {
        if ($prev_session_name ne "") {
          $html_body .= "</table><br>\n";
        }
        $html_body .= "$break_time Break<br>\n" if ($session_name eq "Afternoon Session I");
        $html_body .= "$arbreak_time1 Afternoon Refreshment Break - $break_area_name<br>\n" if ($prev_session_name eq "Afternoon Session I" and my_defined($arbreak_time1));
        $html_body .= "$arbreak_time2 Afternoon Refreshment Break - $break_area_name<br>\n" if ($prev_session_name eq "Afternoon Session II" and my_defined($arbreak_time2));
        $prev_session_name=$session_name;
        $html_body .= "<b>$time_desc $session_name</b>\n<table border=\"0\" cellspacing=\"0\" cellpadding=\"0\" width=\"800\">\n";
      }
      my $group_type_id = db_select($dbh,"select group_type_id from groups_ietf where group_acronym_id=$group_acronym_id");
      $group_acronym = "<a href=\"http://www.ietf.org/html.charters/$group_acronym-charter.html\">$group_acronym</a>" if ($group_acronym_id > 30 and $group_type_id==1);
      $html_body .= "<tr><td width=\"200\">$room_name</td><td width=\"50\">$area</td><td width=\"100\">$group_acronym</td><td>$group_name"; 
      $html_body .= " - <b>$special_agenda_note</b>" if my_defined($special_agenda_note); 
      $html_body .= " </td></tr>\n";
    }

  }
  $html_body .= "</table>\n<br>\n";
}
db_update($dbh,"drop table temp_agenda$table_id");
$dbh->disconnect();
print $q->p($html_top),
      $q->p($html_body),
      $q->p($html_bottom),
      $q->end_html;

exit;

