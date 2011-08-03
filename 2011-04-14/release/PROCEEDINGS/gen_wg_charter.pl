#!/usr/bin/perl -w
##########################################################################
# Copyright © 2002, Foretec Seminars, Inc.
##########################################################################

use lib '/a/www/ietf-datatracker/release';
use GEN_UTIL;
use GEN_DBUTIL_NEW;
use IETF;

init_database("ietf");
$dbh=get_dbh();
my $g_acronym = db_quote($ARGV[0]);
my ($group_acronym_id,$group_name,$group_acronym) = rm_tr(db_select($dbh,"select acronym_id,name,acronym from acronym where acronym=$g_acronym"));
die "FATAL ERROR:Unknown Group Acronym\n\n" unless ($group_acronym_id);
%additional_webs = ();
open INFILE, "/a/www/www6/wg.www.pages";
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
$dbh->disconnect();
exit;


sub html_header {
  my ($group_acronym_id,$group_name,$group_acronym) = @_;
  my ($group_status_id,$last_modified_date,$group_type_id,$ad_id,$email_address,$email_subscribe,$email_keyword,$email_archive) = rm_tr(db_select($dbh,"select status_id,last_modified_date,group_type_id,area_director_id,email_address,email_subscribe,email_keyword,email_archive from groups_ietf where group_acronym_id = $group_acronym_id"));
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
  my $ret_val = qq{
$additional_web_html
<p>Last Modified: $last_modified_date

};
  ####### Group Chairs #########
  my $chairs_str = "";
  my @List = db_select_multiple($dbh,"select person_or_org_tag from g_chairs where group_acronym_id = $group_acronym_id");
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
  my ($area_acronym_id,$area_name) = rm_tr(db_select($dbh,$sqlStr));
  unless ($area_acronym_id) {
    $sqlStr = qq {
    select a.acronym_id,a.name from acronym a,area_directors ad, groups_ietf g
    where g.group_acronym_id = $group_acronym_id
    and g.area_director_id = ad.id
    and ad.area_acronym_id = a.acronym_id
    };
    ($area_acronym_id,$area_name) = rm_tr(db_select($dbh,$sqlStr));
  }
  my $ad_str = "";
  @List = db_select_multiple($dbh,"select person_or_org_tag from area_directors where area_acronym_id = $area_acronym_id");
  for $array_ref (@List) {
    my ($ad_tag) = @$array_ref;
    my $ad_name = get_name($ad_tag);
    my $ad_email = get_email($ad_tag);
    $ad_str .= get_html($ad_name,$ad_email);
    $ad_str .= "<br>\n";

  }
  $ad_str .= "<br>* The Real-time Applications and Infrastructure Area Directors were seated during the IETF 65.<br>\n" if ($area_acronym_id==1683); 
  ##### Area Advisor #########
  $ad_adv_tag = db_select($dbh,"select person_or_org_tag from area_directors where id=$ad_id");
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
  @List = db_select_multiple($dbh,"select person_or_org_tag from g_tech_advisors where group_acronym_id = $group_acronym_id");
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
  @List = db_select_multiple($dbh,"select person_or_org_tag from g_editors where group_acronym_id = $group_acronym_id");
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

  ###### Group Secretary ########
  @List = db_select_multiple($dbh,"select person_or_org_tag from g_secretaries where group_acronym_id = $group_acronym_id");
  if ($#List > -1) {
    $ret_val .= "<h2>Secretary(ies):</h2>\n";
    for $array_ref (@List) {
      my ($sec_tag) = @$array_ref;
      my $sec_name = get_name($sec_tag);
      my $sec_email = get_email($sec_tag);
      $ret_val .= get_html($sec_name,$sec_email);
      $ret_val .= "<br>\n";
    }
  }

  ##### Mail List ############
  my $email_subscribe_link = "";
  if ($email_subscribe =~ /http/) {
    $email_subscribe_link = $email_subscribe;
  } else {
    $email_subscribe_link = "mailto:$email_subscribe";
  }
  $ret_val .= qq{<h2>Mailing Lists:</h2> 
General Discussion: $email_address<br>
To Subscribe: <a href="$email_subscribe_link">$email_subscribe</a><br>
};
  if (my_defined($email_keyword)) {
    $ret_val .= "In Body: $email_keyword<br>\n";
  }
  my @temp = split ' ',$email_archive;
  my $email_archive_url = $temp[0];
  $ret_val .= "Archive: <a href=\"$email_archive_url\">$email_archive</a><br>\n";
  
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
  my @List = db_select_multiple($dbh,"select id_document_name,filename,revision,start_date,revision_date from internet_drafts where group_acronym_id = $group_acronym_id and status_id = 1 and filename <> 'rfc%' order by start_date");
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
    my $text_file = "${filename}-${revision}.txt";
    $ret_val .= qq{<li> <a href="IDs/$text_file" target="_blank">$text_file</a><br>
};
  } 
  }
  return $ret_val;

}

sub process_rfc {
  my $group_acronym = shift;
  $group_acronym = db_quote($group_acronym);
  my @List = db_select_multiple($dbh,"select a.rfc_number,b.status_value,a.rfc_name from rfcs a,
rfc_status b where a.group_acronym = $group_acronym and a.status_id = b.status_id order by a.rfc_number");
  my $ret_val = "";
  if ($#List < 0) {
     $ret_val .= qq{
<h2>No Request For Comments</h2>
}; 
  } else {
    $ret_val .= qq{<h2>Request For Comments:</h2>
<table>
<tr align=left><th>RFC</th><th>Status</th><th>Title</th></tr>
};

  for $array_ref (@List) {
    my ($rfc_number,$status_value,$rfc_name) = rm_tr(@$array_ref);
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
    $filesize = 0 unless my_defined($filesize);
    $ret_val .= qq{
<tr align=left><td width=90><A HREF="RFCs/rfc$rfc_number.txt" target="_blank">RFC$rfc_number</A></td><td width=90> $status_value </td><td>$rfc_name</td></tr>
};
  }
  }
  $ret_val .= "</table>\n";
  return $ret_val;
}

sub process_gm {
  my $group_acronym_id = shift;
  my $ret_val = qq {
<h2>Goals and Milestones:</h2>

};
  my @List = db_select_multiple($dbh,"select description,expected_due_date,done,done_date from goals_milestones where group_acronym_id = $group_acronym_id order by expected_due_date,done_date");
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
  my $filename = "/a/www/www6s/wg-descriptions/${group_acronym}.desc.txt";
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

