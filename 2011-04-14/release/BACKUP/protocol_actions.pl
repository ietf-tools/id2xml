#!/usr/local/bin/perl -

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

$todate = get_current_date();



print qq {              IESG Protocol Tracking Report
                  $todate

Contact the IESG Secretary <iesg-secretary\@cnri.reston.va.us>
 for questions or clarifications.




};

my $e_status_id = db_select("select intended_status_id from id_intended_status where status_value = 'Experimental'");
my $i_status_id = db_select("select intended_status_id from id_intended_status where status_value = 'Informational'");
my $n_status_id = db_select("select intended_status_id from id_intended_status where status_value = 'None'");

my $sqlStr_header = qq{
  select id_document_name,rfc_number,filename,revision,intended_status_id,revision_date,
  lc_sent_date
  from internet_drafts
};
###################################
#  IESG Action
###################################

print "IESG Action\n-----------\n\n";

$sqlStr = qq {
$sqlStr_header
  where (b_sent_date $is_not_null OR intended_status_id in ($e_status_id,$i_status_id))
  and b_approve_date $is_null
  and intended_status_id <> $n_status_id
  order by lc_sent_date
};
draw_list ($sqlStr);

##################################
#  AD Action
##################################

print "Area Director Action Requested\n";
print "------------------------------\n\n";

$sqlStr = qq {
$sqlStr_header
  where lc_expiration_date < $CURRENT_DATE
  and lc_expiration_date $is_not_null
  and b_sent_date $is_null
  and intended_status_id <> $n_status_id
  order by lc_sent_date
};
draw_list($sqlStr);

##################################
#  Last Call Expire
##################################

print "Last Call Expire\n";
print "----------------\n\n";
$sqlStr = qq {
$sqlStr_header
   where lc_sent_date $is_not_null
   and lc_expiration_date $is_not_null
   and $CURRENT_DATE <= lc_expiration_date
  and intended_status_id <> $n_status_id
  order by lc_sent_date
};
draw_list($sqlStr);

#################################
#  Working Group Action
#################################

print "Working Group/ Author Action\n";
print "----------------------------\n\n";
$sqlStr = qq {
$sqlStr_header
  where wgreturn_date $is_not_null
  and rfc_number $is_null
  and intended_status_id <> $n_status_id
  order by lc_sent_date
};
draw_list($sqlStr);

################################
#  Admin Action Section
################################

print "RFC EDITOR'S PLATE, NO IESG ACTION NEEDED\n";
print "-----------------------------------------\n\n";
$sqlStr = qq {
$sqlStr_header
   where b_approve_date $is_not_null
   and rfc_number $is_null
  and intended_status_id <> $n_status_id
  order by lc_sent_date
};
draw_list($sqlStr);


exit;


sub draw_list {
  my $sqlStr = shift;
  my @List = db_select_multiple($sqlStr);
for $array_ref (@List) {
  my ($id_document_name,$rfc_number,$filename,$revision,$intended_status_id,$last_modified_date) = @$array_ref;
  unless ($rfc_number) {
    ($id_document_name,$filename) = rm_tr($id_document_name,$filename);
    $filename .= "-$revision";
  } else {
    my $sqlStr = qq {
    select rfc_name,rfc_published_date from rfcs where rfc_number = $rfc_number };
    ($id_document_name,$last_modified_date) =rm_tr(db_select($sqlStr));
    $filename = "RFC${rfc_number}";
  }
  my $status_value = rm_tr(db_select("select status_value from id_intended_status where intended_status_id = $intended_status_id"));
  print qq { $id_document_name
  Document Pathname:\t\t <$filename> 
  Last Document Update:\t\t $last_modified_date
  Intended Status:\t\t $status_value

};
}  ### End of for loop
}


