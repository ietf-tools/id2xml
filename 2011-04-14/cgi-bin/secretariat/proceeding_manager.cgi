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

use constant BUFFER_SIZE => 16_384;
use constant MAX_FILE_SIZE => 25_242_880; # 5 MB Max file size
use constant MAX_OPEN_TRIES => 100;
$CGI::DISABLE_UPLOADS = 0;
$CGI::POST_MAX = MAX_FILE_SIZE;

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
$preliminary_url = ($devel_mode)?"https://datatracker.ietf.org/public/meeting_materials_devel.cgi":"https://datatracker.ietf.org/public/meeting_materials.cgi";
my $q = new CGI;
$program_name = "proceeding_manager.cgi";
$host_name = "www.ietf.org";
$host_name = "datatracker.ietf.org" if ($devel_mode); #DEPLOY - Enable
$program_title = "IETF Proceedings Manager";
$style_url="http://www.ietf.org/css/proceedings.css";
$proceeding_dir = "proceedings";
$web_dir = "/a/www/www6s/$proceeding_dir";
$web_dir = "/a/www/ietf-datatracker/htdocs/$proceeding_dir" if ($devel_mode);
#$data_dir = "/home/mlee/DATA-IETF/PROCEEDING";
$table_header = qq{<table cellpadding="0" cellspacing="0" border="0">
};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">};
$form_header_noname = qq{<form action="$program_name" method="POST">};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">};
$form_header_get = qq{<form action="$program_name" method="GET">};
$form_header_upload = qq{<form action="$program_name" method="POST" ENCTYPE="multipart/form-data" name="upload_form">};
$SOURCE_DIR="/a/www/ietf-datatracker/release/PROCEEDINGS";
$first_slide = "sld1.htm";
$html_top = qq|
<link rel="stylesheet" type="text/css" href="$style_url" />
<blockquote>
<h2><center>$program_title</center></h2>
<br><br>
|;
$html_bottom = qq{
</blockquote>
};
$meeting_num = $q->param("meeting_num") or 0;
my $max_meeting_num=db_select($dbh,"select max(meeting_num) from proceedings");
$meeting_scheduled_field = ($max_meeting_num==$meeting_num)?"meeting_scheduled":"meeting_scheduled_old";

$html_body = get_html_body($q);
$dbh->disconnect();
print $q->header("text/html"),
	$q->start_html(-title=>$program_title),
	$q->p($html_top),
	$q->p($html_body),
	$q->p($html_bottom),
	$q->end_html;
exit;

sub error {
  my ($q,$reason)=@_;
                                                                                                
  print $q->header("text/html"),
        $q->start_html("Error"),
        $q->h1("Error"),
        $q->p("Your request was not proceed because the following error ",
              "occured: "),
        $q->p($q->i($reason)),
        $q->end_html;
  exit;
}

sub get_html_body {
   my $q = shift;
   my $meeting_num=$q->param("meeting_num");
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
   <input type="hidden" name="command" value="display_meeting">
   <input type="hidden" name="meeting_num" value="$meeting_num">
   <input type="submit" value="Main Menu">
   <input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true">
   </form>
} if (($command ne "retrieve_old_meeting" and $command ne "main_screen") );
   $html_txt .= qq{
   $form_header_bottom
   <input type="hidden" name="command" value="main_screen">
   <input type="submit" value=" First Screen ">
   </form>
   }  if (my_defined($command));
   return $html_txt;
}

sub main_screen {
  return qq{
<p><font size=+1>
<li><a href="$program_name?command=create_new_meeting_pre"> Create New Proceedings</a><br>
<li><a href="$program_name?command=retrieve_old_meeting"> Retrieve Old Proceedings</a><br>
</font>
<p><p>
};
}

sub create_new_meeting_pre {
  my $q=shift;
  return qq{
<h3>Create New IETF Meeting: Step 1</h3>
$form_header_get
<input type="hidden" name="command" value="create_new_meeting">
<ul><li> Enter IETF Meeting Number: <input type="text" name="meeting_num" size="4"></li></ul>
<input type="submit" value = " Proceed ">
</form><br><br><br>
};
}

