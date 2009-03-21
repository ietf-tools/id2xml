#!/usr/bin/perl
##########################################################################
# Copyright © 2003 anbd 2002, Foretec Seminars, Inc.
##########################################################################

use lib '/home/mlee/RELEASE';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

init_database("ietf");

#$out_file = "/home/mlee/bofchairs";
$out_file = "/home/ietf/STATIC-MAILING-LISTS/bofchairs";

open OUTFILE, ">$out_file";

$report_top = qq{"Beaulieu, Marcia"            (agenda)       <mbeaulie\@foretec.com>
};

print OUTFILE $report_top;
close OUTFILE;
$sqlStr = "select person_or_org_tag,acronym from groups_ietf a,  g_chairs c, acronym d where group_type_id =3 and status_id=1 and a.group_acronym_id=acronym_id and a.group_acronym_id=c.group_acronym_id";

my @List = db_select_multiple($sqlStr);
for $array_ref (@List) {
  my ($person_or_org_tag,$acronym) = rm_tr(@$array_ref);
  my $name = get_name($person_or_org_tag,1);
  $name = "\"$name\"";
  my $email = get_email($person_or_org_tag);
  $email = "<$email>";
  $acronym = "($acronym)";
format REPORT = 
@<<<<<<<<<<<<<<<<<<<<<<<<<<<  @<<<<<<<<<<<<  @<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
$name,$acronym,$email
.

  open REPORT,">>$out_file";
  write REPORT;
  close REPORT;
}

#$sqlStr="select person_or_org_tag,irtf_acronym from irtf_chairs a, irtf b where a.irtf_id=b.irtf_id and meeting_scheduled=1";
#my @bofList = db_select_multiple($sqlStr);
#for $array_ref (@bofList) {
#  my ($person_or_org_tag,$acronym) = rm_tr(@$array_ref);
#  my $name = get_name($person_or_org_tag,1);
#  $name = "\"$name\"";
#  my $email = get_email($person_or_org_tag);
#  $email = "<$email>";
#  $acronym = "($acronym)";
#format REPORT2 =
#@<<<<<<<<<<<<<<<<<<<<<<<<<<<  @<<<<<<<<<<<<  @<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
#$name,$acronym,$email
#.
#                                                                                
#  open REPORT2,">>$out_file";
#  write REPORT2;
#  close REPORT2;
#}

exit;
