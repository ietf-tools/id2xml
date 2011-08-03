#!/usr/bin/perl

use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

init_database("ietf");
require '/a/www/ietf-datatracker/release/PROCEEDINGS/header.pl';
die "Error\n" unless defined($ARGV[0]);
my $section_num = $ARGV[1];
my $meeting_num = $ARGV[0];
my $text_val = "";
my @List = db_select_multiple("select name,acronym,meeting_date,message_body from acronym a, interim_info b where a.acronym_id=b.group_acronym_id and b.meeting_num=$meeting_num order by acronym");
for my $array_ref (@List) {
  my ($group_name,$group_acronym,$meeting_date,$message_body) = @$array_ref;
  $text_val .= qq{<li> <a href="$group_acronym-interim.txt">$group_name - $meeting_date</a><br></li>
};
  open INT,">$TARGET_DIR/$group_acronym-interim.txt";
  print INT $message_body;
  close INT;
}
open OUT,">$TARGET_DIR/interim.html";
print OUT qq{<HTML>
<HEAD>
<TITLE></TITLE>
</HEAD>
<BODY BGCOLOR="#ffffff" LINK="#004080" BACKGROUND="graphics/peachbkg.gif"><A NAME="TopOfPage"> </A>
<img src='graphics/ib2.gif' width='100%' height=21><br><br>
<h2>$section_num Interim Meetings</h2>
$text_val
</BODY></HTML>
};
close OUT;
exit
