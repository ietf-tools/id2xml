#!/usr/local/bin/perl -w

if ($#ARGV < 0) {
   print "\n change_email [-f] <last name> <new email>\n    or\n";
   print " change_email [-f] <first name> <last name> <new email>\n\n";
   exit(1);
}
$program_name = "/export/home/mlee/RELEASE/rolodex.pl";

exec("$program_name -change_email @ARGV");