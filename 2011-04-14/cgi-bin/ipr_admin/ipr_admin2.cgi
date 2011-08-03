#!/usr/bin/perl
##########################################################################
# Copyright © 2004 and 2003, Foretec Seminars, Inc.
##########################################################################
use lib '/a/www/ietf-datatracker/release';
use GEN_DBUTIL;
use GEN_UTIL;
use IETF;
use CGI;
$host = $ENV{SCRIPT_NAME};
$test_mode = ($host =~ /ipr_test/)?1:0;
$db_name = ($test_mode)?"ipr_test":"ietf";
$mode_text = ($test_mode)?"Test Mode":"";

init_database($db_name);
my $q = new CGI;
print qq{Content-type: text/html

<html>
<head><title>IPR Administrate Page $mode_text</title></head>
<body>
};


print qq{
<br>
<center><h2>IPR Admin Page</h2></center><br>
<hr>
<center><h2>Current List in the queue</h2></center>
<blockquote>
};
my $sqlStr = qq{select document_title, ipr_id, submitted_date,status from ipr_detail where status = 0 order by submitted_date desc};
my @List = db_select_multiple($sqlStr);
for $array_ref(@List) {
my ($title, $ipr_id, $submitted_date,$status) = @$array_ref;
print qq{
 <li> <a href="ipr_admin_detail.cgi?&ipr_id=$ipr_id">$title\n</a><br>
};
  }

print qq{
<br><br>
<hr>
<center><h2>Current Active IPR list</h2></center><br>
<h3>Generic IPR</h3>
};
                                                                                
$sqlStr = qq{select document_title, ipr_id, submitted_date,status,additional_old_title1,additional_old_url1,additional_old_title2,additional_old_url2 from ipr_detail where status = 1 and generic=1 and third_party=0 order by submitted_date desc};
my @List2 = db_select_multiple($sqlStr);
for $array_ref(@List2) {
($title, $ipr_id, $submitted_date,$status,$additional_old_title1,$additional_old_url1,$additional_old_title2,$additional_old_url2) = @$array_ref;
print qq{
 <li> <a href="ipr_admin_update.cgi?&ipr_id=$ipr_id">$title\n</a><br>
};
  if (my_defined($additional_old_title1)) {
    print qq{&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href="$additional_old_url1">$additional_old_title1,</a><br>
};
  }
  if (my_defined($additional_old_title2)) {
    print qq{&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href="$additional_old_url2">$additional_old_title2,</a><br>
};
  }


}

print qq{
<br><br>
<hr>
<h3>Third Party Notification</h3>
};
                                                                                                
$sqlStr = qq{select document_title, ipr_id, submitted_date,status,additional_old_title1,additional_old_url1,additional_old_title2,additional_old_url2 from ipr_detail where status = 1 and third_party=1 order by submitted_date desc};
my @List3 = db_select_multiple($sqlStr);
for $array_ref(@List3) {
  ($title, $ipr_id, $submitted_date,$status,$additional_old_title1,$additional_old_url1,$additional_old_title2,$additional_old_url2) = @$array_ref;
  my $count = db_select("select count(*) from ipr_ids where ipr_id=$ipr_id");
  if ($count) {
    print qq{
   <li> <a href="ipr_admin_update.cgi?&ipr_id=$ipr_id">$title ($ipr_id)\n</a><br>
    };
    if (my_defined($additional_old_title1)) {
      print qq{&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href="$additional_old_url1">$additional_old_title1,</a><br>
  };
    }
    if (my_defined($additional_old_title2)) {
      print qq{&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href="$additional_old_url2">$additional_old_title2,</a><br>
  };
    }
  }
}
                                                                                                
print qq{
<br><br>
<hr>
<h3>Specific IPR</h3>
};
                                                                                                
$sqlStr = qq{select document_title, ipr_id, submitted_date,status,additional_old_title1,additional_old_url1,additional_old_title2,additional_old_url2 from ipr_detail where status = 1 and generic=0 and third_party=0 order by submitted_date desc};
my @List4 = db_select_multiple($sqlStr);
for $array_ref(@List4) {
  ($title, $ipr_id, $submitted_date,$status,$additional_old_title1,$additional_old_url1,$additional_old_title2,$additional_old_url2) = @$array_ref;
  my $count = db_select("select count(*) from ipr_ids where ipr_id=$ipr_id");
  if ($count) {
    print qq{
     <li> <a href="ipr_admin_update.cgi?&ipr_id=$ipr_id">$title ($ipr_id)\n</a><br>
    };
    if (my_defined($additional_old_title1)) {
      print qq{&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href="$additional_old_url1">$additional_old_title1,</a><br>
  };
    }
    if (my_defined($additional_old_title2)) {
      print qq{&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href="$additional_old_url2">$additional_old_title2,</a><br>
  };
    }
  }
}
                                                                                                

print qq{
<br><br>
<hr>
<center><h2>IPR Removed by IPR Admin list</h2></center><br>
<blockquote>
};
my $sqlStr = qq{select document_title, ipr_id, submitted_date,status,additional_old_title1,additional_old_url1,additional_old_title2,additional_old_url2 from ipr_detail where status = 2 order by submitted_date desc};
@List = db_select_multiple($sqlStr);
for $array_ref(@List) {
($title, $ipr_id, $submitted_date,$status,$additional_old_title1,$additional_old_url1,$additional_old_title2,$additional_old_url2) = @$array_ref;
print qq{
 <li> <a href="ipr_admin_update.cgi?&ipr_id=$ipr_id">$title ($ipr_id)\n</a><br>
};
 if (my_defined($additional_old_title1)) {
    print qq{&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href="$additional_old_url1">$additional_old_title1,</a><br>
};
  }
  if (my_defined($additional_old_title2)) {
    print qq{&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href="$additional_old_url2">$additional_old_title2,</a><br>
};
  } 
  }

print qq{
</blockquote>
<br><br>
<hr>
<center><h2>IPR Removed by Request list</h2></center><br>
<blockquote>
}; 
$sqlStr = qq{select document_title, ipr_id, submitted_date,status,additional_old_title1,additional_old_url1,additional_old_title2,additional_old_url2 from ipr_detail where status = 3 order by submitted_date desc};
@List = db_select_multiple($sqlStr);
for $array_ref(@List) {
($title, $ipr_id, $submitted_date,$status,$additional_old_title1,$additional_old_url1,$additional_old_title2,$additional_old_url2) = @$array_ref;
print qq{
 <li> <a href="ipr_admin_update.cgi?&ipr_id=$ipr_id">$title ($ipr_id)\n</a><br>
};
 if (my_defined($additional_old_title1)) {
    print qq{&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href="$additional_old_url1">$additional_old_title1,</a><br>
};
  }
  if (my_defined($additional_old_title2)) {
    print qq{&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href="$additional_old_url2">$additional_old_title2,</a><br> };
  }
  }
                                                                                                    

print qq{
  </blockquote>
  <hr>
  <br><br>
  <a href="ipr_internal.cgi"><img src="/images/blue.gif" hspace="3" border="0">IPR Internal page</a><br><br>
  <a href="https://datatracker.ietf.org/public/ipr_disclosure.cgi"><img src="/images/blue.gif" hspace="3" border="0">IPR Disclosure page</a><br><br>
                                                                                
  </body></html>
};

