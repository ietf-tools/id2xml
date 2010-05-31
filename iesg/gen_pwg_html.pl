#!/usr/local/bin/perl

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;
use IETF_DBUTIL;

#$ENV{"DBPATH"} = "/export/home/mlee/database";
$ENV{"DBPATH"} = "/usr/informix/databases";
$ENV{"DBNAME"} = "ietf";
#$ENV{"DBNAME"} = "people";

$html_txt = qq{<html>
<TITLE>Proposed Working Groups</TITLE>
</HEAD>

<center><h2>IETF Working Groups </H2></center>

These are the submitted WG descriptions and milestones for all Proposed Working Groups AND/OR recharter submissions, along with whatever status information is available.<p>

<B>NOTE:</B> Explicit direction by the AD is requested to add the group to an IESG Telechat agenda.
<HR>

<A name="grp10"><h2>Proposed Working Groups</H2></A>
<table><tr><th>Area<th>Submitted<th> 
};


$sqlStr=qq{select a.name,a.acronym,g.status_date,g.note,m.acronym         
from group_internal g, acronym a, area_group p, acronym m
where g.group_acronym_id = a.acronym_id
AND g.group_acronym_id = p.group_acronym_id
ANd p.area_acronym_id = m.acronym_id
order by g.status_date DESC
};

my @List = db_select_multiple($sqlStr);
for my $array_ref (@List) {
   my ($name,$acronym,$status_date,$note,$aAcronym) = @$array_ref;
   $name = rm_tr($name);
   $acronym = rm_tr($acronym);
   $status_date = convert_date($status_date,2);
   $status_date = convert_date($status_date);
   if (defined($aAcronym)) {
      $area = uc($aAcronym);
   } else {
      $area = "UND";
   }
   $html_txt .= qq{
<tr><td>$area</td><td nowrap>$status_date</td><td><A HREF="/IESG/internal/BALLOT/${acronym}-charter.txt">$name</a> ($acronym)</td></tr>
};
   if (my_defined($note)) {
      $html_txt .= qq{<tr><td></td><td>Note:</td><td>$note</td></tr>
      };
   }
}

$html_txt .= qq{
</TABLE>
<P>
</body></html>
};
if (defined($ARGV[0]) and $ARGV[0] eq "-deploy") {
   open (OUTFILE,">/usr/local/etc/httpd/htdocs/IESG/internal/PWG.html");
} else {
   open (OUTFILE,">/usr/local/etc/httpd/htdocs/IESG/PWG_NEW.html");
}
print OUTFILE $html_txt;
close(OUTFILE);

exit;