sub create_new_meeting {
  my $q=shift;
  my $meeting_num = $q->param("meeting_num");
  my $proceeding_exist = db_select($dbh,"select count(*) from proceedings where meeting_num=$meeting_num");
  return "<h3>Proceedings for IETF $meeting_num is existing</h3>" if ($proceeding_exist);
  my $meeting_exist = db_select($dbh,"select count(*) from meetings where meeting_num=$meeting_num");
  my $meeting_info = "";
  if ($meeting_exist) {
    my ($start_date,$end_date,$city,$state,$country) = db_select($dbh,"select start_date,end_date,city,state,country from  meetings where meeting_num=$meeting_num");
    $meeting_info = qq{
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
};
  }
  my $html_txt = "<h3>Create New IETF Meeting: Step 2</h3>\n";
  $html_txt .= qq{
$form_header_post
<input type="hidden" name="command" value="create_new_confirm">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="meeting_exist" value="$meeting_exist">
<h4>IETF Meeting $meeting_num</h4>
$meeting_info
<h4>IETF Meeting $meeting_num Proceeding</h4>
$table_header
<tr><td> <li> Enter home directory name for proceeding materials (eg. 75) &nbsp; &nbsp; </td>
<td><input type="text" name="dir_name" size="15"></td></tr>
<tr><td> <li> Enter the Beginning date of submission </td>
<td><input type="text" name="sub_begin_date" size="15"></td></tr>
<tr><td> <li> Enter the Cut-Off date of submission </td>
<td><input type="text" name="sub_cut_off_date" size="15"></td></tr>
<tr><td> <li> Enter the Submission Corrections Cut Off Date </td>
<td><input type="text" name="c_sub_cut_off_date" size="15"></td></tr>
<tr><td> <li> Enter the time frame for Progress Report </td>
<td><input type="text" name="pr_from_date" size="15"> to <input type="text" name="pr_to_date" size="15"></td></tr>

</table>
<input type="submit" value=" Proceed "><br>

</form>

};
  return $html_txt;
}
sub create_new_confirm {
  my $q=shift;
  my $meeting_exist = $q->param("meeting_exist");
  my $meeting_num = $q->param("meeting_num");
  my $dir_name = $q->param("dir_name");
  my $sub_begin_date = $q->param("sub_begin_date");
  my $sub_cut_off_date = $q->param("sub_cut_off_date");
  my $c_sub_cut_off_date = $q->param("c_sub_cut_off_date");
  my $pr_from_date=$q->param("pr_from_date");
  my $pr_to_date=$q->param("pr_to_date");
  my $meeting_info = "";
  if ($meeting_exist) {
    my ($start_date,$end_date,$city,$state,$country) = db_select($dbh,"select start_date,end_date,city,state,country from  meetings where meeting_num=$meeting_num");
    $meeting_info = qq{
$table_header
<tr><td>Meeting Start Date: </td><td>$start_date</td></tr>
<tr><td>Meeting End Date: </td><td>$end_date</td></tr>
<tr><td>Meeting City: </td><td>$city</td></tr>
<tr><td>Meeting State: </td><td>$state</td></tr>
<tr><td>Meeting Country: </td><td>$country</td></tr>
</table>
};

  } else {
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
}
  }
  my $html_txt = "<h3>Create New IETF Meeting: Step 3 - Confirmation</h3>\n";
  $html_txt .= qq{
$form_header_post
<input type="hidden" name="command" value="do_create_new">
<input type="hidden" name="meeting_exist" value="$meeting_exist">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="dir_name" value="$dir_name">
<input type="hidden" name="sub_begin_date" value="$sub_begin_date">
<input type="hidden" name="sub_cut_off_date" value="$sub_cut_off_date">
<input type="hidden" name="c_sub_cut_off_date" value="$c_sub_cut_off_date">
<input type="hidden" name="pr_from_date" value="$pr_from_date">
<input type="hidden" name="pr_to_date" value="$pr_to_date">

<h4>IETF Meeting $meeting_num</h4>
$meeting_info
<h4>IETF Meeting $meeting_num Proceeding</h4>
$table_header
<tr><td> <li> IETF Meeting Number </td><td>$meeting_num</td></tr>
<tr><td> <li> Home directory name for proceeding materials (eg. 75) &nbsp; &nbsp; </td>
<td>$dir_name</td></tr>
<tr><td> <li> Beginning date of submission </td>
<td>$sub_begin_date</td></tr>
<tr><td> <li> Cut-Off date of submission </td>
<td>$sub_cut_off_date</td></tr>
<tr><td> <li> Submission Corrections Cut Off Date </td>
<td>$c_sub_cut_off_date</td></tr>
<tr><td> <li> Progress Report Time Frame </td>
<td>$pr_from_date to $pr_to_date </td></tr>
</table>
<input type="submit" value=" Proceed "><br>

</form>

};

  return $html_txt;

}

