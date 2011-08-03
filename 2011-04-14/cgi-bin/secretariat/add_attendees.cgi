#!/usr/bin/perl
##########################################################################
#      Copyright (c) 2006 Neustar Secretariat Services, Inc.
#
#      Program: 
#      Author : Michael Lee, Neustar Secretariat Services
#      Last Modified Date: 12/1/2006
#
#      This Web application provides ... 
#
#####################################################
use lib '/a/www/ietf-datatracker/release';
use GEN_DBUTIL_NEW;
use GEN_UTIL;
use IETF;
use CGI;
#use CGI qw(':standard');
use CGI_UTIL;

use constant MAX_FILE_SIZE => 8_388_608;
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
  $dbname="idst_test";
  $mode_text = "Test Mode";
}
$dbname="ietf";
init_database($dbname);
$dbh=get_dbh();
$host = $ENV{SERVER_NAME};
my $q = new CGI;
error($q,"No Meeting Number found") unless defined($q->param("meeting_num"));
$meeting_num=$q->param("meeting_num");

$style_url="https://www1.ietf.org/css/base.css";
$program_name = "add_attendees.cgi";
$program_title = "IETF $meeting_num Meeting Attendees Upload";
$program_title .= " db: $dbname" if ($devel_mode);
$table_header = qq{<table cellpadding="1" cellspacing="1" border="0">
};
$table_header2 = qq{<table cellpadding="1" cellspacing="1" border="0" width="800">
};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post" enctype="multipart/form-date">};
$form_header_post2 = qq{<form action="$program_name" method="POST" name="form_post2">};
$form_header_post3 = qq{<form action="$program_name" method="POST" name="form_post3">};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">};
$form_header_get = qq{<form action="$program_name" method="GET">};
$form_header_noname = qq{<form action="$program_name" method="GET">
};
$bc="{";
$ec="}";
$color1="#cccccc";
$color2="#eeeeee";
$rUser=$ENV{REMOTE_USER};
$html_top = qq|
<link rel="stylesheet" type="text/css" href="$style_url" />
<blockquote>
<h2><center>$program_title <font color="red"><i>$mode_text</i></font></center></h2>
<i>$rUser</i> logged on
<hr>

|;
$html_bottom = qq{
<hr>
<li>If you require assistance in using this tool, or wish to report a bug, then please send a message to <a href="mailto:ietf-action\@ietf.org">ietf-action\@ietf.org</a>.</li>

</blockquote>
};

$asterisk = "<font color=\"red\"><b>*</b></font>";
$html_body = get_html_body($q);
print $q->header("text/html"),
      $q->start_html(-title=>$program_title),
      $q->p($html_top),
      $q->p($html_body),
      $q->p($html_bottom),
      $q->end_html;

$dbh->disconnect();
exit;

sub get_html_body {
   my $q = shift;
   my $command = $q->param("command");
   my $html_txt = "";
   unless (my_defined($command)) {
     $html_txt .= main_screen($q);
   } else {
     my $func = "$command(\$q)";
     $html_txt .= eval($func);
   }
   $html_txt .= qq{
$form_header_bottom
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="submit" value=" User's First Screen ">
</form>
} if (my_defined($command));
   return $html_txt;
}

sub main_screen {
  $test_text = CGI::escapeHTML("<please ignore this tag> ");
  my $ct=db_select($dbh,"select count(*) from meeting_attendees where meeting_num=$meeting_num");
  return qq{
Meeting attendees for IETF $meeting_num have already been uploaded once.<br>
Please click the button below to delete existing records and re-upload them.<br>
$form_header_noname
<input type="hidden" name="command" value="delete_all">
<input type="hidden" name="meeting_num" value="$meeting_num">
<input type="submit" value="Delete all IETF $meeting_num attendees" onClick="return window.confirm('Are you sure');">

</form>
} if $ct;
  return qq{$test_text 
$form_header_post
<input type="hidden" name="command" value="process_file">
<input type="hidden" name="meeting_num" value="$meeting_num">
<b>Instruction:</b>
<ol>
<li> Open filemaker file for IETF $meeting_num as a root.</li>
<li> Go to Main DB window.</li>
<li> Click "Find" button.</li>
<li> Enter " > 1/1/2007" in Arrival Date field and hit ENTER.</li>
<li> Go to 'File' menu and select 'Export Report'. </li>
<li> Save the file as i$meeting_num.txt in your desktop.</li>
<li> Select "Firstname", "Lastname", "Email Address", and "Company" in that order.</li>
<li> Click 'Export'.</li>
<li> Find the file: <input type="file" name="list_file"></li>
<li> Click 'Upload' Button below.</li>
</ol>
<input type="submit" value="Upload"><br>
</form>

};
}

sub process_file {
  my $q=shift;
  my $file = $q->param("list_file")  || error ($q,"No file received.");
  my $fh=$q->upload("list_file",-override=>1);
  error ($q,"Invalid file, $file, $fh") unless ($fh);
  my $ran_file_name=generate_random_string(5);
  error($q,"Could not upload file") unless fileuploader($fh,"/tmp/$ran_file_name");
  system "/a/www/ietf-datatracker/release/add_attendees.pl $meeting_num < /tmp/$ran_file_name";
  unlink "/tmp/$ran_file_name";
  return qq{
Upload was successful: $ran_file_name
};  
}

sub delete_all {
  my $q=shift;
  db_update($dbh,"delete from meeting_attendees where meeting_num=$meeting_num");
  return main_screen();
}

