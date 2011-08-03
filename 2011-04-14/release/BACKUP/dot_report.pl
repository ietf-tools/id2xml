#!/usr/local/bin/perl -w

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

$MYSQL = 2;

init_database($MYSQL);


$sqlStr = qq{SELECT last_name,first_name, a.person_or_org_tag
     FROM person_or_org_info a,g_chairs
	where g_chairs.person_or_org_tag=a.person_or_org_tag
	ORDER BY last_name,first_name,a.person_or_org_tag
};

my @List = db_select_multiple($sqlStr);
print "BLUE DOT REPORT\n\n";
print "NAMES                  ROSTER                              BADGE\n";
print "----------------------------------------------------------------\n";
my $pre_tag = 0;
for $array_ref (@List) {
  my ($last_name,$first_name,$person_or_org_tag) = rm_tr(@$array_ref);
  my $full_name = "$last_name, $first_name";
  my $badge = "BLUE";
  my $roster = "";
  my $sqlStr2 = qq{SELECT acronym,meeting_scheduled
     FROM person_or_org_info a,acronym,groups_ietf,g_type,g_status,g_chairs
     where g_chairs.person_or_org_tag = $person_or_org_tag 
        and g_type.group_type_id=groups_ietf.group_type_id
        and g_status.status_id=groups_ietf.status_id
        and g_chairs.person_or_org_tag=a.person_or_org_tag
        and g_chairs.group_acronym_id=groups_ietf.group_acronym_id
        and groups_ietf.group_acronym_id=acronym.acronym_id
        and g_status.status_value = "Active"
        and (g_type.group_type = "WG"
         or g_type.group_type = "BOF"
         or g_type.group_type = "AG"
         or g_type.group_type = "PWG")
};
  my @List2 = db_select_multiple($sqlStr2);
  for $array_ref2 (@List2) {
    my ($val) = rm_tr(@$array_ref2);
    $roster .= "$val, ";
  }
  chop($roster);chop($roster);
  if ($roster ne "" and $person_or_org_tag != $pre_tag) {
    format STDOUT =
@<<<<<<<<<<<<<<<<<<<<< @<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<   @<<<<<<<<
$full_name,            $roster,                            $badge
.
  write STDOUT;
  }
  $pre_tag = $person_or_org_tag;
}

exit;



    