sub do_create_new {
  my $q=shift;
  my $meeting_num = $q->param("meeting_num");
  my $old_meeting_num = $meeting_num-1;
  my $meeting_exist = $q->param("meeting_exist");
  my $dir_name = $q->param("dir_name");
  my $sub_begin_date = $q->param("sub_begin_date");
  my $sub_cut_off_date = $q->param("sub_cut_off_date");
  my $pr_from_date = $q->param("pr_from_date");
  my $pr_to_date = $q->param("pr_to_date");
  my $c_sub_cut_off_date = $q->param("c_sub_cut_off_date");
  unless ($meeting_exist) {
    my $start_date = $q->param("start_date");
    my $end_date = $q->param("end_date");
    my $city = db_quote($q->param("city"));
    my $state=db_quote($q->param("state"));
    my $country = db_quote($q->param("country"));
    db_update($dbh,"insert into meetings (meeting_num,start_date,end_date,city,state,country) values ($meeting_num,'$start_date','$end_date',$city,$state,$country)");
  }
  system "mkdir $web_dir/$dir_name";
  system "mkdir $web_dir/$dir_name/slides";
  system "cp $web_dir/base_images/* $web_dir/$dir_name/slides/.";
  system "mkdir $web_dir/$dir_name/minutes";
  system "mkdir $web_dir/$dir_name/agenda";
### This routine needs to be performed separtely
# Proceeding Tool can be opened way before the meeting start.
# proceeding database should be created right before the meeting
###
#  unless (-e "$data_dir/pr_dump_$old_meeting_num.sql") {
#    system "/usr/bin/mysqldump --user=mlee --password=sunnyohm proceeding > $data_dir/pr_dump_$old_meeting_num.sql" unless $devel_mode;
#  }
#  unless ($devel_mode) {
#    system "/usr/bin/mysqldump --user=mlee --password=sunnyohm ietf > $data_dir/pr_dump.sql";
#    system "/home/mlee/DATA-IETF/PROCEEDING/pop_db_proceeding.sh";
#  }
  my $pre_exist = db_select($dbh,"select count(*) from proceedings where meeting_num=$meeting_num");
  db_update($dbh,"insert into proceedings (meeting_num,dir_name,sub_begin_date,sub_cut_off_date,frozen,c_sub_cut_off_date,pr_from_date,pr_to_date) values ($meeting_num,'$dir_name','$sub_begin_date','$sub_cut_off_date',0,'$c_sub_cut_off_date','$pr_from_date','$pr_to_date')") unless ($pre_exist);
  # Create place holder for  
# need to be disabled from here
  #$pre_exist = db_select($dbh,"select count(*) from minutes where meeting_num=$meeting_num and group_acronym_id=-1");
  #unless ($pre_exist) {
  #  db_update($dbh,"insert into minutes (meeting_num,group_acronym_id,filename) values ($meeting_num,-1,'0')"); # Plenary Wednesday
  #  db_update($dbh,"insert into wg_agenda (meeting_num,group_acronym_id,filename) values ($meeting_num,-1,'0')"); # Plenary Wednesday
  #  db_update($dbh,"insert into minutes (meeting_num,group_acronym_id,filename) values ($meeting_num,-2,'0')"); #Plenary Thursday
  #  db_update($dbh,"insert into wg_agenda (meeting_num,group_acronym_id,filename) values ($meeting_num,-2,'0')"); #Plenary Thursday
  #}
  #my @List = db_select_multiple($dbh,"select group_acronym_id from groups_ietf where meeting_scheduled='yes'");
  #for my $array_ref (@List) {
  #  my ($group_acronym_id) = @$array_ref;
  #  my $gr_exist = db_select($dbh,"select count(*) from minutes where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id");
  #  my $gr_exist_agenda = db_select($dbh,"select count(*) from minutes where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id");
  #  db_update($dbh,"insert into minutes (meeting_num,group_acronym_id,filename) values ($meeting_num,$group_acronym_id,'0')") unless ($gr_exist);
  #  db_update($dbh,"insert into  wg_agenda (meeting_num,group_acronym_id,filename) values ($meeting_num,$group_acronym_id,'0')") unless ($gr_exist_agenda);
  #}
# need to be disabled to here
  return qq{
Meeting was created successfuly<br>
};
}

sub retrieve_old_meeting {
  my $q=shift;
  my $html_txt = qq{
<h2>Retrieve Old  IETF Meeting</h2>
$form_header_get
<input type="hidden" name="command" value="display_meeting">
<select name="meeting_num"><option value="0">--Select Meeting</option>
};
  my @List = db_select_multiple($dbh,"select meeting_num from proceedings order by meeting_num");
  for my $array_ref (@List) {
    my ($meeting_num) = @$array_ref;
    $html_txt .= "<option value=\"$meeting_num\">IETF $meeting_num</option>\n";
  }
  $html_txt .= qq{</select>
<br><br>
<input type="submit" value=" Retrieve ">
</form>
<br><br>

};
  return $html_txt;
}

