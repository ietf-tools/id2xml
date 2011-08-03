#!/usr/local/bin/perl -w

if ($#ARGV < 0) {
   print "\n phone <last name>\n    or\n";
   print " phone <first name> <last name>\n\n";
   exit(1);
}
$program_name = "/export/home/mlee/RELEASE/rolodex.pl";

exec("$program_name -phone @ARGV");