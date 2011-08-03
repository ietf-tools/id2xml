#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE';
use IETF_UTIL;
use IETF_DBUTIL;


init_database_mysql();

my $start_date = db_select("select date_sub(CURRENT_DATE,interval 1 month)");
my $end_date = db_select("select date_sub(CURRENT_DATE,interval 1 day)");
my $month = db_select("select month('$start_date')");
$month = "0"."$month" if ($month < 10);
my $year = db_select("select year('$start_date')");
system "/export/home/mlee/RELEASE/imr.pl $start_date $end_date > /usr/local/etc/httpd/htdocs/IMR/IMR-${year}-${month}";
#print "/export/home/mlee/RELEASE/imr.pl $start_date $end_date > /usr/local/etc/httpd/htdocs/IMR/IMR-${year}-${month}";
#print "\n";

exit;
