#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

   $MYSQL = 2;

($db_mode,$CURRENT_DATE,$CONVERT_SEED) = init_database($MYSQL);
$is_null = " is NULL ";
$is_not_null = " is NOT NULL ";
if ($db_mode == $MYSQL) {
   $is_null = " = ''";
   $is_not_null = " <> ''";
}
$todate = get_current_date();
my $pwg_group_type_id = db_select("select group_type_id from g_type where group_type='PWG'");
print qq {              IESG Working Group Formation Report

                    $todate

Contact the IESG Secretary <iesg-secretary\@ietf.org>
 for questions or clarifications.




Under Consideration by the IESG
--------------------------------
};

my $sqlStr = qq {
select g.group_acronym_id,a.name,a.acronym,g.proposed_date
from groups_ietf g, acronym a
where g.group_type_id = $pwg_group_type_id
and g.group_acronym_id = a.acronym_id
};

my @List = db_select_multiple($sqlStr);

for $array_ref (@List) {
  my ($group_acronym_id,$group_name,$group_acronym,$proposed_date) = rm_tr(@$array_ref);
  my $area_acronym = uc(get_area_acronym($group_acronym_id));
  print qq {
$group_name ($group_acronym) -- $area_acronym
  Proposed Date:\t\t $proposed_date
 
};


}


exit;

sub get_area_acronym{
   my $group_acronym_id = shift;
   return "None" unless ($group_acronym_id);
   my $sqlStr = qq {
   select a.acronym from acronym a,area_directors ad,groups_ietf g
   where g.group_acronym_id = $group_acronym_id
   and ad.id = g.area_director_id
   and ad.area_acronym_id = a.acronym_id
};
   my $area_acronym = rm_tr(db_select($sqlStr));
   return "None" unless ($area_acronym);
   return $area_acronym;
}



