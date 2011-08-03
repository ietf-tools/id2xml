#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

#$ENV{"DBPATH"} = "/export/home/mlee/database";
$ENV{"DBPATH"} = "/usr/informix/databases";
#$ENV{"DBNAME"} = "testdb";
$ENV{"DBNAME"} = "people";

$dateStr = get_current_date();

$html_txt = qq{<html>
<TITLE>Item by AD</TITLE>
</HEAD>

<body>
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
   10 => 'Proposed Working Groups'
);
my $pGroupFlag=0;
my $pTokenName = "";
my $pwg_html_txt = "";
$sqlStr = qq{select rfc_flag,a.id_document_tag,ballot_id,status_date,
primary_flag,group_flag,token_email,email_display,note,token_name
from id_internal a,internet_drafts b
where a.id_document_tag = b.id_document_tag and b.b_approve_date is null
order by token_name,group_flag, ballot_id, primary_flag DESC
};
@List = db_select_multiple($sqlStr);
for $array_ref (@List) {
   ($rfc_flag,$id_document_tag,$temp_val,$status_date,
$pFlag,$gFlag,$token_email,$token_name,$note,$TokenName) = @$array_ref;
   $TokenName = rm_tr($TokenName);
   if ($rfc_flag) {
      $sqlStr = qq{
	  Select r.rfc_name,s.status_value,r.area_acronym 
	  from rfcs r, id_intended_status s
	  where r.rfc_number = $id_document_tag
	  AND r.intended_status_id = s.intended_status_id
	  };
	 ($doc_name,$statusStr,$gAcronym) = db_select($sqlStr);
	 $filename = "rfc${id_document_tag}.txt";
	 $filename2 = "rfc/rfc${id_document_tag}.txt";
   } else {
     $sqlStr = qq{
	 Select i.id_document_name,i.filename,i.revision,s.status_value,m.acronym
	 from internet_drafts i,id_intended_status s,area_group p,acronym m
	 Where i.id_document_tag = $id_document_tag
	 AND i.intended_status_id = s.intended_status_id
	 AND i.b_approve_date is NULL
	 AND i.group_acronym_id = p.group_acronym_id
	 AND p.area_acronym_id = m.acronym_id
	 };
	 ($doc_name,$filename,$revision,$statusStr,$gAcronym) = db_select($sqlStr);
     $filename = rm_tr($filename);
	 $filename1 = $filename;
     $filename2 = "internet-drafts/${filename}-${revision}.txt";
	 $filename = "${filename}-${revision}.txt";
   }
   if ($TokenName ne $pTokenName) {
      my @temp = split ' ',$TokenName;
	  my $token_ref = @temp[0];
      $html_txt .= qq{
	  $pwg_html_txt
	  </table>
	  <hr>
	  <center><a name="$token_ref"><h2>Status Items of $TokenName</h2></a></center>
	  };

	    $qTokenName = db_quote($TokenName);
		$sqlStr2=qq{select a.name,a.acronym,g.status_date,m.acronym         
		from group_internal g, acronym a, area_group p, acronym m
		where g.token_name = $qTokenName
		AND g.group_acronym_id = a.acronym_id
		AND g.group_acronym_id = p.group_acronym_id
		ANd p.area_acronym_id = m.acronym_id
		order by g.status_date DESC
		};

		my @gList = db_select_multiple($sqlStr2);
		my $head_flag = 0;
		$pwg_html_txt = "";
		for $gArray_ref (@gList) {
		   ($gname,$gacronym,$gstatus_date,$gaAcronym) = @$gArray_ref;
		   $gname = rm_tr($gname);
		   $gacronym = rm_tr($gacronym);
		   $gstatus_date = convert_date($gstatus_date);
		   if (defined($gaAcronym)) {
		      $garea = uc($gaAcronym);
		   } else {
		      $garea = "UND";
		   }
	       unless ($head_flag) {
  			    $pwg_html_txt = qq{
				</table>
	            <h2>Proposed Working Groups</H2>
	            <table><tr><th>Area<th>Submitted<th></tr>
				};
			    $head_flag = 1;
	       }
	      $pwg_html_txt .= qq{
		   <tr><td>$garea</td><td nowrap>$gstatus_date</td>
		   <td>$gname ($gacronym)</td></tr>
		   <tr><td colspan="2"></td>
		   <td><A HREF="/IESG/internal/BALLOT/${gacronym}-charter.txt">${gacronym}-charter.txt</a></td></tr>
		   };
        }



	  $pTokenName = $TokenName;
   }
   if ($gFlag != $pGroupFlag) {
      $pGroupFlag = $gFlag;
      $gName = $group_name{$gFlag};
      $refName = "grp".$gFlag;
      if ($gFlag > 1) {
          $html_txt .= "</table>\n";
       }
      $html_txt .= qq{
     <h2>$gName</H2>
     <table><tr><th>Area<th>Date<th></tr>
      };
   }
   $doc_name = rm_tr($doc_name);
   $status_date = convert_date($status_date);
   if (defined($gAcronym)) {
      $area = uc($gAcronym);
   } else {
      $area = "UND";
   }
   if ($pFlag) {
      $_ = "/usr/local/etc/httpd/htdocs/IESG/internal/BALLOT/${filename1}.bal";
      if (-e) {
         $html_txt .= qq{<tr><td><a href="/IESG/internal/BALLOT/${filename1}.bal">$area</a></td>};
      }
      else {
         $html_txt .= qq{<tr><td>$area</td>};
      }
      $html_txt .= qq{<td nowrap>$status_date</td>};
   } else {
      $html_txt .= qq{<tr><td></td><td nowrap></td>};
   }
   $html_txt .= qq{<td>$doc_name ($statusStr)</td></tr>
<tr><td></td><td></td>
<td><A HREF="/${filename2}">${filename}</a> </td></tr>
};
#   if (defined($token_email) and $pFlag) {
#      $html_txt .= qq{<tr><td></td><td>Token:</td>
#      <td><a href="mailto:$token_email">$token_name</a></td></tr>
#      };
#   }
   if (defined($note) and $pFlag) {
      $html_txt .= qq{<tr><td></td><td>Note:</td>
      <td>$note</td></tr>
      };
   }
}



$html_txt .= qq{
</TABLE>
<HR>
<b><A href="http://www.rfc-editor.org/queue.html">RFC Editor Queue</a></b>
<p>


<!-- begin new footer -->
<HR>

<i>This page produced by the <A HREF="mailto:iesg-secretary\@ietf.org">IETF Secretariat</a> 
for the <A HREF="mailto:iesg\@ietf.org">IESG</A></i>
<p>
</body></html>
};
if (defined($ARGV[0]) and $ARGV[0] eq "-deploy") {
   open (OUTFILE,">/usr/local/etc/httpd/htdocs/IESG/internal/single.html");
} else {
   open (OUTFILE,">/usr/local/etc/httpd/htdocs/IESG/SINGLE.html");
}
print OUTFILE $html_txt;
close(OUTFILE);

exit;