sub display_meeting {
  my $q=shift;
  my $meeting_num = $q->param("meeting_num");
  my $message = $q->param("message") or "";
  my ($dir_name,$sub_begin_date,$sub_cut_off_date,$c_sub_cut_off_date,$pr_from_date,$pr_to_date) = db_select($dbh,"select dir_name,sub_begin_date,sub_cut_off_date,c_sub_cut_off_date,pr_from_date,pr_to_date from proceedings where meeting_num=$meeting_num");
  my $frozen = db_select($dbh,"select frozen from proceedings where meeting_num=$meeting_num");
  my $button_html = "";
  if ($frozen) {
    $button_html = "<font color=\"red\"><b>This is a frozen Proceedings</b></font>\n";
  } else {
    $button_html = qq{
$form_header_get
<input type="hidden" name="command" value="gen_final">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="submit" value = " CREATE FINAL PROCEEDINGS ">
</form>
$form_header_noname
<input type="hidden" name="command" value="freeze_proceeding">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="submit" value = " FREEZE THIS PROCEEDINGS ">
</form>

};
  }
  my $html_txt = qq{
<h2>IETF $meeting_num</h2>
<font color="red">$message</font>
<hr>
$form_header_post
<input type="hidden" name="command" value="do_update_meeting_info">
<input type="hidden" name="meeting_num" value="$meeting_num">
$table_header
<tr><td>Submission Start Date:</td>
    <td><input type="text" name="sub_begin_date" value="$sub_begin_date"></td>
</tr>
<tr><td>Submission Cut Off Date: &nbsp; &nbsp; </td>
    <td><input type="text" name="sub_cut_off_date" value="$sub_cut_off_date"></td>
</tr>
<tr><td>Submission Corrections Cut Off Date: &nbsp; &nbsp; </td>
    <td><input type="text" name="c_sub_cut_off_date" value="$c_sub_cut_off_date"></td>
</tr>
<tr><td>Progress Report Time Frame: </td>
    <td><input type="text" name="pr_from_date" value="$pr_from_date"> to <input type="text" name="pr_to_date" value="$pr_to_date"></td>
</tr>
</table>
<br>
<input type="submit" value=" Update Info ">
</form><br>
<li><a href="$program_name?command=select_group&meeting_num=$meeting_num">Upload New Presentations/Agenda/Minutes</a></li>
<li><a href="$program_name?command=view_queue&meeting_num=$meeting_num">Convert PPT/DOC files in Queue</a></li>
<li><a href="$preliminary_url?meeting_num=$meeting_num">View Preliminary Page</a></li>
<li><a href="add_attendees.cgi?meeting_num=$meeting_num">Upload Attendees</a></li>
<br><br><br>
$button_html
<br><br><br>
};
  return $html_txt;
}

sub view_queue {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $dir_name=db_select($dbh,"select dir_name from proceedings where meeting_num=$meeting_num");
  my @List = db_select_multiple($dbh,"select id,slide_name,slide_num,group_acronym_id,irtf,interim from slides  where meeting_num=$meeting_num and in_q=1");
  my $html_txt = qq{<h2>IETF $meeting_num: PPT/DOC Files in Queue</h2>
<hr>
<ul>
};
  for my $array_ref (@List) {
    my ($id,$slide_name,$slide_num,$group_acronym_id,$irtf,$interim) = @$array_ref;
    my $group_name=db_select($dbh,"select acronym from acronym where acronym_id=$group_acronym_id");
    $group_name=db_select($dbh,"select irtf_acronym from irtf where irtf_id=$group_acronym_id") if ($irtf);
   $group_name .= "<font color=\"red\">(INTERIM)</font>" if ($interim);
    
    $html_txt .= qq{<li> $slide_name <b>($group_name)</b>  <a href="http://$host_name/$proceeding_dir/$dir_name/slides/$group_name-$slide_num.ppt">Download</a> <a href="$program_name?command=upload_slide_minute&id=$id&meeting_num=$meeting_num">Upload</a></li>
};
  }
  $html_txt .= "</ul><br><br>\n";
  return $html_txt;
}

sub freeze_proceeding {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  db_update($dbh,"update proceedings set frozen=1 where meeting_num=$meeting_num");
  $q->param('message'=>"This Proceedings are now frozen");
  return display_meeting($q);
}

sub gen_final {
  my $q=shift;
  my $meeting_num=$q->param("meeting_num");
  my $dir_name=db_select($dbh,"select dir_name from proceedings where meeting_num=$meeting_num");
  open OUT,">/a/www/ietf-datatracker/release/PROCEEDINGS/header.pl";
  print OUT qq{\$TARGET_DIR = "/a/www/www6s/proceedings/$dir_name";
\$SOURCE_DIR = "/a/www/ietf-datatracker/release/PROCEEDINGS";
};
  close OUT;
  my $frozen = db_select($dbh,"select frozen from proceedings where meeting_num=$meeting_num");
  unless ($frozen) {
    system "$SOURCE_DIR/gen_index.pl $meeting_num";
    system "$SOURCE_DIR/gen_introduction.pl $meeting_num";
    system "$SOURCE_DIR/gen_ack.pl $meeting_num 1";
    system "$SOURCE_DIR/gen_pr.pl $meeting_num 2";
    system "$SOURCE_DIR/gen_agenda_pr.pl $meeting_num 3";
    system "$SOURCE_DIR/gen_overview.pl 4";
    system "$SOURCE_DIR/gen_fm.pl $meeting_num 5";
    system "$SOURCE_DIR/gen_toc.pl $meeting_num";
    system "$SOURCE_DIR/gen_plenary.pl $meeting_num";
    system "$SOURCE_DIR/gen_attendees.pl $meeting_num";
    system "$SOURCE_DIR/gen_dnm.pl $meeting_num"; 
    $q->param('message'=>"Final PROCEEDING has been created");
  } else {
    $q->param('message'=>"You cannot modify a FROZEN Proceedings");
  }
  return display_meeting($q);
}

