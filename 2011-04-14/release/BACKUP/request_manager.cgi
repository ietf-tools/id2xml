#!/usr/local/bin/perl -w

use lib '/export/home/mlee/RELEASE/';
use CGI;
use IETF_UTIL;
use IETF_DBUTIL;

my $cwd = `pwd`;
my $warnning_msg = "";
chomp($cwd);
$_ = $cwd;
$devel = "";
if (/devel/) {
   $ENV{"DBPATH"} = "/export/home/mlee/database";
   $ENV{"DBNAME"} = "testdb";
   $devel = "devel/";
} else {
   $ENV{"DBPATH"} = "/usr/informix/databases";
   $ENV{"DBNAME"} = "people";
}
if (defined($ENV{HTTP_USER_AGENT})) {
   my $user_agent = $ENV{HTTP_USER_AGENT};
   @version_temp = split ' ',$user_agent;
   $browser_version = $version_temp[0];
} else {
   $browser_version = "Unknown Version";
}
my $q = new CGI;
$program_name = "request_manager.cgi";
########## End Pre Populate Option lists ###################
$table_header = qq{<table cellpadding="1" cellspacing="0" border="1">
};
$form_header = qq{<form action="$program_name" method="POST" name="form1">
};
$html_top = qq{
<html>
<HEAD><TITLE>IESTG ID Tracker version control-- $browser_version</title>
<STYLE TYPE="text/css">
<!--

	  TD {text-decoration: none; color: #000000; font: 11pt arial;} 
	  A:Link {color: #0000ff; text-decoration:underline}
	  A:Hover {color: #ff0000; text-decoration:underline}
      A:visited {color: #0000ff; text-decoration:underline}
	  #largefont {font-weight: bold; color: #000000; font: 16pt arial}
	  #largefont_red {font-weight: bold; color: #ff0000; font: 16pt arial}
-->
</STYLE>

</head>
<body link="blue" vlink="blue">
$warnning_msg
};
$html_bottom = qq{
</body>
</html>
};

$html_body = get_html_body($q);

print <<END_HTML;
Content-type: text/html
$html_top
$html_body
$html_bottom
END_HTML




sub get_html_body {
   my $q = shift;
   my $html_txt;
   my $command = $q->param("command");
   unless (my_defined($command)) {
      $html_txt = main_screen();
   } else {
      my $func = "${command}(\$q)";
	  $html_txt = eval($func);
   }
   return $html_txt;
}

sub main_screen {
   my $html_txt = qq {
   <h2>IESG DraftTracker Version Control and Request Status</h2>
   <h3>Requests</h3>
   $form_header
   <input type="hidden" name="command" value="add">
   <input type="submit" value="Add Request">
   </form>
   $table_header
   <tr>
   <th>Description</th><th>Requested By</th><th>Request Date</th><th>Current Version</th><th>Status</th><th></th>
   </tr>
   };
   my @List = db_select_multiple("select a.id,a.desc,b.first_name,b.last_name,a.request_date,a.cur_version,a.status,a.done_flag from dt_request a,iesg_login b where a.request_by = b.id order by a.done_flag,a.request_date DESC");
   for $array_ref (@List) {
      my ($id,$desc,$request_by_f,$request_by_l,$request_date,$cur_version,$status,$done_flag) = @$array_ref;
	  $desc = rm_tr($desc);
	  $status = rm_tr($status);
	  $request_by_f = rm_tr($request_by_f);
	  $request_by_l = rm_tr($request_by_l);
	  $html_txt .= qq {
	  $form_header
	  <input type="hidden" name="command" value="update">
	  <input type="hidden" name="req_id" value="$id">
	  <tr>
	  <td>$desc</td><td>$request_by_f $request_by_l</td><td>$request_date</td><td>$cur_version</td><td>$status</td>
	  <td>
	  <input type="submit" value="UPDATE">
	  </td>
	  </tr>
	  </form>
	  };
   }

   $html_txt .= qq {
   </table>
   <p>
   };
   return $html_txt;
}

sub add {
   my $q = shift;
   my @List = db_select_multiple("select id,first_name,last_name from iesg_login where user_level < 2 order by first_name");
   my $option_str = "";
   for $array_ref (@List) {
      my ($id,$fName,$lName) = @$array_ref;
	  $fName = rm_tr($fName);
	  $lName = rm_tr($lName);
	  $option_str .= qq {<option value="$id">$fName $lName</option>
	  };
   }
   my $html_txt = qq {
   $form_header
   <input type="hidden" name="command" value="add_db">
   $table_header
   <tr>
   <td>Description: </td><td><textarea cols="50" rows="4" wrap="virtual" name="desc"></textarea></td>
   </tr>
   <tr>
   <td>Request By: </td><td><select name="request_by">$option_str</select></td>
   </tr>
   <tr>
   <td>Current Version: </td><td><input type="text" name="cur_version" size="5"></td>
   </tr>
   <tr>
   <td>Status: </td><td><textarea name="status" cols="50" rows="5" wrap="virtual"></textarea></td>
   </tr>
   </table>
   <input type="submit" value="Submit">
   </form>
   };
   return $html_txt;
}

sub add_db {
   my $q = shift;
   my $desc = format_textarea($q->param("desc"));
   my $request_by = $q->param("request_by");
   my $status = format_textarea($q->param("status"));
   my $cur_version = $q->param("cur_version");
   ($desc,$status,$cur_version) = db_quote($desc,$status,$cur_version);
   my $sqlStr = qq {
   insert into dt_request (desc,request_by,cur_version,request_date,status,done_flag)
   values ($desc,$request_by,$cur_version,TODAY,$status,0)
   };
   unless (db_update($sqlStr)) {
      return "<h2>FATAL ERROR raised while adding a new record</h2><br>SQL = $sqlStr";
   }
   
   return main_screen();
}

sub update {
   my $q = shift;
   my $id = $q->param("req_id");

   my ($desc,$request_by,$cur_version,$status,$request_date,$done_flag) = db_select("select desc,request_by,cur_version,status,request_date,done_flag from dt_request where id=$id");
   $desc = rm_tr($desc);
   $cur_version = rm_tr($cur_version);
   $status = rm_tr($status);

   my @List = db_select_multiple("select id,first_name,last_name from iesg_login where user_level < 2 order by first_name");
   my $option_str = "";
   for $array_ref (@List) {
      my ($sid,$fName,$lName) = @$array_ref;
	  my $selected = "";
	  $fName = rm_tr($fName);
	  $lName = rm_tr($lName);
	  if ($sid == $request_by) {
	     $selected = "selected";
	  }
	  $option_str .= qq {<option value="$sid" ${selected}>$fName $lName</option>
	  };
   }
   my $checked = "";
   $checked = "checked" if ($done_flag);
   my $html_txt = qq {
   $form_header
   <input type="hidden" name="command" value="update_db">
   <input type="hidden" name="req_id" value="$id">
   $table_header
   <tr>
   <td>Description: </td><td><textarea cols="50" rows="4" wrap="virtual" name="desc">$desc</textarea></td>
   </tr>
   <tr>
   <td>Request By: </td><td><select name="request_by">$option_str</select></td>
   </tr>
   <tr>
   <td>Current Version: </td><td><input type="text" name="cur_version" size="5" value="$cur_version"></td>
   </tr>
   <tr>
   <td>Status: </td><td><textarea name="status" cols="50" rows="5" wrap="virtual">$status</textarea></td>
   </tr>
   <tr>
   <td>Request Date: </td><td><input type="text" name="request_date" size="15" value="$request_date"></td>
   </tr>
   <tr>
   <td>Done? : </td><td><input type="checkbox" name="done_flag" value="$done_flag" $checked></td>
   </tr>
   </table>
   <input type="submit" value="Submit">
   </form>
   };
   return $html_txt;
}


sub update_db {
   my $q = shift;
   my $id = $q->param("req_id");
   my $desc = format_textarea($q->param("desc"));
   my $request_by = $q->param("request_by");
   my $request_date = $q->param("request_date");
   my $status = format_textarea($q->param("status"));
   my $cur_version = $q->param("cur_version");
   my $done_flag = $q->param("done_flag");
   unless (my_defined($done_flag)) {
      $done_flag = 0;
   } else {
      $done_flag = 1;
   }
   ($desc,$status,$cur_version,$request_date) = db_quote($desc,$status,$cur_version,$request_date);
   my $sqlStr = qq {
   update dt_request
   set desc = $desc,
       request_by = $request_by,
	   cur_version = $cur_version,
	   request_date = $request_date,
	   status = $status,
	   done_flag = $done_flag
   where id = $id
   };
   unless (db_update($sqlStr)) {
      return "<h2>FATAL ERROR raised while adding a new record</h2><br>SQL = $sqlStr";
   }
   
   return main_screen();
}

