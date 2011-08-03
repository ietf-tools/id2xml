#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE';
use IETF_UTIL;
use IETF_DBUTIL;

   $TESTDB = 0;
   $INFORMIX = 1;
   $MYSQL = 2;

($db_mode,$CURRENT_DATE,$CONVERT_SEED) = init_database($MYSQL);
$is_null = " is NULL ";
$is_not_null = " is NOT NULL ";
if ($db_mode == $MYSQL) {
   $is_null = " = ''";
   $is_not_null = " <> ''";
}


open OUTFILE, ">/export/home/ietf/MAILING-LISTS/wgchairs";

$report_top = qq{"WGChair Archive"                            <wgchairs-archive\@lists.ietf.org>
"The IESG"                                   <iesg\@ietf.org>
"The IAB"                                    <iab\@iab.org>
"Beaulieu, Marcia"            (agenda)       <mbeaulieu\@ietf.org>
"Leslie Daigle"                              <leslie\@thinkingcat.com>
};

print OUTFILE $report_top;
close OUTFILE;
my $start_date = db_quote(convert_date("1/1/1980",$CONVERT_SEED));
$sqlStr = qq {
select gc.person_or_org_tag,a.acronym from g_chairs gc,groups_ietf g, acronym a
where gc.group_acronym_id = g.group_acronym_id
and g.start_date > $start_date
and g.concluded_date $is_null
and g.status_id = 1
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

  open REPORT,">>/export/home/ietf/MAILING-LISTS/wgchairs";
  write REPORT;
  close REPORT;
}

exit;
