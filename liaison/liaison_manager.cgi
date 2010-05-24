#!/usr/bin/perl
use lib '/a/www/ietf-datatracker/release';
use GEN_DBUTIL_NEW;
use GEN_UTIL;
use IETF;
use CGI;
use CGI_UTIL;
use Encode;
use constant BUFFER_SIZE => 16_384;
use constant MAX_FILE_SIZE => 5_242_880; # 5 MB Max file size
use constant MAX_OPEN_TRIES => 100;
$CGI::DISABLE_UPLOADS = 0;
$CGI::POST_MAX = MAX_FILE_SIZE;
                                                                                                                  
$host=$ENV{SCRIPT_NAME};
$devel_mode = ($host =~ /ls_demo/)?1:0;
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
$dbh=get_dbh();
$aristorisk = "<font color=\"red\"><b>*</b></font>";
$up_dir_local = "/a/www/ietf-datatracker/documents/LIAISON";
$up_dir = "/a/www/ietf-datatracker/documents/LIAISON/upload";

if ($devel_mode) {
  $up_dir_local = "/a/www/ietf-datatracker/documents/LIAISON";
  $up_dir = "/a/www/ietf-datatracker/documents/LIAISON/upload";

}
$temp_dir = "temp_queue";
$doc_url = ($devel_mode)?"https://datatracker.ietf.org/documents":"https://datatracker.ietf.org/documents/LIAISON";
$list_url = ($devel_mode)?"https://datatracker.ietf.org/devel/ls":"https://datatracker.ietf.org/public";
$rUser = $ENV{REMOTE_USER};
my $q = new CGI;
$person_or_org_tag = db_select($dbh,"select person_or_org_tag from iesg_login where login_name = '$rUser'");
$person_or_org_tag = db_select($dbh,"select person_or_org_tag from users where login_name = '$rUser'")  unless ($person_or_org_tag);
$person_or_org_tag = db_select($dbh,"select person_or_org_tag from email_addresses where email_address='$rUser'") unless ($person_or_org_tag);
$person_or_org_tag = db_select($dbh,"select person_or_org_tag from wg_password where login_name='$rUser'") unless ($person_or_org_tag);
$person_or_org_tag = $q->param("person_or_org_tag") unless ($person_or_org_tag);
print qq|Content-Type: text/html

<html>
<head><title>Liaison_Manager $mode_text</title>
<style type="text/css">

a:link, a:visited {
border-bottom:1px dotted #69f;
color:blue;
text-decoration:none;
}
a:visited {
border-bottom:1px dotted #969;
color:#939;
}
a:hover {
border-bottom:1px dotted #f00;
color:#f00;
}
</style>
</head>
<body topmargin='0' bottommargin='0' leftmargin='0' rightmargin='0' background='/images/back_dot.gif'>
<table bgcolor="#F4F2F2" border=2 cellpadding=0 cellspacing=0 width='800' height="300" align='center'>
<tr valign="top"><td>
<table width="100%" height='100%' border=0 cellpadding=0 cellspacing=0 bgcolor="#FFFFFF">
  <tr valign="top"><td align="center"><img src="/images/liaison_title.gif" height="96" border="0"></td></tr>
  <tr valign="top"><td>
|;
error($q,"Unknown User",1) unless ($person_or_org_tag);

$in_users_table = db_select($dbh,"select count(*) from users where person_or_org_tag=$person_or_org_tag");
$user_level = ($in_users_table)?db_select($dbh,"select user_level from users where person_or_org_tag=$person_or_org_tag"):"1";
$is_other_sdo = db_select($dbh,"select count(*) from from_bodies where poc=$person_or_org_tag and other_sdo=1");

$form_header = "<form name=\"form_post\"  action=\"liaison_manager.cgi\" method=\"post\">\n<input type=\"hidden\" name=\"person_or_org_tag\" value=\"$person_or_org_tag\">";

$form_header_name .= "<form name=\"form2\" action=\"liaison_manager.cgi\" method=\"post\">\n<input type=\"hidden\" name=\"person_or_org_tag\" value=\"$person_or_org_tag\">";

$form_header_java = qq|<form action="liaison_manager.cgi" method="post" name="form1">


<input type="hidden" name="person_or_org_tag" value="$person_or_org_tag">
<script language="javascript">
function verify_other_purpose () {
  if (document.form1.purpose_id.selectedIndex == 5) {
    document.form1.purpose.disabled = false;
  } else {
    document.form1.purpose.disabled = true;
    alert ("You must select 'Other' purpose to use this text box");
  }
  return true;
}
function verify_deadline () {
  if (document.form1.purpose_id.selectedIndex == 5 \|\| document.form1.purpose_id.selectedIndex == 1 \|\| document.form1.purpose_id.selectedIndex == 2) {
  } else {
    document.form1.deadline_day.disabled = true;
    document.form1.deadline_month.disabled = true;
    document.form1.deadline_year.disabled = true;
    alert ("You must select 'For action,' 'For comment,' or 'Other' purpose to set a deadline date");
  }
  return true;
}
function modify_other_purpose (selectedIndex) {
  if (selectedIndex == 5) {
    document.form1.purpose.disabled = false;
    document.form1.deadline_day.disabled=false;
    document.form1.deadline_month.disabled=false;
    document.form1.deadline_year.disabled=false;
  } else {
    document.form1.purpose.value = "";
    document.form1.purpose.disabled = true;
    if (selectedIndex == 1 \|\| selectedIndex == 2) {
      document.form1.deadline_day.disabled=false;
      document.form1.deadline_month.disabled=false;
      document.form1.deadline_year.disabled=false;
    } else {
      document.form1.deadline_day.disabled=true;
      document.form1.deadline_month.disabled=true;
      document.form1.deadline_year.disabled=true;
      document.form1.deadline_day.selectedIndex=0;
      document.form1.deadline_month.selectedIndex=0;
      document.form1.deadline_year.selectedIndex=0;
    }
  }
}
</script>
|;


$form_header_upload = "<form action=\"liaison_manager.cgi\" method=\"post\"  ENCTYPE=\"multipart/form-data\" name=\"upload_form\">\n<input type=\"hidden\" name=\"person_or_org_tag\" value=\"$person_or_org_tag\">";

my $command = $q->param("command");
unless (my_defined($command)) {
main_screen($q);
} else {
my $func = "$command(\$q)";
eval($func);
}

$dbh->disconnect();
print qq{
<blockquote>
<a href="$list_url/liaisons.cgi"><img src="/images/blue_dot.gif" border="0">List of all liaison statements</a>
<br><br><br><br><br>
</td></tr>
</table>
</td></tr>
</table>
</body></html>
};


sub main_screen {
my $q=shift;
my $name = get_name($person_or_org_tag);
my $sqlStr = qq{select title, detail_id from liaison_detail where person_or_org_tag = $person_or_org_tag};


my $message = $q->param("message") or "";
$message = "**$message**" if (my_defined($message));
print qq{ 
<blockquote>
<font color="red">$message</font><br>
<img src="/images/blue_dot.gif" border="0">Current list of liaison statement(s) submitted by $name
<img src="/images/title_line.gif" border="0" height="12"><br>
};
my @List = db_select_multiple($dbh,$sqlStr);
if ($#List > -1) {
print qq{
&nbsp; &nbsp; (Click on the link below to update the liaison statement.)<br>
};
} else {
print qq{
&nbsp; &nbsp; No liaison statement has been submitted<br>
};
}  
for $array_ref (@List) {
my ($title,$detail_id) = @$array_ref;

print qq{
<table>
<tr><td>&nbsp;</td>
  <td><li><a href="liaison_manager.cgi?person_or_org_tag=$person_or_org_tag&command=view_liaison&detail_id=$detail_id">
$title</a></td></tr>
</table>
};
}


print qq{
<br><br>
<a href="liaison_manager.cgi?person_or_org_tag=$person_or_org_tag&command=add_new_liaison"><img src="/images/blue_dot.gif" border="0" >Add new liaison statement</a>
</blockquote>
};

}

