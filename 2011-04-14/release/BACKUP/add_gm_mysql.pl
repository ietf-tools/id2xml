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

$filename = $ARGV[1];
open (INFILE,$filename);
%attr = (
	PrintError => 0,
	RaiseError => 1
);
%months = (
   Jan => 1,
   Feb => 2,
   Mar => 3,
   Apr => 4,
   May => 5,
   Jun => 6,
   Jul => 7,
   Aug => 8,
   Sep => 9,
   Oct => 10,
   Nov => 11,
   Dec => 12
);
@dates = localtime(time);
$local_month = $dates[4] + 1;
$local_year = $dates[5];
chomp($acronym = <INFILE>);
$acronym = db_quote($acronym);
$gID = db_select("select acronym_id from acronym where acronym=$acronym");
die "Acronym \"$acronym\" does not exist\n" unless defined($gID);
#print "$gID\n";
while ($inline = <INFILE>) {
   chomp($inline);
   if (length($inline) == 0) {next;}
   @GM = split ' ',$inline;
   $month_str = shift (@GM);
   $month_val = $months{$month_str};
   $day_val = shift (@GM);
   if ($month_val < $local_month) {
      $year_val = $local_year + 1 + 1900;
   } else {
      $year_val = $local_year + 1900;
   }
   $date_str = "${month_val}/${day_val}/${year_val}";
   $date_str = convert_date($date_str,$CONVERT_SEED);
   $desc_str = sprintf "@GM";
   $desc_str = db_quote($desc_str);
   $sqlStr = qq{insert into goals_milestones
   (group_acronym_id,description,expected_due_date,last_modified_date)
   values ($gID,$desc_str,'$date_str',$CURRENT_DATE)
   };
#   print "$sqlStr\n";
   db_update($sqlStr);
}

close (INFILE);
exit;


