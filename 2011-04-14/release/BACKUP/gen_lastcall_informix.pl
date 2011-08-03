#!/usr/local/bin/perl -w

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

($db_mode,$CURRENT_DATE,$CONVERT_SEED) = init_database($MYSQL);

my ($id_document_tag,$intended_status,$filename,$area,$token_name,$token_email) = input_screen();
print qq{-------------------------
File name  : $filename
area       : $area
token name : $token_name
token email: $token_email

Continue [Y/N]:> };

chomp (my $cont = <STDIN>);
unless (uc($cont) eq "Y") {
   print "Good bye...\n";
   exit(1);
}

my $update_tag = 0;
if (check_exist($id_document_tag)) {
   print "This draft exists in current internal table\n";
   print "Do you want to update the existing record instead of creating new record? [Y/N] : ";
   chomp (my $ans = <STDIN>);
   if (uc($ans) eq "Y") {
      $update_tag = 1;
   } else {
      die "FATAL ERROR: Can't creat a new record\n";
   }
}

unless (open (OUTFILE,">${filename}.lastcall")) {
   die "FATAL ERROR: Can not create ${filename}.lastcall\n";
}
unless (open (OUTFILE2,">${filename}.ballot")) {
   die "FATAL ERROR: Can not create ${filename}.ballot\n";
}

my $lc_expiration_date = update_record($id_document_tag,$intended_status);
my ($lastcall_msg,$ballot_msg) = generate_email($id_document_tag,$intended_status,$lc_expiration_date);
print OUTFILE $lastcall_msg;
close (OUTFILE);
print OUTFILE2 $ballot_msg;
close (OUTFILE2);
system "/usr/informix/bin/format_lc ${filename}.lastcall";
system "/usr/informix/bin/format_lc ${filename}.ballot";
print "\n";
update_internal_db($update_tag,$id_document_tag,$area,$token_name,$token_email,$lc_expiration_date);
exit;

sub input_screen {
   print "Enter file name: ";
   chomp(my $filename = <STDIN>);
   my $id_document_tag = validate_filename($filename);
   unless ($id_document_tag) {
      die "FATAL ERROR: Record does not exist\n";
   }
   print "\nSet Intended Status value\n------------------------------\n";
   my $is_count = 0;
   my @List = db_select_multiple("select * from id_intended_status");
   for $array_ref (@List) {
      $is_count++;
      my ($id,$val) = @$array_ref;
	  print "${id}\t${val}\n";
   }
   print "\nSelect 1 ~ $is_count : ";
   chomp ($is_select = <STDIN>);
   unless (validate_intended_status($is_select,$is_count)) {
      die "FATAL ERROR: Invalid selection\n";
   }
   
   print "\nSet Area\n--------------\n";
   $sqlStr = qq { select a.acronym from acronym a, area_group c, internet_drafts i
   where i.id_document_tag = $id_document_tag and i.group_acronym_id = c.group_acronym_id and
   c.area_acronym_id = a.acronym_id
   };
   my $area = rm_tr(db_select($sqlStr));
   
   $sqlStr = "select a.acronym from acronym a, areas b where b.area_acronym_id = a.acronym_id order by 1";
   @List = db_select_multiple ($sqlStr);
   for $array_ref (@List) {
      my ($area_acronym) = @$array_ref;
	  print "$area_acronym\n";
   }
   print "\nSelect Area Acronym [$area] : ";
   chomp ($area_acronym_select = <STDIN>);
   if (my_defined($area_acronym_select)) {
      my $q_area_acronym_select = db_quote($area_acronym_select);
      my $val_count = db_select ("select count(*) from acronym where acronym = $q_area_acronym_select");
	  if ($val_count) {
	     $area = $area_acronym_select;
	  } else {
	     die "FATAL ERROR: Invalid Area Acronym\n";
	  }
   }
   print "\nArea Director\n------------------\n";
   my $q_area = db_quote($area);
   $sqlStr = qq{
   select p.firstname,p.lastname,p.person_or_org_tag from print_name p, area_directors a, acronym m
   where m.acronym = $q_area and
   m.acronym_id = a.area_acronym_id and
   a.person_or_org_tag = p.person_or_org_tag
   };
   my ($ad_fName,$ad_lName,$token_tag) = db_select($sqlStr);
   $ad_fName = rm_tr($ad_fName);
   $ad_lName = rm_tr($ad_lName);
   my $token_name;
   @List = db_select_multiple ($sqlStr);
   my $p_count = 0;
   for $array_ref (@List) {
      ($ad_fName,$ad_lName,$token_tag) = @$array_ref;
	  $p_count++;
      $ad_fName = rm_tr($ad_fName);
      $ad_lName = rm_tr($ad_lName);
	  $token_name = "$ad_fName $ad_lName";
	  print "Area Director is $token_name? [ENTER/Y/N] : ";
	  chomp (my $y_or_n = <STDIN>);
	  if (uc($y_or_n) eq "Y" or $y_or_n eq "") {
	     last;
	  } else {
	     $token_name = "";
	  }
   }
   unless (my_defined($token_name)) {
      die "FATAL ERROR: No other ADs available\n";
   }
   my $token_email = rm_tr(db_select("select email_address from email_addresses where person_or_org_tag = $token_tag"));
   print "Enter Email Address [$token_email] : ";
   chomp (my $email_select = <STDIN>);
   if (my_defined($email_select)) {
      $token_email = $email_select;
   }
   return ($id_document_tag,$is_select,$filename,$area,$token_name,$token_email);
}

