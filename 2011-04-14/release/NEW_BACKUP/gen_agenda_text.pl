#!/usr/local/bin/perl -w

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

$TESTDB = 0;
$INFORMIX = 1;
$MYSQL = 2;

($db_mode,$CURRENT_DATE,$CONVERT_SEED,$is_null) = init_database($MYSQL);


$dateStr = get_current_date();
$ret_txt = qq{
        INTERNET ENGINEERING STEERING GROUP (IESG)
      Agenda for the $date_str IESG Teleconference

1. Administrivia

  o Roll Call
  o Bash the Agenda
  o Approval of the Minutes
    - $date_str
  o Review of Action Items

OUTSTANDING TASKS
   Last updated: $date_str

<OUTSTANDING ITEM LIST>
.
.
.


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
   12 => 'Individual via RFC Editor'
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
     ($doc_name,$filename,$revision,$statusStr,$gAcronym) = rm_tr(db_select($sqlStr));
     next unless (my_defined($doc_name));
     $filename = "${filename}-${revision}.txt";
   }
   if ($gFlag != $pGroupFlag) {
      $pGroupFlag = $gFlag;
      $gName = $group_name{$gFlag};
      $refName = "grp".$gFlag;
      if ($gFlag > 1) {
          $ret_txt .= "\n\n";
       }
      $ret_txt .= qq{
${indexCnt}. $gName
};
      $indexCnt++;
   }
   $statusStr = rm_tr($statusStr);
   $one_line = "$doc_name ($statusStr)";
   $one_line = indent_text2($one_line,4);
   $ret_txt .= qq {  o $one_line  
           <$filename>
};
   if (my_defined($token_email) and $pFlag) {
      $ret_txt .= qq {    Token: $token_name
};
   }
   if (my_defined($note) and $pFlag) {
      $one_line = "Note: " . $note;
      $one_line = indent_text2($one_line,4);
      $ret_txt .= "    $one_line\n"; 
   }
}
$sqlStr = "select group_acronym_id,note,token_name from group_internal where agenda=1";
@List = db_select_multiple($sqlStr);
if ($#List > -1) {
   $ret_txt .= qq {
${indexCnt}. Proposed Working Group
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


my $template_html = db_select("select note from id_internal where group_flag = 100");
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
$ret_txt .= qq{
${news_index}. Working Group News we can use

${iab_index}. IAB News we can use

${mi_index}. Management Issues
$template_html
};

print $ret_txt;

exit;




