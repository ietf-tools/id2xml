#!/usr/local/bin/perl -w
use lib '/export/home/mlee/DBIs/';
use CGI;
use IETF_UTIL;
use IETF_DBUTIL;

$ENV{"DBPATH"} = "/export/home/mlee/database";
#$ENV{"DBPATH"} = "/usr/informix/databases";
$ENV{"DBNAME"} = "testdb";
#$ENV{"DBNAME"} = "people";

$program_name = "site_manager_devel.cgi";
$ENV{"PROG_NAME"} = $program_name;

my $q = new CGI;
my $dbh = get_dbh();
my $bgcolor = "CCE1C6";
my $switch = "-deploy";
my $user_agent = $ENV{HTTP_USER_AGENT};
@version_temp = split ' ',$user_agent;
$ENV{version} = $version_temp[0];

%group_name = (
     1 => 'Protocol Action              ',
     2 => 'Under Discussion             ',
     3 => 'In Last Call                 ',
     4 => 'AD Review                    ',
     5 => 'On Hold                      ',
     6 => 'Returned - Waiting for update',
     7 => 'Tentatively Approved         ',
     8 => 'Working Group Submissionn    ',
     9 => 'Individual Submissions       ',
     10 => 'Proposed Working Groups     ',
	 99 => 'History Folder              '
);
$status_select_list = get_status_select_list();
$table_header = qq{<table cellpadding="0" cellspacing="0" border="0" bgcolor="$bgcolor">
};
$form_header = qq{<form action="$program_name" method="POST">
};
$html_top = qq{
<html>
<HEAD><TITLE>Internal Site Manger -- $ENV{version}</title>

</head>
<body link="blue" vlink="blue">
<center>
<h2>Internal Site Manager</h2>
<table border=0 cellpadding="0" cellspacing="0" bgcolor="black">
<tr><td colspan="3"><img src="spacer.gif" border=0 width=1 height=1></td></tr>
<tr><td><img src="spacer.gif" border=0 width=1 height=1></td><td bgcolor="$bgcolor">
<table border=0 cellpadding="4" cellspacing="0">
<tr valign="top"><td align="center">
};

if (defined($q->param("generate"))) { ## Decide which menu has been selected
   if (defined($q->param("soi"))) {
      $command = "soi";
   }
   if (defined($q->param("pwg"))) {
	  $command = "pwg";
   }
   if (defined($q->param("agenda"))) {
	  $command = "agenda";
   }
   if (defined($q->param("request"))) {
	  $command = "request";
   } 
   if (defined($q->param("template"))) {
	  $command = "template";
   } 
   $func = "gen_${command}(\$dbh)";
   $html_body .= eval($func);
} elsif (defined($q->param("option"))) {
   if ($q->param("option") eq "add_delete_pwg") {
      if (defined($q->param("delete"))) {
	     $html_body .= delete_pwg($q->param("filename"));
	  } else {
         $html_body .= add_pwg($q->param("acronym"),$q->param("status_date"),$q->param("title_val"),$q->param("token_list"))
      }
   } elsif ($q->param("option") eq "add_db") {
      $html_body .= add_db($dbh,$q->param("acronym"),$q->param("status_date"),$q->param("note"),$q->param("token_name"));
   } elsif ($q->param("option") eq "edit_db") {
      $html_body .= edit_db($dbh,$q->param("acronym_id"),$q->param("status_date"),$q->param("note"),$q->param("agenda"));
   } elsif ($q->param("option") eq "edit_delete") {
      $gID = $q->param("gID");
	  if (defined($q->param("delete"))) {
         $sqlStr = "delete from group_internal where group_acronym_id = $gID";
		 my $sth = $dbh->prepare($sqlStr);
		 $sth->execute();
		 $html_body .= gen_pwg($dbh);
      } elsif (defined($q->param("edit"))) {
	     $html_body .= edit_pwg($dbh,$gID,$q->param("acronym"),$q->param("title"));
	  }
   } elsif ($q->param("option") eq "action") {
      $command = $q->param("cat");
	  system ("/export/home/mlee/DBIs/gen_${command}_html.pl $switch");
      $func = "gen_${command}(\$dbh)";
      $html_body .= eval($func);
   } elsif ($q->param("option") eq "display_by_group") {
      $group_title = $q->param("group_num");
	  $group_num = substr($group_title,6,1);
	  $html_body .= display_group($dbh,$group_num);
   } elsif ($q->param("option") eq "display_all_group") {
	  $html_body .= display_all_group($dbh);
   } elsif ($q->param("option") eq "edit_id") {
	  $html_body .= edit_id($dbh,$q);
   } elsif ($q->param("option") eq "add_ballot") {
	  $html_body .= add_ballot($dbh,$q);
   } elsif ($q->param("option") eq "update_agenda") {
      $html_body .= update_agenda($dbh,$q);
   } elsif ($q->param("option") eq "search_soi" or $q->param("option") eq "search_sub") {
      $html_body .= search_soi($dbh,$q);
   } elsif ($q->param("option") eq "confirm_soi" or $q->param("option") eq "confirm_sub") {
      $html_body .= confirm_soi($dbh,$q);
   } elsif ($q->param("option") eq "add_soi" or $q->param("option") eq "add_sub") {
      $html_body .= add_soi($dbh,$q);
   } elsif ($q->param("option") eq "display_history") {
      $html_body .= display_history($dbh);
   } elsif ($q->param("option") eq "delete_ballot") {
      $html_body .= delete_ballot($dbh,$q);
   } elsif ($q->param("option") eq "delete_request") {
      $html_body .= delete_request($dbh,$q);
   } elsif ($q->param("option") eq "search_request") {
      $html_body .= search_request($dbh,$q);
   } elsif ($q->param("option") eq "confirm_request") {
      $html_body .= confirm_request($dbh,$q);
   } elsif ($q->param("option") eq "add_request") {
      $html_body .= add_request($dbh,$q);
   } elsif ($q->param("option") eq "update_template") {
      $html_body .= update_template($q);
   }
} elsif (defined($q->param("document_tag"))) {
   $html_body .= edit_each_document($dbh,$q);
} else {  #Display Main Menu
   if ($ENV{version} eq "Mozilla/5.0") {
      $soi_str = "Status of Items                         ";
	  $request_str = "Submissions to IESG      ";
   } else {
      $soi_str = "Status of Items        ";
	  $request_str = "Submissions to IESG    ";
   }
   $html_body = qq{
   $table_header
   $form_header
   <input type="hidden" name="generate" value="yes">
   <tr>
       <td>
       <input type="submit" value="$soi_str" width="250" name="soi">
      </td>
      <td>
       <input type="submit" value="Draft Telechat Agenda " width="250" name="agenda">
      </td>
   </tr>
   <tr>
      <td>
       <input type="submit" value="Proposed Working Groups" width="250" name="pwg">
      </td>
      <td>
       <input type="submit" value="$request_str" width="250" name="request">
      </td>
   </tr>
   <tr><td colspan=2 align="center">
       <input type="submit" value="Templates?" width="250" name="template">
   </td></tr>
   </form>
   $form_header
   <input type="hidden" name="option" value="action">
   <input type="hidden" name="cat" value="single">
   <tr>
      <td colspan=2 align="center">
       <input type="submit" value="Singles?" width="250" name="single">
      </td>
   </tr>
   </form>
   </table>
   };
}
$html_bottom = "";
if (defined($q->param)) {
   $html_bottom = qq{
   $form_header
   <input type="submit" value="Main Menu" width="200">
   </form>
   };
}

$html_bottom .= qq{
</td></tr></table>
</td><td><img src="spacer.gif" border=0 width=1 height=1></td></tr>
<tr><td colspan="3"><img src="spacer.gif" border=0 width=1 height=1></td></tr>
</table>
</center>
</body>
</html>
};

$dbh->disconnect();

