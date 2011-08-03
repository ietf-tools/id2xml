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
my ($city,$state,$country) = db_select($dbh,"select city,state,country from meetings where meeting_num=$meeting_num");
my $meeting_num_verbal = "${meeting_num}th";
if ($meeting_num =~ /1$/) {
  $meeting_num_verbal = "${meeting_num}st";
} elsif ($meeting_num =~ /2$/) {
  $meeting_num_verbal = "${meeting_num}nd";
} elsif ($meeting_num =~ /3$/) {
  $meeting_num_verbal = "${meeting_num}rd";
}
$meeting_info = "$meeting_num_verbal IETF Meeting in $city, $state $country";
open TOC,">$TARGET_DIR/toc.html";
print TOC qq{<HTML>
<BODY BGCOLOR="#00448F" LINK="#050505" VLINK="#050505" ><A NAME="#Top"> </A>
<center><img src="graphics/ib.gif" width="100%" height=21></center>
<table width="100%" border=0 cellspacing=5>
<tr><td bgcolor="#00448F">
<P ALIGN=LEFT><A HREF="introduction.html" TARGET="FRAME_BODY">
<B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>1 Introduction</FONT></B></A></P>
</tr>
<tr></td><td bgcolor="#00448F">
<P ALIGN=LEFT><A HREF="ack.html" TARGET="FRAME_BODY">
<B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>1.1 Acknowledgements</FONT></B></A></P>
</tr>
<tr></td><td bgcolor="#00448F">
<P ALIGN=LEFT><A HREF="pr.html" TARGET="FRAME_BODY">
<B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>1.2 IETF Progress Report</FONT></B></A></P>
</tr>
<tr></td><td bgcolor="#00448F">
<P ALIGN=LEFT><A HREF="agenda.html" TARGET="FRAME_BODY">
<B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>1.3 Agenda of IETF $meeting_num</FONT></B></A></P>
</tr>
<tr></td><td bgcolor="#00448F">
<P ALIGN=LEFT><A HREF="overview.html" TARGET="FRAME_BODY">
<B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>1.4 IETF Overview</FONT></B></A></P>
</tr><tr></td><td bgcolor="#00448F">
<P ALIGN=LEFT><A HREF="fm.html" TARGET="FRAME_BODY">
<B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>1.5 Future IETF Meeting Sites</FONT></B></A></P>
<P ALIGN=LEFT><A HREF="http://videolab.uoregon.edu/events/ietf/" TARGET="FRAME_BODY">
<B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>1.6 Audio Stream</FONT></B></A></P>
<P ALIGN=LEFT><A HREF="http://jabber.ietf.org/logs/" TARGET="FRAME_BODY">
<B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>1.7 Jabber Logs</FONT></B></A></P>
</tr></td>
</table>
<p>
<table width="100%" border=0>

<tr><td bgcolor="#00448F">

<P><A HREF="#awg"><B><FONT FACE="Eurostile" COLOR="#ffff00" SIZE=3>2 Area and Working Group Reports</FONT></B></A></P>
</td></tr>
};
my @List_area = db_select_multiple($dbh,"select acronym, name,acronym_id from areas a, acronym b where a.area_acronym_id=b.acronym_id and a.status_id=1 order by acronym");
my $section_number = 0;
for my $array_ref (@List_area) {
  my ($acronym,$name) = @$array_ref;
  $section_number++;
  print TOC qq{<tr><td bgcolor="#00448F">
<P><A HREF="#$acronym"><B><FONT FACE="Eurostile" COLOR="#ffff00" SIZE=3>2.$section_number $name</FONT></B></A></P>
</td></tr>
};
}

