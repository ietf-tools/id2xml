#!/opt/local/bin/perl

# This is a hand edited version of the output of select body_name,poc from from_bodies

%bodies=(
"3GPP",99,
"3GPP TSG RAN WG2",100,
"3GPP2",104,
"ATIS",18,
"ATM Forum",4,
"BBF",115,
"CableLabs",108,
"DSL",90,
"DSL Forum",26,
"EPCGlobal",41,
"ETSI",19,
"ETSI EMTEL",17,
"ETSI TISPAN",40,
"Femto Forum",116,
"GSMA WLAN",93,
"IAB",21,
"IAB/IESG",105,
"IAB/ISOC",31,
"ICANN",13,
"IEEE 802",12,
"IEEE 802.1",129,
"IEEE 802.1 WG",95,
"IEEE 802.11",101,
"IEEE 802.21",103,
"IESG",118,
"IETF ADSL MIB",89,
"IETF ANCP WG",96,
"IETF CCAMP WG",27,
"IETF IMSS",82,
"IETF INT AD",106,
"IETF IPCDN WG",29,
"IETF LEMONADE WG",30,
"IETF Mead Team",114,
"IETF MEAD Team",124,
"IETF MMUSIC WG",38,
"IETF MPLS WG",28,
"IETF PCE WG",37,
"IETF PWE3 WG",92,
"IETF RAI Area",112,
"IETF RAI WG",102,
"IETF ROHC WG",98,
"IETF Routing Area",34,
"IETF SEC AREA",120,
"IETF SIGTRAN",107,
"IETF SIPPING WG",111,
"IETF SPEECHSC WG",32,
"IETF Transport Directorate",33,
"IETF-Radext WG",81,
"INCITS T11.5",83,
"ISO/IEC JTC 1 SGSN",117,
"ISO/IEC JTC 1/SC 29/WG 11",122,
"ISO/IEC JTC 1/SC31/WG 4/SG 1",42,
"ISO/IEC JTC1 SC2",1,
"ISO/IEC JTC1 SC29",3,
"ISO/IEC JTC1 SC6",2,
"ISOC",20,
"ISOC/IAB",22,
"ITU",44,
"ITU-R WP 5A",126,
"ITU-R WP 5D",127,
"ITU-R WP8A",80,
"ITU-R WP8F",86,
"ITU-T",5,
"ITU-T FG IPTV",97,
"ITU-T MPLS",128,
"ITU-T SG 11",70,
"ITU-T SG 12",71,
"ITU-T SG 13",113,
"ITU-T SG 15",73,
"ITU-T SG 16",74,
"ITU-T SG 17",75,
"ITU-T SG 19",76,
"ITU-T SG 2",64,
"ITU-T SG 3",65,
"ITU-T SG 4",66,
"ITU-T SG 5",67,
"ITU-T SG 6",68,
"ITU-T SG 9",69,
"ITU-T TSAG",77,
"JCA-IdM",125,
"MFA Forum",62,
"MPLS and Frame Relay Alliance",24,
"NANP LNPA WG",35,
"NGN Management Focus Group",36,
"OIF",25,
"OMA",78,
"Open IPTV Forum",109,
"PANA WG",84,
"RSSAC",11,
"TIA",85,
"TMOC",23,
"Unicode",6,
"W3C",7,
"W3C Geolocation WG",130,
"WIPO",8,
);

open(INPUT, "liaisondetail_list_hacked.html");
$/ = '<tr>';
while ($_ = <INPUT>) {
    last if (/Legacy stuff, hardcoded/);
}
$index = 0;
while ($_ = <INPUT>) {
    s/ valign=top>/>/g;
    s/ valign="top">/>/g;
    s/ nowrap>/>/g;
    s/<td>/<td>/gi;
    s/<\/td>//gi;
    s/<\/tr>//gi;
    s/<tr>//gi;
    s/<br>//gi;
    s/\s+/ /g;
    s/<.table> .. endblock ..//;
    s/^\s*<td>//;
    s/\s*<td>/\t/g;
    @cols = split /\t/;
#    print "****\n";
#    print join(':',@cols)."\n";
#    print $cols[3]."\n";
    if (@cols != 4) {
        die "Not four columns";
    } 
    $date = $cols[0];
    if ($date !~ /^(\w+) (\d\d\d\d)$/) {
        print $_;
        die "Bad date $date";
    }
    else {
     $month=$1; $year=$2;
        $month2 = "01" if ($month =~ /^jan/i);
        $month2 = "02" if ($month =~ /^feb/i);
        $month2 = "03" if ($month =~ /^mar/i);
        $month2 = "04" if ($month =~ /^apr/i);
        $month2 = "05" if ($month =~ /^may/i);
        $month2 = "06" if ($month =~ /^jun/i);
        $month2 = "07" if ($month =~ /^jul/i);
        $month2 = "08" if ($month =~ /^aug/i);
        $month2 = "09" if ($month =~ /^sep/i);
        $month2 = "10" if ($month =~ /^oct/i);
        $month2 = "11" if ($month =~ /^nov/i);
        $month2 = "12" if ($month =~ /^dec/i);
        $date = "$year-$month2-01";
    }

    $links = $cols[3];
    $links =~ s/\(\.?pdf file\)//g;
    $links =~ s/\(pdf\)//g;
    $links =~ s/<\/a>( \(Temporary Document [^)]+\))/\1<\/a>/g;
