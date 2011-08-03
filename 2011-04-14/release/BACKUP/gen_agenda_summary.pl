#!/usr/local/bin/perl -w

use lib '/home/mlee/RELEASE/';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;


my ($agenda_date_str,$test_mode) = @ARGV;
$db_name = "ietf";
$db_name = "testdb" if ($test_mode);
init_database($db_name);
@v_number = ("Zero","One","Two","Three","Four","Five","Six","Seven","Eight","Nine");
$dateStr = get_current_date();
$timeStr = get_current_time();

$ret_txt = qq{
          INTERNET ENGINEERING STEERING GROUP (IESG)
Summarized Agenda for the $agenda_date_str IESG Teleconference

This agenda was generated at $timeStr EDT, $dateStr
                                                                                
1. Administrivia
                                                                                
  1.1 Roll Call
  1.2 Bash the Agenda
  1.3 Approval of the Minutes
  1.4 Review of Action Items
  1.5 Review of Projects
      http://www.unreason.com/jfp/iesg-projects
                                                                                
};




$not_via_rfc_where = "AND via_rfc_editor = 0\n";
$via_rfc_where = "AND via_rfc_editor = 1\n";
$gap = "";

my $indexCnt = 2;
$ret_txt .= get_agenda_body("PA");
$ret_txt .= get_agenda_body("DA");
$ret_txt .= get_wg_action();
$ret_txt .= get_agenda_footer();

print $ret_txt;
                                                                                               
exit;

