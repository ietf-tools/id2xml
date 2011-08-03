#!/usr/local/bin/perl 

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

$TESTDB = 0;
$INFORMIX = 1;
$MYSQL = 2;
$LOG_DIR = "/export/home/mlee/LOGs";
$LOG_FILE = "group_flag.log";
($db_mode,$CURRENT_DATE,$CONVERT_SEED,$is_null) = init_database($MYSQL);

die "Usage: change_group <filename> [group number]\n" unless defined($ARGV[0]);
my $login = getlogin();
my ($filename,$id_document_tag,$ballot_id) = verify_filename();
my ($group_number,$group_name) = get_group_number();
my $documents = "";
my @docList = db_select_multiple("select filename from internet_drafts a, id_internal b where b.ballot_id = $ballot_id and b.id_document_tag = a.id_document_tag");
for $array_ref (@docList) {
  my ($document) = rm_tr(@$array_ref);
  $documents .= "$document "
}
print "\nGroup of Following ID(s): $documents will be changed to $group_name [Y/N] > ";
$_ = <STDIN>;
chomp;
my $confirm = uc($_);
die "Group was not changed\n" unless ($confirm eq "Y");
my $old_group = db_select("select group_flag from id_internal where id_document_tag=$id_document_tag");
my $cur_date = db_select("select current_date");
$cur_date .= " ";
$cur_date .= db_select("select current_time");
my $sqlStr = "update id_internal set group_flag=$group_number where ballot_id = $ballot_id";
die "Group was not changed successfully\n" unless (db_update($sqlStr));
open (LOGFILE,">>$LOG_DIR/$LOG_FILE");
print LOGFILE "$login|$cur_date|$ballot_id|$old_group|$group_number\n";
close LOGFILE;
print "Group was changed successfully\n";
exit;


sub verify_filename {
  my $filename = $ARGV[0];
  $filename = db_quote($filename);
  my $id_document_tag = db_select("select id_document_tag from internet_drafts where filename=$filename");
  die "ERROR: $filename does not exist in the database\n" unless ($id_document_tag);
  my $ballot_id = db_select("select ballot_id from id_internal where id_document_tag=$id_document_tag");
  die "ERROR: $filename is not being reviewed by IESG now\n" unless ($ballot_id);
  return ($filename,$id_document_tag,$ballot_id);
}

sub get_group_number {
  if (defined($ARGV[1])) {
    my $group_flag = $ARGV[1];
    my $group_name = db_select("select group_flag_val from group_flag where group_flag=$group_flag");
    die "ERROR: Invalid group number $group_flag." unless ($group_name);
    return ($group_flag,$group_name);

  } else {
    print "\nGroup numbers and names\n--------------------------\n";
    my @List = db_select_multiple("select group_flag,group_flag_val from group_flag order by group_flag");
    for $array_ref (@List) {
      my ($group_flag,$val) = rm_tr(@$array_ref);
      print "$group_flag  $val\n";
    }
    print "Select group number > ";
    my $group_flag = <STDIN>;
    chomp($group_flag);
    my $group_name = db_select("select group_flag_val from group_flag where group_flag=$group_flag");
    die "ERROR: Invalid group number $group_flag." unless ($group_name);
    return ($group_flag,$group_name);
  }
}



