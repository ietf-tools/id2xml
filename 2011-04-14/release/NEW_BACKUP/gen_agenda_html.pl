#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

$TESTDB = 0;
$INFORMIX = 1;
$MYSQL = 2;

($db_mode,$CURRENT_DATE,$CONVERT_SEED,$is_null) = init_database($MYSQL);


$dateStr = get_current_date();
$output_path = "/usr/local/etc/httpd/htdocs/IESG/internal";
$outfile_name = "agenda.txt";
$html_txt = qq{<html>
<TITLE>IESG Agenda</TITLE>
</HEAD>

<center><h1>IESG Agenda</H1></center>
Good approximation of what will be included in the next Telechat Agenda.<br><br>
<i>Updated $dateStr</i><br>
<HR>
<h2>1. Administrivia</h2>
<UL>
<LI>Roll Call
<LI>Bash the Agenda
<LI>Approval of the <A HREF="MINUTES.txt">Minutes</a> of the past telechat
<LI>List of Remaining <A HREF="task.txt">Action Items</a> from Last Telechat
</UL><P><P>
};

$text_txt = qq{IESG Agenda

Updated $dateStr
---------------------------------------------------------------------------
};

my %group_name = (
   1 => 'Protocol Action',
   2 => 'Under Discussion',
   3 => 'In Last Call',
   4 => 'AD Review',
   5 => 'On Hold',
   6 => 'Returned - Waiting for update',
   7 => 'Tentatively Approved',
   8 => 'Working Group Submissions',
   9 => 'Individual Submissions',
   10 => 'Proposed Working Groups',
   11 => 'Individual via RFC Editor',
   12 => 'Submissions'
);
my $pGroupFlag=0;
my $indexCnt = 2;


$sqlStr = qq{select rfc_flag,id_document_tag,ballot_id,status_date,
primary_flag,group_flag,token_email,email_display,note,acronym
from id_internal, acronym
where group_flag < 99
AND agenda = 1
AND id_internal.area_acronym_id = acronym.acronym_id
order by group_flag, ballot_id, primary_flag DESC, status_date
};

@List = db_select_multiple($sqlStr);
for $array_ref (@List) {
    ($rfc_flag,$id_document_tag,$temp_val,$status_date,
$pFlag,$gFlag,$token_email,$token_name,$note,$area_acronym) = rm_tr(@$array_ref);
   if ($rfc_flag) {
      $sqlStr = qq{
	  Select r.rfc_name,s.status_value,r.area_acronym 
	  from rfcs r, id_intended_status s
	  where r.rfc_number = $id_document_tag
	  AND r.intended_status_id = s.intended_status_id
	  };
	 ($doc_name,$statusStr,$gAcronym) = db_select($sqlStr);
	 $filename = "rfc${id_document_tag}.txt";
	 $filename1 = $filename;
	 $filename2 = "rfc/rfc${id_document_tag}.txt";
   } else {
     $sqlStr = qq{
	 Select i.id_document_name,i.filename,i.revision,s.status_value,m.acronym
	 from internet_drafts i,id_intended_status s,area_group p,acronym m
	 Where i.id_document_tag = $id_document_tag
	 AND i.intended_status_id = s.intended_status_id
	 AND (i.b_approve_date $is_null  or i.b_approve_date is NULL) 
	 AND i.group_acronym_id = p.group_acronym_id
	 AND p.area_acronym_id = m.acronym_id
	 };
	 ($doc_name,$filename,$revision,$statusStr,$gAcronym) = db_select($sqlStr);
	 next unless (my_defined($doc_name));
     $filename = rm_tr($filename);
	 $filename1 = $filename;
     $filename2 = "/internet-drafts/${filename}-${revision}.txt";
	 $filename = "${filename}-${revision}.txt";
   }
   if ($gFlag != $pGroupFlag) {
      $pGroupFlag = $gFlag;
      $gName = $group_name{$gFlag};
      $refName = "grp".$gFlag;
      if ($gFlag > 1) {
          $html_txt .= "</table>\n";
		  $text_txt .= "\n${line}\n";
       }
      $html_txt .= qq{
     <A name="$refName"><h2>${indexCnt}. $gName</H2></A>
     <table><tr><th>Area<th>Date<th></tr>
      };
	  $text_txt .= qq{
$gName
$line
};
      $indexCnt++;
   }
   $doc_name = rm_tr($doc_name);
   $status_date = convert_date($status_date,2);
   $status_date = convert_date($status_date);
   $status_date = "" unless ($status_date) ;
   #if ($gFlag == 9) {
      $area = rm_tr(uc($area_acronym));
   #} else {
   #   if (defined($gAcronym)) {
   #      $area = rm_tr(uc($gAcronym));
   #   } else {
   #      $area = "UND";
   #   }
   #}
   if ($area eq "ADM" or $area eq "UND") {
      $area = rm_tr(uc($area_acronym));
	  unless (defined($area)) {
	     $area = "UND";
	  }
   }
   $filename1 =~ s/.txt//;
   if ($pFlag) {
      $_ = "/usr/local/etc/httpd/htdocs/IESG/EVALUATIONS/${filename1}.bal";
      if (-e) {
         $html_txt .= qq{<tr><td><a href="/IESG/EVALUATIONS/${filename1}.bal">$area</a></td>};
      }
      else {
         $html_txt .= qq{<tr><td>$area</td>};
      }
      $html_txt .= qq{<td nowrap>$status_date</td>};
	  #$text_txt .= "\n"; 

   } else {
      $html_txt .= qq{<tr><td></td><td nowrap></td>};
   }
   $statusStr = rm_tr($statusStr);
   $html_txt .= qq{<td>$doc_name ($statusStr)</td></tr>
<tr><td></td><td></td>
<td><A HREF="${filename2}">${filename}</a> </td></tr>
};
   $one_line = "$doc_name ($statusStr)";
   $one_line = indent_text2($one_line,5);
   $text_txt .= qq{   * $one_line  
           <$filename>};
   if (my_defined($token_email) and $pFlag) {
      $html_txt .= qq{<tr><td></td><td>Token:</td>
      <td><a href="mailto:$token_email">$token_name</a></td></tr>
      };
   }
   if (my_defined($note) and $pFlag) {
      $html_txt .= qq{<tr><td></td><td>Note:</td>
      <td>$note</td></tr>
      };
	  $note = rm_tr($note);
   }
   $text_txt .="\n";
}
$sqlStr = "select group_acronym_id,note,token_name from group_internal where agenda=1";
@List = db_select_multiple($sqlStr);
if ($#List > -1) {
   $html_txt .= qq {
</table>
<h2>${indexCnt}. Proposed Working Group</h2>
     <table><tr><th>Area<th>Date<th></tr>
};
          $text_txt .= qq{
Proposed Working Group
$line
};
      $indexCnt++;
}

