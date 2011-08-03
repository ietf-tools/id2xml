#!/usr/bin/perl

use lib '/a/www/ietf-datatracker/release';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;
use utf8;
require Encode;



init_database("ietf");
die "Error\n" unless defined($ARGV[0]);
my $meeting_num = $ARGV[0];
while (<STDIN>) {
    my $line = Encode::encode_utf8($_);
    my @temp = split ',', $line;
    my $first_name = $temp[0];
    my $last_name = $temp[1];
    my $email_address = $temp[2];
    my $affiliated_company = $temp[3];
    $first_name =~ s/"//g;
    $last_name =~ s/"//g;
    $email_address =~ s/"//g;
    $affiliated_company =~ s/"//g;
    ($first_name,$last_name,$email_address,$affiliated_company) = db_quote($first_name,$last_name,$email_address,$affiliated_company);
    my $exist = db_select("select count(*) from meeting_attendees where email_address = $email_address and meeting_num=$meeting_num");
    unless ($exist) {
      db_update("insert into meeting_attendees (first_name,last_name,affiliated_company,email_address,meeting_num) values ($first_name,$last_name,$affiliated_company,$email_address,$meeting_num)");
    }
}
exit;

