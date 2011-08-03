package IETF_DBUTIL;
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(init_database get_dbh db_quote db_update db_select db_select_multiple get_name get_email get_intended_status_value);

use lib '/export/home/mlee/RELEASE/';
use DBI;
use IETF_UTIL;


sub init_database {
   my $request_db = shift;
   $TESTDB = 0;
   $MYSQL = 2;
   $CURRENT_DATE = "CURRENT_DATE"; # "TODAY" for Informix, "CURRENT_DATE" for MySQL
   $CONVERT_SEED = 1; # To convert date format to fit into the current database eng
   $is_null = " = '' ";
   $db_mode = $MYSQL;
   $ENV{"DBNAME"} = "ietf";
   return ($db_mode,$CURRENT_DATE,$CONVERT_SEED,$is_null);
}

sub get_dbh {
   $dbname = $ENV{"DBNAME"};
   my $dbh;
   $dbh = DBI->connect("dbi:mysql:$dbname:ran","mlee","sunnyohm");
   return $dbh;
}


sub db_quote {
  my @list = @_;
  my $dbh = get_dbh();
  for ($loop=0;$loop<=$#list;$loop++) {
    $list[$loop] =~ s/'/''/g;
    if ($ENV{"DBNAME"} =~ /ietf/) {
	  $list[$loop] = "'" . rm_tr($list[$loop]);
	  $list[$loop] .= "'";
	} else {
      $list[$loop] = $dbh->quote(rm_tr($list[$loop]));
    }
  }
  $dbh->disconnect();
   if ($#list == 0) {
     return $list[0];
   } else {
     return @list;
   }
}

sub db_update {
   my $sqlStr = shift;
   my $dbh = get_dbh();
   my $sth = $dbh->prepare($sqlStr) || return 0;
   $sth->execute();
   #$sth->execute() || return 0;
   $dbh->disconnect();
   return 1;
}

sub db_select {
   my $sqlStr = shift;
   my @list;
   my $dbh = get_dbh();
   my $sth = $dbh->prepare($sqlStr) || print "$sqlStr\n";
   $sth->execute();
   @list = $sth->fetchrow_array();
   #$dbh->disconnect();
   if ($#list == 0) {
     return $list[0];
   } else {
     return @list;
   }
}

sub db_select_multiple {
   my $sqlStr = shift;
   my $dbh = get_dbh();
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute();
   my @nList;
   while (my @row = $sth->fetchrow_array()) {
      push @nList, [ @row ];
   }
   return @nList;
}

sub get_name {
   my $person_or_org_tag = shift;
   my $reverse = shift;
   my ($firstname,$lastname) = rm_tr(db_select("select first_name,last_name from person_or_org_info where person_or_org_tag = $person_or_org_tag"));
   return "$lastname, $firstname" if ($reverse);
   return "$firstname $lastname";
}

sub get_email {
   my $person_or_org_tag = shift;
   my $ret_val = rm_tr(db_select("select email_address from email_addresses where person_or_org_tag = $person_or_org_tag"));                     

   return $ret_val;
}

sub get_intended_status_value {
  my $id = shift;
  my $draft_type = shift;
  my $table_name = "id_intended_status";
  $table_name = "rfc_intend_status" if ($draft_type eq "RFC");
  my $ret_val = rm_tr(db_select("select status_value from $table_name where intended_status_id = $id"));
  return $ret_val;
}


