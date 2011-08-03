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

    wginfo wgacronym <switches>

 -id		Show the current internet-drafts
 -rfc 		Show the rfcs produced by the group
 -gm		Show the current goals and milestones
 -charter	Generate a text charter for the WG.
		(includes -description, -gm)
 -description	Show the working group description

};

unless (defined($ARGV[0])) {
   die $usage_str;
}
my $argc = 1;
my $arg_id = 0;
my $arg_rfc = 0;
my $arg_gm = 0;
my $arg_charter = 0;
my $arg_all = 0;
my $arg_mailarchive = 0;
my $arg_meetings = 0;
my $arg_description = 0;
while (defined($ARGV[$argc])) {
  my $arg = $ARGV[$argc];
  $arg_id = 1 if ($arg eq "-id"); 
  $arg_rfc = 1 if ($arg eq "-rfc");
  $arg_gm = 1 if ($arg eq "-gm");
  $arg_charter = 1 if ($arg eq "-charter");
  $arg_all = 1 if ($arg eq "-all");
  $arg_description = 1 if ($arg eq "-description");
  $argc++;
}
my $g_acronym= db_quote($ARGV[0]);
my ($group_acronym_id,$group_name,$group_acronym) = rm_tr(db_select("select acronym_id,name,acronym from acronym where acronym=$g_acronym"));
die "FATAL ERROR:Unknown Group Acronym\n\n" unless ($group_acronym_id);

print wg_header($group_acronym_id,$group_name,$group_acronym);
print process_description($group_acronym) if ($arg_description);
if ($arg_charter) {
   print process_description($group_acronym);
   print process_gm($group_acronym_id);
}
print process_description($group_acronym) if ($arg_description);
print process_gm($group_acronym_id) if ($arg_gm);
print process_id($group_acronym_id) if ($arg_id);
print process_rfc($group_acronym) if ($arg_rfc);

exit;


sub wg_header {
  my ($group_acronym_id,$group_name,$group_acronym) = @_;
  my ($group_status_id,$last_modified_date,$group_type_id,$ad_id,$email_address,$email_subscribe,$email_keyword,$email_archive) = rm_tr(db_select("select status_id,last_modified_date,group_type_id,area_director_id,email_address,email_subscribe,email_keyword,email_archive from groups_ietf where group_acronym_id = $group_acronym_id"));
  my $header = "$group_name ($group_acronym)";
  my $dotted_line = "";
  my $str_len = length($header);
  for ($loop=0;$loop<$str_len;$loop++) {
    $dotted_line .= "-";
  }
  my $ret_val = qq{
$header
$dotted_line

 Charter
 Last Modified: $last_modified_date

};
  my $status_value = rm_tr(db_select("select status_value from g_status where status_id = $group_status_id"));
  my $type_value = rm_tr(db_select("select group_type from g_type where group_type_id = $group_type_id"));
  if ($type_value eq "WG") {
    $status_value .= " Working Group";
  } elsif ($type_value eq "PWG") {
    $status_value .= " Proposed Working Group";
  } else {
    $status_value .= " $type_value";
  }
  $ret_val .= qq{ Current Status: $status_value

};
  ####### Group Chairs #########
  my $chairs_str = "";
  my @List = db_select_multiple("select person_or_org_tag from g_chairs where group_acronym_id = $group_acronym_id");
  for $array_ref (@List) {
    my ($chair_tag) = @$array_ref;
    my $chair_name = get_name($chair_tag);
    my $chair_email = get_email($chair_tag);
    $chairs_str .= "     $chair_name  <$chair_email>\n";
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
    $ad_str .= "     $ad_name  <$ad_email>\n";
  }
  ##### Area Advisor #########
  $ad_adv_tag = db_select("select person_or_org_tag from area_directors where id=$ad_id");
  my $ad_adv_name = get_name($ad_adv_tag);
  my $ad_adv_email = get_email($ad_adv_tag);
  my $ad_adv_str = "     $ad_adv_name  <$ad_adv_email>\n";
  $ret_val .= qq{ Chair(s):
$chairs_str
 $area_name Director(s):
$ad_str
 $area_name Advisor:
$ad_adv_str
};
  ###### Technical Advisors ######
  @List = db_select_multiple("select person_or_org_tag from g_tech_advisors where group_acronym_id = $group_acronym_id");
  if ($#List > -1) {
    $ret_val .= " Technical Advisor(s):\n";
    for $array_ref (@List) {
      my ($tech_tag) = @$array_ref;
      my $tech_name = get_name($tech_tag);
      my $tech_email = get_email($tech_tag);
      $ret_val .= "     $tech_name  <$tech_email>\n";
    }
    $ret_val .= "\n";
  }
  ###### Group Editors ########
  @List = db_select_multiple("select person_or_org_tag from g_editors where group_acronym_id = $group_acronym_id");
  if ($#List > -1) {
    $ret_val .= " Editor(s):\n";
    for $array_ref (@List) {
      my ($editor_tag) = @$array_ref;
      my $editor_name = get_name($editor_tag);
      my $editor_email = get_email($editor_tag);
      $ret_val .= "     $editor_name  <$editor_email>\n";
    }
    $ret_val .= "\n";
  }
  ##### Mail List ############
  $ret_val .= qq { Mailing Lists: 
     General Discussion:$email_address
     To Subscribe:      $email_subscribe
};
  if (my_defined($email_keyword)) {
    $ret_val .= "         In Body:       $email_keyword\n";
  }
  $ret_val .= "     Archive:           $email_archive\n";
  
  return $ret_val;
}


