#!/usr/bin/perl
##########################################################################
# Copyright © 2004 and 2003, Foretec Seminars, Inc.
##########################################################################

use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;


$telechat_date = $ARGV[0];
$db_name = $ARGV[1];
init_database($db_name);
($telechat_id,$mi_frozen) = db_select("select telechat_id,mi_frozen from telechat where telechat_date='$telechat_date'");

$not_via_rfc_where = "AND via_rfc_editor = 0\n";
$via_rfc_where = "AND via_rfc_editor = 1\n";

#db_update("delete from agenda_items where telechat_id=$telechat_id");

get_agenda_body("PA");
get_agenda_body("DA");
get_wg_action();
get_templates();
get_management_issues() unless ($mi_frozen);
check_removed_items();
exit;


sub check_removed_items {
  my @List = db_select_multiple("select ballot_id from id_internal a, telechat_dates b where agenda=1 and telechat_date='$telechat_date'");
  my $ballot_id_list="";
  for my $array_ref (@List) {
    my ($val) = @$array_ref;
    $ballot_id_list.="$val,";
  }
  if (my_defined($ballot_id_list)) {
    chop $ballot_id_list;
    db_update("delete from agenda_items where ballot_id > 0 and ballot_id not in ($ballot_id_list) and telechat_id=$telechat_id","gen_agenda_item_table.cgi","Telechat Admin");
  }
  
  my @List2 = db_select_multiple("select group_acronym_id from group_internal a, telechat_dates b where agenda=1 and telechat_date='$telechat_date'");
  my $g_list="";
  for my $array_ref (@List2) {
    my ($val) = @$array_ref;
    $g_list.="$val,";
  }
  if (my_defined($g_list)) {
    chop $g_list;
    db_update("delete from agenda_items where group_acronym_id > 0 and group_acronym_id not in ($g_list) and telechat_id=$telechat_id","gen_agenda_item_table.cgi","Telechat Admin");
  }
}

