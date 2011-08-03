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
$outfile_name = "status.txt";
$line = "--------------------------------------------------------------------------------";
$html_txt = qq{<html>
<TITLE>IESG Status of Items</TITLE>
</HEAD>

<center><h1>IESG Status of Items</H1></center>
<i>Generated $dateStr</i><br>

};

$text_txt = qq {
IESG Status of Items

Generated $dateStr

};
###status.html
$html_txt2 = qq{<html>  
<TITLE>IESG Status of Items</TITLE>
</HEAD>

<center><h1>IESG Status of Items</H1></center>
<i>Generated $dateStr</i><br>

};

$pCur_state = 0;

$sqlStr = qq{select rfc_flag,id_document_tag,ballot_id,status_date,
cur_state,token_email,email_display,note,area_acronym
from id_internal
where group_flag < 15 AND primary_flag = 1 AND cur_state <> 41
order by cur_state, status_date, ballot_id
};
@List = db_select_multiple($sqlStr);
for $array_ref (@List) {
    ($rfc_flag,$id_document_tag,$ballot_id,$status_date,$cur_state,$token_email,$token_name,$note,$area_acronym) = @$array_ref;
     my ($doc_name,$filename,$filename1,$filename2,$revision,$statusStr,$gAcronym) = get_sqlStr($rfc_flag,$id_document_tag);
     next unless (my_defined($doc_name));
	 
   if ($cur_state != $pCur_state) {
      $pCur_state = $cur_state;
      my $state_name = rm_tr(db_select("select document_state_val from ref_doc_states where document_state_id = $cur_state"));
      $refName = "grp".$state_name;
      if ($cur_state > 1) {
          $html_txt .= "</table>\n";
          $html_txt2 .= "</table>\n";
		  $text_txt .= "\n${line}\n";
       }
      $html_txt .= qq{
     <A name="$refName"><h2>$state_name</H2></A>
     <table><tr><th>Area<th>Date<th></tr>
      };
      $html_txt2 .= qq{
     <A name="$refName"><h2>$state_name</H2></A>
     <table><tr><th>Area<th>Date<th></tr>
      };
	  $text_txt .= qq{
$gName
Area    Date
$line
};
   }
   $doc_name = rm_tr($doc_name);
   $status_date = convert_date($status_date,2);
   $status_date = convert_date($status_date);
   if ($gFlag == 9) {
      $area = rm_tr(uc($area_acronym));
   } else {
      if (defined($gAcronym)) {
         $area = rm_tr(uc($gAcronym));
      } else {
         $area = "UND";
      }
   }
   if ($area eq "ADM" or $area eq "UND") {
      $area = rm_tr(uc($area_acronym));
	  unless (defined($area)) {
	     $area = "UND";
	  }
   }
   my $pFlag = 1;
   my ($r_html_txt,$r_html_txt2,$r_text_txt) = get_list_html($area,$pFlag,$filename,$filename1,$filename2,$status_date,$statusStr,$note,$token_name,$token_email,$doc_name);
   $html_txt .= $r_html_txt;
   $html_txt2 .= $r_html_txt2;
   $text_txt .=  $r_text_txt;
   $sqlStr = qq{select rfc_flag,id_document_tag,status_date,
   token_email,email_display,note,area_acronym
   from id_internal
   where ballot_id = $ballot_id AND (primary_flag = 0 OR primary_flag is null)
   order by status_date
   };
   my @subList = db_select_multiple($sqlStr);
   for $sub_array_ref (@subList) {
    ($rfc_flag,$id_document_tag,$status_date,$token_email,$token_name,$note,$area_acronym) = @$sub_array_ref;
    ($doc_name,$filename,$filename1,$filename2,$revision,$statusStr,$gAcronym) = get_sqlStr($rfc_flag,$id_document_tag);
     next unless (my_defined($doc_name));      
     my $pFlag = 0;
     ($r_html_txt,$r_html_txt2,$r_text_txt) = get_list_html($area,$pFlag,$filename,$filename1,$filename2,$status_date,$statusStr,$note,$token_name,$token_email,$doc_name);
     $html_txt .= $r_html_txt;
     $html_txt2 .= $r_html_txt2;
     $text_txt .=  $r_text_txt;
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
$html_txt2 .= qq{
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
   open (OUTFILE,">/usr/local/etc/httpd/htdocs/IESG/internal/iesg.html");
   open (OUTFILE2,">/usr/local/etc/httpd/htdocs/IESG/status.html");
   print OUTFILE2 $html_txt2;
   close (OUTFILE2);
} elsif (defined($ARGV[0] and $ARGV[0] eq "-text")) {
   if (defined($ARGV[1] and -e $ARGV[1])) {
      $output_path = $ARGV[1];
   }
   open (OUTFILE,">${output_path}/${outfile_name}");
   print OUTFILE $text_txt;
   close(OUTFILE);
   exit(2);
} else {
   open (OUTFILE,">/usr/local/etc/httpd/htdocs/IESG/IESG2.html");
}
print OUTFILE $html_txt;
close(OUTFILE);

exit;

sub get_sqlStr {
   my $rfc_flag = shift;
   my $id_document_tag = shift;
   my $sqlStr;
   my ($doc_name,$filename,$filename1,$filename2,$revision,$statusStr,$gAcronym);
   if ($rfc_flag) {
      $sqlStr = qq{
	  Select r.rfc_name,s.status_value,r.area_acronym 
	  from rfcs r, id_intended_status s
	  where r.rfc_number = $id_document_tag
	  AND r.intended_status_id = s.intended_status_id
	  };
	 ($doc_name,$statusStr,$gAcronym) = db_select($sqlStr);
	 $filename = "rfc${id_document_tag}.txt";
	 $filename1 = "rfc${id_document_tag}";
	 $filename2 = "rfc/rfc${id_document_tag}.txt";
   } else {
     $sqlStr = qq{
	 Select i.id_document_name,i.filename,i.revision,s.status_value,m.acronym
	 from internet_drafts i,id_intended_status s,area_group p,acronym m
	 Where i.id_document_tag = $id_document_tag
	 AND i.intended_status_id = s.intended_status_id
	 AND i.b_approve_date $is_null 
	 AND i.group_acronym_id = p.group_acronym_id
	 AND p.area_acronym_id = m.acronym_id
	 };
	 ($doc_name,$filename,$revision,$statusStr,$gAcronym) = db_select($sqlStr);
	 
     $filename = rm_tr($filename);
	 $filename1 = $filename;
	 if (my_defined($revision)) {
        $filename2 = "internet-drafts/${filename}-${revision}.txt";
	    $filename = "${filename}-${revision}.txt";
	 }
   }
   
   return $doc_name,$filename,$filename1,$filename2,$revision,$statusStr,$gAcronym;
}

sub get_list_html {
   my ($area,$pFlag,$filename,$filename1,$filename2,$status_date,$statusStr,$note,$token_name,$token_email,$doc_name) = @_;
   my ($html_txt,$html_txt2,$text_txt);
   $_ = $filename1;
   s/-\d\d.txt//;
   s/.txt//;
   $filename1 = $_;
   if ($pFlag) {
      $_ = "/usr/local/etc/httpd/htdocs/IESG/internal/BALLOT/${filename1}.bal";
      if (-e) {
         $html_txt .= qq{<tr><td><a href="/IESG/internal/BALLOT/${filename1}.bal">$area</a></td>};
      }
      else {
         $html_txt .= qq{<tr><td>$area</td>};
      }
	  $html_txt2 .= qq{<tr><td>$area</td>};
      $html_txt .= qq{<td nowrap>$status_date</td>};
      $html_txt2 .= qq{<td nowrap>$status_date</td>};
	  $text_txt .= qq{
$area   $status_date};
   } else {
      $html_txt .= qq{<tr><td></td><td nowrap></td>};
      $html_txt2 .= qq{<tr><td></td><td nowrap></td>};
   }
   $statusStr = rm_tr($statusStr);
   $html_txt .= qq{<td>$doc_name ($statusStr)</td></tr>
<tr><td></td><td></td>
<td><A HREF="/${filename2}">${filename}</a> </td></tr>
};
   $html_txt2 .= qq{<td>$doc_name ($statusStr)</td></tr>
<tr><td></td><td></td>
<td><A HREF="/${filename2}">${filename}</a> </td></tr>
};
   $text_txt .= qq{    $doc_name ($statusStr)  
           $filename};
   if (my_defined($token_email) and $pFlag) {
      $html_txt .= qq{<tr><td></td><td>Token:</td>
      <td><a href="mailto:$token_email">$token_name</a></td></tr>
      };
      $html_txt2 .= qq{<tr><td></td><td>Token:</td>
      <td><a href="mailto:$token_email">$token_name</a></td></tr>
      };
	  $text_txt .= "\n          Token: $token_name";
   }
   if (my_defined($note) and $pFlag) {
      $html_txt .= qq{<tr><td></td><td>Note:</td>
      <td>$note</td></tr>
      };
      $html_txt2 .= qq{<tr><td></td><td>Note:</td>
      <td>$note</td></tr>
      };
	  $note = rm_tr($note);
	  $text_txt .= "\n          Note: $note";
   }
   $text_txt .="\n";
   return ($html_txt,$html_txt2,$text_txt);
}


