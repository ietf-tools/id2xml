#!/usr/bin/perl
##########################################################################
# Copyright © 2004 and 2003, Foretec Seminars, Inc.
##########################################################################

use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

$MAX_AGENDA_NUM = 19;
($program_name, $command_name, $telechat_date,$db_name) = @ARGV;
init_database($db_name);
my $gap = "&nbsp; &nbsp";
my $telechat_id = db_select("select telechat_id from telechat where telechat_date = '$telechat_date'");
my $prev_agenda_cat_id = 0;
for ($agenda_cat_id=1;$agenda_cat_id<=$MAX_AGENDA_NUM;$agenda_cat_id++) {

  if ($agenda_cat_id != $prev_agenda_cat_id) {
    $prev_agenda_cat_id = $agenda_cat_id;
    my $heading = db_select("select agenda_cat_value from agenda_cat where agenda_cat_id=$agenda_cat_id");
    $heading =~ s/\n/<br>/g;
    print "<br>$heading<br>\n";;
  }

  my $sqlStr2 = "select agenda_item_id,ballot_id,group_acronym_id from agenda_items where telechat_id = $telechat_id and agenda_cat_id=$agenda_cat_id order by agenda_item_id";
  my @List2 = db_select_multiple($sqlStr2);
  if ($#List2 < 0) {
    print "$gap NONE<br>\n";
    next;
  }
  for $array_ref (@List2) {
    my ($agenda_item_id,$ballot_id,$group_acronym_id) = @$array_ref;
    if ($ballot_id > 0) { 
      my $ballot_count = db_select("select count(ballot_id) from id_internal where ballot_id=$ballot_id");
      if ($ballot_count > 1) {
        print "o $ballot_count documents ballot<br>\n";
        print get_ballot_list($agenda_item_id,$ballot_id,$agenda_cat_id,"$gap -",$telechat_date,$command_name);
      } else {
        print get_ballot_list($agenda_item_id,$ballot_id,$agenda_cat_id, "o",$telechat_date,$command_name);
      }
    } elsif ($group_acronym_id > 0) {
       my $wg_name = db_select("select acronym from acronym where acronym_id = $group_acronym_id");
       print qq{$gap o <a href="$program_name?command=$command_name&agenda_item_id=$agenda_item_id&telechat_date=$telechat_date">$wg_name</a><br>
};
    }
  }
}
exit;


