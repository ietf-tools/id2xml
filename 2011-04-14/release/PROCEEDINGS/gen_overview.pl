#!/usr/bin/perl

use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

init_database("ietf");
require '/a/www/ietf-datatracker/release/PROCEEDINGS/header.pl';
die "Error\n" unless defined($ARGV[0]);
my $section_num = $ARGV[0];
my $text_val1 = db_select("select info_text from general_info where info_name='overview1'");
my $text_val2 = db_select("select info_text from general_info where info_name='overview2'");
my $iesg_list = qq{<p>
<table cellspacing="1" cellpadding="1">
  <tbody>
    <tr>
      <td valign="Top" width="191">
      <p align="Left"><font face="Times New Roman">Name</font></p>
      </td>
      <td valign="Top" width="204">
      <p align="Left"><font face="Times New Roman">Area</font></p>

      </td>
      <td valign="Top" width="216">
      <p align="Left"><font face="Times New Roman">Email</font></p>
      </td>
    </tr>
};
my $person_or_org_tag_chair = db_select("select person_or_org_tag from proceeding.chairs where chair_name='IETF'");
my $chair_name=get_name($person_or_org_tag_chair);
$iesg_list .= qq{<tr>
   <td valign="Top" width="191">
   <p align="Left"><font face="Times New Roman">$chair_name</font></p>
   </td>
   <td valign="Top" width="204">
   <p align="Left"><font face="Times New Roman">IETF Chair</font></p>

   </td>
   <td valign="Top" width="216">
   <p align="Left"><font face="Times New Roman">&lt;chair\@ietf.org&gt;</font></p>
   </td>
</tr>
};
my @List = db_select_multiple("select first_name,last_name,person_or_org_tag from proceeding.iesg_login where user_level=1 and person_or_org_tag <> $person_or_org_tag_chair and id <> 1 order by last_name");
for my $array_ref (@List) {
  my ($first_name,$last_name,$person_or_org_tag) = @$array_ref;
  my $area_name = db_select("select name from proceeding.acronym a, proceeding.area_directors b, proceeding.areas c where b.person_or_org_tag=$person_or_org_tag and b.area_acronym_id=acronym_id and b.area_acronym_id=c.area_acronym_id and c.status_id=1");
  $area_name =~ s/Area//g;
  my $email = get_email($person_or_org_tag);
  $iesg_list .= qq{<tr>
      <td valign="Top" width="191">
      <p align="Left"><font face="Times New Roman">$first_name $last_name</font></p>
      </td>
      <td valign="Top" width="204">

      <p align="Left"><font face="Times New Roman">$area_name</font></p>
      </td>
      <td valign="Top" width="216">
      <p align="Left"><font face="Times New Roman">&lt;$email&gt;</font></p>
      </td>
</tr>
};
}

$iesg_list .= "</tbody></table></>\n";
open OUT,">$TARGET_DIR/overview.html";
print OUT qq{<HTML>
<HEAD>
<TITLE></TITLE>
</HEAD>
<BODY BGCOLOR="#ffffff" LINK="#004080" BACKGROUND="graphics/peachbkg.gif"><A NAME="TopOfPage"> </A>
<img src='graphics/ib2.gif' width='100%' height=21><br><br>
<h2>1.$section_num IETF Overview</h2>
$text_val1
$iesg_list
$text_val2
</BODY></HTML>
};
close OUT;
exit
