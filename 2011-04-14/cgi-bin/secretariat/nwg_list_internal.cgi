#!/usr/bin/perl
##########################################################################
# Copyright © 2004, Foretec Seminars, Inc.
##########################################################################
use lib '/a/www/ietf-datatracker/release';
use GEN_DBUTIL;
use GEN_UTIL;
use IETF;
use CGI;
init_database("ietf");

my $q = new CGI;
$program_name = "nwg_list_internal.cgi";
$program_title="IETF Non WG Mailing List Internal Tool";
$table_header = qq{<table cellpadding="0" cellspacing="0" border="0">
};
$form_header_post = qq{<form action="$program_name" method="POST">};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">};
$form_header_get = qq{<form action="$program_name" method="GET" name="form_get">};
$html_top = qq|
<html>
<HEAD><TITLE>$program_title</title>
<STYLE TYPE="text/css">
<!--
TD {text-decoration: none; color: #000000; font: 10pt arial;}
body {
  margin:0;
  padding:0;
  font-family: Arial, sans-serif;
  font-size: 13px;
  color: #022D66;
  font-style: normal;
  }
th {
  padding:6px 0px 10px 30px;
  line-height:1em;
  font-family: Arial, sans-serif;
  font-size: 1.0em;
  color: #333;
                                                                                                   
 }
/* Links
----------------------------------------------- */
a:link, a:visited {
  border-bottom:1px dotted #69f;
  color:#36c;
  text-decoration:none;
  }
a:visited {
  border-bottom-color:#969;
  color:#36c;
  }
a:hover {
  border-bottom:1px solid #f00;
  color:#f00;
  }
a.noline:link, a.noline:visited, a.noline:hover {border-style:none;}
-->
</STYLE>

</head>
<body>
<blockquote>
<img src="/images/nwg/mail_title_internal.gif" border="0"><br>
<img src="/images/nwg/t_un1.gif" border="0">
<br><br>
|;
$html_bottom = qq{
</blockquote>
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
   my $command = $q->param("command");
   my $html_txt;
   unless (my_defined($command)) {
     $html_txt .= main_menu();
   } else {
     my $func = "$command(\$q)";
     $html_txt .= eval($func);
   }
   $html_txt .= qq {
   $form_header_bottom
   <input type="hidden" name="command" value="main_menu">
   <input type="submit" value="Main Menu">
   <input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true">
   </form>
   };
   return $html_txt;
}

sub confirm {
  my $q=shift;
  my $id=$q->param("id");
  my $add_edit=$q->param("add_edit");
  my $list_url = $q->param("list_url");
  my $list_name = $q->param("list_name");
  my $admin = $q->param("admin");
  my $admin_confirm = $admin;
  my $status = $q->param("status");
  my $status_value = ($status == 1)?"Active":"Inactive";
  $admin_confirm =~ s/</&lt;/;
  $admin_confirm =~ s/>/&gt;/;
  my $purpose=$q->param("purpose");
  my $area_acronym_id=$q->param("area_acronym_id");
  my $area=db_select("select acronym from acronym where acronym_id=$area_acronym_id");
  my $subscribe_url=$q->param("subscribe_url");
  my $confirm_txt = qq{
<tr><td>List Name: </td><td><pre>$list_name</pre></td></tr>
<tr><td>List URL: </td><td><pre>$list_url</pre></td></tr>
<tr><td>Administrator(s): </td><td><pre>$admin_confirm</pre></td></tr>
<tr><td>Purpose: </td><td><pre>$purpose</pre></td></tr>
<tr><td>Area: </td><td><pre>$area</pre></td></tr>
<tr><td>Status: </td><td>$status_value</td></tr>
<tr><td>How to Subscribe: </td><td>$subscribe_url</td></tr>
};
  $subscribe_url = remove_dq($subscribe_url);
  return qq{
<table bgcolor="#88AED2" cellspacing="1" border="0">
<tr><td> 
<table bgcolor="f3f8fd" cellpadding="3" cellspacing="0" border="0">
<tr>
<td colspan=2>
<h3>Add/Edit confirmation</h3>
</td>
</tr>
$form_header_post
<input type="hidden" name="command" value="do_$add_edit">
<input type="hidden" name="id" value="$id">
<input type="hidden" name="list_name" value="$list_name">
<input type="hidden" name="list_url" value="$list_url">
<input type="hidden" name="purpose" value="$purpose">
<input type="hidden" name="admin" value="$admin">
<input type="hidden" name="status" value="$status">
<input type="hidden" name="area_acronym_id" value="$area_acronym_id">
<input type="hidden" name="subscribe_url" value="$subscribe_url">
$confirm_txt
<br>
<tr>
<td></td>
<td>
<input type="submit" value=" Submit ">
</form>
</td>
</tr>
</table>
</td>
</tr>
</table>
<br><br>
};
}

sub do_add {
  my $q=shift;
  my $list_name = db_quote($q->param("list_name"));
  my $list_url = db_quote($q->param("list_url"));
  my $admin = db_quote($q->param("admin"));
  my $purpose=db_quote($q->param("purpose"));
  my $subscribe_url=db_quote(restore_dq($q->param("subscribe_url")));
  my $area_acronym_id=$q->param("area_acronym_id");
  my $exist = 1;
  my $id = 0;
  while ($exist) {
    $id = db_quote(gen_random());
    $exist = db_select("select count(id) from none_wg_mailing_list where id=$id");
  }
  my $sqlStr = "insert into none_wg_mailing_list (id,purpose,area_acronym_id,admin,list_url,list_name,subscribe_url) values ($id,$purpose,$area_acronym_id,$admin,$list_url,$list_name,$subscribe_url)";
  db_update($sqlStr);
  return main_menu();
}

sub do_edit {
  my $q=shift;
  my $id=$q->param("id");
  my $list_url = db_quote($q->param("list_url"));
  my $list_name = db_quote($q->param("list_name"));
  my $admin = db_quote($q->param("admin"));
  my $purpose=db_quote($q->param("purpose"));
  my $area_acronym_id=$q->param("area_acronym_id");
  my $status = $q->param("status");
  my $subscribe_url=db_quote(restore_dq($q->param("subscribe_url")));
  my $sqlStr = "update none_wg_mailing_list set list_name = $list_name,list_url=$list_url,admin=$admin,purpose=$purpose,area_acronym_id=$area_acronym_id,status=$status,subscribe_url=$subscribe_url where id='$id'";
  db_update($sqlStr);
  return main_menu();
}


sub edit {
  my $q=shift;
  my $id=$q->param("id");
  my ($temp_id,$purpose,$area_acronym_id,$admin,$list_url,$list_name,$status,$subscribe_url) = db_select("select id,purpose,area_acronym_id,admin,list_url,list_name,status,subscribe_url from none_wg_mailing_list where id='$id'");
  my $area_option = get_area_option_str($area_acronym_id);
  my $active_selected = ($status == 1)?"selected":"";
  my $inactive_selected = ($status < 1)?"selected":"";
  $subscribe_url="http://" unless my_defined($subscribe_url);
  return qq{
<table bgcolor="#88AED2" cellspacing="1" border="0" width="594">
<tr><td> 
<table bgcolor="f3f8fd" cellpadding="3" cellspacing="0" border="0">

$form_header_post
<input type="hidden" name="command" value="confirm">
<input type="hidden" name="add_edit" value="edit">
<input type="hidden" name="id" value="$id">
<tr>
<td>List Name: </td>
<td><input type="text" name="list_name" size="50" value="$list_name"></td>
</tr>

<tr>
<td>List URL: </td>
<td><input type="text" name="list_url" size="50" value="$list_url"></td>
</tr>
<tr>
<td>Administrator(s)<br>
<i>(Name &lt;email address&gt;, ...): </i>
</td>
<td><textarea name="admin" rows="3" cols="50">$admin</textarea></td>
</tr>
<tr>
<td>Purpose: </td>
<td><textarea name="purpose" rows="4" cols="80">$purpose</textarea></td>
</tr>
<tr>
<td>Area</td>
<td><select name="area_acronym_id">
<option value="0">--Select Area</option>
$area_option
</select>
<br><br>
</td>
</tr>
<tr>
<td>Status</td>
<td><select name="status">
<option value="1" $active_selected>Active</option>
<option value="-1" $inactive_selected>Inactive</option>
</select>
<td></td>
</tr>
<Tr><td>How to Subscribe:</td>
<td><textarea name="subscribe_url" rows="3" cols="60">$subscribe_url</textarea></td></tr>
<tr>
<td colspan="2">
<input type="submit" value=" Submit ">
</form><br>
</td>
</tr>
</table>
<br>
$form_header_post
<input type="hidden" name="command" value="delete_list">
<input type="hidden" name="id" value="$id">
<input type="submit" value=" Delete this Mailing List " onClick="return window.confirm('Are you sure about deleting this mailing list?')">
</form>
<br>
};
}

sub delete_list {
  my $q=shift;
  my $id=$q->param("id");
  db_update("update none_wg_mailing_list set status=-1 where id=$id");
  return main_menu();
}

sub main_menu {
  my $list = get_list();
  my $area_option = get_area_option_str();
  return qq{
<a href="https://datatracker.ietf.org/public/nwg_list.cgi"><b>View Current list</b></a><br><br>
<table bgcolor="#88AED2" cellspacing="1" border="0" width="594">
<tr><td> 
<table bgcolor="f3f8fd" cellpadding="3" cellspacing="0" border="0">
<tr>
<td colspan=2><b>Add new list</b><br></td>
</tr>
$form_header_post
<input type="hidden" name="command" value="confirm">
<input type="hidden" name="add_edit" value="add">
<tr>
<td>List Name: </td>
<td><input type="text" name="list_name" size="50" value=""></td>
</tr>
<tr>
<td>List URL: </td>
<td><input type="text" name="list_url" size="50" value="http://"></td>
</tr>
<tr>
<td>Administrator(s)<br>
<i>(Name &lt;email address&gt;, ...): </i>
</td>
<td><textarea name="admin" rows="3" cols="50"></textarea></td>
</tr>
<tr>
<td>Purpose: </td>
<td><textarea name="purpose" rows="4" cols="80"></textarea></td>
</tr>
<tr>
<td>Area</td>
<td><select name="area_acronym_id">
<option value="0">--Select Area</option>
$area_option
</select>
<br><br>
</td>
</tr>
<tr>
<td></td>
<td>
<input type="submit" value=" ADD ">
</form><br>
</td>
</tr>
</table>
</td>
</tr>
</table>
<br><br>
<b>Edit current list</b><br>
$list
<br><br>
};
}

sub get_list {
  my $html_txt=undef;
  my @List = db_select_multiple("select id,list_name,list_url,status from none_wg_mailing_list  order by status DESC, list_name");
  for my $array_ref (@List) {
    my ($id,$list_name,$list_url,$status) = @$array_ref;
    $list_name = $list_url unless (my_defined($list_name));
    if ($status < 1) {
      $html_txt .= qq{<li><a href="$program_name?command=edit&id=$id"><font color="red">$list_name</a></font><br>
};
    } else {
      $html_txt .= qq{<li><a href="$program_name?command=edit&id=$id">$list_name</a><br>
};
    }
  }
  return $html_txt;
}




