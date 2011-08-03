#!/usr/bin/perl -w
##########################################################################
#      Copyright © 2004 Foretec Seminars, Inc.
#
#      Program: wg_portal.cgi
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

my $q = new CGI;
error ($q,"This page is currently unavailable. <br>If you need further assistance, please send an email to <a href=\"mailto:ietf-action\@ietf.org\">ietf-action\@ietf.org</a>.<br>Thank you.");
$rUser=$ENV{REMOTE_USER};
$loginid=db_select("select person_or_org_tag from wg_password where login_name = '$rUser'");
error ($q,"This page is currently available to IETF Working Group chairs only.<br>If you need further assistance, please send an email to <a href=\"mailto:ietf-action\@ietf.org\">ietf-action\@ietf.org</a>.<br>Thank you.") unless $loginid;
$wg_chair_name=get_name($loginid);
$style_url="https://www1.ietf.org/css/base.css";
$program_name = "password_manager.cgi";
$program_title = "IETF Working Group Chair Password Manager";
$program_title .= " db: $dbname" if ($devel_mode);
$table_header = qq{<table cellpadding="1" cellspacing="1" border="0">
};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">};
$form_header_post2 = qq{<form action="$program_name" method="POST" name="form_post2">};
$form_header_post3 = qq{<form action="$program_name" method="POST" name="form_post3">};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">};
$form_header_get = qq{<form action="$program_name" method="GET" name="form_get">};
$html_top = qq|
<link rel="stylesheet" type="text/css" href="$style_url" />
<h2><center>$program_title <i>$mode_text</i></center></h2>
Hi $wg_chair_name 
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
   <input type="submit" value="First Screen">
   </form>
   } if (my_defined($command) and $command ne "main_screen");
   return $html_txt;
}

sub main_screen {
  my $login_name=db_select("select login_name from wg_password where person_or_org_tag=$loginid");
  return qq{
$form_header_post
<input type="hidden" name="command" value="reset_password">
$table_header
<tr><td>Enter Login Name: </td><td><input type="text" name="login_name" value="$login_name" size="25"></td></tr>
<tr><td>Enter old password: </td><td><input type="password" name="old_password" size="25"></td></tr>
<tr><td>Enter new password: </td><td><input type="password" name="new_password1" size="25"></td></tr>
<tr><td>Re-Enter new password: &nbsp; &nbsp; </td><td><input type="password" name="new_password2" size="25"></td></tr>
</table>
<br><br>
<input type="submit" value="Submit">
</form>
<br>
<hr>
<h2>Links</h2>
<ul>
<li> <a href="wg_proceedings.cgi">Meeting Materials Management Tool</a></li>
</ul>
<br><br><br>
};
}

sub reset_password {
  my $q=shift;
  my $login_name=$q->param("login_name");
  my $old_password=$q->param("old_password");
  my $new_password1=$q->param("new_password1");
  my $new_password2=$q->param("new_password2");
  my $db_password=db_select("select password from wg_password where person_or_org_tag=$loginid");
  error ($q,"Old password does not match your current password. <br>Please try again.") unless ($old_password eq $db_password);
  error($q,"Two new passwords are not the same.<br>Please try again.") unless ($new_password1 eq $new_password2);
  error ($q,"Blank Login Name.<br>Please try again.") unless my_defined($login_name);
  error ($q,"Blank password.<br>Please try again.") unless my_defined($new_password1);
  my $new_password = db_quote($new_password1);
  $login_name=db_quote($login_name);
  my $exist=db_select("select count(*) from wg_password where login_name=$login_name and person_or_org_tag <> $loginid");
  error ($q,"Existing Login Name.<br>Please try another login name.") if ($exist);
  db_update("update wg_password set login_name=$login_name, password=$new_password where person_or_org_tag=$loginid");
  return qq{
Password will be updated in 15 minutes<br>
Please use the new password for future login
};
}