for $array_ref (@List) {
   my ($group_acronym_id,$note,$token_name) = rm_tr(@$array_ref);
   my $group_acronym = rm_tr(db_select("select acronym from acronym where acronym_id = $group_acronym_id"));
   
   my $area = uc(db_select("select a.acronym from acronym a,area_group ag where ag.group_acronym_id = $group_acronym_id and ag.area_acronym_id = a.acronym_id"));
   my $status_date = db_select("select last_modified_date from groups_ietf where group_acronym_id = $group_acronym_id");
   $status_date = convert_date($status_date,2);
   $status_date = convert_date($status_date);
   $status_date = "" unless ($status_date) ;
   my $group_name = rm_tr(db_select("select name from acronym where acronym_id = $group_acronym_id"));
   $html_txt .= "<tr><td>$area</td><td>$status_date</td><td><a href=\"/IESG/EVALUATIONS/${group_acronym}-charter.txt\">$group_name</a></td></tr>\n";  
   $text_txt .= "   * $group_name ($group_acronym)\n";
   if(my_defined($token_name)) {
     my $pTag = db_select("select person_or_org_tag from iesg_login where first_name = '$token_name'");
     $pTag = 0 unless (my_defined($pTag));
     my $email = get_email($pTag);
     $html_txt .= "<tr><td></td><td>Token:</td><td><a href=\"mailto:$email\">$token_name</a></td></tr>\n";
   }
   if (my_defined($note)) {
     $html_txt .= "<tr><td></td><td>Note:</td><td>$note</td></tr>";
   }
} 
$html_txt .= "</table>\n";

$text_txt .= "\n-------------------------------------------------\n";

my $template_html = db_select("select note from id_internal where group_flag = 100");


$news_index = $indexCnt;
$iab_index = $news_index + 1;
$mi_index = $iab_index + 1;
$html_txt .= qq{
<P><P>
<h3>${news_index}. Working Group News we can use</h3>
<P><P>
<h3>${iab_index}. IAB News we can use</h3>
<p><p>
<h3>${mi_index}. Management Issues</h3>
<P><P>
$template_html
<P>
</body></html>
};
if (defined($ARGV[0]) and $ARGV[0] eq "-deploy") {
   open (OUTFILE,">/usr/local/etc/httpd/htdocs/IESG/internal/agenda.html");
} elsif (defined($ARGV[0] and $ARGV[0] eq "-text")) {
   if (defined($ARGV[1] and -e $ARGV[1])) {
      $output_path = $ARGV[1];
   }
   #open (OUTFILE,">${output_path}/${outfile_name}");
   open (OUTFILE,">./${outfile_name}");
   print OUTFILE $text_txt;
   close(OUTFILE);
   exit(2);
} else {
   open (OUTFILE,">/usr/local/etc/httpd/htdocs/IESG/AGENDA.html");
}
print OUTFILE $html_txt;
close(OUTFILE);

exit;




