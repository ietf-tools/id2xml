#!/usr/bin/perl -w
##########################################################################
#      Copyright © 2004 Foretec Seminars, Inc.
#
#      Program: idnits.cgi
#      Author : Michael Lee, Foretec Seminars, Inc
#      Last Modified Date: 9/25/2004
#
#      This Web application provides ... 
#
#####################################################
use lib '/a/www/ietf-datatracker/release';
use GEN_DBUTIL;
use GEN_UTIL;
use IETF;
use CGI;
use CGI_UTIL;
use constant BUFFER_SIZE => 16_384;
use constant MAX_FILE_SIZE => 1_572_864;
use constant MAX_OPEN_TRIES => 100;
$CGI::DISABLE_UPLOADS = 0;
$CGI::POST_MAX = MAX_FILE_SIZE;

init_database("ietf");

my $q = new CGI;
$program_name = "idnits.cgi";
$program_title = "I-D Validator";
$table_header = qq{<table cellpadding="0" cellspacing="0" border="0">
};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">};
$form_header_post2 = qq{<form action="$program_name" method="POST" name="form_post2">};
$form_header_post3 = qq{<form action="$program_name" method="POST" name="form_post3">};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">};
$form_header_upload = qq{<form action="$program_name" method="POST" ENCTYPE="multipart/form-data" name="upload_form">};

$form_header_get = qq{<form action="$program_name" method="GET" name="form_get">};
$current_year = db_select("select year(current_date)");
$correct_cs_header = "Copyright (C) The IETF Trust ($current_year)";
$ipr1_o = "By submitting this Internet-Draft, each author represents 
that any applicable patent or other IPR claims of which he 
or she is aware have been or will be disclosed, and any of 
which he or she becomes aware will be disclosed, in 
accordance with Section 6 of BCP 79";
$ipr2_o = "This document is subject to the rights, licenses 
and restrictions contained in BCP 78, and except as set forth 
therein, the authors retain all their rights";
$ipr3_o = "This document and the information contained herein 
are provided on an \"AS IS\" basis and THE CONTRIBUTOR, THE 
ORGANIZATION HE/SHE REPRESENTS OR IS SPONSORED BY (IF ANY), THE 
INTERNET SOCIETY AND THE INTERNET ENGINEERING TASK FORCE DISCLAIM 
ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO 
ANY WARRANTY THAT THE USE OF THE INFORMATION HEREIN WILL NOT 
INFRINGE ANY RIGHTS OR ANY IMPLIED WARRANTIES OF MERCHANTABILITY 
OR FITNESS FOR A PARTICULAR PURPOSE";
$ipr3_o_new = "This document and the information contained herein
are provided on an \"AS IS\" basis and THE CONTRIBUTOR, THE
ORGANIZATION HE/SHE REPRESENTS OR IS SPONSORED BY (IF ANY), THE 
INTERNET SOCIETY, THE IETF TRUST AND THE INTERNET ENGINEERING TASK FORCE DISCLAIM
ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
ANY WARRANTY THAT THE USE OF THE INFORMATION HEREIN WILL NOT
INFRINGE ANY RIGHTS OR ANY IMPLIED WARRANTIES OF MERCHANTABILITY
OR FITNESS FOR A PARTICULAR PURPOSE";
$ipr3_o_both = "This document and the information contained herein
are provided on an \"AS IS\" basis and THE CONTRIBUTOR, THE
ORGANIZATION HE/SHE REPRESENTS OR IS SPONSORED BY (IF ANY), THE
INTERNET SOCIETY, (THE IETF TRUST) AND THE INTERNET ENGINEERING TASK FORCE DISCLAIM
ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
ANY WARRANTY THAT THE USE OF THE INFORMATION HEREIN WILL NOT
INFRINGE ANY RIGHTS OR ANY IMPLIED WARRANTIES OF MERCHANTABILITY
OR FITNESS FOR A PARTICULAR PURPOSE";

