##########################################################################
# Copyright © 2004 and 2002, Foretec Seminars, Inc.
##########################################################################

package GEN_DBUTIL_IETFDB;
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(get_dbh db_update db_select db_select_multiple init_database db_quote update_db_log db_error_log get_dbh_readonly db_select_secure db_select_multiple_secure db_update_secure);

use lib '/a/www/ietf-datatracker/release/';
use DBI;
use GEN_UTIL;

$passfile="/a/www/ietf-datatracker/release/db_pass";
$passfile_readonly="/a/www/ietf-datatracker/release/db_pass_readonly";

sub db_error_log {
  my $program_name=shift;
  my $sqlStr = shift;
  my $user=shift;
  open IDLOG, ">>/a/www/ietf-datatracker/logs/db_error.log";
  my $c_date = get_current_date();
  my $c_time = get_current_time();
  print IDLOG qq{[$c_date, $c_time] $program_name 
SQL: $sqlStr
User: $user

};
  close IDLOG;
}

sub update_db_log {
  my $program_name=shift;
  my $sqlStr =shift;
  my $user=shift;
  my $c_time = get_current_time();
  my $c_date = get_current_date();
  open LOG, ">>/a/www/ietf-datatracker/logs/update_db.log";
  print LOG qq{[$c_time, $c_date] $program_name
SQL: $sqlStr
User: $user
                                                                                         
};
  close LOG;
}

sub init_database {
  my $dbname = shift;
  return 0 unless (my_defined($dbname));
  $ENV{"DBNAME"} = $dbname;
  return 1;
}

sub db_quote {
  my @list = @_;
  for ($loop=0;$loop<=$#list;$loop++) {
    $list[$loop] =~ s/'/''/g;
    $list[$loop] =~ s/\\/\\\\/g; 
    $list[$loop] = "'" . rm_tr($list[$loop]);
    $list[$loop] .= "'";
  }
   if ($#list == 0) {
     return $list[0];
   } else {
     return @list;
   }
}
                                                                                                     

#sub get_dbh {
#   $dbname = $ENV{"DBNAME"};
#   my $dbh;
#   $dbh = DBI->connect("dbi:mysql:$dbname:stiedprstage1","mlee","sunnyohm");
#   #$dbh = DBI->connect("dbi:mysql:$dbname:localhost","mlee","sunnyohm");
#   return $dbh;
#}

sub get_dbh {
   open (IN,$passfile);
   $_=<IN>;
   chomp;
   my ($user,$pass) = split ':';
   close IN; 
   $dbname = $ENV{"DBNAME"};
   my $dbh;
   $dbh = DBI->connect("dbi:mysql:$dbname:localhost",$user,$pass);
   return $dbh;
}

sub get_dbh_readonly {
   open (IN,$passfile_readonly);
   $_=<IN>;
   chomp;
   my ($user,$pass) = split ':';
   close IN;
   $dbname = $ENV{"DBNAME"};
   my $dbh;
   $dbh = DBI->connect("dbi:mysql:$dbname:chiedprietfdb1.nc.neustar.com",$user,$pass);
   return $dbh;
}

sub db_update {
   my $dbh=shift;
   my $sqlStr = shift;
   my $program_name=shift;
   my $user = shift;
   #my $dbh = get_dbh();
   my $failed = 0;
   my $sth = $dbh->prepare($sqlStr) or $failed = 1;
   if ($failed) {
     db_error_log($program_name,$sqlStr,$user) if (defined($program_name) and defined($user));
     return 0;
   }
   $sth->execute() or $failed=1;
   if ($failed) {
     db_error_log($program_name,$sqlStr,$user) if (defined($program_name) and defined($user));
     return 0;
   }

   #$dbh->disconnect();
   update_db_log($program_name,$sqlStr,$user) if (defined($program_name) and defined($user));
   return 1;
}

sub db_select {
   my $dbh=shift;
   my $sqlStr = shift;
   my @list;
   #my $dbh = get_dbh();
   my $sth = $dbh->prepare($sqlStr);
   $sth->execute() or return 0;
   @list = $sth->fetchrow_array();
   #$dbh->disconnect();
   if ($#list == 0) {
     return $list[0];
   } else {
     return @list;
   }
}

sub db_select_multiple {
   my $dbh=shift;
   my $sqlStr = shift;
   #my $dbh = get_dbh();
   my $sth = $dbh->prepare($sqlStr) or return 0;
   $sth->execute() or return 0;
   my @nList;
   while (my @row = $sth->fetchrow_array()) {
      push @nList, [ @row ];
   }
   #$dbh->disconnect();
   return @nList;
}

sub db_select_multiple_secure {
   my $dbh=shift;
   my $sqlStr = shift;
   my @args = @_;
   my $sth = $dbh->prepare($sqlStr) or return 0;
   $sth->execute(@args) or return 0;
   my @nList;
   while (my @row = $sth->fetchrow_array()) {
      push @nList, [ @row ];
   }
   return @nList;
}
                                                                                    
sub db_select_secure {
   my $dbh=shift;
   my $sqlStr = shift;
   my @args = @_;
   my $sth = $dbh->prepare($sqlStr) or return 0;
   $sth->execute(@args) or return 0;
   my @list;
   @list = $sth->fetchrow_array();
   if ($#list == 0) {
     return $list[0];
   } else {
     return @list;
   }
}
sub db_update_secure {
   my $dbh=shift;
   my $sqlStr = shift;
   my @args = @_;
   my $sth = $dbh->prepare($sqlStr) or $failed = 1;
   $sth->execute(@args) or return 0;
   update_db_log($program_name,$sqlStr,$user) if (defined($program_name) and defined($user));
   return 1;
}

