#!/usr/bin/perl
##########################################################################
#      Copyright © 2004, Foretec Seminars, Inc.
#
#      Program: id_date.cgi
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
$program_name = "id_date.cgi";
$program_title = "Internet-Draft Submission Dates";
$table_header = qq{<table cellpadding="0" cellspacing="0" border="0">
};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">};
$form_header_get = qq{<form action="$program_name" method="GET" name="form_get">};
$html_top = qq|
<html>
<HEAD><TITLE>$program_title</title>
</head>
<body>
<center><h2>$program_title</h2></center>
<br><br>
|;
$html_bottom = qq{
</body>
</html>
};
@List = db_select_multiple ("select id,f_name,date_name,id_date from id_dates");
$html_body = get_html_body($q);
print <<END_HTML;
Content-type: text/html
$html_top
$html_body
$html_bottom
END_HTML

sub get_html_body {
   my $q = shift;
   my $command = $q->param("command");
   my $html_txt;
   unless (my_defined($command)) {
     $html_txt .= main_menu();
   } else {
     my $func = "$command(\$q)";
     $html_txt .= eval($func);
   }
   return $html_txt;

}

sub main_menu {
  my $table_contents = "";
  for my $array_ref (@List) {
    my ($id,$f_name,$date_name,$id_date) = @$array_ref;
    $table_contents .= qq{<tr><td> <font size=+1>$date_name &nbsp; &nbsp; </font></td><td><input type="text" name="$f_name" value="$id_date"></td></tr>
};
  }
  my @meetingList=db_select_multiple("select meeting_num from meetings order by meeting_num desc");
  my $meeting_list = "";
  for my $array_ref (@meetingList) {
    my ($meeting_num) = @$array_ref;
    $meeting_list .= "<option value=\"$meeting_num\">IETF $meeting_num</option>\n";
  }
return qq{
<P>
$form_header_post
<input type="hidden" name="command" value="update_confirm">
$table_header
$table_contents

</table>
<p>
<input type="submit" value="Submit">
</form>
<br>
$form_header_post
<input type="hidden" name="command" value="update_confirm">
<input type="hidden" name="reset_dates" value="yes">
<h3>Reset the dates for following meeting</h3>
<select name="meeting_num">
<option value="0">--Select Meeting--</option>
$meeting_list
</select> &nbsp; &nbsp; &nbsp; 
<input type="submit" value="Submit">
</form>
};
}

sub update_confirm {
  my $q=shift;
  my $first_date = $q->param("first");
  my $second_date = $q->param("second");
  my $third_date = $q->param("third");
  my $fourth_date = $q->param("fourth");
  my $fifth_date = $q->param("fifth");
  my $sixth_date = $q->param("sixth");
  if (defined($q->param("reset_dates"))) {
    my $meeting_num = $q->param("meeting_num");
    my $start_date = db_select("select start_date from meetings where meeting_num=$meeting_num");
    $first_date = get_offset_date($start_date,"-",20,"day");
    $second_date = get_offset_date($start_date,"-",13,"day");
    $third_date = get_offset_date($start_date,"+",1,"day");
    $fourth_date = get_offset_date($start_date,"-",10,"day");
    $fifth_date = get_offset_date($start_date,"+",8,"day");
    $sixth_date = get_offset_date($start_date,"-",27,"day");
  }
  my $table_contents = "";
  my $hidden_list = "";
  for my $array_ref (@List) {
    my ($id,$f_name,$date_name,$id_date) = @$array_ref;
    eval("\$set_date = \$${f_name}_date");
    $hidden_list .= qq{<input type="hidden" name="$f_name" value="$set_date">
};
    $table_contents .= qq{<tr><td> <font size=+1>$date_name &nbsp; &nbsp; </font></td><td>
$set_date</td></tr>
};
  }

  return qq{
<h2>Confirmation</h2>
$form_header_post
<input type="hidden" name="command" value="update_dates">
$hidden_list
$table_header
$table_contents
</table>
<br><br>
<input type="submit" value="  All the dates are correct. Do update!  ">
</form>
<br><br><br><br>
  };
}

sub update_dates {
  my $q=shift;
  for my $array_ref (@List) {
    my ($id,$f_name,$date_name,$id_date) = @$array_ref;
    eval("\$set_date = \$q->param(\"$f_name\")");
    db_update("update id_dates set id_date='$set_date' where id=$id");
  }
  return "<h2>Dates were updated successfully</h2><a href=\"id_date.cgi\">First Screen</a><br>\n";
}

