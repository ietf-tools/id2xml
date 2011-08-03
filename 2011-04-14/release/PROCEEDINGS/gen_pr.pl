#!/usr/bin/perl
##########################################################################
# Copyright © 2003, Foretec Seminars, Inc.
##########################################################################

use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

init_database("ietf");

unless (defined ($ARGV[0])) {
   die "Usage: gen_pr.pl <meeting number>\n";
}
require '/a/www/ietf-datatracker/release/PROCEEDINGS/header.pl';
$meeting_num=$ARGV[0];
$CONVERT_SEED = 1; # To convert date format to fit into the current database engine

($start_date,$end_date) = db_select("select pr_from_date,pr_to_date from proceedings where meeting_num=$meeting_num");
$start_date = convert_date($start_date,$CONVERT_SEED);
$end_date = convert_date($end_date,$CONVERT_SEED);
$section_num=$ARGV[1];
$dsd = convert_date($start_date,2);
$ded = convert_date($end_date,2);
$dsd = convert_date($dsd,4);
$ded = convert_date($ded,4);
$start_date = db_quote($start_date);
$end_date = db_quote($end_date);
open OUT,">$TARGET_DIR/pr.html";
print OUT qq{
<html>
<TITLE> IETF Proceedings </TITLE>
<body background="graphics/peachbkg.gif" target="_blank">
<img src='graphics/ib2.gif' width='100%' height=21><br><br>
<h2>1.$section_num  IETF Progress Report</h2>
<h3>$dsd to $ded</h3>
<br>
};

$section_count = 0;

#  IESG Protocol Action
$sqlStr = "select count(id_document_tag) from internet_drafts where b_approve_date >= $start_date and b_approve_date <= $end_date and b_approve_date is not null and b_approve_date <> ''";
$exist_count = db_select($sqlStr);
report_protocol_action($exist_count) if ($exist_count > 0);

#IESG Laet Call Issued to the IETF
$sqlStr = "select count(id_document_tag) from internet_drafts where lc_sent_date >= $start_date and lc_sent_date <= $end_date and lc_sent_date is not null and lc_sent_date <> ''";
$exist_count = db_select($sqlStr);
report_last_call($exist_count) if ($exist_count > 0);

#Internet-Drafts Actions
$sqlStr = "select count(id_document_tag) from internet_drafts where revision_date >= $start_date and revision_date <= $end_date and revision_date is not null and revision_date <> '' and filename not like 'rfc%'";
$exist_count = db_select($sqlStr);
report_id_action($exist_count) if ($exist_count > 0);

#New Working Groups
$sqlStr = "select count(group_acronym_id) from groups_ietf where start_date >= $start_date and start_date <= $end_date and start_date is not null and start_date <> '' and group_type_id = 1";
$exist_count = db_select($sqlStr);
report_new_wg($exist_count) if ($exist_count > 0);

#Concluded Working Groups
$sqlStr = "select count(group_acronym_id) from groups_ietf where concluded_date >= $start_date and concluded_date <= $end_date and concluded_date is not null and concluded_date <> ''";
$exist_count = db_select($sqlStr);
report_concluded_wg($exist_count) if ($exist_count > 0);

#RFC Produced
$sqlStr = "select count(rfc_number) from rfcs where rfc_published_date >= $start_date and rfc_published_date <= $end_date and rfc_published_date is not null and rfc_published_date <> ''";
$exist_count = db_select($sqlStr);
report_rfc_produced($exist_count) if ($exist_count > 0);

#List of Active Working Groups
#report_active_wg() if (defined($ARGV[2]) and $ARGV[2] eq "-long");

print OUT "</body></html>\n";
close OUT;

exit;



sub report_protocol_action {
  my $item_count = shift;
  print OUT "$item_count IESG Protocol and Document Actions this period\n ";
  print OUT "<br>\n";
  return;
}

sub report_last_call {
  my $item_count = shift;
  print OUT "$item_count IESG Last Calls issued to the IETF this period\n ";
  print OUT "<br>\n";
  return;
}

sub report_new_wg {
  my $item_count = shift;
  print OUT "<br>$item_count New Working Group(s) formed this period\n ";
  print OUT "<br>\n";
  my $sqlStr = "select acronym,name from groups_ietf, acronym where group_acronym_id = acronym_id and start_date >= $start_date and start_date <= $end_date and start_date is not null and start_date <> '' and group_type_id = 1";
  my @List = db_select_multiple($sqlStr);
  print OUT "<pre>\n";
  for $array_ref (@List) {
    my ($group_acronym,$group_name) = rm_tr(@$array_ref);     
    $group_name = indent_text($group_name,4);     
    print OUT "$group_name ($group_acronym)\n\n";
  }
  print OUT "</pre>\n";
  return;
}

sub report_concluded_wg {
  my $item_count = shift;
  print OUT "<br>$item_count Working Group(s) concluded this period\n ";
  print OUT "<br>\n";
  my $sqlStr = "select acronym,name from groups_ietf, acronym where group_acronym_id = acronym_id and concluded_date >= $start_date and concluded_date <= $end_date and concluded_date is not null and concluded_date <> ''";
  my @List = db_select_multiple($sqlStr);
  print OUT "<pre>\n";
  for $array_ref (@List) {
    my ($group_acronym,$group_name) = rm_tr(@$array_ref);
    $group_name = indent_text($group_name,4);
    print OUT "$group_name ($group_acronym)\n\n";
  }
  print OUT "</pre>\n";
  return;
}

sub report_id_action {
  my $item_count = shift;
  print OUT "$item_count new or revised Internet-Drafts this period\n ";
  print OUT "<br>\n";
  return;
}

sub report_rfc_produced {
  my $item_count = shift;
  print OUT "$item_count RFC produced this period<br>\n";
print OUT qq{<table cellpadding="3" cellspacing="2" border="0" width="100%">
<tbody>
};

  my @status_ary = ('','PS','DS','S ','E ','I ','B ','H ','N ');

  my $sqlStr = "select rfc_number,status_id,group_acronym,rfc_published_date,rfc_name from rfcs where rfc_published_date >= $start_date and rfc_published_date <= $end_date and rfc_published_date is not null and rfc_published_date <> ''";
  my @List = db_select_multiple($sqlStr);
  my $s_count = 0;
  my $bcp_count = 0;
  my $e_count = 0;
  my $i_count = 0;

  for $array_ref (@List) {
    my ($rfc_number,$status_id,$group_acronym,$pDate,$rfc_name) = rm_tr (@$array_ref);
    $pDate = convert_date($pDate,2);
    $pDate = convert_date($pDate,3);
    if ($status_id > 0 and $status_id <= 3) {
      $s_count++;
    } elsif ($status_id == 4) {
      $e_count++;
    } elsif ($status_id == 5) {
      $i_count++;
    } elsif ($status_id == 6) {
      $bcp_count++;
    }
    my $si = $status_ary[$status_id];
    $rfc_name = indent_text2($rfc_name,33);
    $group_acronym = "($group_acronym)";
    $group_acronym = add_spaces($group_acronym,10);
    print OUT qq{<tr><td valign="middle"><a href="ftp://ftp.ietf.org/rfc/rfc$rfc_number.txt" target="_blank">RFC$rfc_number</a></td><td>$si</td><td>$group_acronym</td><td width="50">$pDate</td><td>$rfc_name</td></tr>
};
  }
  print OUT "</table>\n";
  print OUT "   $s_count Standards Track;  $bcp_count BCP;  $e_count Experimental;  $i_count Informational<br><br>\n";
  return;
}