$verbatim_o = "Internet-Drafts are working documents of the Internet 
Engineering Task Force (IETF), its areas, and its 
working groups. Note that other groups may also distribute 
working documents as Internet-Drafts.

Internet-Drafts are draft documents valid for a maximum of 
six months and may be updated, replaced, or obsoleted by 
other documents at any time. It is inappropriate to use 
Internet-Drafts as reference material or to cite them other 
than as \"work in progress.\"

The list of current Internet-Drafts can be accessed at http://www.ietf.org/1id-abstracts.html 

The list of Internet-Draft Shadow Directories can be accessed at http://www.ietf.org/shadow.html";
$ipr1 = lc($ipr1_o);
$ipr2 = lc($ipr2_o);
$ipr3 = lc($ipr3_o);
$ipr3_new = lc($ipr3_o_new);
$verbatim_f = lc($verbatim_o);
$ipr1 =~ s/\(/\\(/g;
$ipr2 =~ s/\(/\\(/g;
$ipr3 =~ s/\(/\\(/g;
$ipr3_new =~ s/\(/\\(/g;
$verbatim_f =~ s/\(/\\(/g;
$ipr1 =~ s/\)/\\)/g;
$ipr2 =~ s/\)/\\)/g;
$ipr3 =~ s/\)/\\)/g;
$ipr3_new =~ s/\)/\\)/g;
$verbatim_f =~ s/\)/\\)/g;
$ipr1 =~ s/\s+//g;
$ipr2 =~ s/\s+//g;
$ipr3 =~ s/\s+//g;
$ipr3_new =~ s/\s+//g;
$verbatim_f =~ s/\s+//g;
$html_top = qq|
<h2><center>$program_title</center></h2>
<br><br>
|;
$html_bottom = qq{
</body>
</html>
};

$html_body = get_html_body($q);

print $q->header("text/html"),
      $q->start_html("$program_title"),
      $q->p($html_top),
      $q->p($html_body),
      $q->end_html;

exit;

sub get_html_body {
   my $q = shift;
   my $command = $q->param("command");
   my $html_txt;
   unless (my_defined($command)) {
     $html_txt = main_screen($q);
   } else {
     my $func = "$command(\$q)";
     $html_txt = eval($func);
   }
   $html_txt .= qq {
   $form_header_bottom
   <input type="hidden" name="command" value="main_screen">
   <input type="submit" value="Main Menu">
   <input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true">
   </form>
   } if (my_defined($command) and $command ne "main_menu");
   return $html_txt;
}

sub main_screen {
  my $ret_val= qq{
$form_header_upload
<input type="hidden" name="command" value="upload">
<p> Please choose an I-D to validate:
<input type="FILE" name="file">
<br>
<br><input type="submit" value="Validate Now"><br>
</form>
<br><br><font color="#FF0000"><b>NOTE: THIS IS NOT THE SAME TOOL AS THE CURRENT "IDNITS" TOOL USED BY THE COMMUNITY.  THIS TOOL WAS LAST MODIFIED IN 2005.  DO NOT EXPECT THE SAME RESULTS WITH THIS TOOL AS YOU WOULD GET FROM THE CURRENT COMMUNITY TOOL!!!</b></font>
<br><br><br>
};

  my $emerg_auto_response=db_select("select emerg_auto_response from id_submission_env");
  if ($emerg_auto_response) {
    $ret_val .= qq{
<font size=+1 color="red">Auto responder is sending a notification with I-D processing difficulty alert
$form_header_post
<input type="hidden" name="command" value="toggle_emerg">
<input type="hidden" name="emerg_auto_response" value="0">
<input type="submit" value="Switch to normal auto response message">
</form>
</font>
};
  } else {
    $ret_val .= qq{<br><br><br><br><br>
Auto responder is sending a normal notification
$form_header_post
<input type="hidden" name="command" value="toggle_emerg">
<input type="hidden" name="emerg_auto_response" value="1">
<input type="submit" value="Switch to I-D processing difficulty alert auto response message" onClick="return window.confirm('You are about to switch the auto response message to alert mode');">
</form>
};

  }

  return $ret_val;

}

