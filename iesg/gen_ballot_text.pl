#!/usr/bin/perl
##########################################################################
# Copyright © 2004 and 2003, Foretec Seminars, Inc.
##########################################################################


use lib '/home/henrik/src/db/legacy/iesg/';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

init_database("ietf");

my $ballot_id = $ARGV[0] or die "USAGE: gen_ballot_text.pl <ballot id>\n";
my $test_mode = (defined($ARGV[1]))?$ARGV[1]:"";
$ENV{"DBNAME"} = "develdb" if ($test_mode == 1);
$tracker_url = ($test_mode eq "public")?"public/pidtracker":"cgi-bin/idtracker";
my $ex_count = db_select("select count(ballot_id) from ballot_info where ballot_id=$ballot_id");
exit unless $ex_count;
my $filename_set = get_filename_set($ballot_id,3);
my ($id_document_tag,$rfc_flag) = db_select("select id_document_tag,rfc_flag from id_internal where ballot_id = $ballot_id and primary_flag = 1");
my ($filename,$id_document_name,$revision,$lc_expire_date,$intended_status,$group_acronym_id) = rm_tr(db_select("select filename,id_document_name,revision,lc_expiration_date,intended_status_id,group_acronym_id from internet_drafts where id_document_tag = $id_document_tag"));
my $id_status_value = rm_tr(db_select("select status_value from id_intended_status where intended_status_id = $intended_status"));
if ($rfc_flag) {
  ($id_document_name,$lc_expire_date,$group_acronym,$intended_status_id) = db_select("select rfc_name,lc_expiration_date,group_acronym,intended_status_id from rfcs where rfc_number=$id_document_tag");
  $filename = "rfc$id_document_tag.txt";
  $group_acronym_id = db_select("select acronym_id from acronym where acronym='$group_acronym'");
  $id_status_value = db_select("select status_value from rfc_intend_status where intended_status_id=$intended_status_id");
}
my $email_address = rm_tr(db_select("select email_address from groups_ietf where group_acronym_id = $group_acronym_id"));
$email_address = "exec-director\@ietf.org" unless (my_defined($email_address));
my $subject_line = "Evaluation: $filename_set";

$subject_line = indent_text2($subject_line,9);
my $filename_set2 = get_filename_set($ballot_id,2);
my $url_part = indent_text("Evaluation for $filename_set2 can be found at https://merlot.tools.ietf.org/$tracker_url.cgi?command=view_id&dTag=$id_document_tag&rfc_flag=$rfc_flag",0);
my $lc_exp_line = "";
$lc_exp_line = "Last Call to expire on: $lc_expire_date" unless ($lc_expire_date eq "0000-00-00");
my $ballot_txt = qq {To: Internet Engineering Steering Group <iesg\@ietf.org>
From: IESG Secretary <iesg-secretary\@ietf.org>
Reply-To: IESG Secretary <iesg-secretary\@ietf.org>
Subject: $subject_line
--------

$url_part

$lc_exp_line

        Please return the full line with your position.

                      Yes  No-Objection  Discuss  Abstain
};
my $sqlStr = qq{
select iesg_login.id,first_name,last_name,yes_col,no_col,abstain,discuss,recuse
from iesg_login left outer join ballots on (iesg_login.id = ballots.ad_id and ballots.ballot_id = $ballot_id)
where user_level = 1 and iesg_login.id > 1 order by last_name
};
   my @List = db_select_multiple($sqlStr);
   my $blank_vote = "[   ]";
   my $filled_vote = "[ X ]";
   my $cleared_vote = "[ . ]";
   for $array_ref (@List) {
      my ($id,$first_name,$last_name,$yes_col,$no_col,$abstain,$discuss,$recuse) = rm_tr(@$array_ref);
        #$filled_vote = "[ ..]" if ($d_count);
        my $d_count = db_select("select count(ballot_id) from ballots where ballot_id = $ballot_id and ad_id = $id and discuss = -1");
        my $yes_col_val = $blank_vote;
        my $no_col_val = $blank_vote;
        my $abstain_val = $blank_vote;
        my $recuse_val = $blank_vote;
        my $discuss_val = $blank_vote;
        $yes_col_val = $filled_vote if ($yes_col);
        $no_col_val = $filled_vote if ($no_col);
        $abstain_val = $filled_vote if ($abstain);
        $abstain_val = "[ R ]" if ($recuse);
        $filled_vote = "[ X ]";
        $discuss_val = $filled_vote if ($discuss==1);
        $discuss_val = $cleared_vote if ($d_count);
        my $name = "$first_name $last_name";
        my $len = length($name);
        my $num_space = 20 - $len;
        for ($loop=0;$loop<$num_space;$loop++) { $name .= " ";}
        $ballot_txt .= qq {$name $yes_col_val     $no_col_val     $discuss_val     $abstain_val
};
    }


