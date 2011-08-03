#!/usr/local/bin/perl -w

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

$ENV{"DBNAME"} = "ietf";

$aID = $ARGV[0] or die "USAGE: touchrec.pl <acronym>\n";
$q_aID = db_quote($aID); 

if (db_select("select count(*) from acronym where acronym = $q_aID")) {
   $rID = db_select("select acronym_id from acronym where acronym = $q_aID");
   $a_count = db_select("select count(*) from areas where area_acronym_id = $rID");
   if ($a_count) {
      $sqlStr = qq {
	  update areas
	  set last_modified_date = CURRENT_DATE
	  where area_acronym_id = $rID
	  };
      db_update($sqlStr);
   }
   else {
      $sqlStr = qq {
	  update groups_ietf
	  set last_modified_date = CURRENT_DATE
	  where group_acronym_id = $rID
	  };
      db_update($sqlStr);
   }
} else {
   die "ERROR: Invalid acronym: $aID\n";
}



exit;

