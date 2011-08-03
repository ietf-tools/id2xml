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

my $usage_str = qq {
To use wginfo command, use the form:

    wginfotohtml wgacronym

};

unless (defined($ARGV[0])) {
   die $usage_str;
}
my $g_acronym = db_quote($ARGV[0]);
my ($group_acronym_id,$group_name,$group_acronym) = rm_tr(db_select("select acronym_id,name,acronym from acronym where acronym=$g_acronym"));
die "FATAL ERROR:Unknown Group Acronym\n\n" unless ($group_acronym_id);
%additional_webs = {};
open INFILE, "/export/home/ietf/wg.www.pages";
while (<INFILE>) {
   last if (/WG-Acronym/);
}
$_ = <INFILE>;
$_ = <INFILE>;
while (<INFILE>) {
  chomp;
  my @temp = split '\|';
  my $name_key = rm_tr($temp[0]);
  my $url_value = rm_tr($temp[1]);
  my $url_name = rm_tr($temp[2]);
  $additional_webs{$name_key}->{'URL_VALUE'} = $url_value;
  $additional_webs{$name_key}->{'URL_NAME'} = $url_name;
}
close INFILE;
print html_header($group_acronym_id,$group_name,$group_acronym);
print process_description($group_acronym);
print process_gm($group_acronym_id);
print process_id($group_acronym_id);
print process_rfc($group_acronym);
print html_footer();

exit;


sub html_header {
  my ($group_acronym_id,$group_name,$group_acronym) = @_;
  my ($group_status_id,$last_modified_date,$group_type_id,$ad_id,$email_address,$email_subscribe,$email_keyword,$email_archive) = rm_tr(db_select("select status_id,last_modified_date,group_type_id,area_director_id,email_address,email_subscribe,email_keyword,email_archive from groups_ietf where group_acronym_id = $group_acronym_id"));
  my $header = "$group_name ($group_acronym)";
  my $dotted_line = "";
  my $str_len = length($header);
  for ($loop=0;$loop<$str_len;$loop++) {
    $dotted_line .= "-";
  }
  my $additional_web_html = "";
  if (defined($additional_webs{$group_acronym})) {
    my $url_value = $additional_webs{$group_acronym}->{'URL_VALUE'};
    my $url_name = $additional_webs{$group_acronym}->{'URL_NAME'};
    $additional_web_html = qq{<hr>
In addition to this official charter maintained by the IETF Secretariat, there is additional information about this working group on the Web at:<br><br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="$url_value">$url_name</a><hr>
};
  }
  my $ret_val = qq{<html>
<title>$header Charter</title>
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

<h1>$header</h1>
$additional_web_html
<p>Last Modified: $last_modified_date

};
#  my $status_value = rm_tr(db_select("select status_value from g_status where status_id = $group_status_id"));
#  my $type_value = rm_tr(db_select("select group_type from g_type where group_type_id = $group_type_id"));
#  if ($type_value eq "WG") {
#    $status_value .= " Working Group";
#  } elsif ($type_value eq "PWG") {
#    $status_value .= " Proposed Working Group";
#  } else {
#    $status_value .= " $type_value";
#  }
#  $ret_val .= qq{ Current Status: $status_value
#
#};
  ####### Group Chairs #########
  my $chairs_str = "";
  my @List = db_select_multiple("select person_or_org_tag from g_chairs where group_acronym_id = $group_acronym_id");
  for $array_ref (@List) {
    my ($chair_tag) = @$array_ref;
    my $chair_name = get_name($chair_tag);
    my $chair_email = get_email($chair_tag);
    $chairs_str .= get_html($chair_name,$chair_email);
    $chairs_str .= "<br>\n";
  }
  ###### Area Directors ########
  $sqlStr = qq {
  select acronym_id,name from acronym a, area_group ag
  where ag.group_acronym_id = $group_acronym_id
  and ag.area_acronym_id = a.acronym_id
  };
  my ($area_acronym_id,$area_name) = rm_tr(db_select($sqlStr));
  unless ($area_acronym_id) {
    $sqlStr = qq {
    select a.acronym_id,a.name from acronym a,area_directors ad, groups_ietf g
    where g.group_acronym_id = $group_acronym_id
    and g.area_director_id = ad.id
    and ad.area_acronym_id = a.acronym_id
    };
    ($area_acronym_id,$area_name) = rm_tr(db_select($sqlStr));
  }
  my $ad_str = "";
  @List = db_select_multiple("select person_or_org_tag from area_directors where area_acronym_id = $area_acronym_id");
  for $array_ref (@List) {
    my ($ad_tag) = @$array_ref;
    my $ad_name = get_name($ad_tag);
    my $ad_email = get_email($ad_tag);
    $ad_str .= get_html($ad_name,$ad_email);
    $ad_str .= "<br>\n";

  }
  ##### Area Advisor #########
  $ad_adv_tag = db_select("select person_or_org_tag from area_directors where id=$ad_id");
  my $ad_adv_name = get_name($ad_adv_tag);
  my $ad_adv_email = get_email($ad_adv_tag);
  $ad_adv_str .= get_html($ad_adv_name,$ad_adv_email);
  $ad_adv_str .= "<br>\n";

  $ret_val .= qq{ <br>
<h2>Chair(s):</h2>
$chairs_str
<h2>$area_name Director(s):</h2>
$ad_str
<h2>$area_name Advisor:</h2>
$ad_adv_str
};
  ###### Technical Advisors ######
  @List = db_select_multiple("select person_or_org_tag from g_tech_advisors where group_acronym_id = $group_acronym_id");
  if ($#List > -1) {
    $ret_val .= "<h2>Technical Advisor(s):</h2>\n";
    for $array_ref (@List) {
      my ($tech_tag) = @$array_ref;
      my $tech_name = get_name($tech_tag);
      my $tech_email = get_email($tech_tag);
      $ret_val .= get_html($tech_name,$tech_email);
      $ret_val .= "<br>\n";
    }
  }
  ###### Group Editors ########
  @List = db_select_multiple("select person_or_org_tag from g_editors where group_acronym_id = $group_acronym_id");
  if ($#List > -1) {
    $ret_val .= "<h2>Editor(s):</h2>\n";
    for $array_ref (@List) {
      my ($editor_tag) = @$array_ref;
      my $editor_name = get_name($editor_tag);
      my $editor_email = get_email($editor_tag);
      $ret_val .= get_html($editor_name,$editor_email);
      $ret_val .= "<br>\n";
    }
  }
  ##### Mail List ############
  $ret_val .= qq {<h2>Mailing Lists:</h2> 
General Discussion: $email_address<br>
To Subscribe: $email_subscribe<br>
};
  if (my_defined($email_keyword)) {
    $ret_val .= "In Body: $email_keyword<br>\n";
  }
  $ret_val .= "Archive: $email_archive<br>\n";
  
  return $ret_val;
}

