#!/usr/bin/perl

use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL_NEW;
use IETF;

init_database("ietf");
$dbh=get_dbh();
require '/a/www/ietf-datatracker/release/PROCEEDINGS/header.pl';
die "Error\n" unless defined($ARGV[0]);
my $meeting_num = $ARGV[0];
my ($start_date,$end_date,$city,$state,$country) = db_select($dbh,"select start_date,end_date,city,state,country from meetings where meeting_num=$meeting_num");
my $year = db_select($dbh,"select year('$start_date')");
my $month_name_s=db_select($dbh,"select monthname('$start_date')");
my $month_name_e=db_select($dbh,"select monthname('$end_date')");
my $day_s = db_select($dbh,"select dayofmonth('$start_date')");
my $day_e = db_select($dbh,"select dayofmonth('$end_date')");
my $meeting_num_verbal = get_verbal_number($meeting_num);
my $period = "$month_name_s $day_s - $month_name_e $day_e";
if ($month_name_s eq  $month_name_e) {
  $period = "$month_name_s $day_s-$day_e";
}
open OUT,">$TARGET_DIR/introduction.html";
print OUT qq{<HTML>
<HEAD>
<TITLE>IETF $month_name $year proceedings</TITLE>
</HEAD>
<BODY BGCOLOR="#ffffff" LINK="#004080" BACKGROUND="graphics/peachbkg.gif"><A NAME="TopOfPage"> </A>
<P ALIGN=CENTER><FONT FACE="Times New Roman" SIZE="+3">PROCEEDINGS OF THE $meeting_num_verbal</FONT>
<BR><FONT FACE="Times New Roman" SIZE="+3">INTERNET ENGINEERING TASK FORCE</FONT></P>
<P ALIGN=CENTER><BR><BR><B><FONT FACE="Times New Roman" SIZE="+1">$city, $state, $country</FONT></B>
<BR><B><FONT FACE="Times New Roman" SIZE="+1">$period, $year</FONT></B></P>
<P ALIGN=center><FONT FACE="Times New Roman">Compiled and Edited by: <BR></FONT>
<FONT FACE="Times New Roman">Association Management Solutions</FONT>
<BR><FONT FACE="Times New Roman">48377 Fremont Blvd Suite 117</FONT>
<BR><FONT FACE="Times New Roman">Fremont, CA  94538</FONT></P><P ALIGN=CENTER>
</BODY></HTML>
};
close OUT;
$dbh->disconnect();
exit;

