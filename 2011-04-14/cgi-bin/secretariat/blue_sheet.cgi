#!/usr/bin/perl
##########################################################################
# Copyright © 2003, Foretec Seminars, Inc.
##########################################################################

use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

$local_dir="/a/www/ietf-datatracker/documents";
init_database("ietf");
$meeting_num=db_select("select max(meeting_num) from meetings");
open OUT,">$local_dir/blue_sheet.rtf";

my $sqlStr = qq{select acronym,name,group_type,email_address
from acronym a, groups_ietf b, g_type c
where a.acronym_id = b.group_acronym_id 
and b.meeting_scheduled = 'YES'
and b.group_type_id = c.group_type_id
order by acronym
};

#if ($ARGV[0] ne "-all") {
#  $sqlStr = qq{select acronym,name,group_type,email_address
#from acronym a, groups_ietf b, g_type c
#where a.acronym_id = b.group_acronym_id
#and b.group_type_id = c.group_type_id
#and a.acronym = '$ARGV[0]'
#};
#}

my @List = db_select_multiple($sqlStr);
die "ERROR: INVALID WG ACRONYM\\n" if ($#List < 0);

print OUT qq|{\\rtf1\\ansi\\ansicpg1252\\uc1 \\deff0\\deflang1033\\deflangfe1033
 {\\fonttbl{\\f0\\froman\\fcharset0\\fprq2{\\*\\panose 02020603050405020304}Times New Roman;}}
 {\\colortbl;\\red0\\green0\\blue0;\\red0\\green0\\blue255;\\red0\\green255\\blue255;\\red0\\green255\\blue0;
\\red255\\green0\\blue255;\\red255\\green0\\blue0;\\red255\\green255\\blue0;\\red255\\green255\\blue255;
\\red0\\green0\\blue128;\\red0\\green128\\blue128;\\red0\\green128\\blue0;\\red128\\green0\\blue128;
\\red128\\green0\\blue0;\\red128\\green128\\blue0;\\red128\\green128\\blue128;
\\red192\\green192\\blue192;}
 \\widowctrl\\ftnbj\\aenddoc\\hyphcaps0\\formshade\\viewkind1\\viewscale100\\pgbrdrhead\\pgbrdrfoot
 \\fet0\\sectd \\pgnrestart\\linex0\\endnhere\\titlepg\\sectdefaultcl
|;


for $array_ref (@List) {
  my ($group_acronym,$group_name,$group_type,$email_address) = rm_tr(@$array_ref);
  print OUT qq| {\\header \\pard\\plain \\s15\\qr\\nowidctlpar\\widctlpar\\tqc\\tx4320\\tqr\\tx8640\\adjustright \\fs20\\cgrid
 { Meeting # $meeting_num  $group_acronym ($group_type) \\par }
 \\pard \\s15\\nowidctlpar\\widctlpar\\tqc\\tx4320\\tqr\\tx8640\\adjustright
 {\\b\\fs24 Mailing List: $email_address 
 \\par
 \\par \\tab The NOTE WELL statement included in your registration packet applies to this meeting.
 \\par
 \\par                               NAME                                                  EMAIL ADDRESS
 \\par \\tab
 \\par }}
 {\\footer \\pard\\plain \\s16\\qc\\nowidctlpar\\widctlpar\\tqc\\tx4320\\tqr\\tx8640\\adjustright \\fs20\\cgrid {\\cs17 Page }
 {\\field{\\*\\fldinst {\\cs17  PAGE }}}
 { \\par }}
  {\\headerf \\pard\\plain \\s15\\qr\\nowidctlpar\\widctlpar\\tqc\\tx4320\\tqr\\tx8640\\adjustright \\fs20\\cgrid
  {\\b\\fs24 Meeting # $meeting_num $group_acronym ($group_type) \\par }}
 {\\footerf \\pard\\plain \\s16\\qc\\nowidctlpar\\widctlpar\\tqc\\tx4320\\tqr\\tx8640\\adjustright \\fs20\\cgrid
  {Page 1 \\par }}
  \\pard\\plain \\qc\\nowidctlpar\\widctlpar\\adjustright \\fs20\\cgrid
  {\\b\\fs32 $meeting_num IETF Working Group Roster \\par }
  \\pard \\nowidctlpar\\widctlpar\\adjustright
  {\\fs28 \\par Working Group Session: $group_name \\par \\par }
{\\b \\fs24 Mailing List: $email_address                    Actual Start Time: __________	 \\par \\par Chairperson:_______________________________     Actual End Time: __________ \\par \\par }
 {\\tab \\tab	   }
{\\par \\tab The NOTE WELL statement included in your registration packet applies to this meeting. \\par \\par
\\b NAME\\tab \\tab \\tab \\tab \\tab EMAIL ADDRESS \\par }
  \\pard \\fi-90\\li90\\nowidctlpar\\widctlpar\\adjustright
 {\\fs16
|;
  for ($loop=1;$loop<130;$loop++) {
print OUT qq|

 \\par $loop._________________________________________________ \\tab _____________________________________________________
 \\par
|;
}
  print OUT qq|
 }
 \\pard \\nowidctlpar\\widctlpar\\adjustright
 {\\fs16 \\sect }
 \\sectd \\pgnrestart\\linex0\\endnhere\\titlepg\\sectdefaultcl
|;

}


print OUT " } \n";
close OUT;
#chdir $local_dir;
#open FTPODIN,"| /usr/bin/ftp -n" or return "Can't execute ftp\n\n";
#print FTPODIN <<END_OF_FTPODIN
#open odin
#user ietfadm h0t3l;cal
#cd $remote_dir
#put blue_sheet.rtf 
#quit
#
#END_OF_FTPODIN
#;
#close FTPODIN;
print qq{Content-type: text/html

<HTML>
<HEAD><TITLE>BLUE SHEET</TITLE></HEAD>
<BODY>
<a href="https://datatracker.ietf.org/documents/blue_sheet.rtf">BLUE SHEET</a>
</BODY>
</HTML>
};

exit;

