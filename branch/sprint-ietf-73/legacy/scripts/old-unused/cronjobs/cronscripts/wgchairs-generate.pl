#!/usr/local/bin/perl

use lib '/home/mlee/RELEASE';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

init_database("ietf");


open OUTFILE, ">/home/master-site/htdocs/MAILING-LISTS/wgchairs";

$report_top = qq{"WGChair Archive"                            <wgchairs-archive\@lists.ietf.org>
"The IESG"                                   <iesg\@ietf.org>
"The IAB"                                    <iab\@iab.org>
"Beaulieu, Marcia"            (agenda)       <mbeaulieu\@foretec.com>
"Leslie Daigle"                              <leslie\@thinkingcat.com>
};

print OUTFILE $report_top;
close OUTFILE;
my $start_date = db_quote("1980-1-1");
$sqlStr = qq {
select gc.person_or_org_tag,a.acronym from g_chairs gc,groups_ietf g, acronym a
where gc.group_acronym_id = g.group_acronym_id
and g.start_date > $start_date
and (g.status_id = 1 or g.group_acronym_id = 1591)
and g.group_acronym_id = a.acronym_id
order by a.acronym
};

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

  open REPORT,">>/usr/IETF/output/wgchairs";
  write REPORT;
  close REPORT;
}

exit;
