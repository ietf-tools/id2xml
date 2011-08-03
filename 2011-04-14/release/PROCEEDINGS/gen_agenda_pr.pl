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
my $text_val = `/a/www/ietf-datatracker/release/PROCEEDINGS/meeting_agenda_html.cgi meeting_num=$meeting_num`;
#my $text_val = db_select("select agenda_html from meetings where meeting_num=$meeting_num");
open OUT,">$TARGET_DIR/agenda.html";
print OUT qq{<HTML>
<HEAD>
<TITLE></TITLE>
</HEAD>
<BODY BGCOLOR="#ffffff" LINK="#004080" BACKGROUND="graphics/peachbkg.gif"><A NAME="TopOfPage"> </A>
<img src='graphics/ib2.gif' width='100%' height=21><br><br>
<h2>1.$section_num Agenda of IETF $meeting_num</h2>
$text_val
</BODY></HTML>
};
close OUT;

$text_val = `/a/www/ietf-datatracker/release/PROCEEDINGS/meeting_agenda_text.cgi meeting_num=$meeting_num`;
#$text_val = db_select("select agenda_text from meetings where meeting_num=$meeting_num");
open OUT2,">$TARGET_DIR/agenda.txt";
print OUT2 qq{
$text_val
};
close OUT2;

exit
