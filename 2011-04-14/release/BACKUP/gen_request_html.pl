#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE';
use IETF_UTIL;
use IETF_DBUTIL;

$TESTDB = 0;
$INFORMIX = 1;
$MYSQL = 2;

($db_mode,$CURRENT_DATE,$CONVERT_SEED,$is_null) = init_database($MYSQL);

$html_txt = qq{<html>
<TITLE>Submissions to the IESG</TITLE>
</HEAD>

<center><h1>Submissions to the IESG</H1></center>
<table>
};


$sqlStr = qq{select i.id_document_name,i.filename,i.revision,a.status_date,b.status_value,m.acronym
from id_internal a, internet_drafts i, acronym m,id_intended_status b
where a.group_flag = 12
AND a.id_document_tag = i.id_document_tag
AND i.intended_status_id = b.intended_status_id
AND a.rfc_flag = 0
AND a.area_acronym_id = m.acronym_id
};

my @List = db_select_multiple($sqlStr);
for my $array_ref (@List) {
   my ($doc_name,$filename,$revision,$status_date,$statusStr,$gAcronym, $area_acronym) = @$array_ref;
   $doc_name = rm_tr($doc_name);
   $filename = rm_tr($filename);
   $status_date = convert_date($status_date,1);
   if (defined($gAcronym)) {
      $area = rm_tr(uc($gAcronym));
   } else {
      $area = "UND";
   }
   if ($area eq "ADM" or $area eq "UND") {
      $area = rm_tr(uc($area_acronym));

	  unless (my_defined($area)) {
	     $area = "UND";
	  }
   }

   $html_txt .= qq{
<tr><td width=35>$area</td><td width=95>$status_date</td><td>$doc_name ($statusStr)</td></tr>
<tr><td></td><td></td>
<td><b>${filename}-${revision}.txt</b></td></tr>
};
}

$sqlStr = qq{select r.rfc_number,r.rfc_name,a.status_date,b.status_value,r.area_acronym
from id_internal a, rfcs r, rfc_intend_status b
WHERE a.id_document_tag = r.rfc_number
AND a.rfc_flag = 1
AND a.group_flag = 12
AND r.intended_status_id = b.intended_status_id
};
@List = db_select_multiple($sqlStr);
for my $array_ref (@List) {
   my ($rfc_number,$doc_name,$status_date,$statusStr,$gAcronym) = @$array_ref;
   $doc_name = rm_tr($doc_name);
   $filename = rm_tr($filename);
   $status_date = convert_date($status_date,1);
   if (defined($gAcronym)) {
      $area = rm_tr(uc($gAcronym));
   } else {
      $area = "UND";
   }
   if ($area eq "ADM" or $area eq "UND") {
      $area = rm_tr(uc($area_acronym));
	  
	  unless (my_defined($area)) {
	     $area = "UND";
	  }
   }
   
   $html_txt .= qq{
<tr><td width=35>$area</td><td width=95>$status_date</td><td>$doc_name ($statusStr)</td></tr>
<tr><td></td><td></td>
<td><b>rfc${rfc_number}.txt</b></td></tr>
};
}



$html_txt .= qq{
</TABLE>
</body></html>
};
if (defined($ARGV[0]) and $ARGV[0] eq "-deploy") {
   open (OUTFILE,">/usr/local/etc/httpd/htdocs/IESG/internal/request.html");
   open (OUTFILE2,">/usr/local/etc/httpd/htdocs/IESG/request.html");
   print OUTFILE2 $html_txt;
   close(OUTFILE2);
} else {
   open (OUTFILE,">/usr/local/etc/httpd/htdocs/IESG/REQUEST.html");
}
print OUTFILE $html_txt;
close(OUTFILE);

exit;




