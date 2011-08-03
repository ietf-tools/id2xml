#!/usr/bin/perl

use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

init_database("ietf");
require '/a/www/ietf-datatracker/release/PROCEEDINGS/header.pl';
die "Error\n" unless defined($ARGV[0]);
$meeting_num = $ARGV[0];
open OUT0,">$TARGET_DIR/plenary.html";
print OUT0 qq{<HTML>
<HEAD>
<TITLE>Plenary</TITLE>
</HEAD>
<body bgcolor="#ffffff"  background="graphics/peachbkg.gif">
<img src="graphics/ib2.gif" width="100%" height=21><br><br>
<h2>3  Plenary</h2>

<A HREF="plenaryw.html">Wednesday Plenary</a><br>
<p>
<A HREF="plenaryt.html">Thursday Plenary</a><br>
</HTML>
};
close OUT0;
my $minute_file = db_select("select filename from minutes where meeting_num=$meeting_num and group_acronym_id=-1");
my $minute_text = `cat $TARGET_DIR/minutes/$minute_file`;
$minute_text = "<pre>$minute_text</pre>\n" if ($minute_file =~ /.txt/);
my $slide_html = get_slide_html(-1);
open OUT,">$TARGET_DIR/plenaryw.html";
print OUT qq{<html>
<title>Wednesday Plenary</title>

<body bgcolor="#ffffff"  background="graphics/peachbkg.gif">
<a HREF='#cmr'><img src='graphics/minutes.gif' border=0></a>
<a HREF='#slides'><img src='graphics/slides.gif' border=0></a>
<img src='graphics/ib2.gif' width='100%' height=21><br><br>
<h2>3 Wednesday Plenary</h2>
<a href="plenaryt.html">Thursday Plenary</a>
<a name="cmr">
<h4>Current Meeting Report</h4></a>
<table border=1 bordercolor="#0000FF" width=100% ><tr><td bgcolor="#FFFFFF"><!--hcdel-->
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
$minute_text
</td></tr>
</table>
<a name="slides">
<h4>Slides</h4>
$slide_html
</BODY></HTML>
};
close OUT;

my $minute_file2 = db_select("select filename from minutes where meeting_num=$meeting_num and group_acronym_id=-2");
my $minute_text2 = `cat $TARGET_DIR/minutes/$minute_file2`;
$minute_text2 = "<pre>$minute_text2</pre>\n" if ($minute_file2 =~ /.txt/);
my $slide_html2 = get_slide_html(-2);
open OUT2,">$TARGET_DIR/plenaryt.html";
print OUT2 qq{<html>
<title>Thursday Plenary</title>
                                                                                                            
<body bgcolor="#ffffff"  background="graphics/peachbkg.gif">
<a HREF='#cmr'><img src='graphics/minutes.gif' border=0></a>
<a HREF='#slides'><img src='graphics/slides.gif' border=0></a>
<img src='graphics/ib2.gif' width='100%' height=21><br><br>
<h2>3 Thursday Plenary</h2>
<a href="plenaryw.html">Wednesday Plenary</a>
<a name="cmr">
<h4>Current Meeting Report</h4></a>
<table border=1 bordercolor="#0000FF" width=100% ><tr><td bgcolor="#FFFFFF"><!--hcdel-->
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
$minute_text2
</td></tr>
</table>
<a name="slides">
<h4>Slides</h4>
$slide_html2
</BODY></HTML>
};
close OUT2;

exit;

sub get_slide_html {
    my $group_acronym_id=shift;
    my $html_txt = "";
    my @List_slides = db_select_multiple("select slide_num,slide_type_id,slide_name from slides where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id order by order_num");
    if ($#List_slides < 0) {
      $html_txt = "<p>None received.</p>\n";
    } else {
      for my $array_ref (@List_slides) {
        my ($slide_num,$slide_type_id,$slide_name) = @$array_ref;
        my $slide_type = ($slide_type_id==2)?"pdf":"txt";
        my $slide_url = "";
        if ($group_acronym_id==-1) {
          $slide_url = "plenaryw";
        } elsif ($group_acronym_id==-2) {
          $slide_url = "plenaryt";
        }
        if ($slide_type_id==1) {
          $slide_url="$slide_url-$slide_num/sld1.htm";
        } else {
          $slide_url = "$slide_url-$slide_num.$slide_type";
        }
        $slide_url = "i$slide_url" if ($interim);
        $html_txt .= "<a href=\"slides/$slide_url\" target=\"_blank\">$slide_name</a><br>\n";
      }
    }
    return $html_txt;
}


