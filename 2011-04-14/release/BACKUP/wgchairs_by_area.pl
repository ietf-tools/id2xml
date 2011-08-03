#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE';
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
$TARGET_DIR = "/export/home/ietf/MAILING-LISTS";
#$TARGET_DIR = ".";

$sqlStr_area = qq{
select a.acronym,a.acronym_id from acronym a,areas b
where a.acronym_id = b.area_acronym_id and
b.status_id = 1
order by a.acronym
};
my @areaList = db_select_multiple($sqlStr_area);
for $array_ref_area (@areaList) {
  my ($area_acronym,$area_acronym_id) = rm_tr(@$array_ref_area);


  open OUTFILE, ">$TARGET_DIR/${area_acronym}-chairs";
  close OUTFILE;
  my @adList = db_select_multiple("select person_or_org_tag from area_directors where area_acronym_id = $area_acronym_id");
  for $array_ref_ad (@adList) {
    my ($person_or_org_tag) = @$array_ref_ad;
    my $name = get_name($person_or_org_tag,1);
    $name = "\"$name\"";
    my $email = get_email($person_or_org_tag);
    $email = "<$email>";
    $area_acronym2 = "($area_acronym)";

format REPORT2 =
@<<<<<<<<<<<<<<<<<<<<<<<<<<<  @<<<<<<<<<<<<  @<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
$name,$area_acronym2,$email
.

    open REPORT2,">>$TARGET_DIR/${area_acronym}-chairs";
    write REPORT2;
    close REPORT2;

  }
  my $start_date = db_quote(convert_date("1/1/1980",$CONVERT_SEED));
  $sqlStr = qq {
select gc.person_or_org_tag,a.acronym from g_chairs gc,groups_ietf g, acronym a, area_group ag
where gc.group_acronym_id = g.group_acronym_id
and g.start_date > $start_date
and g.concluded_date $is_null
and g.status_id = 1
and g.group_acronym_id = a.acronym_id
and g.group_acronym_id = ag.group_acronym_id
and ag.area_acronym_id = $area_acronym_id
order by a.acronym
};

  my @List = db_select_multiple($sqlStr);
  for $array_ref (@List) {
    my ($person_or_org_tag,$acronym) = rm_tr(@$array_ref);
    my $name = get_name($person_or_org_tag,1);
    $name = "\"$name\"";
    my $email = get_email($person_or_org_tag);
    $email = "<$email>";
    $acronym = "($acronym)";
format REPORT = 
@<<<<<<<<<<<<<<<<<<<<<<<<<<<  @<<<<<<<<<<<<  @<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
$name,$acronym,$email
.

    open REPORT,">>$TARGET_DIR/${area_acronym}-chairs";
    write REPORT;
    close REPORT;
  }


}
exit;