sub select_group {
  my $q=shift;
  my $meeting_num = $q->param("meeting_num");
  my $html_txt = qq{
<h2>IETF $meeting_num: Upload Presentations/Agenda/Minutes</h2>
<hr>
<b>Step 1:<b><br><br>
$form_header_get
<input type="hidden" name="command" value="upload_slide_minute">
<input type="hidden" name="meeting_num" value="$meeting_num">
<select name="group_acronym_id">
<option value="0">--Select Group/BOF/Plenary</option>
<option value="-1">Wednesday Plenary</option>
<option value="-2">Thursday Plenary</option>
<option value="-3">---------------------------</option>
};
  my @List = db_select_multiple($dbh,"select acronym,group_acronym_id from acronym a, groups_ietf b where $meeting_scheduled_field='YES' and b.group_acronym_id=a.acronym_id order by acronym");
  for my $array_ref (@List) {
    my ($acronym,$group_acronym_id) = @$array_ref;
    $html_txt .= "<option value=\"$group_acronym_id\">$acronym</option>\n";
  }
  $html_txt .= qq{</select> <input type="submit" value=" Proceed ">
</form><br><br><br>

$form_header_get
<input type="hidden" name="command" value="upload_slide_minute">
<input type="hidden" name="meeting_num" value="$meeting_num">
<select name="group_acronym_id"> <option value="0">--Select Training </option>
};
  my @List3 = db_select_multiple($dbh,"select name,acronym_id from acronym a where acronym_id in (select group_acronym_id from wg_meeting_sessions where group_acronym_id < -2 and meeting_num=$meeting_num)");
  for my $array_ref (@List3) {
    my ($acronym,$acronym_id) = @$array_ref;     
    $html_txt .= "<option value=\"$acronym_id\">$acronym</option>\n";
  }                                                                                                    
  $html_txt .= qq{
</select>
<input type="submit" value=" Proceed "> </form><br><br><br>


$form_header_get
<input type="hidden" name="command" value="upload_slide_minute">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="irtf" value="1">
<select name="group_acronym_id">
<option value="0">--Select IRTF Group </option>
};
  my @List2 = db_select_multiple($dbh,"select irtf_acronym,irtf_id from irtf order by irtf_acronym");
  for my $array_ref (@List2) {
    my ($irtf_acronym,$irtf_id) = @$array_ref;
    $html_txt .= "<option value=\"$irtf_id\">$irtf_acronym</option>\n";
  }

  $html_txt .= qq{
</select> 
<input type="submit" value=" Proceed ">
</form><br><br><br>
$form_header_get
<input type="hidden" name="command" value="upload_slide_minute">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="interim" value="1">
<select name="group_acronym_id">
<option value="0">--Select Interim Meeting Group/BOF</option>
};
  for my $array_ref (@List) {
    my ($acronym,$group_acronym_id) = @$array_ref;
    $html_txt .= "<option value=\"$group_acronym_id\">$acronym</option>\n";
  }
  $html_txt .= qq{</select> <input type="submit" value=" Proceed ">
</form><br><br><br>

};
  return $html_txt;
}

