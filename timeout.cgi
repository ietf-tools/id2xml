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
use CGI_UTIL;

$script_loc=$ENV{SCRIPT_NAME};
$http_host=$ENV{HTTP_HOST};
$devel_mode = ($script_loc =~ /devel/)?1:0;
$qa_mode = 0;
$dbname = "ietf";
$query = new CGI;

if ($devel_mode) {
  $qa_mode = ($http_host =~ /datatracker/)?1:0;
  $rUser = $ENV{REMOTE_USER};
  $dbname=($qa_mode)?"ietf_qa":"test_idst";
  $title_text = ($qa_mode)?"QA Mode":"Development Mode";
}
init_database($dbname);
$dbh = get_dbh();

my $q = new CGI;
$style_url="https://www1.ietf.org/css/base.css";
$program_title = "Internet-Draft Submission Tool session was timed out";
$program_title .= " db: $dbname" if ($devel_mode);
$table_header = qq{<table cellpadding="1" cellspacing="1" border="0">
};
$table_header2 = qq{<table cellpadding="1" cellspacing="1" border="0" width="800">
};
$sql_injection_warning="Possible SQL Injection detected.";
$html_body = get_html_body($q);
print $q->header("text/html"),
      $q->start_html(-title=>$program_title),
      $q->p($html_body),
      $q->end_html;

$dbh->disconnect();
exit;

sub get_html_body {
   my $q = shift;
   my $command = $q->param("command");
   error_idst ($q,$sql_injection_warning) if check_sql_injection ($command);
   my $html_txt = "";
   unless (my_defined($command)) {
     $html_txt .= main_screen($q);
   } else {
     my $func = "$command(\$q)";
     $html_txt .= eval($func);
   }
   return $html_txt;
}

sub main_screen {
  my $q=shift;
  my $submission_id=$q->param("submission_id");
  error_idst ($q,$sql_injection_warning) if check_sql_injection ($submission_id);
  my ($max_interval,$staging_path) = db_select($dbh,"select max_interval,staging_path from id_submission_env");
  my ($filename,$revision)=db_select($dbh,"select filename,revision from id_submission_detail where submission_id=$submission_id");
  unlink $_ while (<$staging_path/$filename-$revision.*>);
  db_update($dbh,"update id_submission_detail set status_id=-4 where submission_id=$submission_id");
  return qq{Your I-D submission session was timed out after $max_interval minutes of idle time, and the draft that you were trying to submit has been deleted from the staging area.<br>
Please go back to <a href="upload.cgi">Upload Page</a> and re-submit your draft.<br>

}; 

}
