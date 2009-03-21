#!/usr/local/bin/perl

use lib '/home/mlee/RELEASE';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

init_database("ietf");

#$outfile="wgchairs";
$outfile="/usr/IETF/output/wgchairs";

open OUTFILE, ">$outfile";

$report_top = qq{"WGChair Archive"                            <wgchairs-archive\@megatron.ietf.org>
"The IESG"                                   <iesg\@ietf.org>
"The IAB"                                    <iab\@iab.org>
"Beaulieu, Marcia"            (agenda)       <mbeaulie\@foretec.com>
"Leslie Daigle"                              <leslie\@thinkingcat.com>
"The IAD"                                    <iad\@ietf.org>
"ietf.wgchairs"                              <ietf.wgchairs\@netlab.nec.de>
"WGChair Web Archive"                              <wgchairs-web-archive\@megatron.ietf.org>
};

print OUTFILE $report_top;
close OUTFILE;
$sqlStr = qq{
select gc.person_or_org_tag,a.acronym from g_chairs gc,groups_ietf g, acronym a
where gc.group_acronym_id = g.group_acronym_id
and g.start_date > '1980-1-1'
and (g.status_id = 1 or g.group_acronym_id = 1591)
and g.group_acronym_id = a.acronym_id
order by a.acronym
};

my @List = db_select_multiple($sqlStr);
my $sqlStr_sec = qq{select gc.person_or_org_tag,a.acronym from g_secretaries gc,groups_ietf g, acronym a
where gc.group_acronym_id = g.group_acronym_id
and g.start_date > '1980-1-1'
and (g.status_id = 1 or g.group_acronym_id = 1591)
and g.group_acronym_id = a.acronym_id
order by a.acronym 
};
my @List_sec = db_select_multiple($sqlStr_sec);
for my $array_ref (@List) {
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

  open REPORT,">>$outfile";
  write REPORT;
  close REPORT;
}
for my $array_ref (@List_sec) {
  my ($person_or_org_tag,$acronym) = rm_tr(@$array_ref);
  my $name = get_name($person_or_org_tag,1);
  $name = "\"$name\"";
  my $email = get_email($person_or_org_tag);
  $email = "<$email>";
  $acronym = "($acronym sec)";
format REPORT2 = 
@<<<<<<<<<<<<<<<<<<<<<<<<<<<  @<<<<<<<<<<<<  @<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
$name,$acronym,$email
.

  open REPORT2,">>$outfile";
  write REPORT2;
  close REPORT2;
}

exit;