#    if ($links !~ /^(\s*<a href="[^"]+">[^<]*<\/a>)+\s*$/i) {
#        print "------\n", $links, "\n";  
#    }
    
    while ($links=~/\s*<a href="(.*?)"\s*>(.*?)<\/A>\s*/gi)
    { 
      $link = $1; 
      if ($link=~/itut-ls-dismanwg-liaison-reply/) { $link=~s/reply/reply.pdf/;}
      $desc = $2; 
    }

    if ($link=~/itut-ls-dismanwg-liaison-reply/) { $link=~s/reply/reply.pdf/;}
# AM HERE - look for more than one link

    @funk = split(/href/i, $links);
    if ($#funk>1) {die $links;} 



    $date[$index] = $date;
    $from[$index] = $cols[1];
    $to[$index] = $cols[2];
    $link[$index] = $link;
    @junk = split '/',$link; 
    $f=pop @junk; 
    @decomp=split '\.',$f;
    if (@decomp>1) {$ext[$index] = ".".(pop @decomp);} else {$ext[$index]="";}
    $basename[$index] = join '.',@decomp;
    $desc[$index] = $desc;


    $index++;
}

#print "Have $index things\n";
#print join("\n",@from);
#print join("\n",@link);


open (SQLOUT,">stufftodo.sql");
# Print out rows to add to from_bodies
$from_body_insert_index = 135; # leaves some unused indexes
for ($i=0;$i<$index;$i++)
{
  if (!exists($bodies{$from[$i]}) )
  {
    print SQLOUT "insert into from_bodies (from_id, body_name) values ($from_body_insert_index,\"$from[$i]\");\n";
    $bodies{$from[$i]} = $from_body_insert_index;
    $from_body_insert_index++;
  }
#  else
#  { print "Going to use existing row for $from[$i]\n"; }
}

# Print out rows to add to Uploads

# Print out rows to add to liason_detail
$liaison_detail_insert_index = 615; # leaves some unused indexes
$uploads_insert_index = 740; # leaves some unused indexes
for ($i=0;$i<$index;$i++)
{
   $safedesc=$desc[$i];
   $safedesc=~s/'/''/g;
   print SQLOUT "insert into uploads (file_id,file_title,file_extension,detail_id) values ($uploads_insert_index,\'$safedesc\',\"$ext[$i]\",$liaison_detail_insert_index);\n";
   print SQLOUT "insert into liaison_detail (detail_id,submitted_date,from_id,to_body,by_secretariat,submitter_email,submitter_name) ".
                             "values ($liaison_detail_insert_index,\"$date[$i]\",$bodies{$from[$i]},\"$to[$i]\",1,NULL,\"$to[$i]\");\n";
   $name_to_file_no{$link[$i]}=$uploads_insert_index;
   $uploads_insert_index++;
   $liaison_detail_insert_index++;
}

close (SQLOUT);

open (SHOUT,">stufftodo.sh");

# Print out shell commands to move and back-link old statements
for ($i=0;$i<$index;$i++)
{
  if ($link[$i]=~/w3.org/)
  {
    print SHOUT "echo '<html><body><t>See $link[$i]</t></body></html>' > file$name_to_file_no{$link[$i]}$ext[$i]\n";
  }
  else
  {
    print SHOUT "mv $basename[$i]$ext[$i] file$name_to_file_no{$link[$i]}$ext[$i]\n";
    print SHOUT "ln -s file$name_to_file_no{$link[$i]}$ext[$i] $basename[$i]$ext[$i]\n";
  }
}

close (SHOUT);
