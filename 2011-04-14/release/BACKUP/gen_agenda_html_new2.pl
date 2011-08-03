#!/usr/local/bin/perl -w

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

init_database();


$dateStr = get_current_date();
$telechat_date = db_select("select date1 from telechat_dates");
$not_via_rfc_where = "AND via_rfc_editor = 0\n";
$via_rfc_where = "AND via_rfc_editor = 1\n";
$gap = "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ";
$table_header = qq{
<table border="0" cellspacing="0" cellpadding="0">
<tr>
<td>$gap</td>
<td>
};
$table_footer = "</td></tr></table>\n";
$html_txt = qq{<html>
<TITLE>IESG Agenda</TITLE>
</HEAD>

<center><h1>IESG Agenda</H1></center>
Good approximation of what will be included in the Agenda of next Telechat ($telechat_date).<br><br>
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

my $indexCnt = 2;
$html_txt .= get_agenda_body("PA");
$html_txt .= get_agenda_body("DA");
$html_txt .= get_wg_action();
$html_txt .= get_agenda_footer();

open (OUTFILE,">/usr/local/etc/httpd/htdocs/IESG/internal/agenda_new.html");
print OUTFILE $html_txt;
close(OUTFILE);
                                                                                               
exit;
                                                                                               

sub get_agenda_body {
  my $group_type = shift;
  my $heading;
  my $id_list = "";
  my $pReturningItem = -1;
  if ($group_type eq "PA") {  #generate Protocol Action list
    $heading = "Protocol Actions";
    $id_list = "1,2,6,7";
  } else {  #generate Docuement Action list
    $heading = "Document Actions";
    $id_list = "3,5";
  }
  my $valid_sql = "select count(*) from id_internal a, internet_drafts b, telechat_dates where a.id_document_tag=b.id_document_tag and agenda=1 and telechat_date=date1 and intended_status_id in ($id_list) ";
  my $valid = db_select($valid_sql);
  return unless($valid);
  my $html_txt = qq{<h2>${indexCnt}. $heading</H2>
  $table_header
  };
  $indexCnt++;

  my $sqlStr_base = qq{select rfc_flag,id_internal.id_document_tag,status_date,
primary_flag,token_email,email_display,note,acronym
from id_internal, internet_drafts, acronym, telechat_dates 
where group_flag < 99
AND agenda = 1
AND id_internal.id_document_tag = internet_drafts.id_document_tag
AND internet_drafts.intended_status_id in ($id_list)
AND id_internal.area_acronym_id = acronym.acronym_id
AND telechat_date = date1
};
  $html_txt .= get_wg_individual($sqlStr_base,"WG",$valid_sql,$group_type);
  $html_txt .= get_wg_individual($sqlStr_base,"IND",$valid_sql,$group_type);
  $html_txt .= $table_footer;
  return $html_txt;
}

sub get_wg_individual {
  my $sqlStr = shift;
  my $type = shift;
  my $valid_sql = shift;
  my $group_type = shift;
  my $heading = "";
  if ($type eq "IND") {
    $heading = "Individual Submissions";
    $sqlStr .= "AND group_acronym_id = 1027\n";
    $valid_sql .= "AND group_acronym_id = 1027\n";
    if ($group_type eq "DA") {
      return "" unless (db_select($valid_sql));
      my $html_txt = get_via_rfc_ad($sqlStr,"AD",$valid_sql);
      $html_txt .= get_via_rfc_ad($sqlStr,"RFC",$valid_sql);
      $html_txt .= $table_footer;
      return $html_txt;
    }
  } else {
    $heading = "WG Submissions";
    $sqlStr .= "AND group_acronym_id <> 1027\n";
    $valid_sql .= "AND group_acronym_id <> 1027\n";
  }
  $sqlStr .= $not_via_rfc_where;
  $valid_sql .= $not_via_rfc_where;
  my $valid = db_select($valid_sql);
  return "" unless ($valid); 
  my $html_txt = "<h3>$heading</h3>\n$table_header";
  $html_txt .= get_new_returning($sqlStr,"NEW",$valid_sql);
  $html_txt .= get_new_returning($sqlStr,"RET",$valid_sql);
  $html_txt .= $table_footer;
  return $html_txt;
}

sub get_via_rfc_ad {
  my $sqlStr = shift;
  my $type = shift;
  my $valid_sql = shift;
  my $heading = "<h3>Individual Submissions ";
  if ($type eq "AD") {
    $heading .= "Via AD";
    $sqlStr .= $not_via_rfc_where;
    $valid_sql .= $not_via_rfc_where;
  } else {
    $heading .= "Via RFC Editor";
    $sqlStr .= $via_rfc_where;
    $valid_sql .= $via_rfc_where;
  }
  return "" unless (db_select($valid_sql));
  my $html_txt = "$heading</h3>\n$table_header";
  $html_txt .= get_new_returning($sqlStr,"NEW",$valid_sql);
  $html_txt .= get_new_returning($sqlStr,"RET",$valid_sql);
  $html_txt .= $table_footer;
  return $html_txt;
}

sub get_new_returning {
  my $sqlStr = shift;
  my $type = shift;
  my $valid_sql = shift;
  my $heading = "";
  if ($type eq "NEW") {
    $heading = "New Item";
    $sqlStr .= "AND returning_item = 0\n";
    $valid_sql .= "AND returning_item = 0\n";
  } else {
    $heading = "Returning Item";
    $sqlStr .= "AND returning_item = 1\n";
    $valid_sql .= "AND returning_item = 1\n";
  }
  my $valid = db_select($valid_sql);
  return "" unless ($valid);
  my $html_txt = "<b>$heading</b>\n";
  $sqlStr .= "order by primary_flag DESC, status_date";
  $html_txt .= "<table><tr><th> &nbsp; &nbsp; &nbsp; </th><th>Area<th>Date<th></tr>\n";

  my @List = db_select_multiple($sqlStr);
  for $array_ref (@List) {
    ($rfc_flag,$id_document_tag,$status_date,$pFlag,$token_email,$token_name,$note,$area_acronym) = rm_tr(@$array_ref);
    if ($rfc_flag) {
      $sqlStr = qq{
	  Select r.rfc_name,s.status_value,r.area_acronym 
	  from rfcs r, id_intended_status s
	  where r.rfc_number = $id_document_tag
	  AND r.intended_status_id = s.intended_status_id
	  };
	 ($doc_name,$statusStr,$gAcronym) = rm_tr(db_select($sqlStr));
	 $filename = "rfc${id_document_tag}.txt";
	 $filename1 = $filename;
	 $filename2 = "rfc/rfc${id_document_tag}.txt";
    } else {
     $sqlStr = qq{
	 Select i.id_document_name,i.filename,i.revision,s.status_value,m.acronym
	 from internet_drafts i,id_intended_status s,area_group p,acronym m
	 Where i.id_document_tag = $id_document_tag
	 AND i.intended_status_id = s.intended_status_id
	 AND (i.b_approve_date = '0000-00-00'  or i.b_approve_date is NULL) 
	 AND i.group_acronym_id = p.group_acronym_id
	 AND p.area_acronym_id = m.acronym_id
	 };
	 ($doc_name,$filename,$revision,$statusStr,$gAcronym) = rm_tr(db_select($sqlStr));
	 next unless (my_defined($doc_name));
	 $filename1 = $filename;
         $filename2 = "/internet-drafts/${filename}-${revision}.txt";
	 $filename = "${filename}-${revision}.txt";
    }
    $status_date = convert_date($status_date,2);
    $status_date = convert_date($status_date);
    $status_date = "" unless ($status_date) ;
    $area = rm_tr(uc($area_acronym));
    if ($area eq "ADM" or $area eq "UND") {
      $area = rm_tr(uc($area_acronym));
      $area = "UND" unless (defined($area));
    }
    $filename1 =~ s/.txt//;
    if ($pFlag) {
      $_ = "/usr/local/etc/httpd/htdocs/IESG/EVALUATIONS/${filename1}.bal";
      if (-e) {
         $html_txt .= qq{<tr><td></td><td><a href="/IESG/EVALUATIONS/${filename1}.bal">$area</a></td>}; #"
      }
      else {
         $html_txt .= qq{<tr><td></td><td>$area</td>};
      }
      $html_txt .= qq{<td nowrap>$status_date</td>};

    } else {
      $html_txt .= qq{<tr><td></td><td></td><td nowrap></td>};
    }
    $statusStr = rm_tr($statusStr);
    $html_txt .= qq{<td>$doc_name ($statusStr)</td></tr>
<tr><td></td><td></td><td></td>
<td><A HREF="${filename2}">${filename}</a> </td></tr>
};
#"
    $one_line = "$doc_name ($statusStr)";
    $one_line = indent_text2($one_line,5);
    if (my_defined($token_email) and $pFlag) {
      $html_txt .= qq{<tr><td></td><td></td><td>Token:</td>
      <td><a href="mailto:$token_email">$token_name</a></td></tr>
      };
    }
    if (my_defined($note) and $pFlag) {
      $html_txt .= qq{<tr><td></td><td></td><td>Note:</td>
      <td>$note</td></tr>
      };
    }
  }
  $html_txt .= "</table>\n";
  return $html_txt;
}

sub get_wg_action {
  my $sqlStr = "select group_acronym_id,note,token_name from group_internal where agenda=1";
  my $html_txt = "";
  my @List = db_select_multiple($sqlStr);
if ($#List > -1) {
   $html_txt = qq {
<h2>${indexCnt}. Working Group Actions</h2>
     <table><tr><th>Area<th>Date<th></tr>
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
   if(my_defined($token_name)) {
     my $pTag = db_select("select person_or_org_tag from iesg_login where first_name = '$token_name'");
     $pTag = 0 unless (my_defined($pTag));
     my $email = get_email($pTag);
     $html_txt .= "<tr><td></td><td>Token:</td><td><a href=\"mailto:$email\">$token_name</a></td></tr>\n";
   }
   if (my_defined($note)) {
     $html_txt .= "<tr><td></td><td></td><td>Note:</td><td>$note</td></tr>";
   }
} 
$html_txt .= "</table>\n";
  return $html_txt;
}

sub get_agenda_footer {
  my $template_html = db_select("select note from id_internal where group_flag = 100");
  $news_index = $indexCnt;
  $iab_index = $news_index + 1;
  $mi_index = $iab_index + 1;
  return qq{
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

}