sub process_id {
  my $group_acronym_id = shift;
  my $ret_val = "";
  my @List = db_select_multiple("select id_document_name,filename,revision,start_date,revision_date from internet_drafts where group_acronym_id = $group_acronym_id and status_id = 1 and filename <> 'rfc%' order by start_date");
  if ($#List < 0) {
    $ret_val = qq {
 Internet-Drafts:

  No Current Internet-Drafts.

};
  } else {
  $ret_val = qq {
 Internet-Drafts:

Posted Revised         I-D Title   <Filename>
------ ------- --------------------------------------------
};
  for $array_ref (@List) {
    my ($id_document_name,$filename,$revision,$start_date,$revision_date) = rm_tr(@$array_ref);
    $start_date = convert_date($start_date,2);
    $start_date = convert_date($start_date,3);
    $revision_date = convert_date($revision_date,2);
    $revision_date = convert_date($revision_date,3);
    $id_document_name = indent_text($id_document_name,16);
    $ret_val .= "$start_date $revision_date   <${filename}-${revision}.txt>\n$id_document_name\n\n";
  } 
  }
  chop ($ret_val);
  return $ret_val;

}

sub process_rfc {
  my $group_acronym = shift;
  $group_acronym = db_quote($group_acronym);
  my @List = db_select_multiple("select rfc_number,status_value,rfc_name,rfc_published_date from rfcs,rfc_status where group_acronym = $group_acronym and rfcs.status_id = rfc_status.status_id order by rfc_published_date");
  my $ret_val = "";
  if ($#List < 0) {
     $ret_val = qq{
 Request For Comments:

  None to date.

}; 
  } else {
   $ret_val = qq {
 Request For Comments:

  RFC   Stat Published     Title
------- -- ----------- ------------------------------------
};
  for $array_ref (@List) {
    my ($rfc_number,$status_value,$rfc_name,$rfc_published_date) = rm_tr(@$array_ref);
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
    $ret_val .= "RFC${rfc_number}${status_value}  $rfc_published_date    $rfc_name\n\n";
  }
  }
  chop($ret_val);
  return $ret_val;
}

sub process_gm {
  my $group_acronym_id = shift;
  my $ret_val = qq {
 Goals and Milestones:

};
  my @List = db_select_multiple("select description,expected_due_date,done,done_date from goals_milestones where group_acronym_id = $group_acronym_id order by expected_due_date,done_date");
  for $array_ref (@List) {
    my ($description,$expected_due_date,$done) = rm_tr(@$array_ref);
    $expected_due_date = convert_date($expected_due_date,2);
    $expected_due_date = convert_date($expected_due_date,3);
    $description = indent_text2($description,16);
    if ($done =~ /Yes|YES|yes|Done|DONE|done/) {
      $ret_val .= "   Done         $description\n\n";
    }
    else {
      $ret_val .= "   $expected_due_date       $description\n\n";
    }
  }
  return $ret_val;
}

sub process_description {
  my $group_acronym = shift;
  my $ret_val = qq{
Description of Working Group:

};
  my $filename = "/export/home/ietf/WG_DESCRIPTIONS/${group_acronym}.desc.txt";
  unless (open(INFILE,$filename)) {
    $ret_val .= "No description available\n\n";
  } else {
    while (<INFILE>) {
      $ret_val .= $_;
    }    
    close (INFILE)
  }

  return $ret_val;

}