sub gen_unassigned {
  my $type = shift;
  my $via_rfc_editor = shift;
  my $wg_submission = shift;
  my $sqlStr = "select rfc_flag,ballot_id,a.id_document_tag from id_internal a, internet_drafts b where (cur_state < 16 or cur_state > 21) and agenda=1 and via_rfc_editor=$via_rfc_editor and telechat_date='$telechat_date'  and a.id_document_tag = b.id_document_tag";
  if ($wg_submission) {
    $sqlStr .= " AND b.group_acronym_id <> 1027";
  } else {
    $sqlStr .= " AND group_acronym_id = 1027";
  } 

  my @List = db_select_multiple($sqlStr);
  return 0 if ($#List < 0);
  my $total_count = $#List + 1;
  my $this_count = 0;
  my $ballot_id_list = "";
  for $array_ref (@List) {
    my ($rfc_flag,$ballot_id,$id_document_tag) = @$array_ref;
    my $sqlStr2 = "";
    $this_count++;
    if ($rfc_flag) {
      $sqlStr2 = qq{select status_value from rfcs a, rfc_intend_status b, acronym c where a.rfc_number=$id_document_tag and a.intended_status_id = b.intended_status_id and a.group_acronym = c.acronym};
    } else {
      $sqlStr2 = qq{select status_value from internet_drafts a, id_intended_status b where a.intended_status_id = b.intended_status_id and id_document_tag = $id_document_tag};
    }
    my ($status_value) = db_select($sqlStr2);
    next if ($status_value =~ /Experimental|Informational/ and $type eq "PA");
    next if ($status_value =~ /BCP|Proposed|Standard|Draft/ and $type eq "DA");
    my $agenda_cat_id;
    if ($type eq "PA") {
      if ($wg_submission) {
        $agenda_cat_id = 3;
      } else {
        $agenda_cat_id = 6;
      }
      $sqlStr .= " AND intended_status_id in (1,2,6,7)";
    } else  {
      if ($wg_submission) {
        $agenda_cat_id = 9;
      } else {
        if ($via_rfc_editor) {
          $agenda_cat_id = 15;
        } else {
          $agenda_cat_id = 12;
        }
      }
      $sqlStr .= " AND intended_status_id in (3,5,4)";
    }
    update_agenda_items($telechat_id,$agenda_cat_id,$ballot_id,0,$total_count,$this_count);
  }
  return 1;
}


sub get_agenda_body {
  my $group_type = shift;
  my $id_list = "";
  my $pReturningItem = -1;
  if ($group_type eq "PA") {  #generate Protocol Action list
    $id_list = "1,2,6,7";
    $rfc_list = "1,2,3,7";
  } else {  #generate Docuement Action list
    $id_list = "3,5,4";
    $rfc_list = "4,5"
  }

  my $sqlStr_base = qq{select ballot_id
from id_internal, internet_drafts 
WHERE agenda = 1 and primary_flag=1
AND id_internal.id_document_tag = internet_drafts.id_document_tag
AND internet_drafts.intended_status_id in ($id_list)
AND telechat_date = '$telechat_date' 
AND cur_state >= 16 and cur_state <= 21
};
  my $sqlStr_base_rfc = qq{select ballot_id
from id_internal, rfcs
WHERE rfc_flag = 1 and agenda = 1 and primary_flag = 1
AND id_internal.id_document_tag = rfcs.rfc_number
AND rfcs.intended_status_id in ($rfc_list)
AND telechat_date = '$telechat_date' 
AND cur_state >= 16 and cur_state <= 21
};

  get_wg_individual($sqlStr_base,$sqlStr_base_rfc,"WG",$group_type);
  get_wg_individual($sqlStr_base,$sqlStr_base_rfc,"IND",$group_type);
  return 1;
}

sub get_wg_individual {
  my $sqlStr = shift;
  my $sqlStr_rfc = shift;
  my $submit_type = shift;
  my $group_type = shift;
  if ($submit_type eq "IND") {
    $sqlStr .= "AND group_acronym_id = 1027\n";
    $sqlStr_rfc .= "AND group_acronym = 'none'\n";
    if ($group_type eq "DA") {
      get_via_rfc_ad($sqlStr,$sqlStr_rfc,$submit_type,"AD");
      gen_unassigned("DA",0);
      get_via_rfc_ad($sqlStr,$sqlStr_rfc,$submit_type,"RFC");
      gen_unassigned("DA",1);
      return 1;
    }
  } else {
    $sqlStr .= "AND group_acronym_id <> 1027\n";
    $sqlStr_rfc .= "AND group_acronym <> 'none'\n";
  }
  $sqlStr .= $not_via_rfc_where;
  $sqlStr_rfc .= $not_via_rfc_where;
  get_new_returning($sqlStr,$sqlStr_rfc,"NEW",$submit_type,$group_type);
  get_new_returning($sqlStr,$sqlStr_rfc,"RET",$submit_type,$group_type);
  my $wg_submission = ($submit_type eq "IND")?0:1;
  $ret_txt .= gen_unassigned($group_type,0,$wg_submission);
  return 1;
}

sub get_via_rfc_ad {
  my $sqlStr = shift;
  my $sqlStr_rfc = shift;
  my $submit_type=shift;
  my $group_type=shift;
  if ($group_type eq "AD") {
    $sqlStr .= $not_via_rfc_where;
    $sqlStr_rfc .= $not_via_rfc_where;
  } else {
    $sqlStr .= $via_rfc_where;
    $sqlStr_rfc .= $via_rfc_where;
  }
  get_new_returning($sqlStr,$sqlStr_rfc,"NEW",$submit_type,$group_type);
  get_new_returning($sqlStr,$sqlStr_rfc,"RET",$submit_type,$group_type);
  return 1;
}

sub get_new_returning {
  my $sqlStr = shift;
  my $sqlStr_rfc = shift;
  my $age_type = shift;
  my $submit_type = shift;
  my $group_type=shift;
  if ($age_type eq "NEW") {
    $sqlStr .= "AND returning_item = 0\n";
    $sqlStr_rfc .= "AND returning_item = 0\n";
  } else {
    $sqlStr .= "AND returning_item = 1\n";
    $sqlStr_rfc .= "AND returning_item = 1\n";
  }
  $sqlStr .= "order by ballot_id, primary_flag DESC, status_date";
  $sqlStr_rfc .= "order by ballot_id, primary_flag DESC, status_date";
  my @List = db_select_multiple($sqlStr);
  my @List_rfc = db_select_multiple($sqlStr_rfc);
  my $total_count = $#List + $#List_rfc + 2;
  return 0 if ($#List < 0 and $#List_rfc < 0);
  my $this_count = 0;
  my $agenda_cat_id = get_agenda_cat_id($age_type,$submit_type,$group_type);
  for $array_ref (@List) {
    my ($ballot_id) = @$array_ref;
    $this_count++;
    update_agenda_items($telechat_id,$agenda_cat_id,$ballot_id,0,$total_count,$this_count);
  }
  for $array_ref (@List_rfc) {
    my ($ballot_id) = @$array_ref;
    $this_count++;
    update_agenda_items($telechat_id,$agenda_cat_id,$ballot_id,0,$total_count,$this_count);
  }
  return 1;
}

sub get_agenda_cat_id {
  my ($age_type,$submit_type,$group_type) = @_;
  return 1 if ($age_type eq "NEW" and $submit_type eq "WG" and $group_type eq "PA");
  return 2 if ($age_type eq "RET" and $submit_type eq "WG" and $group_type eq "PA");
  return 4 if ($age_type eq "NEW" and $submit_type eq "IND" and $group_type eq "PA");
  return 5 if ($age_type eq "RET" and $submit_type eq "IND" and $group_type eq "PA");
  return 7 if ($age_type eq "NEW" and $submit_type eq "WG" and $group_type eq "DA");
  return 8 if ($age_type eq "RET" and $submit_type eq "WG" and $group_type eq "DA");
  return 10 if ($age_type eq "NEW" and $submit_type eq "IND" and $group_type eq "AD");
  return 11 if ($age_type eq "RET" and $submit_type eq "IND" and $group_type eq "AD");
  return 13 if ($age_type eq "NEW" and $submit_type eq "IND" and $group_type eq "RFC");
  return 14 if ($age_type eq "RET" and $submit_type eq "IND" and $group_type eq "RFC");
  return 16 if ($age_type eq "CREATE" and $submit_type eq "REV");
  return 17 if ($age_type eq "CREATE" and $submit_type eq "APP");
  return 18 if ($age_type eq "RECHART" and $submit_type eq "REV");
  return 19 if ($age_type eq "RECHART" and $submit_type eq "APP");
}


sub get_wg_action {
  my @List = db_select_multiple("select id,pwg_status_val from pwg_cat where id <> 11 and id <> 21 order by id");
  my $age_type;
  my $submit_type;
  for $array_ref (@List) {
    my ($id,$val) = rm_tr(@$array_ref);
    my @temp_heading = split "::",$val;
    my $sub_heading1 = $temp_heading[0];
    my $sub_heading2 = $temp_heading[1];
    if ($id < 20) {
      $age_type = "CREATE";
    } else {
      $age_type = "RECHART";
    }
    if ($id == 12 or $id ==22) {
      $submit_type="REV";
    } else {
      $submit_type="APP";
    }
    my $agenda_cat_id = get_agenda_cat_id($age_type,$submit_type);
    my $sqlStr = "select group_acronym_id from group_internal where agenda=1 and pwg_cat_id = $id and telechat_date='$telechat_date'";
    my @List2 = db_select_multiple($sqlStr);
    my $total_count = $#List2 + 1;
    my $this_count = 0;
    for $array_ref2 (@List2) {
      my ($group_acronym_id) = @$array_ref2;
      $this_count++;
      update_agenda_items($telechat_id,$agenda_cat_id,0,$group_acronym_id,$total_count,$this_count);
    }
  }
  return 1;
}

sub get_templates {
  my $wg_news_txt="";
  my $iab_news_txt="";
  my $management_issue="";
  my @field_list = ("wg_news_txt","iab_news_txt","management_issue");
  for ($template_type=1;$template_type<3;$template_type++) {
    my @List = db_select_multiple("select template_title,template_text from templates where template_type=$template_type");
    my $news_txt = "";
    for $array_ref (@List) {
      my ($title,$text) = @$array_ref;
      $news_txt .= "$title\n$text\n\n";
    }
    $news_txt = db_quote($news_txt);
    my $field_name = $field_list[$template_type-1];
    db_update ("update telechat set $field_name=$news_txt where telechat_id=$telechat_id");
  }
}

sub get_management_issues {
  db_update("delete from management_issues where telechat_id=$telechat_id");
  my @List = db_select_multiple("select template_title,template_text from templates where template_type=3");
  for $array_ref (@List) {
    my ($title,$text) = db_quote(@$array_ref);
    db_update ("insert into management_issues (telechat_id,title,issue) values ($telechat_id,$title,$text)");
  }

}

sub update_agenda_items {
  my ($telechat_id,$agenda_cat_id,$ballot_id,$group_acronym_id,$total_count,$this_count) = @_;
  my $agenda_item_id = db_select("select agenda_item_id from agenda_items where telechat_id=$telechat_id and ballot_id=$ballot_id");
  $agenda_item_id = db_select("select agenda_item_id from agenda_items where telechat_id=$telechat_id and group_acronym_id=$group_acronym_id") unless ($ballot_id);
  unless ($agenda_item_id) {
    db_update("insert into agenda_items (telechat_id,agenda_cat_id,ballot_id,group_acronym_id,total_num,item_num) values ($telechat_id,$agenda_cat_id,$ballot_id,$group_acronym_id,$total_count,$this_count)");
  } else {
    db_update("update agenda_items set agenda_cat_id=$agenda_cat_id, total_num=$total_count, item_num=$this_count where agenda_item_id=$agenda_item_id");
  }
}

