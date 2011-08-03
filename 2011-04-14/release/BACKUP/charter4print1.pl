#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

   $TESTDB = 0;
   $INFORMIX = 1;
   $MYSQL = 2;

($db_mode,$CURRENT_DATE,$CONVERT_SEED) = init_database();
$is_null = " is NULL ";
$is_not_null = " is NOT NULL ";
if ($db_mode == $MYSQL) {
   $is_null = " = ''";
   $is_not_null = " <> ''";
}

$WG_DIR_PROG = "/export/home/mlee/RELEASE/wg_dir_html.pl";
$WG_INFO_PROG = "/export/home/mlee/RELEASE/wginfotoprint.pl";
$TARGET_DIR = "/export/home/ietf/public_html/print.charters";

print "Which IETF? (51st, 52nd 53rd...): ";
my $which_ietf = <STDIN>;
chomp($which_ietf);
print "What City? : ";
my $city = <STDIN>;
chomp($city);
print "What State?: ";
my $state = <STDIN>;
chomp($state);
print "What Country? : ";
my $country = <STDIN>;
chomp($country);
print "What Date?  (YYmmm - 02mar) : ";
my $meeting_date = <STDIN>;
chomp($meeting_date);
$note = "$which_ietf IETF Meeting in $city, $state $country";
print "\n$note at $meeting_date\n\n";
print "Proceed? (y/n) ";
my $answer = <STDIN>;
chomp($answer);
die "Aborted\n\n" if (uc($answer) eq "N");
my $start_date = db_quote(convert_date("1/1/1980",$CONVERT_SEED));

######## generate wg-dir.html ################
system "$WG_DIR_PROG -print";

####### generate each charter pages ################
my $sqlStr = qq {
select a.acronym,a2.acronym,a.name from acronym a, acronym a2, area_group ag,groups_ietf g
where g.group_acronym_id = a.acronym_id
and a.acronym <> 'none'
and g.status_id = 1
and (g.group_type_id = 1 or g.group_type_id = 4)
and g.start_date > $start_date
and g.group_acronym_id = ag.group_acronym_id
and ag.area_acronym_id = a2.acronym_id
order by a2.acronym,a.name
};

my @List = db_select_multiple($sqlStr);
for $array_ref (@List) {
  my ($group_acronym) = rm_tr(@$array_ref);
  print "Processing $group_acronym ...\n";
  system "$WG_INFO_PROG $group_acronym $meeting_date \"$note\"";
}


####### generate active.txt #####################

open OUTFILE,">$TARGET_DIR/active.txt";
for $array_ref (@List) {
  my ($group_acronym) = rm_tr(@$array_ref);
  print OUTFILE "${group_acronym}-charter.html\n";
}


close OUTFILE;
exit;