sub view_liaison {
my $q=shift;
my $message = $q->param("message") or "";
$message = "<br><font color=\"red\">**$message**</font>" if (my_defined($message));
my $detail_id = $q->param("detail_id");
my ($submitted_date,$from_id,$to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$deadline_date,$body,$to_poc,$purpose_id) = db_select($dbh,"select submitted_date,from_id,to_body,cc1,cc2,title,response_contact,technical_contact,purpose,deadline_date,body,to_poc,purpose_id from liaison_detail where detail_id = $detail_id");
my $email_priority=db_select($dbh,"select email_priority from from_bodies where from_id=$from_id");
my $body_name = get_name_from($from_id);
$deadline_date = "None" if ($deadline_date eq "0000-00-00");
$to_poc = parse_email_list($to_poc);
$to_body .= "($to_poc)";
my $response_list = parse_email_list($response_contact);
my $tech_list = parse_email_list($technical_contact);
my $cc_list = parse_email_list($cc1);
$cc_list = make_one_per_line($cc_list);
$response_list = make_one_per_line($response_list);
$tech_list = make_one_per_line($tech_list);
my $purpose_text = ($purpose_id == 5)?"$purpose":db_select($dbh,"select purpose_text from liaison_purpose where purpose_id=$purpose_id");
$purpose_text = "" unless $purpose_id;
my $from_name=get_name($person_or_org_tag);
my $from_email=get_email($person_or_org_tag,$email_priority);
$from_name = "<a href=\"mailto:$from_email\">$from_name</a>";
print qq{
$message
<center><h3>$title</h3></center>
  <blockquote>
  <table cellspacing="3" bgcolor="cccc99">
  <tr>
  <td bgcolor="#efefef" width="25%">Submission Date: </td><td width="75%"><pre>$submitted_date</pre></td></tr>
  <tr>
  <td bgcolor="#efefef" width="25%">From: </td><td width="75%"><pre>$body_name ($from_name)</pre></td></tr>
  <tr>
  <td bgcolor="#efefef">To: </td><td><pre>$to_body</pre></td></tr>
  <tr>
  <td bgcolor="#efefef">Cc:</td><td><pre>$cc_list</pre></td></tr>
  <tr>
  <td bgcolor="#efefef">Response Contact:</td>
  <td>
<pre>$response_list</pre>
  </td></tr>
  <tr>
  <td bgcolor="#efefef">Technical Contact:</td>
  <td>
<pre>$tech_list</pre></td>
  </tr>
  <tr>
  <td bgcolor="#efefef">Purpose:</td><td><pre>$purpose_text</pre></td></tr>
  <tr>
  <td bgcolor="#efefef">Deadline:</td><td><pre>$deadline_date</pre></td></tr>
  <tr>
  <td bgcolor="#efefef">Body:</td><td><pre>$body</pre></td></tr>
  </table>
<hr>
<h3>Attached Document(s)</h3>};
  my $sqlStr = "select file_id,file_title,file_extension from uploads where detail_id=$detail_id";
  my @List = db_select_multiple($dbh,$sqlStr);
  for $array_ref (@List) {
    my ($file_id,$file_title,$file_extension) = @$array_ref;
    print qq{<li><a href="$doc_url/file$file_id$file_extension">$file_title</a><br>
};
  }
  print "<i>NONE</i><br>\n" if ($#List < 0);
  print qq{<hr>
$form_header
<input type="hidden" name="detail_id" value="$detail_id">
<input type="hidden" name="command" value="update_liaison">
<input type="submit" name="submit" value="Update Liaison Satatement">
</form>
$form_header
<input type="submit" name="submit" value="User Main Screen">
</form>

};

}


sub update_liaison {
  my $q = shift;
  my $cc_help_cgi = ($user_level)?"liaison_guide_from_ietf":"liaison_guide_to_ietf";
  $cc_help_cgi = "liaison_guide_to_ietf" if $is_other_sdo;
  my $cc_help_line =($user_level and $is_other_sdo)?qq{
  <li> <a href="https://datatracker.ietf.org/public/liaison_guide_from_ietf.cgi" target="help_screen">Guidelines for Completing Cc Field From IETF</a></li>
  <li> <a href="https://datatracker.ietf.org/public/liaison_guide_to_ietf.cgi" target="help_screen">Guidelines for Completing Cc Field To IETF</a></li>
}:qq{
  <li> <a href="https://datatracker.ietf.org/public/$cc_help_cgi.cgi" target="help_screen">Guidelines for Completing Cc Field</a></li>
};
  my $message = $q->param("message") or "";
  $message = "<br><font color=\"red\">**$message**</font>" if (my_defined($message));
  my $detail_id = $q->param("detail_id");
  my $current_date = db_select($dbh, "select curdate()");
  my ($my_from_id,$to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$deadline_date,$body,$to_poc,$purpose_id)= db_select($dbh,"select from_id, to_body, cc1, cc2, title, response_contact,technical_contact,purpose,deadline_date,body,to_poc,purpose_id from liaison_detail where detail_id=$detail_id");
  ($to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc) = html_bracket($to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc);
  ($to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc) = html_dq($to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc);
  my $poc_count = db_select($dbh,"select count(*) from from_bodies where poc = $person_or_org_tag");
  my ($deadline_year,$deadline_month,$deadline_day) = db_select($dbh,"select year('$deadline_date'),month('$deadline_date'),dayofmonth('$deadline_date')");
  my $purpose_list = get_purpose_list($purpose_id);
  print qq{
<center><font size=4><b>Update Liaison Statement</b></font></center><br>
$message
 <li> If you wish to submit your liaison statement by e-mail, then please send it to <a HREF="mailto:statements\@ietf.org">statements\@ietf.org</a></li>
  <li> <a href="https://datatracker.ietf.org/public/liaison_field_help.cgi" target="help_screen">Field Help</a></li>
  <li> <a href="https://datatracker.ietf.org/public/liaison_managers_list.cgi" target="help_screen">IETF Liaison Managers</a></li>
$cc_help_line
($aristorisk <font color="red">- required field)</font>
$form_header_java
<table bgcolor="cccc99">
};
  my $wg_count = db_select($dbh,"select count(*) from g_chairs a, groups_ietf b where person_or_org_tag=$person_or_org_tag and a.group_acronym_id = b.group_acronym_id and b.status_id=1 and b.group_type_id=1");
  my $area_count = db_select($dbh,"select count(*) from areas a, area_directors b where b.person_or_org_tag=$person_or_org_tag and a.area_acronym_id=b.area_acronym_id and a.status_id=1");
  if (($poc_count + $wg_count + $area_count) > 1) {
    my $sqlStr = qq{select from_id, body_name from from_bodies where poc = $person_or_org_tag};
    print qq{
<tr>
<td bgcolor="#cccc99">From:</td> <td><select name="from_id" size=1>
};  
    my @List = db_select_multiple($dbh,$sqlStr);
    for $array_ref (@List) {
      my ($from_id, $body_name) = @$array_ref;
      my $selected = "";
      if ($from_id == $my_from_id) {
        $selected = "selected";
      }
      print qq{<option value="$from_id" $selected>$body_name</option>
};
    }
    my @List2 = db_select_multiple($dbh,"select a.group_acronym_id, acronym from g_chairs a, groups_ietf b, acronym c where person_or_org_tag=$person_or_org_tag and a.group_acronym_id = b.group_acronym_id and b.status_id=1 and b.group_acronym_id=c.acronym_id  and b.group_type_id=1");
    for my $array_ref (@List2) {
      my ($from_id,$body_name) = @$array_ref;
      $body_name = uc($body_name);
      $body_name = "IETF $body_name WG";
      my $selected = "";
       if ($from_id == $my_from_id) {
         $selected = "selected";
       }
      print qq{<option value="$from_id" $selected>$body_name</option>
};
    }
    my @List3 = db_select_multiple($dbh,"select a.area_acronym_id,c.acronym from area_directors a, areas b, acronym c where a.person_or_org_tag=$person_or_org_tag and a.area_acronym_id=b.area_acronym_id and b.status_id=1 and a.area_acronym_id=c.acronym_id");
    for my $array_ref (@List3) {
      my ($from_id,$body_name) = @$array_ref;
      $body_name = uc($body_name);
      $body_name = "IETF $body_name AREA";
      my $selected = "";
       if ($from_id == $my_from_id) {
         $selected = "selected";
       }

      print qq{<option value="$from_id" $selected>$body_name</option>
};
    }

    print qq{
</select></td></tr>};
    
  }
  else {
	my $is_secretariat = db_select($dbh,"select user_level from iesg_login where person_or_org_tag = '$person_or_org_tag'");
	if ($is_secretariat eq 0){
            my $sqlStr = qq{select from_id, body_name from from_bodies};
            print qq{
            <tr>
            <td bgcolor="#cccc99">From:</td> <td><select name="from_id" size=1>
};  
            my @List = db_select_multiple($dbh,$sqlStr);
        
            for $array_ref (@List) {
                my ($from_id, $body_name) = @$array_ref;
                my $selected = "";
                if ($from_id == $my_from_id) {
                   $selected = "selected";
                }
            print qq{<option value="$from_id" $selected>$body_name</option>
};
           }

            my @List2 = db_select_multiple($dbh,"select a.group_acronym_id, acronym from g_chairs a, groups_ietf b, acronym c where a.group_acronym_id = b.group_acronym_id and b.status_id=1 and b.group_acronym_id=c.acronym_id  and b.group_type_id=1");

            for my $array_ref (@List2) {
                my ($from_id,$body_name) = @$array_ref;
                $body_name = uc($body_name);
                $body_name = "IETF $body_name WG";
                my $selected = "";
                if ($from_id == $my_from_id) {
                    $selected = "selected";
                }
           print qq{<option value="$from_id" $selected>$body_name</option>
};
           }

            my @List3 = db_select_multiple($dbh,"select a.area_acronym_id,c.acronym from area_directors a, areas b, acronym c where a.area_acronym_id=b.area_acronym_id and b.status_id=1 and a.area_acronym_id=c.acronym_id");

            for my $array_ref (@List3) {
                my ($from_id,$body_name) = @$array_ref;
                $body_name = uc($body_name);
                $body_name = "IETF $body_name AREA";
                my $selected = "";
                if ($from_id == $my_from_id) {
                    $selected = "selected";
                }

           print qq{<option value="$from_id" $selected>$body_name</option>
};
           }

    print qq{
</select></td></tr>};
	} else {	
  my ($from_id,$body_name) = db_select($dbh,"select from_id,body_name from from_bodies where poc = $person_or_org_tag");
	  print qq{
<input type="hidden" name="from_id" value="$from_id">
<table bgcolor="#cccc99" cellpadding="4">
  <tr>
    <td bgcolor="#efefef">From:</td> <td>$body_name</td></tr> 
};
	}
  }
my $deadline_day_options = "<option value=\"0\">--</option>\n";
for ($loop=1;$loop<32;$loop++) {
  my $selected = "";
  $selected = "selected" if ($loop == $deadline_day);
  $deadline_day_options .= "<option value=\"$loop\"i $selected>$loop</option>\n";
}
my $current_year = db_select($dbh,"select year(current_date)");
my $deadline_year_options = "<option value=\"0\">----</option>\n";
for ($loop=0;$loop<5;$loop++) {
  my $selected = "";
  $selected = "selected" if ($current_year == $deadline_year);
  $deadline_year_options .= "<option value=\"$current_year\" $selected>$current_year</option>\n";
  $current_year++;
}
my @months = ("","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec");
my $deadline_month_options = "<option value=\"0\">---</option>\n";
for ($loop=1;$loop<13;$loop++) {
  my $selected = "";
  $selected="selected" if ($loop == $deadline_month);
  $deadline_month_options .= "<option value=\"$loop\" $selected>$months[$loop]</option>\n";
}
print qq{
<tr>
<td  bgcolor="#efefef">Reply-To:$aristorisk</td>
<td><input type="text" name="replyto" size="94"></td></tr>
<tr>
<td bgcolor="#efefef">To:</td> 
<td>
<table cellpadding="0" cellspacing="0" border="0">
<tr><td>Organization:$aristorisk</td><td><input type="text" onkeypress="return handleEnter(this, event)" name="to_body" size="80" value="$to_body"></td></tr>
<Tr><td>POC:</td><td><input type="text" onkeypress="return handleEnter(this, event)" name="to_poc" size="80" value="$to_poc"></td></tr>
</table>

</td></tr>
<tr>
<td bgcolor="#efefef">Cc:<br>(Separated by commas)</td><td><input type="text"  onkeypress="return handleEnter(this, event)" name="cc1" value="$cc1" size="100"></td></tr>
<input type="hidden" name="cc2" value="">
<tr>
<td bgcolor="#efefef">Title:$aristorisk</td> <td><input type="text"  onkeypress="return handleEnter(this, event)" name="title" value="$title" size="100"></td></tr>
<tr>
<td bgcolor="#efefef">Response Contact: (Separated by commas)</td> <td><input type="text"  onkeypress="return handleEnter(this, event)" name="response_contact" value="$response_contact" size="100"></td></tr>
<tr>
<td bgcolor="#efefef">Technical Contact: (Separated by commas)</td> <td><input type="text"  onkeypress="return handleEnter(this, event)" name="technical_contact" value="$technical_contact" size="100"></td></tr>
<tr>
<td bgcolor="#efefef">Purpose: </td></td> 
<td><select name="purpose_id" onChange="modify_other_purpose(this.selectedIndex);">
<option value="0">--Select Purpose--</option>
$purpose_list
</select>
</td></tr>
<tr>
<td bgcolor="#efefef">Other Purpose:</td> <td><textarea name="purpose" rows=3 cols=80 onFocus="verify_other_purpose();">$purpose</textarea></td></tr>
<tr>
<td bgcolor="#efefef">Deadline:</td> 
<td><select name="deadline_day" onFocus="return verify_deadline();">
$deadline_day_options
</select>
<select name="deadline_month"  onFocus="return verify_deadline();">> 
$deadline_month_options
</select>
<select name="deadline_year" onFocus="return verify_deadline();">>
$deadline_year_options
  </select></td>
</tr>
<tr>
<td bgcolor="#efefef">Body:</td> <td><textarea name="body" rows=20 cols=80>$body</textarea></td></tr>
};
print qq{
<tr>
<td bgcolor="#efefef">Attachment(s):</td> 
<td>};
my $sqlStr = "select file_id,file_title,file_extension from uploads where detail_id = $detail_id";
my @List = db_select_multiple($dbh,$sqlStr);
for $array_ref (@List) {
  my ($file_id,$file_title,$file_extension) = @$array_ref;
print qq{
<li><a href="$doc_url/file$file_id$file_extension">$file_title</a>
};
  }
print qq{
</td></tr>
</table></blockquote>
<center>
<table><tr><td>
<input type="hidden" name="detail_id" value="$detail_id">
<input type="hidden" name="command" value="update_liaison_confirm">
<input type="submit" name="submit" value="Continue to Add/Remove Attachment(s)>>">
</form></td><td>
$form_header
<input type="hidden" name="command" value="view_liaison">
<input type="hidden" name="detail_id" value="$detail_id">
<input type="submit" value=" Back to View Detail Page ">
</form></td><td>
$form_header
<input type="submit" name="submit" value="User Main Screen">
</form>
</td></tr></table>
</center>
};
}
sub edit_attachment {
  my $q=shift;
  my $detail_id=$q->param("detail_id");
  my $title = db_select($dbh,"select title from liaison_detail where detail_id=$detail_id");
  my $message = $q->param("message") or "";
  $message = "<br><font color=\"red\">**$message**</font>" if (my_defined($message));
  print qq{$message
<h3>$title - Add/Remove Attachment</h3>
};
  my $sqlStr = "select file_id,file_title,file_extension from uploads where detail_id = $detail_id";
  my @List = db_select_multiple($dbh,$sqlStr);
  for $array_ref (@List) {
    my ($file_id,$file_title,$file_extension) = @$array_ref;
    print qq{<table border="0"><tr valign="top">
<td><li><a href="$doc_url/file$file_id$file_extension">$file_title</a></td>
$form_header
<input type="hidden" name="command" value="remove_document">
<input type="hidden" name="detail_id" value="$detail_id">
<input type="hidden" name="file_id" value="$file_id">
<input type="hidden" name="is_temp" value="0">
<td>
<input type="submit" name="submit" value="Remove" onClick="return window.confirm('Are you sure to remove this document from current Liaison Statement?');"></form>
</td></tr></table>
};
  }
  my $upload_form = get_upload_form($detail_id,0,0);
  print qq{$upload_form
<center>
<table><tr><td>
$form_header
<input type="hidden" name="command" value="view_liaison">
<input type="hidden" name="detail_id" value="$detail_id">
<input type="submit" value=" Back to View Detail Page ">
</form></td><td>
$form_header
<input type="submit" name="submit" value="User Main Screen">
</form>
</td></tr></table>
</center>
};
}

sub get_upload_form {
  my $detail_id=shift;
  my $is_temp=shift;
  my $detail_id_temp=shift;
  return qq{
<hr> 
<blockquote>
<h2>Add Attachment</h2>
$form_header_upload
<input type="hidden" name="command" value="upload_file">
<input type="hidden" name="detail_id" value="$detail_id">
<input type="hidden" name="detail_id_temp" value="$detail_id_temp">
<input type="hidden" name="is_temp" value="$is_temp">
<p> Please choose a file to upload:
<input type="FILE" name="file">
<br>
Please enter the title of this document:
<input type="text" name="file_title" size="75"><br>
<input type="submit" value=" Attach this Document ">
</blockquote>
</form>
};
}

sub upload_file {
  my $q=shift;
  my $file_title=$q->param("file_title");
  my $detail_id=$q->param("detail_id");
  my $is_temp=$q->param("is_temp");
  my $table = "uploads";
  my $extra_dir="";
  if ($is_temp) {
    $table="uploads_temp";
    $extra_dir = "$temp_dir/";
  }
  my $error_message = "";
  $q->cgi_error and $error_message = "<br>Error transferring file: ".$q->cgi_error;
  $error_message .= "<br>Title of the document is missing." unless my_defined($file_title);
  my $file = $q->param("file");
  unless (my_defined($file)) {
    $error_message .= "<br>No file received.";
  } else {
    $fh = $q->upload("file", -override=>1);   
    $error_message .= "<br>Invalid File - $file, $fh" unless ($fh);
  }
  error($q,$error_message,1) if (my_defined($error_message));
  my @temp = split '\.',$file;
  my $file_type = $temp[$#temp];
  my $type=$q->uploadInfo($fh)->{'Content-Type'};
  seek($fh,0,2);
  my $size=tell($fh);
  seek($fh,0,0);   
  my $buffer = "";
  my $file_id = db_select($dbh,"select max(file_id) from $table");
  $file_id++;
  my $filename = "file$file_id.$file_type";
  open OUTPUT,">$up_dir_local/$extra_dir$filename";
  binmode $fh;   
  binmode OUTPUT;
  while (read($fh,$buffer,BUFFER_SIZE)) {
    print OUTPUT $buffer;
  }
  close OUTPUT;
#  unless ($devel_mode and $is_temp) {
#    chdir $up_dir_local;
#    open FTP,"| /usr/bin/ftp -n" or return "Can't execute ftp\n\n";
#    print FTP <<END_OF_TRANSPORT
#open odin
#user ietfadm h0t3l;cal
#cd $up_dir
#put $filename
#quit
#                                                                                                                  
#END_OF_TRANSPORT
#;
#    close FTP;
#  }
  my $file_extension = ".$file_type";
  $file_title=db_quote($file_title);
  db_update($dbh,"insert into $table (file_id,file_title,person_or_org_tag,file_extension,detail_id) values ($file_id,$file_title,$person_or_org_tag,'$file_extension',$detail_id)");

  $q=add_cgi_message($q,"File has been uploaded successfully");
  if ($is_temp) {
    add_new_liaison_confirm($q);
  } else {
    update_liaison_confirm($q);
  }
}

sub check_liaison_error {
  my ($replyto,$title,$to_body,$response_contact,$technical_contact,$to_poc,$purpose_id,$body,$deadline_date,$cc1,$purpose) = @_;
  my $error_messgae = "";
  $error_message .= "Title is missing.<br>\n" unless my_defined($title);
  if (my_defined($replyto)) {
    $error_message .= "Reply-To - Email address is not in valid format.<br>\n" unless is_valid_email($replyto);
  } else {
    $error_message .= "Reply-To field is missing.<br>\n";
  }
  $error_message .= "To - Organization field is missing.<br>\n" unless my_defined($to_body);
  if (my_defined($to_poc)) {
    $error_message .= "To - POC's Email address is not in valid format.<br>\n" unless is_valid_email($to_poc);
  } else {
    $error_message .= "To - POC field is missing.<br>\n";
  }
  $error_message .= "Cc - Email address is not in valid format.<br>\n" if (my_defined($cc1) and !is_valid_email($cc1));
  $error_message .= "Response Contact - Email address is not in valid format.<br>\n" if (my_defined($response_contact) and !is_valid_email($response_contact));
  $error_message .= "Technical Contact - Email address is not in valid format.<br>\n" if (my_defined($technical_contact) and !is_valid_email($technical_contact));
  $error_message .= "Deadline date must be specified.<br>\n" if (($purpose_id == 1 or $purpose_id == 2) and $deadline_date eq "");
  $error_message .= "Please specify other purpose in the given text box.<br>\n" if ($purpose_id == 5 and $purpose eq "");
  if (my_defined($deadline_date)) {
    if ($purpose_id =~ /1|2|5/) {
      my $cur_time = time;
      my $deadline_time=get_time_stamp($deadline_date);
      $error_message .= "Deadline date must be set as later than today's date." if ($deadline_time < $cur_time);
    } else {
      $error_message .= "Deadline date cannot be set for the purpose other than 'For action,' 'For comment,' and 'Other'.";
    }
  }
  return $error_message;
}

sub do_update_liaison {
  my $q = shift;
  my $detail_id = $q->param("detail_id");
  my $detail_id_temp=$q->param("detail_id_temp");
  my ($from_id,$replyto,$to_body,$to_poc,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$deadline_date,$body,$submitted_date,$purpose_id) = db_select($dbh,"select from_id,replyto,to_body,to_poc,cc1,cc2,title,response_contact,technical_contact,purpose,deadline_date,body,submitted_date,purpose_id from liaison_detail_temp where detail_id=$detail_id_temp");
  my $num_attachment = db_select($dbh,"select count(*) from uploads where detail_id=$detail_id");
  error($q,"You must either fill in the body field or add an attachment.",1) if ($num_attachment == 0 and $body eq "");

  ($replyto,$to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc) = de_html_bracket($replyto,$to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc);
  ($replyto,$to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc) = de_html_dq($replyto,$to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc);
  ($replyto,$to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc) = db_quote($replyto,$to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc);
  my $sqlStr = "update liaison_detail set last_modified_date = current_date, from_id = $from_id, replyto=$replyto,to_body = $to_body, cc1 = $cc1, cc2 = $cc2, title = $title, response_contact=$response_contact, technical_contact=$technical_contact, purpose =$purpose, purpose_id=$purpose_id, deadline_date = '$deadline_date', body = $body, to_poc=$to_poc where detail_id = $detail_id";
  db_update($dbh,$sqlStr);
  if (defined($q->param("notify"))) {
    error($q,"Updated Liaison statement was not sent to the recipients.",1) unless  send_liaison_notification($detail_id,1);
  } else {
    send_liaison_notification($detail_id,2);
  }
  $q=add_cgi_message($q,"Liaison statement was updated successfully\n<br>Please confirm that your Liaison Statement has been updated on the <a href=\"https://datatracker.ietf.org/public/liaisons.cgi\">Liaison Statements</a> Web page.");
  view_liaison($q); 
}
  
sub get_single_from_id {
  my $person_or_org_tag=shift;
  my $from_id = db_select($dbh,"select from_id from from_bodies where poc = $person_or_org_tag");
  $from_id = db_select($dbh,"select a.group_acronym_id from g_chairs a, groups_ietf b where person_or_org_tag=$person_or_org_tag and a.group_acronym_id = b.group_acronym_id and b.status_id=1  and b.group_type_id=1") unless $from_id;
  $from_id = db_select($dbh,"select a.area_acronym_id from areas a, area_directors b where b.person_or_org_tag=$person_or_org_tag and a.area_acronym_id=b.area_acronym_id and a.status_id=1") unless $from_id;
  return $from_id;
}

sub add_new_liaison {
  my $q = shift;
  my $cc_help_cgi = ($user_level)?"liaison_guide_from_ietf":"liaison_guide_to_ietf";
  $cc_help_cgi = "liaison_guide_to_ietf" if $is_other_sdo;
  my $cc_help_line =($user_level and $is_other_sdo)?qq{
  <li> <a href="https://datatracker.ietf.org/public/liaison_guide_from_ietf.cgi" target="help_screen">Guidelines for Completing Cc Field From IETF</a></li>
  <li> <a href="https://datatracker.ietf.org/public/liaison_guide_to_ietf.cgi" target="help_screen">Guidelines for Completing Cc Field To IETF</a></li>
}:qq{
  <li> <a href="https://datatracker.ietf.org/public/$cc_help_cgi.cgi" target="help_screen">Guidelines for Completing Cc Field  user level $user_level</a></li>
};
  print qq{
$form_header_java
  <center> <font size=4><b>Add New Liaison Statement</b></font></center><br>
  <li> If you wish to submit your liaison statement by e-mail, then please send it to <a HREF="mailto:statements\@ietf.org">statements\@ietf.org</a></li>
  <li> <a href="https://datatracker.ietf.org/public/liaison_field_help.cgi" target="help_screen">Field Help</a></li>
  <li> <a href="https://datatracker.ietf.org/public/liaison_managers_list.cgi" target="help_screen">IETF Liaison Managers</a></li>
$cc_help_line
($aristorisk <font color="red">- required field)</font>
<table bgcolor="cccc99">
  <tr>
};
  my $current_date = db_select($dbh, "select curdate()");
  my $name_from = db_select($dbh,"select body_name from from_bodies where poc = $person_or_org_tag");
  my $poc_count = db_select($dbh,"select count(*) from from_bodies where poc = $person_or_org_tag");
  my $wg_count = db_select($dbh,"select count(*) from g_chairs a, groups_ietf b where person_or_org_tag=$person_or_org_tag and a.group_acronym_id = b.group_acronym_id and b.status_id=1 and b.group_type_id=1");
  my $area_count = db_select($dbh,"select count(*) from areas a, area_directors b where b.person_or_org_tag=$person_or_org_tag and a.area_acronym_id=b.area_acronym_id and a.status_id=1");


  if (($poc_count + $wg_count + $area_count) > 1) {
    print qq{
    <td bgcolor="#efefef">From:</td> <td><select name="from_id" size=1>
};
    my @List = db_select_multiple($dbh,"select from_id, body_name from from_bodies where poc = $person_or_org_tag");
    for my $array_ref (@List) {
      my ($from_id, $body_name) = @$array_ref;
      print qq{<option value="$from_id">$body_name</option>
};
    }
    my @List2 = db_select_multiple($dbh,"select a.group_acronym_id, acronym from g_chairs a, groups_ietf b, acronym c where person_or_org_tag=$person_or_org_tag and a.group_acronym_id = b.group_acronym_id and b.status_id=1 and b.group_acronym_id=c.acronym_id and b.group_type_id=1");
    for my $array_ref (@List2) {
      my ($from_id,$body_name) = @$array_ref;
      $body_name = uc($body_name);
      $body_name = "IETF $body_name WG";
      print qq{<option value="$from_id">$body_name</option>
};
    }
    my @List3 = db_select_multiple($dbh,"select a.area_acronym_id,c.acronym from area_directors a, areas b, acronym c where a.person_or_org_tag=$person_or_org_tag and a.area_acronym_id=b.area_acronym_id and b.status_id=1 and a.area_acronym_id=c.acronym_id");
    for my $array_ref (@List3) {
      my ($from_id,$body_name) = @$array_ref;
      $body_name = uc($body_name);
      $body_name = "IETF $body_name AREA";
      print qq{<option value="$from_id">$body_name</option>
};
    }
   print qq{
</select></td></tr>};

    }
  else {
	 my $is_secretariat = db_select($dbh,"select user_level from iesg_login where person_or_org_tag = '$person_or_org_tag'");
	 if ($is_secretariat == 0){
	 print qq{
	 <td bgcolor="#efefef">From:</td> <td><select name="from_id" size=1>
};

	 my @List = db_select_multiple($dbh,"select from_id, body_name from from_bodies");
	 for my $array_ref (@List) {
             my ($from_id, $body_name) = @$array_ref;
             print qq{<option value="$from_id">$body_name</option>
};
         }
         my @List2 = db_select_multiple($dbh,"select a.group_acronym_id, acronym from g_chairs a, groups_ietf b, acronym c where a.group_acronym_id = b.group_acronym_id and b.status_id=1 and b.group_acronym_id=c.acronym_id and b.group_type_id=1");

         for my $array_ref (@List2) {
             my ($from_id,$body_name) = @$array_ref;
             $body_name = uc($body_name);
             $body_name = "IETF $body_name WG";
             print qq{<option value="$from_id">$body_name</option>
};
         }
         my @List3 = db_select_multiple($dbh,"select a.area_acronym_id,c.acronym from area_directors a, areas b, acronym c where a.area_acronym_id=b.area_acronym_id and b.status_id=1 and a.area_acronym_id=c.acronym_id");

         for my $array_ref (@List3) {
             my ($from_id,$body_name) = @$array_ref;
             $body_name = uc($body_name);
	     $body_name = "IETF $body_name AREA";
	     print qq{<option value="$from_id">$body_name</option>
};
         }
         print qq{
</select></td></tr>};

        } else {
             my $from_id=get_single_from_id($person_or_org_tag);
             $name_from = get_name_from($from_id);
             print qq{
<input type="hidden" name="from_id" value="$from_id">
    <td bgcolor="#efefef">From:</td><td>$name_from</td></tr>
};

          }
  }
my $deadline_day_options = "<option value=\"0\">Day</option>\n";
for ($loop=1;$loop<32;$loop++) {
  $deadline_day_options .= "<option value=\"$loop\"i $selected>$loop</option>\n";
}
my $current_year = db_select($dbh,"select year(current_date)");
my $deadline_year_options = "<option value=\"0\">Year</option>\n";
for ($loop=0;$loop<5;$loop++) {
  $deadline_year_options .= "<option value=\"$current_year\" $selected>$current_year</option>\n";
  $current_year++;
}
my @months = ("","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec");
my $deadline_month_options = "<option value=\"0\">Month</option>\n";
for ($loop=1;$loop<13;$loop++) {
  $deadline_month_options .= "<option value=\"$loop\" $selected>$months[$loop]</option>\n";
}
  my $purpose_list = get_purpose_list();
  print qq{
<tr>
<td  bgcolor="#efefef">Reply-To:$aristorisk</td>
<td><input type="text"  onkeypress="return handleEnter(this, event)" name="replyto" size="80"></td></tr>
<tr>
<td  bgcolor="#efefef">To:</td><td>
<table cellpadding="0" cellspacing="0" border="0">
<tr><td>Organization:$aristorisk</td><td><input type="text" onkeypress="return handleEnter(this, event)" name="to_body" size="65"></td></tr>
<Tr><td>POC:$aristorisk</td><td><input type="text" onkeypress="return handleEnter(this, event)" name="to_poc" size="65"></td></tr>
</table>

</td></tr>
<tr>
<td bgcolor="#efefef">Cc:<br>(Separated by commas)</td><td><input type="text"  onkeypress="return handleEnter(this, event)" name="cc1" size="80"></td></tr>
<input type="hidden" name="cc2" value="">
<tr>
<td bgcolor="#efefef">Title:$aristorisk</td><td><input type="text"  onkeypress="return handleEnter(this, event)" name="title" size="80"></td></tr>
<tr>
<td bgcolor="#efefef">Response Contact: (Separated by commas)</td> <td><input type="text"  onkeypress="return handleEnter(this, event)" name="response_contact" size="80"></td></tr>
<tr>
<td bgcolor="#efefef">Technical Contact: (Separated by commas) </td></td> <td><input type="text"  onkeypress="return handleEnter(this, event)" name="technical_contact" size="80"></td></tr>
<tr>
<td bgcolor="#efefef">Purpose: </td></td> 
<td><select name="purpose_id" onChange="modify_other_purpose(this.selectedIndex);">
<option value="0">--Select Purpose--</option>
$purpose_list
</select>
</td></tr>
<tr>
<td bgcolor="#efefef">Other Purpose:</td> <td><textarea name="purpose" rows=3 cols=80 onFocus="verify_other_purpose();"></textarea></td></tr>
<tr>
<td bgcolor="#efefef">Deadline:</td>
<td><select name="deadline_day" onFocus="return verify_deadline();">>
$deadline_day_options
</select>
<select name="deadline_month" onFocus="return verify_deadline();">>
$deadline_month_options
</select>
<select name="deadline_year" onFocus="return verify_deadline();">>
$deadline_year_options
</select></td>
</tr>
<tr>
<td bgcolor="#efefef">Body:</td> <td><textarea name="body" rows=20 cols=80></textarea></td></tr>
};


print qq{
</table>   
</blockquote>
<center>
<table>
<tr valign="top"><td>
<input type="hidden" name="person_or_org_tag" value="$person_or_org_tag">
<input type="hidden" name="command" value="add_new_liaison_confirm">
<input type="submit" name="submit" value=" Continue>>">
</form></td><td>
$form_header
<input type="hidden" name="person_or_org_tag" value="$person_or_org_tag">
<input type="submit" name="submit" value="User Main Screen">
</form>
</td></tr>
</table>
</center>
};
}

sub get_purpose_list {
  my $selected_id=shift;
  $selected_id = 0 unless defined($selected_id);
  my $list_text = "";
  my @List = db_select_multiple($dbh,"select purpose_id,purpose_text from liaison_purpose");
  for my $array_ref (@List) {
    my ($purpose_id,$purpose_text) = @$array_ref;
    my $selected = ($selected_id == $purpose_id)?"selected":"";
    $list_text .= "<option value=\"$purpose_id\" $selected>$purpose_text</option>\n";
  }
  return $list_text;
}
sub update_liaison_confirm {
  my $q = shift;
  my $is_temp=$q->param("is_temp");
  my $from_id=0;
  my $to_body = "";
  my $replyto="";
  my $to_poc="";
  my $cc1="";
  my $cc2="";
  my $title="";
  my $response_contact="";
  my $technical_contact="";
  my $purpose="";
  my $purpose_id=0;
  my $deadline_date="";
  my $detail_id_temp=0;
  my $detail_id = $q->param("detail_id");
  if (defined($q->param("is_temp"))) {
    $detail_id_temp = $detail_id if $is_temp;
    $detail_id_temp = $q->param("detail_id_temp") unless $is_temp;
    ($from_id,$replyto,$to_body,$to_poc,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$deadline_date,$purpose_id) = db_select($dbh,"select from_id,replyto,to_body,to_poc,cc1,cc2,title,response_contact,technical_contact,purpose,body,deadline_date,purpose_id from liaison_detail_temp where detail_id=$detail_id_temp");
    $deadline_date = "" if ($deadline_date eq "0000-00-00");
  } else {
    $from_id = $q->param("from_id");
    $replyto = $q->param("replyto");
    $to_body = $q->param("to_body");
    $to_poc = $q->param("to_poc");
    $cc1 = $q->param("cc1");
    $cc2 = $q->param("cc2");
    $title = $q->param("title");
    $response_contact = $q->param("response_contact");
    $technical_contact = $q->param("technical_contact");
    $purpose = $q->param("purpose");
    $purpose_id = $q->param("purpose_id");
    my $deadline_day = $q->param("deadline_day");
    my $deadline_month = $q->param("deadline_month");
    my $deadline_year = $q->param("deadline_year");
    if ($deadline_year and $deadline_month and $deadline_day) {
      $deadline_date = "$deadline_year\-$deadline_month\-$deadline_day";
    }
                                                                                             
    $body = $q->param("body");
    my $error_message = check_liaison_error($replyto,$title,$to_body,$response_contact,$technical_contact,$to_poc,$purpose_id,$body,$deadline_date,$cc1,$purpose);
    error ($q,$error_message,1) if my_defined($error_message);
    my ($qreplyto,$qto_body,$qcc1,$qcc2,$qtitle,$qresponse_contact,$qtechnical_contact,$qpurpose,$qbody,$qto_poc) = db_quote($replyto,$to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc);
    my $new_liaison_detail_temp = "insert into liaison_detail_temp (person_or_org_tag,submitted_date,last_modified_date,from_id,replyto,to_body,cc1,cc2,title,response_contact,technical_contact,purpose,deadline_date,body,to_poc,purpose_id) values ($person_or_org_tag,current_date,current_date,$from_id,$qreplyto,$qto_body,$qcc1,$qcc2,$qtitle,$qresponse_contact,$qtechnical_contact,$qpurpose,'$deadline_date',$qbody,$qto_poc,$purpose_id)";
    db_update($dbh,$new_liaison_detail_temp);
    $detail_id_temp = db_select($dbh,"select max(detail_id) from liaison_detail_temp");
  }
  ($replyto,$to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc) = html_bracket($replyto,$to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc);
  $cc1 = make_one_per_line($cc1);
  $response_contact = make_one_per_line($response_contact);
  $technical_contact = make_one_per_line($technical_contact);
  my $name_from = get_name_from($from_id);
  my $attachement_list = "";
  my @List_attachment = db_select_multiple($dbh,"select file_id,file_title,file_extension from uploads where detail_id=$detail_id");
  if ($#List_attachment < 0) {
    $attachment_list = "<font color=\"red\"><i>No document has been attached</i></font>";
  } else {
     for my $array_ref (@List_attachment) {
       my ($file_id,$file_title,$file_extension) = @$array_ref;
       $attachment_list .= "<li> <a href=\"$doc_url/file$file_id$file_extension\">$file_title</a> <a href=\"$program_name?command=remove_document&detail_id=$detail_id&file_id=$file_id&is_temp=0&person_or_org_tag=$person_or_org_tag&detail_id_temp=$detail_id_temp\">[Remove]</a><br>\n";
     }
  }
  my $upload_form = get_upload_form($detail_id,0,$detail_id_temp);
  my $purpose_text = db_select($dbh,"select purpose_text from liaison_purpose where purpose_id=$purpose_id");
  $purpose_text = "" unless $purpose_id;
  $deadline_date = "None" unless my_defined($deadline_date);
  my $user_name = get_name($person_or_org_tag);
  my $from_email = get_email($person_or_org_tag);
  my $from_list = "$user_name($name_from) &lt;$from_email&gt;";
  print qq{
<table bgcolor="#FFFFFF" cellpadding="4" >
  <tr>
    <td bgcolor="#efefef">From:</td><td><pre>$from_list</pre></td></tr>
  <tr>
    <td bgcolor="#efefef">Reply-To:</td><td><pre>$replyto</pre></td></tr>
  <tr>
    <td  bgcolor="#efefef">To:</td><td>
<table border="0" cellpadding="0" cellspacing="0">
<tr valign="top"><td>Organization: </td><td><pre>$to_body</pre></td></tr>
<Tr valign="top"><td>POC: </td><td><pre>$to_poc</pre></td></tr>
</table>
</td></tr>
<tr>
<td bgcolor="#efefef">Cc:</td><td><pre>$cc1</pre></td></tr>
<tr>
<td bgcolor="#efefef">Title:</td><td><pre>$title</pre></td></tr>
<tr>
<td bgcolor="#efefef">Response Contact:</td> <td><pre>$response_contact</pre></td></tr>
<tr>
<td bgcolor="#efefef">Technical Contact: </td></td> <td><pre>$technical_contact</pre></td></tr>
<tr>
<td bgcolor="#efefef">Purpose:</td> <td><pre>$purpose_text</pre></td></tr>
<tr>
<td bgcolor="#efefef">Other Purpose:</td> <td><pre>$purpose</pre></td></tr>
<tr>
<td bgcolor="#efefef">Deadline:</td>
<td><pre>$deadline_date</pre></td>
</tr>
<tr>
<td bgcolor="#efefef">Body:</td> <td><pre>$body</pre></td></tr>
<tr>
<td bgcolor="#efefef">Attachment(s):</td><td><pre>$attachment_list</pre></td></tr>
</table>
</center>
<br>
$upload_form
<hr>
$form_header_name
<input type="hidden" name="command" value="do_update_liaison">
<input type="hidden" name="detail_id_temp" value="$detail_id_temp">
<input type="hidden" name="detail_id" value="$detail_id">
<input type="checkbox" name="notify"> Check this box if you want to notify all the recipients above about this update.<br>
<input type="submit" name="submit_form" value=" Submit this Update ">
</form>
$form_header
<input type="submit" name="submit" value="User Main Screen">
</form>

};
}

sub add_new_liaison_confirm {
  my $q = shift;
  my $is_temp=$q->param("is_temp");
  my $from_id=0;
  my $replyto = "";
  my $to_body = "";
  my $to_poc="";
  my $cc1="";
  my $cc2="";
  my $title="";
  my $response_contact="";
  my $technical_contact="";
  my $purpose="";
  my $purpose_id=0;
  my $deadline_date="";
  my $detail_id_temp=0;
  if ($is_temp) {
    $detail_id_temp = $q->param("detail_id");
    ($from_id,$replyto,$to_body,$to_poc,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$deadline_date,$purpose_id) = db_select($dbh,"select from_id,replyto,to_body,to_poc,cc1,cc2,title,response_contact,technical_contact,purpose,body,deadline_date,purpose_id from liaison_detail_temp where detail_id=$detail_id_temp");
    $deadline_date = "" if ($deadline_date eq "0000-00-00");
  } else {
    $from_id = $q->param("from_id");
    $email_priority=db_select($dbh,"select email_priority from from_bodies where from_id=$from_id");
    $replyto = $q->param("replyto");
    $to_body = $q->param("to_body");
    $to_poc = $q->param("to_poc");
    $cc1 = $q->param("cc1");
    $cc2 = $q->param("cc2");
    $title = $q->param("title");
    $response_contact = $q->param("response_contact");
    $technical_contact = $q->param("technical_contact");
    $purpose = $q->param("purpose");
    $purpose_id = $q->param("purpose_id");
    my $deadline_day = $q->param("deadline_day");
    my $deadline_month = $q->param("deadline_month");
    my $deadline_year = $q->param("deadline_year");
    if ($deadline_year and $deadline_month and $deadline_day) {
      $deadline_date = "$deadline_year\-$deadline_month\-$deadline_day";
    } 
	    
    $body = $q->param("body");
    my $error_message = check_liaison_error($replyto,$title,$to_body,$response_contact,$technical_contact,$to_poc,$purpose_id,$body,$deadline_date,$cc1,$purpose);
    error ($q,$error_message,1) if my_defined($error_message);
    my ($qreplyto,$qto_body,$qcc1,$qcc2,$qtitle,$qresponse_contact,$qtechnical_contact,$qpurpose,$qbody,$qto_poc) = db_quote($replyto,$to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc);
    my $new_liaison_detail_temp = "insert into liaison_detail_temp (person_or_org_tag,submitted_date,last_modified_date,from_id,replyto,to_body,cc1,cc2,title,response_contact,technical_contact,purpose,deadline_date,body,to_poc,purpose_id) values ($person_or_org_tag,current_date,current_date,$from_id,$qreplyto,$qto_body,$qcc1,$qcc2,$qtitle,$qresponse_contact,$qtechnical_contact,$qpurpose,'$deadline_date',$qbody,$qto_poc,$purpose_id)";
    db_update($dbh,$new_liaison_detail_temp);  
    $detail_id_temp = db_select($dbh,"select max(detail_id) from liaison_detail_temp");
  }
  ($replyto,$to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc) = html_bracket($replyto,$to_body,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body,$to_poc);
  $cc1 = make_one_per_line($cc1);
  $response_contact = make_one_per_line($response_contact);
  $technical_contact = make_one_per_line($technical_contact);
  my $name_from = get_name_from($from_id);
  my $attachement_list = "";
  my @List_attachment = db_select_multiple($dbh,"select file_id,file_title,file_extension from uploads_temp where detail_id=$detail_id_temp");
  if ($#List_attachment < 0) {
    $attachment_list = "<font color=\"red\"><i>No document has been attached</i></font>";
  } else {
     for my $array_ref (@List_attachment) {
       my ($file_id,$file_title,$file_extension) = @$array_ref;
       $attachment_list .= "<li> <a href=\"$doc_url/$temp_dir/file$file_id$file_extension\" target=\"_blank\">$file_title</a> <a href=\"$program_name?command=remove_document&detail_id=$detail_id_temp&file_id=$file_id&is_temp=1&person_or_org_tag=$person_or_org_tag\">[Remove]</a><br>\n";
     }
  }
  my $upload_form = get_upload_form($detail_id_temp,1,0);
  my $purpose_text = db_select($dbh,"select purpose_text from liaison_purpose where purpose_id=$purpose_id");
  $purpose_text = "" unless $purpose_id;
  $deadline_date = "None" unless my_defined($deadline_date);
  my $user_name = get_name($person_or_org_tag);
  my $from_email = get_email($person_or_org_tag,$email_priority);
  my $from_list = "$user_name($name_from) &lt;$from_email&gt;";
  print qq{
<table bgcolor="#FFFFFF" cellpadding="4" >
  <tr>
    <td bgcolor="#efefef">From:</td><td><pre>$from_list</pre></td></tr>
  <tr>
    <td bgcolor="#efefef">Reply-To:</td><td><pre>$replyto</pre></td></tr>
  <tr>
    <td  bgcolor="#efefef">To:</td><td>
<table border="0" cellpadding="0" cellspacing="0">
<tr valign="top"><td>Organization: </td><td><pre>$to_body</pre></td></tr>
<Tr valign="top"><td>POC: </td><td><pre>$to_poc</pre></td></tr>
</table>
</td></tr>
<tr>
<td bgcolor="#efefef">Cc:</td><td><pre>$cc1</pre></td></tr>
<tr>
<td bgcolor="#efefef">Title:</td><td><pre>$title</pre></td></tr>
<tr>
<td bgcolor="#efefef">Response Contact:</td> <td><pre>$response_contact</pre></td></tr>
<tr>
<td bgcolor="#efefef">Technical Contact: </td></td> <td><pre>$technical_contact</pre></td></tr>
<tr>
<td bgcolor="#efefef">Purpose:</td> <td><pre>$purpose_text</pre></td></tr>
<tr>
<td bgcolor="#efefef">Other Purpose:</td> <td><pre>$purpose</pre></td></tr>
<tr>
<td bgcolor="#efefef">Deadline:</td>
<td><pre>$deadline_date</pre></td>
</tr>
<tr>
<td bgcolor="#efefef">Body:</td> <td><pre>$body</pre></td></tr>
<tr>
<td bgcolor="#efefef">Attachment(s):</td><td><pre>$attachment_list</pre></td></tr>
</table>
</center>
$upload_form
<hr>
$form_header_name
<input type="hidden" name="command" value="do_add_liaison">
<input type="hidden" name="detail_id_temp" value="$detail_id_temp">
<input type="submit" name="submit_form" value=" Submit ">
</form>
$form_header
<input type="submit" name="submit" value="User Main Screen">
</form>
};

#print qq{<pre>
#From : $from_lis
#Reply-To: $replyto
#To Organization : $to_body
#To POC : $to_poc
#Cc : $cc1
#Title : $title
#Response Contact : $response_contact
#Technical Contcat : $technical_contact
#Purpose : $purpose_text
#Other Purpose : $purpose
#Deadline : $deadline_date
#Body : $body
#Attchements : $attachment_list
#upload_form : $upload_form
#</pre>
#};

}

sub do_add_liaison {
  my $q = shift;
  my $detail_id_temp = $q->param("detail_id_temp");
  my @List_temp = db_select_multiple($dbh,"select file_id,file_title,file_extension from uploads_temp where detail_id=$detail_id_temp");
  my ($from_id,$replyto,$to_body,$to_poc,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$deadline_date,$body,$submitted_date,$purpose_id) = db_select($dbh,"select from_id,replyto,to_body,to_poc,cc1,cc2,title,response_contact,technical_contact,purpose,deadline_date,body,submitted_date,purpose_id from liaison_detail_temp where detail_id=$detail_id_temp"); 
  if ($#List_temp < 0 and $body eq "") {
    error($q,"You must either fill in the body field or add an attachment.",1);
  }
  ($replyto,$to_body,$to_poc,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body) = db_quote($replyto,$to_body,$to_poc,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,$body);
  my $exist_id = db_select($dbh,"select detail_id from liaison_detail where title=$title");
  if ($exist_id) {
    $go_back = qq{$form_header
<input type="button" value="Go back to the form" onClick="return history.go(-2);"><br><br><input type="submit" value="User Main Screen">
</form>
};
    error($q,"A liaison statement with the same title, <a href=\"$program_name?person_or_org_tag=$person_or_org_tag&command=view_liaison&detail_id=$exist_id\" target=\"_blank\">$title</a> has previously been submitted. Please go back and use different title.\n$go_back",1);
  }
  my $new_liaison_detail = "insert into liaison_detail (person_or_org_tag,submitted_date,last_modified_date,from_id,replyto,to_body,to_poc,cc1,cc2,title,response_contact,technical_contact,purpose,deadline_date,body,purpose_id) values ($person_or_org_tag,'$submitted_date',current_date,$from_id,$replyto,$to_body,$to_poc,$cc1,$cc2,$title,$response_contact,$technical_contact,$purpose,'$deadline_date',$body,$purpose_id)";
  db_update($dbh,$new_liaison_detail);
  my $new_id=db_select($dbh,"select max(detail_id) from liaison_detail");
  for my $array_ref (@List_temp)  {
    my ($file_id,$file_title,$file_extension) = @$array_ref;
    $file_title = db_quote($file_title);
    db_update($dbh,"insert into uploads (file_title,file_extension,detail_id,person_or_org_tag) values ($file_title,'$file_extension',$new_id,$person_or_org_tag)");
    my $new_file_id = db_select($dbh,"select max(file_id) from uploads");
    system "mv $up_dir_local/temp_queue/file$file_id$file_extension $up_dir_local/file$new_file_id$file_extension"; 

  }
  error($q,"New Liaison statement was not sent to the recipients.",1) unless  send_liaison_notification($new_id,0);
  $q=add_cgi_message($q,"New Liaison Statement has been submitted successfully\n<br>Please confirm that your Liaison Statement has been posted on the <a href=\"https://datatracker.ietf.org/public/liaisons.cgi\">Liaison Statements</a> Web page.");
  main_screen($q);
}



sub remove_document {
  my $q = shift;
  my $detail_id = $q->param("detail_id");
  my $file_id = $q->param("file_id");
  my $is_temp=$q->param("is_temp");
  my $table = "uploads";
  my $extra_dir="";
  if ($is_temp) {
    $table="uploads_temp";
    $extra_dir = "$temp_dir/";
  }
  my $file_extension=db_select($dbh,"select file_extension from $table where file_id=$file_id");
  my $document = "delete from $table where detail_id = $detail_id and file_id = $file_id ";
  db_update($dbh,$document);
  unlink "$up_dir_local/${extra_dir}file$file_id$file_extension";
  $q=add_cgi_message($q,"Document has been removed successfully");
  if ($is_temp) {
    add_new_liaison_confirm($q);
  } else {
    update_liaison_confirm($q);
  }
}

sub send_liaison_notification {
  my $detail_id=shift;
  my $is_update=shift;
  my ($submitted_date,$replyto,$to_body,$to_poc,$response_contact,$technical_contact,$title,$person_or_org_tag,$from_id,$purpose,$body,$deadline_date,$cc1,$purpose_id) = db_select($dbh,"select submitted_date,replyto,to_body,to_poc,response_contact,technical_contact,title,person_or_org_tag,from_id,purpose,body,deadline_date,cc1,purpose_id from liaison_detail where detail_id=$detail_id");
  my $email_priority=db_select($dbh,"select email_priority from from_bodies where from_id=$from_id");
  my $cc_list = "$cc1";
  $cc_list .= "," if my_defined($cc1);
  $cc_list .= "$response_contact," if my_defined($response_contact);
  $cc_list .= "$technical_contact," if my_defined($technical_contact);

  $cc_list .= get_cc_list($person_or_org_tag);
  chop($cc_list);
  $to_body .= "($to_poc)" if my_defined($to_poc);
  my $from_name = get_name_from($from_id);
  #my $from_name = db_select($dbh,"select body_name from from_bodies where from_id=$from_id");
  my $user_name = get_name($person_or_org_tag);
  my $from_email = get_email($person_or_org_tag,$email_priority);
  my $from_list = "$user_name($from_name) <$from_email>";
  my $subject = ($is_update)?"Updated Liaison Statement, \"$title\"":"New Liaison Statement, \"$title\"";
  $deadline_date = "" if ($deadline_date eq "0000-00-00");
  my $deadline_text = (my_defined($deadline_date))?"Please reply by $deadline_date\n":"";
  my $attachement_list = "";
  my @List_attachment = db_select_multiple($dbh,"select file_id,file_title,file_extension from uploads where detail_id=$detail_id");
  if ($#List_attachment < 0) {
    $attachment_list = "No document has been attached";
  } else {
      for my $array_ref (@List_attachment) {
       my ($file_id,$file_title,$file_extension) = @$array_ref;
       $attachment_list .= "     $file_title ($doc_url/file$file_id$file_extension)\n";
     }
  }
  my $purpose_text = ($purpose_id == 5)?"$purpose":db_select($dbh,"select purpose_text from liaison_purpose where purpose_id=$purpose_id");
  $purpose_text = "" unless $purpose_id;
  $cc1 = make_one_per_line($cc1) if my_defined($cc1);
  $response_contact = make_one_per_line($response_contact) if my_defined($response_contact);
  $technical_contact = make_one_per_line($technical_contact) if my_defined($technical_contact);
  my $email_text = qq{
Title: $title
Submission Date: $submitted_date
URL of the IETF Web page: $list_url/liaison_detail.cgi?detail_id=$detail_id 
$deadline_text
From: $from_list
To: $to_body
Cc: $cc1
Reponse Contact: $response_contact
Technical Contact: $technical_contact
Purpose: $purpose_text 
Body: $body
Attachment(s):
$attachment_list

};
#  if (0) {
  if ($devel_mode) {
    ($from_list,$to_body,$cc_list,$subject,$email_text) = html_bracket($from_list,$to_body,$cc_list,$subject,$email_text);
    if ($is_update == 2) {
      $to_body = "statements\@ietf.org";
      $cc_list = "";
    }
#return 1;
    print qq{
<b>Demo version of this tool does NOT actually send the liaison statement to the recipients.<br>
Rather, the actual email body (including mail header) is displayed below.<br>
In production mode, you will not see this screen.</b>
<hr>
<pre>
From: $from_list
Reply-To: $replyto
To: $to_body
Cc: $cc_list
Subject: $subject

$email_text
</pre>
<hr>
$form_header
<input type="submit" name="submit" value="User Main Screen">
</form>
<blockquote>
<a href="$list_url/liaisons.cgi"><img src="/images/blue_dot.gif" border="0">List of liaison statements</a>
<br><br><br><br><br>
      </td></tr>
    </table>
  </td></tr>
</table>
  </body></html>
};
    exit;
  }
  #$cc_list .= ",statements\@ietf.org" unless $devel_mode;
  if ($is_update == 2) {
    $to_poc = "statements\@ietf.org";
    $cc_list = "";
  }
  my $extra="bcc: statements\@ietf.org^reply-to: $replyto";
  $email_text = decode("utf8",$email_text);
  return 1 if $devel_mode;

  return 1 if send_mail("liaison_manager.cgi",$user_name,"$to_poc",$from_list,$subject,$email_text,$cc_list,$extra);

  return 0;
}

sub get_cc_list {
  my $person_or_org_tag=shift;
  my $ret_val = "";
  my $is_wg_chair = ($devel_mode)?0:db_select($dbh,"select count(*) from g_chairs a, groups_ietf b where b.status_id=1 and b.group_acronym_id=a.group_acronym_id and person_or_org_tag=$person_or_org_tag and b.group_type_id=1");
  my $is_iesg = ($devel_mode)?0:db_select($dbh,"select count(*) from iesg_login where user_level=2 and person_or_org_tag=$person_or_org_tag");
  return $ret_val;
}