sub validate_filename {
   my $filename = shift;
   $filename = db_quote($filename);
   my $id_document_tag = db_select("select id_document_tag from internet_drafts where filename = $filename");
   if (defined($id_document_tag)) {
      return $id_document_tag;
   } else {
      return 0;
   }
}

sub validate_intended_status {
   my $is_select = shift;
   my $is_count = shift;
   $_ = $is_select;
   if (/\D/ or $is_select > $is_count) {
      return 0;
   }
   return 1;
}

sub update_record {
   my ($id_document_tag,$intended_status) = @_;
   my $lc_expiration_date = get_current_date(0,14);
   my $q_lc_exp_date = db_quote($lc_expiration_date);
   my $sqlStr = qq{
		UPDATE internet_drafts
			SET	lc_sent_date 		= 	TODAY,
				intended_status_id 	=	$intended_status,
				lc_expiration_date  =   $q_lc_exp_date,
				last_modified_date 	= 	TODAY
			WHERE id_document_tag 	= 	$id_document_tag
   };
   print "FATAL ERROR:\n$sqlStr" unless db_update($sqlStr);
   return $lc_expiration_date;
}

sub update_internal_db {
  my ($update_tag,$id_document_tag,$area_acronym,$token_name,$token_email,$status_date) = @_;
  ($area_acronym,$token_name,$token_email,$status_date) = db_quote($area_acronym,$token_name,$token_email,$status_date);
  my $sqlStr;
  my $group_flag = 3;
  my $mark_by = 1;
  my $assigned_to = db_quote("Unassigned");
  if ($update_tag) {
     $sqlStr = qq {
	 update id_internal
	 set group_flag = $group_flag,
	     area_acronym = $area_acronym,
		 token_name = $token_name,
		 email_display = $token_name,
		 token_email = $token_email,
		 status_date = $status_date
	 where id_document_tag = $id_document_tag
	 };
  } else {
     my $rfc_flag = 0;
	 my $primary_flag = 1;
	 my $ballot_id = db_select("select max(ballot_id) from id_internal");
	 $ballot_id++;
	 $agenda = 0;
     $sqlStr = qq {
   insert into id_internal 
   (ballot_id,primary_flag,group_flag,id_document_tag,status_date,token_name,token_email,email_display,agenda,rfc_flag,area_acronym,mark_by,assigned_to,ref_history,event_date,job_owner)
   values 
   ($ballot_id,$primary_flag,$group_flag,$id_document_tag,$status_date,$token_name,$token_email,$token_name,$agenda,$rfc_flag,$area_acronym,$mark_by,$assigned_to,999999,TODAY,2)
	 };
  }
  print "FATAL ERROR:\n$sqlStr" unless (db_update($sqlStr));
}