sub get_html {
  my $name = shift;
  my $email = shift;
  return qq {<a href="mailto:$email"><b>$name &lt;$email&gt;</b></a>};
}

sub process_id {
  my $group_acronym_id = shift;
  my $ret_val = "";
  my @List = db_select_multiple("select id_document_name,filename,revision,start_date,revision_date from internet_drafts where group_acronym_id = $group_acronym_id and status_id = 1 and filename <> 'rfc%' order by start_date");
  if ($#List < 0) {
    $ret_val .= qq {
<h2>No Current Internet-Drafts</h2>
};
  } else {
  $ret_val .= "<h2>Internet-Drafts:</h2>\n";
  for $array_ref (@List) {
    my ($id_document_name,$filename,$revision,$start_date,$revision_date) = rm_tr(@$array_ref);
    $start_date = convert_date($start_date,2);
    $start_date = convert_date($start_date,3);
    $revision_date = convert_date($revision_date,2);
    $revision_date = convert_date($revision_date,3);
    $id_document_name = indent_text($id_document_name,16);
    my $text_file = "/internet-drafts/${filename}-${revision}.txt";
    my @stat_file = stat "/ftp${text_file}";
    my $filesize = $stat_file[7];
    $ret_val .= qq{<a href="$text_file">$id_document_name</a> ($filesize bytes)<br>
};
  } 
  }
  return $ret_val;

}