print TOC "</table>\n";
print TOC qq{
<p>

<table width="100%" border=0>

<tr><td bgcolor="#00448F">

<P ALIGN=LEFT><A HREF="plenary.html" TARGET="FRAME_BODY">

<B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>3 Plenary</FONT></B></A></P>

</td></tr>
<tr><td bgcolor="#00448F">
                                                                                                           
<P ALIGN=LEFT><A HREF="training.html" TARGET="FRAME_BODY"><br>
                                                                                                           
<B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>4 Training</FONT></B></A></P>
                                                                                                           
</td></tr>
};
my @List_tr = db_select_multiple($dbh,"select group_acronym_id,acronym,name from acronym a, wg_meeting_sessions b where group_acronym_id=acronym_id and group_acronym_id < -2 and meeting_num=$meeting_num and group_acronym_id not in (-16,-14,-13,-8)");
#my @List_tr = db_select_multiple($dbh,"select acronym_id,acronym,name from acronym where acronym_id < -2");
$tr_sub_section=0;
my $training_html = "";
for my $array_ref (@List_tr) {
  my ($acronym_id,$acronym,$name) = @$array_ref;
  $tr_sub_section++;
  $section_str = "4.$tr_sub_section";
  print TOC qq{
<tr><td bgcolor="#00448F"><P ALIGN=LEFT><A HREF="$acronym.html" TARGET="FRAME_BODY"><B><FONT FACE="Times New Roman" color="#EEEEDD" SIZE=2> $section_str   <I> $name Training </I></B></A></td></tr>
};
  $training_html .= qq{
<tr><td><P ALIGN=LEFT><A HREF="$acronym.html" TARGET="FRAME_BODY"><B>$section_str   <I> $name Training </I></B></A></td></tr>
};
  system "$SOURCE_DIR/gen_training.pl $meeting_num $section_str $acronym_id";
}
#Create training.html#
open OUT,">$TARGET_DIR/training.html";
print OUT qq{
<html>
<title>Training</title>
<body bgcolor="#ffffff"  BACKGROUND="graphics/peachbkg.gif">
<img src='graphics/ib2.gif' width='100%' height=21><br><br>
<H2>4 Training</h2>
<table width="100%" border=0>
$training_html
</table>
</html>
};                                                                                                           
close OUT;

$section_number = 5;
my $irtf = db_select($dbh,"select count(*) from minutes where meeting_num=$meeting_num and irtf=> 0");
if (1) {
#if ($irtf) {
  print TOC qq{
<tr><td bgcolor="#00448F">
                                                                                                           
<P ALIGN=LEFT><A HREF="irtf.html" TARGET="FRAME_BODY" NAME="irtf"><br>                                             
<B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>$section_number Internet Research Task Force </FONT></B></A></P>
                                                                                                           
</td></tr>

};
  my @List = db_select_multiple($dbh,"select group_acronym_id,irtf_acronym,irtf_name from irtf a, minutes b where b.irtf > 1 and meeting_num=$meeting_num and group_acronym_id=irtf_id order by irtf_acronym");
  #my @List2 = db_select_multiple($dbh,"select group_acronym_id,irtf_acronym,irtf_name from irtf a, wg_agenda b where b.irtf > 1 and meeting_num=$meeting_num and group_acronym_id=irtf_id order by irtf_acronym");
  #push @List, @List2;
  my $wg_section_number=0;
  for my $array_ref (@List) {
    my ($group_acronym_id,$group_acronym,$group_name) = @$array_ref;
    $wg_section_number++;
    print TOC qq{
<tr><td bgcolor="#00448F"><P ALIGN=LEFT><A HREF="$group_acronym.html" TARGET="FRAME_BODY"><B><FONT FACE="Times New Roman" color="#EEEEDD" SIZE=2> $section_number.$wg_section_number   <FONT size=2 color="#DDDD02"> ($group_acronym)</FONT><I> $group_name </I></B></A></td></tr>
};
    my $charter_html = "";
    $charter_html = db_select($dbh,"select charter_text from irtf where irtf_id=$group_acronym_id");
    open OUT1,">$TARGET_DIR/$group_acronym.html";
#    my $minute_html = get_minute_html($group_acronym_id,$group_acronym,$group_acronym_id,0);
    my $minute_file = get_minute_file($group_acronym_id,$group_acronym,$group_acronym_id,0);
    print OUT1 qq{<html>
<title>$group_name ($group_acronym) Charter</title>
<body bgcolor="#ffffff"  BACKGROUND="graphics/peachbkg.gif">
<A HREF="minutes/$minute_file" TARGET="_BLANK"><img src='graphics/minutes.gif' border=0></A>
<A HREF='#slides'><img src='graphics/slides.gif' border=0></A>
<img src='graphics/ib2.gif' width='100%' height=21><br><br>
<h3>2.$section_number.$wg_section_number $group_name ($group_acronym)</h3>
<i>NOTE: This charter is a snapshot of the $meeting_info. It may now be out-of-date.</i>
$charter_html
<h4><a href="minutes/$minute_file" target="_blank">Meeting Minutes</a></h4>
<br>
};
    my $slide_html = get_slide_html($group_acronym_id,$group_acronym,$group_acronym_id,0);
    print OUT1 qq{<A name="slides">
<H4>Slides</H4>
$slide_html
};
    close OUT1;
  }
  system "$SOURCE_DIR/gen_irtf.pl $section_number";
  $section_number++;
}
print TOC qq{
<tr><td bgcolor="#00448F">
                                                                                                           
<P ALIGN=LEFT><A HREF="attendees.html" TARGET="FRAME_BODY"><br>
                                                                                                           
<B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>$section_number Attendees</FONT></B></A></P>
                                                                                                           
</td></tr>
};
my $interim = db_select($dbh,"select count(*) from minutes where meeting_num=$meeting_num and interim=1");
if ($interim) {
  $section_number++;
  print TOC qq{
<tr><td bgcolor="#00448F">
                                                                                                           
<P ALIGN=LEFT><A HREF="interim.html" TARGET="FRAME_BODY"><br>
                                                                                                           
<B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>$section_number Interim Working Group Meetings</FONT></B></A></P>
                                                                                                           
</td></tr>

};
  my @List = db_select_multiple($dbh,"select acronym_id,acronym,name from acronym a, minutes b where b.interim=1 and meeting_num=$meeting_num and group_acronym_id=acronym_id order by acronym");
  my $wg_section_number=0;
  for my $array_ref (@List) {
    my ($group_acronym_id,$group_acronym,$group_name) = @$array_ref;
    $wg_section_number++;
    print TOC qq{
<tr><td bgcolor="#00448F"><P ALIGN=LEFT><A HREF="i$group_acronym.html" TARGET="FRAME_BODY"><B><FONT FACE="Times New Roman" color="#EEEEDD" SIZE=2> $section_number.$wg_section_number   <FONT size=2 color="#DDDD02"> ($group_acronym)</FONT><I> $group_name </I></B></A></td></tr>
};
    my $charter_html = "";
    $charter_html = `$SOURCE_DIR/gen_wg_charter.pl $group_acronym`;
    open OUT2,">$TARGET_DIR/i$group_acronym.html";
#    my $minute_html = get_minute_html($group_acronym_id,$group_acronym,0,1);
    my $minute_file = get_minute_file($group_acronym_id,$group_acronym,0,1);
    print OUT2 qq{<html>
<title>$group_name ($group_acronym) Charter</title>
<body bgcolor="#ffffff"  BACKGROUND="graphics/peachbkg.gif">
<A HREF="minutes/$minute_file" TARGET="_BLANK"><img src='graphics/minutes.gif' border=0></A>
<A HREF='#slides'><img src='graphics/slides.gif' border=0></A>
<img src='graphics/ib2.gif' width='100%' height=21><br><br>
<h3>2.$section_number.$wg_section_number Interim Meeting - $group_name ($group_acronym)</h3>
<i>NOTE: This charter is a snapshot of the $meeting_info. It may now be out-of-date.</i>
$charter_html
<h4><a href="minutes/$minute_file" target="_blank">Meeting Minutes</a></h4>
<br>

};
    my $slide_html = get_slide_html($group_acronym_id,$group_acronym,0,1);
    print OUT2 qq{<A name="slides">
<H4>Slides</H4>
$slide_html
};
    close OUT2;
  }
  system "$SOURCE_DIR/gen_interim.pl $meeting_num $section_number";

}