sub generate_email {
   my ($id_document_tag,$intended_status,$lc_expiration_date) = @_;
   my $sqlStr = qq {
select g.email_address,i.id_document_name,i.filename,i.revision, a.name, i.group_acronym_id
from groups_ietf g, internet_drafts i, acronym a 
where i.id_document_tag = $id_document_tag and i.group_acronym_id = g.group_acronym_id 
and g.group_acronym_id = a.acronym_id   
};
   my ($email_address,$id_document_name,$filename,$revision,$display_group, $group_acronym_id) = db_select($sqlStr);
   $id_document_name = rm_tr($id_document_name);
   $filename = rm_tr($filename);
   $display_group = rm_tr($display_group);
   my $id_status_value = rm_tr(db_select("select status_value from id_intended_status where intended_status_id = $intended_status"));
   my $wgMail = "";
   if ($display_group eq "none") {
      $wgMail = "This has been reviewed in the IETF but is not the product of an IETF Working Group.";
   }
   
   my $email_msg = qq|
To: IETF-Announce :;
Dcc: all-ietf
Cc: $email_address
From: The IESG <iesg-secretary\@ietf.org>
SUBJECT: Last Call: $id_document_name to $id_status_value
Reply-to: iesg\@ietf.org
-------------

The IESG has received a request $display_group to consider $id_document_name <${filename}-${revision}.txt> as a $id_status_value.  $wgMail

The IESG plans to make a decision in the next few weeks, and solicits
final comments on this action.  Please send any comments to the 
iesg\@ietf.org or ietf\@ietf.org mailing lists by $lc_expiration_date.

Files can be obtained via http://www.ietf.org/internet-drafts/${filename}-${revision}.txt
|;

   my $subject = "Protocol Action";
   $sqlStr = qq {
   	    SELECT distinct firstname, lastname
		  FROM groups_ietf,
		  	   area_directors A,
			   area_directors B,
			   areas,
			   print_name
		 WHERE groups_ietf.group_acronym_id = $group_acronym_id
		   AND groups_ietf.area_director_id = A.id
		   AND A.area_acronym_id 			= B.area_acronym_id
		   AND B.person_or_org_tag 			= print_name.person_or_org_tag
   };
#   die "$sqlStr\n";
   my @List2 = db_select_multiple($sqlStr);
   $Directors = "";
   my $count = 0;
   for $array_ref2 (@List2) {
      $count++;
	  if ($count > 1) {
	     $Directors .= " and ";
	  }
      my ($fName,$lName) = @$array_ref2;
	  $fName = rm_tr($fName);
	  $lName = rm_tr($lName);
	  $Directors .= "$fName $lName";
   }
   if ($intended_status == 3 or $intended_status == 5) {
      $subject = "Document Action";
   }
   my $Working_Group = ".";
   $sqlStr = qq {select count(*) from internet_drafts i, groups_ietf g
   where i.id_document_tag = $id_document_tag
   and i.group_acronym_id = g.group_acronym_id
   and g.group_type_id = 4
   };
   my $temp_cnt = db_select($sqlStr);
   unless ($temp_cnt) {
      $Working_Group = " Working Group.";
   }
   my $ballot_msg = qq|
To: Internet Engineering Steering Group <iesg\@ietf.org>
From: IESG Secretary <iesg-secretary\@ietf.org>
Reply-To: IESG Secretary <iesg-secretary\@ietf.org>
Subject: Evaluation: $filename - $id_document_name to $id_status_value
--------

Last Call to expire on: $lc_expiration_date

	Please return the full line with your position.

                    Yes    No-Objection  Discuss *  Abstain  


Harald Alvestrand   [   ]     [   ]       [   ]      [   ] 
Scott Bradner       [   ]     [   ]       [   ]      [   ] 
Randy Bush          [   ]     [   ]       [   ]      [   ] 
Patrik Faltstrom    [   ]     [   ]       [   ]      [   ] 
Bill Fenner         [   ]     [   ]       [   ]      [   ] 
Ned Freed           [   ]     [   ]       [   ]      [   ] 
Marcus Leech        [   ]     [   ]       [   ]      [   ] 
Allison Mankin      [   ]     [   ]       [   ]      [   ] 
April Marine        [   ]     [   ]       [   ]      [   ] 
Thomas Narten       [   ]     [   ]       [   ]      [   ] 
Erik Nordmark       [   ]     [   ]       [   ]      [   ] 
Jeff Schiller       [   ]     [   ]       [   ]      [   ] 
Bert Wijnen         [   ]     [   ]       [   ]      [   ]
 
 2/3 (9) Yes or No-Objection opinions needed to pass. 
 
 * Indicate reason if 'Discuss'.
 
^L
To: IETF-Announce:;
Dcc: *******
Cc: RFC Editor <rfc-editor\@isi.edu>,
 Internet Architecture Board <iab\@isi.edu>, $email_address
From: The IESG <iesg-secretary\@ietf.org>
Subject: $subject: $id_document_name to $id_status_value
-------------


The IESG has approved the Internet-Draft '$id_document_name' <${filename}-${revision}.txt> as a $id_status_value.
This document is the product of the $display_group$Working_Group
The IESG contact persons are $Directors
 
 
Technical Summary
 
 (What does this protocol do and why does the community need it)
 
Working Group Summary
 
 (Was there any significant dissent? Was the choice obvious?)
 
Protocol Quality
 
 (Who has reviewed the spec for the IESG? Are there implementations?)
|;
   return $email_msg, $ballot_msg;
}

sub check_exist {
   my $id_document_tag = shift;
   return db_select("select count(*) from id_internal where id_document_tag = $id_document_tag");
}




