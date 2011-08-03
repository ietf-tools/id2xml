#!/usr/bin/perl

use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

init_database("ietf");
require '/a/www/ietf-datatracker/release/PROCEEDINGS/header.pl';
die "Error\n" unless defined($ARGV[0]);
my $meeting_num = $ARGV[0];
my $section_num = $ARGV[1];
my $text_val = db_select("select ack from meetings where meeting_num=$meeting_num");
open OUT,">$TARGET_DIR/ack.html";
print OUT qq{<HTML>
<HEAD>
<TITLE></TITLE>
</HEAD>
<BODY BGCOLOR="#ffffff" LINK="#004080" BACKGROUND="graphics/peachbkg.gif"><A NAME="TopOfPage"> </A>
<img src='graphics/ib2.gif' width='100%' height=21><br><br>
<h2>1.$section_num Acknowledgements</h2>
<pre>
$text_val
</pre>
</BODY></HTML>
};
close OUT;
exit
