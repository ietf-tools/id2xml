#!/usr/local/bin/perl -w

if ($#ARGV < 0) {
   print "\n change_fax [-f] <last name> <new fax number>\n    or\n";
   print " change_fax [-f] <first name> <last name> <new fax number>\n\n";
   exit(1);
}
$program_name = "/export/home/mlee/RELEASE/rolodex.pl";

exec("$program_name -change_fax @ARGV");