sub gen_unassigned {
  my $type = shift;
  my $via_rfc_editor = shift;
  my $wg_submission = shift;
  my $date1 = db_select("select date1 from telechat_dates");
  my $sqlStr = "select rfc_flag,a.id_document_tag,token_email,token_name,ballot_id,note from id_internal a, internet_drafts b where (cur_state < 16 or cur_state > 21) and agenda=1 and via_rfc_editor=$via_rfc_editor and primary_flag=1 and a.id_document_tag=b.id_document_tag AND telechat_date = '$date1' ";
  if ($wg_submission) {
    $sqlStr .= " AND group_acronym_id <> 1027";
  } else {
    $sqlStr .= " AND group_acronym_id = 1027";
  }
  my $heading = "";
  if ($type eq "PA") {
    if ($wg_submission) {
      $heading = "2.1.3 For Action";
    } else {
      $heading = "2.2.3 For Action";
    }
    $sqlStr .= " AND intended_status_id in (1,2,6,7)";
  } else {
    if ($wg_submission) {
      $heading = "3.1.3 For Action";
    } else {
      if ($via_rfc_editor) {
        $heading = "3.3.3 For Action";
      } else { 
        $heading = "3.2.3 For Action";
      }
    }
    $sqlStr .= " AND intended_status_id in (3,5)";
  } 
  my @List = db_select_multiple($sqlStr);
  return "" if ($#List < 0);
  my $ret_txt = "$heading\n";

  my $total_count=$#List + 1;
  my $this_count = 0;
  my $valid_count = 0;
  for $array_ref (@List) {
    my ($rfc_flag,$id_document_tag,$token_email,$token_name,$ballot_id,$note) = @$array_ref;
    next if ($id_document_tag == 0 or !my_defined($id_document_tag));
    $this_count++;
    $ret_txt .= get_one_item($rfc_flag,$id_document_tag,$token_email,$token_name,$note,$ballot_id, $total_count,$this_count);
  }


  return $ret_txt;
}


sub get_agenda_body {
  my $group_type = shift;
  my $heading;
  my $id_list = "";
  my $pReturningItem = -1;
  if ($group_type eq "PA") {  #generate Protocol Action list
    $heading = qq{Protocol Actions
\tReviews should focus on these questions: "Is this document a
\treasonable basis on which to build the salient part of the Internet
\tinfrastructure? If not, what changes would make it so?"
};
    $id_list = "1,2,6,7";
    $rfc_list = "1,2,3,7";
  } else {  #generate Docuement Action list
    $heading = "Document Actions";
    $id_list = "3,5";
    $rfc_list = "4,5"
  }
  my $ret_txt = "${indexCnt}. $heading\n\n";

  my $sqlStr_base = qq{select rfc_flag,id_internal.id_document_tag,
token_email,email_display,note,ballot_id
from id_internal, internet_drafts, telechat_dates 
WHERE agenda = 1 and primary_flag=1
AND id_internal.id_document_tag = internet_drafts.id_document_tag
AND internet_drafts.intended_status_id in ($id_list)
AND telechat_date = date1
AND cur_state >= 16 and cur_state <= 21
};
  my $sqlStr_base_rfc = qq{select rfc_flag,id_internal.id_document_tag,
token_email,email_display,note,ballot_id
from id_internal, rfcs, telechat_dates
WHERE rfc_flag = 1 and agenda = 1 and primary_flag = 1
AND id_internal.id_document_tag = rfcs.rfc_number
AND rfcs.intended_status_id in ($rfc_list)
AND telechat_date = date1
AND cur_state >= 16 and cur_state <= 21
};

  $ret_txt .= get_wg_individual($sqlStr_base,$sqlStr_base_rfc,"WG",$group_type);
  $ret_txt .= get_wg_individual($sqlStr_base,$sqlStr_base_rfc,"IND",$group_type);
  $indexCnt++;
  return $ret_txt;
}

sub get_wg_individual {
  my $sqlStr = shift;
  my $sqlStr_rfc = shift;
  my $type = shift;
  my $group_type = shift;
  my $heading = "";
  my $hd_num;
  if ($type eq "IND") {
    $hd_num = "${indexCnt}.2";
    $heading = "$hd_num Individual Submissions";
    $sqlStr .= "AND group_acronym_id = 1027\n";
    $sqlStr_rfc .= "AND group_acronym = 'none'\n";
    if ($group_type eq "DA") {
      my $ret_txt = get_via_rfc_ad($sqlStr,$sqlStr_rfc,"AD");
      $ret_txt .= gen_unassigned("DA",0);
      $ret_txt .= get_via_rfc_ad($sqlStr,$sqlStr_rfc,"RFC");
      $ret_txt .= gen_unassigned("DA",1);
      $ret_txt .= "\n";
      return $ret_txt;
    }
  } else {
    $hd_num = "${indexCnt}.1";
    $heading = "$hd_num WG Submissions";
    $heading .= qq{
\tReviews should focus on these questions: "Is this document a reasonable
\tcontribution to the area of Internet engineering which it covers? If
\tnot, what changes would make it so?"
} if ($indexCnt == 3);
    $sqlStr .= "AND group_acronym_id <> 1027\n";
    $sqlStr_rfc .= "AND group_acronym <> 'none'\n";
  }
  $sqlStr .= $not_via_rfc_where;
  $sqlStr_rfc .= $not_via_rfc_where;
  my $ret_txt = "$gap$heading\n";
  $ret_txt .= get_new_returning($sqlStr,$sqlStr_rfc,"NEW",$hd_num);
  $ret_txt .= get_new_returning($sqlStr,$sqlStr_rfc,"RET",$hd_num);
  my $wg_submission = ($type eq "IND")?0:1;
  $ret_txt .= gen_unassigned($group_type,0,$wg_submission);
  $ret_txt .= "\n";
  return $ret_txt;
}

sub get_via_rfc_ad {
  my $sqlStr = shift;
  my $sqlStr_rfc = shift;
  my $type = shift;
  my $hd_num;
  my $heading;
  if ($type eq "AD") {
    $hd_num = "${indexCnt}.2";
    $heading .= qq{$hd_num Individual Submissions Via AD
\tReviews should focus on these questions: "Is this document a reasonable
\tcontribution to the area of Internet engineering which it covers? If
\tnot, what changes would make it so?"
};
    $sqlStr .= $not_via_rfc_where;
    $sqlStr_rfc .= $not_via_rfc_where;
  } else {
    $hd_num = "${indexCnt}.3";
    $heading .= qq{$hd_num Individual Submissions Via RFC Editor
\tReviews should focus on these questions: "Does this document
\trepresent an end run around the IETF's working groups
\tor its procedures? Does this document present an incompatible
\tchange to IETF technologies as if it were compatible?" Other
\tmatters may be sent to the RFC Editor in private review.
};
    $sqlStr .= $via_rfc_where;
    $sqlStr_rfc .= $via_rfc_where;
  }
  my $ret_txt = "$gap$heading\n";
  $ret_txt .= get_new_returning($sqlStr,$sqlStr_rfc,"NEW",$hd_num);
  $ret_txt .= get_new_returning($sqlStr,$sqlStr_rfc,"RET",$hd_num);
  return $ret_txt;
}

sub get_new_returning {
  my $sqlStr = shift;
  my $sqlStr_rfc = shift;
  my $type = shift;
  my $hd_num = shift;
  my $heading = "";
  if ($type eq "NEW") {
    $heading = "${hd_num}.1 New Item";
    $sqlStr .= "AND returning_item = 0\n";
    $sqlStr_rfc .= "AND returning_item = 0\n";
  } else {
    $heading = "${hd_num}.2 Returning Item";
    $sqlStr .= "AND returning_item = 1\n";
    $sqlStr_rfc .= "AND returning_item = 1\n";
  }
  my $ret_txt = "$gap$gap$heading\n";
  $sqlStr .= "order by ballot_id, primary_flag DESC, status_date";
  $sqlStr_rfc .= "order by ballot_id, primary_flag DESC, status_date";
  my @List = db_select_multiple($sqlStr);
  my @List_rfc = db_select_multiple($sqlStr_rfc);
  my $total_count = $#List + $#List_rfc + 2;
  return "$gap$gap$heading\nNONE\n" if ($#List < 0 and $#List_rfc < 0);
  my $this_count = 0;
  for $array_ref (@List) {
    $this_count++;
    $ret_txt .= get_one_item(@$array_ref,$total_count,$this_count);
  }
  for $array_ref (@List_rfc) {
    $this_count++;
    $ret_txt .= get_one_item(@$array_ref,$total_count,$this_count);
  }
  $ret_txt .= "\n";
  return $ret_txt;
}

sub get_one_item {
    my ($rfc_flag,$id_document_tag,$token_email,$token_name,$note,$ballot_id, $total_count,$this_count) = @_; 
    my $num_doc = db_select("select count(*) from id_internal where ballot_id=$ballot_id");
    my $ret_txt = "";
    if ($num_doc > 1) {
      $ret_txt = "$gap  o $v_number[$num_doc]-document ballot:  - $this_count of $total_count\n";
      my $sqlStr2 = qq{select c.id_document_tag,rfc_flag,filename,id_document_name,status_value,c.note,revision from internet_drafts a, id_intended_status b, id_internal c
where c.ballot_id = $ballot_id and
c.id_document_tag = a.id_document_tag and a.intended_status_id = b.intended_status_id
};
     my @List2 = db_select_multiple($sqlStr2);
     for $array_ref (@List2) {
       my ($id_document_tag,$rfc_flag,$filename,$doc_name,$statusStr,$note,$revision) = @$array_ref;
       $filename = "${filename}-${revision}.txt";
       if ($rfc_flag) {
        $filename = "RFC $id_document_tag";
        ($doc_name,$statusStr) = db_select("select rfc_name,status_value from rfcs a,
rfc_intend_status b where a.intended_status_id=b.intended_status_id and a.rfc_number=$id_document_tag");
      }
       my $one_line = "$doc_name ($statusStr)";
       my $indent = 7;
       my $ex_space = "";
       #$indent = $indent+2;
       $ex_space = "  ";
       $one_line = indent_text2($one_line,$indent);
       $ret_txt .= qq {     - $filename
       $one_line
};
      if (my_defined($note)) {
        $note =~ s/<br>/. /g;
        $one_line = "Note: " . $note;
        $one_line = indent_text2($one_line,7);
        $ret_txt .= "       $one_line\n";
      }

                                                                                
     }

    } else {
      if ($rfc_flag) {
        $sqlStr = qq{
          Select r.rfc_name,s.status_value,r.area_acronym
          from rfcs r, id_intended_status s
          where r.rfc_number = $id_document_tag
          AND r.intended_status_id = s.intended_status_id
          };
         ($doc_name,$statusStr,$gAcronym) = rm_tr(db_select($sqlStr));
         $filename = "rfc${id_document_tag}.txt";
      } else {
        $sqlStr = qq{
         Select i.id_document_name,i.filename,i.revision,s.status_value,m.acronym
         from internet_drafts i,id_intended_status s,area_group p,acronym m
         Where i.id_document_tag = $id_document_tag
         AND i.intended_status_id = s.intended_status_id
         AND i.group_acronym_id = p.group_acronym_id
         AND p.area_acronym_id = m.acronym_id
         };
         ($doc_name,$filename,$revision,$statusStr,$gAcronym) = rm_tr(db_select($sqlStr));
         next unless (my_defined($doc_name));
         $filename = "${filename}-${revision}.txt";
      }
      $statusStr = rm_tr($statusStr);
      $one_line = "$doc_name ($statusStr) - $this_count of $total_count";
      my $indent = 4;
      my $ex_space = "";
      #$indent = $indent+2;
      $ex_space = "  ";
      $one_line = indent_text2($one_line,$indent);
      $ret_txt .= qq {  o $filename
    $one_line
};
      if (my_defined($note)) {
        $note =~ s/<br>/. /g;
        $one_line = "Note: " . $note;
        $one_line = indent_text2($one_line,4);
        $ret_txt .= "    $one_line\n";
      }
   }
  if ($num_doc > 1) {
    my $sqlStr2 = qq{select c.id_document_tag,rfc_flag,filename,id_document_name,status_value,c.note,revision from internet_drafts a, id_intended_status b, id_internal c
where c.ballot_id = $ballot_id and c.primary_flag <> 1 and
c.id_document_tag = a.id_document_tag and a.intended_status_id = b.intended_status_id
};

   @List2 = db_select_multiple(@List2);
   for $array_ref (@List2) {
      my ($id_document_tag,$rfc_flag,$filename,$doc_name,$statusStr,$note,$revision) = @$array_ref;
      $filename = "${filename}-${revision}.txt2";
      if ($rfc_flag) {
        $filename = "RFC $id_document_tag";
        ($doc_name,$statusStr) = db_select("select rfc_name,status_value from rfcs a, rfc_intend_status b where a.intended_status_id=b.intended_status_id and a.rfc_number=$id_document_tag");
      }
      my $one_line = "$doc_name ($statusStr)";
      my $indent = 4;
      my $ex_space = "";
   #$indent = $indent+2;
      $ex_space = "  ";
      $one_line = indent_text2($one_line,$indent);
      $ret_txt .= qq {  - $filename
    $one_line
};

   }
  }
  if (my_defined($token_email)) {
    $ret_txt .= qq {    Token: $token_name
};
  }

   return $ret_txt;
}
sub get_wg_action {
  my $ret_txt = "${indexCnt}. Working Group Actions\n";
  my @List = db_select_multiple("select id,pwg_status_val from pwg_cat where id <> 11 and id <> 21 order by id");
  for $array_ref (@List) {
    my ($id,$val) = rm_tr(@$array_ref);
    my $sub_count1 = "${indexCnt}.";
    my $sub_count2;
    my @temp_heading = split "::",$val;
    my $sub_heading1 = $temp_heading[0];
    my $sub_heading2 = $temp_heading[1];
    if ($id < 20) {
      $sub_count1 .= "1";
    } else {
      $sub_count1 .= "2";
    }
    my $temp_id = $id % 10 -1;
    $sub_count2 = $sub_count1 . ".$temp_id";
    #if ($id == 11 or $id ==21) {
    if ($temp_id == 1) {
      $ret_txt .= "$gap$sub_count1 $sub_heading1\n";
    }
    $ret_txt .= "$sub_count2 $sub_heading2\n";
    my $sqlStr = "select group_acronym_id,note,token_name from group_internal,telechat_dates where agenda=1 and pwg_cat_id = $id and telechat_date=date1";
    $ret_txt .= get_wg_action_text($sqlStr);
  }
  $indexCnt++;
  return $ret_txt;
}



sub get_wg_action_text {
  my $sqlStr = shift;
  my $ret_txt = "";
  @List = db_select_multiple($sqlStr);
  if ($#List < 0) {
    $ret_txt .= qq {    NONE
};
  } else {
    my $total_count = $#List + 1;
    my $this_count = 0;
    for $array_ref (@List) {
      my ($group_acronym_id,$note,$token_name) = rm_tr(@$array_ref);
      $this_count++;
      my ($group_acronym, $group_name) = rm_tr(db_select("select acronym,name from acronym where acronym_id = $group_acronym_id"));
      $ret_txt .= "  o $group_name ($group_acronym) - $this_count of $total_count\n";
      if (my_defined($note)) {
        $note =~ s/<br>/. /g;
        $one_line = "Note: " . $note;
        #$one_line = indent_text2($one_line,17);
        $one_line = indent_text2($one_line,4);
        $ret_txt .= "    $one_line\n";
      }
      if(my_defined($token_name)) {
        $ret_txt .= "    Token: $token_name\n";
      }
    }
  }
  return $ret_txt;
}

sub get_agenda_footer {
  my $news_index = $indexCnt;
  my $iab_index = $news_index + 1;
  my $mi_index = $iab_index + 1;
  my $wg_news_txt = "$news_index. Working Group News\n";
  my $iab_news_txt = "$iab_index. IAB News We can use\n";
  my $m_issue_txt = "$mi_index. Management Issue\n";
  my $i_count = 0;
     my @List1 = db_select_multiple("select template_title from templates where template_type = 1");
     for $array_ref (@List1) {
       $i_count++;
       my ($title) = @$array_ref;
       $wg_news_txt .= qq{
$gap $news_index.$i_count $title
};
     }
     $i_count = 0;
     my @List2 = db_select_multiple("select template_title from templates where template_type = 2");
     for $array_ref (@List2) {
       $i_count++;
       my ($title) = @$array_ref;
       $iab_news_txt .= qq{
$gap $iab_index.$i_count $title
};
     }
                                                                                       
     $i_count = 0;
     my @List3 = db_select_multiple("select template_title from templates where template_type = 3");
     for $array_ref (@List3) {
       $i_count++;
       my ($title) = @$array_ref;
       $m_issue_txt .= qq{
$gap $mi_index.$i_count $title
};
     }
                                                                                       
  return qq{
$wg_news_txt
$iab_news_txt
$m_issue_txt
};

}