sub do_update_meeting_info {
  my $q=shift;
  $q->param('message'=>"Meeting Information was updated");
  my $meeting_num = $q->param("meeting_num");
  my $sub_begin_date = $q->param("sub_begin_date");
  my $sub_cut_off_date = $q->param("sub_cut_off_date");
  my $c_sub_cut_off_date = $q->param("c_sub_cut_off_date");
  my $pr_from_date=$q->param("pr_from_date");
  my $pr_to_date=$q->param("pr_to_date");
  db_update($dbh,"update proceedings set sub_begin_date='$sub_begin_date',sub_cut_off_date='$sub_cut_off_date',c_sub_cut_off_date='$c_sub_cut_off_date', pr_from_date='$pr_from_date', pr_to_date='$pr_to_date' where meeting_num=$meeting_num");
  return display_meeting($q);
}
sub upload_slide_minute {
  my $q=shift;
  my $meeting_num = $q->param("meeting_num");
  my $dir_name = db_select($dbh,"select dir_name from proceedings where meeting_num=$meeting_num");
  my $existing=0;
  my $group_acronym_id=$q->param("group_acronym_id");
  my $irtf=(defined($q->param("irtf")) and $q->param("irtf") > 0)?$q->param("group_acronym_id"):0;
  my $irtf_param=($irtf)?"&irtf=1":"";
  my $interim=(defined($q->param("interim")))?$q->param("interim"):0;
  my $present_checked = "";
  my $present_name="";
  my $html_checked="";
  if (defined($q->param("id"))) {
    $existing=$q->param("id");
    ($group_acronym_id,$irtf,$interim,$present_name) = db_select($dbh,"select group_acronym_id,irtf,interim,slide_name from slides where id=$existing");
    $present_checked = "checked";
    $html_checked="checked";
  }
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
#    my $is_area = db_select($dbh,"select count(*) from areas where area_acronym_id=$group_acronym_id and status_id=1");
#    $group_name_short = $group_name."area" if ($is_area);
#    $group_name = $group_name." area" if ($is_area);
  }
  my $html_txt =qq{
<font color="red">$message</font>
<h2>IETF $meeting_num: Upload Presentations/Agenda/Minutes: <font color="red">$group_name</font></h2>
<hr>
<b>Step 2:</b><br><br>
$form_header_upload
<input type="hidden" name="command" value="upload_file">
<input type="hidden" name="group_name" value="$group_name_short">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="group_acronym_id" value="$group_acronym_id">
<input type="hidden" name="irtf" value="$irtf">
<input type="hidden" name="interim" value="$interim">
<input type="hidden" name="existing" value="$existing">
<table bgcolor="#eeeeee" cellpadding="3" cellspacing="0" border="0" width="600">
  <tr><td colspan="2">
    <ul><li>Upload new presentation/agenda/minutes</li></ul></td></tr>
  <tr><td>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp<input type="radio" name="slide_minute" value="1" $present_checked> Presentation </td></tr>
  <tr><td>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp<input type="radio" name="slide_minute" value="3"> Agenda </td></tr>
  <tr><td>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp<input type="radio" name="slide_minute" value="2"> Minutes </td></tr>
  <tr>
    <td><ul><li>Name of presentation (for presentations only): </li></ul> </td>
    <td><input type="text" name="slide_name" size="50" value="$present_name"></td>
  </tr>
  <tr>
    <td colspan="2"><ul><li> Select file format for presentation/minutes:</li></ul></td>
  </tr>
  <tr><td>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp<input type="radio" name="slide_type_id" value="1" $html_checked> html (Zipped) </td></tr>
  <tr><td>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp<input type="radio" name="slide_type_id" value="2"> pdf </td></tr>
  <tr><td>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp<input type="radio" name="slide_type_id" value="3"> txt </td></tr>
<tr>
    <td><ul><li>Select file: </li></ul></td>
    <td><input type="FILE" name="file"></td>
  </tr>
  <tr><td colspan="2">&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp
&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp
<input type="submit" value="Upload Now"></td></tr>
</form>
</table>
<br><br>
<hr>
<h2>Current Agenda</h2>
};
my $agenda_filename = db_select($dbh,"select filename from wg_agenda where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim");
$html_txt .= qq{<ul><li><a href="http://$host_name/$proceeding_dir/$dir_name/agenda/$agenda_filename">View Agenda</a> &nbsp; &nbsp; &nbsp; &nbsp; <a href="$program_name?command=delete_file&meeting_num=$meeting_num&group_acronym_id=$group_acronym_id&is_minute=2$irtf_param&group_name_short=$group_name_short&interim=$interim" onclick="return confirm('Do you really want to delete this file?');"> [ DELETE ] </a></li></ul><br>
} if (my_defined($agenda_filename) and $agenda_filename ne "0"); 
$html_txt .= qq{
<hr>
<h2>Current Minutes</h2>
};
my $minute_filename = db_select($dbh,"select filename from minutes where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim");
$html_txt .= qq{<ul><li><a href="http://$host_name/$proceeding_dir/$dir_name/minutes/$minute_filename">View Minute</a> &nbsp; &nbsp; &nbsp; &nbsp; <a href="$program_name?command=delete_file&meeting_num=$meeting_num&group_acronym_id=$group_acronym_id&is_minute=1$irtf_param&group_name_short=$group_name_short&interim=$interim" onclick="return confirm('Do you really want to delete this file?');"> [ DELETE ] </a></li></ul><br>
} if (my_defined($minute_filename) and $minute_filename ne "0");
$html_txt .= qq{
<hr>
<h2>Current Presentations</h2>
( <font size=+1 color=\"red\"> <b> *</b></font> - In waiting to be converted to HTML format)<br>
$form_header_noname
<input type="hidden" name="command" value="reorder">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="group_acronym_id" value="$group_acronym_id">
<input type="hidden" name="irtf" value="$irtf">
<input type="hidden" name="interim" value="$interim">
};
  my @List_slides = db_select_multiple($dbh,"select slide_num,slide_type_id,slide_name,order_num,id,in_q from slides where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim order by order_num");
  $html_txt .= "<ul>\n";
  for my $array_ref (@List_slides) {
    my ($slide_num,$slide_type_id,$slide_name,$order_num,$slide_id,$in_q) = @$array_ref;
    my $delete_button = qq{ &nbsp; &nbsp; &nbsp; &nbsp; <a href="$program_name?command=delete_file&meeting_num=$meeting_num&group_acronym_id=$group_acronym_id&is_minute=0$irtf_param&slide_num=$slide_num&group_name_short=$group_name_short&interim=$interim" onclick="return confirm('Do you really want to delete this file?');"> [ DELETE ] </a>};
    $html_txt .= "<li> <input type=\"text\" name=\"$slide_id\" value=\"$order_num\" size=\"1\"> \n";
    if ($in_q) {
        $html_txt .= " <a href=\"http://$host_name/$proceeding_dir/$dir_name/slides/$group_name_short-$slide_num.ppt\">$slide_name</a> <font color=\"red\"><b>*</b></font> $delete_button</li><br>\n";
    } else {
      if ($slide_type_id == 1) {
        $html_txt .= " <a href=\"http://$host_name/$proceeding_dir/$dir_name/slides/$group_name_short-$slide_num/$first_slide\">$slide_name</a> $delete_button</li><br>\n";
      } elsif ($slide_type_id == 2) {
        $html_txt .= " <a href=\"http://$host_name/$proceeding_dir/$dir_name/slides/$group_name_short-$slide_num.pdf\">$slide_name</a> $delete_button</li><br>\n";
      } elsif ($slide_type_id ==3) {
        $html_txt .= " <a href=\"http://$host_name/$proceeding_dir/$dir_name/slides/$group_name_short-$slide_num.txt\">$slide_name</a> $delete_button</li><br>\n";
      }
    }
  }
  $html_txt .= qq{
</ul>
<input type="submit" value=" RE-ORDER ">
</form>
<hr>
$form_header_get
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="hidden" name="command" value="select_group">
<input type="submit" value="Select Other Group">
</form>
<br><br><br>
};
  return $html_txt;
}