$sqlStr = qq{
select iesg_login.id,first_name,last_name,yes_col,no_col,discuss,abstain,recuse
from iesg_login,ballots
where user_level = 2 and 
iesg_login.id = ballots.ad_id and ballots.ballot_id = $ballot_id
 order by last_name
};
   my @List_ex = db_select_multiple($sqlStr);
   $ballot_txt .= "\n\n" if ($#List_ex > -1);
   $blank_vote = "[   ]";
   $filled_vote = "[ X ]";
   for $array_ref (@List_ex) {
      my ($id,$first_name,$last_name,$yes_col,$no_col,$discuss,$abstain,$recuse) = rm_tr(@$array_ref);
        #my $d_count = db_select("select count(ballot_id) from ballots_discuss where ballot_id = $ballot_id and ad_id = $id and discuss_text is not NULL");
        #$filled_vote = "[ ..]" if ($d_count);
        my $yes_col_val = $blank_vote;
        my $no_col_val = $blank_vote;
        my $abstain_val = $blank_vote;
        my $recuse_val = $blank_vote;
        my $discuss_val = $blank_vote;
        $yes_col_val = $filled_vote if ($yes_col);
        $no_col_val = $filled_vote if ($no_col);
        $abstain_val = $filled_vote if ($abstain);
        $abstain_val = "[ R ]" if ($recuse);
        $filled_vote = "[ X ]";
        $discuss_val = $filled_vote if ($discuss);
        $discuss_val = $cleared_vote if ($discuss and ($yes_col or $no_col or $abstain));
        my $name = "$first_name $last_name";
        my $len = length($name);
        my $num_space = 20 - $len;
        for ($loop=0;$loop<$num_space;$loop++) { $name .= " ";}
        $ballot_txt .= qq {$name $yes_col_val     $no_col_val     $discuss_val     $abstain_val
};
    }
                                                                                                   




   $sqlStr = qq{select first_name,last_name,discuss_text,comment_text,a.id,discuss_date,comment_date
from iesg_login a left outer join ballots_discuss b on
(a.id = b.ad_id and b.ballot_id=$ballot_id)
left outer join ballots_comment c on (a.id = c.ad_id and c.ballot_id=$ballot_id)
where user_level = 1
order by last_name
};
   my $discuss_str = "";
   my @discusses_comments = rm_tr(db_select_multiple($sqlStr));
   for $array_ref (@discusses_comments) {
     my ($first_name,$last_name,$discuss,$comment,$ad_id,$discuss_date,$comment_date) = @$array_ref;
     my $discuss_val = db_select("select discuss from ballots where ad_id=$ad_id and ballot_id=$ballot_id");
     $discuss_val = 0 unless my_defined($discuss_val);
     $comment = "" unless my_defined($comment);
     $discuss = "" unless my_defined($discuss);
     if (length($comment) > 1 or (length($discuss) > 1 and $discuss_val==1)) {
       my $ad_name = "$first_name $last_name";
       $discuss_str .= "$ad_name:\n";
       if (length($discuss) > 1 and $discuss_val == 1) {
         $discuss = format_comment_text($discuss);
         $discuss_str .= qq{
Discuss [$discuss_date]:
$discuss

};
       }
       if (length($comment) > 1) {
         $comment = format_comment_text($comment);
         $discuss_str .= qq{
Comment [$comment_date]:
$comment

};
       }
     }
   }
   $discuss_str .= "\n";

my $email_body = db_select("select approval_text from ballot_info where ballot_id = $ballot_id"); 
$email_body =~ s/\r//g;
#$email_body = indent_text2($email_body,0);
$ballot_txt .= qq{
"Yes" or "No-Objection" positions from 2/3 of non-recused ADs, 
with no "Discuss" positions, are needed for approval.

DISCUSSES AND COMMENTS:
======================
$discuss_str

^L 
---- following is a DRAFT of message to be sent AFTER approval ---
$email_body
};




  my $ballot_writeup = rm_tr(db_select("select ballot_writeup from ballot_info where ballot_id = $ballot_id"));
#  $ballot_writeup = indent_text($ballot_writeup,0);
  $ballot_txt .= "\n$ballot_writeup\n" if (my_defined($ballot_writeup));
  $ballot_txt .= "\n\n\n\n";
 print $ballot_txt;

exit;


