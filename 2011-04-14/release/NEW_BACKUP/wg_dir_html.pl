#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

   $TESTDB = 0;
   $INFORMIX = 1;
   $MYSQL = 2;

($db_mode,$CURRENT_DATE,$CONVERT_SEED) = init_database($MYSQL);
$is_null = " is NULL ";
$is_not_null = " is NOT NULL ";
if ($db_mode == $MYSQL) {
   $is_null = " = ''";
   $is_not_null = " <> ''";
}
$print_mode = 0;
$or_AG = "";
$PATH = "/usr/local/etc/httpd/htdocs/html.charters";
if (defined($ARGV[0]) and $ARGV[0] eq "-print") {
   $PATH = "/export/home/ietf/public_html/print.charters";
   $print_mode = 1;
   $or_AG = "or group_type_id = 4";
}
open HTML,">$PATH/wg-dir.html" or die "Can't open target file to write\n";
$current_date = get_current_date();
$current_time = get_current_time();
##### Populate area web page hash table #####
%area_web = {};
open INFILE, "/export/home/ietf/wg.www.pages";
while (<INFILE>) {
  last if (/Area Name/);
}
$_ = <INFILE>;
while (<INFILE>) {
  chomp;
  last if ($_ eq "#");
  my @temp = split '\|';
  my $name_key = rm_tr($temp[0]);
  my $url_value = rm_tr($temp[1]);
  my $url_name = rm_tr($temp[2]);
  $area_web{$name_key}->{'URL_VALUE'} = $url_value;
  $area_web{$name_key}->{'URL_NAME'} = $url_name;
}
  
close INFILE;
$html_top = qq{
<html>
<head>
<title> Active IETF Working Groups </title>
</head>
<body bgcolor="#ffffff" >
<center>
<table border=0 cellpadding=0 cellspacing=0>
<tr>
<td><a href="/home.html"><img src="/images/header/ietflogo_sm.gif" border=0></a></td>
<td><a href="/home.html"><img src="/images/header/home11.gif" border=0></a></td>
<td><img src="/images/header/separator.gif" border=0></td>
<td><a href="/html.charters/wg-dir.html"><img src="/images/header/wg11.gif" border=0></a></td>
<td><img src="/images/header/separator.gif" border=0></td>
<td><a href="/meetings/meetings.html"><img src="/images/header/meetings11.gif" border=0></a></td>
<td><img src="/images/header/separator.gif" border=0></td>
<td><a href="/proceedings/directory.html"><img src="/images/header/proceed11.gif"  border=0></a></td>
<td><img src="/images/header/separator.gif" border=0></td>
<td><a href="/ID.html"><img src="/images/header/id-index11.gif" border=0></a></td>
<td><img src="/images/header/separator.gif" border=0></td>
<td><a href="/rfc.html"><img src="/images/header/rfc11.gif" border=0></a></td>
</tr>
</table>
</center>
<hr>

<h1> Active IETF Working Groups </h1> </p>
<hr>
<b>
This list and the associated charters were generated on
    $current_date at $current_time<p>

If you find errors, please notify <i> <a href="mailto:ietf-web\@ietf.org">ietf-web\@ietf.org</a></i>.
    </b>
<p>Can't find a specific Working Group? It may no longer be active. Check the list of <a href=OLD/index.html>Concluded</a> Working Groups.
    <hr>

};

$html_bottom = qq {
<hr>
<i> IETF Secretariat - Please send questions, comments, and/or 
    suggestions to </i> <a href="mailto:ietf-web\@ietf.org">ietf-web\@ietf.org</a>. <p>

<a HREF="/home.html">
<img SRC="/icons/back.gif"> Return to IETF home page. </a>
</html>


};

my $html_body = get_body();

print HTML $html_top;
print HTML $html_body; 
print HTML $html_bottom;

close HTML;
exit;

sub get_body {
  my $html_txt = "<h2>Table of Contents</h2>\n";
  my $start_date = db_quote(convert_date("1/1/1980",$CONVERT_SEED));
  my $sqlStr = qq {
  select ac.name,ac.acronym_id from acronym ac,groups_ietf g,area_group ag
  where ag.area_acronym_id = ac.acronym_id
  and ag.group_acronym_id = g.group_acronym_id 
  and (g.group_type_id = 1 $or_AG)
  and g.status_id = 1
  group by 1,2
  order by 1
};
  my $wg_content = "";
  my @List = db_select_multiple($sqlStr);
  for $array_ref (@List){
    my ($area_name,$area_acronym_id) = rm_tr(@$array_ref);
    $html_txt .= qq {<li><a href="#${area_name}">$area_name</a>
};
    $wg_content .= get_wg_content($area_acronym_id,$area_name);
  }
  $html_txt .= "<hr>\n";
  $html_txt .= $wg_content;
  return $html_txt;
}

sub get_wg_content {
  my $area_acronym_id = shift;
  my $area_name = shift;
  my $html_txt = "<a name=\"$area_name\"><h2>$area_name</h2></a>\n";
  $html_txt .= "Area Director(s): <br>\n";
  my @List = db_select_multiple("select person_or_org_tag from area_directors where area_acronym_id = $area_acronym_id");
  for $array_ref (@List) {
    my ($person_or_org_tag) = @$array_ref;
    my $name = get_name($person_or_org_tag);
    my $email = get_email($person_or_org_tag);
    $html_txt .= qq {<li> <a href="mailto:$email">$name &lt;$email&gt;</a><br>
};  
  }

  if (defined($area_web{$area_name})) {
    my $url = $area_web{$area_name}->{'URL_VALUE'};
    my $url_name = $area_web{$area_name}->{'URL_NAME'};
    $html_txt .= qq {<br>Area Specific Web Page:<br>
<li> <a href="$url">$url_name</a><br>
};    
  }
  $html_txt .= qq {<br>Working Groups:<br>
<table>
<tr><td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td><td></td><td></td></tr>
};
  my $sqlStr = qq {
  select a.acronym,a.name from acronym a, area_group ag, groups_ietf g
  where ag.area_acronym_id = $area_acronym_id
  and ag.group_acronym_id = g.group_acronym_id
  and g.status_id = 1
  and (g.group_type_id = 1 $or_AG)
  and g.group_acronym_id = a.acronym_id
  order by a.acronym
};
  @List = db_select_multiple($sqlStr);
  for $array_ref (@List) {
    my ($acronym,$name) = rm_tr(@$array_ref); 
    $html_txt .= qq{<tr><td></td><td><a href="/html.charters/${acronym}-charter.html">$acronym</a></td><td>$name</td></tr>
};
  }
  $html_txt .= "</table><hr>\n";  

  return $html_txt;
}