print TOC qq{
</table><P>

<center><img src="graphics/ib.gif" width="100%" height=21></center>

<table width="100%" border=0 cellspacing=8>

<tr><td bgcolor="#000074">

<P ALIGN=LEFT><A NAME="awg">

<B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>2 Area and Working Group Reports</FONT></B></A></P></td></tr><tr>

</table>

<table width="%100" border=0 cellpadding=3>
};
$section_number = 0;
for my $array_ref (@List_area) {
  my ($area_acronym,$area_name,$area_acronym_id) = @$array_ref;
  $section_number++;
  print TOC qq{
<tr><td bgcolor="#000074"><P ALIGN=LEFT><A HREF="$area_acronym.html" TARGET="FRAME_BODY" NAME="$area_acronym"><B><FONT FACE="Times New Roman" COLOR="#FFFFFF" SIZE=3>2.$section_number $area_name</FONT></A></td></tr>
};
  my $wg_section_number=1;
  my @List_wg = db_select_multiple($dbh,"select acronym,name,acronym_id from acronym a, area_group b, groups_ietf c where b.area_acronym_id=$area_acronym_id and b.group_acronym_id=a.acronym_id and b.group_acronym_id=c.group_acronym_id and c.meeting_scheduled_old='YES' order by acronym");
  for my $array_ref2 (@List_wg) {
    my ($group_acronym,$group_name,$group_acronym_id) = @$array_ref2;
    print TOC qq{
<tr><td bgcolor="#00448F"><P ALIGN=LEFT><A HREF="$group_acronym.html" TARGET="FRAME_BODY"><B><FONT FACE="Times New Roman" color="#EEEEDD" SIZE=2> 2.$section_number.$wg_section_number   <FONT size=2 color="#DDDD02"> ($group_acronym)</FONT><I> $group_name </I></B></A></td></tr>
};
    my $charter_html = "";
    $charter_html = `$SOURCE_DIR/gen_wg_charter.pl $group_acronym`;
    open OUT,">$TARGET_DIR/$group_acronym.html";
#    my $minute_html = get_minute_html($group_acronym_id,$group_acronym,0,0);
    my $minute_file = get_minute_file($group_acronym_id,$group_acronym,0,0);
    print OUT qq{<html>
<title>$group_name ($group_acronym) Charter</title>
<body bgcolor="#ffffff"  BACKGROUND="graphics/peachbkg.gif">
<A HREF="minutes/$minute_file" TARGET="_BLANK"><img src='graphics/minutes.gif' border=0></A>
<A HREF='#slides'><img src='graphics/slides.gif' border=0></A>
<img src='graphics/ib2.gif' width='100%' height=21><br><br>
<h3>2.$section_number.$wg_section_number $group_name ($group_acronym)</h3>
<i>NOTE: This charter is a snapshot of the $meeting_info. It may now be out-of-date.</i>
$charter_html
<h4><a href="minutes/$minute_file" target="_blank">Meeting Minutes</a></h4>
<br>

};
    my $slide_html = get_slide_html($group_acronym_id,$group_acronym,0,0);
    print OUT qq{<A name="slides">
<H4>Slides</H4>
$slide_html
};
    close OUT;
    $wg_section_number++;
  }
  print TOC qq{
<tr><td bgcolor="#00448F"><P ALIGN=LEFT><A HREF="${area_acronym}_dnm.html" TARGET="FRAME_BODY"><B><FONT FACE="Times New Roman" color="#EEEEDD" SIZE=2> 2.$section_number.$wg_section_number   <I> Groups that did not meet </I></B></A></td></tr>
};
 
}

