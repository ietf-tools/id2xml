#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

init_database();
my $date1 = db_quote(db_select("select date_add(current_date,interval 14 day)"));
my $date2 = db_quote(db_select("select date_add(current_date,interval 28 day)"));
my $date3 = db_quote(db_select("select date_add(current_date,interval 42 day)"));
my $date4 = db_quote(db_select("select date_add(current_date,interval 56 day)"));
my $sqlStr = qq{
update telechat_dates
set date1=$date1,date2=$date2,date3=$date3,date4=$date4
};

db_update($sqlStr);

exit;


