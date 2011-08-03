#!/usr/local/bin/perl -w

if ($#ARGV < 0) {
   print "\n change_name [-f] <last name> <NewFirstName_NewLastName>\n    or\n";
   print " change_name [-f] <first name> <last name> <NewFirstName_NewLastName>\n\n";
   exit(1);
}
$program_name = "/export/home/mlee/RELEASE/rolodex.pl";

exec("$program_name -change_name @ARGV");