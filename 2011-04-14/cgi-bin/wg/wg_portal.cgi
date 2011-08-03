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
$rUser=$ENV{REMOTE_USER};
$loginid=db_select("select person_or_org_tag from email_addresses where email_address like '%$rUser'");
$wg_chair_name=get_name($loginid);
$style_url="http://www.ietf.org/css/base.css";
$program_name = "wg_portal.cgi";
$program_title = "IETF Working Group Chairs Portal Page";
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
   <input type="submit" value="Main Menu">
   <input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true">
   </form>
   } if (my_defined($command) and $command ne "main_screen");
   return $html_txt;
}

sub main_screen {
  return qq{
<!--<li> Change My Password <font size-=1 color="red"><i>Under construction</i></font></li><br>-->
<li> <a href="wg_proceedings.cgi">Upload Proceeding Materials</a></li><Br>
<!--<li> Change My Profile <font size-=1 color="red"><i>Under construction</i></font></li><br>
<li> List of I-Ds to be approved <font size-=1 color="red"><i>Under construction</i></font></li>--><br>
};
}

sub set_auth {
  return qq{
$form_header_post
<input type="hidden" name="command" value="reset_password">
$table_header
<tr><td>Enter old password: </td><td><input type="password" name="old_password" size="25"></td></tr>
<tr><td>Enter new password: </td><td><input type="password" name="new_password1" size="25"></td></tr>
<tr><td>Re-Enter new password: &nbsp; &nbsp; </td><td><input type="password" name="new_password2" size="25"></td></tr>
</table>
<br><br>
<input type="submit" value="Submit">
</form>
<br><br>
};
}

sub reset_password {
  my $q=shift;
  my $old_password=$q->param("old_password");
  my $new_password1=$q->param("new_password1");
  my $new_password2=$q->param("new_password2");
  my $old_password_crypted=crypt($old_password,"dd");
  my $db_password=db_select("select password from wg_password where person_or_org_tag=$loginid");
  unless ($old_password_crypted eq $db_password) {
    return qq{Old password does not match - $loginid, -$old_password_crypted-, -$db_password-<br>
Please try again};
  }
  unless ($new_password1 eq $new_password2) {
    return qq{Two new passwords are not same<br>
Please try again};
  }
  my $new_password = db_quote(crypt($new_password1,"dd"));
  db_update("update wg_password set password=$new_password where person_or_org_tag=$loginid");
  return qq{
Password will be updated in 15 minutes<br>
Please use the new password for the future login
};
}

