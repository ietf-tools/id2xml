#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE';
use IETF_UTIL;
use IETF_DBUTIL;


init_database_mysql();

my $sqlStr = qq{
select gm.description,gm.expected_due_date,
a.acronym,a.acronym_id
from goals_milestones gm,groups_ietf g,acronym a
where gm.expected_due_date < current_date and
gm.done = "" and gm.group_acronym_id = g.group_acronym_id and
g.group_acronym_id = a.acronym_id and g.status_id = 1 and
g.group_type_id = 1
order by a.acronym,gm.expected_due_date
};
my $p_group_acronym_id = -1;
my $p_group_acronym = "";
my @List = db_select_multiple($sqlStr);
my $mail_body = "";
my $todate = get_current_date();
my $status_report = ""; 
my $wg_list = "";
my $num_sent = 0;
my $num_total = 0;
for $array_ref (@List) {
  my ($description,$expected_due_date,$group_acronym,$group_acronym_id) = rm_tr(@$array_ref);
  $group_acronym = uc($group_acronym);
  if ($p_group_acronym_id != $group_acronym_id) {
    if (my_defined($mail_body)) {
      unless (send_mail($mail_body,$p_group_acronym_id,$p_group_acronym)) {
          $status_report .= "Fail to send reminders to $p_group_acronym\n";
      } else {
          $num_sent++;
          $wg_list .= "$group_acronym, ";
      }
    }
    $num_total++;
    $p_group_acronym_id = $group_acronym_id;
    $p_group_acronym = $group_acronym;
    $mail_body = qq{
Dear $group_acronym Working Group Chair(s):

Below is a list of the $group_acronym Working Group milestones that are past due.  Please be reminded that changes to existing milestones or due dates require Area Director approval.  Therefore, please send comments, requests, or status reports regarding these milestones directly to your Area Directors.

To report that a milestone has been achieved, please send a message to iesg-secretary\@ietf.org with the name of the milestone and the completion date.  If you do not provide a completion date, then the completion date recorded will be the date that your message is received.

The IESG Secretariat
--------------------------------------------------------------------------------------

Past Due Milestones:

};
    
  }
  $expected_due_date =  convert_date($expected_due_date,2);
  $expected_due_date =  convert_date($expected_due_date,3);
  $mail_body .= "$expected_due_date  ";
  $mail_body .= indent_text2($description,8);
  $mail_body .= "\n";





}
unless (send_mail($mail_body,$p_group_acronym_id,$p_group_acronym)) {
    $status_report .= "Fail to send reminders to $p_group_acronym\n";
} else {
    $num_sent++;
    $wg_list .= "$group_acronym, ";
}
$wg_list = indent_text2($wg_list,10);

my $status_email = qq{"IETF Director" <exec-director\@ietf.org>, "Michael Lee" <mlee\@foretec.com>};
chop($wg_list);chop($wg_list);
open MAIL, "| /usr/exim/bin/exim exec-director\@ietf.org mlee\@foretec.com" or return 0;
print MAIL <<END_OF_MESSAGE;
To: $status_email
From: "WG Milestone Tracker" <iesg-secretary\@ietf.org>
Subject: Milestone Tracker status report

           STATUS REPORT -- BI-MONTHLY PAST DUE MILESTONES REMINDERS

$status_report
Reminders Sent Out Date: $todate

Reminders sent to: $wg_list

Result (<number of sent message / number of WG that has past due milestone) : $num_sent / $num_total

END OF REPORT
END_OF_MESSAGE

close MAIL;

exit;


sub send_mail {
  my ($mail_body,$group_acronym_id,$group_acronym) = @_;
  $mail_body .= "--------------------------------------------------------------------------------------\n";
  my $to_field = "";
  my $mail_heading = "";
  my @List = db_select_multiple("select person_or_org_tag from g_chairs where group_acronym_id = $group_acronym_id");
  for $array_ref2 (@List) {
    my ($person_or_org_tag) = @$array_ref2;
    my $email = get_email($person_or_org_tag);
    $to_field .= qq{"$group_acronym Chair" <$email>, };
    $mail_heading .= "$email ";
  }
  chop ($to_field);chop($to_field);
  my $cc_field = "";
  my $area_acronym_id = db_select("select area_acronym_id from area_group where group_acronym_id=$group_acronym_id");
  my @List2 = db_select_multiple("select person_or_org_tag from area_directors where area_acronym_id = $area_acronym_id");
  my $area_acronym = uc(rm_tr(db_select("select acronym from acronym where acronym_id = $area_acronym_id")));
  for $array_ref3 (@List2) {
    my ($person_or_org_tag) = @$array_ref3;
    my $email = get_email($person_or_org_tag);
    $cc_field .= qq{"$area_acronym ADs" <$email>, };
    $mail_heading .= "$email ";
  }
  $cc_field .= qq{"IETF Chair" <chair\@ietf.org>};
  $mail_heading .= "chair\@ietf.org";
#$to_field = qq{"Michael Lee" <mlee\@foretec.com>, "M Lee" <mlee\@foretec.com>};
#$cc_field = qq{"CC to M Lee" <homin1972@yahoo.com>};
#$mail_heading = "mlee\@foretec.com";
   #open MAIL, "| /usr/exim/bin/exim  $mail_heading" or return 0;
   #print MAIL <<END_OF_MESSAGE;
#To: $to_field 
#Cc: $cc_field 
#From: "WG Milestone Tracker" <iesg-secretary\@ietf.org>
#Subject: $group_acronym Mlestones past due
#
#$mail_body
#END_OF_MESSAGE
#
#  close MAIL;
}
