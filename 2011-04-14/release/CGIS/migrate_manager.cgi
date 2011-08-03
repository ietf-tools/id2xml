#!/usr/local/bin/perl -w

use lib '/export/home/mlee/RELEASE/';
use CGI;
use IETF_UTIL;
use IETF_DBUTIL;

   $TESTDB = 0;
   $INFORMIX = 1;
   $MYSQL = 2;
my ($db_mode,$CURRENT_DATE,$CONVERT_SEED,$is_null) = init_database($MYSQL);
my $q = new CGI;
@groups = ("CGI SCRIPTS", "CRON SCRIPTS", "MODULE", "COMMAND LINE UTILITY");
$program_name = "migrate_manager.cgi";
########## End Pre Populate Option lists ###################
$table_header = qq{<table cellpadding="1" cellspacing="0" border="1">
};
$form_header = qq{<form action="$program_name" method="POST" name="form1">
};
$html_top = qq{
<html>
<HEAD><TITLE>Migrate Status Manager</title>
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
<h2>Migrate Status Manager</h2>
<font color="800000"><h3>Check Item</h3></font>
1. Change <b>DB_MODE</b> to <b>MYSQL</b> by calling <b>init_database(\$MYSQL)</b><br>
2. Rewrite <b>Outer Join</b> SQL statement<br>
3. Replace <b>IS NULL</b> with <b>= ''</b> within SQL<br>
4. Replace <b>IS NOT NULL</b> with <b>&lt;&gt; ''</b> within SQL<br>
5. Replace <b>TODAY</b> with <b>CURRENT_DATE</b> within SQL<br>
6. Rewrite <b>SUB SELECT</b> SQL statement<br>
7. Use Date format of <b>YYYY-MM-DD</b><br>
<font color="800000"><h3>Test Item</h3></font>
1. run <b>diff</b> unix command on a file created by old script and a file created by a new script, and there should be no difference on contents<br>
2. udpate the test database using a old script and update MySQL database using a new script, and the result should be matched<br>
<hr>
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
   $form_header
   <input type="hidden" name="command" value="add">
   <input type="submit" value="Add Item">
   </form>
   $table_header
   <tr>
   <th>New Script</th><th>Old Script</th><th>Needs to be done</th><th>How to test</th><th>Status</th><th></th>
   </tr>
   };
   my @List = db_select_multiple("select done_flag,id,new_script,old_script,need_done,how_to_test,status,group_id from migrate_stat order by group_id,done_flag");
   
   for $array_ref (@List) {
      my ($done_flag,$id,$new_script,$old_script,$need_done,$how_to_test,$status,$group_id) = rm_tr(@$array_ref);
	  $html_txt .= qq {
	  $form_header
	  <input type="hidden" name="command" value="update">
	  <input type="hidden" name="req_id" value="$id">
	  <tr>
	  <td>$new_script</td><td>$old_script</td><td>$need_done</td><td>$how_to_test</td><td>$status</td><td><input type="submit"  value="EDIT"></td>
	  </tr>
	  </form>
	  };
   }


   $html_txt .= qq {
   </table>
   <p>
   <p><p>
   <script language="javascript">
   function doSub() {
   document.form2.command.value = document.form0.command.value;
   document.form2.submit();
   return true;
   }
   </script>
   <form name="form0" onSubmit="return false;">
Command:   <input type="text" name="command">
   </form>
   <form name="form2" action="migrate_manager.cgi" method="post" onSubmit="doSub(); return false;">
   <input type="hidden" name="command" value="">
   
   ID: <input type="text" name="req_id" >
   <br>
   <input type="submit">
   </form>
   };
   return $html_txt;
}

sub add {
   my $q = shift;
   my $option_str = "";
   my $ind = 0;
   for $array_ref (@groups) {
      my $value = $array_ref;
	  $option_str .= qq {<option value="$ind">$value</option>
	  };
	  $ind++;
   }
   my $html_txt = qq {
   $form_header
   <input type="hidden" name="command" value="add_db">
   $table_header
   <tr>
   <td>Group ID: </td><td><select name="group_id">$option_str</select></td>
   </tr>
   <tr>
   <td>New Script: </td><td><input type="text" name="new_script"></td>
   </tr>
   <tr>
   <td>Old Script: </td><td><input type="text" name="old_script"></td>
   </tr>
   <tr>
   <td>Needs to be done: </td><td><input type="text" name="need_done" size="50"></td>
   </tr>
   <tr>
   <td>How to Test: </td><td><input type="text" name="how_to_test" size="50"></td>
   </tr>
   <tr>
   <td>Status: </td><td><textarea name="status" cols="50" rows="5" wrap="virtual"></textarea></td>
   </tr>
   <tr>
   <td></td>
   <td>
   <select name="done_flag">
   <option value="0">Not Done</option>
   <option value="1">Done</option>
   </select>
   </td>
   </tr>
   </table>
   <input type="submit" value="Submit">
   </form>
   };
   return $html_txt;
}