sub toggle_emerg {
  my $q=shift;
  my $emerg_auto_response = $q->param("emerg_auto_response");
  db_update("update id_submission_env set emerg_auto_response=$emerg_auto_response");
  return main_screen();

}

sub upload {
  my $q=shift;
  $q->cgi_error and cgi_error ($q, "Error transferring file:. " . $q->cgi_error );
  my $file = $q->param("file")  || cgi_error ($q,"No file received.");
  my $fh = $q->upload("file", -override=>1);
  unless ($fh) {
    cgi_error ($q,"Invalid File - $file, $fh");
  }
  my $id_body = "";
  my $type=$q->uploadInfo($fh)->{'Content-Type'};
  seek($fh,0,2);
  my $size=tell($fh);
  seek($fh,0,0);
  my $buffer = "";
  binmode $fh;
  while (read($fh,$buffer,BUFFER_SIZE)) {
    $buffer = rm_hd($buffer);
    $id_body .= $buffer;
  }
  my ($valid_ipr,$valid_cs1,$valid_cs2,$valid_cs3,$valid_filename,$valid_bp,$first_page,$filename,$num_page,$last_two_page,$last_three_page,$valid_cs_header) = id_validate($id_body);
  ($first_page,$last_two_page,$last_three_page) = html_bracket($first_page,$last_two_page,$last_three_page);
  my $html_txt = qq{<center><font size=+2> *** Validating Result ***</font></center><br>
$form_header_post
<input type="hidden" name="command" value="display_error">
<input type="hidden" name="valid_ipr" value="$valid_ipr">
<input type="hidden" name="valid_cs1" value="$valid_cs1">
<input type="hidden" name="valid_cs2" value="$valid_cs2">
<input type="hidden" name="valid_cs3" value="$valid_cs3">
<input type="hidden" name="valid_cs_header" value="$valid_cs_header">
<input type="hidden" name="valid_filename" value="$valid_filename">
<input type="hidden" name="valid_bp" value="$valid_bp">
};
  my $ipr_result = ($valid_ipr)?"Correct IPR statement was found":"<font color=\"red\">Correct IPR statement WAS NOT found in first page of the document <BR><pre>$ipr1_o</pre></font>";
  my $cs_result1 = ($valid_cs1)?"Correct Copyright statement (First Paragraph) was found":"<font color=\"red\">Correct Copyright statement (First Paragraph) WAS NOT found <BR><pre>$ipr2_o</pre></font>";
  my $cs_result2 = ($valid_cs2)?"Correct Copyright statement (Second Paragraph) was found on last two pages":"<font color=\"red\">Correct Copyright statement (Second Paragraph) WAS NOT found on the last two pages <br><pre>$ipr3_o_new</pre></font>";
  if ($valid_cs2) {
    $cs_result3 = ($valid_cs3)?"Copyright statement (Second Paragraph) was only on the last two pages":"<font color=\"red\">Copyright statement (Second Paragraph) was found on a page other than the last two pages <br><pre>$ipr3_o_new</pre></font>";
  }
  my $cs_header_result = ($valid_cs_header)?"Correct Copyright Statement was found":"<font color=\"red\">Correct Copyright Statement, \"$correct_cs_header,\" WAS NOT found</font>";
  my $filename_result = "";
  my $version_result = "";
  my $old_rfc_number_result = "";
  if ($id_body =~ /2026|3667|3668/) {
    $old_rfc_number_result = qq{<li> <font color="#aa0088">One of the old RFC number (2026, 3667, 3668) has been detected.</font><br>
};
  }
  if ($valid_filename) { 
    $_ = $filename;
    /^(draft-.*)-(\d\d)$/;
    $filename = $1;
    my $version = $2;
    $filename_result = "Filename: $filename";
    $version_result = "<li> Version: $version<br>";
  } else {
     $filename_result = "<font color=\"red\">I-D Filename WAS NOT found</font>";
  }
  my $bp_result = ($valid_bp)?"Correct verbatim statement was found on the first page":"<font color=\"red\">Correct verbatim statement WAS NOT found on the first page <br><pre>$verbatim_o</pre></font>";
  $html_txt .= qq{
<br>
<li> $ipr_result  <br>
<li> $cs_header_result <br>
<li> $cs_result1 <br>
<li> $cs_result2 <br>
<li> $cs_result3 <br>
<li> $bp_result <br>
<li> $filename_result<br>
$version_result
$old_rfc_number_result
<li> Number of Pages: $num_page<br>
<hr>
<b>First Two Pages:</b><br>
<pre>
$first_page
</pre>
<br><br>
<input type="checkbox" name="valid_abstract"> <font size=+1 color="blue">Abstract section found</font><br>
<hr>
<b>Last Two Pages:</b><br>
<pre>
$last_two_page
</pre>
<br><br>
<input type="checkbox" name="valid_author"> <font size=+1 color="blue">Valid Authors' Contact information found</font><br><hr>
<br>
<input type="submit" value=" Display Error message "><br><br>
</form>
<br><br>
};
  return $html_txt;
}