sub reorder {
  my $q=shift;
  foreach ($q->param) {
    if (/^\d/) {
      my $slide_id=$_;
      my $order_num = (my_defined($q->param("$slide_id")))?$q->param("$slide_id"):99;
      db_update($dbh,"update slides set order_num=$order_num where id=$slide_id");
    }
  }
  $q->param('message'=>"Presentations have been re-ordered");
  return upload_slide_minute($q);
}

sub upload_file {
  my $q=shift;
  my $group_name=$q->param("group_name");
  my $meeting_num=$q->param("meeting_num");
  my $group_acronym_id=$q->param("group_acronym_id");
  my $slide_minute = $q->param("slide_minute");
  my $slide_type_id=$q->param("slide_type_id");
  my $interim = $q->param("interim");
  my $irtf=$q->param("irtf");
  my $existing=$q->param("existing");
  my $sqlStr="";
  my $local_dir = "";
  my $filename = $group_name;
  my $slide_type = "";
  if ($slide_type_id==1) {
    $slide_type .="html";
  } elsif ($slide_type_id==2) {
    $slide_type .= "pdf";
  } elsif ($slide_type_id==3) {
    $slide_type .= "txt";
  }
  my $dir_name = db_select($dbh,"select dir_name from proceedings where meeting_num=$meeting_num");
  if ($slide_minute ==1) { #Upload SLide
    $slide_type ="zip" if ($slide_type_id==1);
    $local_dir = "slides";
    $slide_name=$q->param("slide_name");
    error($q,"Please enter slide name") unless my_defined($slide_name);
    $slide_name = db_quote($slide_name);
    my $slide_num = db_select($dbh,"select max(slide_num) from slides where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim");
    unless (my_defined($slide_num)) {
      $slide_num = 0;
    } else {
      $slide_num++;
    }
    $sqlStr = "insert into slides (meeting_num,group_acronym_id,slide_num,slide_type_id,slide_name,irtf,interim) values ($meeting_num,$group_acronym_id,$slide_num,$slide_type_id,$slide_name,$irtf,$interim)";
    if ($existing) {
      ($slide_num,$interim,$irtf,$group_acronym_id) = db_select($dbh,"select slide_num,interim,irtf,group_acronym_id from slides where id=$existing");
      $slide_type_id=1;
      $slide_type="zip";
      $sqlStr = "update slides set slide_type_id=$slide_type_id,in_q=0 where id=$existing";
      $group_name = db_select($dbh,"select acronym from acronym where acronym_id=$group_acronym_id");
    }
    $filename = $group_name unless $irtf;
    $filename .= "-$slide_num.$slide_type";
    #my $minute_exist = db_select($dbh,"select count(*) from minutes where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim");
    #unless ($minute_exist) {
    #  db_update($dbh,"insert into minutes (meeting_num,group_acronym_id,filename,irtf,interim) values ($meeting_num,$group_acronym_id,'0',$irtf,$interim)");
    #}
  } elsif ($slide_minute == 2 or $slide_minute == 3) { #Minutes or Agenda
    my $training = ($group_acronym_id < -2)?1:0;
    my $table_name = ($slide_minute == 2)?"minutes":"wg_agenda";
    $local_dir = ($slide_minute == 2)?"minutes":"agenda";
    #if ($irtf or $interim or $training) {
    #  db_update($dbh,"delete from $table_name where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim");
    #  db_update($dbh,"insert into $table_name (meeting_num,group_acronym_id,filename,irtf,interim) values ($meeting_num,$group_acronym_id,'0',$irtf,$interim)");
    #}
    my $exist = db_select($dbh,"select count(*) from $table_name where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and filename <> '0' and irtf=$irtf and interim=$interim");
    $filename ="$filename.$slide_type";
    $sqlStr = ($exist)?"update $table_name set filename='$filename' where group_acronym_id=$group_acronym_id and meeting_num=$meeting_num and irtf=$irtf and interim=$interim":"insert into $table_name (meeting_num,group_acronym_id,filename,irtf,interim) values ($meeting_num,$group_acronym_id,'$filename',$irtf,$interim)";
  } else {
    error($q,"Please select Presentation/Agenda/Minutes");
  }

#UPload file first
  $q->cgi_error and error($q,"Error transferring file: ".$q->cgi_error);
  my $file = $q->param("file")  || error ($q,"No file received.");
  my $fh = $q->upload("file", -override=>1);
  unless ($fh) {
    error ($q,"Invalid File - $file, $fh");
  }
  my $type=$q->uploadInfo($fh)->{'Content-Type'};
  seek($fh,0,2);
  my $size=tell($fh);
  seek($fh,0,0);
  my $buffer = "";
  open OUTPUT,">$web_dir/$dir_name/$local_dir/$filename";
  binmode $fh;
  binmode OUTPUT;
  while (read($fh,$buffer,BUFFER_SIZE)) {
    print OUTPUT $buffer;
  }
  close OUTPUT;
  if ($slide_minute == 1 and $slide_type_id == 1) { # Zipped files must have been uploaded.
                                                    # create a new dir and extract file there
    error ($q,"Please upload zip file only for html slides") unless ($file =~ /.zip$/);
    my $gr_dir = $filename;
    $gr_dir =~ s/.zip$//;
    my $ppt_name_low=lc($gr_dir);
    system "mkdir $web_dir/$dir_name/$local_dir/$gr_dir";
    system "mv $web_dir/$dir_name/$local_dir/$filename $web_dir/$dir_name/$local_dir/$gr_dir/$filename";
    chdir "$web_dir/$dir_name/$local_dir/$gr_dir";
    system "/usr/bin/unzip $filename";
    
#REMOVED CODE TO DELETE THE ORIGINAL SLIDES FILE ON 02/19/2010
#    unlink $filename;
#    unlink "$web_dir/$dir_name/$local_dir/$gr_dir.ppt" if ($existing);

    system "cp $gr_dir.ppt $ppt_name_low.ppt";
  }
#Update database here
  db_update($dbh,$sqlStr);
  $q->param('message'=>"File Upload was successful: $web_dir/$dir_name/$local_dir/$filename - $size byte<br>DO NOT refresh this page: you will repeat the last upload action.");
  return upload_slide_minute($q);
}

