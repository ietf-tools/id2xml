#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

$TESTDB = 0;
$INFORMIX = 1;
$MYSQL = 2;

($db_mode,$CURRENT_DATE,$CONVERT_SEED,$is_null) = init_database($MYSQL);

my $ballot_id = $ARGV[0] or die "USAGE: gen_ballot_text.pl <ballot id>\n";
my $id_document_tag = db_select("select id_document_tag from id_internal where ballot_id = $ballot_id and primary_flag = 1");
my ($filename,$id_document_name,$lc_expire_date,$intended_status,$group_acronym_id) = rm_tr(db_select("select filename,id_document_name,lc_expiration_date,intended_status_id,group_acronym_id from internet_drafts where id_document_tag = $id_document_tag"));
my $id_status_value = rm_tr(db_select("select status_value from id_intended_status where intended_status_id = $intended_status"));
my $display_group = rm_tr(db_select("select name from acronym where acronym_id = $group_acronym_id"));
my $email_address = rm_tr(db_select("select email_address from groups_ietf where group_acronym_id = $group_acronym_id"));
$email_address = "scoya\@ietf.org" unless (my_defined($email_address));
my $is_are = " is";
   my $subject = "Protocol Action";
   $sqlStr = qq {
            SELECT distinct first_name, last_name
                  FROM groups_ietf,
                           area_directors A,
                           area_directors B,
                           areas,
                           person_or_org_info P
                 WHERE groups_ietf.group_acronym_id = $group_acronym_id
                   AND groups_ietf.area_director_id = A.id
                   AND A.area_acronym_id                        = B.area_acronym_id
                   AND B.person_or_org_tag                      = P.person_or_org_tag
   };
   my @List2 = db_select_multiple($sqlStr);
   $Directors = "";
   my $count = 0;
   for $array_ref2 (@List2) {
      $count++;
          if ($count > 1) {
             $Directors .= " and ";
             $is_are = "s are"
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



my $ballot_txt = qq {
To: Internet Engineering Steering Group <iesg\@ietf.org>
From: IESG Secretary <iesg-secretary\@ietf.org>
Reply-To: IESG Scretary <iesg-secretary\@ietf.org>
Subject: Evaluation: $filename -
        $id_document_name
--------

Last Call to expire on: $lc_expire_date

        Please return the full line with your position.

                      Yes  No-Objection  Discuss  Abstain
};
   my $sqlStr = qq {
select id,first_name,last_name,yes_col,no_col,abstain
from iesg_login left outer join ballots on (iesg_login.id = ballots.ad_id and ballots.ballot_id = $ballot_id)
where user_level = 1 and id > 1 order by last_name
};
   my @List = db_select_multiple($sqlStr);
   my $blank_vote = "[   ]";
   my $filled_vote = "[ X ]";
   for $array_ref (@List) {
      my ($id,$first_name,$last_name,$yes_col,$no_col,$abstain) = rm_tr(@$array_ref);
        my $yes_col_val = $blank_vote;
        my $no_col_val = $blank_vote;
        my $abstain_val = $blank_vote;
        my $discuss_val = $blank_vote;
        $yes_col_val = $filled_vote if ($yes_col);
        $no_col_val = $filled_vote if ($no_col);
        $abstain_val = $filled_vote if ($abstain);
        my $d_count = db_select("select count(ballot_id) from ballots_discuss where ballot_id = $ballot_id and ad_id = $id and active = 1 and discuss_text is not NULL");
        $discuss_val = $filled_vote if ($d_count);
        my $name = "$first_name $last_name";
        my $len = length($name);
        my $num_space = 20 - $len;
        for ($loop=0;$loop<$num_space;$loop++) { $name .= " ";}
        $ballot_txt .= qq {$name $yes_col_val     $no_col_val     $abstain_val     $discuss_val
};
    }
$subject = "$subject: $id_document_name to $id_status_value";
$subject = indent_text2($subject,5);
my $email_body = qq {The IESG has approved the Internet-Draft '$id_document_name' <${filename}-${revision}.txt> as a $id_status_value.  This document is the product of the $display_group$Working_Group The IESG contact person${is_are} $Directors
};
$email_body = indent_text2($email_body,0);
$ballot_txt .= qq {
2/3 (9) Yes or No-Objection opinions needed to pass.

^L 
To: IETF-Announce:; 
Dcc: *******
Cc: RFC Editor <rfc-editor\@isi.edu>,
 Internet Architecture Board <iab\@iab.org>, $email_address
From: The IESG <iesg-secretary\@ietf.org>
Subject: $subject
-------------

$email_body
};




  my ($tech_summary,$wg_summary,$pq,$other_comment) = rm_tr(db_select("select tech_summary,wg_summary,pq,other_comment from ballot_info where ballot_id = $ballot_id"));
  $tech_summary = indent_text($tech_summary,0);
  $ballot_txt .= "\nTechnical Summary\n\n$tech_summary\n" if (my_defined($tech_summary));
  $ballot_txt .= "\nWorking Group Summary\n\n$wg_summary\n" if (my_defined($wg_summary));
  $ballot_txt .= "\nProtocol Quality\n\n$pq\n" if (my_defined($pq));
  $ballot_txt .= "\nAdditional Comment\n\n$other_comment\n" if (my_defined($other_comment));

 print $ballot_txt;

exit;