print TOC "</table>\n";
print TOC qq{
</body>
</html>
};
close TOC;
$dbh->disconnect();
exit;

sub get_slide_html {
    my ($group_acronym_id,$group_acronym,$irtf,$interim) = @_;
    my $html_txt = "";
    my @List_slides = db_select_multiple($dbh,"select slide_num,slide_type_id,slide_name from slides where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim and in_q=0 order by order_num");
    if ($#List_slides < 0) {
      $html_txt = "<p>None received.</p>\n";
    } else {
      for my $array_ref (@List_slides) {
        my ($slide_num,$slide_type_id,$slide_name) = @$array_ref;
        my $slide_type = ($slide_type_id==2)?"pdf":"txt";
        my $slide_url = $group_acronym;
        if ($group_acronym_id==-1) {
          $slide_url = "plenaryw";
        } elsif ($group_acronym_id==-2) {
          $slide_url = "plenaryt";
        }
        if ($slide_type_id==1) {
          #$slide_url="$slide_url-$slide_num/sld1.htm";
          $slide_url="$group_acronym-$slide_num/$group_acronym-$slide_num.htm";
        } else {
          $slide_url = "$slide_url-$slide_num.$slide_type";
        }
        $slide_url = "i$slide_url" if ($interim);
        $html_txt .= "<a href=\"slides/$slide_url\" target=\"_blank\">$slide_name</a><br>\n";
      }
    }
    return $html_txt;
}

sub get_minute_html {
  my ($group_acronym_id,$group_acronym,$irtf,$interim) = @_;
  my $html_txt = "";
  my $minute_file = db_select($dbh,"select filename from minutes where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim");
  unless ($minute_file) {
    $html_txt = "<p>None received.</p>\n";
  } else {
    my $minute_text = `cat $TARGET_DIR/minutes/$minute_file`;
    $minute_text = "<pre>$minute_text</pre>\n" if ($minute_file =~ /.txt/);
    $html_txt = qq{
<table border=1 bordercolor="#0000FF" width=100% ><tr><td bgcolor="#FFFFFF"><!--hcdel-->
<font color="#000000">
$minute_text
</font></td></tr></table>
};
  }
  return $html_txt;
}

sub get_minute_file { 
  my ($group_acronym_id,$group_acronym,$irtf,$interim) = @_;
  my $html_txt = "";
  my $minute_file = db_select($dbh,"select filename from minutes where meeting_num=$meeting_num and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim");
  $minute_file = "" unless ($minute_file); 
  return $minute_file;
}

