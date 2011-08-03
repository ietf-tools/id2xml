#!/usr/bin/perl
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
  $dbname="test_idst";
  $mode_text = "Test Mode";
}
init_database($dbname);


$TESTDB = 0;
$INFORMIX = 1;
$MYSQL = 2;

$is_null = " is NULL ";
$is_not_null = " is NOT NULL ";

my $q = new CGI;
$program_name = "rolodex.cgi";
$modified_by = "INTERNAL WEB PAGE";
$form_begin = qq{<form action="$program_name" method="post">};
if (defined($q->param("option"))) {
   $title = $q->param("option");
   $option = $title;
} else {
   $title = "Main";
}
$title = uc($title);
$error_msg = qq{
<h2>There is a fatal raised while processing your request</h2>
};
$html_head = qq {
<html>
<head>
<title>IETF ROLODEX $title</title>
<STYLE TYPE="text/css">
<!--

	  BODY {text-decoration: none; color: #000000; font: 9pt arial} 
	  TD {text-decoration: none; color: #000000; font: 9pt arial} 
	  TD A:link {text-decoration:none}
      A:link {text-decoration:none}
	  A:Hover {color: #ff0000; text-decoration:underline}
      A:visited {text-decoration:none}
      #menu A {text-decoration: none; color: #2f4f4f; font: 9pt arial} 
      #menu A:Hover {color: "#0000cd"; text-decoration:none}      
      #menu2 A {text-decoration: none; color: #316630; font: 9pt arial} 
      #menu2 A:Hover {color: "#2f4f4f"; text-decoration:underline}  
	  #smallfont {text-decoration: none; color: #000000; font: 10pt arial}
	  #smallfont td {text-decoration: none; color: #000000; font: 10pt arial}
	  #smallerfont {text-decoration: none; color: #000000; font: 8pt arial}
-->
</STYLE>
</head>
<body>
};
$html_bottom = qq {
</body>
</html>
};

if (defined($option)) {
   if ($option eq "search") {
      $html_body = html_search();
   } elsif ($option eq "add") {
      $html_body = html_add();
   } elsif ($option eq "delete") {
      $html_body = html_delete();
   }
   elsif ($option eq "name_search") {
      $fName = $q->param("first_name");
	  $mI = $q->param("middle_initial");
	  $lName = $q->param("last_name");
      $html_body = qq{<center>
<h3>Search Result</h3>
<hr width=400>
	  };
      $html_body .= name_search($fName,$mI,$lName);
	  $html_body .= "</center>";
   }
   elsif ($option eq "tag_search") {
     $tag = $q->param("tag");
	 $html_body = tag_search($tag);
   } 
   elsif ($option eq "email_search") {
     $email=$q->param("email");
     $html_body = email_search($email);
   }
   elsif ($option eq "view") {
     $tag = $q->param("tag");
     $html_body = locate_record($tag);
   }
   elsif ($option eq "modify") {
     $tag = $q->param("tag");
	 if (defined($q->param("name"))) {
	   $html_body = change_name($tag);
	 }
 	 elsif (defined($q->param("address"))) {
	   $html_body = change_address($tag);
	 }
	 elsif (defined($q->param("email"))) {
	   $html_body = change_email($tag);
	 }
	 elsif (defined($q->param("phone"))) {
	   $html_body = change_phone($tag);
	 }
   }
   elsif ($option eq "add_more") {
      $html_body .= add_more($q);
   } elsif ($option eq "add_complete") {
      $html_body .= add_complete($q);
   } elsif ($option eq "delete_complete") {
      $html_body .= delete_complete($q);
   } elsif ($option eq "change_address_complete") {
      $html_body .= change_address_complete($q);
   } elsif ($option eq "add_new_address_complete") {
      $html_body .= add_new_address_complete($q);
   } elsif ($option eq "delete_address_complete") {
      $html_body .= delete_address_complete($q);
   } elsif ($option eq "delete_phone_complete") {
      $html_body .= delete_phone_complete($q);
   } elsif ($option eq "add_new_phone_complete") {
      $html_body .= add_new_phone_complete($q);
   } elsif ($option eq "change_phone_complete") {
      $html_body .= change_phone_complete($q);
   } elsif ($option eq "change_email_complete") {
      $html_body .= change_email_complete($q);
   } elsif ($option eq "delete_email_complete") {
      $html_body .= delete_email_complete($q);
   } elsif ($option eq "add_new_email_complete") {
      $html_body .= add_new_email_complete($q);
   }
   elsif ($option eq "verification") {
      $fName = $q->param("first_name");
	  $mI = $q->param("middle_initial");
	  $lName = $q->param("last_name");
	  $prefix = $q->param("prefix");
	  $suffix = $q->param("suffix");
	  $uF = uc($fName);
	  $uM = uc($mI);
	  $uL = uc($lName);
	  $html_body = "<h3>Adding $prefix $uF $uM $uL $suffix</h3>\n";
	  $html_body .= "<font color=\"red\"><b>Please take a minute to search the list below to prevent creating duplicate record<br></b></font>\n";
	  $fName2 = "";
	  $mI2 = "";
      $html_body .= name_search($fName2,$mI2,$lName);
	  $html_body .= qq{<table>
	  <tr>
	  <form action="$program_name" method="post">
	  <input type="hidden" name="option" value="add">
	  <td><input type="submit" value="Try Again"></td>
	  </form>
	  <form action="$program_name" method="post">
	  <input type="hidden" name="option" value="add_more">
	  <input type="hidden" name="first_name" value="$fName">
	  <input type="hidden" name="middle_initial" value="$mI">
	  <input type="hidden" name="last_name" value="$lName">
	  <input type="hidden" name="prefix" value="$prefix">
	  <input type="hidden" name="suffix" value="$suffix">
	  <td><input type="submit" value="PROCEED"></td>
	  </form>
	  <form action="$program_name" method="post">
	  <td><input type="submit" value="Main Menu"></td>
	  </form>
	  </tr>
	  </table>
	  };
   }
   elsif ($option eq "verification_delete") {
      $fName = $q->param("first_name");
	  $mI = $q->param("middle_initial");
	  $lName = $q->param("last_name");
	  $prefix = $q->param("prefix");
	  $suffix = $q->param("suffix");
	  $uF = uc($fName);
	  $uM = uc($mI);
	  $uL = uc($lName);
	  $html_body = "<h3>Deleting $prefix $uF $uM $uL $suffix</h3>\n";
      $html_body .= name_search($fName,$mI,$lName,1);
	  $html_body .= qq{<table>
	  <tr>
	  <form action="$program_name" method="post">
	  <input type="hidden" name="option" value="delete">
	  <td><input type="submit" value="Try Again"></td>
	  </form>
	  </tr>
	  </table>
	  };
   } elsif ($option eq "verification_update") {
      $html_body = change_name_verification($q);
   }  else {
      $html_body = qq{<META HTTP-EQUIV="Refresh" CONTENT="0; URL=$program_name">};
   }
   $html_body .= display_footer();
}
else {
   $html_body = html_main();
}
print <<END_HTML;
Content-type: text/html
$html_head
$html_body
$html_bottom
END_HTML
##############################
##  Search
############################## 
sub html_search {
   $html_txt = qq{
<center>
<h3>Search</h3>
<hr width=300>
  <form action="$program_name" method="POST">
<table bgcolor="82B5BD" cellpadding="5" cellspacing="0" border=0>
  <tr>
    <td colspan="5" align="right">
      <input type="submit" value="Main Menu">
    </td>
  </tr>
  </form>
  <form action="$program_name" method="POST">
  <input type="hidden" name="option" value="name_search">
  <tr>
    <td>
      <b>Search by Name:</b><br>
      (First) (M.I.) (Last)
    </td>
    <td><input type="text" name="first_name" size="20"></td>
    <td><input type="text" name="middle_initial" size="2"></td>
    <td><input type="text" name="last_name" size="20"></td>
    <td><input type="submit" value="SEARCH" width="15"></td>
  </tr>
  </form>
  <form action="$program_name" method="POST">
  <input type="hidden" name="option" value="email_search">
  <tr>
    <td>
      <b>Search by email:</b>
    </td>
    <td colspan="3"><input type="text" name="email" size="40"></td>
    <td><input type="submit" value="SEARCH" width="15"></td>
  </tr>
  </form>
  <form action="$program_name" method="POST">
  <input type="hidden" name="option" value="tag_search">
  <tr>
    <td>
      <b>Search by tag:</b>
    </td>
    <td colspan="3"><input type="text" name="tag" size="8"></td>
    <td><input type="submit" value="SEARCH" width="15"></td>
  </tr>
</table>
  </form>
</center>
	  };
   return $html_txt;
}
##############################
##  Add
############################## 
sub html_add {
   $html_txt = qq{
<center>
<h3>Add</h3>
<hr width=300>
<table bgcolor="82B5BD" cellpadding="5" cellspacing="0" border=0>
<form action="$program_name" method="POST">
<input type="hidden" name="option" value="verification">
  <tr>
    <td>
      <b>Enter Name:</b>
    </td>
	<td><input type="text" name="prefix" size="5"></td>
    <td><input type="text" name="first_name" size="20"></td>
    <td><input type="text" name="middle_initial" size="2"></td>
    <td><input type="text" name="last_name" size="20"></td>
	<td><input type="text" name="suffix" size="5"></td>
	<td>&nbsp;</td>
  </tr>
  <tr align="center">
    <td>&nbsp;</td>
	<td>(Prefix)</td>
	<td>(First Name)</td>
	<td>(M.I)</td>
	<td>(Last Name)</td>
	<td>(Suffix)</td>
    <td><input type="submit" value="PROCEED" width="15"></td>
  </tr>
</form>
</table>
</center>
	  };
   return $html_txt;
}
##############################
##  Delete
############################## 
sub html_delete {
   $html_txt = qq{
<center>
<h3>Delete</h3>
<hr width=300>
<table bgcolor="82B5BD" cellpadding="5" cellspacing="0" border=0>
<form action="$program_name" method="POST">
<input type="hidden" name="option" value="verification_delete">
  <tr>
    <td>
      <b>Enter Name:</b>
    </td>
	<td><input type="text" name="prefix" size="5"></td>
    <td><input type="text" name="first_name" size="20"></td>
    <td><input type="text" name="middle_initial" size="2"></td>
    <td><input type="text" name="last_name" size="20"></td>
	<td><input type="text" name="suffix" size="5"></td>
	<td>&nbsp;</td>
  </tr>
  <tr align="center">
    <td>&nbsp;</td>
	<td>(Prefix)</td>
	<td>(First Name)</td>
	<td>(M.I)</td>
	<td>(Last Name)</td>
	<td>(Suffix)</td>
    <td><input type="submit" value="PROCEED" width="15"></td>
  </tr>
</form>
</table>
</center>
	  };
   return $html_txt;
}

##############################
##  Main Menu
############################## 
sub html_main {
   $html_txt = qq {
<center><h3>IETF Rolodex Main Menu</h3>
<hr width=300>
<table>
<tr>
<td><form action="$program_name" method="POST">
<input type="hidden" name="option" value="search">
<input type="submit" name="search_b" value="Search" width="100"></form></td>
<td><form action="$program_name" method="POST">
<input type="hidden" name="option" value="add">
<input type="submit" name="add_b" value="Add" width="100"></form></td>
<td><form action="$program_name" method="POST">
<input type="hidden" name="option" value="delete">
<input type="submit" name="delete_b" value="Delete" width="100"></form></td>
</tr></table>
</center>
   };
   return $html_txt;
}

sub display_footer {
   $html_txt = qq{<center>
   <hr width=300>
   <table>
   <tr>
<td><form action="$program_name" method="POST">
<input type="hidden" name="option" value="search">
<input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true" width="100">
<input type="submit" name="search_b" value="Search" width="100"></form></td>
<td><form action="$program_name" method="POST">
<input type="hidden" name="option" value="add">
<input type="submit" name="add_b" value="Add" width="100"></form></td>
<td><form action="$program_name" method="POST">
<input type="hidden" name="option" value="delete">
<input type="submit" name="delete_b" value="Delete" width="100"></form></td>
   </tr>
   </table>
   </center>
   };
   return $html_txt;
}

sub add_more {
      my $q = shift;
	  my $html_txt = "";
      my $fName = $q->param("first_name");
	  my $mI = $q->param("middle_initial");
	  my $lName = $q->param("last_name");
	  my $prefix = $q->param("prefix");
	  my $suffix = $q->param("suffix");
      $html_txt .= "<font color=\"red\"><b>Add email and Phone Number Here</b></font>\n";
	  $html_txt .= "<h3>$prefix $fName $mI $lName $suffix</h3>";
	  $html_txt .= qq{<table>
	  $form_begin
	  <input type="hidden" name="phone_priority" value="1">
	  <input type="hidden" name="email_priority" value="1">
	  <input type="hidden" name="address_priority" value="1">
	  <tr bgcolor="9FD9A8"><td>Phone Type:</td><td>
	  <input type="radio" name="phone_type" value="W" checked>Work
	  <input type="radio" name="phone_type" value="H">Home
	  <input type="radio" name="phone_type" value="WF">Work Fax
	  <input type="radio" name="phone_type" value="HF">Home Fax
	  </td></tr>
	  <tr bgcolor="9FD9A8"><td>Enter Phone Number:</td><td><input type="text" name="phone_number"></td></tr>
	  <tr bgcolor="9FD9A8"><td>Enter Phone Comment:</td><td><input type="text" name="phone_comment"></td></tr>
	  <tr bgcolor="EAB4F5"><td>Email Type</td><td>
	  <input type="radio" name="email_type" value="INET" checked>Internet Style
	  <input type="radio" name="email_type" value="MCI">MCI Mail Style
	  <input type="radio" name="email_type" value="ULST">Unknown
	  </td></tr>
	  <tr bgcolor="EAB4F5"><td>Enter Email Address</td><td><input type="text" name="email_address" size="30"></td></tr>
	  <tr bgcolor="EAB4F5"><td>Enter Email Comment</td><td><input type="text" name="email_comment" size="30"></td></tr>
	  <tr bgcolor="B4B8EF"><td>Address Type</td><td>
	  <input type="radio" name="address_type" value="W" checked>Work
	  <input type="radio" name="address_type" value="H">Home
	  </td></tr>
	  <tr bgcolor="B4B8EF"><td>Title:</td><td><input type="text" name="person_title"></td></tr>
	  <tr bgcolor="B4B8EF"><td>Company name:</td><td><input type="text" name="affiliated_company" size="50"></td></tr>
	  <tr  bgcolor="B4B8EF"><td>Department:</td><td><input type="text" name="department"></td></tr>
	  <tr  bgcolor="B4B8EF"><td>Mail Stop:</td><td><input type="text" name="mail_stop"></td></tr>
	  <tr bgcolor="B4B8EF"><td>Street Address 1:</td><td><input type="text" name="staddr1"></td></tr>
	  <tr bgcolor="B4B8EF"><td>Street Address 2:</td><td><input type="text" name="staddr2"></td></tr>
	  <tr  bgcolor="B4B8EF"><td>City, State(Prov), Postal Code:</td><td><input type="text" name="city">
	  <input type="text" name="state_or_prov" size="15">
	  <input type="text" name="postal_code" size="12"></td></tr>
	  <tr bgcolor="B4B8EF"><td>Country:</td><td><input type="text" name="country"></td></tr>
	  </table>
	  };
	  $html_txt .= qq{<table>
	  <tr>
	  <input type="hidden" name="option" value="add_complete">
	  <input type="hidden" name="first_name" value="$fName">
	  <input type="hidden" name="middle_initial" value="$mI">
	  <input type="hidden" name="last_name" value="$lName">
	  <input type="hidden" name="prefix" value="$prefix">
	  <input type="hidden" name="suffix" value="$suffix">
	  <td><input type="submit" value="COMPLETE"></td>
	  </form>
	  $form_begin
 	  <td><input type="submit" value="CANCEL"></td>
	  </form>
	  </tr>
	  </table>
	  };
   return $html_txt;
}

sub add_complete {
 my $html_txt = "New Record Added";
 my $q = shift;
 my $first_name_key = uc($q->param("first_name"));
 my $last_name_key = uc($q->param("last_name"));
 my $middle_initial_key = uc($q->param("middle_initial"));
 my $email_type = $q->param("email_type");
 my $email_priority = $q->param("email_priority");
 my $email_address = $q->param("email_address");
 my $phone_type = $q->param("phone_type");
 my $phone_priority = $q->param("phone_priority");
 my $phone_number = $q->param("phone_number");
 my $address_type = $q->param("address_type");
 my $person_title = $q->param("person_title");
 my $affiliated_company = $q->param("affiliated_company");
 my $department = $q->param("department");
 my $staddr1 = $q->param("staddr1");
 my $staddr2 = $q->param("staddr2");
 my $city = $q->param("city");
 my $state_or_prov = $q->param("state_or_prov");
 my $postal_code = $q->param("postal_code");
 my $country = $q->param("country");
 my $mail_stop = $q->param("mail_stop");
 my $address_priority = $q->param("address_priority");
 my $email_comment = $q->param("email_comment");
 my $phone_comment = $q->param("phone_comment");

 ($first_name,$last_name,$middle_initial,$prefix,$suffix,$first_name_key,$last_name_key,$middle_initial_key,$modified_here) = 
   db_quote($q->param("first_name"),$q->param("last_name"),$q->param("middle_initial"),$q->param("prefix"),$q->param("suffix"),$first_name_key,$last_name_key,$middle_initial_key,$modified_by);
 my $sqlStr = qq {
 insert into person_or_org_info (first_name,last_name,middle_initial,name_prefix,name_suffix,first_name_key,last_name_key,middle_initial_key,date_modified,modified_by,date_created)
 values ($first_name,$last_name,$middle_initial,$prefix,$suffix,$first_name_key,$last_name_key,$middle_initial_key,CURRENT_DATE,$modified_here,CURRENT_DATE)
 };
#return $sqlStr; 
return $error_msg unless db_update($sqlStr);

 $sqlStr = "select max(person_or_org_tag) from person_or_org_info";
 $person_or_org_tag = db_select($sqlStr);
 
 $sqlStr = qq {
 insert into print_name (person_or_org_tag,firstname,lastname) values ($person_or_org_tag,$first_name,$last_name)
 };
 return $error_msg unless db_update($sqlStr);
 if (my_defined($email_address)) {
    ($email_type,$email_address,$email_comment) = db_quote($email_type,$email_address,$email_comment);
    $sqlStr = qq {insert into email_addresses (person_or_org_tag,email_type,email_priority,email_address,email_comment)
    values ($person_or_org_tag,$email_type,$email_priority,$email_address,$email_comment)
    };
	#$html_txt .= "$sqlStr \n <br> \n";
    return $error_msg unless db_update($sqlStr);
 }
 if (my_defined($phone_number)) {
    ($phone_type,$phone_number,$phone_comment) = db_quote($phone_type,$phone_number,$phone_comment);
    $sqlStr = qq {insert into phone_numbers (person_or_org_tag,phone_type,phone_priority,phone_number,phone_comment)
    values ($person_or_org_tag,$phone_type,$phone_priority,$phone_number,$phone_comment)
    };
	#$html_txt .= "$sqlStr \n <br> \n";
    return $error_msg unless db_update($sqlStr);
 }
 if (my_defined($affiliated_company) or my_defined($city)) {
    my $aff_company_key = uc($affiliated_company);
   ($address_type,$person_title,$affiliated_company,$aff_company_key,$department,$staddr1,$staddr2,$mail_stop,$city,$state_or_prov,$postal_code,$country) =
   db_quote($address_type,$person_title,$affiliated_company,$aff_company_key,$department,$staddr1,$staddr2,$mail_stop,$city,$state_or_prov,$postal_code,$country);  
   $sqlStr = qq {insert into postal_addresses 
   (person_or_org_tag,address_type,address_priority,person_title,
   affiliated_company,aff_company_key,department,staddr1,staddr2,
   mail_stop,city,state_or_prov,postal_code,country)
   values ($person_or_org_tag,$address_type,$address_priority,
   $person_title,$affiliated_company,$aff_company_key,$department,
   $staddr1,$staddr2,
   $mail_stop,$city,$state_or_prov,$postal_code,$country)
   };
	#$html_txt .= "$sqlStr \n <br> \n";
    return $error_msg unless db_update($sqlStr);
	$sqlStr = qq { Update person_or_org_info
	set address_type = $address_type
	where person_or_org_tag = $person_or_org_tag
	};
	return $error_msg unless db_update($sqlStr);
 }
 return $html_txt;
}

sub delete_complete {
  my $html_txt = "Record Deleted";
  my $q = shift;
  my $tag = $q->param("tag");
  my $sqlStr = "delete from person_or_org_info where person_or_org_tag = $tag";
  return $error_msg unless db_update($sqlStr);
  $sqlStr = "delete from email_addresses where person_or_org_tag = $tag";
  return $error_msg unless db_update($sqlStr);
  $sqlStr = "delete from postal_addresses where person_or_org_tag = $tag";
  return $error_msg unless db_update($sqlStr);
  $sqlStr = "delete from phone_numbers where person_or_org_tag = $tag";
  return $error_msg unless db_update($sqlStr);
  
  
  $sqlStr = "delete from g_chairs where person_or_org_tag = $tag";
  return $error_msg unless db_update($sqlStr);
  $sqlStr = "delete from area_directors where person_or_org_tag = $tag";
  return $error_msg unless db_update($sqlStr);
  $sqlStr = "delete from print_name where person_or_org_tag = $tag";
  return $error_msg unless db_update($sqlStr);
  return $html_txt;
}

sub change_name {
   my $tag = shift;
   $sqlStr = "Select name_prefix,first_name,middle_initial,last_name,name_suffix from person_or_org_info where person_or_org_tag = $tag";
   my ($name_prefix,$first_name,$middle_initial,$last_name,$name_suffix) = db_select($sqlStr);
   my $html_txt = qq{
<center>
<h3>Changing Name</h3>
<hr width=300>
<table bgcolor="82B5BD" cellpadding="5" cellspacing="0" border=0>
$form_begin
<input type="hidden" name="option" value="verification_update">
<input type="hidden" name="tag" value="$tag">
  <tr>
    <td>
      <b>Change Name:</b>
    </td>
	<td><input type="text" name="prefix" size="5" value="$name_prefix"></td>
    <td><input type="text" name="first_name" size="20" value="$first_name"></td>
    <td><input type="text" name="middle_initial" size="2" value="$middle_initial"></td>
    <td><input type="text" name="last_name" size="20" value="$last_name"></td>
	<td><input type="text" name="suffix" size="5" value="$name_suffix"></td>
	<td>&nbsp;</td>
  </tr>
  <tr align="center">
    <td>&nbsp;</td>
	<td>(Prefix)</td>
	<td>(First Name)</td>
	<td>(M.I)</td>
	<td>(Last Name)</td>
	<td>(Suffix)</td>
    <td><input type="submit" value="PROCEED" width="15"></td>
  </tr>
</form>
</table>
</center>
	  };
   
   return $html_txt;
}

sub change_name_verification {
   my $q = shift;
   my $html_txt = "Name has been changed";
   my $tag = $q->param("tag");
   my $first_name = rm_tr($q->param("first_name"));
   my $middle_initial = rm_tr($q->param("middle_initial"));
   my $last_name = rm_tr($q->param("last_name"));
   my $name_prefix = $q->param("name_prefix");
   my $name_suffix = $q->param("name_suffix");
   my $first_name_key = uc($first_name);
   my $last_name_key = uc($last_name);
   my $middle_initial_key = uc($middle_initial);
   my $error_msg = "$first_name $middle_initial $last_name is already existed in the database.";
   my $button_msg = "I still want to change the name to $first_name $middle_initial $last_name";
   my $hidden_values = qq{
	  <input type="hidden" name="prefix"  value="$name_prefix">
      <input type="hidden" name="first_name"  value="$first_name">
      <input type="hidden" name="middle_initial" value="$middle_initial">
      <input type="hidden" name="last_name" value="$last_name">
	  <input type="hidden" name="suffix"  value="$name_suffix">
	  <input type="hidden" name="tag" value="$tag">
   };   
   ($first_name,$middle_initial,$last_name,$name_prefix,$name_suffix,$first_name_key,$last_name_key,$middle_initial_key) = 
   db_quote($first_name,$middle_initial,$last_name,$name_prefix,$name_suffix,$first_name_key,$last_name_key,$middle_initial_key);
   my $update_sqlStr = qq {
      update person_or_org_info
	     Set name_prefix = $name_prefix,
		     name_suffix = $name_suffix,
			 first_name = $first_name,
			 first_name_key = $first_name_key,
			 middle_initial = $middle_initial,
			 middle_initial_key = $middle_initial_key,
			 last_name = $last_name,
			 last_name_key = $last_name_key
	  where person_or_org_tag = $tag
   };
   my $update_print_name_sqlStr = qq {
      update print_name
	     set firstname = $first_name,
		     lastname = $last_name
		 where person_or_org_tag = $tag
   };
   if (defined($q->param("force_update"))) {
      return $error_msg unless db_update($update_sqlStr);
      return $html_txt;
   }
   $sqlStr = qq { select count(*) from person_or_org_info
   where first_name = $first_name AND
   last_name = $last_name AND
   middle_initial = $middle_initial
   };
   my $rec_count = db_select($sqlStr);
   if ($rec_count > 0) {
      $html_txt = qq {$error_msg <br>
	  $form_begin
	  <input type="hidden" name="option" value="verification_update">
	  <input type="hidden" name="force_update" value="yes">
	  $hidden_values
	  <input type="submit" value="$button_msg">
	  </form>
	  };
   } else {
      return $error_msg unless db_update($update_sqlStr);
	  return $error_msg unless db_update($update_print_name_sqlStr);
   }
   return $html_txt;
}

sub change_address {
   my $tag = shift;
   my $html_txt = "changing address <br>";
   $sqlStr = "select address_priority, address_type, person_title, affiliated_company, department, mail_stop, staddr1, staddr2, city, state_or_prov, postal_code, country from postal_addresses where person_or_org_tag = $tag order by 1";
   my $count = 0;
   my @nList = db_select_multiple($sqlStr);
   for $array_ref ( @nList ) {
      my ($address_priority,$address_type, $person_title, $affiliated_company, $department, $mail_stop, $staddr1, $staddr2, $city, $state_or_prov, $postal_code, $country) = @$array_ref;
      $count++;
      my $w_checked = "";
      my $h_checked = "";
      my $primary_str = "";
      if ($address_priority == 1) {
         $primary_str = "<b>Primiary</b>";
      }
      if (rm_tr($address_type) eq "W") {
         $w_checked = "checked";
      } else {
         $h_checked = "checked";
      }
      $html_txt .= qq {
      <b>Change an Address</b>
      <table>
      $form_begin
 	  <input type="hidden" name="option" value="change_address_complete">
	  <input type="hidden" name="person_or_org_tag" value="$tag">
	  <input type="hidden" name="address_priority" value="$address_priority">
	  <tr bgcolor="B4B8EF"><td>Address Type</td><td>
	  <input type="radio" name="address_type" value="W" $w_checked>Work
	  <input type="radio" name="address_type" value="H" $h_checked>Home
	  &nbsp;$primary_str
	  </td></tr>
	  <tr bgcolor="B4B8EF"><td>Title:</td><td><input type="text" name="person_title" value="$person_title"></td></tr>
	  <tr bgcolor="B4B8EF"><td>Company name:</td><td><input type="text" name="affiliated_company" size="50" value="$affiliated_company"></td></tr>
	  <tr  bgcolor="B4B8EF"><td>Department:</td><td><input type="text" name="department" value="$department"></td></tr>
	  <tr  bgcolor="B4B8EF"><td>Mail Stop:</td><td><input type="text" name="mail_stop" value="$mail_stop"></td></tr>
	  <tr bgcolor="B4B8EF"><td>Street Address 1:</td><td><input type="text" name="staddr1" value="$staddr1"></td></tr>
	  <tr bgcolor="B4B8EF"><td>Street Address 2:</td><td><input type="text" name="staddr2" value="$staddr2"></td></tr>
	  <tr  bgcolor="B4B8EF"><td>City, State(Prov), Postal Code:</td><td><input type="text" name="city" value="$city">
	  <input type="text" name="state_or_prov" size="15" value="$state_or_prov">
	  <input type="text" name="postal_code" size="12" value="$postal_code"></td></tr>
	  <tr bgcolor="B4B8EF"><td>Country:</td><td><input type="text" name="country" value="$country"></td></tr>
  	  <tr><td align="right"><input type="submit" value="UPDATE"></td></form>
	  $form_begin
	  <input type="hidden" name="option" value="delete_address_complete">
	  <input type="hidden" name="person_or_org_tag" value="$tag">
	  <input type="hidden" name="address_priority" value="$address_priority">
	  <td><input type="submit" value="DELETE"
	  onClick="return window.confirm('This address will be permanently removed from Database');"></td></tr>
	  </form>
	  </table>
	  };
   }
   $count++;
      $html_txt .= qq {
      <b>Add an Address</b>
      <table>
	  $form_begin
	  <input type="hidden" name="option" value="add_new_address_complete">
	  <input type="hidden" name="address_priority" value="$count">
	  <input type="hidden" name="person_or_org_tag" value="$tag">
	  <tr bgcolor="93EAAF"><td>Address Type</td><td>
	  <input type="radio" name="address_type" value="W" checked>Work
	  <input type="radio" name="address_type" value="H">Home
	  </td></tr>
	  <tr bgcolor="93EAAF"><td>Title:</td><td><input type="text" name="person_title"></td></tr>
	  <tr bgcolor="93EAAF"><td>Company name:</td><td><input type="text" name="affiliated_company" size="50"></td></tr>
	  <tr  bgcolor="93EAAF"><td>Department:</td><td><input type="text" name="department"></td></tr>
	  <tr  bgcolor="93EAAF"><td>Mail Stop:</td><td><input type="text" name="mail_stop"></td></tr>
	  <tr bgcolor="93EAAF"><td>Street Address 1:</td><td><input type="text" name="staddr1"></td></tr>
	  <tr bgcolor="93EAAF"><td>Street Address 2:</td><td><input type="text" name="staddr2"></td></tr>
	  <tr  bgcolor="93EAAF"><td>City, State(Prov), Postal Code:</td><td><input type="text" name="city">
	  <input type="text" name="state_or_prov" size="15">
	  <input type="text" name="postal_code" size="12"></td></tr>
	  <tr bgcolor="93EAAF"><td>Country:</td><td><input type="text" name="country"></td></tr>
	  <tr><td colspan="2"><input type="submit" value="Add This Address"></td></tr>
	  </form>
	  </table>
	  };
   return $html_txt;
}

sub change_email {
   my $tag = shift;
   my $html_txt = "changing email";
   $sqlStr = "select email_priority, email_type, email_address, email_comment from email_addresses where person_or_org_tag = $tag order by 1";
   my $count = 0;
   my @nList = db_select_multiple($sqlStr);
   my $new_email_priority = db_select("select max(email_priority) from email_addresses where person_or_org_tag=$tag and email_priority < 100"); 
   $new_email_priority++;
   for $array_ref ( @nList ) {
      $count++;
      my ($email_priority, $email_type, $email_address, $email_comment) = @$array_ref;
	  my $inet_checked = "";
	  my $mci_checked = "";
	  my $ulst_checked = "";
	  my $primary_str = "";
      if ($email_priority == 1) {
         $primary_str = "<b>Primiary</b>";
      }
	  if (rm_tr($email_type) eq "INET") {
	     $inet_checked = "checked";
	  }
	  if (rm_tr($email_type) eq "MCI") {
	     $mci_checked = "checked";
	  }
	  if (rm_tr($email_type) eq "ULST") {
	     $ulst_checked = "checked";
	  }
	  $html_txt .= qq{<table>
          <form action="$program_name" method="post" name="form_$count">
	  <input type="hidden" name="email_priority" value="$email_priority">
 	  <input type="hidden" name="option" value="change_email_complete">
	  <input type="hidden" name="person_or_org_tag" value="$tag">
	  <tr bgcolor="B4B8EF"><td>Email Type:</td><td>
	  <input type="radio" name="email_type" value="INET" $inet_checked>Internet Style
	  <input type="radio" name="email_type" value="MCI" $mci_checked>MCI Mail Style
	  <input type="radio" name="email_type" value="ULST" $ulst_checked>Unknown
	  &nbsp; $primary_str
	  </td></tr>
	  <tr bgcolor="B4B8EF"><td>Enter Email Address:</td><td><input type="text" name="email_address" value="$email_address"></td></tr>
	  <tr bgcolor="B4B8EF"><td>Enter Email Comment:</td><td><input type="text" name="email_comment" value="$email_comment"></td></tr>
	  <tr><td><input type="submit" value="UPDATE" onClick="if(document.form_$count.email_address.value == '')  {window.alert('Email address can not be blank');document.form_$count.email_address.focus();return false;}"></td>
	  </form>
	  $form_begin
	  <input type="hidden" name="option" value="delete_email_complete">
	  <input type="hidden" name="person_or_org_tag" value="$tag">
	  <input type="hidden" name="email_priority" value="$email_priority">
	  <td><input type="submit" value="DELETE"
	  onClick="return window.confirm('This email address will be permanently removed from Database');"></td></tr>
	  </form>
	  </table>
	  };
   }
   $count++;
      $html_txt .= qq {
      <b>Add an Email Address</b>
      <table>
	  $form_begin
	  <input type="hidden" name="email_priority" value="$new_email_priority">
 	  <input type="hidden" name="option" value="add_new_email_complete">
	  <input type="hidden" name="person_or_org_tag" value="$tag">
	  <tr bgcolor="9FD9A8"><td>Email Type:</td><td>
	  <input type="radio" name="email_type" value="INET" checked>Internet Style
	  <input type="radio" name="email_type" value="MCI">MCI Mail Style
	  <input type="radio" name="email_type" value="ULST">Unknown
	  </td></tr>
	  <tr bgcolor="9FD9A8"><td>Enter Email Address:</td><td><input type="text" name="email_address" value="$email_address"></td></tr>
	  <tr bgcolor="9FD9A8"><td>Enter Email Comment:</td><td><input type="text" name="email_comment" value="$email_comment"></td></tr>
	  <tr><td colspan="2"><input type="submit" value="Add This Email Address"></td></tr>
	  </form>
	  </table>
	  };
   return $html_txt;
}

sub change_phone {
   my $tag = shift;
   my $html_txt = "changing phone";
   $sqlStr = "select phone_priority, phone_type, phone_number, phone_comment from phone_numbers where person_or_org_tag = $tag order by 1";
   my $count = 0;
   my @nList = db_select_multiple($sqlStr);
   
   for $array_ref ( @nList ) {
      $count++;
      my ($phone_priority, $phone_type, $phone_number, $phone_comment) = @$array_ref;
	  my $w_checked = "";
	  my $h_checked = "";
	  my $wf_checked = "";
	  my $hf_checked = "";
	  my $primary_str = "";
      if ($phone_priority == 1) {
         $primary_str = "<b>Primiary</b>";
      }
	  if (rm_tr($phone_type) eq "W") {
	     $w_checked = "checked";
	  }
	  if (rm_tr($phone_type) eq "WF") {
	     $wf_checked = "checked";
	  }
	  if (rm_tr($phone_type) eq "H") {
	     $h_checked = "checked";
	  }
	  if (rm_tr($phone_type) eq "HF") {
	     $hf_checked = "checked";
	  }
	  $html_txt .= qq{<table>
          <form action="$program_name" method="post" name="form_$count">
	  <input type="hidden" name="phone_priority" value="$phone_priority">
 	  <input type="hidden" name="option" value="change_phone_complete">
	  <input type="hidden" name="person_or_org_tag" value="$tag">
	  <tr bgcolor="B4B8EF"><td>Phone Type:</td><td>
	  <input type="radio" name="phone_type" value="W" $w_checked>Work
	  <input type="radio" name="phone_type" value="H" $h_checked>Home
	  <input type="radio" name="phone_type" value="WF" $wf_checked>Work Fax
	  <input type="radio" name="phone_type" value="HF" $hf_checked>Home Fax
	  &nbsp; $primary_str
	  </td></tr>
	  <tr bgcolor="B4B8EF"><td>Enter Phone Number:</td><td><input type="text" name="phone_number" value="$phone_number"></td></tr>
	  <tr bgcolor="B4B8EF"><td>Enter Phone Comment:</td><td><input type="text" name="phone_comment" value="$phone_comment"></td></tr>
	  <tr><td><input type="submit" value="UPDATE"
          onClick="if (document.form_$count.phone_number.value == '') {window.alert('Phone number can not be blank');document.form_$count.phone_number.focus();return false;}"></td>
	  </form>
	  $form_begin
	  <input type="hidden" name="option" value="delete_phone_complete">
	  <input type="hidden" name="person_or_org_tag" value="$tag">
	  <input type="hidden" name="phone_priority" value="$phone_priority">
	  <td><input type="submit" value="DELETE"
	  onClick="return window.confirm('This phone number will be permanently removed from Database');"></td></tr>
	  </form>
	  </table>
	  };
   }
   $count++;
      $html_txt .= qq {
      <b>Add a Phone Number</b>
      <table>
	  $form_begin
	  <input type="hidden" name="option" value="add_new_phone_complete">
	  <input type="hidden" name="phone_priority" value="$count">
	  <input type="hidden" name="person_or_org_tag" value="$tag">
	  <tr bgcolor="9FD9A8"><td>Phone Type:</td><td>
	  <input type="radio" name="phone_type" value="W" checked>Work
	  <input type="radio" name="phone_type" value="H">Home
	  <input type="radio" name="phone_type" value="WF">Work Fax
	  <input type="radio" name="phone_type" value="HF">Home Fax
	  </td></tr>
	  <tr bgcolor="9FD9A8"><td>Enter Phone Number:</td><td><input type="text" name="phone_number"></td></tr>
	  <tr bgcolor="9FD9A8"><td>Enter Phone Comment:</td><td><input type="text" name="phone_comment"></td></tr>
	  <tr><td colspan="2"><input type="submit" value="Add This Phone Number"></td></tr>
	  </form>
	  </table>
	  };
   
   return $html_txt;
}


sub add_new_address_complete {
   my $q = shift;
   my $html_txt = "New Address added";
 my $address_type = $q->param("address_type");
 my $address_priority = $q->param("address_priority");
 my $person_or_org_tag = $q->param("person_or_org_tag");
 my $person_title = $q->param("person_title");
 my $affiliated_company = $q->param("affiliated_company");
 my $aff_company_key = uc($affiliated_company);
 my $department = $q->param("department");
 my $staddr1 = $q->param("staddr1");
 my $staddr2 = $q->param("staddr2");
 my $mail_stop = $q->param("mail_stop");
 my $city = $q->param("city");
 my $state_or_prov = $q->param("state_or_prov");
 my $postal_code = $q->param("postal_code");
 my $country = $q->param("country");
   ($address_type,$person_title,$affiliated_company,$aff_company_key,$department,$staddr1,$staddr2,$mail_stop,$city,$state_or_prov,$postal_code,$country) =
   db_quote($address_type,$person_title,$affiliated_company,$aff_company_key,$department,$staddr1,$staddr2,$mail_stop,$city,$state_or_prov,$postal_code,$country);  
   $sqlStr = qq {insert into postal_addresses 
   (person_or_org_tag,address_type,address_priority,person_title,
   affiliated_company,aff_company_key,department,staddr1,staddr2,
   mail_stop,city,state_or_prov,postal_code,country)
   values ($person_or_org_tag,$address_type,$address_priority,
   $person_title,$affiliated_company,$aff_company_key,$department,
   $staddr1,$staddr2,
   $mail_stop,$city,$state_or_prov,$postal_code,$country)
   };
	#$html_txt .= "$sqlStr \n <br> \n";
    return $error_msg unless db_update($sqlStr);
   $html_txt = locate_record($person_or_org_tag);
   return $html_txt;
}

sub change_address_complete {
   my $q = shift;
   my $html_txt = "Phone Number changed";
 my $address_type = $q->param("address_type");
 my $address_priority = $q->param("address_priority");
 my $person_or_org_tag = $q->param("person_or_org_tag");
 my $person_title = $q->param("person_title");
 my $affiliated_company = $q->param("affiliated_company");
 my $aff_company_key = uc($affiliated_company);
 my $department = $q->param("department");
 my $staddr1 = $q->param("staddr1");
 my $staddr2 = $q->param("staddr2");
 my $mail_stop = $q->param("mail_stop");
 my $city = $q->param("city");
 my $state_or_prov = $q->param("state_or_prov");
 my $postal_code = $q->param("postal_code");
 my $country = $q->param("country");
   ($address_type,$person_title,$affiliated_company,$aff_company_key,$department,$staddr1,$staddr2,$mail_stop,$city,$state_or_prov,$postal_code,$country) =
   db_quote($address_type,$person_title,$affiliated_company,$aff_company_key,$department,$staddr1,$staddr2,$mail_stop,$city,$state_or_prov,$postal_code,$country);  
 $sqlStr = qq {
   Update postal_addresses
   Set address_type = $address_type,
       person_title = $person_title,
	   affiliated_company = $affiliated_company,
	   aff_company_key = $aff_company_key,
	   department = $department,
	   staddr1 = $staddr1,
	   staddr2 = $staddr2,
	   mail_stop = $mail_stop,
	   city = $city,
	   state_or_prov = $state_or_prov,
	   postal_code = $postal_code,
	   country = $country
   Where person_or_org_tag = $person_or_org_tag AND address_priority = $address_priority
   };
   #return $sqlStr;
   return $error_msg unless db_update($sqlStr);
    $html_txt = locate_record($person_or_org_tag);
  return $html_txt;
}

sub delete_address_complete {
   my $q = shift;
   my $html_txt = "Postal Address Deleted";
   my $person_or_org_tag = $q->param("person_or_org_tag");
   my $address_priority = $q->param("address_priority");
   $sqlStr = "Delete from postal_addresses where person_or_org_tag = $person_or_org_tag AND address_priority = $address_priority";
   return $error_msg unless db_update($sqlStr);
   $html_txt = locate_record($person_or_org_tag);
   return $html_txt;
}

sub add_new_phone_complete {
   my $q = shift;
   my $html_txt = "Phone Number added";
 my $phone_type = $q->param("phone_type");
 my $phone_number = $q->param("phone_number");
 my $phone_comment =$q->param("phone_comment");
 my $phone_priority = $q->param("phone_priority");
 my $person_or_org_tag = $q->param("person_or_org_tag");
($phone_type,$phone_number,$phone_comment) =
   db_quote($phone_type,$phone_number,$phone_comment);  
   $sqlStr = qq {insert into phone_numbers
   (person_or_org_tag,phone_type,phone_priority,phone_number,phone_comment)
   values ($person_or_org_tag,$phone_type,$phone_priority,$phone_number,$phone_comment)
   };
	#$html_txt .= "$sqlStr \n <br> \n";
    return $error_msg unless db_update($sqlStr);
   $html_txt = locate_record($person_or_org_tag);
   return $html_txt;
}

sub change_phone_complete {
   my $q = shift;
 my $phone_type = $q->param("phone_type");
 my $phone_number = $q->param("phone_number");
 my $phone_comment =$q->param("phone_comment");
 my $phone_priority = $q->param("phone_priority");
 my $person_or_org_tag = $q->param("person_or_org_tag");
 ($phone_type,$phone_number,$phone_comment) =
   db_quote($phone_type,$phone_number,$phone_comment);  
 $sqlStr = qq {
   Update phone_numbers
   Set phone_type = $phone_type,
       phone_number = $phone_number,
	   phone_comment = $phone_comment
   Where person_or_org_tag = $person_or_org_tag AND phone_priority = $phone_priority
   };
   return $error_msg unless db_update($sqlStr);
   my $html_txt = locate_record($person_or_org_tag);
   return $html_txt;
}

sub delete_phone_complete {
   my $q = shift;
   my $html_txt = "Phone Number Deleted";
   my $person_or_org_tag = $q->param("person_or_org_tag");
   my $phone_priority = $q->param("phone_priority");
   $sqlStr = "Delete from phone_numbers where person_or_org_tag = $person_or_org_tag AND phone_priority = $phone_priority";
   return $error_msg unless db_update($sqlStr);
   $html_txt = locate_record($person_or_org_tag);
   return $html_txt;
}



sub add_new_email_complete {
   my $q = shift;
   my $html_txt = "Email Address added";
 my $email_type = $q->param("email_type");
 my $email_address = $q->param("email_address");
 my $email_comment =$q->param("email_comment");
 my $email_priority = $q->param("email_priority");
 my $person_or_org_tag = $q->param("person_or_org_tag");
($email_type,$email_address,$email_comment) =
   db_quote($email_type,$email_address,$email_comment);  
   $sqlStr = qq {insert into email_addresses
   (person_or_org_tag,email_type,email_priority,email_address,email_comment)
   values ($person_or_org_tag,$email_type,$email_priority,$email_address,$email_comment)
   };
  # return $sqlStr;
    return $error_msg unless db_update($sqlStr);
   $html_txt = locate_record($person_or_org_tag);
   return $html_txt;
}

sub change_email_complete {
   my $q = shift;
   my $html_txt = "Email Address changed";
 my $email_type = $q->param("email_type");
 my $email_address = $q->param("email_address");
 my $email_comment =$q->param("email_comment");
 my $email_priority = $q->param("email_priority");
 my $person_or_org_tag = $q->param("person_or_org_tag");
($email_type,$email_address,$email_comment) =
   db_quote($email_type,$email_address,$email_comment);  
 $sqlStr = qq {
   Update email_addresses
   Set email_type = $email_type,
       email_address = $email_address,
	   email_comment = $email_comment
   Where person_or_org_tag = $person_or_org_tag AND email_priority = $email_priority
   };
   return $error_msg unless db_update($sqlStr);
   $html_txt = locate_record($person_or_org_tag);
   return $html_txt;
}

sub delete_email_complete {
   my $q = shift;
   my $html_txt = "Email Address Deleted";
   my $person_or_org_tag = $q->param("person_or_org_tag");
   my $email_priority = $q->param("email_priority");
   $sqlStr = "Delete from email_addresses where person_or_org_tag = $person_or_org_tag AND email_priority = $email_priority";
   return $error_msg unless db_update($sqlStr);
   $html_txt = locate_record($person_or_org_tag);
   return $html_txt;
}

sub name_search {
   my ($fName,$mI,$lName,$delete_key) = @_;
   $html_txt = "";
   $sqlStr = qq {
SELECT a.person_or_org_tag, a.first_name,a.last_name,b.affiliated_company
from person_or_org_info a 
left outer join postal_addresses b on 
(a.person_or_org_tag = b.person_or_org_tag AND a.address_type = b.address_type)
WHERE 1 = 1
};
   unless ($fName eq "") {
      $uFirstName = uc($fName);
      $uFirstName =~ s/'/''/g;
      $sqlStr .= qq{AND first_name_key LIKE '$uFirstName%'\n};
   }
   unless ($mI eq "") {
      $uMI = uc ($mI);
      $sqlStr .= qq{AND middle_initial_key LIKE '$uMI%'\n};
   }
   unless ($lName eq "") {
      $uLastName = uc($lName);
      $uLastName =~ s/'/''/g;
	  
      $sqlStr .= qq{AND last_name_key LIKE '$uLastName%'\n};
   } 
   $sqlStr .= "ORDER BY a.last_name,a.first_name\n";
   my @nList;
   my @List = db_select_multiple($sqlStr);
   for $array_ref (@List) {
      my @row = @$array_ref;
      push @nList, [ @row ];
   }
   if ($#nList == -1) {
      $html_txt = "No record found";
   }
   else {
      $count = 0;
      $html_txt .= qq{<table><tr bgcolor="aqua">
	  <td><b>Name</b></td><td><b>Company Name</b></td><td><b>Tag</b></td>
	  </tr>
	  };
      for $array_ref ( @nList ) {
	    ($tag,$fName,$lName,$cName) = @$array_ref;
		$html_txt .= "<tr>\n";
		$html_txt .= qq{<td><a href="$program_name?option=view&tag=$tag">$fName $lName</a></td><td>$cName</td><td>$tag</td>};
		if (defined($delete_key)) {
		   $fName = rm_tr($fName);
		   $lName = rm_tr($lName);
		   $html_txt .= qq {
		   $form_begin
		   <input type="hidden" name="option" value="delete_complete">
		   <input type="hidden" name="tag" value="$tag">
		   <td><input type="submit" value="delete" 
		   onClick="return window.confirm('$fName $lName will be permanently removed from Database');"></td>
		   </form>
		   };
		}
		$html_txt .= "</tr>\n";
	  }
	  $html_txt .= "</table>\n";
   }
   return $html_txt;
}

sub tag_search {
   $tag = shift;
   $html_txt = qq{<center>
<h3>Search Result</h3>
<hr width=400>
};
   $sqlStr = "SELECT a.person_or_org_tag,a.first_name,a.last_name";
   $sqlStr .= ",b.affiliated_company \n";
   $sqlStr .= "from person_or_org_info a,outer postal_addresses b";
   $sqlStr .= "\nWHERE a.person_or_org_tag = $tag\n";
   $sqlStr .= "AND a.person_or_org_tag = b.person_or_org_tag\n";
   $sqlStr .= "AND a.address_type = b.address_type\n";
   $sqlStr = qq {
SELECT a.person_or_org_tag,a.first_name,a.last_name,b.affiliated_company
from person_or_org_info a left outer join postal_addresses b on
(a.person_or_org_tag = b.person_or_org_tag and
a.address_type = b.address_type)
WHERE a.person_or_org_tag = $tag 
};
   my @nList;
   my @List = db_select_multiple($sqlStr);
   for $array_ref (@List) {
      my @row = @$array_ref;
      push @nList, [ @row ];
   }
   if ($#nList == -1) {
      $html_txt = "No record found";
   }
   else {
      $count = 0;
      $html_txt .= qq{<table><tr bgcolor="aqua">
	  <td><b>Name</b></td><td><b>Company Name</b></td><td><b>Tag</b></td>
	  </tr>
	  };
      for $array_ref ( @nList ) {
	    ($tag,$fName,$lName,$cName) = @$array_ref;
		$html_txt .= "<tr>\n";
		$html_txt .= qq{<td><a href="$program_name?option=view&tag=$tag">$fName $lName</a></td><td>$cName</td><td>$tag</td>};
		$html_txt .= "</tr>\n";
	  }
	  $html_txt .= "</table>\n";
   }
   $html_txt .= "</center>\n";
   return $html_txt;
}

sub email_search {
  my $email=shift;
   $html_txt = qq{<center>
<h3>Search Result</h3>
<hr width=400>
};
   $sqlStr = qq{
SELECT a.person_or_org_tag,a.first_name,a.last_name,b.affiliated_company
from person_or_org_info a left outer join postal_addresses b on
(a.person_or_org_tag = b.person_or_org_tag and
a.address_type = b.address_type), email_addresses c
WHERE c.email_address like '%$email%' and a.person_or_org_tag = c.person_or_org_tag
};
   my @nList;
   my @List = db_select_multiple($sqlStr);
   for $array_ref (@List) {
      my @row = @$array_ref;
      push @nList, [ @row ];
   }
   if ($#nList == -1) {
      $html_txt = "No record found";
   }
   else {
      $count = 0;
      $html_txt .= qq{<table><tr bgcolor="aqua">
          <td><b>Name</b></td><td><b>Company Name</b></td><td><b>Tag</b></td>
          </tr>
          };
      for $array_ref ( @nList ) {
            ($tag,$fName,$lName,$cName) = @$array_ref;
                $html_txt .= "<tr>\n";
                $html_txt .= qq{<td><a href="$program_name?option=view&tag=$tag">$fName $lName</a></td><td>$cName</td><td>$tag</td>};
                $html_txt .= "</tr>\n";
          }
          $html_txt .= "</table>\n";
   }
   $html_txt .= "</center>\n";
   return $html_txt;
 
}

sub locate_record {
   my $tag = shift;
   $ret_txt = "<center><table><tr><td colspan=2>\n";
   $ret_txt .= display_name($tag);
   $ret_txt .= "</td></tr>\n";
   $ret_txt .="<tr valign=\"top\"><td><img src=\"/spacer.gif\" width=30></td><td>\n";
   $ret_txt .= display_addresses($tag);
   $ret_txt .="</td><td><img src=\"/spacer.gif\" width=10></td><td>\n";
   $ret_txt .= display_phone_numbers($tag);
   $ret_txt .= display_email_addresses($tag);
   $ret_txt .= "</td></tr></table></center>";
   $ret_txt .= qq{<center>
   <table>$form_begin
   <input type="hidden" name="option" value="modify">
   <input type="hidden" name="tag" value="$tag">
   <tr>
   <td><input type="submit" value="Change Name" id="name" name="name" width="150"></td>
   <td><input type="submit" value="Change Address" id="address" name="address" width="150"></td>
   <td><input type="submit" value="Change Email" id="email" name="email" width="150"></td>
   <td><input type="submit" value="Change Phone" id="phone" name="phone" width="150"></td>
   </tr></form></table>
   </center>
   };
   return $ret_txt;
}

sub display_name {
   my $tag = shift;
   
   $sqlStr = qq{SELECT name_prefix,first_name,middle_initial,last_name,name_suffix
   FROM person_or_org_info
   WHERE person_or_org_tag = $tag
   };
   my ($prefix,$fName,$mI,$lName,$suffix) = db_select($sqlStr);
   $prefix = rm_tr($prefix);
   $fName = rm_tr($fName);
   $lName = rm_tr($lName);
   $suffix = rm_tr($suffix);
   $mI = rm_tr($mI);
   return "<h3>$prefix $fName $mI $lName $suffix ($tag)</h3>\n";
} 

sub display_addresses {
   my $tag = shift;
   $html_txt = "<table>";   
   $sqlStr = qq{SELECT address_type,person_title,affiliated_company,department,
   staddr1,staddr2,mail_stop,city,state_or_prov,postal_code,country
   FROM postal_addresses
   WHERE person_or_org_tag = $tag
   };
   my @addrList;
   my @List = db_select_multiple($sqlStr);
   for $array_ref (@List) {
      my @row = @$array_ref;
      push @addrList, [ @row ];
   }
   for $array_ref ( @addrList ) {
 
      my ($address_type,$person_title,$cName,$dept,$staddr1,$staddr2,$mailstop,$city,
      $state_or_prove,$postal_code,$country) = @$array_ref;
      $city = rm_tr($city);
      $address_type = rm_tr($address_type);
      $state_or_prove = rm_tr($state_or_prove);
      $person_title = rm_tr($person_title) if my_defined($person_title);
      $cName = rm_tr($cName) if my_defined($cName);
      $dept = rm_tr($dept) if my_defined($dept);
      if ($address_type eq "W") {      
         $html_txt .= "<tr><td colspan=2><b>Work Address</b></td></tr>\n";
      } elsif ($address_type eq "H") {
         $html_txt .= "<tr><td colspan=2><b>Home Address</b></td></tr>\n";
      } else {
         $html_txt .= "<tr><td colspan=2><b>Extra Address</b></td></tr>\n";
      }
         $html_txt .= "<tr><td>Title:</td><td>$person_title</td></tr>\n" if my_defined($person_title);
         $html_txt .= "<tr><td>Company:</td><td>$cName<br></td></tr>\n" if my_defined($cName);
         $html_txt .= "<tr><td>Department:</td><td>$dept<br></td></tr>\n" if my_defined($dept);
         $html_txt .= "<tr><td></td><td>$staddr1<br>\n";
         $html_txt .= "$staddr2<br>\n" if my_defined($staddr2);
         $html_txt .= "$city $state_or_prove  $postal_code<br>\n";
         $html_txt .= "$country</td></tr>\n";
   }
   $html_txt .= "</table>\n";
   return $html_txt;
}

sub display_phone_numbers {
   my $tag = shift;
   my @phList;
   $html_txt = "<table><tr><td colspan=3><b>Phone Numbers</b></td></tr>\n";
   %phType = (
      W => 'Work Phone',
      H => 'Home Phone',
      WF => 'Work Fax',
      HF => 'Home Fax',
      HT => 'Home TDD',
      WT => 'Work TDD',
      MP => 'Mobile',
      PG => 'Pager'
   );
   $sqlStr = qq{SELECT phone_type,phone_number,phone_comment
   FROM phone_numbers
   WHERE person_or_org_tag = $tag
   };
   my @List = db_select_multiple($sqlStr);
   for $array_ref (@List) {
      my @row = @$array_ref;
      push @phList, [ @row ];
   }
   for $array_ref (@phList) {
      my ($phone_type,$phone_number,$phone_comment) = @$array_ref;
      $phone_type = rm_tr($phone_type);
      $phone_number = rm_tr($phone_number) if my_defined($phone_number);
      if (my_defined($phone_comment)) {
         $phone_comment = rm_tr($phone_comment) ;
      } else {
         $phone_comment = " ";
      }
      if (defined($phType{$phone_type})) {
         $html_txt .= "<tr><td>$phType{$phone_type}:</td>";
      } else {
         $html_txt .= "<tr><td>Unknown:</td>";
      }
      $html_txt .= "<td>$phone_number</td><td>$phone_comment</td></tr>\n";
   }
   $html_txt .= "</table>\n";
   return $html_txt;
}

sub display_email_addresses {
   my $tag = shift;
   my @emailList;
   $html_txt = "<table><tr><td colspan=3><b>Email</b></td</tr>\n";
   $sqlStr = qq{SELECT email_type,email_address,email_comment,email_priority
   FROM email_addresses
   WHERE person_or_org_tag = $tag
   ORDER BY email_priority
   };
   my @List = db_select_multiple($sqlStr);
   for $array_ref (@List) {
      my @row = @$array_ref;
      push @emailList, [ @row ];
   }
   for $array_ref (@emailList) {
      my ($email_type,$email_address,$email_comment,$email_priority) = @$array_ref;
      $email_type = "I-D" if ($email_priority > 50);
      $email_address = rm_tr($email_address);
      $html_txt .= "<tr><td>${email_type}:</td><td>$email_address</td>";
      if (my_defined($email_comment)) {
         $email_comment = rm_tr($email_comment) ;
         $html_txt .= "<td>$email_comment</td></tr>\n";
      }
	  else {
	     $html_txt .= "<td></td></tr>\n";
      }
      
   }
   $html_txt .= "</table>\n";
   return $html_txt;
}


    
