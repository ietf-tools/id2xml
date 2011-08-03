#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

   $MYSQL = 2;

($db_mode,$CURRENT_DATE,$CONVERT_SEED) = init_database($MYSQL);
$todate = get_current_date();
@List = db_select_multiple("select rfc_acted_on from rfcs_obsolete where action = 'Obsoletes'");
my $obsoletes = "";
for $array_ref (@List) {
   my ($val) = @$array_ref;
   $obsoletes .= "${val},";
}
chop($obsoletes);

print qq{              Standards Track RFC's Eligible for Advancement
                     $todate

};

$sqlStr_head = qq {
select rfc.rfc_number,rfc.rfc_name,rfc.rfc_published_date,rfc.group_acronym,
rfc.proposed_date,rfc.draft_date from rfcs rfc};

my $draft_status_id=db_select("select status_id from rfc_status where status_value='Draft Standard'");
my $proposed_status_id=db_select("select status_id from rfc_status where status_value='Proposed Standard'");

###########################
# Expired Draft Standard
###########################
if ($db_mode == $MYSQL) {
   $sqlStr =  $sqlStr_head . qq {
   where draft_date <> ''
   and draft_date < date_sub(current_date, interval 730 day)
   and rfc_number not in ($obsoletes)
   and status_id = $draft_status_id
   order by rfc_number DESC
   };
} else {
   $sqlStr = $sqlStr_head . qq {
   where draft_date < TODAY - 730
   and rfc_number not in ($obsoletes)
   and status_id = $draft_status_id
   order by rfc_number DESC
   };
}

@List = db_select_multiple($sqlStr);
draw_text("Draft RFC's expired in grade.",@List);


############################
# Expired Proposed Standard
###########################
if ($db_mode == $MYSQL) {
   $sqlStr =  $sqlStr_head . qq {
   where proposed_date <> ''
   and proposed_date < date_sub(current_date, interval 730 day)
   and rfc_number not in ($obsoletes)
   and status_id = $proposed_status_id
   order by rfc_number DESC
   };
} else {
   $sqlStr = $sqlStr_head . qq {
   where proposed_date < TODAY - 730
   and rfc_number not in ($obsoletes)
   and status_id = $proposed_status_id
   order by rfc_number DESC
   };
}

@List = db_select_multiple($sqlStr);
draw_text("Proposed RFC's expired in grade.",@List);


###########################
# Soon to Expire Draft Standard
###########################

if ($db_mode == $MYSQL) {
   $sqlStr =  $sqlStr_head . qq {
   where draft_date <> ''
   and draft_date > date_sub(current_date, interval 730 day)
   and draft_date < date_sub(current_date, interval 640 day)
   and rfc_number not in ($obsoletes)
   and status_id = $draft_status_id
   order by rfc_number DESC
   };
} else {
   $sqlStr = $sqlStr_head . qq {
   where draft_date > TODAY - 730
   and draft_date < TODAY - 640
   and rfc_number not in ($obsoletes)
   and status_id = $draft_status_id
   order by rfc_number DESC
   };
}

@List = db_select_multiple($sqlStr);
draw_text("Draft RFC's to expire in less than 3 months.",@List);

############################
# Soon to expire Proposed Standard
###########################


if ($db_mode == $MYSQL) {
   $sqlStr =  $sqlStr_head . qq {
   where proposed_date <> ''
   and proposed_date > date_sub(current_date, interval 730 day)
   and proposed_date < date_sub(current_date, interval 640 day)
   and rfc_number not in ($obsoletes)
   and status_id = $proposed_status_id
   order by rfc_number DESC
   };
} else {
   $sqlStr = $sqlStr_head . qq {
   where proposed_date > TODAY - 730
   and proposed_date < TODAY - 640
   and rfc_number not in ($obsoletes)
   and status_id = $proposed_status_id
   order by rfc_number DESC
   };
}

@List = db_select_multiple($sqlStr);
draw_text("Proposed RFC's to expire in less than 3 months.",@List);





###########################
# Eligible Draft Standard
###########################
my $target_date;
if ($db_mode == $MYSQL) {
   $sqlStr =  $sqlStr_head . qq {
   where draft_date <> ''
   and draft_date < date_sub(current_date, interval 120 day)
   and rfc_number not in ($obsoletes)
   and status_id = $draft_status_id
   order by rfc_number DESC
   };
   $target_date = db_select("select date_sub(current_date, interval 120 day)");
} else {
   $sqlStr = $sqlStr_head . qq {
   where draft_date < TODAY - 120
   and rfc_number not in ($obsoletes)
   and status_id = $draft_status_id
   order by rfc_number DESC
   };
   $target_date = db_select("select unique TODAY-120 from rfc_status");
}

@List = db_select_multiple($sqlStr);
draw_text("Draft RFC's eligible for advancement.\n\tDraft status achived before $target_date",@List);


############################
# Eligible Proposed Standard
###########################
if ($db_mode == $MYSQL) {
   $sqlStr =  $sqlStr_head . qq {
   where proposed_date <> ''
   and proposed_date < date_sub(current_date, interval 180 day)
   and rfc_number not in ($obsoletes)
   and status_id = $proposed_status_id
   order by rfc_number DESC
   };
   $target_date = db_select("select date_sub(current_date, interval 180 day)");
} else {
   $sqlStr = $sqlStr_head . qq {
   where proposed_date < TODAY - 180 
   and rfc_number not in ($obsoletes)
   and status_id = $proposed_status_id
   order by rfc_number DESC
   };
   $target_date = db_select("select unique TODAY-180 from rfc_status");
}

@List = db_select_multiple($sqlStr);
draw_text("Proposed RFC's eligible for advancement.\n\tProposed status achived before $target_date",@List);





exit;



sub draw_text {
   my $header = shift;
   my @List = @_;
   print qq {$header
-----------------------------

};

   for $array_ref (@List) {
   my ($rfc_number,$rfc_name,$rfc_published_date,$group_acronym,$proposed_date,$draft_date) = rm_tr(@$array_ref);
   $rfc_published_date = convert_date($rfc_published_date,1);
   $proposed_date = convert_date($proposed_date,1);
   if ($header =~ /Proposed/) {
      $draft_date = "";
   } else {
      $draft_date = convert_date($draft_date,1);
      $draft_date = "             Draft Date:     $draft_date\n";
   }
   $rfc_name = indent_text($rfc_name,1);
   my $rfc_area = get_area_name($group_acronym);
   my $space = "    ";
   unless (my_defined($proposed_date)) {
      $space .= "          ";
   }
   print qq {$rfc_name
         RFC${rfc_number}  Published: $rfc_published_date
             Proposed Date:  $proposed_date $space Area: $rfc_area
$draft_date
};
   }
}

sub get_area_name {
   my $group_acronym = shift;
   $group_acronym = db_quote($group_acronym);
   my $group_acronym_id = db_select("select acronym_id from acronym where acronym = $group_acronym");
   return "None" unless ($group_acronym_id);
   my $sqlStr = qq {
   select a.name from acronym a,area_directors ad,groups_ietf g
   where g.group_acronym_id = $group_acronym_id
   and ad.id = g.area_director_id
   and ad.area_acronym_id = a.acronym_id
};
   my $area_name = rm_tr(db_select($sqlStr));
   return "None" unless ($area_name);
   return $area_name;
}
