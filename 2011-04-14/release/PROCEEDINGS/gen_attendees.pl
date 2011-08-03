#!/usr/bin/perl

use lib '/a/www/ietf-datatracker/release';
use GEN_UTIL;
use GEN_DBUTIL_NEW;
use IETF;

init_database("ietf");
$dbh=get_dbh();
require '/a/www/ietf-datatracker/release/PROCEEDINGS/header.pl';
die "Error\n" unless defined($ARGV[0]);
my $meeting_num = $ARGV[0];
open OUT,">$TARGET_DIR/attendees.html";
print OUT qq{<HTML>
<HEAD>
<TITLE></TITLE>
</HEAD>
<BODY BGCOLOR="#ffffff" LINK="#004080" BACKGROUND="graphics/peachbkg.gif"><A NAME="TopOfPage"> </A>
<img src="graphics/ib2.gif" width="100%" height=21><br><br>
<h2>6  Attendees List</h2>

<p><font face="Times New Roman">
The list of attendees of the following pages is provided for the convenience of IETF participants while doing IETF work.  Note that it is inappropriate to use this information for marketing purposes.</FONT></P>
</P> <a href="att0.html">Click here for list.</a>

</BODY></HTML>
};
close OUT;
for ($loop=0;$loop<8;$loop++) {
  my $like_ph = "";
  if ($loop==0) {
    $like_ph = "last_name like 'A%' or last_name like 'B%'";
  } elsif ($loop == 1) {
    $like_ph = "last_name like 'C%' or last_name like 'D%' or last_name like 'E%'";
  } elsif ($loop == 2) {
    $like_ph = "last_name like 'F%' or last_name like 'G%' or last_name like 'H%'";
  } elsif ($loop == 3) {
    $like_ph = "last_name like 'I%' or last_name like 'J%' or last_name like 'K%'";
  } elsif ($loop == 4) {
    $like_ph = "last_name like 'L%' or last_name like 'M%'";
  } elsif ($loop == 5) {
    $like_ph = "last_name like 'N%' or last_name like 'O%' or last_name like 'P%'";
  } elsif ($loop == 6) {
    $like_ph = "last_name like 'Q%' or last_name like 'R%' or last_name like 'S%'";
  } elsif ($loop == 7) {
    $like_ph = "last_name like 'T%' or last_name like 'U%' or last_name like 'V%' or last_name like 'W%' or last_name like 'X%' or last_name like 'Y%' or last_name like 'Z%'";
  }
  open OUT2,">$TARGET_DIR/att$loop.html";
  print OUT2 qq{
<html>
<title>
Attendees List
</title>
<body bgcolor="#ffffff"  background="graphics/peachbkg.gif">
The list of attendees is provided for the convenience of IETF participants<br>
while doing IETF work. Note that it is inappropriate to use this<br>
information for marketing purposes.<br> 
<h2>Attendees List</h2>
<p><font face="Times New Roman">

<h2>
<a href="att0.html"> A B </a>&nbsp;  
<a href="att1.html"> C D E </a> &nbsp; 
<a href="att2.html"> F G H </a> &nbsp; 
<a href="att3.html"> I J K </a> &nbsp; 
<a href="att4.html"> L M </a> &nbsp; 
<a href="att5.html"> N O P </a> &nbsp; 
<a href="att6.html"> Q R S </a> &nbsp; 
<a href="att7.html"> T U V W X Y Z </a> &nbsp; 
</h2>
};
  my @List = db_select_multiple($dbh,"select first_name,last_name,affiliated_company from meeting_attendees where meeting_num=$meeting_num and ($like_ph) order by last_name,first_name");
  for my $array_ref (@List) {
    my ($first_name,$last_name,$comp) = @$array_ref;
    print OUT2 "$last_name, $first_name<br>\n$comp<br><br>\n\n"; 
  }
  print OUT2 "</body></html>\n";
  close OUT2;
}
$dbh->disconnect();
exit
