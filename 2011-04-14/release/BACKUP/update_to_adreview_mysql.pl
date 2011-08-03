#!/usr/local/bin/perl -w

use lib '/home/mlee/RELEASE';
use lib '/export/home/mlee/RELEASE';

use IETF_DBUTIL;
use IETF_UTIL;

my $usage_str = qq {
   USAGE: update_to_adreview.pl -[mysql|informix] <-f>

};


die $usage_str unless (defined($ARGV[0]));
die $usage_str if ($ARGV[0] ne "-mysql" and  $ARGV[0] ne "-informix");
my $interactive = 1;
if (defined($ARGV[1]) and $ARGV[1] eq "-f") {
   $interactive = 0;
}
$db_mode = 0;
$INFORMIX = 1;
$MYSQL = 2;
$CURRENT_DATE = "CURRENT_DATE";
$CONVERT_SEED = 1;

if ($ARGV[0] eq "-mysql") {
   $db_mode = $MYSQL;
   $db_name = "ietf";
} else {
   $db_mode = $INFORMIX;
#   $ENV{"DBPATH"} = "/export/home/mlee/database";
#   $db_name = "testdb";
   $ENV{"DBPATH"} = "/usr/informix/databases";
   $db_name = "people";
   $CURRENT_DATE = "TODAY";
   $CONVERT_SEED = 2;
}
$ENV{"DBNAME"} = $db_name;

$sqlStr = qq{
select id_document_tag,cur_state from id_internal
where group_flag = 3
and status_date < $CURRENT_DATE
};
my $rec_count = 0;
my @List = db_select_multiple($sqlStr);
for $array_ref (@List) {
   my ($id_document_tag,$cur_state) = @$array_ref;
   my $updateSql = qq {
   update id_internal
   set group_flag = 4,
       cur_state = 18,
	   prev_state = $cur_state,
	   event_date = $CURRENT_DATE
   where id_document_tag = $id_document_tag
   };
   ### Interactive Routine needed here ###
   if (db_update($updateSql)) {
      $rec_count++;
	  ######## enter comment ##########
      my $rfc_flag = 0;
      my $public_flag = 0;
      my $comment_time = db_quote(get_current_time());
      my $comment_date = $CURRENT_DATE;
      my $version = db_quote(db_select("select revision from internet_drafts where id_document_tag = $id_document_tag"));
      my $created_by = 26;
      my $result_state = 18;
      my $origin_state = $cur_state;
      my $old_state_str = rm_tr(db_select("select document_state_val from ref_doc_states where document_state_id = $cur_state"));
      my $comment_text = db_quote("State changes to <b>Wait for Writeup</b> from <b>$old_state_str by IETF Secretariat");
      my $insertSql = qq {
	  insert into document_comments
	  (document_id,rfc_flag,public_flag,comment_time,comment_date,version,created_by,result_state,origin_state,comment_text)
	  values ($id_document_tag,$rfc_flag,$public_flag,$comment_time,$comment_date,$version,$created_by,$result_state,$origin_state,$comment_text)
	  };
	  #print $insertSql; exit;
	  db_update($insertSql);
	  
   } else {
      my $filename = db_select("select filename from internet_drafts where id_document_tag = $id_document_tag");
	  print "Can't update $filename\n";
   }
}

print "$rec_count record(s) updated\n\n";

exit;


