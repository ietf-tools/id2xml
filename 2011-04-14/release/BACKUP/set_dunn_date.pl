#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

$TESTDB = 0;
$INFORMIX = 1;
$MYSQL = 2;

($db_mode,$CURRENT_DATE,$CONVERT_SEED) = init_database($MYSQL);

my $sqlStr = qq {
select count(id_document_tag) from internet_drafts
where revision_date < date_add(date_sub((date_sub(current_date,interval 183 day)), interval dayofmonth(date_sub(current_date,interval 183 day)) day), interval 1 day)
and  intended_status_id = 8 and status_id = 1 and (extension_date is null or extension_date = '')
and (dunn_sent_date is null or dunn_sent_date = '')
};
my $count = db_select($sqlStr);
print "\nThere are $count IDs to be expired\n";
exit unless ($count); 
print "Do you want to expire them now? (Y/N): ";
my $ans = <STDIN>;
chomp($ans);
my $ans = uc($ans);
die "No ID has been expired\n" if ($ans ne "Y"); 
$sqlStr = qq {
update internet_drafts
set dunn_sent_date=date_sub(current_date, interval 1 day),lc_changes="YES"
where revision_date < date_add(date_sub((date_sub(current_date,interval 183 day)), interval dayofmonth(date_sub(current_date,interval 183 day)) day), interval 1 day)
and  intended_status_id = 8 and status_id = 1 and (extension_date is null or extension_date = '')
};
db_update($sqlStr);
print "\n\nDone.\n";
exit;


