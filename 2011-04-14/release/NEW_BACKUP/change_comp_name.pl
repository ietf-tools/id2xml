#!/usr/local/bin/perl -w

if ($#ARGV < 0) {
   print "\n change_comp_name [-f] <last name> <company name>\n    or\n";
   print " cnage_comp_name [-f] <first name> <last name> <company_name>\n\n";
   exit(1);
}
$program_name = "/export/home/mlee/RELEASE/rolodex.pl";

exec("$program_name -change_comp_name @ARGV");