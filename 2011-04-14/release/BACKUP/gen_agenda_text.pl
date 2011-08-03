#!/usr/local/bin/perl -w

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

init_database();

my ($agenda_date_str,$minute_date_str) = @ARGV;
my $outstanding_str = "";
my $outstanding_date_str = db_select("select max(last_updated_date) from outstanding_tasks");
my @osList = db_select_multiple("select item_text from outstanding_tasks where done=1");
for $array_ref (@osList) {
  my ($item_text) = rm_tr(@$array_ref);
  $item_text = "o " . $item_text;
  $item_text = indent_text($item_text,2);
  $outstanding_str .= "$item_text\n";
}
#my $telechat_date = db_select("select date1 from telechat_dates");
$ret_txt = qq{
        INTERNET ENGINEERING STEERING GROUP (IESG)
      Agenda for the $agenda_date_str IESG Teleconference
                                                                                
1. Administrivia
                                                                                
  o Roll Call
  o Bash the Agenda
  o Approval of the Minutes
    - $minute_date_str
  o Review of Action Items
                                                                                
OUTSTANDING TASKS
   Last updated: $outstanding_date_str
                                                                                
$outstanding_str
                                                                                
};




$not_via_rfc_where = "AND via_rfc_editor = 0\n";
$via_rfc_where = "AND via_rfc_editor = 1\n";
$gap = "  ";

my $indexCnt = 2;
$ret_txt .= get_agenda_body("PA");
$ret_txt .= get_agenda_body("DA");
$ret_txt .= get_wg_action();
$ret_txt .= get_agenda_footer();

print $ret_txt;
                                                                                               
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
  #return "" unless (db_select($valid_sql));
  my $ret_txt = "${indexCnt}. $heading\n\n";

  my $sqlStr_base = qq{select rfc_flag,id_internal.id_document_tag,
primary_flag,token_email,email_display,note
from id_internal, internet_drafts, telechat_dates 
WHERE agenda = 1
AND id_internal.id_document_tag = internet_drafts.id_document_tag
AND internet_drafts.intended_status_id in ($id_list)
AND telechat_date = date1
};
  $ret_txt .= get_wg_individual($sqlStr_base,"WG",$valid_sql,$group_type);
  $ret_txt .= get_wg_individual($sqlStr_base,"IND",$valid_sql,$group_type);
  $ret_txt .= "\n";
  $indexCnt++;
  return $ret_txt;
}

sub get_wg_individual {
  my $sqlStr = shift;
  my $type = shift;
  my $valid_sql = shift;
  my $group_type = shift;
  my $heading = "";
  my $hd_num;
  if ($type eq "IND") {
    $hd_num = "${indexCnt}.2";
    $heading = "$hd_num Individual Submissions";
    $sqlStr .= "AND group_acronym_id = 1027\n";
    $valid_sql .= "AND group_acronym_id = 1027\n";
    if ($group_type eq "DA") {
      #return "" unless (db_select($valid_sql));
      #my $ret_txt = "$gap $heading\n";
      my $ret_txt .= get_via_rfc_ad($sqlStr,"AD",$valid_sql);
      $ret_txt .= get_via_rfc_ad($sqlStr,"RFC",$valid_sql);
      $ret_txt .= "\n";
      return $ret_txt;
    }
  } else {
    $hd_num = "${indexCnt}.1";
    $heading = "$hd_num WG Submissions";
    $sqlStr .= "AND group_acronym_id <> 1027\n";
    $valid_sql .= "AND group_acronym_id <> 1027\n";
  }
  $sqlStr .= $not_via_rfc_where;
  $valid_sql .= $not_via_rfc_where;
  #return "" unless (db_select($valid_sql));
  my $ret_txt = "$gap $heading\n";
  $ret_txt .= get_new_returning($sqlStr,"NEW",$valid_sql,$hd_num);
  $ret_txt .= get_new_returning($sqlStr,"RET",$valid_sql,$hd_num);
  $ret_txt .= "\n";
  return $ret_txt;
}

