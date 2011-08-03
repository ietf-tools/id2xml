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
$program_name = "staff_manager.cgi";
$program_title = "IETF Secretariat Staff Manager";
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
  my $current_list_html = "$table_header";
  my @List = db_select_multiple("select person_or_org_tag,title from secretariat_staff");
  for my $array_ref (@List) {
    my ($person_or_org_tag,$title) = @$array_ref;
    my $name = get_name($person_or_org_tag);
    $current_list_html .= qq{
<tr><td>
$form_header_post
<input type="hidden" name="command" value="edit_title">
<input type="hidden" name="person_or_org_tag" value="$person_or_org_tag">
<input type="text" name="title" value="$title" size="50"> &nbsp; &nbsp; <b>$name</b> &nbsp; &nbsp; </td>
<td><input type="submit" value=" Edit Title "></form></td>
$form_header_post2
<input type="hidden" name="command" value="delete_staff">
<input type="hidden" name="person_or_org_tag" value="$person_or_org_tag">
<td><input type="submit" value=" Delete Staff "></form>
</td>
</tr>
};
  }
  $current_list_html .= "</table>\n";
  return qq{
<h2>Edit Current Staff</h2>
$current_list_html
<hr width="300" align="left">
<h2>Add New Staff</h2>
$form_header_post
<input type="hidden" name="command" value="add_new_staff">
<b>Enter Name (First Name, Last Name) : </b>
<input type="text" name="first_name" size="35"> &nbsp; &nbsp; 
<input type="text" name="last_name" size="35"> 
<input type="submit" value=" Next Step "><br>
</form>
};
}
sub delete_staff {
  my $q=shift;
  my $person_or_org_tag = $q->param("person_or_org_tag");
  db_update("delete from secretariat_staff where person_or_org_tag=$person_or_org_tag");
  return main_screen();
}
sub edit_title {
  my $q=shift;
  my $title=db_quote($q->param("title"));
  my $person_or_org_tag=$q->param("person_or_org_tag");
  db_update("update secretariat_staff set title=$title where person_or_org_tag=$person_or_org_tag");
  return main_screen();
}

sub add_new_staff {
  my $q=shift;
  my $first_name=$q->param("first_name");
  my $last_name=$q->param("last_name");
  $first_name =db_quote("$first_name%");
  $last_name =db_quote("$last_name%");
  my @List = db_select_multiple("select person_or_org_tag from person_or_org_info where first_name like $first_name and last_name like $last_name");
  if ($#List < 0) {
    return qq{<h2>Such a person cannot be found from the IETF Rolodex database</h2>
<h3>Please use <a href="rolodex.cgi">IETF Rolodex</a> to add the person's information first and try again.</h3>
<br><br>
};
  }
  my $html_txt = qq{<h3>Please select a person from the list below</h3>
$form_header_post
<input type="hidden" name="command" value="add_new_staff2">
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

sub add_new_staff2 {
  my $q=shift;
  my $person_or_org_tag=$q->param("person_or_org_tag");
  my $name=get_name($person_or_org_tag);
  return qq{
<h3>Please enter title for $name</h3>
$form_header_post
<input type="hidden" name="command" value="confirm_add">
<input type="hidden" name="person_or_org_tag" value="$person_or_org_tag">
<input type="text" name="title" size="75"><br>
<input type="submit" value=" Next Step "><br>
</form>
};
}

sub confirm_add {
  my $q=shift;
  my $person_or_org_tag=$q->param("person_or_org_tag");
  my $title=$q->param("title");
  my $name=get_name($person_or_org_tag);
  my $email=get_email($person_or_org_tag);
  return qq{
<h3>Please confirm the following information</h3>
<b>
Name: $name<br>
Email: $email<br>
Title: $title<br><br>
$form_header_post
<input type="hidden" name="command" value="do_add_new_staff">
<input type="hidden" name="person_or_org_tag" value="$person_or_org_tag">
<input type="hidden" name="title" value="$title">
<input type="submit" value=" Add New Staff "><br>
</form>
};
}

sub do_add_new_staff {
  my $q=shift;
  my $person_or_org_tag=$q->param("person_or_org_tag");
  my $title=db_quote($q->param("title"));
  db_update("insert into secretariat_staff (person_or_org_tag,title) values ($person_or_org_tag,$title)");
  return main_screen();
}

