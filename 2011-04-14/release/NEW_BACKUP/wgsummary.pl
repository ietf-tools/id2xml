#!/usr/local/bin/perl

use lib '/home/mlee/RELEASE';
use lib '/export/home/mlee/RELEASE';

use IETF_DBUTIL;
use IETF_UTIL;

my $usage_str = qq {
   USAGE: wgsummary.pl -[mysql|informix] [-byacronym] 

};


die $usage_str unless (defined($ARGV[0]));
die $usage_str if ($ARGV[0] ne "-mysql" and  $ARGV[0] ne "-informix");

$db_mode = 0;
$MYSQL = 2;
$start_date = "1980-1-1";
$concluded_date_is_null = "(g.concluded_date = '' or g.concluded_date is NULL)";
if ($ARGV[0] eq "-mysql") {
   $db_mode = $MYSQL;
   $db_name = "ietf";
}
$ENV{"DBNAME"} = $db_name; 
$start_date = db_quote($start_date);

my $bya = 0;
my $by_str = "By Area";
my $area_sort = "ac1.name, ";
if (defined($ARGV[1])) {
   if ($ARGV[1] eq "-byacronym") {
      $bya = 1;
      $by_str = "By Acronym";
      $area_sort = "";
   } else {
      die $usage_str;
   }
}

my $doc_header = "           IETF Working Group Summary ($by_str)\n\n";

if ($bya) {
   $doc_header .= "\nThe following Area Abreviations are used in this document\n\n";
   my @List = db_select_multiple("select acronym.acronym,acronym.name from acronym,areas where acronym.acronym_id = areas.area_acronym_id AND areas.status_id = 1");
   for $array_ref (@List) {
      my ($acronym,$a_name) = rm_tr(@$array_ref);
      $doc_header .= "$acronym\t - $a_name\n";
   }
   $doc_header .= "\n";
}
print $doc_header;

my $sqlStr = qq {
  select ac1.name,ac1.acronym,ac1.acronym_id,
  ac2.name,ac2.acronym,ac2.acronym_id
  from area_group ag,areas ar,acronym ac1,acronym ac2,groups_ietf g
  where ag.area_acronym_id = ar.area_acronym_id
     and ar.status_id = 1
     and ar.area_acronym_id = ac1.acronym_id
     and ag.group_acronym_id = ac2.acronym_id
     and ac2.acronym_id = g.group_acronym_id
     and g.group_type_id = 1
     and g.start_date > $start_date
     and $concluded_date_is_null
  order by $area_sort ac2.acronym
};
my @List = db_select_multiple($sqlStr);
if ($bya) {
   for $array_ref (@List) {
      my ($a_name,$a_acronym,$a_acronym_id,$g_name,$g_acronym,$g_acronym_id) = 
          rm_tr(@$array_ref);
      $a_acronym = uc($a_acronym);
      print "$g_name ($g_acronym) -- $a_acronym\n";
      my $wg_info_str = get_wg_info_str($g_acronym_id);
      print "$wg_info_str\n";
   }
} else {
   my $current_area = "undefined";
   for $array_ref (@List) {
      my ($a_name,$a_acronym,$a_acronym_id,$g_name,$g_acronym,$g_acronym_id) =
          rm_tr(@$array_ref);
      if ($a_acronym ne $current_area) {
         $current_area = $a_acronym;
	 my $area_header = "$a_name ($current_area)\n";
	 print $area_header;
	 for (my $loop=0;$loop<length($area_header);$loop++) {
	    print "-";
	 }
	 print "\n";
	 my $ad_info_str = get_ad_info_str($a_acronym_id);
	 print "$ad_info_str\n";
      }
      print "$g_name ($g_acronym)\n";
      my $wg_info_str = get_wg_info_str($g_acronym_id);
      print "$wg_info_str\n";
   }
}


exit;

sub get_ad_info_str {
   my $area_acronym_id = shift;
   my $ret_val = "";
   my $sqlStr = qq {
     select p.first_name,p.last_name,e.email_address
     from area_directors a,person_or_org_info p,email_addresses e
     where a.area_acronym_id = $area_acronym_id
     and a.person_or_org_tag = p.person_or_org_tag
     and a.person_or_org_tag = e.person_or_org_tag
     and e.email_priority = 1
   };
   my @List = db_select_multiple($sqlStr);
   for $array_ref (@List) {
      my ($firstname,$lastname,$email) = rm_tr(@$array_ref);
      $ret_val .= "  $firstname $lastname <$email>\n";
   }
   return $ret_val;
}

sub get_wg_info_str {
   my $group_acronym_id = shift;
   my $ret_val = "";

   ##############################
   #      Get WG Chairs Info
   ##############################
   $ret_val .= "   Chairs(s):  ";
   my $sqlStr = qq {
     select p.first_name,p.last_name,e.email_address
     from g_chairs g,person_or_org_info p,email_addresses e
     where g.group_acronym_id = $group_acronym_id
     and g.person_or_org_tag = p.person_or_org_tag
     and g.person_or_org_tag = e.person_or_org_tag
     and e.email_priority = 1
   };
   my @List = db_select_multiple($sqlStr);
   my $gch_count=0;
   for $array_ref (@List) {
      my ($firstname,$lastname,$email) = rm_tr(@$array_ref);
      $ret_val .= "               " if ($gch_count > 0);
      $ret_val .= "$firstname $lastname <$email>\n";
      $gch_count++;
   }
   $sqlStr = qq {
     select email_address,email_subscribe,email_keyword,email_archive
     from groups_ietf where group_acronym_id = $group_acronym_id
   };
   my ($wg_mail,$wg_join,$wg_body,$wg_archive) = rm_tr(db_select($sqlStr));
   $ret_val .= "   WG Mail:    $wg_mail\n";
   $ret_val .= "   To Join:    $wg_join\n";
   if (my_defined($wg_body)) {
      $ret_val .= "   In Body:    $wg_body\n";
   }
   $ret_val .= "   Archive:    $wg_archive\n";

   return $ret_val;
}