sub id_validate {
  my $o_body = shift;
  $_ = lc($o_body);
  s/ \r//g;
  s/\s+\n/\n/g;
  s/\n\s+/ /g; 
  s/\n/ /g; 
  s/\r//g; 
  s/\s+//g;
  my $body = $_;
  my @pages = split "page1";
  my $first_page = $pages[0];
  @pages = split "Page ",$o_body;
  my $o_first_page = $pages[0] . $pages[1];
  #my $last_two_page = $pages[$#pages-1].$pages[$#pages];
  $last_two_page = $pages[$#pages-2].$pages[$#pages-1];
  my $last_three_page = $pages[$#page-3].$last_two_page;
  my $last_page = $pages[$#pages];
  $last_two_page = $pages[$#pages-1].$pages[$#pages] if ($last_page =~ /\S{5}/);
  my $last_one_page = $pages[$#pages-1];
  my $last_two_page_ori=$last_two_page;
  $_ = lc($last_two_page);
  s/ \r//g;
  s/\s+\n/\n/g;
  s/\n\s+/ /g;
  s/\n/ /g;
  s/\r//g;
  s/\s+//g;
  $last_two_page=$_;
  pop @pages;
  pop @pages;
  pop @pages;
  my $body_wo_last = join "",@pages;
  $_=lc($body_wo_last);
  s/ \r//g;
  s/\s+\n/\n/g;
  s/\n\s+/ /g;
  s/\n/ /g;
  s/\r//g;
  s/\s+//g;
  $body_wo_last=$_;
  my $valid_ipr = 1;
  my $valid_cs1 = 1;
  my $valid_cs2 = 0;
  my $valid_cs3 = 1;
  my $valid_filename = 1;
  my $valid_bp = 1;
  $_ = $last_page;
  /^(\d+).*/;
  my $num_page = $1;
  $_ = $o_first_page;
  /.*(draft-\S+-\d\d).*/;
  my $filename = $1;
  $filename = "" unless ($filename =~ /^draft-/);
  ######### Check IPR statement ###########
  $valid_ipr = 0 unless ($first_page =~ /$ipr1/);
  ######### End check IPR statement #########

  ######## Check Copy Right Statement ######
  $valid_cs1 = 0 unless ($body =~ /$ipr2/);
  #$valid_cs2 = 0 unless ($body =~ /$ipr3/);
#  $valid_cs2 = 1 if ($last_two_page =~ /$ipr3/);
  $valid_cs2 = 1 if ($last_two_page =~ /$ipr3_new/);
#  $valid_cs2 = 1 if ($last_page_plus =~ /$ipr3_new/);
#  $valid_cs3 = 0 if ($body_wo_last =~ /$ipr3/);
  $valid_cs3 = 0 if ($body_wo_last =~ /$ipr3_new/);

  ############## End check Copy Right Statement ####

  ############## Check Filename ############
  $valid_filename = 0 unless my_defined($filename);
   error($q,"Filename contains non alpha-numeric character") if ($filename =~/\&|\*|;/);
  ############## End check Filename #######

  ############ Check Verbatim Statement #######
  $first_page =~ s/abstracts.txt/abstracts.html/g;
  $first_page =~ s/\/ietf\//\//g;
  $first_page =~ s/abstracts.html\./abstracts.html/g;
  $first_page =~ s/shadow.html\./shadow.html/g;
  $valid_bp = 0 unless ($first_page =~ /$verbatim_f/);
   ############ End check Verbatim Statement ###
  $_ = $o_body;
  my $valid_cs=0;
  while (/(Copyright \(C\) The )(IETF Trust)( \()(\d\d\d\d)/) {
    my $cs_year = $4;
    $valid_cs = ($cs_year == $current_year)?1:0;
    last if ($valid_cs == 0);
    s/Copyright \(C\) The (IETF Trust) \(\d\d\d\d\)//;
    $valid_cs=1;
  }
  #$valid_cs=0 if ($valid_cs<0);
  return ($valid_ipr,$valid_cs1,$valid_cs2,$valid_cs3,$valid_filename,$valid_bp,$o_first_page,$filename,$num_page,$last_two_page_ori,$last_three_page,$valid_cs);
}

sub display_error {
  my $q=shift;
  my $valid_ipr=$q->param("valid_ipr");
  my $valid_cs1 = $q->param("valid_cs1");
  my $valid_cs2 = $q->param("valid_cs2");
  my $valid_cs3 = $q->param("valid_cs3");
  my $valid_cs_header = $q->param("valid_cs_header");
  my $valid_filename=$q->param("valid_filename");
  my $valid_bp = $q->param("valid_bp");
  my $valid_abstract=$q->param("valid_abstract");
  my $valid_author=$q->param("valid_author");
  my $error_msg = "The Secretariat CANNOT process your Internet-Draft submission due to following reason(s): <br><br>";
  $error_msg .= qq{ <b>*</b> All Internet-Drafts must have on the first page an intellectual property
rights (IPR) statement that says:
<br>
$ipr1_o.<br>
If you are using xml2rfc, this can be accomplished by updating the
'ipr' attribute in the 'rfc' element to refer to 3978. See
http://xml.resource.org/authoring/draft-mrose-writing-rfcs.html#ipr for
more information.<Br>
} unless ($valid_ipr);
  $error_msg .= qq{ <b>*</b> All Internet-Drafts must include the following statement:

$correct_cs_header.
<br>
} unless ($valid_cs_header);
  $error_msg .= qq{ <b>*</b> All Internet-Drafts must include the following statement:
                                                                                                            
$ipr2_o.
<br>
} unless ($valid_cs1);
  $error_msg .= qq{ <b>*</b> All Internet-Drafts must include the following statement near the end of the document.:
                                                                                                            
$ipr3_o_new.
<br>
} unless ($valid_cs2);
  $error_msg .= qq{ <b>*</b> All Internet-Drafts must not include the following statement on any other page than near the end of the document:
                                                                                                                                                                         
$ipr3_o_new.
<br>
} unless ($valid_cs3);

  $error_msg .= qq{ <b>*</b> All Internet-Drafts must contain the full filename
(beginning with draft- and including the version number) in the text
of the document.<br><br>
} unless ($valid_filename);
  $error_msg .= qq{ <b>*</b> All Internet-Drafts must include the following statements:

$verbatim_o
<br>
} unless ($valid_bp);
  $error_msg .= qq{ <b>*</b> All Internet-Drafts must have an Abstract section.<br>
} unless ($valid_abstract);
  $error_msg .= qq{ <b>*</b> All Internet-Drafts should contain a section giving 
the name(s) and contact information for the authors.
} unless ($valid_author);
  return "<pre>\n$error_msg\n</pre>\n";
}

