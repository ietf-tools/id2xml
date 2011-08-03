#!/usr/local/bin/perl -w

if ($#ARGV < 0) {
   print "\n change_phone.pl [-f] <last name> <new phone number>\n    or\n";
   print " change_phone.pl [-f] <first name> <last name> <new phone number>\n\n";
   exit(1);
}
$program_name = "/export/home/mlee/RELEASE/rolodex.pl";

exec("$program_name -change_phone @ARGV");