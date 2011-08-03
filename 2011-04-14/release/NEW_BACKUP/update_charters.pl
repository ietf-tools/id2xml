#!/usr/local/bin/perl

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

my $start_date = db_quote(convert_date("1/1/1980",$CONVERT_SEED));
my $all_area = 0;
if (defined($ARGV[0])) {
  die "FATAL ERROR: Unknown Switch $ARGV[0]\n" unless ($ARGV[0] eq "-all");
  $all_area = 1;
} 
my $sqlStr = qq {
select a.acronym from acronym a,groups_ietf g
where g.group_acronym_id = a.acronym_id
and a.acronym <> 'none'
and g.status_id = 1
and g.group_type_id = 1
and g.start_date > $start_date
};

unless ($all_area) {
  my $gi_set = "";
  my @subList = db_select_multiple("select group_acronym_id from internet_drafts where last_modified_date = $CURRENT_DATE");
  for $array_ref (@subList) {
    my ($gi) = @$array_ref;
    $gi_set .= "$gi,";
  }
  if (my_defined($gi_set)) {
    chop($gi_set);
  } else {
    $gi_set = "0000";
  }
  $sqlStr .= qq {and (g.last_modified_date = $CURRENT_DATE or
g.group_acronym_id in ($gi_set))
};
}

#die "$sqlStr\n";


my @List = db_select_multiple($sqlStr);
for $array_ref (@List) {
  my ($acronym) = rm_tr(@$array_ref);
  print "Processing $acronym...\n";
  my $command = qq{sh -c "mkdir /ftp/ietf/$acronym 2>&1"};
  unless (-e "/ftp/ietf/$acronym") {
    system $command;
  }
  $command = qq|/export/home/mlee/RELEASE/wginfo.pl $acronym -charter -id -rfc > /ftp/ietf/$acronym/${acronym}-charter.txt|;
  system $command;
  $command = qq|/export/home/mlee/RELEASE/wginfotohtml.pl $acronym > /usr/local/etc/httpd/htdocs/html.charters/${acronym}-charter.html|;
  system $command;
}
  system "/export/home/mlee/RELEASE/wg_dir_html.pl";
exit;
