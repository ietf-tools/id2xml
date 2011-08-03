#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

($db_mode,$CURRENT_DATE,$CONVERT_SEED,$is_null) = init_database($MYSQL);

$temp = db_select("select abstract from internet_drafts where id_document_tag=6029");
$new_temp = indent_text($temp,3);
print "$new_temp\n";