sub delete_file {
  my $q=shift;
  my $meeting_num = $q->param("meeting_num");
  my $group_acronym_id=$q->param("group_acronym_id");
  my $is_minute = $q->param("is_minute");
  my $sqlStr = "";
  my $deleted_file = "";
  if ($is_minute) {
    my $dir_name = ($is_minute==1)?"minutes":"agenda";
    my $table_name= ($is_minute==1)?"minutes":"wg_agenda";
    $deleted_file = "$dir_name/";
    $deleted_file .= db_select($dbh,"select filename from $table_name where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id");
    $sqlStr = "delete from $table_name where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id";
    #$sqlStr = "update minutes set filename='0' where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id";
  } else {
    my $slide_num = $q->param("slide_num");
    my $group_name_short=$q->param("group_name_short");
    $deleted_file = "slides/$group_name_short-$slide_num*";
    $sqlStr = "delete from slides where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and slide_num=$slide_num";
  }
  my $dir_name = db_select($dbh,"select dir_name from proceedings where meeting_num=$meeting_num");

  system "rm -Rf $web_dir/$dir_name/$deleted_file" if db_update($dbh,$sqlStr);
  $q->param('message'=>"File Deletion was successful:$web_dir/$dir_name/$deleted_file");
  return upload_slide_minute($q);
}
