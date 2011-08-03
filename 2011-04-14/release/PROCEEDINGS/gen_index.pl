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
my $meeting_date = db_select($dbh,"select start_date from meetings where meeting_num=$meeting_num");
my $month_name=db_select($dbh,"select monthname('$meeting_date')");
my $year = db_select($dbh,"select year('$meeting_date')");
open OUT,">$TARGET_DIR/index.html";
print OUT qq{<HTML>
<HEAD>
<TITLE>IETF $month_name $year</TITLE>
</HEAD>
<FRAMESET COLS="35%,*">
    <FRAME SRC="toc.html" NAME="FRAME_TOC">
    <FRAME SRC="introduction.html" NAME="FRAME_BODY">
<NOFRAMES>
<BODY>
<H2>This Web publication contains frames, but this browser doesn't support frames.</H2></BODY>
</NOFRAMES>
</FRAMESET>
</HTML>
};
close OUT;
$dbh->disconnect();
exit