print <<END_HTML;
Content-type: text/html

$html_top
$html_body
$html_bottom
END_HTML

exit(1);

sub gen_template {
   my $html_txt = qq {
   <h2>Templates</h2>
   Please put HTML code for each template<br>
   <h3>Agenda</h3>
   };
   $sqlStr = "select note from id_internal where group_flag=100";
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   my $text = $sth->fetchrow_array();
   if (my_defined($text)) {
      $text = rm_tr($text);
   }
   $html_txt .= qq {
   <form action="http://10.27.30.48/test/system/update_template.cfm" method="POST">
   <input type="hidden" name="option" value="update_template">
   <textarea name="note" cols="70" rows="10" wrap="virtual">$text</textarea><br>
   <input type="submit" value="SUBMIT">
   </form>
   };
   return $html_txt;
}

sub update_template {
   my $q = shift;
   my $note = $q->param("note");
   $note =~ tr/\n/ /;
   $note =~ tr/\r/ /;
   $note = rm_tr($note);
   $note = $dbh->quote($note);
   $sqlStr = qq {
   update id_internal
   set note = $note
   where group_flag = 100
   };
   return $sqlStr;
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   my $html_txt = gen_template();
   return $html_txt;
}

sub gen_single {
   my $html_txt = qq{Single Page Generated};
   return $html_txt;
}
sub gen_pwg {
   my $dbh = shift;
   my $html_txt = "$table_header <tr><td>\n";
   $html_txt .= "<center><h3>Proposed Working Groups</h3></center><h4>Current List</h4>";
   $sqlStr=qq{select a.name,a.acronym,g.status_date,g.note,g.group_acronym_id
   from group_internal g, acronym a
   where g.group_acronym_id = a.acronym_id
   order by g.status_date DESC
   };
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   my %aID;
   $html_txt .= "$table_header \n";
   while (@row = $sth->fetchrow_array()) {
      $ac=rm_tr($row[1]);
      $aID{$ac} = $row[4];
	  $dateStr = $row[2];
	  $dateStr = convert_date($dateStr);
      $html_txt .= qq{
	  $form_header
	  <input type="hidden" name="option" value="edit_delete">
	  <input type="hidden" name="gID" value="$row[4]">
	  <input type="hidden" name="acronym" value="$ac">
	  <input type="hidden" name="title" value="$row[0]">
	  <tr>
	  <td>$dateStr</td><td>$row[0] ($ac)</td>
	  <td><input type="submit" name="edit" value="EDIT"></td>
	  <td><input type="submit" name="delete" value="DELETE"></td>
	  </tr>
	  </form>
	  };
   }
   $html_txt .= "</table>\n";
   $html_txt .= qq{
   <h4>Possible List</h4>
   $table_header
   };
   while ($filename=</usr/local/etc/httpd/htdocs/IESG/internal/BALLOT/*-charter.txt>) {
      open INFILE,$filename;
      $_ = <INFILE>;
      while (/^\W/) {
         $_ = <INFILE>;
      }
      chomp ($header = $_);
      @headAry = split '\(',$header;
      $name_val = $headAry[0];
      $ac_val = $headAry[1];
      @headAry = split '\)',$ac_val;
      $ac_val = $headAry[0];
	  if (!defined($aID{$ac_val})) {
         for ($loop=0;$loop<4;$loop++) {
            chomp($_ = <INFILE>);
         }
         @aryStr = split ':',$_;
         $dateStr = $aryStr[1];
         @dateParts = split '-',$dateStr;
         $day = $dateParts[0] + 1;
         $month = uc(substr($dateParts[1],0,3));
         $year = $dateParts[2];
         if (length($year) < 4) {
            $year = "20".$year;
         }
         $dateStr = $day."-".$month."-".$year;
		 my $token_list;
		 while (<INFILE>) {
            if (/.Area Director./) {
               $line = <INFILE>;
               chomp($line);
               while (length($line)) {
                  @temp = split ' ',$line;
                  $token_list .= "$temp[0] ";
                  $line = <INFILE>;
                  chomp($line);
                  chop($line);
				  chop($line);
                  chop($line);
				  chop($line);
               }
		       last;
		   }
		}
		 $html_txt .= qq{
		 $form_header
		 <input type="hidden" name="option" value="add_delete_pwg">
		 <input type="hidden" name="acronym" value="$ac_val">
		 <input type="hidden" name="status_date" value="$dateStr">
		 <input type="hidden" name="title_val" value="$name_val">
		 <input type="hidden" name="filename" value="$filename">
		 <input type="hidden" name="token_list" value="$token_list">
		 <tr>
		 <td>$month $day</td>
		 <td>$name_val ($ac_val)</td>
		 <td><input type="submit" value="ADD"></td>
		 <td><input type="submit" value="PERMANENT DELETE" name="delete"
		 onClick="return window.confirm('The file will be permanently removed from server');"></td>
		 </tr>
		 </form>
		 };
      }
      close (INFILE);
   }
   $html_txt .= qq{</table></td></tr></table>};  
   $html_txt .= qq{
   $form_header
   <input type="hidden" name="option" value="action">
   <input type="hidden" name="cat" value="pwg">
   <input type="submit" value = "Generate Web Page">
   </form>
   };
   return $html_txt;
}
sub gen_soi {
   my $dbh = shift;
   my $html_txt = "$table_header <tr><td>\n";
   my $space = "";
   my $his_space = "";
   $html_txt .= qq{<center><h3>Status of Items</h3></center>
   <h4>Select Group</h4>
   $form_header
   <table>
   <input type="hidden" name="option" value="display_by_group">
   };
   for ($loop=1;$loop<10;$loop++) {
      if ($ENV{version} eq "Mozilla/5.0") {
	    if ($loop == 1) {
		   $space = "                ";
		} elsif ($loop == 2) {
		   $space = "            ";
		} elsif ($loop == 3) {
		   $space = "                      ";
		} elsif ($loop == 4) {
		   $space = "                  ";
		} elsif ($loop == 5) {
		   $space = "                      ";
		} elsif ($loop == 6) {
		   $space = "   ";
		} elsif ($loop == 7) {
		   $space = "        ";
		} elsif ($loop == 8) {
		   $space = "";
		} elsif ($loop == 9) {
		   $space = "        ";
		}
		$his_space = "                                                 ";
      } else {
		$his_space = "                       ";
	  }
      $html_txt .= qq{
        <tr><td><input type="submit" value="Group ${loop}: $group_name{$loop}${space}" name="group_num" width="355"></td></tr>
	  };
   }
   $html_txt .= qq{</table></td></td></form>
   $form_header
   <input type="hidden" name="option" value="display_all_group">
   <tr><td>
   &nbsp;<input type="submit" value="Display All List                  " name="AllList" width="355">
   </form>
   $form_header
   <input type="hidden" name="option" value="display_history">
   &nbsp;<input type="submit" value="History Folder ${his_space}" name="hFolder" width="355">
   </form>
   </td></tr></table>};  
   $html_txt .= qq{
   <center>
   $form_header
   <input type="hidden" name="option" value="search_soi">
   <input type="submit" value="Add Ballot" width="180">
   </form>
   $form_header
   <input type="hidden" name="option" value="action">
   <input type="hidden" name="cat" value="soi">
   <input type="submit" value = "Generate Web Page">
   </form>
   </center>
   };
   return $html_txt;
}
sub gen_request {
   my $dbh = shift;
   my $html_txt = "";
$html_txt .= qq{
<center><h1>Submissions to the IESG</H1></center>
   <table cellpadding="0" cellspacing="0" border="0" ><tr>
   <td>
   $form_header
   <input type="hidden" name="option" value="search_request">
   <input type="submit" value="Add Request">
   </form>
   </td>
   <td>
   $form_header
   <input type="hidden" name="option" value="action">
   <input type="hidden" name="cat" value="request">
   <input type="submit" value = "Generate Web Page">
   </form>
   </td>
   </tr></table>
<table cellpadding="0" cellspacing="0" border="0"><tr><td align="center"><b>Current list in alphabetical order</b></td></tr>
$form_header
<input type="hidden" name="option" value="delete_request">
};


$sqlStr = qq{select a.id_document_tag,i.id_document_name,i.filename
from request a, internet_drafts i
where a.id_document_tag = i.id_document_tag
AND a.rfc_flag = 0
ORDER BY 3
};
my $sth = $dbh->prepare($sqlStr);
$sth->execute();
while (($dTag,$doc_name,$filename) = $sth->fetchrow_array()) {
   $doc_name = rm_tr($doc_name);
   $filename = rm_tr($filename);
   $html_txt .= qq{
<tr><td><input type="checkbox" name="${dTag}_id"><b>$filename</b><font size=-1>($doc_name)</font></td></tr>
};
}
$sqlStr = qq{select a.id_document_tag,r.rfc_name
from request a, rfcs r
where a.id_document_tag = r.rfc_number
AND a.rfc_flag = 1
ORDER BY 2
};
$sth = $dbh->prepare($sqlStr);
$sth->execute();
while (($dTag,$doc_name) = $sth->fetchrow_array()) {
   $doc_name = rm_tr($doc_name);
   $filename = "rfc${dTag}.txt";
   $html_txt .= qq{
<tr><td><font color="red"><input type="checkbox" name="${dTag}_rfc"><b>$filename</b><font size=-1>($doc_name)</font></font></td></tr>
};
}

   $html_txt .= qq{<tr><td><input type="submit" value="Delete Checked Item"
   onClick="return window.confirm('The item(s) will be permanently removed from database');"></td></tr></form></table>
   $form_header
   <input type="hidden" name="option" value="action">
   <input type="hidden" name="cat" value="request">
   <input type="submit" value = "Generate Web Page">
   </form>
    };
	
	
   return $html_txt;
}

sub search_request {
   my ($dbh,$q) = @_;
   my $html_txt = "";
   my $option = "";
   my ($id,$val);
   my $iStatusStr = "";
   my $StatusStr = "";
   $sqlStr = qq{
   select intended_status_id,status_value from id_intended_status
   };
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   while (($id,$val) = $sth->fetchrow_array()) {
      $iStatusStr .= qq{
	  <option value="$id">$val
	  };
   }

   $sqlStr = qq{
   select status_id,status_value from id_status
   };
   $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   while (($id,$val) = $sth->fetchrow_array()) {
      $StatusStr .= qq{
	  <option value="$id">$val
	  };
   }
   $html_txt .= qq{
        <CENTER>
		$form_header
		<input type="hidden" name="option" value="confirm_request">
        $table_header
                <TR><TD BGCOLOR="silver"><FONT COLOR=Black SIZE=+1><B> ID - Search Criteria </B></FONT>   </TD></TR>
                <TR><TD>
                        $table_header
						 <tr><td align="right"><B>Type:</b></td>
						 <td><input type="radio" name="dType" checked value="id">ID  
							<input type="radio" name="dType" value="rfc">RFC
						 </td>
						 </tr>
                                <TR><TD ALIGN="right"><B>Intended Status:</B>           </TD>
								   <TD><SELECT NAME="search_Intended_Status_id"><OPTION VALUE="">
								   $iStatusStr
								   </SELECT></TD></TR>
                                <TR><TD ALIGN="right"><B>Document Name:</B>                     </TD>
								   <TD><INPUT TYPE="text" NAME="search_id_document_name" SIZE="20" MAXLENGTH="200"></TD></TR>
                                <TR><TD ALIGN="right"><B>Group Acronym:</B>                     </TD>
								   <TD><INPUT TYPE="text" NAME="search_group_acronym" SIZE="20" MAXLENGTH="50"></TD></TR>
                                <TR><TD ALIGN="right"><B>Filename:</B>                          </TD>
								   <TD><INPUT TYPE="text" NAME="search_filename" SIZE="20" MAXLENGTH="40"></TD></TR>
                                <TR><TD ALIGN="right"><B>Status:</B>                            </TD>
								   <TD><SELECT NAME="search_status_id">
								      $StatusStr
									  <OPTION VALUE="">All</SELECT></TD></TR>
                        </TABLE>
                </TD></TR>
                <TR><TD ALIGN="CENTER" BGCOLOR="silver"><INPUT TYPE="submit" VALUE="Submit"></TD></TR>
        </TABLE>
		</form>
        </CENTER>
        
        </FORM>
        
<FONT COLOR="red">
<B>Note:</B> If you do not enter search criteria, it will take longer to display the results given that
all records will be returned.
</FONT>
   };
   return $html_txt;
}

sub confirm_request {
   my ($dbh,$q) = @_;
   my $html_txt = qq{$table_header
   <tr><th>Document Name</th><th>Status Date</th><th>Status</th></tr>
   };
   my $whereClause = "WHERE 0 = 0\n";
   my $dType = "";
   $iStatusId = $q->param("search_Intended_Status_id");
   $dName = uc($q->param("search_id_document_name"));
   $gAcronym = $q->param("search_group_acronym");
   $filename = $q->param("search_filename");
   $StatusId = $q->param("search_status_id");
   if (my_defined($iStatusId)) {
      $whereClause .= "AND intended_status_id = $iStatusId\n";
   }
   if (my_defined($StatusId)) {
      $whereClause .= "AND status_id = $StatusId\n";
   }
   if ($q->param("dType") eq "id") {
      $dType = "id";
      if (my_defined($dName)) {
	     $dName .= "%";
         $dName = $dbh->quote($dName);
         $whereClause .= "AND id_document_key like $dName\n";
      }
      if (my_defined($gAcronym)) {
	     $gAcronym .= "%";
         $gAcronym = $dbh->quote($gAcronym);
         $sqlStr = "select acronym_id from acronym where acronym like $gAcronym";
   	     my $sth0 = $dbh->prepare($sqlStr);
  	     $sth0->execute();
	     my $gID = $sth0->fetchrow_array();
         $whereClause .= "AND group_acronym_id = $gID\n";
      }
      if (my_defined($filename)) {
	     $filename .= "%";
         $filename = $dbh->quote($filename);
         $whereClause .= "AND filename like $filename\n";
      }
      $sqlStr = qq{
      select id_document_tag,id_document_name
      from internet_drafts
      $whereClause
      };


   } elsif ($q->param("dType") eq "rfc") {
      $dType = "rfc";
      if (my_defined($dName)) {
	     $dName .= "%";
         $dName = $dbh->quote($dName);
         $whereClause .= "AND rfc_name_key like $dName\n";
      }
      if (my_defined($gAcronym)) {
	     $gAcronym .= "%";
         $gAcronym = $dbh->quote($gAcronym);
         $whereClause .= "AND group_acronym like $gAcronym\n";
      }
      if (my_defined($filename)) {
	     $_ = $filename;
  	     s/(\D+)(\d+)(\D+)/$2/;
		 $rfc_number = $_;
         $whereClause .= "AND rfc_number = $rfc_number\n";
      }
      $sqlStr = qq{
      select rfc_number,rfc_name
      from rfcs
      $whereClause
      };
   } #elsif

#return $sqlStr;

   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   while (($dTag,$document_name) = $sth->fetchrow_array()) {
      $html_txt .= qq{
		$form_header
		<input type="hidden" name="option" value="add_request">
		<input type="hidden" name="dTag" value="$dTag">
		<input type="hidden" name="dType" value="$dType">
		<tr><Td>$document_name</td><td><input type="text" name="status_date" size="10"></td>
		<td>$status_select_list</td>
		<td><input type="submit" value="Add"></td></tr>
		</form>
      };
   } #while
   $html_txt .= "</table>\n";
   #$html_txt = $sqlStr;
   return $html_txt;
}

sub display_group {
   my ($dbh,$group_num) = @_;
   my $group_title = $group_name{$group_num};
   my $html_txt = qq{
   <h4>$group_title</h4>
   <table cellpadding="2" cellspacing="2" border="0">
   };
   
   $sqlStr = qq{select a.rfc_flag,a.ballot_id,a.id_document_tag,i.filename,i.id_document_name, a.primary_flag, a.status_date
   from id_internal a, outer internet_drafts i
   where a.group_flag = $group_num 
   AND a.id_document_tag = i.id_document_tag 
   AND i.b_approve_date is null
   order by a.ballot_id, a.primary_flag DESC
   };
   
   
   $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   while (($rfc_flag,$temp_val,$document_tag,$filename,$doc_name,$pFlag,$status_date) = $sth->fetchrow_array()) {
      if ($rfc_flag) {
	     my $sth2 = $dbh->prepare("Select rfc_name from rfcs where rfc_number = $document_tag");
		 $sth2->execute();
		 $doc_name = $sth2->fetchrow_array();
		 $filename = "rfc${document_tag}.txt";
	  }
      if ($pFlag) {
         $html_txt .= qq{<tr><td><a href="${program_name}?document_tag=$document_tag&ballot=yes" 
		 onMouseOver="window.status='Edit document $document_tag';return true;" 
		 onMouseOut="window.status='';return true;"><b>$filename</b></a>&nbsp;
		 <a href="http://ietfdev/dev/system/id/add/search_id3.cfm?id_document_tag=$document_tag&isnew=no&searchResults=$document_tag" target="_blank">
		 <font size="-2">[detail]</font>
		 </a>
		 </td><td>$status_date</td><td><font size=-1>($doc_name)</font></td></tr>
	     };
	  } else {
         $html_txt .= qq{<tr><td colspan="2"><img src="/spacer.gif" width="50" height="1" border="0" vspace="0">
		 <a href="${program_name}?document_tag=$document_tag" 
		 onMouseOver="window.status='Edit document $document_tag';return true;" 
		 onMouseOut="window.status='';return true;">$filename</a>&nbsp;
		 <a href="http://ietfdev/dev/system/id/add/search_id3.cfm?id_document_tag=$document_tag&isnew=no&searchResults=$document_tag" target="_blank">
		 <font size="-2">[detail]</font>
		 </a>
		 </td><td><font size=-1>($doc_name)</font></td></tr>
	     };
	  }


   }
   $html_txt .= "</table>\n";
   return $html_txt;
}

sub display_all_group {
   my $dbh = shift;
   
   my $html_txt = qq{
   <h4>$group_title</h4>
   <table cellpadding="2" cellspacing="2" border="0">
   };
   
   $sqlStr = qq{select a.group_flag, a.rfc_flag,a.ballot_id,a.id_document_tag,i.filename,i.id_document_name, a.primary_flag, a.status_date
   from id_internal a, outer internet_drafts i
   Where a.id_document_tag = i.id_document_tag 
   AND i.b_approve_date is null
   order by a.group_flag,a.ballot_id, a.primary_flag DESC
   };
   
   
   $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   my $old_group_num = 0;
   while (($group_num,$rfc_flag,$temp_val,$document_tag,$filename,$doc_name,$pFlag,$status_date) = $sth->fetchrow_array()) {
      if ($group_num != $old_group_num) {
	     $old_group_num = $group_num;
		 $group_title = $group_name{$group_num};
		 $html_txt .= qq {
		 <tr><td colspan="3"><hr><h3>$group_title</h3></td></tr>
		 };
	  }
      if ($rfc_flag) {
	     my $sth2 = $dbh->prepare("Select rfc_name from rfcs where rfc_number = $document_tag");
		 $sth2->execute();
		 $doc_name = $sth2->fetchrow_array();
		 $filename = "rfc${document_tag}.txt";
	  }
      if ($pFlag) {
         $html_txt .= qq{<tr><td><a href="${program_name}?document_tag=$document_tag&ballot=yes" 
		 onMouseOver="window.status='Edit document $document_tag';return true;" 
		 onMouseOut="window.status='';return true;"><b>$filename</b></a>&nbsp;
		 <a href="http://ietfdev/dev/system/id/add/search_id3.cfm?id_document_tag=$document_tag&isnew=no&searchResults=$document_tag" target="_blank">
		 <font size="-1">[detail]</font>
		 </a>
		 </td><td>$status_date</td><td><font size=-1>($doc_name)</font></td></tr>
	     };
	  } else {
         $html_txt .= qq{<tr><td colspan="2"><img src="/spacer.gif" width="50" height="1" border="0" vspace="0">
		 <a href="${program_name}?document_tag=$document_tag" 
		 onMouseOver="window.status='Edit document $document_tag';return true;" 
		 onMouseOut="window.status='';return true;">$filename</a>&nbsp;
		 <a href="http://ietfdev/dev/system/id/add/search_id3.cfm?id_document_tag=$document_tag&isnew=no&searchResults=$document_tag" target="_blank">
		 <font size="-2">[detail]</font>
		 </a>
		 </td><td><font size=-2>($doc_name)</font></td></tr>
	     };
	  }


   }
   $html_txt .= "</table>\n";
   return $html_txt;
}



sub delete_ballot {
   my($dbh,$q) = @_;
   my $cnt = 0;
   $sqlStr = "DELETE FROM id_internal where \n";
   foreach ($q->param) {
      if (/^\d/) {
	     $cnt++;
	     $sqlStr .= "ballot_id = $_ OR\n";
      }
   }
   unless ($cnt) {
      $sqlStr .= "group_flag = 99\n";
   } else {
      chop($sqlStr);
      chop($sqlStr);
      chop($sqlStr);
      chop($sqlStr);
   }
   #$html_txt .= $sqlStr;   
   my $sth2 = $dbh->prepare($sqlStr);
   $sth2->execute();
   
   
   my $html_txt = gen_soi($dbh);
   return $html_txt;
}

sub delete_request {
   my($dbh,$q) = @_;
   $sqlStr = "DELETE FROM request where \n";
   foreach ($q->param) {
      if (/^\d/) {
	     @temp = split '_';
		 $dTag = $temp[0];
		 $dType = $temp[1];
		 if ($dType eq "id") {
	        $sqlStr .= "(id_document_tag = $dTag AND rfc_flag=0) OR\n";
		 } else {
	        $sqlStr .= "(id_document_tag = $dTag AND rfc_flag=1) OR\n";
		 }
      }
   }
   chop($sqlStr);
   chop($sqlStr);
   chop($sqlStr);
   chop($sqlStr);
   #$html_txt .= $sqlStr;   
   my $sth2 = $dbh->prepare($sqlStr);
   $sth2->execute();
   
   
   my $html_txt = gen_request($dbh);
   return $html_txt;
}

sub display_history {
   my $dbh = shift;
   my $html_txt = qq{
   <h4>History Folder</h4>
   <table cellpadding="0" cellspacing="0" border="0">
   $form_header
   <input type="hidden" name="option" value="delete_ballot">
   };
   
   $sqlStr = qq{select a.rfc_flag,a.ballot_id,a.id_document_tag,i.filename,i.id_document_name, a.primary_flag
   from id_internal a, outer internet_drafts i
   where a.group_flag = 99 
   AND a.id_document_tag = i.id_document_tag 
   order by a.ballot_id, a.primary_flag DESC
   };
   
   
   $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   while (($rfc_flag,$ballot_id,$document_tag,$filename,$doc_name,$pFlag) = $sth->fetchrow_array()) {
      if ($rfc_flag) {
	     my $sth2 = $dbh->prepare("Select rfc_name from rfcs where rfc_number = $document_tag");
		 $sth2->execute();
		 $doc_name = $sth2->fetchrow_array();
		 $filename = "rfc${document_tag}.txt";
	  }
      if ($pFlag) {
         $html_txt .= qq{<tr><td><input type="checkbox" name="$ballot_id">
		 <a href="${program_name}?document_tag=$document_tag&ballot=yes"><b>$filename</b><font size=-1>($doc_name)</font></a></td></tr>
	     };
	  } else {
         $html_txt .= qq{<tr><td><img src="/spacer.gif" width="50" height="1" border="0" vspace="0">
		 <a href="${program_name}?document_tag=$document_tag">$filename<font size=-1>($doc_name)</font></a></td></tr>
	     };
	  }


   }
   $html_txt .= qq{
   <tr><td><input type="submit" value="Delete checked ballots"
   onClick="return window.confirm('The item(s) will be permanently removed from database');"></td></tr>
   };
   $html_txt .= "</form></table>\n";
   return $html_txt;
}

sub gen_agenda {
   my $dbh = shift;
   my $html_txt = qq{<center><h3>Draft Telechat Agendas</h3></center>
   $form_header
   <input type="hidden" name="option" value="action">
   <input type="hidden" name="cat" value="agenda">
   <input type="submit" value = "Generate Web Page">
   </form>
   $form_header
   <input type="hidden" name="option" value="update_agenda">
   $table_header <tr><td>
   <h2>All Ballots</h2>
	     <table cellpadding="0" cellspacing="0" border="0">
   };
   $oldGroup = 0;
   $sqlStr = qq{select a.rfc_flag,a.ballot_id,a.id_document_tag,i.filename,i.id_document_name,a.group_flag,a.agenda
   from id_internal a, outer internet_drafts i
   where a.id_document_tag = i.id_document_tag
   AND i.b_approve_date is null
   AND a.primary_flag = 1
   order by a.group_flag, a.ballot_id
   };
   
   
   $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   while (($rfc_flag,$ballot_id,$document_tag,$filename,$doc_name,$gFlag,$agenda) = $sth->fetchrow_array()) {
      if ($rfc_flag) {
	     my $sth2 = $dbh->prepare("Select rfc_name from rfcs where rfc_number = $document_tag");
		 $sth2->execute();
		 $doc_name = $sth2->fetchrow_array();
	  }
      if ($oldGroup != $gFlag) {
	     $oldGroup = $gFlag;
         $html_txt .= qq{
		 </table>
		 <h3>$group_name{$gFlag}</h3>
	     <table cellpadding="0" cellspacing="0" border="0">
	     };
	  }
	  $checkedStr = "";
	  if ($agenda) {
	     $checkedStr = "checked";
	  }
      $html_txt .= qq{<tr><td><input type="checkbox" value="on" name="$ballot_id" $checkedStr></td>
	  <td><li><a href="${program_name}?document_tag=$document_tag&ballot=yes" 
	  onMouseOver="window.status='Edit document $document_tag';return true;" 
	  onMouseOut="window.status='';return true;"><b>$filename</b><font size=-1>($doc_name)</font></a></td></tr>
	  };
   }
   $html_txt .= "</table>\n";
   $html_txt .= qq{
   <input type="submit" value="UPDATE">
   </form>
   };
   $html_txt .= qq{
   $form_header
   <input type="hidden" name="option" value="action">
   <input type="hidden" name="cat" value="agenda">
   <input type="submit" value = "Generate Web Page">
   </td></tr></table>
   </form>
   };
   return $html_txt;
}


sub edit_each_document {
   my ($dbh,$q) = @_;
   $id_document_tag = $q->param("document_tag");
   my $html_txt = qq{
      <table cellpadding="3" cellspacing="0" border="0">
   };
   my $sqlStr = qq{
      select a.rfc_flag,i.id_document_name,i.filename,i.revision, a.status_date, 
	  a.note, a.group_flag, a.token_email, a.token_name, a.email_display,a.agenda,a.ballot_id,a.area_acronym
	  from id_internal a, internet_drafts i
	  where a.id_document_tag = $id_document_tag
	  AND a.id_document_tag = i.id_document_tag
   };
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   my ($rfc_flag,$document_name,$filename,$revision,$status_date,$note,$group_flag,
       $email,$owner,$email_display,$agenda,$ballot_id,$area_acronym) = $sth->fetchrow_array();
   $note = rm_tr($note);
   $owner = rm_tr($owner);
   my $select_str_area = "";
   my $select_area_html = "";
   if ($group_flag == 9) {
      $select_str_area = qq{<select name="area_acronym">
      <option value=""></option>
      };
      $sqlStr = "select a.acronym from acronym a, areas b where b.area_acronym_id = a.acronym_id order by 1";
      my $sth_select = $dbh->prepare($sqlStr);
      $sth_select->execute();
      while ($acronym_val = $sth_select->fetchrow_array()) {
         $acronym_val = rm_tr(uc($acronym_val));
		 $selected_str = "";
		 if ($acronym_val eq $area_acronym) {
		    $selected_str = "selected";
		 }
         $select_str_area .= qq{
   	     <option value="$acronym_val" $selected_str>$acronym_val</option>
	     };
      }
      $select_str_area .= "</select>";
	  $select_area_html = qq{
	  <tr><td>Area Acronym:</td><td>$select_str_area</td></tr>
	  };
   } else {
      $select_area_html = qq{
	  <input type="hidden" name="area_acronym" value="$area_acronym">
	  };
   }
   if ($rfc_flag) {
      my $sth2 = $dbh->prepare("Select rfc_name from rfcs where rfc_number = $id_document_tag");
	 $sth2->execute();
	 $document_name = $sth2->fetchrow_array();
	 $filename = "rfc${id_document_tag}.txt";
   } else {
     $filename = rm_tr($filename);
     $filename = "${filename}-${revision}.txt";
   }
   $email = rm_tr($email);
   $email_display = rm_tr($email_display);
   @emails = split ',', $email;
   my $cnt=0;
   my $email_str = "";
   my $add_ballot_str = "";
   my $email_list_html = get_email_list("new_email");
   my $cur_date = get_current_date(1);
   foreach $email_addr (@emails) {
      $cnt++;
      $email_str .= qq{
         <tr><td>Email${cnt}:</td><td><input type="text" name="email${cnt}" value="$email_addr"></td></tr>
      };
   }
   $email_str .= qq{
      <tr><td>Add Email:</td><td>$email_list_html</td></tr>
   };
   $_ = $group_flag;
   if (/1|2|5|6|7|8/) {
      $select_str = qq{<select name="group_flag" onChange="document.form1.status_date.value='$cur_date';">};
   } else {
      $select_str = qq{<select name="group_flag">};
   }
   foreach $gKey (sort keys %group_name) {
      my $selected = "";
	  if ($gKey eq $group_flag) {
	     $selected = "selected";
      }
      $select_str .= qq{
	     <option value="$gKey" $selected>$group_name{$gKey}</option>
	  };  
   }
   $select_str .= qq{</select>};
   my $agenda_str = "";
   my $group_str = "";
   if (defined($q->param("ballot"))) {
     if($agenda) {
        $agenda_str .= qq{
    	    <tr><td>Check for Agenda</td><td><input type="checkbox" checked name="agenda"></td></tr>
    	 };
     } else {
        $agenda_str .= qq{
    	    <tr><td>Check for Agenda</td><td><input type="checkbox" name="agenda"></td></tr>
    	 };
	 }
	 $group_str .= qq{
   <tr><td>Group:</td><td>$select_str</td></tr>
	 };
	 $add_ballot_str .= qq{
      <form>
      <tr><td colspan="2" align="center"><input type="hidden" name="option" value="search_sub">
      <input type="hidden" name="ballot_id" value="$ballot_id"><input type="hidden" name="group_flag" value="$group_flag">
      <input type="submit" value="Add sub ballot"></td></tr>
      </form>
      };	 
   } else {
      $group_str .= qq{
	  <input type="hidden" name="group_flag" value="$group_flag">
	  };
   }
	  
   $html_txt .= qq{
   <form action="$program_name" method="POST" name="form1">
   <input type="hidden" name="option" value="edit_id">
   <input type="hidden" name="id_document_tag" value="$id_document_tag">
   <input type="hidden" name="email_count" value="$cnt">
   <input type="hidden" name="ballot_id" value="$ballot_id">
   <tr><td>Document Name:</td><td><b>$document_name</b></td></tr>
   <tr><td>File Name:</td><td>${filename}</td></tr>
   <tr><td>Status Date:</td><td><input type="text" name="status_date" value="$status_date"></td></tr>
   $group_str
   $select_area_html
   $email_str
   <tr><td>Email Display:</td><td><input type="text" name="email_display" value="$email_display"></td></tr>
   <tr><td>Owner:</td><td><input type="text" name="owner" value="$owner"></td></tr>
   $agenda_str
   <tr><td>Note:</td><td><textarea name="note" cols="40" rows="3">$note</textarea></td></tr>
   <tr><td colspan="2" align="center">
   <input type="submit" value="EDIT">
   <input type="reset" value="RESET">
   <input type="button" name="cancel" value="CANCEL" onClick="history.go(-1);return true"></td></tr>
   </form>
   $add_ballot_str
   };
   
   
   $html_txt .= qq{
   </table>
   };
   return $html_txt;
}

sub search_soi {
   my ($dbh,$q) = @_;
   my $html_txt = "";
   my $option = "";
   my $ballot_str = "";
   my ($id,$val);
   if ($q->param("option") eq "search_soi") {
      $option = "confirm_soi";
   } else {
      $option = "confirm_sub";
	  my $ballot_id = $q->param("ballot_id");
	  my $group_flag = $q->param("group_flag");
	  $ballot_str = qq{<input type="hidden" name="ballot_id" value="$ballot_id">
	  <input type="hidden" name="group_flag" value="$group_flag">
      };
   }
   my $iStatusStr = "";
   my $StatusStr = "";
   $sqlStr = qq{
   select intended_status_id,status_value from id_intended_status
   };
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   while (($id,$val) = $sth->fetchrow_array()) {
      $iStatusStr .= qq{
	  <option value="$id">$val
	  };
   }

   $sqlStr = qq{
   select status_id,status_value from id_status
   };
   $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   while (($id,$val) = $sth->fetchrow_array()) {
      $StatusStr .= qq{
	  <option value="$id">$val
	  };
   }
   $html_txt .= qq{
        <CENTER>
		$form_header
		<input type="hidden" name="option" value="$option">
		$ballot_str
        $table_header
                <TR><TD BGCOLOR="silver"><FONT COLOR=Black SIZE=+1><B> ID - Search Criteria </B></FONT>   </TD></TR>
                <TR><TD>
                        $table_header
						 <tr><td align="right"><B>Type:</b></td>
						 <td><input type="radio" name="dType" checked value="id">ID  
							<input type="radio" name="dType" value="rfc">RFC
						 </td>
						 </tr>
                                <TR><TD ALIGN="right"><B>Intended Status:</B>           </TD>
								   <TD><SELECT NAME="search_Intended_Status_id"><OPTION VALUE="">
								   $iStatusStr
								   </SELECT></TD></TR>
                                <TR><TD ALIGN="right"><B>Document Name:</B>                     </TD>
								   <TD><INPUT TYPE="text" NAME="search_id_document_name" SIZE="20" MAXLENGTH="200"></TD></TR>
                                <TR><TD ALIGN="right"><B>Group Acronym:</B>                     </TD>
								   <TD><INPUT TYPE="text" NAME="search_group_acronym" SIZE="20" MAXLENGTH="50"></TD></TR>
                                <TR><TD ALIGN="right"><B>Filename:</B>                          </TD>
								   <TD><INPUT TYPE="text" NAME="search_filename" SIZE="20" MAXLENGTH="40"></TD></TR>
                                <TR><TD ALIGN="right"><B>Status:</B>                            </TD>
								   <TD><SELECT NAME="search_status_id">
								      $StatusStr
									  <OPTION VALUE="">All</SELECT></TD></TR>
                        </TABLE>
                </TD></TR>
                <TR><TD ALIGN="CENTER" BGCOLOR="silver"><INPUT TYPE="submit" VALUE="Submit"></TD></TR>
        </TABLE>
		</form>
        </CENTER>
        
        </FORM>
        
<FONT COLOR="red">
<B>Note:</B> If you do not enter search criteria, it will take longer to display the results given that
all records will be returned.
</FONT>
   };
   return $html_txt;
}

sub confirm_soi {
   my ($dbh,$q) = @_;
   my $html_txt = "$table_header\n";
   my $option = "";
   my $ballot_str = "";
   my ($id,$val);
   my $dType = "";
   if ($q->param("option") eq "confirm_soi") {
      $option = "add_soi";
   } else {
      $option = "add_sub";
	  my $ballot_id = $q->param("ballot_id");
	  my $group_flag = $q->param("group_flag");
	  $ballot_str = qq{<input type="hidden" name="ballot_id" value="$ballot_id">
	  <input type="hidden" name="group_flag" value="$group_flag">
	  };
   }
   my $whereClause = "WHERE 0 = 0\n";
   my $dType = "";
   $iStatusId = $q->param("search_Intended_Status_id");
   $dName = uc($q->param("search_id_document_name"));
   $gAcronym = $q->param("search_group_acronym");
   $filename = $q->param("search_filename");
   $StatusId = $q->param("search_status_id");
   if (my_defined($iStatusId)) {
      $whereClause .= "AND intended_status_id = $iStatusId\n";
   }
   if (my_defined($StatusId)) {
      $whereClause .= "AND status_id = $StatusId\n";
   }
   if ($q->param("dType") eq "id") {
      $dType = "id";
      if (my_defined($dName)) {
	     $dName .= "%";
         $dName = $dbh->quote($dName);
         $whereClause .= "AND id_document_key like $dName\n";
      }
      if (my_defined($gAcronym)) {
	     $gAcronym .= "%";
         $gAcronym = $dbh->quote($gAcronym);
         $sqlStr = "select acronym_id from acronym where acronym like $gAcronym";
   	     my $sth0 = $dbh->prepare($sqlStr);
  	     $sth0->execute();
	     my $gID = $sth0->fetchrow_array();
         $whereClause .= "AND group_acronym_id = $gID\n";
      }
      if (my_defined($filename)) {
	     $filename .= "%";
         $filename = $dbh->quote($filename);
         $whereClause .= "AND filename like $filename\n";
      }
      $sqlStr = qq{
      select id_document_tag,id_document_name
      from internet_drafts
      $whereClause
      };


   } elsif ($q->param("dType") eq "rfc") {
      $dType = "rfc";
      if (my_defined($dName)) {
		 $dName .= "%";
         $dName = $dbh->quote($dName);
         $whereClause .= "AND rfc_name_key like $dName\n";
      }
      if (my_defined($gAcronym)) {
	     $gAcronym .= "%";
         $gAcronym = $dbh->quote($gAcronym);
         $whereClause .= "AND group_acronym like $gAcronym\n";
      }
      if (my_defined($filename)) {
	     $_ = $filename;
  	     s/(\D+)(\d+)(\D+)/$2/;
		 $rfc_number = $_;
         $whereClause .= "AND rfc_number = $rfc_number\n";
      }
      $sqlStr = qq{
      select rfc_number,rfc_name
      from rfcs
      $whereClause
      };
   } #elsif
   #return $sqlStr;
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   while (my ($dTag,$document_name) = $sth->fetchrow_array()) {
      $html_txt .= qq{
		$form_header
		<input type="hidden" name="option" value="$option">
		<input type="hidden" name="dTag" value="$dTag">
		<input type="hidden" name="dType" value="$dType">
		<input type="hidden" name="dName" value="$document_name">
		$ballot_str 
		<tr><Td>$document_name $dTag</td><td>
		<input type="submit" value="Submit"></td></tr>
		</form>
      };
   }
   $html_txt .= "</table>\n";
   #$html_txt .= $sqlStr;
   return $html_txt;
}

sub add_soi {
   my ($dbh,$q) = @_;
   my $html_txt = qq{
      <table cellpadding="3" cellspacing="0" border="0">
   };
   my $group_str = "";
   my $agenda_str = "";
   my $ballot_id;
   my $dTag = $q->param("dTag");
   my $dType = $q->param("dType");
   if ($dType eq "id") {
      $rfc_flag = 0;
   } elsif ($dType eq "rfc") {
      $rfc_flag = 1;
   }
   my $dName = $q->param("dName");
   my $select_str_area = qq{<select name="area_acronym">
   <option value=""></option>
   };
   $sqlStr = "select a.acronym from acronym a, areas b where b.area_acronym_id = a.acronym_id order by 1";
   my $sth_select = $dbh->prepare($sqlStr);
   $sth_select->execute();
   while ($acronym_val = $sth_select->fetchrow_array()) {
      $acronym_val = uc($acronym_val);
      $select_str_area .= qq{
	  <option value="$acronym_val">$acronym_val</option>
	  };
   }
   $select_str_area .= "</select>";
   if ($q->param("option") eq "add_soi") {
      my $sqlStr = qq{
      select max(ballot_id) from id_internal
      };
      my $sth = $dbh->prepare($sqlStr);
      $sth->execute();
      $ballot_id = $sth->fetchrow_array();
      $ballot_id++;
  
      $select_str = qq{<select name="group_flag">};
      foreach $gKey (sort keys %group_name) {
         my $selected = "";
   	     if ($gKey eq $group_flag) {
    	     $selected = "selected";
         }
         $select_str .= qq{
   	     <option value="$gKey" $selected>$group_name{$gKey}</option>
    	  };  
      }
      $select_str .= qq{</select>};
	  $group_str .= qq{
	  <tr><td>Group:</td><td>$select_str</td></tr>
	  };
      $agenda_str .= qq{
   <tr><td>Check for Agenda</td><td><input type="checkbox" name="agenda"></td></tr>
      };
   } elsif ($q->param("option") eq "add_sub") {
      my $group_flag = $q->param("group_flag");
	  $ballot_id = $q->param("ballot_id");
      $group_str .= qq{
	  <input type="hidden" name="group_flag" value="$group_flag">
	  <input type="hidden" name="sub_ballot" value="yes">
	  };
   }
   my $email_list_html = get_email_list("email_address");
   $html_txt .= qq{
   $form_header
   <input type="hidden" name="option" value="add_ballot">
   <input type="hidden" name="ballot_id" value="$ballot_id">
   <input type="hidden" name="id_document_tag" value="$dTag">
   <input type="hidden" name="rfc_flag" value="$rfc_flag">
   <tr><td>Document Name:</td><td>$dName</td></tr>
   <tr><td>Status Date:</td><td><input type="text" name="status_date" value="$status_date"></td></tr>
   $group_str
   <tr><td>Area Acronym:</td><td>$select_str_area</td></tr>
   <tr><td>Email Display:</td><td><input type="text" name="email_display"></td></tr>
   <tr><td>Email Address:</td><td>$email_list_html</td></tr>
   <tr><td>Owner:</td><td><input type="text" name="owner"></td></tr>
   $agenda_str
   <tr><td>Note:</td><td><textarea name="note" cols="40" rows="3"></textarea></td></tr>
   <tr><td colspan="2" align="center">
   <input type="submit" value="ADD">
   <input type="button" name="cancel" value="CANCEL" onClick="history.go(-1);return true"></td></tr>
   </form>
   };
   
   
   $html_txt .= qq{
   </table>
   };
   return $html_txt;
}

sub add_pwg {
   my ($ac_val,$status_date,$title_val,$token_list) = @_;
   my @list = split " ",$token_list;
   my $select_str = qq{<select name="token_name">};
   foreach $val (@list) {
      $select_str .= qq{
	     <option value="$val">$val</option>
	  };  
   }
   $select_str .= qq{</select>};
   
   $html_txt = "";
   $html_txt .= qq{<h4>Adding new PWG list</h4>
   $table_header <tr><td>
   $form_header
   <input type="hidden" name="acronym" value="$ac_val">
   <input type="hidden" name="option" value="add_db">
   <font color="red"><b>$title_val ($ac_val)</b></font><br><br>
   Status Date: <input type="text" name="status_date" value="$status_date"><br>
   Token Name: $select_str<br>
   Note: <br>
   <textarea name="note" cols="40" rows="5"></textarea><br>
   <input type="submit" value="CONFIRM ADD">
   </form>
   </td></tr></table>
   };
   return $html_txt;
}

sub add_db {
   my ($dbh,$ac_val,$status_date,$note,$token_name) = @_;
   $status_date = y_two_k($status_date);
   $status_date = $dbh->quote($status_date);
   $note = $dbh->quote($note);
   $ac_val = $dbh->quote($ac_val);
   $token_name = $dbh->quote($token_name);
   $sqlStr = "select acronym_id from acronym where acronym = $ac_val";
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   $gID = $sth->fetchrow_array();
   return "<b>ERROR: The group acronym can not be found</b>" if !defined($gID);
   $sqlStr = qq{
   insert into group_internal (group_acronym_id,note,status_date,token_name)
   values ($gID,$note,$status_date,$token_name)
   };
#   $html_txt2 = $sqlStr;
   $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   $html_txt2 .= gen_pwg($dbh);
   return $html_txt2;
}
sub edit_pwg {
   my ($dbh,$gID,$acronym,$title) = @_;
   my $sqlStr = qq{
   select status_date,note,agenda,token_name from group_internal where group_acronym_id = $gID
   };
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   my ($status_date,$note,$agenda,$token_name) = $sth->fetchrow_array();
   $note = rm_tr($note);
   my $agenda_str = "";
   if ($agenda) {
     $agenda_str .= qq{
	    <input type="checkbox" checked name="agenda"><br>
	 };
   } else {
     $agenda_str .= qq{
	    <input type="checkbox" name="agenda"><br>
	 };

   }
   $html_txt = "";
   $html_txt .= qq{<h4>Edit PWG list</h4>
   $table_header
   <tr><td>
   $form_header
   <input type="hidden" name="acronym_id" value="$gID">
   <input type="hidden" name="option" value="edit_db">
   <font color="red"><b>$title ($acronym)</b></font><br><br>
   Status Date: <input type="text" name="status_date" value="$status_date"><br>
   Token Name: <input type="text" name="token_name" value="$token_name"><br>
   Check for Agenda: $agenda_str
   Note: <br>
   <textarea name="note" cols="40" rows="5">$note</textarea><br>
   <input type="submit" value="CONFIRM EDIT">
   </form>
   </td></tr></table>
   };
   return $html_txt;
}

sub edit_db {
   my ($dbh,$gID,$status_date,$note,$agenda,$token_name) = @_;
   my $html_txt = "";
   if ($agenda eq "on") {
      $agenda_val = 1;
   } else {
      $agenda_val = 0;
   }
   $status_date = y_two_k($status_date);
   $status_date = $dbh->quote($status_date);
   $note = $dbh->quote($note);
   $token_name = $dbh->quote($token_name);
   $sqlStr = qq{update group_internal set note = $note, status_date = $status_date, agenda=$agenda_val, token_name=$token_name
   where group_acronym_id = $gID};
   $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   $html_txt .= gen_pwg($dbh);
   
   return $html_txt;
}

sub edit_id {
   my ($dbh,$q) = @_;
   my $agenda_val = 0;
   if (defined($q->param("agenda")) and $q->param("agenda") eq "on") {
      $agenda_val = 1;
   }
   $id_document_tag = $q->param("id_document_tag");
   $ballot_id = $q->param("ballot_id");
   $group_flag = $q->param("group_flag");
   $status_date = y_two_k($q->param("status_date"));
   $status_date = $dbh->quote($status_date);
   $email_display = $dbh->quote($q->param("email_display"));
   $owner = $dbh->quote($q->param("owner"));
   $note = $dbh->quote($q->param("note"));
   $area_acronym = $dbh->quote($q->param("area_acronym"));
   my $email_str = "";
   for ($loop=1;$loop <= $q->param("email_count");$loop++) {
      if ($q->param("email${loop}") ne "" and my_defined($q->param("email${loop}"))) {
         $email_str .= $q->param("email${loop}") . ",";
	  }
   }
   if ($q->param("new_email") ne "" and my_defined($q->param("new_email"))) {
      $email_str .= $q->param("new_email");
   } else {
      chop($email_str);
   }
   $email_str = $dbh->quote($email_str);
   $sqlStr = qq{
   update id_internal
      set status_date = $status_date,
    	  note = $note,
    	  token_name = $owner,
    	  token_email = $email_str,
    	  email_display = $email_display,
    	  group_flag = $group_flag, 
		  agenda=$agenda_val,
		  area_acronym=$area_acronym
	  where id_document_tag = $id_document_tag
   };
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   $sqlStr = qq{
   update id_internal
      set group_flag = $group_flag
	  where ballot_id = $ballot_id and id_document_tag <> $id_document_tag
   };
   $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   #my $html_txt = gen_soi($dbh);
   my $html_txt = display_group($dbh,$group_flag);
   #$html_txt = $sqlStr;
   return $html_txt;
}

sub add_ballot {
   my ($dbh,$q) = @_;
   my $agenda_val = 0;
   if (defined($q->param("agenda")) and $q->param("agenda") eq "on") {
      $agenda_val = 1;
   }
   $ballot_id = $q->param("ballot_id");
   if (defined($q->param("sub_ballot")) and $q->param("sub_ballot") eq "yes") {
      $primary_flag = 0;
   } else {
      $primary_flag = 1;
   }
   my $rfc_flag = $q->param("rfc_flag");
   $id_document_tag = $q->param("id_document_tag");
   $group_flag = $q->param("group_flag");
   $status_date = y_two_k($q->param("status_date"));
   $status_date = $dbh->quote($status_date);
   $email_display = $dbh->quote($q->param("email_display"));
   $owner = $dbh->quote($q->param("owner"));
   $note = $dbh->quote($q->param("note"));
   $email_address = $dbh->quote($q->param("email_address"));
   $area_acronym = $dbh->quote($q->param("area_acronym"));
   $sqlStr = "select count(*) from id_internal where id_document_tag = $id_document_tag";
   #return $sqlStr;
   my $sth2 = $dbh->prepare($sqlStr);
   $sth2->execute();
   my $cnt = $sth2->fetchrow_array();
   if ($cnt) {
      my $html_txt = qq{
      This document already exists<br>
	  <form><input type="button" name="cancel" value="EDIT" onClick="history.go(-1);return true"></form>
	  };
	  return $html_txt;
   }
   $sqlStr = qq{
   insert into id_internal 
   (ballot_id,primary_flag,group_flag,id_document_tag,status_date,note,token_name,token_email,email_display,agenda,rfc_flag,area_acronym)
   values 
   ($ballot_id,$primary_flag,$group_flag,$id_document_tag,$status_date,$note,$owner,$email_address,$email_display,$agenda_val,$rfc_flag,$area_acronym)
   };
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   my $html_txt = gen_soi($dbh);
   #my $html_txt = $sqlStr;
   return $html_txt;
}

sub add_request {
   my ($dbh,$q) = @_;
   my $rfc_val = 0;
   if ($q->param("dType") eq "rfc") {
      $rfc_val = 1;
   }
   $dTag = $q->param("dTag");
   $status_date = y_two_k($q->param("status_date"));
   $status_date = $dbh->quote($status_date);
   $sqlStr = "select count(*) from request where id_document_tag = $dTag";
   my $sth2 = $dbh->prepare($sqlStr);
   $sth2->execute();
   my $cnt = $sth2->fetchrow_array();
   if ($cnt) {
      my $html_txt = qq{
      This document already exists<br>
	  <form><input type="button" name="cancel" value="EDIT" onClick="history.go(-1);return true"></form>
	  };
	  return $html_txt;
   }
   $sqlStr = qq{
   insert into request 
   (id_document_tag,status_date,rfc_flag)
   values 
   ($dTag,$status_date,$rfc_val)
   };
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   my $html_txt = gen_request($dbh);
   #my $html_txt = $sqlStr;
   return $html_txt;
}

sub update_agenda {
   my ($dbh,$q) = @_;
   my $sqlStr = "UPDATE id_internal set agenda=0 where 0=0\n";
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   $sqlStr = "UPDATE id_internal set agenda=1 where \n";
   foreach ($q->param) {
      if (/^\d/) {
	     $sqlStr .= "ballot_id = $_ OR\n";
      }
   }
   chop($sqlStr);
   chop($sqlStr);
   chop($sqlStr);
   chop($sqlStr);
#   $html_txt .= $sqlStr;   
   my $sth2 = $dbh->prepare($sqlStr);
   $sth2->execute();
   my $html_txt = "</center>\n";
   $html_txt .= gen_agenda($dbh);
   return $html_txt;
}

sub delete_pwg {
	     $filename = shift;
		 my $html_txt = "";
		 $cnt = unlink $filename;
         my @str = split '/',$filename;
	     my $filename_simple = $str[$#str];
		 if ($cnt) {
    	     $html_txt .= qq{<b>$filename</b> is deleted<br>};
	     } else {
    	     $html_txt .= qq{<b>$filename</b> cannot be deleted<br>};
		 }
    	return $html_txt;
}

sub y_two_k {
   my $ret_val = shift;
   $_ = $ret_val;
   if (/\//) {
      my @temp = split '\/';
	  if ($temp[2] < 50) {
		 $temp[2] = 2000 + $temp[2];
	  } 
	  $ret_val = join '/', @temp;
   } else {
      my @temp = split '-';
	  if ($temp[2] < 50) {
	     $temp[2] = $temp[2] + 2000;
	  } 
	  $ret_val = join '-', @temp;
   }
   return $ret_val;
}

sub get_email_list {
   my $target_name = shift;
   @email_list = ("","mankin\@isi.edu","april.marine\@nominum.com","bwijnen\@lucent.com","fenner\@research.att.com","nordmark\@eng.sun.com","harald\@alvestrand.no","jis\@mit.edu","mleech\@nortelnetworks.com","ned.freed\@mrochek.com","paf\@cisco.com","randy\@psg.com","sob\@harvard.edu","narten\@us.ibm.com");
   my $ret_val = qq{<select name="$target_name">
   };
   for ($loop = 0;$loop<=$#email_list;$loop++) {
      $ret_val .= qq{<option value="$email_list[$loop]">$email_list[$loop]</option>
      };  
   }
   $ret_val .= qq{</select>
   };
   return $ret_val;
}


sub get_status_select_list {
   my $ret_val = qq{
<select name="intended_status_id">
<option value=""></option>
};
  my $sth = $dbh->prepare("select status_value from id_intended_status");
  $sth->execute();
  while (my $status_value = $sth->fetchrow_array()) {
     $ret_val .= qq{<option value="$status_value">$status_value</option>
	 };
  }
$ret_val .= qq{</select>
};
   return $ret_val;
}