sub add_db {
   my $q = shift;
   my $group_id = $q->param("group_id");
   my $done_flag = $q->param("done_flag");
   my $new_script = $q->param("new_script");
   my $old_script = $q->param("old_script");
   my $need_done = $q->param("need_done");
   $need_done = "<a href=#check_ietm>Check Item</a> $need_done";
   my $how_to_test = $q->param("how_to_test");
   $how_to_test = "<a href=#test_item>Test Item</a> $how_to_test";
   my $status = format_textarea($q->param("status"));
   ($new_script,$old_script,$need_done,$how_to_test,$status) = db_quote($new_script,$old_script,$need_done,$how_to_test,$status);
   my $sqlStr = qq {
   insert into migrate_stat (new_script,old_script,need_done,how_to_test,status,group_id,done_flag)
   values ($new_script,$old_script,$need_done,$how_to_test,$status,$group_id,$done_flag)
   };
   unless (db_update($sqlStr)) {
      return "<h2>FATAL ERROR raised while adding a new record</h2><br>SQL = $sqlStr";
   }
   
   return main_screen();
}

sub update {
   my $q = shift;
   my $id = $q->param("req_id");

   my ($done_flag,$id,$new_script,$old_script,$need_done,$how_to_test,$status,$group_id) = rm_tr(db_select("select done_flag,id,new_script,old_script,need_done,how_to_test,status,group_id from migrate_stat  where id=$id"));

   my $option_str = "";
   my $ind = 0;
   for $array_ref (@groups) {
      my $value = $array_ref;
	  my $selected = "";
	  $selected= "selected" if ($ind == $group_id);
	  $option_str .= qq {<option value="$ind" $selected>$value</option>
	  };
	  $ind++;
   }

   my $checked = "";
   $checked = "checked" if ($done_flag);
   my $html_txt = qq {
   $form_header
   <input type="hidden" name="command" value="update_db">
   <input type="hidden" name="req_id" value="$id">
   $table_header
   <tr>
   <td>Group ID: </td><td><select name="group_id">$option_str</select></td>
   </tr>
   <tr>
   <td>New Script: </td><td><input type="text" name="new_script" value="$new_script"></td>
   </tr>
   <tr>
   <td>Old Script: </td><td><input type="text" name="old_script" value="$old_script"></td>
   </tr>
   <tr>
   <td>Needs to be done: </td><td><input type="text" name="need_done" size="50" value="$need_done"></td>
   </tr>
   <tr>
   <td>How to Test: </td><td><input type="text" name="how_to_test" size="50" value="$how_to_test"></td>
   </tr>
   <tr>
   <td>Status: </td><td><textarea name="status" cols="50" rows="5" wrap="virtual">$status</textarea></td>
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
   my $group_id = $q->param("group_id");
   my $done_flag = $q->param("done_flag");
   my $new_script = $q->param("new_script");
   my $old_script = $q->param("old_script");
   my $need_done = $q->param("need_done");
   my $how_to_test = $q->param("how_to_test");
   my $status = format_textarea($q->param("status"));
   ($new_script,$old_script,$need_done,$how_to_test,$status) = db_quote($new_script,$old_script,$need_done,$how_to_test,$status);
   unless (my_defined($done_flag)) {
      $done_flag = 0;
   } else {
      $done_flag = 1;
   }
   my $sqlStr = qq {
   update migrate_stat
   set new_script = $new_script,
       group_id = $group_id,
	   old_script = $old_script,
	   need_done = $need_done,
	   how_to_test = $how_to_test,
	   status = $status,
	   done_flag = $done_flag
   where id = $id
   };
   unless (db_update($sqlStr)) {
      return "<h2>FATAL ERROR raised while adding a new record</h2><br>SQL = $sqlStr";
   }
   
   return main_screen();
}

