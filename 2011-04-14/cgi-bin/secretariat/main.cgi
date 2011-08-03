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
$program_name = "main.cgi";
$program_title = "IETF Secretariat Portal";
$table_header = qq{<table cellpadding="5" cellspacing="5" border="0" width="800">
};
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
  my $meeting_list = "";
  my @List=db_select_multiple("select meeting_num from meetings order by meeting_num");
  for my $array_ref (@List) {
    my ($meeting_num) = @$array_ref;
    $meeting_list .= "<option value=\"$meeting_num\">$meeting_num</option>\n";
  }
  return qq{
<h2><a href="http://www.ietf.org/">IETF Home Page</a></h2>
<h2>Tool List</h2>
$table_header
<tr valign="top"><td>
<h3>IETF General Information</h3>
<li> <a href="iesg_chairs.cgi"><b>IESG and Other Chairs and Officers Manager</b></a></li><br>
<li> <a href="staff_manager.cgi"><b>Secretariat Staff Manager</b></a></li><br>
<li> <a href="nomcom.cgi"><b>NOMCOM Members and Web Page Contents Manager</b></a></li><br>
<li> <a href="general_manager.cgi"><b>IETF Miscellaneous Information Manager</b></a></li><br>
</td>
<td>
<h3>I-Ds and WGs Process</h3>
<li> <a href="https://datatracker.ietf.org/cgi-bin/idtracker.cgi"><b>IESG ID Tracker</b></a></li><br>
<li> <a href="http://cf.amsl.com/"><b>Secretariat Internal Database Interface (ColdFusion)</b></a></li><br>
<li> <a href="/cgi-bin/secretariat/idnits.cgi"><b>I-D Validator <font color="red">UPDATED</font> (use this version from May 9, 2005)</b></a></li><br>
<li> <a href="rolodex.cgi"><b>IETF Rolodex</b></a></li><br>
<li> <a href="init_rev_approval.cgi"><b>Initial Version Approver</b></a></li><br>
</td></tr>
<tr valign="top"><td>
<h3>Meeting, Agenda, and Proceedings</h3>
<li> <a href="meeting_manager.cgi"><b>Meeting Manager</b></a></li><br>
<li> <a href="proceeding_manager.cgi"><b>Proceeding Manager</b></a></li><br>
<li> <a href="blue_sheet.cgi"><b>Blue Sheets Creator</b></a></li><br>
<li> <a href="blue_dot_report.cgi"><b>WG Chairs List</b></a></li><br>
<li> <a href="id_date.cgi"><b>NEW! Set Draft Cutoff Dates</b></a></li><br>
</td>
<td>
<h3>IPR</h3>
<li> <a href="/cgi-bin/ipr_admin/ipr_admin.cgi"><b>IPR Administrator Page</b></a></li><br>
<li> <a href="/cgi-bin/ipr_admin/ipr_internal.cgi"><b>IPR Email Submission Entry Page</b></a></li><br>
<li> <a href="https://datatracker.ietf.org/public/ipr_disclosure.cgi"><b>IPR Disclosure Page</b></a></li><br>
<li> <a href="https://datatracker.ietf.org/public/ipr_list.cgi"><b>IPR List Page</b></a></li><br>
</td></tr>
<tr valign="top"><td>
<h3>Liaisons</h3>
<li> <a href="/cgi-bin/liaison_interim.cgi"><b>Liaison Manager (interim)</b></a></li><br>
</td><td>
<h3>Telechat</h3>
<li> <a href="itelechat.cgi"><b>Telechat Manager</b></a></li><br>
<li> <a href="add_telechat_minute.cgi"><b>Add Minute</b></a></li><br>
<li> <a href="edit_telechat_minute.cgi"><b>Edit Old Minutes</b></a></li><br>
</td>
</tr>
<tr valign="top"><td>
<h3>Community Tool</h3>
<li> <a href="https://datatracker.ietf.org/"><b>Public ID Tracker</b></a></li><br>
<li> <a href="https://datatracker.ietf.org/public/idindex.cgi"><b>Internet-Drafts Database Interface</b></a></li><br>
<li> <a href="https://datatracker.ietf.org/public/request_list.cgi"><b>Mailing List Request Tool</b></a></li><br>
<li> <a href="https://datatracker.ietf.org/public/nwg_list_submit.cgi"><b>Non WG Mailing List Submission Page</b></a></li><br>
</td><td>
<h3>Other Tools</h3>
<li> <a href="/cgi-bin/ietf_announcement.cgi"><b>IETF Announcement</b></a></li><br>
<li> <a href="https://rt.amsl.com/"><b>IETF Tickets</b></a></li><br>
<li> <a href="message_scheduler.cgi"><b>Message Scheduler</b></a></li><br>
<li> <a href="staff_sched.cgi"><b>Developers Schedules</b></a></li><br>
</td>
</tr>
</table>
<br><br><br><br>
<br><br><br><br>
};
}

