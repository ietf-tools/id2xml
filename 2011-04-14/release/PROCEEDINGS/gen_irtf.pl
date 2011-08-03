#!/usr/bin/perl

use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

init_database("ietf");
require '/a/www/ietf-datatracker/release/PROCEEDINGS/header.pl';
die "Error\n" unless defined($ARGV[0]);
my $section_num = $ARGV[0];
my $text_val1 = db_select("select info_text from general_info where info_name='irtf'");
open OUT,">$TARGET_DIR/irtf.html";
print OUT qq{<HTML>
<HEAD>
<TITLE></TITLE>
</HEAD>
<BODY BGCOLOR="#ffffff" LINK="#004080" BACKGROUND="graphics/peachbkg.gif"><A NAME="TopOfPage"> </A>
<h2>$section_num IRTF</h2>
$text_val1
</BODY></HTML>
};
close OUT;
exit