sub get_via_rfc_ad {
  my $sqlStr = shift;
  my $type = shift;
  my $valid_sql = shift;
  my $hd_num;
  my $heading;
  if ($type eq "AD") {
    $hd_num = "${indexCnt}.2";
    $heading .= "$hd_num Indiviual Submissions Via AD";
    $sqlStr .= $not_via_rfc_where;
    $valid_sql .= $not_via_rfc_where;
  } else {
    $hd_num = "${indexCnt}.3";
    $heading .= "$hd_num Indiviual Submissions Via RFC Editor";
    $sqlStr .= $via_rfc_where;
    $valid_sql .= $via_rfc_where;
  }
  #return "" unless (db_select($valid_sql));
  my $ret_txt = "$gap $heading\n";
  $ret_txt .= get_new_returning($sqlStr,"NEW",$valid_sql,$hd_num);
  $ret_txt .= get_new_returning($sqlStr,"RET",$valid_sql,$hd_num);
  $ret_txt .= "\n";
  return $ret_txt;
}

sub get_new_returning {
  my $sqlStr = shift;
  my $type = shift;
  my $valid_sql = shift;
  my $hd_num = shift;
  my $heading = "";
  if ($type eq "NEW") {
    $heading = "${hd_num}.1 New Item";
    $sqlStr .= "AND returning_item = 0\n";
    $valid_sql .= "AND returning_item = 0\n";
  } else {
    $heading = "${hd_num}.2 Returning Item";
    $sqlStr .= "AND returning_item = 1\n";
    $valid_sql .= "AND returning_item = 1\n";
  }
  #return "" unless (db_select($valid_sql));
  return "$gap $gap $heading\n $gap $gap $gap NONE\n" unless (db_select($valid_sql));
  my $ret_txt = "$gap $gap $heading\n";
  $sqlStr .= "order by ballot_id, primary_flag DESC, status_date";

  my @List = db_select_multiple($sqlStr);
  for $array_ref (@List) {
    ($rfc_flag,$id_document_tag,$pFlag,$token_email,$token_name,$note) = rm_tr(@$array_ref);
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
   $statusStr = rm_tr($statusStr);
   $one_line = "$doc_name ($statusStr)";
   my $indent = 11;
   my $ex_space = "";
   unless ($pFlag) {
     $indent = $indent+2;
     $ex_space = "  ";
   }
   $one_line = indent_text2($one_line,$indent);
   $ret_txt .= qq {$gap $gap $gap$ex_space o $one_line
           $ex_space<$filename>
};
   if (my_defined($token_email) and $pFlag) {
      $ret_txt .= qq {$gap $gap $gap   Token: $token_name
};
   }
   if (my_defined($note) and $pFlag) {
      $one_line = "Note: " . $note;
      $one_line = indent_text2($one_line,11);
      $ret_txt .= "$gap $gap $gap   $one_line\n";
   }
  }
  $ret_txt .= "\n";
  return $ret_txt;
}

sub get_wg_action {
  my $ret_txt = "";
  $sqlStr = "select group_acronym_id,note,token_name from group_internal where agenda=1";
  @List = db_select_multiple($sqlStr);
  if ($#List > -1) {
    $ret_txt .= qq {
${indexCnt}. Working Group Actions
};
    $indexCnt++;
  }
                                                                                
  for $array_ref (@List) {
    my ($group_acronym_id,$note,$token_name) = rm_tr(@$array_ref);
    my $group_acronym = rm_tr(db_select("select acronym from acronym where acronym_id = $group_acronym_id"));
                                                                                
    my $group_name = rm_tr(db_select("select name from acronym where acronym_id = $group_acronym_id"));
    $ret_txt .= "  o $group_name\n";
    if(my_defined($token_name)) {
      $ret_txt .= "    Token: $token_name\n";
    }
    if (my_defined($note)) {
       $one_line = "Note: " . $note;
       $one_line = indent_text2($one_line,4);
       $ret_txt .= "    $one_line\n";
    }
  }

  return $ret_txt;
}

sub get_agenda_footer {
my $template_html = db_select("select template_text from templates where template_id = 1");
$template_html =~ s/<LI>/  o /g;
$template_html =~ s/<li>/  o /g;
$template_html =~ s/<UL>//g;
$template_html =~ s/<ul>//g;
$template_html =~ s/<\/ul>//g;
$template_html =~ s/<\/UL>//g;
$template_html =~ s/<\/a>//g;
$template_html =~ s/<\/A>//g;
$news_index = $indexCnt;
$iab_index = $news_index + 1;
$mi_index = $iab_index + 1;
return qq{
${news_index}. Working Group News we can use
                                                                                
${iab_index}. IAB News we can use
                                                                                
${mi_index}. Management Issues
$template_html
};

}

