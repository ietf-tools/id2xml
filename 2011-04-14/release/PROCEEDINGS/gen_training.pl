#!/usr/bin/perl

use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

init_database("ietf");
require '/a/www/ietf-datatracker/release/PROCEEDINGS/header.pl';
die "Error\n" unless defined($ARGV[0]);
$meeting_num = $ARGV[0];
$section_num = $ARGV[1];
$group_acronym_id = $ARGV[2];
($group_name,$name)=db_select("select acronym,name from acronym where acronym_id=$group_acronym_id");
$slide_html=get_slide_html();
open OUT,">$TARGET_DIR/$group_name.html";
print OUT qq{<html>
<title>Training</title>
<body bgcolor="#ffffff"  BACKGROUND="graphics/peachbkg.gif">
<A HREF='#slides'><img src='graphics/slides.gif' border=0></A>
<img src='graphics/ib2.gif' width='100%' height=21><br><br>
<H3>$section_num $name Training</h3>

<A name="slides">
<H4>Slides</H4>
$slide_html

</html>

};
close OUT;
exit;

sub get_slide_html {
    my $html_txt = "";
    my @List_slides = db_select_multiple("select slide_num,slide_type_id,slide_name from slides where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id order by order_num");
    if ($#List_slides < 0) {
      $html_txt = "<p>None received.</p>\n";
    } else {
      for my $array_ref (@List_slides) {
        my ($slide_num,$slide_type_id,$slide_name) = @$array_ref;
        my $slide_type = ($slide_type_id==2)?"pdf":"txt";
        my $slide_url = $group_name;
        if ($slide_type_id==1) {
          #$slide_url="$slide_url-$slide_num/sld1.htm";
          $slide_url="$group_name-$slide_num/$group_name-$slide_num.htm";
        } else {
          $slide_url = "$slide_url-$slide_num.$slide_type";
        }
        $html_txt .= "<a href=\"slides/$slide_url\" target=\"_blank\">$slide_name</a><br>\n";
      }
    }
    return $html_txt;
}


