#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE/';
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
my $sqlStr = qq {
  select a.acronym,a.name,a2.name from acronym a,acronym a2,groups_ietf g, area_directors ad
  where g.group_acronym_id = a.acronym_id
  and g.group_type_id = 1
  and g.status_id = 1
  and g.area_director_id = ad.id
  and ad.area_acronym_id = a2.acronym_id
};
if (defined($ARGV[0]) and $ARGV[0] eq "-byacronym") {
  $sqlStr .= qq{  order by a.acronym
};
} else {
  $sqlStr .= qq{  order by a2.name, a.name
};
}
my @List = db_select_multiple($sqlStr);
open OUTFILE,">./1wg-charter.txt";

for $array_ref (@List) {
  my ($group_acronym) = @$array_ref;
  print OUTFILE "$group_acronym\n";
}
close OUTFILE;
for $array_ref (@List) {
  my ($group_acronym) = @$array_ref;
  system "/export/home/mlee/RELEASE/wginfo.pl $group_acronym -description -id >> ./1wg-charter.txt";

}
system "cat ./1wg-charter.txt;rm ./1wg-charter.txt";
#unlink "./1wg-charter.txt";

exit;   


