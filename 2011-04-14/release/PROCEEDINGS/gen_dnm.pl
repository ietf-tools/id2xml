#!/usr/bin/perl

use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;
init_database("ietf");
$meeting_num = $ARGV[0];
require '/a/www/ietf-datatracker/release/PROCEEDINGS/header.pl';

my $area_num=0;
my @List=db_select_multiple("select area_acronym_id,name,acronym from areas a, acronym b where a.area_acronym_id=b.acronym_id and status_id=1 order by acronym");
for my $array_ref (@List) {
  my ($area_acronym_id,$area_name,$area_acronym) = @$array_ref;
  $area_num++;
  my @List_dm=db_select_multiple("select name,acronym from area_group a, groups_ietf b, acronym c where a.area_acronym_id=$area_acronym_id and a.group_acronym_id=b.group_acronym_id and b.status_id=1 and b.meeting_scheduled_old = 'Yes' and b.group_acronym_id=c.acronym_id order by acronym");
  my $dm_list = "";
  for my $array_ref (@List_dm) {
    my ($group_name,$group_acronym) = @$array_ref;
    $dm_list .= qq{<A HREF="$group_acronym.html" TARGET="_self"><B><FONT FACE="Times New Roman" COLOR="#0000ff" SIZE=3> $group_name ($group_acronym) </FONT></B></A><p>
};
  }
  open AREA,">$TARGET_DIR/$area_acronym.html"; 
  open DNM,">$TARGET_DIR/${area_acronym}_dnm.html"; 
  print AREA qq{<html>
<head><title>2.$area_num</title></head>

<body bgcolor="#ffffff"  background="graphics/peachbkg.gif">
<img src="graphics/ib2.gif" width="100%" height=21><br><br>
<h2>2.$area_num  $area_name</h2>
<a name="dm"><h4>Groups that met at IETF $meeting_num</h4></a><br>
$dm_list
<a name="dnm"><h4>Groups that did not meet at IETF $meeting_num</h4></a><br>
};
  print DNM qq{<html>
<head>
<title>$area_name Groups that did not meet at IETF $meeting_num</title>
</head>
<body bgcolor="#ffffff"  background="graphics/peachbkg.gif">
<img src="graphics/ib2.gif" width="100%" height=21><br><br>
<h2>2.$area_num  $area_name</h2>
<h3>Groups that did not meet at IETF $meeting_num</h3><br>
};
  my @List_dnm = db_select_multiple("select acronym,acronym_id,name from area_group a, groups_ietf b, acronym c where a.area_acronym_id=$area_acronym_id and a.group_acronym_id=b.group_acronym_id and b.status_id=1 and b.meeting_scheduled_old <> 'Yes' and b.group_acronym_id=c.acronym_id and group_type_id = 1 order by acronym");
  for my $array_ref2 (@List_dnm) {
    my ($group_acronym,$group_acroym_id,$group_name) = @$array_ref2;
    print AREA qq{<A HREF="$group_acronym.html" TARGET="_self"><B><FONT FACE="Times New Roman" COLOR="#0000ff" SIZE=3> $group_name ($group_acronym) </FONT></B></A><p>
};
    print DNM qq{<A HREF="$group_acronym.html" TARGET="_self"><B><FONT FACE="Times New Roman" COLOR="#0000ff" SIZE=3> $group_name ($group_acronym) </FONT></B></A><p>
};
    my $charter_html = "";
    $charter_html = `$SOURCE_DIR/gen_wg_charter.pl $group_acronym`;
    open CHARTER,">$TARGET_DIR/$group_acronym.html";
    print CHARTER qq{<html>
<title>$group_name ($group_acronym) Charter</title>
<body bgcolor="#ffffff"  BACKGROUND="graphics/peachbkg.gif">
<h3>$group_name ($group_acronym)</h3>
<i>NOTE: This charter is a snapshot of the $meeting_info. It may now be out-of-date.</i>
$charter_html
};
    close CHARTER;
  }
  print AREA "</body></html>\n";
  print DNM "</body></html>\n";
  close DNM;
  close AREA;
}


exit