sub process_rfc {
  my $group_acronym = shift;
  $group_acronym = db_quote($group_acronym);
  my @List = db_select_multiple("select a.rfc_number,b.status_value,a.rfc_name,a.rfc_published_date,c.rfc_number from rfcs a
left outer join rfcs_obsolete c on a.rfc_number = c.rfc_acted_on and c.action='Obsoletes',
rfc_status b where a.group_acronym = $group_acronym and a.status_id = b.status_id order by a.rfc_published_date");
  my $ret_val = "";
  if ($#List < 0) {
     $ret_val .= qq{
<h2>No Request For Comments</h2>
}; 
  } else {
    $ret_val .= "<h2>Request For Comments:</h2>\n";
  for $array_ref (@List) {
    my ($rfc_number,$status_value,$rfc_name,$rfc_published_date,$obs_rfc_number) = rm_tr(@$array_ref);
    $rfc_published_date = convert_date($rfc_published_date,2);
    $rfc_published_date = convert_date($rfc_published_date,3);
    $_ = $status_value;
    $status_value = " PS " if (/Proposed/);
    $status_value = " DS " if (/Draft/);
    $status_value = " S  " if (/Full/);
    $status_value = " H  " if (/Historic/);
    $status_value = " I  " if (/Informational/);
    $status_value = " E  " if (/Experimental/);
    $rfc_name = indent_text2($rfc_name,23);
    my $text_file = "/rfc/rfc${rfc_number}.txt";
    my @stat_file = stat "/ftp${text_file}";
    my $filesize = $stat_file[7];
    my $obs_text = "";
    if ($obs_rfc_number > 0) {
       $obs_text = qq {<font color="red"> obsoleted by RFC $obs_rfc_number </font> };
    }
    $ret_val .= qq{<a href="$text_file">$rfc_name (RFC $rfc_number)</a> ($filesize bytes) $obs_text<br>
};
  }
  }
  return $ret_val;
}

sub process_gm {
  my $group_acronym_id = shift;
  my $ret_val = qq {
<h2>Goals and Milestones:</h2>

};
  my @List = db_select_multiple("select description,expected_due_date,done,done_date from goals_milestones where group_acronym_id = $group_acronym_id order by expected_due_date,done_date");
  $ret_val .= "<table>\n";
  for $array_ref (@List) {
    my ($description,$expected_due_date,$done) = rm_tr(@$array_ref);
    $expected_due_date = convert_date($expected_due_date,2);
    $expected_due_date = convert_date($expected_due_date,3);
    $description = indent_text2($description,16);
    $ret_val .= qq{<tr ALIGN=left VALIGN="top"><td WIDTH=70 VALIGN="top">};
    if ($done =~ /Yes|YES|yes|Done|DONE|done/) {
      $ret_val .= "Done";
    }
    else {
      $ret_val .= "$expected_due_date";
    }
    $ret_val .= "</td><td>&nbsp;&nbsp;</td><td>$description</td></tr>\n";
  }
  $ret_val .= "</table>\n";
  return $ret_val;
}

sub process_description {
  my $group_acronym = shift;
  my $ret_val_body = "";
  my $filename = "/export/home/ietf/WG_DESCRIPTIONS/${group_acronym}.desc.txt";
  unless (open(INFILE,$filename)) {
    $ret_val_body .= "No description available\n\n";
  } else {
    while (<INFILE>) {
      $ret_val_body .= $_;
      #if ($_ eq "\r\n") {
      #  $ret_val .= "<p>\n";
      #}
    }    
    close (INFILE)
  }
  $ret_val_body = format_textarea($ret_val_body);
  my $ret_val = qq{
<h2>Description of Working Group:</h2>
$ret_val_body
};

  return $ret_val;

}

sub html_footer {
  return qq {
<HR>

<i> IETF Secretariat - Please send questions, comments, and/or
suggestions to </i>
<a href="mailto:ietf-web\@ietf.org">ietf-web\@ietf.org</a>. <P>

<A HREF="/html.charters/wg-dir.html">
<IMG SRC="/icons/back.gif"> Return to working group directory. </A> <P>

<A HREF="/home.html">
<IMG SRC="/icons/back.gif"> <IMG SRC="/icons/back.gif">
Return to IETF home page. </A>
</html>

};
}
