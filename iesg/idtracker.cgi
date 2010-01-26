#!/usr/bin/perl

##########################################################################
#      Copyright © 2004, 2003, and 2002, Foretec Seminars, Inc.
#              
#      Program: idtracker.cgi
#      Author : Michael Lee, Foretec Seminars, Inc
#      Last Modified Date: 8/25/2004
#  
#      This Web application provides ID Draft Tracking and Maintaining 
#      capability to IESG Members
#
#####################################################

use lib '/home/henrik/src/db/legacy/iesg';
use CGI;
use IETF;
use GEN_DBUTIL_NEW;
use GEN_UTIL;
use CGI_UTIL;

$script_loc=$ENV{SCRIPT_NAME};
$host=$ENV{HTTP_HOST};

$test_mode=0;
$devel_mode=0;
my $db_name = "ietf";

$test_url_part = "";

$SOURCE_DIR = "/home/henrik/src/db/legacy/iesg";
$INTERNAL_DIR = "/a/www/www6/iesg/internal";
$EVAL_DIR = "/a/www/www6/iesg/evaluation";
$WEB_DIR = "/a/www/www6";
$VERSION = "v6.0";

$LOCAL_CONST = "/dyn";

$ENV{"PROG_NAME"} = "idtracker.cgi";    #ENV Variable to be used by lib. files


if (defined($ENV{HTTP_USER_AGENT})) {   # Get the version of client browser
   my $user_agent = $ENV{HTTP_USER_AGENT};
   @version_temp = split ' ',$user_agent;
   $browser_version = $version_temp[0];
} else {
   $browser_version = "Unknown Version";
}
my $q = new CGI;
$program_name = $ENV{"PROG_NAME"};
$rUser = $ENV{REMOTE_USER};
$fColor = "7DC189";
$sColor = "CFE1CC";
$menu_fColor = "F8D6F8";
$menu_sColor = "E2AFE2";
$REC_DIR = "/a/www/www6s/messages-archive";
$AGENDA_PACK = "agenda-pack-old.txt";
$AGENDA_PACK_NEW = "agenda-pack.txt";
$private_txt = qq{<font color="red" size="-1">[private}; #Private Comment
$public_txt = qq{<font color="blue" size="-1">[public};  #Public Comment
$table_header = qq{<table cellpadding="1" cellspacing="0" border="0">
};
$table_header_640 = qq{<table cellpadding="1" cellspacing="0" border="0" width="640">
};
$TEST_MESSAGE = "This is a test message.\nPlease ignore this message.\n";
$IETF_EMAIL = "iesg-secretary\@ietf.org";

$TRACKER_URL="https://merlot.tools.ietf.org/cgi-bin/idtracker.cgi";


$SEC_TRACKER_URL="https://merlot.tools.ietf.org/cgi-bin/idtracker.cgi";


$TRACKER_PUB_URL="https://merlot.tools.ietf.org/";
$error_msg = qq{
<h2>There is a fatal error occured while processing your request</h2>
};


$TEST_MESSAGE = "" unless ($test_mode);
$TEST_EMAIL = "glenandmatt@ietf.org";
$CURRENT_DATE = "CURRENT_DATE"; # "TODAY" for Informix, "CURRENT_DATE" for MySQL
$CONVERT_SEED = 1; # To convert date format to fit into the current database engine
$ADMIN_MODE = 0;
my $html_txt;
$X_MAIL_HEADER = "X-idtracker: yes";
exit unless (init_database($db_name));
$dbh=get_dbh();
$telechat_date_list = get_telechat_date_list();

$loginid = db_select($dbh,"select id from iesg_login where login_name = '$rUser'") or error_log("select id from iesg_login where login_name = '$rUser'");
$loginid = $q->param("loginid") unless ($loginid);
my $user_level = db_select($dbh,"select user_level from iesg_login where id=$loginid") or error_log("select user_level from iesg_login where id=$loginid");
$ADMIN_MODE = 1 unless ($user_level);
$ADMIN_MODE = 0 unless ($loginid);
$AD_MODE = ($user_level==1)?1:0;
$form_header = qq{<form action="$program_name" method="POST" name="form1">
<input type="hidden" name="loginid" value="$loginid">
};
$form_header_noname = qq{<form action="$program_name" method="POST">
<input type="hidden" name="loginid" value="$loginid">
};
$form_header_search = qq{<form action="$program_name" method="POST" name="search_form">
<input type="hidden" name="loginid" value="$loginid">
};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">
<input type="hidden" name="loginid" value="$loginid">
};

$close_button = get_close_button($q); 
$user_name=get_mark_by($loginid);
$user_tag=db_select($dbh,"select person_or_org_tag from iesg_login where id=$loginid");
$user_email=get_email($user_tag);
$ENV{"USRE_NAME"} = $user_name;
my $devel_mode_txt = "";
$devel_mode_txt = "<h2>Testing Mode</h2>" if ($test_mode);
$devel_mode_txt .= "<h2>Development Mode</h2>loginid : $loginid<br>db: $db_name<br>" if ($devel_mode);
my $prepend_title = "";
$prepend_title = "[TEST VERSION]" if ($test_mode);
my $title_text = "$prepend_title IESG I-D Tracker $VERSION -- $browser_version";
$title_text ="$prepend_title IESG I-D Tracker --" . uc($q->param("command")) if (defined($q->param("command")));
$replaces_ids_list = ",";
my @repList = db_select_multiple($dbh,"select replaced_by from internet_drafts where replaced_by > 0 group by replaced_by");
for my $array_ref (@repList) {
  my ($id) = @$array_ref;
  $replaces_ids_list .="$id,";
}

$html_top = qq{
<html>
<HEAD><TITLE>$title_text (NSS)</title>
<STYLE TYPE="text/css">
<!--

          TD {text-decoration: none; color: #000000; font: 9pt arial;}
          A:Link {color: #0000ff; text-decoration:underline}
          A:Hover {color: #ff0000; text-decoration:underline}
      A:visited {color: #0000ff; text-decoration:underline}
          #largefont {font-weight: bold; color: #000000; font: 18pt arial}
          #largefont2 {font-weight: bold; color: #000000; font: 16pt arial}
          #largefont_red {font-weight: bold; color: #ff0000; font: 16pt arial}
-->
</STYLE>

</head>
<body link="blue" vlink="blue">
$devel_mode_txt
};
my $additional_link = "";
$additional_link = qq{<a href="http://www.ietf.org/iesg/internal/dyn/mod-pack.rtf">[Telechat Agenda Package (Word)]</a> <a href="http://www.ietf.org/iesg/internal/dyn/agenda_summary.rtf">[Telechat Agenda Summary] (Word)</a>} if ($ADMIN_MODE);
$html_bottom = qq{
<!-- begin new footer -->
<HR>
<A HREF="https://www.ietf.org/iesg/internal/agenda.html">[Telechat Agenda (Web)]</a>
<p>
<A HREF="https://www.ietf.org/iesg/internal/dyn/agenda.txt">[Telechat Agenda (Text)]</a>
<p>
<A HREF="https://www.ietf.org/iesg/internal/dyn/agenda-pack.txt">[Telechat Agenda Package (Text)]</a> $additional_link
<p>
<i>This page produced by the <A HREF="mailto:iesg-secretary\@ietf.org">IETF Secretariat</a> 
for the <A HREF="mailto:iesg\@ietf.org">IESG</A></i>
<p>
</body>
</html>
};
my $html_body = get_html_body($q);
#Main body of HTML
$dbh->disconnect();
print <<END_HTML;
Content-type: text/html
$html_top
$html_body
$html_bottom
END_HTML

sub get_close_button {
  my $q=shift;
  my $id_document_tag = $q->param("id_document_tag");
  my $ballot_id = $q->param("ballot_id");
  return 0 unless (my_defined($id_document_tag) or my_defined($ballot_id));
  $id_document_tag = db_select($dbh,"select id_document_tag from id_internal where ballot_id=$ballot_id and primary_flag=1") unless (my_defined($id_document_tag));
  my $where_clause = "";
  if (my_defined($id_document_tag)) {
    $where_clause = "id_document_tag = $id_document_tag";
  } elsif (my_defined($ballot_id)) {
    $where_clause = "ballot_id = $ballot_id";
  } else {
    return "";
  }
  my ($id_document_tag,$rfc_flag,$ballot_id) = db_select($dbh,"select id_document_tag,rfc_flag,ballot_id from id_internal where $where_clause");
  return qq{
  $form_header
  <input type="hidden" name="command" value="view_id">
  <input type="hidden" name="dTag" value="$id_document_tag">
  <input type="hidden" name="rfc_flag" value="$rfc_flag">
  <input type="hidden" name="ballot_id" value="$ballot_id">
  <input type="submit" value="Back to I-D">
  </form>
};
}


###########################################
#
#  Function : get_html_body
#  parameters:
#    $q : main cgi variable
#  result : body of HTML text
#
#  get_html_body calls appropriate function to generate the body of HTML.
#  get_html_body calls functions based on "command" cgi variable
#
########################################### 
sub get_html_body {
   my $q = shift;   # CGI variable
   my $command = $q->param("command");
   my $switch = "-deploy";
   my $html_txt;
   if ($command ne "open_ballot" and $command ne "view_comment" and $command ne "update_ballot" and $command ne "view_update_ballot_comment" and $command ne "update_ballot_comment_db" and $command ne "ballot_writeup" and $command ne "ballot_writeup_db" and $command ne "view_writeup"and $command ne "approve_ballot" and $command ne "approve_ballot_db" and $command ne "print_ballot" and $command ne "view_state_desc" and $command ne "toggle_default_search" and $command ne "make_last_call" and $command ne "make_last_call_pre") {
      my $user_level = db_select($dbh,"select user_level from iesg_login where id=$loginid")  or error_log("select user_level from iesg_login where id=$loginid");
      if ($ADMIN_MODE) {
         my $admin_menu = get_admin_menu($q);
         $html_top .= qq {
$admin_menu
};
      }
      else {
        if ($command eq "main_menu" or !my_defined($command)) {
             $html_top .= qq{
<center><font color="red">
<h1>IESG Data Tracker</h1></font>
$table_header
<tr>
$form_header_noname
<td colspan="2">
   <input type="hidden" name="command" value="gen_agenda">
   <input type="submit" value="        Documents on upcoming agenda(s)           "></center>
</td>
</form>
</tr></table>
};
       }
     }
   }
   unless (my_defined($command)) { # If no command passed, display login screen
      return main_menu();
   }
   elsif ($command eq "search_list") { # Display Search page
      if (defined($q->param("search_button"))) {
	     $html_txt = search_list ($q);
	  } elsif (defined($q->param("add_button"))) {
	     $html_txt = add_id_search ($q);
	  }
      
   }
   elsif ($command =~ /main_menu|view_comment|open_ballot|view_update_ballot_comment|update_ballot|ballot_writeup|notify|view_writeup|approve_ballot|print_ballot|view_state_desc|toggle_default_search|make_last_call/) {
     my $func = "${command}(\$q)";
     return eval($func);
   } elsif ($command eq "action") {
      $script_name = $q->param("cat");
      system ("$SOURCE_DIR/gen_${script_name}_html.pl $switch");
      #unless ($devel_mode) {
      #  chdir $INTERNAL_DIR;
      #  system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa $INTERNAL_DIR/agenda.html ietf\@stiedprstage1:$INTERNAL_DIR/agenda.html";
      #  system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa $INTERNAL_DIR/agenda.txt ietf\@stiedprstage1:$INTERNAL_DIR/agenda.txt";
      #  system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa $INTERNAL_DIR/PWG.html ietf\@stiedprstage1:$INTERNAL_DIR/PWG.html";
      #}
      $func = "gen_${script_name}(\$q)";
      chdir "$EVAL_DIR" if ($script_name eq "ballot");
      $html_txt .= eval($func);
   } elsif ($q->param("command") eq "edit_delete") {
      $gID = $q->param("gID");
	  if (defined($q->param("delete"))) {
		 db_update($dbh,"delete from group_internal where group_acronym_id = $gID",$program_name,$user_name);
		 $html_txt .= gen_pwg($q);
      } elsif (defined($q->param("edit"))) {
	     $html_txt .= edit_pwg($q);
	  }
   } elsif ($q->param("command") eq "add_delete_pwg") {
      if (defined($q->param("delete"))) {
	     $html_txt .= delete_pwg($q->param("filename"));
	  } else {
         $html_txt .= add_pwg($q)
      }
   } elsif ($q->param("command") eq "add_db") {
      $html_txt .= add_db($q);
   } elsif ($q->param("command") eq "edit_db") {
      $html_txt .= edit_db($q);
   }
   else { # Generate a page depends on "command"
      my $func = "${command}(\$q)";
	  $html_txt = eval($func);
   }

# Display footer with "main" and "go back" button
   $html_txt .= qq {
   $form_header
   <input type="hidden" name="command" value="main_menu">
   <input type="submit" value="Main Menu">
   <input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true">
   </form>
   };
   return $html_txt;
}
sub get_sqlStr_for_each_agenda {
  my $agenda_cat_id=shift;
  my $telechat_date=shift;
  my $for_rfc=shift;
  my $my_position=shift;
  my $sqlStr="";
  if (my_defined($my_position) and $my_position ne "no_record") {
    $sqlStr = ($for_rfc)?"select a.ballot_id from id_internal a, rfcs b, ballots c where rfc_flag=1 and a.id_document_tag=b.rfc_number and a.ballot_id=c.ballot_id and $my_position=1 and ad_id=$loginid ":"select a.ballot_id from id_internal a, internet_drafts b, ballots c where a.id_document_tag=b.id_document_tag and rfc_flag=0 and a.ballot_id=c.ballot_id and $my_position=1 and ad_id=$loginid ";
  } else {
    $sqlStr = ($for_rfc)?"select ballot_id from id_internal a, rfcs b where rfc_flag=1 and a.id_document_tag=b.rfc_number ":"select ballot_id from id_internal a, internet_drafts b where a.id_document_tag=b.id_document_tag and rfc_flag=0 ";
  }
  $sqlStr .= "and cur_state < 27 and primary_flag=1 ";
  $sqlStr .= " and agenda=1 and telechat_date='$telechat_date' " if my_defined($telechat_date);
  if ($agenda_cat_id < 7) { #Protocol Action
    $sqlStr .= ($for_rfc)?"and intended_status_id in (1,2,3,7) ":"and intended_status_id in (1,2,6,7) ";
  } else { #Document Action
    $sqlStr .= ($for_rfc)?"and intended_status_id in (4,5) ":"and intended_status_id in (3,4,5) ";
    if ($agenda_cat_id < 13 and $agenda_cat_id > 9) { #Via AD
      $sqlStr .= "and via_rfc_editor=0 ";
    } elsif ($agenda_cat_id > 12) {#Via RFC Editor
      $sqlStr .= "and via_rfc_editor=1 ";
    }
  }
  if ($agenda_cat_id==1 or $agenda_cat_id==2 or $agenda_cat_id==3 or $agenda_cat_id==7 or $agenda_cat_id==8 or $agenda_cat_id==9) { #WG Submission
    $sqlStr .= ($for_rfc)?"and group_acronym <> 'none' ":"and group_acronym_id <> 1027 ";
  } else { #INDIVIDUAL SUBMISSION
    $sqlStr .= ($for_rfc)?"and group_acronym = 'none' ":"and group_acronym_id = 1027 ";
  }
   if ($agenda_cat_id==1 or $agenda_cat_id==4 or $agenda_cat_id==7 or $agenda_cat_id==10 or $agenda_cat_id==13) { #New Item
    $sqlStr .= " and returning_item=0 ";
  } else { #Returning Item
    $sqlStr .= " and returning_item=1 ";
  }
  if ($agenda_cat_id==3 or $agenda_cat_id==6 or $agenda_cat_id==9 or $agenda_cat_id==15 or $agenda_cat_id==12) { #For Action
    $sqlStr .= "and (cur_state < 16 or cur_state > 21) ";
  } else { #Regular Item
    $sqlStr .= "and cur_state >= 16 and cur_state <= 21 ";
  }
  return $sqlStr;
}
  
sub get_ballots_list {
  my $telechat_date=shift;
  my $my_position=shift;
  $MAX_AGENDA_NUM = 15;
  my $ret_val = "";
  for ($agenda_cat_id=1;$agenda_cat_id<=$MAX_AGENDA_NUM;$agenda_cat_id++) {
    my $heading = db_select($dbh,"select agenda_cat_value from agenda_cat where agenda_cat_id=$agenda_cat_id");
    $heading =~ s/(\d)(.*)\n(\d\.\d)(.*)\n(\d\.\d\.\d)(.*)/$5 $2\/$4\/$6/;
    $heading =~ s/\n//g;
    my $sqlStr_id = get_sqlStr_for_each_agenda($agenda_cat_id,$telechat_date,0,$my_position);
    my $sqlStr_rfc = get_sqlStr_for_each_agenda($agenda_cat_id,$telechat_date,1,$my_position);
#return "$sqlStr_id <br>$sqlStr_rfc<br>\n";
    my @List_id = db_select_multiple($dbh,$sqlStr_id);
    my @List_rfc = db_select_multiple($dbh,$sqlStr_rfc);
    next if ($#List_id+$#List_rfc == -2);
    $ret_val .= qq{<tr bgcolor="#F8F8FF"><td colspan="7"><b><font size= +1>$heading</font></b></td></tr>
};
#$ret_val .= "<tr><td colspan=\"7\">id:$agenda_cat_id $sqlStr_id</td></tr>\n";next;
    for my $array_ref (@List_id) {
      my ($ballot_id) = @$array_ref;
      $ret_val .= get_my_ballot_list($ballot_id,$loginid,$my_position) if ($ballot_id); 
    }
    for my $array_ref (@List_rfc) {
      my ($ballot_id) = @$array_ref;
      $ret_val .= get_my_ballot_list($ballot_id,$loginid,$my_position) if ($ballot_id); 
    }
  }

  return $ret_val;
}

sub get_my_ballot_list {
  my $ballot_id=shift;
  my $ad_id=shift;
  my $my_position=shift;
  my ($id_document_tag,$rfc_flag)=db_select($dbh,"select id_document_tag,rfc_flag from id_internal where ballot_id=$ballot_id and primary_flag=1");
  my ($yes_col,$no_col,$abstain,$discuss,$recuse) = db_select($dbh,"select yes_col,no_col,abstain,discuss,recuse from ballots where ballot_id=$ballot_id");
  my ($my_yes_col,$my_no_col,$my_abstain,$my_discuss,$my_recuse) = db_select($dbh,"select yes_col,no_col,abstain,discuss,recuse from ballots where ballot_id=$ballot_id and ad_id=$ad_id");
  my $bgcolor=($my_yes_col+$my_no_col+$my_abstain+$my_recuse == 0 and $my_discuss < 1)?"#FAFAD2":"#B3FF99";
  my $ret_val = "<tr bgcolor=\"$bgcolor\">";
  my $ballot_count = db_select($dbh,"select count(id_document_tag) from id_internal where ballot_id=$ballot_id");
  my $filename_set = get_filename_set($ballot_id,6);
  chop($filename_set); chop($filename_set); chop($filename_set); chop($filename_set); chop($filename_set); 
  $filename_set .= "</a>";
  my $links = "<a href=\"$program_name?command=open_ballot&id_document_tag=$id_document_tag\">[bal]</a> <a href=\"$program_name?command=view_id&dTag=$id_document_tag&rfc_flag=$rfc_flag\">[detail]</a>";
  if ($ballot_count > 1) {
    $ret_val .= "<td nowrap=\"yes\"><li> $ballot_count documents ballot $links<br>\n$filename_set</td>\n";
  } else {
    $ret_val .= "<td nowrap=\"yes\">$filename_set $links</td>\n";
  }
  my $not_recorded_selected = ">";
  my $yes_col_selected = ">";
  my $no_col_selected = ">";
  my $abstain_col_selected = ">";
  my $recuse_col_selected = ">";
  my $discuss_col_selected = ">";
  my $iesg_count = db_select($dbh,"select count(*) from iesg_login where user_level=1");
  $iesg_count--;
  my $yes_col_count=db_select($dbh,"select count(*) from ballots where ballot_id=$ballot_id and yes_col=1");
  my $no_col_count=db_select($dbh,"select count(*) from ballots where ballot_id=$ballot_id and no_col=1");
  my $abstain_col_count=db_select($dbh,"select count(*) from ballots where ballot_id=$ballot_id and abstain=1");
  my $discuss_col_count=db_select($dbh,"select count(*) from ballots where ballot_id=$ballot_id and discuss=1");
  my $recuse_col_count=db_select($dbh,"select count(*) from ballots where ballot_id=$ballot_id and recuse=1");
  my $not_recorded_count=$iesg_count-$yes_col_count-$no_col_count-$discuss_col_count-$abstain_col_count-$recuse_col_count;
  my $xmark = "<font color=\"red\"><b>X</b></font>";
  if ($my_yes_col) {
	  $yes_col_selected="checked>$xmark ";
  } elsif ($my_no_col) {
	  $no_col_selected="checked>$xmark";
  } elsif ($my_abstain) {
	  $abstain_col_selected="checked>$xmark";
  } elsif ($my_discuss==1) {
	  $discuss_col_selected="checked>$xmark";
  } elsif ($my_recuse) {
	  $recuse_col_selected="checked>$xmark";
  } else {
	  $not_recorded_selected="checked>$xmark";
  }
  return "" if ($my_position eq "no_record" and $not_recorded_selected eq ">");
  $ret_val .= qq{<td><input type="radio" name="$ballot_id" value="not_recorded" $not_recorded_selected ($not_recorded_count)</td>
<td><input type="radio" name="$ballot_id" value="yes_col" $yes_col_selected ($yes_col_count)</td>  
<td><input type="radio" name="$ballot_id" value="no_col" $no_col_selected ($no_col_count)</td>  
<td><input type="radio" name="$ballot_id" value="discuss" $discuss_col_selected ($discuss_col_count)</td>  
<td><input type="radio" name="$ballot_id" value="abstain" $abstain_col_selected ($abstain_col_count)</td>  
<td><input type="radio" name="$ballot_id" value="recuse" $recuse_col_selected ($recuse_col_count)</td>  
};
  return $ret_val;
}
sub my_ballot_page {
  my $q=shift;
  my $telechat_date=$q->param("telechat_date");
  my $my_position=$q->param("my_position");
  my $my_pos_up=$my_position;
  if (my_defined($my_pos_up)) {
    $my_pos_up =~ s/yes_col/yes/g;
    $my_pos_up =~ s/no_col/no objection/g;
    $my_pos_up =~ s/no_record/no record/g;
    $my_pos_up = uc($my_pos_up);
  }
  my $writeup_list = "";
  my $all_ballots=qq{
$form_header_post
<input type="hidden" name="command" value="update_all_positions">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="my_position" value="$my_position">
};
  if ($telechat_date eq "all") {
    my $next_telechat_date = "";
    my $heading = (my_defined($my_pos_up))?"Ballots with $my_pos_up":"Position list";
    my $sqlStr = (my_defined($my_pos_up) and $my_position ne "no_record")?"select rfc_flag,filename, a.id_document_tag,a.ballot_id from id_internal a, internet_drafts b, ballots c where a.id_document_tag=b.id_document_tag and primary_flag=1 and a.ballot_id=c.ballot_id and $my_position=1 and ad_id=$loginid order by filename":"select rfc_flag,filename, a.id_document_tag,a.ballot_id from id_internal a, internet_drafts b where a.id_document_tag=b.id_document_tag and primary_flag=1 order by filename";
    my @List = db_select_multiple($dbh,$sqlStr);
    my $ballots_list = get_ballots_list($next_telechat_date,$my_position);
    next unless my_defined($ballots_list);
    for my $array_ref (@List) {
      my ($rfc_flag,$filename,$id_document_tag,$ballot_id) = @$array_ref;
      my $filename_set = get_filename_set($ballot_id,1);
      $filename_set =~ s/\.txt//g;
      my ($ballot_writeup,$approval_text) = db_select($dbh,"select ballot_writeup,approval_text from ballot_info where ballot_id=$ballot_id");         ($ballot_writeup,$approval_text) = html_bracket($ballot_writeup,$approval_text);
                                                                                   
      $writeup_list .= qq{<a name="$filename"></a>
<h1>$filename_set</h1>
<a href="$program_name?command=open_ballot&id_document_tag=$id_document_tag">[ballot]</a>
<a href="$program_name?command=view_id&dTag=$id_document_tag&rfc_flag=$rfc_flag">[I-D Detail]</a>
<a href="#top">[return to top]</a>
<h2>Ballot Writeup</h2>
<pre>
$ballot_writeup
</pre>
<h2>Approval Text</h2>
<pre>
$approval_text
</pre>
};
    }
    $all_ballots .= qq{<a name="top"></a>
<h1>$heading for $user_name</h1>
<table border="1">
<tr>
<th>&nbsp;</th>
<th width="110">Not Recorded</th>
                                                                                     
<th width="110">Yes</th>
<th width="110">No Objection</th>
<th width="110">Discuss</th>
<th width="110">Abstain</th>
<th width="110">Recuse</th>
</tr>
$ballots_list
</table>
<hr>
};
  } else {
    my @telechatDates = ($telechat_date eq "any")?db_select($dbh,"select date1,date2,date3,date4 from telechat_dates"):($telechat_date);
    for my $next_telechat_date (@telechatDates) {
      my $heading = (my_defined($my_pos_up))?"Ballots with $my_pos_up":"Position list";
      my $sqlStr = (my_defined($my_pos_up) and $my_position ne "no_record")?"select rfc_flag,filename, a.id_document_tag,a.ballot_id from id_internal a, internet_drafts b, ballots c where a.id_document_tag=b.id_document_tag and primary_flag=1 and telechat_date='$next_telechat_date' and a.ballot_id=c.ballot_id and $my_position=1 and ad_id=$loginid order by filename":"select rfc_flag,filename, a.id_document_tag,a.ballot_id from id_internal a, internet_drafts b where a.id_document_tag=b.id_document_tag and primary_flag=1 and telechat_date='$next_telechat_date' order by filename";
    
      my @List = db_select_multiple($dbh,$sqlStr);
      my $ballots_list = get_ballots_list($next_telechat_date,$my_position);
      next unless my_defined($ballots_list);
      for my $array_ref (@List) {
        my ($rfc_flag,$filename,$id_document_tag,$ballot_id) = @$array_ref;
        my $filename_set = get_filename_set($ballot_id,1);
        $filename_set =~ s/\.txt//g;
        my ($ballot_writeup,$approval_text) = db_select($dbh,"select ballot_writeup,approval_text from ballot_info where ballot_id=$ballot_id");
        ($ballot_writeup,$approval_text) = html_bracket($ballot_writeup,$approval_text);
      
        $writeup_list .= qq{<a name="$filename"></a>
<h1>$filename_set</h1>
<a href="$program_name?command=open_ballot&id_document_tag=$id_document_tag">[ballot]</a> 
<a href="$program_name?command=view_id&dTag=$id_document_tag&rfc_flag=$rfc_flag">[I-D Detail]</a> 
<a href="#top">[return to top]</a>
<h2>Ballot Writeup</h2>
<pre>
$ballot_writeup
</pre>
<h2>Approval Text</h2>
<pre>
$approval_text
</pre>
};
      }
      $all_ballots .= qq{<a name="top"></a>
<h1>$heading for $user_name for $next_telechat_date telechat</h1>
<table border="1">
<tr>
<th>&nbsp;</th>
<th width="110">Not Recorded</th>

<th width="110">Yes</th>
<th width="110">No Objection</th>
<th width="110">Discuss</th>
<th width="110">Abstain</th>
<th width="110">Recuse</th>
</tr>
$ballots_list
</table>
<hr>
};
    }
  }
  return qq{
$all_ballots
<input type="submit" value=" Update All Positions ">
</form>
   $form_header
   <input type="hidden" name="command" value="main_menu">
   <input type="submit" value="Main Menu">
   <input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true">
   </form>
<hr>
$writeup_list
};
}
sub to_update_discuss_comment {
  my $q=shift;
  my $result_list = $q->param("result_list");
  my $telechat_date=$q->param("telechat_date");
  my $my_position=$q->param("my_position");
  my @idList = split ',',$result_list;
  my $discuss_id_list = "";
  for (@idList) {
    my @eachItem=split '-';
    my $id_document_tag=$eachItem[0];
    my $rfc_flag=$eachItem[1];
    my $ballot_id=$eachItem[2];
    my $doc_name="";
    if ($rfc_flag) {
      $doc_name = "rfc$id_document_tag";
    } else {
      $doc_name = db_select($dbh,"select filename from internet_drafts where id_document_tag=$id_document_tag");
    }
    $firstname=get_mark_by($loginid);
    $discuss_id_list .= "<a href=\"$program_name?command=view_update_ballot_comment&id_document_tag=$id_document_tag&ad_id=$loginid&ballot_id=$ballot_id&filename=$doc_name&firstname=$firstname&edit_discuss_comment=1&result_list=$result_list&telechat_date=$telechat_date&my_position=$my_position\">$doc_name</a> <br>\n";
  }
  return qq{
<h3>You have marked <i>discuss</i> position for following document(s).<br>
Please add or edit your discuss comment</h3>
$discuss_id_list
<br><br>
<a href="$program_name?command=my_ballot_page&telechat_date=$telechat_date&my_position=$my_position">Back to My Ballots</a><br>
};
}

sub update_all_positions {
  my $q=shift;
  my $telechat_date=$q->param("telechat_date");
  my $my_position=$q->param("my_position");
  foreach ($q->param) {
    next if (/-/);
    if (/^\d/) {
      my $ballot_id = $_;
      my $value=$q->param("$ballot_id");
      return $error_msg unless do_update_single_ballot($ballot_id,$loginid,$value);
    }
  }
  my ($date1,$date2,$date3,$date4) = db_select($dbh,"select date1,date2,date3,date4 from telechat_dates");
  my $next_telechat_date=($telechat_date eq "all")?"'$date1','$date2','$date3','$date4'":"'$telechat_date'";
  my @List = db_select_multiple($dbh,"select id_document_tag,a.ballot_id,rfc_flag from id_internal a, ballots b where b.discuss=1 and b.ad_id=$loginid and a.ballot_id=b.ballot_id and primary_flag=1 and telechat_date in ($next_telechat_date)");
  my $discuss_list = ($#List < 0)?"":"<h3>You have marked <i>discuss</i> position for following document(s).<br>Please add or edit your discuss comment</h3>\n";
  my $result_list = "";
  for my $array_ref (@List) {
    my ($id_document_tag,$ballot_id,$rfc_flag) = @$array_ref;
    $result_list .= "$id_document_tag-$rfc_flag-$ballot_id,";
  }
  chop($result_list) if my_defined($result_list);  
  for my $array_ref (@List) {
    my ($id_document_tag,$ballot_id,$rfc_flag) = @$array_ref;
    my $doc_name="";
    if ($rfc_flag) {
      $doc_name = "rfc$id_document_tag";
    } else {
      $doc_name = db_select($dbh,"select filename from internet_drafts where id_document_tag=$id_document_tag");
    }
    $firstname=get_mark_by($loginid);
    $discuss_list .= "<a href=\"$program_name?command=view_update_ballot_comment&id_document_tag=$id_document_tag&ad_id=$loginid&ballot_id=$ballot_id&filename=$doc_name&firstname=$firstname&edit_discuss_comment=1&telechat_date=$telechat_date&result_list=$result_list&my_position=$my_position\">$doc_name</a> <br>\n";
  }

  
     my $ad_id = $q->param("ad_id");
   my $ballot_id = $q->param("ballot_id");
   my $rfc_flag = db_select($dbh,"select rfc_flag from id_internal where ballot_id=$ballot_id and primary_flag=1");
   my $filename = $q->param("filename");
   my $firstname = $q->param("firstname");
   my $id_document_tag = $q->param("id_document_tag");


   
  return qq{
<h2>Update was sucessfull</h2>
<a href="$program_name?command=my_ballot_page&telechat_date=$telechat_date&my_position=$my_position">Back to My Ballots Page</a><br>
$discuss_list
<Br><br>
};
}

sub gen_telechat_dates {
  my ($date1,$date2,$date3,$date4) = db_select($dbh,"select date1,date2,date3,date4 from telechat_dates") or error_log("select date1,date2,date3,date4 from telechat_dates");
  my $date1_not_thursday = "";
  my $date2_not_thursday = "";
  my $date3_not_thursday = "";
  my $date4_not_thursday = "";
  $date1_not_thursday = "<b><font color=\"red\">NOT THURSDAY</font></b>" unless ((db_select($dbh,"select dayofweek('$date1')"))==5);
  $date2_not_thursday = "<b><font color=\"red\">NOT THURSDAY</font></b>" unless ((db_select($dbh,"select dayofweek('$date2')"))==5);
  $date3_not_thursday = "<b><font color=\"red\">NOT THURSDAY</font></b>" unless ((db_select($dbh,"select dayofweek('$date3')"))==5);
  $date4_not_thursday = "<b><font color=\"red\">NOT THURSDAY</font></b>" unless ((db_select($dbh,"select dayofweek('$date4')"))==5);
  my $html_txt = qq{
<h2>Telechat Dates</h2>
$form_header_search
<input type="hidden" name="command" value="update_telechat_dates">
<b>
Date1: <input type="text" name="date1" value="$date1"> $date1_not_thursday<br>
Date2: <input type="text" name="date2" value="$date2"> $date2_not_thursday<br>
Date3: <input type="text" name="date3" value="$date3"> $date3_not_thursday<br>
Date4: <input type="text" name="date4" value="$date4"> $date4_not_thursday<br>
<br>
<input type="submit" value="Update"><input type="reset" value="Reset">
</form>
$form_header_search
<input type="hidden" name="command" value="rollup_telechat_dates">
<input type="submit" value="    Roll Up    ">
</form>
<br><br><br>
};

return $html_txt;
}

sub update_telechat_dates {
  my $q = shift;
  my $date1 = $q->param("date1");
  my $date2 = $q->param("date2");
  my $date3 = $q->param("date3");
  my $date4 = $q->param("date4");
  db_update($dbh,"update telechat_dates set date1='$date1', date2='$date2', date3='$date3', date4='$date4'",$program_name,$user_name);
  my $html_txt = "<h2>Update was successful</h2>\n";
  $html_txt .= gen_telechat_dates();
  return $html_txt;
}

sub rollup_telechat_dates {
  my ($date1,$date2,$date3) = db_select($dbh,"select date2,date3,date4 from telechat_dates") or error_log("select date2,date3,date4 from telechat_dates");
  my $date4 = db_select($dbh,"select date_add('$date3',interval 14 day)") or error_log("select date_add('$date3',interval 14 day)");
  db_update($dbh,"update telechat_dates set date1='$date1', date2='$date2', date3='$date3', date4='$date4'",$program_name,$user_name);
  my $html_txt = "<h2>Update was successful</h2>\n";
  $html_txt .= gen_telechat_dates();
  return $html_txt;
}

sub error_log {
  return 0;
}



###################################################
# Function: get_admin_menu
###################################################
sub get_admin_menu {
   my $q=shift;
   my $command=$q->param("command");
   my $id_document_tag = $q->param("dTag");
   my $resurrect_button = "";
   if ($command eq "view_id" or $command eq "add_id") {
     my $requested = db_select($dbh,"select resurrect_requested_by from id_internal where id_document_tag=$id_document_tag") or error_log("select resurrect_requested_by from id_internal where id_document_tag=$id_document_tag");
     if ($requested > 0) { 
       $resurrect_button = qq{$form_header<td><input type="hidden" name="command" value="do_resurrect">
<input type="hidden" name="id_document_tag" value="$id_document_tag">
<input type="submit" value = "  Resurrection Completed  "></td></form>
};
     }
   }
   my $html_txt = qq {
   <center>
   $table_header
   <tr>
   $form_header
   <td>
   <input type="hidden" name="command" value="gen_agenda">
   <input type="submit" value="Documents on upcoming agenda(s)">
   </td>
   </form>

   $form_header
   <td>
   <input type="hidden" name="command" value="gen_pwg">
   <input type="submit" value="         WG Actions          ">
   </td>
   </form>

   $form_header
   <td>
   <input type="hidden" name="command" value="gen_template">
   <input type="submit" value="Templates">
   </td>
   </form>

   $form_header
   <td>
   <input type="hidden" name="command" value="import_ballots">
   <input type="submit" value="Update All files for Agenda Packet">
   </td>
   </form>
</tr><tr>
   $form_header
   <td>
   <input type="hidden" name="command" value="gen_agenda_package">
   <input type="submit" value="Auto Agenda Package">
   </td>
   </form>
   $form_header
   <td>
   <input type="hidden" name="command" value="gen_telechat_dates">
   <input type="submit" value="      Telechat Dates        ">
   </td>
   </form>
$resurrect_button
   </tr>
   </table>
   </center>
   };
   return $html_txt;
   
}


sub gen_agenda_package {
  my $months_option = qq {
<option value="January">January</option>
<option value="February">Feburary</option>
<option value="March">March</option>
<option value="April">April</option>
<option value="May">May</option>
<option value="June">June</option>
<option value="July">July</option>
<option value="August">August</option>
<option value="September">September</option>
<option value="October">October</option>
<option value="November">November</option>
<option value="December">December</option>
};
  my $days_option = "";
  for ($loop=1;$loop<32;$loop++) {
    $days_option .= qq {  <option value="$loop">$loop</option>
};
  }
  my $years_option = "";
  for ($loop=2005;$loop<2020;$loop++) {
    my $selected = ($loop == 2006)?"selected":"";
    $years_option .= qq {  <option value="$loop" $selected>$loop</option>
};
  }
  my $current_outstanding_tasks = "";
  my @List = db_select_multiple($dbh,"select id,item_text,done from outstanding_tasks order by done") or error_log("select id,item_text,done from outstanding_tasks order by done");
  for $array_ref (@List) {
    my ($id,$item_text,$done) = rm_tr(@$array_ref);
    my $checked = numtocheck($done);
    $current_outstanding_tasks .= qq {
$form_header
<input type="hidden" name="command" value="update_outstanding">
<input type="hidden" name="id" value="$id">
<li> <input type="text" size="70" maxsize="250" name="item_text" value="$item_text">
 Done? <input type="checkbox" name="done" $checked>
<input type="submit" value="Update">
</form>
<br>
};
  }
  my $html_txt = qq {
<br><h2>Agenda Package</h2><br>
$form_header
<input type="hidden" name="command" value="gen_agenda_system">
<b>Agenda for:</b>
<select name="agenda_month">
$months_option
</select>
<select name="agenda_day">
$days_option
</select>,
<select name="agenda_year">
$years_option
</select>
<br>
<b>Approval Date of Minute:</b>
<select name="minute_month">
$months_option
</select>
<select name="minute_day">
$days_option
</select>,
<select name="minute_year">
$years_option
</select>
<br>
Send Prelimiary Agenda to iesg-agenda-dist\@ietf.org <input type="checkbox" name="prelim">
<br><br>
<input type="submit" value="Generate Package">
</form>
<hr>
<h2>Outstanding Tasks</h2>
$current_outstanding_tasks
<br>
$form_header
<input type="hidden" name="command" value="new_outstanding">
<li> <input type="text" size="70" maxsize="250" name="item_text">
<input type="submit" value="Add new Outstanding Task Item">
</form>
<br><br>
};

  return $html_txt;
}

sub gen_agenda_system {
  my $q = shift;
  my $agenda_month = $q->param("agenda_month");
  my $agenda_day = $q->param("agenda_day");
  my $agenda_year = $q->param("agenda_year");
  my $minute_month = $q->param("minute_month");
  my $minute_day = $q->param("minute_day");
  my $minute_year = $q->param("minute_year");
  my $agenda_date = "$agenda_month $agenda_day, $agenda_year";
  my $minute_date = "$minute_month $minute_day, $minute_year";
#  open (OUTFILE,">$REC_DIR/$AGENDA_PACK");
#  print OUTFILE qq {From: IESG Secretary <iesg-secretary\@ietf.org>
#To:iesg\@ietf.org
#Cc:barbara.fuller\@neustar.biz, amy.vezza\@neustar.biz
#Subject:Agenda and Package for $agenda_date Telechat
#
#
#};
#  close OUTFILE;
  open (OUTFILE2,">$INTERNAL_DIR/$LOCAL_CONST/$AGENDA_PACK_NEW");
  print OUTFILE2 qq{From: IESG Secretary <iesg-secretary\@ietf.org>
To: iesg\@ietf.org
Cc: avezza\@amsl.com, tme\@multicasttech.com, spencerdawkins\@mcsr-labs.org, marc.blanchet\@viagenie.ca
Subject:Agenda and Package for $agenda_date Telechat

};
  close OUTFILE2;

#  system "$SOURCE_DIR/gen_agenda_text.pl \"$agenda_date\" \"$minute_date\" >> $REC_DIR/$AGENDA_PACK";
#  system "cat $INTERNAL_DIR/MINUTES.txt >> $REC_DIR/$AGENDA_PACK";



 ## Uncomment following line after convert all ballot to web ballot ##
#  system "cat $INTERNAL_DIR/all_ballots.txt >> $REC_DIR/$AGENDA_PACK";



#  $sqlStr = qq{
#select ballot_id,filename from id_internal a, internet_drafts b
#where primary_flag = 1 and agenda=1 and
#a.id_document_tag = b.id_document_tag and
#b.intended_status_id in  (1,2,6,7)
#}; 
#  my @balList = db_select_multiple($dbh,$sqlStr);
#  for $array_ref (@balList) {
#    my ($ballot_id,$filename) = rm_tr(@$array_ref);
#    open (OUTFILE,">>$REC_DIR/$AGENDA_PACK");
#    print OUTFILE "\n\n";
#    close OUTFILE;
#    system "$SOURCE_DIR/gen_ballot_text.pl $ballot_id >> $REC_DIR/$AGENDA_PACK";
#  }
  system "$SOURCE_DIR/gen_agenda_summary.pl \"$agenda_date\" >> $INTERNAL_DIR/$LOCAL_CONST/$AGENDA_PACK_NEW";
  open (OUTFILE3,">>$INTERNAL_DIR/$LOCAL_CONST/$AGENDA_PACK_NEW");
  print OUTFILE3 qq{
------------------------------------------------------------------------------

};
  close OUTFILE3;
#  system "$SOURCE_DIR/gen_agenda_packet.pl \"$agenda_date\" >> $INTERNAL_DIR/$AGENDA_PACK_NEW";
#  system "$SOURCE_DIR/gen_agenda_summary_rtf.pl \"$agenda_date\" > $INTERNAL_DIR/agenda_summary.rtf";
#  system "$SOURCE_DIR/gen_agenda_packet_rtf.pl \"$agenda_date\" > $INTERNAL_DIR/agenda_pack.rtf";


  system "$SOURCE_DIR/gen_agenda_packet.pl \"$agenda_date\" >> $INTERNAL_DIR/$LOCAL_CONST/$AGENDA_PACK_NEW";
  system "$SOURCE_DIR/gen_agenda_summary_rtf.pl \"$agenda_date\" > $INTERNAL_DIR/$LOCAL_CONST/agenda_summary.rtf";
  system "$SOURCE_DIR/gen_agenda_packet_rtf.pl \"$agenda_date\" > $INTERNAL_DIR/$LOCAL_CONST/mod-pack.rtf";


  if (defined($q->param("prelim"))) {
    my $agenda_html=`cat $WEB_DIR/iesg/internal/agenda.html`;
    #my $agenda_text = `cat $INTERNAL_DIR/agenda.txt`;
    my $agenda_text = `$SOURCE_DIR/gen_agenda_summary.pl \"$agenda_date\"`;
    return  qq{<br><br><br><b><font color="red">Unknown error occured during sending agenda to iesg-agenda-dist mailin glist.<br>Please go back and try again.</font></b><br>$SOURCE_DIR/gen_agenda_summary.pl $agenda_date<br><br><br>} unless my_defined($agenda_text);
    my $to="iesg-agenda-dist\@ietf.org"; 
#   my $to="priyanka\@amsl.com"; 


    send_mail($program_name,$user_name,$to,"IESG Secretary <iesg-secretary-reply\@ietf.org>","IESG Telechat Agenda (HTML) for $agenda_date",$agenda_html,"","","text/html; charset=\"utf-8\"");
    send_mail($program_name,$user_name,$to,"IESG Secretary <iesg-secretary-reply\@ietf.org>","IESG Telechat Agenda (Plain Text) for $agenda_date",$agenda_text);
  }




###### Manual Template Creation #################
#  my @filelist = ();
#  for $array_ref (@filelist) {
#    my $ballot_text = `cat $EVAL_DIR/$array_ref.bal`;
#    $ballot_text =~ s/\r//g;
    #$ballot_text =~ s/<br>/\r/g;
#    open (OUTFILE,">>$REC_DIR/$AGENDA_PACK");
#    print OUTFILE "\n\n$ballot_text\n";
#    close OUTFILE;
#  } 
#  open (OUTFILE,">>$REC_DIR/$AGENDA_PACK");
#  print OUTFILE "\n\n";
#  close OUTFILE;
#  system "cat $INTERNAL_DIR/appending.txt >> $REC_DIR/$AGENDA_PACK";
#################################################


#  my @wgList = db_select_multiple($dbh,"select a.acronym from acronym a,group_internal b, telechat_dates c where b.agenda = 1 and b.group_acronym_id = a.acronym_id and telechat_date = date1");
#  for $array_ref (@wgList) {
#    my ($wg_name) = rm_tr(@$array_ref);
#    open (OUTFILE,">>$REC_DIR/$AGENDA_PACK");
#    print OUTFILE "\n\n";
#    close OUTFILE;
#    system "cat $EVAL_DIR/$wg_name-charter.txt >> $REC_DIR/$AGENDA_PACK";
#  }
  chdir "$INTERNAL_DIR";
#  system "/home/mlee/bin/dos2unix.pl $AGENDA_PACK";
  #system "/home/mlee/bin/dos2unix.pl $AGENDA_PACK_NEW";
  #unless ($devel_mode) {
  #  system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa $REC_DIR/$AGENDA_PACK_NEW ietf\@stiedprstage1:$INTERNAL_DIR/$AGENDA_PACK_NEW";
  #  system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa $REC_DIR/$AGENDA_PACK_NEW ietf\@stiedprstage1:$REC_DIR/$AGENDA_PACK_NEW";
  #  system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa $REC_DIR/agenda_pack.rtf ietf\@stiedprstage1:$INTERNAL_DIR/agenda_pack.rtf";
  #  system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa $REC_DIR/agenda_summary.rtf ietf\@stiedprstage1:$INTERNAL_DIR/agenda_summary.rtf";
  #  system "cp $REC_DIR/agenda_pack* $INTERNAL_DIR/.";
  #}
  return "<br><br><br><b><a href=\"http://www.ietf.org/iesg/internal/dyn/$AGENDA_PACK_NEW\">$AGENDA_PACK_NEW</a> has been created</b><br><br><br><br>";
}


sub update_outstanding {
  my $q=shift;
  my $item_text = $q->param("item_text");
  my $item_text = db_quote($item_text);
  my $done = checktonum($q->param("done"));
  my $id = $q->param("id");
  db_update($dbh,"update outstanding_tasks set item_text=$item_text,last_updated_date=$CURRENT_DATE,done=$done where id=$id",$program_name,$user_name);
  return gen_agenda_package();
}

sub new_outstanding {
  my $q = shift;
  my $item_text = db_quote($q->param("item_text"));
  db_update($dbh,"insert into outstanding_tasks (item_text,last_updated_date) values ($item_text,$CURRENT_DATE)",$program_name,$user_name);
  return gen_agenda_package();
}

sub import_ballots {
$target_dir = "$EVAL_DIR";
$target_file = "*.*";
#chdir $target_dir;
#system "mv $EVAL_DIR/*.bal $EVAL_DIR/archive";
#system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa ietf\@stiedprstage1:/$EVAL_DIR/*.bal $EVAL_DIR/.";
#system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa ietf\@stiedprstage1:$EVAL_DIR/*-charter.txt $EVAL_DIR/.";

#system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa ietf\@stiedprstage1:$INTERNAL_DIR/MINUTES.txt $INTERNAL_DIR/MINUTES.txt";
#system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa ietf\@stiedprstage1:$INTERNAL_DIR/task.txt $INTERNAL_DIR/task.txt";
#system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa ietf\@stiedprstage1:$INTERNAL_DIR/rollcall.txt $INTERNAL_DIR/rollcall.txt";
#system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa ietf\@stiedprstage1:$INTERNAL_DIR/bash_agenda.txt $INTERNAL_DIR/bash_agenda.txt";
#system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa ietf\@stiedprstage1:$INTERNAL_DIR/appending.txt $INTERNAL_DIR/appending.txt";

return "This button has been borked<br>";
}

#########################################################
#
#   Function main_menu
#   Parameters:
#   return: HTML text of main screen with Search table and 
#           Draft list which's been assigned to current user
#
#########################################################
sub main_menu {
   my $html_txt = "";
   my $search_html = search_html();
   my $ballot_search_html=($AD_MODE)?ballot_search_html():"";;
   #my $ballot_search_html=($devel_mode)?ballot_search_html():"";
   my $default_search = db_select($dbh,"select default_search from iesg_login where id=$loginid") or error_log("select default_search from iesg_login where id=$loginid");
   my $action = "<input type=\"hidden\" name=\"enable\" value=\"1\">";
   my $button_value = "Enable Default Search";
   $html_txt .= qq{<CENTER>$search_html</CENTER></center>
<Center>$ballot_search_html</center>   
};
   if ($default_search) {
     $action = "";
     $button_value="Disable Default Search"; 
     my $count = db_select($dbh,"select count(*) from id_internal where job_owner = $loginid");
     if ($count < 1) {
        $html_txt .= qq{<h3>No Document Assigned currently</h3>};
     } else {
     $html_txt .= qq{<h3>Currently Assigned Document</h3>};
     my $sqlStr;
     $sqlStr = qq{ 
select state.id_document_tag, state.status_date,state.event_date,
state.job_owner, state.cur_state,state.cur_sub_state_id,state.assigned_to,state.rfc_flag,state.ballot_id,1
from id_internal state
left outer join internet_drafts id on state.id_document_tag = id.id_document_tag
where state.job_owner = $loginid
   AND state.primary_flag = 1
   order by state.cur_state, state.cur_sub_state_id, id.filename
     };
   #return $sqlStr;
     my @docList = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);  # Generate a list of data pulled from DB
     $html_txt .= display_all(0,0,@docList);# Generate a HTML text to display the list
     }
   }
   $html_txt .= qq{
$form_header
<input type="hidden" name="command" value="toggle_default_search">
$action
<input type="submit" value="$button_value" name="default_search">
</form> 
};
   return $html_txt;
}

sub toggle_default_search {
   my $q = shift;
   my $val = 0;
   $val = 1 if (defined($q->param("enable")));
   unless (db_update($dbh,"update iesg_login set default_search=$val where id=$loginid",$program_name,$user_name)) {
     return "Cannot toggle default search tag";
   }
   return main_menu();
}

sub ballot_search_html {
  my $q=shift;
  my ($date1,$date2,$date3,$date4) = db_select($dbh,"select date1,date2,date3,date4 from telechat_dates");
  return qq{
$form_header_noname
$table_header_640
<input type="hidden" name="command" value="my_ballot_page">
<TR BGCOLOR="silver"><Th colspan="2"><font color="red">NEW ***</font>Ballot - Search Criteria<font color="red">*** NEW</font></Th></TR>
<Tr><Td><b>Telechat date:</b> <select name="telechat_date"><option value="any">Any future telechat</option><option value="all">All telechat</option><option value="$date1">$date1</option><option value="$date2">$date2</option><option value="$date3">$date3</option><option value="$date4">$date4</option>
</select></td>
<td><b>My position:</b> <select name="my_position"><option value="">--All/Any</option><option value="no_record">No record</option><option value="yes_col">Yes</option><option value="no_col">No objection</option><option value="discuss">Discuss</option><option value="abstain">Abstain</option><option value="recuse">Recuse</option>
</select></td></tr>
<Tr BGCOLOR="silver"><td colspan="2" align="center"><input type="submit" value="  Display Ballots  "></td></tr>
</table>
</form>
<hr>
};
}


#########################################################
#
#   Function : search_html
#   Parameters:
#      $ballot_id - ballot_id, optional
#      $add_sub_flag - To indicate adding sub action, optional
#   return : HTML text to display search table
#
########################################################
sub search_html {
   my $ballot_id = shift;
   my $add_sub_flag = shift;
   my $dTag = shift;
   my $button_str;
   my $msg_str = "";
   
   my $default_job_owner = $q->param("search_job_owner");
   my $default_group_acronym = $q->param("search_group_acronym");
   my $default_area_acronym = $q->param("search_area_acronym");
   my $default_filename = $q->param("search_filename");
   my $default_rfcnumber = $q->param("search_rfcnumber");
   my $default_cur_state = $q->param("search_cur_state");
   my $default_status_id = $q->param("search_status_id");
   my $default_note = $q->param("note");
   my $area_option_str = get_area_option_str($default_area_acronym,1);
   my $state_option_str = get_option_str("ref_doc_states_new",$default_cur_state);
   my $status_option_str = get_option_str("id_status",$default_status_id);
   my $max_id = db_select($dbh,"select count(sub_state_id) from sub_state") or error_log("select count(sub_state_id) from sub_state");
   $max_id++;
   my $max_sub_id = db_select($dbh,"select max(sub_state_id) from sub_state") or error_log("select max(sub_state_id) from sub_state");
   $max_sub_id++;
   my $default_sub_state_id = $max_sub_id;
   $default_sub_state_id = $q->param("sub_state_id") if (defined($q->param("sub_state_id")));
   my $sub_state_option_str = get_sub_state_select($default_sub_state_id);

   if (defined($add_sub_flag)) {
      $button_str = qq {
	  <input type="hidden" name="ballot_id" value="$ballot_id">
	  <input type="hidden" name="dTag" value="$dTag">
<TD ALIGN="CENTER" colspan="2"><input type="submit" value="PROCEED" name="add_button" onClick="return validate_input();"></td>
};
   } else {
      $button_str = qq {
<TD ALIGN="CENTER"><INPUT TYPE="submit" VALUE="SEARCH" name="search_button">
<input type="button" value="Clear Fields" onClick="clear_fields();">
</TD>
<td ALIGN="CENTER"><input type="submit" value="ADD" name="add_button" onClick="return validate_input();"></td>
};
      $msg_str = qq {<font color="red" size="-1">**Just click 'SEARCH' button to view entire list of active draft**</font>};
   }
   my $ad_option_str = get_ad_option_str($default_job_owner); # HTML SELECT OPTIONS for Area Directors
   my $html_txt = qq{
   <script language="javascript">
   function validate_input () {
          filename = document.search_form.search_filename.value;
	  temp_val = filename.substring(0,1);
	  if (temp_val == " ") {
	     alert("File name cannot start with a space");
	     return false;
	  }

   	  if ( (document.search_form.search_filename.value == "" || document.search_form.search_filename.value == "null")
		&& (document.search_form.search_rfcnumber.value == "" || document.search_form.search_rfcnumber.value == "null") ){
		 alert("Either File Name or RFC Number field must be filled");
		 return false;
	  }
      return true;
   }
   
   function clear_fields() {
      document.search_form.search_job_owner.selectedIndex=0;
      document.search_form.search_status_id.selectedIndex=0;
      document.search_form.search_area_acronym.selectedIndex=0;
      document.search_form.search_cur_state.selectedIndex=0;
      document.search_form.sub_state_id.selectedIndex=$max_id;
      document.search_form.search_group_acronym.value = "";
      document.search_form.search_filename.value = "";
      document.search_form.search_rfcnumber.value = "";
      document.search_form.note.value = "";
      return true;
   }
</script>
$form_header_search
$table_header_640
<input type="hidden" name="command" value="search_list">
<TR BGCOLOR="silver"><Th colspan="2">I-D - Search Criteria</Th></TR>
<TR><TD colspan="2">
$table_header
  <TR><TD ALIGN="right">
  <B>Responsible AD:</B></TD>
  <TD><select name="search_job_owner">
  <option value="0">--All/Any</option>
  $ad_option_str</select>&nbsp;&nbsp;&nbsp;<B>WG Acronym:</B><INPUT TYPE="text" NAME="search_group_acronym" VALUE="$default_group_acronym" SIZE="6" MAXLENGTH="10">
  &nbsp;&nbsp;&nbsp;
  <B>Status:</B><SELECT NAME="search_status_id"><OPTION VALUE="">--Tracked or active</OPTION>
  $status_option_str</SELECT>
  </TD></TR>
  <TR><TD ALIGN="right"><B>Document State:</B></TD>
  <TD><SELECT NAME="search_cur_state"><OPTION VALUE="">--All/Any</option>
  $state_option_str
  </SELECT>&nbsp;&nbsp;&nbsp;
  <b>sub state</b>: $sub_state_option_str
  </TD></TR>
  <TR><TD ALIGN="right"><B>Filename:</B></TD>
  <TD><INPUT TYPE="text" NAME="search_filename" SIZE="15" MAXLENGTH="60" VALUE="$default_filename">
  &nbsp;&nbsp;&nbsp;<B>RFC Number:</B><INPUT TYPE="text" NAME="search_rfcnumber" SIZE="5" MAXLENGTH="10" VALUE="$default_rfcnumber">
  <B>Area Acronym:</B><select name="search_area_acronym">
  <option value="">--All/Any</option>
  $area_option_str
  </select>

  </TD></TR>
<tr><td align="right"><b>Note:</b></td>
<td>
<input type="text" name="note" size="70" value="$default_note">
</td></tr>
</TABLE>
</TD></TR>
<TR BGCOLOR="silver">$button_str
</TR>
</TABLE>
</FORM>
<HR>
};
   return $html_txt;
}

##########################################################################
# 
#   Function : search_list
#   Parameters :
#     $q : CGI variables
#   return : HTML text of search resulted list of draft
#
#########################################################################
sub search_list {
   my $q = shift;
   my $search_html = search_html();
   my $group_acronym_id = 0;
   my $area_acronym_id = (my_defined($q->param("search_area_acronym")))?$q->param("search_area_acronym"):0;
   my $group_acronym = "";
   my $html_txt .= qq{<CENTER>$search_html</CENTER>};
   $html_txt .= "<b>Search Result</b><br>\n";
   my @idList;
   my @rfcList;
   if (my_defined($q->param("search_filename"))) {
      $_ = $q->param("search_filename");
	  s/-\d\d.txt$//;
	  s/-\d\d$//;
	  $q->param(search_filename => $_);
   }
   if (my_defined($q->param("search_group_acronym"))) {
      $group_acronym = lc($q->param("search_group_acronym"));
	  $group_acronym_id = db_select($dbh,"select acronym_id from acronym where acronym = '$group_acronym'");
	  unless ($group_acronym_id) {
	     return "<h3>Fatal Error: Invalid WG $group_acronym</h3>";
      }
   }
   my @docList;
    
   if (my_defined($q->param("search_filename"))) {  # Searching ID
      $sqlStr = process_id ($q);
	  #return $sqlStr; 
	  @docList = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
   } elsif (my_defined($q->param("search_rfcnumber"))) {  # Searching RFC
      $sqlStr = process_rfc ($q);
	  #return $sqlStr; 
	  @docList = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
   } else {   #searching both ID and RFC
#      if ( my_defined($q->param("search_group_acronym")) or my_defined($q->param("search_status_id")) or my_defined($q->param("search_area_acronym")) ) {  
#         $sqlStr = process_id ($q);
#	     #return $sqlStr; 
#	     my @idList = db_select_multiple($dbh,$sqlStr);
#         $sqlStr = process_rfc ($q);
#	     #return $sqlStr; 
#	     my @rfcList = db_select_multiple($dbh,$sqlStr);
#         #Combine IDs and RFCs result
#         push @docList, @idList;
#         push @docList, @rfcList;
#      } else {
        $sqlStr = process_id_rfc($q);
	#return $sqlStr."<br>$group_acronym_id<br>";;
	@docList = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
#      }
   }   

   my $max_sub_id = db_select($dbh,"select max(sub_state_id) from sub_state");
   $max_sub_id++;
   $html_txt .= display_all($group_acronym_id,$area_acronym_id,@docList);
   if ($q->param("search_job_owner") == 0 and !my_defined($q->param("search_cur_state")) and $q->param("sub_state_id") == $max_sub_id and !my_defined($q->param("note"))) {
      unless (my_defined($q->param("search_rfcnumber"))) {
        $sqlStr = process_id_exists($q);
#return $sqlStr;
        @idList = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
      }
      unless (my_defined($q->param("search_filename"))) {
       if (my_defined($q->param("search_rfcnumber"))) {
        $sqlStr = process_rfc_exists($q);
#return $sqlStr;
        @rfcList = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
       }
      }
      my @newList;
      push @newList, @idList;
      push @newList, @rfcList;
      $html_txt .= display_all(0,0,@newList);
   }
   return $html_txt;
}

sub process_id_exists {
  my $q = shift;
  my $tag_set = "0";
  my $sqlStr0 = "select id_document_tag from id_internal where rfc_flag=0";
  if (my_defined($q->param("note"))) {
    my $note_field = "%" . rm_hd(rm_tr($q->param("note")));
    $note_field .= "%";
    $note_field = db_quote($note_field);
    $sqlStr0 .= " AND note like $note_field";
  }
  my @List = db_select_multiple($dbh,$sqlStr0) or error_log($sqlStr0);
  for $array_ref (@List) {
    my ($temp_tag) = @$array_ref;
    $tag_set .=", $temp_tag";
  }
  my $sqlStr = qq {
select id_document_tag,null,null,100,100,null,null,0,id_document_tag,filename
from internet_drafts
where id_document_tag not in ($tag_set)
};
   if (my_defined($q->param("search_filename"))) {
      my $filename = "%";
          $filename .= rm_hd(rm_tr($q->param("search_filename")));
          $filename .= "%";
          $filename = db_quote($filename);
          $sqlStr .= "AND filename like $filename\n";
   }
   if (my_defined($q->param("search_status_id"))) {
          my $status_id .= $q->param("search_status_id");
          $sqlStr .= "AND status_id = $status_id\n";
   } else {
          $sqlStr .= "AND status_id=1\n";
   }
   if (my_defined($q->param("search_group_acronym"))) {
      my $group_acronym = lc($q->param("search_group_acronym"));
      $group_acronym = db_quote($group_acronym);
          my $gID = db_select($dbh,"select acronym_id from acronym where acronym = $group_acronym");
          $sqlStr .= "AND group_acronym_id = $gID\n";
   }
   #if (my_defined($q->param("search_status_id"))) {
   #       my $status_id .= $q->param("search_status_id");
   #       $sqlStr .= "AND status_id = $status_id\n";
   #}
   if (my_defined($q->param("search_area_acronym"))) {
      my $area_acronym_id = $q->param("search_area_acronym");
          my $group_id_set = "";
          my @groupList = db_select_multiple($dbh,"select group_acronym_id from area_group where area_acronym_id = $area_acronym_id") or error_log("select group_acronym_id from area_group where area_acronym_id = $area_acronym_id");
          my @group_id_set;
          for $array_ref (@groupList) {
             my ($val) = @$array_ref;
                 push @group_id_set,$val;
          }
          $group_id_set = join ",",@group_id_set;
          $sqlStr .= qq { AND (group_acronym_id in ($group_id_set))
          };
   }
  $sqlStr .= "\norder by filename\n";
  return $sqlStr;
}

sub process_rfc_exists {
  my $q = shift;
  my $gAcronym = $q->param("search_group_acronym");
  my $filename = $q->param("search_rfcnumber");

  my $tag_set = "0";
  my $sqlStr0 = "select id_document_tag from id_internal where rfc_flag=1";
  if (my_defined($q->param("note"))) {
    my $note_field = "%" . rm_hd(rm_tr($q->param("note")));
    $note_field .= "%";
    $note_field = db_quote($note_field);
    $sqlStr0 .= " AND note like $note_field";
  }

  my @List = db_select_multiple($dbh,$sqlStr0) or error_log($sqlStr0);
  for $array_ref (@List) {
    my ($temp_tag) = @$array_ref;
    $tag_set .=", $temp_tag";
  }
  my $sqlStr = qq {
select rfc_number,null,null,100,100,null,null,1,rfc_number,rfc_number
from rfcs
where rfc_number not in ($tag_set)
};
   if (my_defined($gAcronym)) {
      $gAcronym = db_quote($gAcronym);
      $sqlStr .= "AND group_acronym = $gAcronym\n";
   }
   if (my_defined($filename)) {
          $_ = $filename;
          s/(\D+)(\d+)(\D+)/$2/;
              $rfc_number = $_;
      $sqlStr .= "AND rfc_number = $rfc_number\n";
   }
   if (my_defined($q->param("search_status_id"))) {
          my $status_id .= $q->param("search_status_id");
          if ($status_id == 2) {
             $sqlStr .= "AND rfc_number = 999999\n";
      }
   }
   if (my_defined($q->param("search_area_acronym"))) {
      my $area_acronym_id = $q->param("search_area_acronym");
          $sqlStr .= qq {AND  area_acronym = $area_acronym_id
          };
   }
  $sqlStr .= "\norder by rfc_number\n";
   return $sqlStr;
}
#############################################################
#
#   Function process_id
#   parameters :
#     $q : CGI variables
#   return : SQL statement which performs search on IDs

#############################################################
sub process_id {
   my $q = shift;
   my $sqlStr = qq{
   select state.id_document_tag, state.status_date,state.event_date,state.job_owner,
   state.cur_state,state.cur_sub_state_id,state.assigned_to,state.rfc_flag,state.ballot_id,id.filename
   from id_internal state, internet_drafts id};
   my $where_clause = qq {
   where id.id_document_tag = state.id_document_tag
   AND state.rfc_flag = 0
   };
   if (my_defined($q->param("note"))) {
     my $note_field = "%" . rm_hd(rm_tr($q->param("note")));
     $note_field .= "%";
     $note_field = db_quote($note_field);
     $where_clause .= " AND note like $note_field";
   }
   if (my_defined($q->param("search_filename"))) {
      my $filename = "%";
	  $filename .= rm_hd(rm_tr($q->param("search_filename")));
	  $filename .= "%";
      $filename = db_quote($filename);
	  $where_clause .= "AND id.filename like $filename and state.rfc_flag = 0\n";
   }
   if (my_defined($q->param("search_group_acronym"))) {
      my $group_acronym = lc($q->param("search_group_acronym"));
      $group_acronym = db_quote($group_acronym);
	  my $gID = db_select($dbh,"select acronym_id from acronym where acronym = $group_acronym");
	  $where_clause .= "AND id.group_acronym_id = $gID\n";
   }
   if (my_defined($q->param("search_assigned_to")) and substr($q->param("search_assigned_to"),0,1) ne "-") {
	  my $assigned_to .= db_quote($q->param("search_assigned_to"));
	  $where_clause .= "AND state.assigned_to = $assigned_to\n";
   }
   if (my_defined($q->param("search_cur_state"))) {
	  my $cur_state .= $q->param("search_cur_state");
	  $where_clause .= "AND state.cur_state = $cur_state\n";
   }
   if (my_defined($q->param("sub_state_id"))) {
      my $max_id = db_select($dbh,"select max(sub_state_id) from sub_state") or error_log("select max(sub_state_id) from sub_state");
      my $sub_state_id .= $q->param("sub_state_id");
      if ($sub_state_id <= $max_id) {
         if ($sub_state_id == 0) {
           $where_clause .= "AND state.cur_sub_state_id <= 0\n";
         } else {
           $where_clause .= "AND state.cur_sub_state_id = $sub_state_id\n";
         }
      }
   }

   if (my_defined($q->param("search_status_id"))) {
	  my $status_id .= $q->param("search_status_id");
	  $where_clause .= "AND id.status_id = $status_id\n";
   }
   if ($q->param("search_job_owner") > 0) {
      my $job_owner = $q->param("search_job_owner");
	  $where_clause .= "AND state.job_owner = $job_owner\n";
   }
   if (my_defined($q->param("search_area_acronym"))) {
      my $area_acronym_id = $q->param("search_area_acronym");
	  my $group_id_set = "";
	  my @groupList = db_select_multiple($dbh,"select group_acronym_id from area_group where area_acronym_id = $area_acronym_id") or error_log("select group_acronym_id from area_group where area_acronym_id = $area_acronym_id");
	  my @group_id_set;
	  for $array_ref (@groupList) {
	     my ($val) = @$array_ref;
		 push @group_id_set,$val;
	  }
	  $group_id_set = join ",",@group_id_set;
	  $where_clause .= qq { AND ((id.group_acronym_id = 1027 AND state.area_acronym_id = $area_acronym_id) OR 
	  (id.group_acronym_id <> 1027 AND id.group_acronym_id in ($group_id_set))) 
	  };
   }
   $sqlStr .= $where_clause;
   $sqlStr .= "\n order by state.cur_state, state.cur_sub_state_id,state.primary_flag desc,id.filename\n";
   return $sqlStr;
}


sub process_id_rfc {
   my $q = shift;
   my $sqlStr;
   my $where_clause;
   $sqlStr = qq{
      select state.id_document_tag, state.status_date,state.event_date,state.job_owner,
      state.cur_state,state.cur_sub_state_id,state.assigned_to,state.rfc_flag,state.ballot_id,1,id.filename
      from id_internal state left outer join internet_drafts id on id.id_document_tag = state.id_document_tag};
      $where_clause = qq {
      where state.primary_flag = 1 
};
   if (my_defined($q->param("note"))) {
     my $note_field = "%" . rm_hd(rm_tr($q->param("note")));
     $note_field .= "%";
     $note_field = db_quote($note_field);
     $where_clause .= " AND note like $note_field";
   }
   if (my_defined($q->param("search_assigned_to")) and substr($q->param("search_assigned_to"),0,1) ne "-") {
	  my $assigned_to .= db_quote($q->param("search_assigned_to"));
	  $where_clause .= "AND state.assigned_to = $assigned_to\n";
   }
   if (my_defined($q->param("search_cur_state"))) {
	  my $cur_state .= $q->param("search_cur_state");
	  $where_clause .= "AND state.cur_state = $cur_state\n";
   
   }
   if (my_defined($q->param("sub_state_id"))) {
      my $max_id = db_select($dbh,"select max(sub_state_id) from sub_state") or error_log("select max(sub_state_id) from sub_state");
      my $sub_state_id .= $q->param("sub_state_id");
      if ($sub_state_id <= $max_id) {
         if ($sub_state_id == 0) {
           $where_clause .= "AND state.cur_sub_state_id <= 0\n";
         } else {
           $where_clause .= "AND state.cur_sub_state_id = $sub_state_id\n";
         }
      }
   }

   if (my_defined($q->param("search_status_id"))) {
	  my $status_id .= $q->param("search_status_id");
	  $where_clause .= "AND id.status_id = $status_id\n";
	  if ($status_id == 2) {
	     $where_clause .= "AND state.rfc_flag = 0\n";
      }
   }
   if ($q->param("search_job_owner") > 0) {
      my $job_owner = $q->param("search_job_owner");
	  $where_clause .= "AND state.job_owner = $job_owner\n";
   }
   $sqlStr .= $where_clause;
   $sqlStr .= "\n order by state.cur_state, state.cur_sub_state_id,id.filename\n";
   return $sqlStr;
}




##################################################
#
#   Function : process_rfc
#   Parameters :
#      $q : CGI variables
#   return : SQL statement which will perform search on RFCs
#
##################################################
sub process_rfc {
   my $q = shift;
   my $dName = uc($q->param("search_id_document_name"));
   my $gAcronym = $q->param("search_group_acronym");
   my $filename = $q->param("search_rfcnumber");
   my $sqlStr = qq{
   select state.id_document_tag, state.status_date,state.event_date,state.job_owner,
   state.cur_state,state.cur_sub_state_id,state.assigned_to,state.rfc_flag,state.ballot_id,rfc.rfc_number
   from id_internal state, rfcs rfc
   };
   my $where_clause = qq {
   where rfc.rfc_number = state.id_document_tag
   AND state.rfc_flag = 1
   };
   if (my_defined($q->param("note"))) {
     my $note_field = "%" . rm_hd(rm_tr($q->param("note")));
     $note_field .= "%";
     $note_field = db_quote($note_field);
     $where_clause .= " AND note like $note_field";
   }
      if (my_defined($dName)) {
         $dName = rm_hd(rm_tr($dName));
	 $dName .= "%";
         $dName = db_quote($dName);
         $where_clause .= "AND rfc_name_key like $dName\n";
      }
      if (my_defined($gAcronym)) {
         $gAcronym = db_quote($gAcronym);
         $where_clause .= "AND group_acronym = $gAcronym\n";
      }
      if (my_defined($filename)) {
	     $_ = $filename;
  	     s/(\D+)(\d+)(\D+)/$2/;
		 $rfc_number = $_;
         $where_clause .= "AND rfc_number = $rfc_number\n";
      }
   if (my_defined($q->param("search_assigned_to")) and substr($q->param("search_assigned_to"),0,1) ne "-") {
	  my $assigned_to .= db_quote($q->param("search_assigned_to"));
	  $where_clause .= "AND state.assigned_to = $assigned_to\n";
   }
   if (my_defined($q->param("search_cur_state"))) {
	  my $cur_state .= $q->param("search_cur_state");
	  $where_clause .= "AND state.cur_state = $cur_state\n";
   }
   if (my_defined($q->param("sub_state_id"))) {
      my $max_id = db_select($dbh,"select max(sub_state_id) from sub_state");
      my $sub_state_id .= $q->param("sub_state_id");
      if ($sub_state_id <= $max_id) {
         if ($sub_state_id == 0) {
           $where_clause .= "AND state.cur_sub_state_id <= 0\n";
         } else {
           $where_clause .= "AND state.cur_sub_state_id = $sub_state_id\n";
         }
      }
   }
 

   if ($q->param("search_job_owner") > 0) {
      my $job_owner = $q->param("search_job_owner");
	  $where_clause .= "AND state.job_owner = $job_owner\n";
   }
   if (my_defined($q->param("search_status_id"))) {
	  my $status_id .= $q->param("search_status_id");
	  if ($status_id == 2) {
	     $where_clause .= "AND rfc.rfc_number = 999999\n";
      }
   }
   if (my_defined($q->param("search_area_acronym"))) {
      my $area_acronym_id = $q->param("search_area_acronym");
	  $where_clause .= qq {AND  state.area_acronym_id = $area_acronym_id
	  };
   }
   $sqlStr .= $where_clause;
   $sqlStr .= "\n order by state.cur_state, state.cur_sub_state_id, state.primary_flag desc, rfc.rfc_number\n";
   return $sqlStr;
}

###################################################
#
#   Function : process_add_id
#   Parameters:
#     $q : CGI variables
#   return : SQL statement 
#
##################################################
sub process_add_id {
   my $q = shift;
   my $dTag = $q->param("dTag");
   my $sqlStr;
   $dName = uc($q->param("search_id_document_name"));
   $gAcronym = $q->param("search_group_acronym");
   $filename = $q->param("search_filename");
   $StatusId = $q->param("search_status_id");
   my $ballot_id = $q->param("ballot_id");
   unless (my_defined($ballot_id)) {
      $ballot_id = 0;
   }
   
   my $whereClause = "";
   if (my_defined($dTag)) {
      $whereClause .= "AND a.id_document_tag <> $dTag\n";
   }
   if (my_defined($StatusId)) {
      $whereClause .= "AND status_id = $StatusId\n";
   }
      if (my_defined($dName)) {
	     $dName .= "%";
         $dName = db_quote($dName);
         $whereClause .= "AND id_document_key like $dName\n";
      }
      if (my_defined($gAcronym)) {
         $gAcronym = db_quote($gAcronym);
         $sqlStr = "select acronym_id from acronym where acronym = $gAcronym";
	     my $gID = db_select($dbh,$sqlStr);
         $whereClause .= "AND group_acronym_id = $gID\n";
      }
      if (my_defined($filename)) {
	     $filename = "%${filename}%";
         $filename = db_quote($filename);
         $whereClause .= "AND filename like $filename\n";
      }
      $sqlStr = qq{
      select a.id_document_tag,filename,b.id_document_tag, b.ballot_id
      from internet_drafts a left outer join id_internal b 
      on a.id_document_tag = b.id_document_tag
      Where 0 = 0
      $whereClause
      order by filename
      };

   return $sqlStr;
}

######################################
#
#   Function : process_add_rfc
#   Parameters :
#      $q : CGI variables
#   return : SQL statement that search on RFCs
#
######################################
sub process_add_rfc {
   my $q = shift;
   my $dTag = $q->param("dTag");
   my $sqlStr;
   $dName = uc($q->param("search_id_document_name"));
   $gAcronym = $q->param("search_group_acronym");
   $filename = $q->param("search_rfcnumber");
   my $ballot_id = $q->param("ballot_id");
   unless (my_defined($ballot_id)) {
      $ballot_id = 0;
   }
   
   my $whereClause = "";
   if (my_defined($dTag)) {
      $whereClause .= "AND a.rfc_number <> $dTag\n";
   }
      if (my_defined($dName)) {
	     $dName .= "%";
         $dName = db_quote($dName);
         $whereClause .= "AND rfc_name_key like $dName\n";
      }
      if (my_defined($gAcronym)) {
         $gAcronym = db_quote($gAcronym);
         $whereClause .= "AND group_acronym = $gAcronym\n";
      }
      if (my_defined($filename)) {
	     $_ = $filename;
  	     s/(\D+)(\d+)(\D+)/$2/;
		 $rfc_number = $_;
         $whereClause .= "AND rfc_number = $rfc_number\n";
      }
      $sqlStr = qq{
      select rfc_number,rfc_name,b.id_document_tag, b.ballot_id
      from rfcs a left outer join id_internal b 
      on a.rfc_number = b.id_document_tag
      Where 0 = 0
      $whereClause
      };
   
   return $sqlStr;
}

##########################################################
#
#   Function : add_id_search
#   Parameters :
#     $q : CGI variables
#   return : HTML text: List of draft if search result is more than one.
#                       View Draft page of search result if only one result
#
#########################################################
sub add_id_search {
   my $q = shift;
   my $html_txt = "Search Result";
   if (my_defined($q->param("search_group_acronym"))) {
      my $group_acronym = lc($q->param("search_group_acronym"));
      $group_acronym = db_quote($group_acronym);
	  my $gID = db_select($dbh,"select acronym_id from acronym where acronym = $group_acronym");
	  unless ($gID) {
	     return "<h3>Fatal Error: Invalid WG $group_acronym</h3>";
      }
   }
   if (my_defined($q->param("search_filename"))) {  # Search on IDs
      $_ = $q->param("search_filename");
	  s/-\d\d.txt$//;
	  s/-\d\d$//;
          $_ = rm_tr($_);
	  $q->param(search_filename => $_);
      $sqlStr = process_add_id ($q);
	  $rfc_flag = 0;
   } else {					    # Search on RFCs
      $sqlStr = process_add_rfc ($q);
	  $rfc_flag = 1;
   }
   my $ballot_id = $q->param("ballot_id");
   my $add_str = "Add";
   my $add_name = "Add";
   unless (my_defined($ballot_id)) { # Add New Ballot
      $ballot_id = 0;
   } else { 			     # Add an action to existing ballot
      $add_str = "Add to Ballot";
      $add_name = "add_existing";
   }
   
#return $sqlStr;

   $html_txt = qq{$table_header
   <tr><th>File Name</th></tr>
   };
   my @list = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
   for $array_ref (@list) {
     my ($dTag,$document_name,$internal_exist,$c_ballot_id) = @$array_ref;
       unless (defined($internal_exist) and $ballot_id==0) {
         if ($#list == 0) {
	   $q->param(dTag => $dTag);
	   $q->param(rfc_flag => $rfc_flag);
	   $q->param(ballot_id => $ballot_id);
	   $q->param(dName => $document_name);
#		   if ($cnt > 0) {
#		      $q->param(add_existing => $ballot_id);
#		   }
	   if ($internal_exist > 0) {
	      $q->param(add_existing => $ballot_id);
	   }
           return add_id_confirm($q);
         }
	 unless ($internal_exist) {
	   $add_name = "add_new";
	 } else {
	   $add_name = "add_existing";
	 }
         $button_str = qq{<input type="submit" value="$add_str" name="$add_name">};
         $button_str = "<font color=\"red\">SAME BALLOT</font>" if ($ballot_id == $c_ballot_id and $ballot_id > 0);
       } else {
	    $button_str = "<font color=\"red\">EXISTS</font>";
       }
       $html_txt .= qq{
		$form_header
		<input type="hidden" name="command" value="add_id_confirm">
		<input type="hidden" name="dTag" value="$dTag">
		<input type="hidden" name="rfc_flag" value="$rfc_flag">
		<input type="hidden" name="dName" value="$document_name">
		<input type="hidden" name="ballot_id" value="$ballot_id">
		<tr><Td>$document_name</td>
		<td>${button_str}</td></tr>
		</form>
      };
   } #for
   $html_txt .= "</table>\n";
   
   return $html_txt;
}

#################################################
#
#   Function : add_existing
#   Parameters :
#      $q : CGI variables
#   return : HTML text to display view draft page after change the ballot id of 
#            existing ballot
#
#################################################
sub add_existing {
   my $q = shift;
   my $ballot_id = $q->param("ballot_id");
   my ($id_document_tag,$cur_state,$cur_sub_state_id,$agenda) = db_select($dbh,"select id_document_tag,cur_state,cur_sub_state_id,agenda from id_internal where ballot_id=$ballot_id and primary_flag=1") or error_log("select id_document_tag,cur_state,cur_sub_state_id,agenda from id_internal where ballot_id=$ballot_id and primary_flag=1");
   my $filename = db_select($dbh,"select filename from internet_drafts where id_document_tag = $id_document_tag");
   my $comment_text = "Merged with $filename";
   my $dTag = $q->param("dTag");
   my $sqlStr = qq {update id_internal
   set ballot_id = $ballot_id,
   primary_flag = 0,
   agenda=$agenda,
   cur_state=$cur_state,
   cur_sub_state_id=$cur_sub_state_id,
   event_date = CURRENT_DATE
   where id_document_tag = $dTag
   };
#   return $sqlStr;
   unless (db_update($dbh,$sqlStr,$program_name,$user_name)) {
     return $error_msg;
   }
   add_document_comment($loginid,$dTag,$comment_text,0);
   return view_id($q);
}

#####################################################
#
#   Function : add_id_confirm
#   Parameters :
#     $q : CGI variables
#   return : HTML text to display form to enter additional information to be inserted as a ballot
#
#####################################################
sub add_id_confirm {
   my $q = shift;
   if (defined($q->param("add_existing"))) { # ballot already existed, No additional information needed
      return add_existing($q);
   }
   my $via_rfc_checkbox = "";
   $via_rfc_checkbox = " &nbsp; Via IRTF or RFC Editor? <input type=\"checkbox\" name=\"via_rfc_editor\"> " if ($ADMIN_MODE);
   my $rfc_flag = $q->param("rfc_flag");
   my $column = "id_document_tag";
   $column = "rfc_number" if ($rfc_flag);
   my $dTag = $q->param("dTag");
   my $name_col = "Draft Name";
   $name_col = "Rfc Name" if ($rfc_flag);
   my ($dName,$revision,$intended_status_id,$id_status_id,$expired_tombstone) = rm_tr(db_select($dbh,"select filename,revision,intended_status_id,status_id,expired_tombstone from internet_drafts where $column = $dTag"));
   if ($rfc_flag) {
      ($dName,$intended_status_id) = rm_tr(db_select($dbh,"select rfc_name,intended_status_id from rfcs where rfc_number=$dTag")) if ($rfc_flag);
      $revision = "RFC $dTag";
   }

   my $id_status_option_str = get_id_status_option_str($intended_status_id,$rfc_flag);
   my $ballot_id = $q->param("ballot_id");
   my $expired_tickler = "";
   my $expired = 0;
   if ($id_status_id==2 and $rfc_flag==0) {
     $expired_tickler = qq{
<font size=+3 color="red"> *** EXPIRED ***</font><br>
<font size=+1>You can't process an expired I-D</font>
$form_header
<input type="hidden" name="command" value="resurrect">
<input type="hidden" name="loginid" value="$loginid">
<input type="hidden" name="id_document_tag" value="$dTag">
<input type="hidden" name="rfc_flag" value="$rfc_flag">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="submit" value="resurrect it first">
</form>
}; 
     $expired = 1;
   } 
   my $status_value = db_select($dbh,"select status_value from internet_drafts a, id_status b where id_document_tag=$dTag and a.status_id=b.status_id");
   unless ($status_value eq "Active") {
     $revision = decrease_revision($revision) unless $expired_tombstone;
     $dName .= "($status_value)";
   }

   my $html_txt = qq|
   <script language="javascript">
   function check_expired () {
     if ($expired == 1) {
       alert ("You can't process an expired I-D");
       return false;
     } else {
       return true;
     }
   }
   </script>

$table_header
$form_header
<tr><td colspan="2" align="center" bgcolor="cccccc"><h1>Add Draft</h1>$expired_tickler</td></tr>
<tr><td>$name_col:</td><td>$dName $via_rfc_checkbox</td></tr>
<tr bgcolor="white"><td>Version: </td><td>$revision</td></tr>

|; 
   my $job_owner = $loginid;
   my $ad_option_str = get_ad_option_str($job_owner,1);
   my $state_option_str = get_option_str("ref_doc_states_new");
   my $area_acronym_str = "";
   my $area_option_str = get_area_option_str();
   my $sub_state_select_str = get_sub_state_select(-2);
   my $gID = db_select($dbh,"select group_acronym_id from internet_drafts where id_document_tag = $dTag");
   if ($rfc_flag) {
     $gID=db_select($dbh,"select acronym_id from acronym a, rfcs b where a.acronym=b.group_acronym and rfc_number=$dTag");
   }
   my $wg_mode = 0;
   my $state_change_notice_to = "";
   if ($gID == 1027) {
      $area_acronym_str = qq{
	  <tr><td>Area Acronym:</td>
	  <td><select name="area_acronym_id">
	  <option value=""></option>
	  $area_option_str
	  </select></td>
	  </tr>
};
      $wg_mode = 1;
      my @List = ($rfc_flag)?db_select_multiple($dbh,"select person_or_org_tag from rfc_authors where rfc_number=$dTag"):db_select_multiple($dbh,"select person_or_org_tag from id_authors where id_document_tag=$dTag");
      for my $array_ref (@List) {
        my ($person_or_org_tag) = @$array_ref;
        my $email = get_email($person_or_org_tag);
        $state_change_notice_to .= "$email, ";
      }
   } else {
     #my @List = db_select_multiple($dbh,"select email_address from email_addresses a, g_chairs b where b.group_acronym_id = $gID and b.person_or_org_tag = a.person_or_org_tag");
     my @List2 = db_select_multiple($dbh,"select email_address from email_addresses a, g_editors b where b.group_acronym_id = $gID and b.person_or_org_tag = a.person_or_org_tag");
     #for my $array_ref (@List) {
     #  my ($email) = @$array_ref;
     #  $state_change_notice_to .= "$email, ";
     #}
     my $group_name=db_select($dbh,"select acronym from acronym where acronym_id=$gID");
     $state_change_notice_to .= "$group_name-chairs\@tools.ietf.org, ";
     for my $array_ref (@List2) {
       my ($email) = @$array_ref;
       $state_change_notice_to .= "$email, ";
     }
   } 
   $state_change_notice_to .= "$dName\@tools.ietf.org";
   #chop ($state_change_notice_to);
   #chop ($state_change_notice_to);
   $html_txt .= qq{
   <input type="hidden" name="command" value="add_id_db">
   <input type="hidden" name="rfc_flag" value="$rfc_flag">
   <input type="hidden" name="dTag" value="$dTag">
   <input type="hidden" name="ballot_id" value="$ballot_id">
   <input type="hidden" name="wg_mode" value="$wg_mode">
   <tr bgcolor="white"><td>Intended Status: </td>
   <td>
   <select name="id_intended_status">
   $id_status_option_str
   </select>
   &nbsp; &nbsp; Agenda? <input type="checkbox" name="agenda" $checked  onClick="return check_expired();"> on
   <select name="telechat_date" onChange="return check_expired();">$telechat_date_list</select>
   <input type="hidden" name="agenda_present" value="1">
   </td></tr>

   $area_acronym_str
   <tr><td>Current State: </td>
   <td>
   <select name="current_state">
   $state_option_str
   </select>
   $sub_state_select_str
   </td></tr>
   <tr>
   <td>Responsible AD:</td>
   <td><select name="job_owner">
   $ad_option_str
   </select></td>
   </tr>
   <tr>
   <td>Status Date:<br>(YYYY-MM-DD)</td>
   <td><input type="text" name="status_date"></td>
   </tr>
   <tr>
    <tr bgcolor="white"><td>Brief Note:<br>(IRTF or RFC Editor and other notes<br>
are entered on the ballot page.)</td><td>
   <textarea name="note" rows="3" cols="74" wrap="virtual"></textarea>
   </td></tr> 
   <td>Comment:</td>
   <td><textarea name="comment" rows="10" cols="74" wrap="virtual"></textarea> <input type="checkbox" name="public_flag" checked> Public</td>
   </tr>
   <tr bgcolor="white"><td>State or Version Change<br>Notice To:</td>
   <td><input type="text" name="state_change_notice_to" value="$state_change_notice_to" size="56"> <b>A comma must exist between email addresses</b></td></tr>
   <tr>
   <td colspan="2"><input type="submit" value="SUBMIT" onClick="return check_expired();"></td>
   </tr>
   </form>
   </table>
   };
   return $html_txt;
}


############################################
#
#   Function : add_id_db
#   Parameters :
#      $q - CGI variables
#   return : HTML text to display main screen
#
#   This function add new ballot and comment to database
#
###########################################
sub add_id_db {
   my $q = shift;
   my $id_document_tag = $q->param("dTag");
   my $ballot_id = $q->param("ballot_id");
   my $primary_flag = 0;
   my $via_rfc_editor = checktonum($q->param("via_rfc_editor"));
   my $area_acronym_id = $q->param("area_acronym_id");
   my $cur_state = $q->param("current_state");
   my $rfc_flag = $q->param("rfc_flag");
   my $comment = $q->param("comment");
   my $note = db_quote($q->param("note"));
   my $state_change_notice_to = db_quote($q->param("state_change_notice_to"));
   my $intended_status_id = $q->param("id_intended_status");
   my $agenda = checktonum($q->param("agenda"));
   my $telechat_date = "NULL";
   $telechat_date = db_quote($q->param("telechat_date")) if ($agenda);
   my $job_owner= $q->param("job_owner");
   my $public_flag = (defined($q->param("public_flag")))?1:0;
   my $mark_by = $loginid;
   my $table_name = "id_internal";
   my $token_name = db_quote(get_mark_by($job_owner));
   my $wg_mode = $q->param("wg_mode");
   my $sub_state_id = $q->param("sub_state_id");
   $area_acronym_id = 1008 if ($wg_mode and !my_defined($area_acronym_id));
   if ($rfc_flag) {
      return $error_msg unless (db_update($dbh,"update rfcs set intended_status_id = $intended_status_id where rfc_number = $id_document_tag",$program_name,$user_name));

   } else {
      return $error_msg unless (db_update($dbh,"update internet_drafts set intended_status_id = $intended_status_id where id_document_tag = $id_document_tag",$program_name,$user_name));
   }
   $sqlStr = qq {
   select email_address from email_addresses e,iesg_login i
   where i.id = $job_owner
   AND i.person_or_org_tag = e.person_or_org_tag
   AND e.email_priority = 1
   };
   my $token_email = db_quote(rm_tr(db_select($dbh,$sqlStr)));
   my $version = db_select($dbh,"select revision from internet_drafts where id_document_tag = $id_document_tag");
   
   $version = db_quote($version);
   if ($rfc_flag) {
      $table_name = "id_internal";
   }
   my $status_date = db_quote(convert_date($q->param("status_date"),$CONVERT_SEED));
   my $assigned_to = $q->param("assigned_to");
   if (substr($assigned_to,0,1) eq "-") {
      $assigned_to = "Unassigned";
   }
   $assigned_to = db_quote($assigned_to);
   if ($ballot_id == 0) {  # if new action
      $ballot_id = db_select($dbh,"select max(ballot_id) from id_internal");
	  $primary_flag = 1;
      unless (my_defined($ballot_id)) {
         $ballot_id = 1;
      } else {
         $ballot_id++;
      }
   }
   unless (my_defined($area_acronym_id)) {
      $sqlStr = qq { select a.acronym_id from acronym a, area_group c, internet_drafts i
      where i.id_document_tag = $id_document_tag and i.group_acronym_id = c.group_acronym_id and
      c.area_acronym_id = a.acronym_id
      };
      $area_acronym_id = db_select($dbh,$sqlStr) or error_log($sqlStr);
   }
   $sqlStr = qq{insert into $table_name
   (id_document_tag,rfc_flag,cur_state,prev_state,assigned_to,status_date,event_date,mark_by,job_owner,ballot_id,primary_flag,area_acronym_id,token_name,email_display,token_email,cur_sub_state_id,prev_sub_state_id,agenda,note,telechat_date,via_rfc_editor,state_change_notice_to)
   values ($id_document_tag,$rfc_flag,$cur_state,$cur_state,$assigned_to,$status_date,$CURRENT_DATE,$mark_by,$job_owner,$ballot_id,$primary_flag,$area_acronym_id,$token_name,$token_name,$token_email,$sub_state_id,0,$agenda,$note,$telechat_date,$via_rfc_editor,$state_change_notice_to)
   };
   #return $sqlStr;
   unless (db_update($dbh,$sqlStr,$program_name,$user_name)) {
     return $error_msg;
   }
   my $replaced_by_tag = db_select($dbh,"select a.id_document_tag from id_internal a, internet_drafts b where replaced_by=$id_document_tag and a.id_document_tag=b.id_document_tag");
   if ($rfc_flag==0 and $replaced_by_tag > 0) { #For Replacement I-D
     my $old_filename = db_select($dbh,"select filename from internet_drafts where id_document_tag=$replaced_by_tag");
     my $comment_text = "Earlier history may be found in the Comment Log for <a href=\"/public/pidtracker.cgi?command=view_id&dTag=$replaced_by_tag&rfc_flag=0\">$old_filename</a>.";
 

     add_document_comment($loginid,$id_document_tag,$comment_text,0);
   }   
   ################### Update Comment Log ####################
   my $new_mark_by = get_mark_by($loginid,1);
   my $state_txt = db_select($dbh,"select document_state_val from ref_doc_states_new where document_state_id = $cur_state");
   my $log_txt = "Draft Added by $new_mark_by in state $state_txt";
   $log_txt = db_quote($log_txt);
   
   unless (update_comment_log($id_document_tag,$version,$mark_by,$cur_state,$cur_state,$comment,$log_txt,$public_flag)) {
      db_update($dbh,"delete from id_internal where id_document_tag = $id_document_tag",$program_name,$user_name);
      return "$error_msg";
   }   
   add_document_comment($loginid,$id_document_tag,"[Note]: $note added",0) unless ($note eq "''");
   my $html_txt = view_id($q);
   return $html_txt;
}



sub copy_ballot {
  $old_ballot = shift;
  $new_ballot = shift;
  my $sqlStr = "select ad_id,yes_col,no_col,abstain,recuse,approve,discuss from ballots where ballot_id = $old_ballot";
  my @List = db_select_multiple($dbh,$sqlStr);
  for $array_ref (@List) {
    my ($ad_id,$yes_col,$no_col,$abstain,$recuse,$approve,$discuss) = @$array_ref;
    db_update($dbh,"insert into ballots values (null,$new_ballot,$ad_id,$yes_col,$no_col,$abstain,$approve,$discuss,$recuse)",$program_name,$user_name);
  }
  my ($active,$ballot_writeup) = rm_tr(db_select($dbh,"select active,ballot_writeup from ballot_info where ballot_id = $old_ballot"));
  my $filename = rm_tr(db_select($dbh,"select filename from internet_drafts a, id_internal b where a.id_document_tag = b.id_document_tag and b.ballot_id=$new_ballot and b,primary_flag=1"));
  my $last_call_text = db_quote(gen_last_call_ann($filename,$new_ballot));
  my $approval_text = db_quote(gen_approval_text($filename,$new_ballot));
  $ballot_writeup = db_quote($ballot_writeup);
  db_update($dbh,"insert into ballot_info (ballot_id,active,approval_text,last_call_text,ballot_writeup) values ($new_ballot,$active,$approval_text,$last_call_text,$ballot_writeup)",$program_name,$user_name);
  $sqlStr = "select ad_id,comment_date,revision,active,comment_text from ballots_comment where ballot_id=$old_ballot";
  @List = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
  for $array_ref (@List) {
    my ($ad_id,$comment_date,$revision,$active,$comment_text) = rm_tr(@$array_ref);
    ($comment_date,$revision,$comment_text) = db_quote($comment_date,$revision,$comment_text);
    db_update($dbh,"insert into ballots_comment values (null,$new_ballot,$ad_id,$comment_date,$revision,$active,$comment_text)",$program_name,$user_name);
  }
  $sqlStr = "select ad_id,discuss_date,revision,active,discuss_text from ballots_discuss where ballot_id=$old_ballot";
  @List = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
  for $array_ref (@List) {
    my ($ad_id,$comment_date,$revision,$active,$comment_text) = rm_tr(@$array_ref);
    ($comment_date,$revision,$comment_text) = db_quote($comment_date,$revision,$comment_text);
    db_update($dbh,"insert into ballots_discuss values (null,$new_ballot,$ad_id,$comment_date,$revision,$active,$comment_text)",$program_name,$user_name);
  }

}

############################################################
#
# Function : detach_ballot
# Parameters:
#   $q - CGI variables
# return : HTML text to display view draft page
#
#   This function separates the current draft from it's action group
# 
############################################################
sub detach_ballot {
   my $q = shift;
   my $dTag = $q->param("dTag");
   my $old_ballot = $q->param("ballot_id");
   my $new_ballot = db_select($dbh,"select max(ballot_id) from id_internal");
   $new_ballot++;      # Get a new ballot id
   my $sqlStr = qq {
   update id_internal
   set ballot_id = $new_ballot,
       primary_flag = 1,
       event_date = CURRENT_DATE
   where id_document_tag = $dTag
   };
   my $ballot_exist = db_select($dbh,"select count(*) from ballot_info where ballot_id = $old_ballot");
   unless (db_update($dbh,$sqlStr,$program_name,$user_name)) {
     return $error_msg;
   }
   copy_ballot($old_ballot,$new_ballot) if ($ballot_exist);
   return view_id($q);
}

sub make_last_call_pre {
  my $q=shift;
  my $ballot_id = $q->param("ballot_id");
  my ($rfc_flag,$dTag) = db_select($dbh,"select rfc_flag,id_document_tag from id_internal where ballot_id=$ballot_id and primary_flag=1") or error_log("select rfc_flag,id_document_tag from id_internal where ballot_id=$ballot_id and primary_flag=1");
  my $filename = $q->param("filename");
  $filename = db_select($dbh,"select rfc_name from rfcs where rfc_number = $dTag") if ($rfc_flag);
  my $group_acronym_id = db_select($dbh,"select group_acronym_id from internet_drafts where filename='$filename'");
  my $IDs = "";
  my $html_txt = "<h2>Make Last Call for following I-D(s):</h2>\n";
  my $sqlStr = qq{select i.id_document_tag,filename,revision,status_value,acronym from id_internal idi,internet_drafts i,id_intended_status iis, acronym a
where idi.ballot_id = $ballot_id and
idi.id_document_tag = i.id_document_tag and
i.intended_status_id = iis.intended_status_id and
i.group_acronym_id = a.acronym_id
};
  my @docList = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
  my $lc_sent_date = db_select($dbh,"select CURRENT_DATE");
  my $lc_expiration_date = db_select($dbh,"select date_add(CURRENT_DATE,interval 14 day)");
  $lc_expiration_date = db_select($dbh,"select date_add(CURRENT_DATE,interval 28 day)") if ($group_acronym_id==1027);
  for $array_ref(@docList) {
    my ($id_document_tag,$filename,$revision,$status_value,$group_acronym) = rm_tr(@$array_ref);
    $html_txt .= "$filename ($group_acronym) - $status_value<br>\n";
    $IDs .= "$id_document_tag,";
  }
  chop($IDs);
  $html_txt .= qq{
<br><br>
$form_header_search
<input type="hidden" name="command" value="make_last_call">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="filename" value="$filename">
<input type="hidden" name="IDs" value="$IDs">
Last Call Sent Date: <input type="text" name="lc_sent_date" value="$lc_sent_date"><br>
Last Call Expiration Date: <input type="text" name="lc_expiration_date" value="$lc_expiration_date"><br>
<input type="submit" value="Make Last Call"><input type="reset">
</form>
<br>
$close_button
};
  return $html_txt;

}


sub make_last_call {
  my $q = shift;
  my $ballot_id = $q->param("ballot_id");
  my $filename = $q->param("filename");
  my $lc_sent_date = db_quote($q->param("lc_sent_date"));
  my $lc_expiration_date = db_quote($q->param("lc_expiration_date"));
  my $IDs = $q->param("IDs");
  my ($dTag,$rfc_flag) = db_select($dbh,"select id_document_tag,rfc_flag from id_internal where ballot_id=$ballot_id and primary_flag=1") or error_log("select id_document_tag,rfc_flag from id_internal where ballot_id=$ballot_id and primary_flag=1");
  my $sqlStr = qq{select a.revision, a.group_acronym_id,b.email_address from internet_drafts a, 
groups_ietf b where a.filename='$filename' and a.group_acronym_id=b.group_acronym_id};
  my ($revision,$group_acronym_id,$group_email) = db_select($dbh,$sqlStr) or error_log($sqlStr);
  $group_email = "" if ($group_acronym_id ==  1027);
  if ($group_email =~ /ietf.org/) {
    my @temp = split '\@',$group_email;
    $group_email = "$temp[0]\@odin.ietf.org";
  }
  my $last_call_text = rm_tr(db_select($dbh,"select last_call_text from ballot_info where ballot_id=$ballot_id"));
  open (OUT,">$REC_DIR/$filename.lastcall");
  print OUT $last_call_text;
  close OUT;
  $last_call_text =~ s/IETF-Announce :;/ietf-announce\@ietf.org/;
  
#  my $iprlinks = "\n\nThe following IPR Declarations may be related to this I-D:\n\n";
  my $filefrag = substr $filename, 0, -4;
  my $sqlStr = qq{select ipr_id from ipr_detail where document_title like "%$filefrag%"};
  my @iprList = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);

  if (@iprList)
  {
    my $iprlinks = "\n\nThe following IPR Declarations may be related to this I-D:\n\n";
    for my $array_ref (@iprList) {
    my ($ipr) = @$array_ref;
     $iprlinks .= "https://merlot.tools.ietf.org/ipr/$ipr/ \r\n";
     }
  }
  else
  {
   my $iprlinks = "No IPR declarations were found that appear related to this I-D.";
  } 

  $last_call_text .= $iprlinks;

  
    open MAIL, "| /usr/lib/sendmail -t" or return 0;
  print MAIL <<END_OF_MESSAGE;
$X_MAIL_HEADER
$last_call_text
$TEST_MESSAGE
END_OF_MESSAGE

  close MAIL or return "<h2>Could not send notification to IESG Secretariat</h2>";
  mail_log($program_name,$last_call_text,$last_call_text,$user_name); 
  update_state($ballot_id,16,0,$test_mode,$devel_mode,$loginid);
  my $ad_id = db_select($dbh,"select job_owner from id_internal where ballot_id = $ballot_id") or error_log("select job_owner from id_internal where ballot_id = $ballot_id");
  my $ad_name = get_mark_by($ad_id,1);
  db_update($dbh,"update internet_drafts set lc_sent_date=$lc_sent_date, lc_expiration_date=$lc_expiration_date where id_document_tag in ($IDs)",$program_name,$user_name);
  my $comment_text = qq{Last Call has been made for $filenames ballot and state has been changed to 'In Last Call'};
  email_to_AD("$filename-$revision.txt",$comment_text,"",$ad_id,"$TRACKER_URL?command=view_id&dTag=$dTag&rfc_flag=$rfc_flag",$test_mode,$devel_mode,$loginid);
  send_iana_message($ballot_id,$last_call_text,'drafts-lastcall');
  my $ad_name = get_mark_by($ad_id,1);
  my $html_txt = qq{<h3>$REC_DIR/$filename.lastcall</h3>has been created.
<h3>Last Call Announcement has been sent out</h3>
<h3>Notification has been sent out to $ad_name</h3>
<hr>
$close_button
};
  return $html_txt;
}

sub get_action_html {
  my $ballot_id = shift;
  my $action_html = "<a name=\"action\"></a><table border=\"1\" bgcolor=\"black\"> <tr><td><font color=\"white\"><h3>Ballot Set</h3></font>\n";
  my $sqlStr = qq{
  select state.id_document_tag, state.status_date,state.event_date,state.job_owner,
  state.cur_state,state.cur_sub_state_id,state.assigned_to,state.rfc_flag,state.ballot_id,1,id.filename
  from id_internal state left outer join internet_drafts id
  on state.id_document_tag = id.id_document_tag
  left outer join rfcs rfc on state.id_document_tag = rfc.rfc_number
  where state.ballot_id = $ballot_id
  AND state.primary_flag = 1
  };
      #return $sqlStr;
  my @action_list = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
  $action_html .= display_all(0,0,@action_list);
  $action_html .= "</td></tr></table>";
  return $action_html;
}

sub do_resurrect {
  my $q=shift;
  my $id_document_tag = $q->param("id_document_tag");
  my ($filename,$revision) = db_select($dbh,"select filename,revision from internet_drafts where id_document_tag=$id_document_tag") or error_log("select filename,revision from internet_drafts where id_document_tag=$id_document_tag");
  $filename .= "-$revision.txt";
  my $person_or_org_tag = db_select($dbh,"select person_or_org_tag from iesg_login,id_internal where id_document_tag=$id_document_tag and rfc_flag=0 and resurrect_requested_by=id") or error_log("select person_or_org_tag from iesg_login,id_internal where id_document_tag=$id_document_tag and rfc_flag=0 and resurrect_requested_by=id");
  my $name=get_name($person_or_org_tag);
  my $email=get_email($person_or_org_tag);
  my $to="$name <$email>";
  my $from = "I-D Administrator <internet-drafts-reply\@ietf.org>";
  my $subject = "I-D Resurrection Completed - $filename";
  $text = qq{
As you requested, the Internet-Draft $filename has been resurrected.

ID Tracker URL: https://merlot.tools.ietf.org/cgi-bin/idtracker.cgi?command=view_id&dTag=$id_document_tag&rfc_flag=0
                                                                                         
<EOM>
};
  send_mail($program_name,$user_name,$to,$from,$subject,$text);
  add_document_comment($loginid,$id_document_tag,"This document has been resurrected");
  db_update($dbh,"update id_internal set resurrect_requested_by=0 where id_document_tag=$id_document_tag",$program_name,$user_name);
  return qq{<br><br><font size=+2>I-D is resurrection has been completed and the message has been sent to the AD.</font><br><br>
};
}
sub resurrect {
  my $q=shift;
  my $id_document_tag=$q->param("id_document_tag");
  my $ballot_id = $q->param("ballot_id");
  my $rfc_flag=$q->param("rfc_flag");
  my ($filename,$revision) = db_select($dbh,"select filename,revision from internet_drafts where id_document_tag=$id_document_tag") or error_log("select filename,revision from internet_drafts where id_document_tag=$id_document_tag");
  $filename .= "-$revision.txt";
  my $person_or_org_tag = db_select($dbh,"select person_or_org_tag from iesg_login where id=$loginid");
  my $name=get_name($person_or_org_tag);
  my $email=get_email($person_or_org_tag);
  
  my $to="I-D Administrator <internet-drafts\@ietf.org>";
  my $from = "$name <$email>";
  my $subject = "I-D Resurrection Request";
  $text = qq{I-D that is requested to be resurrected: $filename
Requested by: $name <$email>
ID Tracker URL: https://merlot.tools.ietf.org/cgi-bin/idtracker.cgi?command=view_id&dTag=$id_document_tag&rfc_flag=$rfc_flag&ballot_id=$ballot_id

<EOM>
};
  send_mail($program_name,$user_name,$to,$from,$subject,$text); 
  add_document_comment($loginid,$id_document_tag,"I-D Resurrection was requested");
  db_update($dbh,"update id_internal set resurrect_requested_by=$loginid where id_document_tag=$id_document_tag",$program_name,$user_name);
  return qq{
<br><br><Br><hr>
<font size=+2>A notification has been sent to the Secretariat to resurrect this I-D.<br>
<hr><br><br></font>
};
}
############################################################
#
# Function : view_id
# Parameters:
#   $q : CGI variables
# return : HTML text to view draft
#
# Many main feature of this application can be performed within this page.
# One can change state of draft, update any information, view action group
# if existed, add a draft to current action group, detach current draft from its
# action group, add a comment about current draft, and view any previous comment.
#
############################################################
sub view_id {
   my $q = shift;
   my $dTag = $q->param("dTag");
   unless (my_defined($q->param("dTag"))) {
     my $filename = $q->param("filename");
     $dTag = db_select($dbh,"select id_document_tag from internet_drafts where filename='$filename'") if (my_defined($filename));
   }
   my $rfc_flag = $q->param("rfc_flag");
   my $name_col = "Draft Name";
   $name_col = "Rfc Name" if ($rfc_flag);
   my $from_field = "";
   if ($rfc_flag == 1) {
	   $sqlStr = qq{
	   select rfc.group_acronym,rfc.rfc_name, rfc.online_version, state.status_date,state.note,state.agenda,state.event_date,state.area_acronym_id, state.via_rfc_editor, state.cur_state,state.prev_state,state.cur_sub_state_id,state.prev_sub_state_id,state.assigned_to,state.job_owner,state.ballot_id, state.telechat_date, rfc.intended_status_id,state.primary_flag, state.state_change_notice_to
	   
	   from rfcs rfc ,
	   id_internal state
	   where rfc.rfc_number = state.id_document_tag
	   AND state.id_document_tag = $dTag
	   AND state.rfc_flag = 1
	   };

   } else {
	   $sqlStr = qq{
	   select id.group_acronym_id, id.filename, id.revision, state.status_date,state.note,state.agenda,state.event_date,state.area_acronym_id, state.via_rfc_editor, state.cur_state,state.prev_state,state.cur_sub_state_id,state.prev_sub_state_id,state.assigned_to,state.job_owner,state.ballot_id, state.telechat_date, id.intended_status_id,state.primary_flag, state.state_change_notice_to,id.expired_tombstone
	   from internet_drafts id,
	   id_internal state
	   where id.id_document_tag = state.id_document_tag
	   AND state.id_document_tag = $dTag
	   AND state.rfc_flag = 0
	   };
   }
   #return $sqlStr;
   my ($group_flag,$filename,$revision,$status_date,$note,$agenda,$event_date,$area_acronym_id,$via_rfc_editor,$cur_state,$prev_state,$cur_sub_state_id,$prev_sub_state_id,$assigned_to,$job_owner,$ballot_id,$telechat_date,$status_id,$primary_flag,$state_change_notice_to,$expired_tombstone) = rm_tr(db_select($dbh,$sqlStr));
   return "<h2>ERROR:<i>Unknown I-D</i></h2>" unless (my_defined($filename));
   my $id_status_option_str = get_id_status_option_str($status_id,$rfc_flag); 
   my $rfc_editor_state = ($cur_state == 31)?"<a href=\"http://www.rfc-editor.org/queue.html#$filename\">[RFC Editor State]</a>":"";
   if ($rfc_flag == 1) {
      $revision = "RFC $dTag";
   }
   my $wg_name = $group_flag;
   $wg_name = db_select($dbh,"select acronym from acronym where acronym_id=$group_flag") if ($group_flag =~ /\d/);
   my $id_submission = "WG &lt;$wg_name&gt; submission";
   $id_submission = "Individual submission" if ($group_flag == 1027 or $group_flag eq "none");
   $id_submission = "Submission via IRTF or RFC Editor" if ($via_rfc_editor);
   $note = unformat_textarea($note);
   my $checked = "";
   $checked = "checked" if ($agenda == 1);
   my $ballot_count = db_select($dbh,"select count(*) from id_internal where ballot_id = $ballot_id");
   my $ad_option_str = get_ad_option_str($job_owner); #Get Area Directors List
   my $action_html = ""; 
   my $action_list_html = "";
   my $detach_button = "";
   if ($ballot_count > 1) { # If an action group existed
      if  ($primary_flag == 0) {
      # Create Detach Button
        $detach_button = qq {$form_header  
        <input type="hidden" name="command" value="detach_ballot">
	  <input type="hidden" name="dTag" value="$dTag">
          <input type="hidden" name="ballot_id" value="$ballot_id">
	  <input type="hidden" name="rfc_flag" value="$rfc_flag">
	  <td>
	  <input type="submit" value="Separate from Ballot Set">
       </td></form>
	  };
      } 
        # Create a short cut to action list
        $action_list_html = "<div align=\"right\"><a href=\"#action\">Ballot Set</a></div>";
        # Create an action list
        $action_html .= get_action_html($ballot_id);
   }
   # Create Add Sub draft button
   my $add_sub_html = "";
#  my $add_sub_html = qq {
#  $form_header
#  <input type="hidden" name="command" value="add_action">
#  <input type="hidden" name="ballot_id" value="$ballot_id">
#  <input type="hidden" name="dTag" value="$dTag">
#  <td><input type="submit" value="Add a document to this ballot"></td></form>
#  };
   my $html_txt = "";
   my $prev_state_txt = db_select($dbh,"select document_state_val from ref_doc_states_new where document_state_id = $prev_state");
   $prev_state_txt = qq {<a href="${program_name}?command=view_state_desc&id=$prev_state">$prev_state_txt</a> };
   if ($prev_sub_state_id > 0) {
     my $prev_sub_state = get_sub_state($prev_sub_state_id);
     $prev_sub_state = qq { <a href="${program_name}?command=view_state_desc&id=$prev_sub_state_id&sub_state=1">$prev_sub_state</a>};
     $prev_state_txt .= " :: $prev_sub_state";
   }
   my $cur_state_txt = db_select($dbh,"select document_state_val from ref_doc_states_new where document_state_id = $cur_state");
   $cur_state_txt = qq {<a href="${program_name}?command=view_state_desc&id=$cur_state">$cur_state_txt</a> };
   if ($cur_sub_state_id > 0) {
     my $cur_sub_state = get_sub_state($cur_sub_state_id);
     $cur_sub_state = qq { <a href="${program_name}?command=view_state_desc&id=$cur_sub_state_id&sub_state=1">$cur_sub_state</a>};
     $cur_state_txt .= " :: $cur_sub_state";
   }
   $cur_state_txt .= " $rfc_editor_state";
   my $next_state_option_str = get_option_str("ref_doc_states_new");
   my $next_state_buttons_str = get_next_state_button_str($cur_state);
   my $sub_state_select_str = get_sub_state_select(-1);
   my $row_color = $fColor;

   
   my $area_acronym_str = "";
   my $area_option_str = get_area_option_str($area_acronym_id);
   my $gID = ($rfc_flag)?db_select($dbh,"select acronym_id from acronym a, rfcs b where a.acronym=b.group_acronym and rfc_number=$dTag"):db_select($dbh,"select group_acronym_id from internet_drafts where id_document_tag = $dTag");
   if ($gID == 1027) {
      $area_acronym_str = qq {
	  <tr><td>Area Acronym:</td>
	  <td><select name="area_acronym_id">
	  $area_option_str
	  </select></td>
	  </tr>
	  };
   }

   my $ballot_link = "";
   my $ballot_button = "";
   my $write_up_button = "";
   my $make_last_call_button = "";
   my $ballot_exist = 0;
   my $ballot_name = $filename;
   my $status_value = db_select($dbh,"select status_value from internet_drafts a, id_status b where id_document_tag=$dTag and a.status_id=b.status_id");
   my $replace_info = get_replaced_by_info($status_value,$dTag,"iesg");
   my $filename_with_link=qq{<a href="http://www.ietf.org/internet-drafts/$filename-$revision.txt">$filename-$revision.txt</a>};
   unless ($status_value eq "Active") {
     $revision = decrease_revision($revision) unless $expired_tombstone;
     $filename_with_link = "$filename-$revision.txt($status_value)";
   }
   if ($rfc_flag==1) {
      $ballot_name = "RFC${dTag}";
      $filename_with_link=qq|<a href="http://www.ietf.org/rfc/rfc${dTag}.txt">$filename</a>|;
   }
   $replace_info .= get_replaces_info($dTag,"iesg") if ($replaces_ids_list =~ /,$dTag,/);
   my $valid_count = db_select($dbh,"select count(id_document_tag) from internet_drafts where id_document_tag=$dTag");
   $valid_count = db_select($dbh,"select count(rfc_number) from rfcs where rfc_number=$dTag") if ($rfc_flag);
######### Ballot Process ############
# if ($devel_mode) {
 if ($valid_count or $ADMIN_MODE) {
   if ($primary_flag) {
       my $button_name="Ballot Write-ups";
       my $valid_count = db_select($dbh,"select count(id_document_tag) from id_internal where id_document_tag=$dTag and cur_state < 15");
       $button_name = "Prepare for Last Call" if ($valid_count);
       $write_up_button = qq{
          <a href="${program_name}?command=ballot_writeup&filename=$filename&ballot_id=$ballot_id">[$button_name]</a>
};
   }
   if ($ADMIN_MODE and $cur_state < 20) {
     $make_last_call_button = qq{
<a href="${program_name}?command=make_last_call_pre&ballot_id=$ballot_id&filename=$filename">[Make Last Call]</a><!---"--->};
   }
      my $active_ballot = db_select($dbh,"select ballot_issued from ballot_info where ballot_id = $ballot_id");
      $ballot_button = qq {
          <a href="${program_name}?command=open_ballot&id_document_tag=$dTag">[Open Web Ballot]</a>
} if ($active_ballot);
 } 
# } ## End of if (devel_mode)
######################################

   if (-e "$EVAL_DIR/${ballot_name}.bal") {
      $ballot_link = "<a href=\"http://www.ietf.org/iesg/evaluation/${ballot_name}.bal\">[Open Ballot]</a>";
      unless ($ADMIN_MODE or $devel_mode) {
        $ballot_button = "";
        #$write_up_button = "";
      }
   }
   $ballot_exist = 1;
   $status_date = convert_date($status_date,1);
   my $default_telechat_date = "";
   if (my_defined($telechat_date) and $telechat_date ne "0000-00-00") {
     $default_telechat_date = "<option value=\"$telechat_date\">$telechat_date</option>\n";
   }
   my $via_rfc_checked = numtocheck($via_rfc_editor);
   my $via_rfc_checkbox = "";
   $via_rfc_checkbox = qq{&nbsp; Via IRTF or RFC Editor? <input type="checkbox" name="via_rfc_editor" $via_rfc_checked>} if ($ADMIN_MODE);
   my $id_status_id = db_select($dbh,"select status_id from internet_drafts where id_document_tag = $dTag");
   my $expired_tickler = "";
   my $expired = 0;
   if ($id_status_id==2 and $rfc_flag==0) {
     $expired_tickler = qq{
<font size=+3 color="red"> *** EXPIRED ***</font><br>
<table><tr><Td>
<font size=+1>You can't process an expired I-D - </font></td>};
     my $resurrect_requested = db_select($dbh,"select resurrect_requested_by from id_internal where id_document_tag=$dTag");
     unless ($resurrect_requested) {
       $expired_tickler .= qq{
$form_header
<input type="hidden" name="command" value="resurrect">
<input type="hidden" name="loginid" value="$loginid">
<input type="hidden" name="id_document_tag" value="$dTag">
<input type="hidden" name="rfc_flag" value="$rfc_flag">
<input type="hidden" name="ballot_id" value="$ballot_id">
<td>
<input type="submit" value="resurrect it first">
</td>
</form>
</tr></table>
};
     } else {
       my $ad_login_name = db_select($dbh,"select login_name from iesg_login where id=$resurrect_requested");
       $expired_tickler .= qq{<Td>
<font size=+1>I-D Resurrection was requested by $ad_login_name
</td></tr></table>
};
     }
     $expired = 1;
  } 

   $html_txt .= qq|
   $table_header
   <script language="javascript">
   function check_date (selectedIndex) {
     if (document.f.agenda.checked) {
       var selected_date = document.f.telechat_date.options[selectedIndex].value;
       var dateStr = new String(selected_date);
       var splitStr = dateStr.split("-");
       var converted_date = splitStr[1] + "/" + splitStr[2] + "/" + splitStr[0];
       var Today = new Date();
       var S_date = new Date(converted_date);
       var diff = S_date.getTime() - Today.getTime();
       if (diff < 0) {
         alert("You can not select a past telechat date");
         document.f.agenda.checked = false;
       }
     }
   }
   function check_expired () {
     if ($expired == 1) {
       alert ("This action is prohibited for an expired I-D");
       return false;
     } else {
       return true;
     }
   }
   </script>

   <tr bgcolor="BEBEBE" align="center"><th colspan="2"><div id="largefont">Detail Info</div> $action_list_html $expired_tickler</th></tr>
   <form action="$program_name" method="POST" name="f">
   <input type="hidden" name="loginid" value="$loginid">
   <input type="hidden" name="command" value="update_id">
   <input type="hidden" name="rfc_flag" value="$rfc_flag">
   <input type="hidden" name="dTag" value="$dTag">
   <input type="hidden" name="expired" value="$expired">
   <input type="hidden" name="version" value="$revision">
   <input type="hidden" name="prev_state" value="$prev_state">
   <input type="hidden" name="cur_state" value="$cur_state">
   <input type="hidden" name="cur_sub_state_id" value="$cur_sub_state_id">
   <input type="hidden" name="prev_sub_state_id" value="$prev_sub_state_id">
   <input type="hidden" name="old_id_intended_status" value="$status_id">
   <input type="hidden" name="old_status_date" value="$status_date">
   <input type="hidden" name="old_area_acronym_id" value="$area_acronym_id">
   <input type="hidden" name="old_job_owner" value="$job_owner">
   <input type="hidden" name="old_telechat_date" value="$telechat_date">
   <input type="hidden" name="old_state_change_notice_to" value="$state_change_notice_to">
   <input type="hidden" name="owner_mode" value="$owner_mode">
   <input type="hidden" name="ballot_exist" value="$ballot_exist">
   <tr bgcolor="white"><td>$name_col: </td><td>$filename_with_link <b><font color="red">($id_submission)</font></b> $via_rfc_checkbox $ballot_link $ballot_button $write_up_button $make_last_call_button$replace_info</td></tr>
   <tr bgcolor="white"><td>Version: </td><td>$revision</td></tr>
   <tr bgcolor="white"><td>Intended Status: </td>
   <td>
   <select name="id_intended_status" onClick="return check_expired();">
   $id_status_option_str
   </select>
   &nbsp; &nbsp; Agenda? <input type="checkbox" name="agenda" $checked onClick="check_date(document.f.telechat_date.selectedIndex);return check_expired();"> on 
   <select name="telechat_date"  onChange="check_date(document.f.telechat_date.selectedIndex);return check_expired();"  onClick="return check_expired();">$default_telechat_date $telechat_date_list</select>
   <input type="hidden" name="agenda_present" value="1">
   </td></tr>
   $area_acronym_str
   <tr bgcolor="white"><td>Previous State: </td>
   <td>
   <a href="${program_name}?command=view_state_desc&id=$prev_state">$prev_state_txt</a>
   </td></tr>
   <tr><td>Current State: </td>
   <td>
   $cur_state_txt
   </td></tr>
   <tr bgcolor="white"><td>Next State: </td>
   <td>
   <br>
   <select name="next_state" onClick="return check_expired();">
   <option value="0">---Select Next State</option>
   $next_state_option_str
   </select> with sub state in   
   $sub_state_select_str 
   <a href="https://merlot.tools.ietf.org/public/states_table.cgi"> Show States Table</a>
   <br>
   or<br>
   $next_state_buttons_str
   <br>or<br>   
   <input type="submit" value="Back to Previous State" name="process_prev_button"  onClick="return check_expired();"><br><br>
   </td></tr>
   <tr bgcolor="white">
   <td>Responsible AD:</td>
   <td>
   <select name="job_owner" onClick="return check_expired();">
   $ad_option_str
   </select>
   <input type="submit" name="assign_to_me" value="Assign to me" onClick="return check_expired();">
   </td>
   </tr>
   <tr bgcolor="white">
   <td>Status Date:<br>(YYYY-MM-DD)</td>
   <td><input type="text" name="status_date" value="$status_date">
   </td>
   </tr>
   <tr bgcolor="white"><td>Brief Note:<br>(IRTF or RFC Editor and other notes<br>
are entered on the ballot page.)</td><td>
   <textarea name="note" rows="3" cols="74" wrap="virtual">$note</textarea>
   </td></tr>
   <tr bgcolor="white"><td>Comment:</td><td>
   <textarea name="comment" rows="10" cols="74" wrap="virtual"></textarea>
   <input type="checkbox" name="public_flag" checked> Public</td></tr>
   <tr bgcolor="white"><td>State or Version Change<br>Notice To:</td>
   <td><input type="text" name="state_change_notice_to" value="$state_change_notice_to" size="56"> <b>A comma must exist between email addresses</b></td></tr>
   <tr bgcolor="white">
   <td width="140"><input type="submit" value="   UPDATE    "><input type="reset" value="RESET"></td></form>
   <td>
   $table_header
   <tr>
   $add_sub_html
   $detach_button
   $form_header
   <input type="hidden" name="command" value="main_menu">
   <td><input type="submit" value="Main Menu"></td></form>
   </tr>
   </table>
   </td>
   </tr>
   
   </table>
  
   <h3>Comment Log</h3>
   $table_header
   <tr bgcolor="$fColor"><th>Date</th><th>Version</th><th>Comment</th></tr>
   |;
   $sqlStr = qq{
   select id,comment_date,version,comment_text,public_flag,created_by,ballot from document_comments
   where document_id = $dTag
   order by 1 desc
   };
#"

   my @commentList = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
   for $array_ref (@commentList) {
      my ($id,$comment_date,$version,$comment_text,$public_flag,$created_by,$ballot) = @$array_ref;
          my $owner_id = db_select($dbh,"select login_name from iesg_login where id=$created_by");
          $owner_id = "system" unless $owner_id;
	  $comment_date = convert_date($comment_date,1);
          $comment_text = format_textarea($comment_text); 
          $comment_text = reduce_text($comment_text,4);
	  if ($public_flag == 1) {
	     $pre_str = "$public_txt-$owner_id]</font>";
	  } else {
	     $pre_str = "$private_txt-$owner_id]</font>";
	  }
          $pre_str .= qq{ <font color="red">[IN IESG DISCUSSION <b>*discuss*</b>]</font> } if ($ballot == 1);
          $pre_str .= qq{ <font color="red">[IN IESG DISCUSSION <b>*comment*</b>]</font> } if ($ballot == 2);
	  if ($row_color eq $fColor) {
	     $row_color = $sColor;
	  } else {
	     $row_color = $fColor;
	  }
	  my $button_str = "";
	  if ($created_by == $loginid) {
	     $button_str = qq{
	  $form_header
	  <input type="hidden" name="command" value="toggle_comment">
	  <input type="hidden" name="comment_id" value="$id">
	  <input type="hidden" name="dTag" value="$dTag">
	  <input type="hidden" name="rfc_flag" value="$rfc_flag">
	  <td>
	  <input type="submit" value="Toggle Private/Public">
	  </td>
	  </form>
		 };
	  }
	  $html_txt .= qq {
	  <tr bgcolor="$row_color"><td>$comment_date</td><td align="center">$version</td><td width="700">$pre_str $comment_text</td>
	  $form_header
          <input type="hidden" name="command" value="view_comment">
          <input type="hidden" name="id" value="$id"> 
	  <td>
          <input type="submit" value="View Detail">
	  </td>
	  </form>
	  $button_str
	  </tr>
	  };
   }

   $html_txt .= "</table><br><br>\n$action_html\n";
   return $html_txt;
}

sub view_state_desc {
  my $q = shift;
  my $id = $q->param("id");
  my $sqlStr;
  if (defined($q->param("sub_state"))) {
    $sqlStr = "select sub_state_val,sub_state_desc from sub_state where sub_state_id = $id";
  } else {
    $sqlStr = "select document_state_val,document_desc from ref_doc_states_new where document_state_id = $id";
  }
  my ($state_name,$state_desc) = rm_tr(db_select($dbh,$sqlStr));
  $state_desc = format_textarea($state_desc);
  my $html_txt = qq{<h3>$state_name</h3>
$state_desc
};
  return $html_txt;
}




###########################################################
#
# Function : toggle_comment
# Parameters :
#   $q - CGI variables
# return: Error message if updating database is failed
#         HTML text of view draft page if successful
#
# This function toggles the private/public flag of comment
#
###########################################################
sub toggle_comment {
   my $q = shift;
   my $comment_id = $q->param("comment_id");
   my $new_public_flag = db_select($dbh,"select public_flag from document_comments where id=$comment_id");
   if ($new_public_flag == 1) {
     $new_public_flag = 0;
   } else {
     $new_public_flag = 1;
   }
   my $sqlStr = "update document_comments set public_flag = $new_public_flag where id = $comment_id";
   unless (db_update($dbh,$sqlStr,$program_name,$user_name)) {
     return $error_msg;
   }
   return view_id($q);
}

###########################################################
#
# Function : update_id
# Parameters:
#    $q : CGI variables
# return: Error message if updating databse is failure
#         HTML text of view draft page if successful
#
# This function update any content of record 
#
##########################################################
sub update_id {
   my $q = shift;
   my $dTag = $q->param("dTag");
   my $prev_sub_state_id = $q->param("prev_sub_state_id");
   my $sub_state_id = $q->param("sub_state_id");
   my $cur_sub_state_id = $q->param("cur_sub_state_id");
   my $expired = $q->param("expired");
   return qq{<br><br><br><hr>
<font size=+2>You cannot process an expired I-D.<br>
Please go back and resurrect this I-D first.
<hr><br><br>
</font>}  if ($expired and $sub_state_id > -1);
   my $ballot_id = db_select($dbh,"select ballot_id from id_internal where id_document_tag=$dTag");
   my $rfc_flag = $q->param("rfc_flag");   # RFC or ID
   my $area_acronym_id = $q->param("area_acronym_id");
   my $update_via_rfc_editor = "";
   if ($ADMIN_MODE) {
     if (defined($q->param("via_rfc_editor"))) {
       $update_via_rfc_editor = "via_rfc_editor = 1,";
     } else {
       $update_via_rfc_editor = "via_rfc_editor = 0,";
     }
   }
   my $update_area_acronym = "";
   if (my_defined($area_acronym_id)) {
      $update_area_acronym = "area_acronym_id = $area_acronym_id,";
   }
   my $agenda = (defined($q->param("agenda")))?checktonum($q->param("agenda")):0;
   $agenda = db_select($dbh,"select agenda from id_internal where id_document_tag = $dTag and rfc_flag=$rfc_flag") unless (defined($q->param("agenda_present"))); 
   #my $agenda = (defined($q->param("agenda")))?checktonum($q->param("agenda")):db_select($dbh,"select agenda from id_internal where id_document_tag = $dTag and rfc_flag=$rfc_flag");
   my $telechat_date = $q->param("telechat_date");
   my $cur_state = $q->param("cur_state"); # Current State
   my $prev_state = $q->param("prev_state"); # Previous State
   $cur_state=db_select($dbh,"select cur_state from id_internal where id_document_tag=$dTag and rfc_flag=$rfc_flag") unless my_defined($cur_state);
   $prev_state=db_select($dbh,"select prev_state from id_internal where id_document_tag=$dTag and rfc_flag=$rfc_flag") unless my_defined($prev_state);
   my $next_state = $q->param("next_state"); # Next State
   #Convert date to appropriate format along with current Database
   my $status_date = $q->param("status_date");
   unless (validate_date($status_date)) {
      return qq{<h3>Invalid Status Date</h3>
<hr>
<li>Date should be in YYYY-MM-DD format<br>
<li>Date can't be prior to current date<br>
<li>Date can't be beyond two years after current date<br>
};
   }
   $status_date = convert_date($status_date,$CONVERT_SEED);
   my $mark_by = $loginid; # Marked by
   my $comment = $q->param("comment"); #Comment
   my $job_owner = (defined($q->param("job_owner")))?$q->param("job_owner"):db_select($dbh,"select job_owner from id_internal where id_document_tag = $dTag and rfc_flag=$rfc_flag"); #Assigned to
   $job_owner = $loginid if (defined($q->param("assign_to_me")));
   my $old_note = db_select($dbh,"select note from id_internal where id_document_tag = $dTag and rfc_flag=$rfc_flag");
   my $note = (defined($q->param("note")))?$q->param("note"):$old_note;
   $note = db_quote(format_textarea($note)); 
   my $old_area_acronym_id = $q->param("old_area_acronym_id");
   my $old_telechat_date = $q->param("old_telechat_date");
   my $update_returning_item = "";
   my $update_telechat_date = "";
   if ($agenda and $old_telechat_date ne $telechat_date) {
      $update_returning_item = "returning_item = 1," if ($old_telechat_date ne "0000-00-00" and my_defined($old_telechat_date));
      $update_telechat_date = "telechat_date = '$telechat_date',";
   }
   my $old_status_date = convert_date($q->param("old_status_date"),$CONVERT_SEED);
   my $old_assigned_to = $q->param("old_assigned_to");
   my $old_job_owner = (defined($q->param("old_job_owner")))?$q->param("old_job_owner"):$job_owner; 
   my $old_state_change_notice_to = (defined($q->param("old_state_change_notice_to")))?$q->param("old_state_change_notice_to"):db_select($dbh,"select state_change_notice_to from id_internal where id_document_tag = $dTag and rfc_flag=$rfc_flag");
   my $state_change_notice_to = $q->param("state_change_notice_to");
   my $public_flag = (defined($q->param("public_flag")))?1:0; #Public or Private
   my $version = db_select($dbh,"select revision from internet_drafts where id_document_tag = $dTag");
   $version = db_quote($version);
   my $html_txt = "Updated...";
   my $cur_time = db_quote(get_current_time());
   my $id_intended_status = $q->param("id_intended_status");
   my $old_id_intended_status = $q->param("old_id_intended_status");
   my $update_iis_sql = qq {update internet_drafts
   set intended_status_id = $id_intended_status
   where id_document_tag = $dTag
   };
   $update_iis_sql = qq{update rfcs set intended_status_id = $id_intended_status
   where rfc_number = $dTag} if ($rfc_flag);
   my $owner_mode = 1;
   if ($mark_by != $old_job_owner) {
      $owner_mode = 0;
   }
   #return $sqlStr;
   my $token_name = db_quote(get_mark_by($job_owner));
   $sqlStr = qq {
   select email_address from email_addresses e,iesg_login i
   where i.id = $job_owner
   AND i.person_or_org_tag = e.person_or_org_tag
   AND e.email_priority = 1
   };
   my $token_email = db_quote(rm_tr(db_select($dbh,$sqlStr)));
   my $log_txt = "";
   if (defined($q->param("process_prev_button"))) {
      $next_state = $prev_state;
   }
   if ($next_state == 0 and defined($q->param("next_state_button"))) {
      my $next_state_val = db_quote($q->param("next_state_button"));
	  $next_state = db_select($dbh,"select document_state_id from ref_doc_states_new where document_state_val = $next_state_val");
          $sub_state_id = 0;
   }
   my $new_mark_by = get_mark_by($loginid,1);

   my $id_status_log = "";
   if ($id_intended_status != $old_id_intended_status) {
      my $new_status = rm_tr(db_select($dbh,"select status_value from id_intended_status where intended_status_id = $id_intended_status"));
      my $old_status = rm_tr(db_select($dbh,"select status_value from id_intended_status where intended_status_id = $old_id_intended_status"));
      if ($rfc_flag) {
         $new_status = rm_tr(db_select($dbh,"select status_value from rfc_intend_status where intended_status_id = $id_intended_status"));
         $old_status = rm_tr(db_select($dbh,"select status_value from rfc_intend_status where intended_status_id = $old_id_intended_status"));
      } 
      $id_status_log .= qq {Intended Status has been changed to <b>$new_status</b> from <b>$old_status</b><br>};
   }
   if (my_defined($status_date) and $old_status_date ne $status_date) {
      $id_status_log .= "Status date has been changed to $status_date from $old_status_date<br>";
   }
   if ($old_state_change_notice_to ne $state_change_notice_to) {
      $id_status_log .= "State Change Notice email list have been change to <b>$state_change_notice_to</b> from $old_state_change_notice_to<br>";
   }
   $state_change_notice_to = db_quote($state_change_notice_to);
   if (my_defined($area_acronym_id) and $old_area_acronym_id != $area_acronym_id) {
      my $new_aval = rm_tr(db_select($dbh,"select acronym from acronym where acronym_id=$area_acronym_id"));
      my $old_aval = rm_tr(db_select($dbh,"select acronym from acronym where acronym_id=$old_area_acronym_id"));
	  $id_status_log .= "Area acronymn has been changed to $new_aval from $old_aval<br>";
   } else {
      $assigned_to = $old_assigned_to;
   }
   if ($old_job_owner != $job_owner) {
      $new_job_owner_str = get_mark_by($job_owner);
	  $old_job_owner_str = get_mark_by($old_job_owner);
	  $id_status_log .= "Responsible AD has been changed to $new_job_owner_str from $old_job_owner_str<br>";
   }
   my $comment_added = "";
   if (my_defined($comment)) {
      $comment_added .= "A new comment added<br>";
   }
   my $email_txt = "";
   if (my_defined($id_status_log) or my_defined($comment_added)) {
      $email_txt = $id_status_log . " $comment_added ";
      $id_status_log .= "by <b>$new_mark_by</b>" if (my_defined($id_status_log));
      $email_txt .= "by $new_mark_by";
      $id_status_log = db_quote($id_status_log) if (my_defined($id_status_log));
   }

   #return update_comment_log($dTag,$version,$mark_by,$cur_state,$prev_state,$comment,$log_txt,$public_flag,$id_status_log);
   return $error_msg unless (update_comment_log($dTag,$version,$mark_by,$cur_state,$prev_state,$comment,$log_txt,$public_flag,$id_status_log));
   ($status_date,$assigned_to) = db_quote($status_date,$assigned_to);
   ###################### Update id_internal Table fields ####################
   my $sqlStr = qq{Update id_internal
   Set status_date = $status_date,
	   assigned_to = $assigned_to,
	   job_owner = $job_owner,
	   mark_by = $mark_by,
	   token_name = $token_name,
	   email_display = $token_name,
	   token_email = $token_email,
           agenda = $agenda,
           state_change_notice_to = $state_change_notice_to,
	   $update_via_rfc_editor
	   $update_area_acronym
           $update_returning_item
           $update_telechat_date
	   event_date = CURRENT_DATE
   Where ballot_id = $ballot_id
   };
   my $pre_agenda = db_select($dbh,"select agenda from id_internal where ballot_id = $ballot_id"); 
   #return $sqlStr;
   unless (db_update($dbh,$sqlStr,$program_name,$user_name)) {
     return $error_msg;
   }
   unless (db_update($dbh,"update id_internal set note=$note, event_date = CURRENT_DATE where ballot_id = $ballot_id")) {
     return $error_msg;
   }
#   if (my_defined($old_note)) {

   if ((my_defined($old_note)) && ($old_note ne "")){

     if ($note eq "''") {
       add_document_comment($loginid,$ballot_id,"Note field has been cleared",1);
     } elsif (db_quote($old_note) ne $note) {
       add_document_comment($loginid,$ballot_id,"[Note]: $note added",1);
     }
   } else {
     if ($note ne "''") {
       add_document_comment($loginid,$ballot_id,"[Note]: $note added",1);
     }
   }
  my $state_changed = "";
  my $last_call_requested=0;
   ################### Update State ####################
   if (($cur_state != $next_state and $next_state != 0) or ($cur_sub_state_id != $sub_state_id and $sub_state_id > -1)) {
     $last_call_requested = 1 if ($next_state == 15);
     $next_state = $cur_state unless ($next_state);
     $state_changed = update_state($ballot_id,$next_state,$sub_state_id,$test_mode,$devel_mode,$loginid);
   }
    my $num_day_telechat_date = db_select($dbh,"select to_days('$telechat_date')");
    my $num_day_current_date = db_select($dbh,"select to_days(current_date)");
    my $valid = $num_day_telechat_date - $num_day_current_date;
 
   if ($agenda != $pre_agenda and $valid > 0) {
     my $comment_text = "";
     if ($agenda) {
        $comment_text = "Placed on agenda for telechat - $telechat_date";
     } else {
        $comment_text = "Removed from agenda for telechat - $telechat_date";
     }
     add_document_comment($loginid,$ballot_id,$comment_text,1);
   } elsif ($agenda and $old_telechat_date ne $telechat_date) {
     $comment_text = "Telechat date was changed to $telechat_date from $old_telechat_date";
     add_document_comment($loginid,$ballot_id,$comment_text,1);
   }
   if ($id_intended_status != $old_id_intended_status) {
      unless (db_update($dbh,$update_iis_sql,$program_name,$user_name)) {
        return $error_msg;
      }
   }
   $email_txt .= "<br>\n$state_changed<br>\n" if (my_defined($state_changed));
   my $filename = "";
   if ($rfc_flag) {
     $filename = "RFC $dTag";
   } else {         ($filename,$revision) = rm_tr(db_select($dbh,"select filename,revision from internet_drafts where id_document_tag = $dTag"));
     $filename = "$filename-$revision.txt";
   } 
   if ((my_defined($email_txt) or my_defined($log_txt)) and $owner_mode == 0) {
      return "<h3>Failed to send an email to AD</h3>" unless (email_to_AD($filename,$email_txt,$log_txt,$old_job_owner,"$TRACKER_URL?command=view_id&dTag=$dTag&rfc_flag=$rfc_flag",$test_mode,$devel_mode,$loginid));
   }
   if ($last_call_requested) {
     my $count = db_select($dbh,"select count(ballot_id) from ballot_info where ballot_id = $ballot_id");
     unless ($count) {
       my $pre_last_call_text = db_quote(gen_last_call_ann($filename,$ballot_id));
       my $pre_approval_text = db_quote(gen_approval_text($filename,$ballot_id));
       my $pre_ballot_writeup_text = db_quote(gen_ballot_writeup_text());
       $sqlStr = "insert into ballot_info (ballot_id,last_call_text,approval_text,ballot_writeup,active) values ($ballot_id,$pre_last_call_text,$pre_approval_text,$pre_ballot_writeup_text,0)";
       db_update($dbh,$sqlStr,$program_name,$user_name);
     }
     $html_txt = notify_ietf($ballot_id,$filename,"last_call",$rfc_flag); 
   } else {
     $html_txt = view_id($q);
   }
   return $html_txt;
}



############################################################
#
# Function : view_comment
# Paramters:
#   $q - CGI variables
# return: HTML text to display detail information of selected comment
#
###########################################################
sub view_comment {
   my $q = shift;
   my $id = $q->param("id");
   my $html_txt = "";
   
   my $sqlStr = qq {
   select document_id,rfc_flag,public_flag,comment_date,comment_time,
   version,comment_text,created_by,result_state,origin_state,ballot
   from document_comments
   where id = $id
   };
   #return $sqlStr;
   my ($document_id,$rfc_flag,$public_flag,$comment_date,$comment_time,$version,$comment_text,$created_by,$result_state,$origin_state,$ballot) = db_select($dbh,$sqlStr);
   my $origin_state_txt = db_select($dbh,"select document_state_val from ref_doc_states_new where document_state_id = $origin_state");
   my $result_state_txt = db_select($dbh,"select document_state_val from ref_doc_states_new where document_state_id = $result_state");
   $comment_date = convert_date($comment_date,1);
   my $created_by_str = get_mark_by($created_by);
   $comment_text = format_textarea($comment_text);
   my $pre_str = "";
   $pre_str .= qq{<h3><font color="red">[IN IESG DISCUSSION <b>*discuss*</b>]</font></h3> } if ($ballot == 1);
   $pre_str .= qq{<h3> <font color="red">[IN IESG DISCUSSION <b>*comment*</b>]</font></h3> } if ($ballot == 2);
   $html_txt .= qq{
$pre_str
   $table_header
   <tr><td><b>Date and Time:</td><td>$comment_date, $comment_time</td></tr>
   <tr><td><b>Version:</td><td>$version</td></tr>
   <tr><td><b>Commented by:</td><td>$created_by_str</td></tr>
   <tr><td><b>State before Comment:</td><td>$origin_state_txt</td></tr>
   <tr><td><b>State after Comment:</td><td>$result_state_txt</td></tr>
   <Tr><td><b>Comment:</td><td>$comment_text</td></tr>
   </table>
<form>
<input type="button" name="back_button" value="Close" onClick="history.go(-1);return true">
</form>

   };
   return $html_txt;
}

sub gen_last_call_ann {
   my $filename = shift;
   my $ballot_id = shift;
   my $cc_line = "Reply-to: ietf\@ietf.org";
   my ($rfc_flag,$id_document_tag) = db_select($dbh,"select rfc_flag, id_document_tag from id_internal where primary_flag=1 and ballot_id=$ballot_id");
  my $sqlStr = qq{select g.email_address,i.id_document_name,i.filename,i.revision,a.name,i.group_acronym_id,b.status_value from groups_ietf g, internet_drafts i, acronym a, id_intended_status b
where i.id_document_tag=$id_document_tag and i.group_acronym_id = g.group_acronym_id
and g.group_acronym_id = a.acronym_id 
and i.intended_status_id = b.intended_status_id
};
  $sqlStr = qq{select g.email_address,i.rfc_name,i.rfc_number,"RFC",i.group_acronym,a.acronym_id, b.status_value from rfcs i, groups_ietf g, acronym a, rfc_intend_status b
where i.rfc_number=$id_document_tag
and i.group_acronym = a.acronym
and a.acronym_id = g.group_acronym_id
and i.intended_status_id = b.intended_status_id
} if ($rfc_flag);
  my ($email_address,$id_document_name,$filename,$revision,$display_group, $group_acronym_id,$id_status_value) = rm_tr(db_select($dbh,$sqlStr));
  if ($rfc_flag) {
    $filename = "rfc${filename}";
  }
  $id_status_value = full_status_value($id_status_value);
  my $imp_report_url = "";
  $imp_report_url = qq{
Implementation Report can be accessed at
http://www.ietf.org/iesg/implementation.html
} if ($id_status_value =~ /Draft|Full/);
  my $subject_id = $id_status_value;
  $subject_id =~ s/a //;
  $subject_id =~ s/an //;
  my $subject_line = "Last Call: $filename ($id_document_name) to $subject_id";
##$subject_line = indent_text2($subject_line,9,73);
  my $lc_expiration_date = db_select($dbh,"select date_add(CURRENT_DATE,interval 14 day)");
  if ($group_acronym_id == 1027 or $group_acronym_id eq "none") {
     $display_group = "an individual submitter";
     $lc_expiration_date = db_select($dbh,"select date_add(CURRENT_DATE,interval 28 day)");
  } else {
     $group_acronym=db_select($dbh,"select acronym from acronym where acronym_id=$group_acronym_id");
     $display_group = "the $display_group WG ($group_acronym)";
     $cc_line .= "\nCC: <$email_address>";
  }
  my $body1 = "The IESG has received a request from $display_group to consider the following ";
  $body1 = indent_text2($body1,0,73);
  my $url_list = "";
  $sqlStr = qq{select rfc_flag, i.id_document_tag,id_document_name,filename,revision,status_value,name,acronym from id_internal idi,internet_drafts i,id_intended_status iis, acronym a
where idi.ballot_id = $ballot_id and
idi.id_document_tag = i.id_document_tag and
i.intended_status_id = iis.intended_status_id and
i.group_acronym_id = a.acronym_id
order by status_value DESC
};
    my @docList = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
    if ($#docList > 0) {
      $file = "files";
      $body1 .= "documents:\n\n";
    } else {
      $body1 .= "document:\n\n";
    }
    for $array_ref(@docList) {
      my ($rfc_flag, $id_document_tag,$id_document_name,$filename,$revision,$status_value,$group_name,$group_acronym) = rm_tr(@$array_ref);
      my $file_line = " <$filename-$revision.txt>";
      if ($rfc_flag) {
        ($id_document_name,$status_value) = db_select($dbh,"select rfc_name,status_value from rfcs a, rfc_intend_status b where a.rfc_number=$id_document_tag and a.intended_status_id = b.intended_status_id");
        $file_line = "RFC $id_document_tag";
        $url_list .= "http://www.ietf.org/rfc/rfc$id_document_tag.txt\n";
      } else {
        $url_list .= "http://www.ietf.org/internet-drafts/$filename-$revision.txt\n";
      }
      $status_value = full_status_value($status_value);
      $id_document_name = indent_text2($id_document_name,3,73);
      $body1 .= "- '$id_document_name'\n  $file_line as $status_value\n";
    }
  my $message_txt = qq{To: IETF-Announce <ietf-announce\@ietf.org> 
From: The IESG <iesg-secretary\@ietf.org>
$cc_line
Subject: $subject_line

$body1
The IESG plans to make a decision in the next few weeks, and solicits
final comments on this action.  Please send substantive comments to the
ietf\@ietf.org mailing lists by $lc_expiration_date. Exceptionally, 
comments may be sent to iesg\@ietf.org instead. In either case, please 
retain the beginning of the Subject line to allow automated sorting.

The file can be obtained via
$url_list$imp_report_url

IESG discussion can be tracked via
https://datatracker.ietf.org/public/pidtracker.cgi?command=view_id&dTag=$id_document_tag&rfc_flag=$rfc_flag


};
return $message_txt;

}


sub gen_ballot_writeup_text {
  return qq{
Technical Summary

   Relevant content can frequently be found in the abstract
   and/or introduction of the document.  If not, this may be 
   an indication that there are deficiencies in the abstract
   or introduction.

Working Group Summary

   Was there anything in the WG process that is worth noting?
   For example, was there controversy about particular points 
   or were there decisions where the consensus was
   particularly rough? 

Document Quality

   Are there existing implementations of the protocol?  Have a 
   significant number of vendors indicated their plan to
   implement the specification?  Are there any reviewers that
   merit special mention as having done a thorough review,
   e.g., one that resulted in important changes or a
   conclusion that the document had no substantive issues?  If
   there was a MIB Doctor, Media Type, or other Expert Review,
   what was its course (briefly)?  In the case of a Media Type
   Review, on what date was the request posted?

Personnel

   Who is the Document Shepherd for this document?  Who is the 
   Responsible Area Director?  If the document requires IANA
   experts(s), insert 'The IANA Expert(s) for the registries
   in this document are <TO BE ADDED BY THE AD>.'

RFC Editor Note

  (Insert RFC Editor Note here or remove section)

IRTF Note

  (Insert IRTF Note here or remove section)

IESG Note

  (Insert IESG Note here or remove section)

IANA Note

  (Insert IANA Note here or remove section)

};
}

sub gen_approval_text {
  my $filename = shift;
  my $ballot_id = shift;
  my ($rfc_flag,$id_document_tag,$job_owner,$cur_state) = db_select($dbh,"select rfc_flag,id_document_tag,job_owner,cur_state from id_internal where ballot_id=$ballot_id and primary_flag=1");
  my $sqlStr = qq{select revision,id_document_name,status_value,group_acronym_id from internet_drafts id, id_intended_status iis where id.id_document_tag=$id_document_tag and id.intended_status_id = iis.intended_status_id};
  $sqlStr = qq{select "RFC",rfc_name,status_value,group_acronym from rfcs r, rfc_intend_status iis where r.rfc_number=$id_document_tag and r.intended_status_id = iis.intended_status_id} if ($rfc_flag);
  my ($revision,$id_document_name,$intended_status,$group_acronym_id) = rm_tr(db_select($dbh,$sqlStr));
  my $toStr = "To: IETF-Announce <ietf-announce\@ietf.org>";
  my $ccStr = qq{Cc: Internet Architecture Board <iab\@iab.org>,
    RFC Editor <rfc-editor\@rfc-editor.org>};
  $group_acronym_id = db_select($dbh,"select acronym_id from acronym where acronym='$group_acronym_id'") if ($rfc_flag);
  my ($group_name,$group_acronym) = rm_tr(db_select($dbh,"select name,acronym from acronym where acronym_id = $group_acronym_id"));
  my $person_is = "person is";
  my $working_group = ". ";
  my ($g_type,$wg_email) = rm_tr(db_select($dbh,"select group_type_id,email_address from groups_ietf where group_acronym_id = $group_acronym_id"));
  if ($g_type != 4 and $group_name !~ /Working Group$/) {
    $working_group = " Working Group. ";
    $ccStr .= ", \n    $group_acronym mailing list <$wg_email>";
    $ccStr .= ", \n    $group_acronym chair <$group_acronym-chairs\@tools.ietf.org>";
    #my @List = db_select_multiple($dbh,"select email_address from email_addresses a, g_chairs b where b.group_acronym_id = $group_acronym_id and b.person_or_org_tag=a.person_or_org_tag  and a.email_priority=1") or error_log("select email_address from email_addresses a, g_chairs b where b.group_acronym_id = $group_acronym_id and b.person_or_org_tag=a.person_or_org_tag and a.email_priority=1");
    #for my $array_ref (@List) {
    #  my ($email) = @$array_ref;
    #  $ccStr2 .= "    $group_acronym chair <$email>,\n";
    #}
    #chop ($ccStr2);
    #chop ($ccStr2);
    #$ccStr .= $ccStr2;
  }
  my $p_or_d = "Protocol";
  $intended_status = full_status_value($intended_status);
  $p_or_d = "Document" if ($intended_status =~ /an /);
  my $subject_is = $intended_status;
  $subject_is =~ s/an //;
  $subject_is =~ s/a //;
  my $subjectStr = "Subject: $p_or_d Action: '$id_document_name' to $subject_is";

  my $mailBody = "The IESG has approved the following ";
  my $via_rfc_editor = db_select($dbh,"select via_rfc_editor from id_internal where ballot_id = $ballot_id");

    my $sqlStr = "select rfc_flag, iin.id_document_tag, id_document_name,filename,revision,status_value from internet_drafts id, id_internal iin, id_intended_status c where iin.ballot_id = $ballot_id and id.intended_status_id = c.intended_status_id and id.id_document_tag = iin.id_document_tag order by status_value DESC";
    my @List = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
    if ($#List > 0) {
      $mailBody .= "documents:\n\n";
    } else {
      $mailBody .= "document:\n\n";
    }
    my $temp_count = 0;
    for $array_ref (@List) {
       my ($rfc_flag,$id_document_tag,$dName,$fName,$version,$status_value) = rm_tr(@$array_ref);
       $temp_count++;
       $status_value_count++;
       $file_line = " <$fName-$version.txt>";
       if ($rfc_flag) {
         ($dName,$status_value) = db_select($dbh,"select rfc_name,status_value from rfcs a, rfc_intend_status b where a.rfc_number=$id_document_tag and a.intended_status_id = b.intended_status_id");
         $file_line = "RFC $id_document_tag";
       }
       $status_value = full_status_value($status_value);
       $dName = indent_text2($dName,3,73);
       $mailBody .= "- '$dName'\n  $file_line as $status_value\n";
    }
  unless ($group_acronym_id == 1027) {
    my $line1 = "";
    if ($temp_count > 1) {
      $line1 = "\nThese documents are products " ;
    } else {
      $line1 = "\nThis document is the product ";
    }
    $line1 .= "of the $group_name$working_group";
    #$line1 = indent_text($line1,0);
    $mailBody .= "\n$line1";
  } else {
    if ($temp_count > 1) {
      $mailBody .="\nThese documents have been reviewed in the IETF but are not the products of\nan IETF Working Group. ";
    } else {
      $mailBody .="\nThis document has been reviewed in the IETF but is not the product of an\nIETF Working Group. ";

    }
  }
  if ($cur_state == 33 or $cur_state==34 or $via_rfc_editor) {
    my $additional_text = "";
    if ($cur_state == 33 or $cur_state == 34) {
      $mailBody = "The IESG recommends that '$id_document_name' <$filename-$revision.txt> NOT be published as an $intended_status.";
    } else {
      $mailBody = "The IESG has no problem with the publication of '$id_document_name' <$filename-$revision.txt> as $intended_status.";
      $additional_text = indent_text2("The IESG would also like the IRSG or RFC-Editor to review the comments in the datatracker (https://datatracker.ietf.org/public/pidtracker.cgi?command=view_id&dTag=$id_document_tag&rfc_flag=$rfc_flag) related to this document and determine whether or not they merit incorporation into the document.  Comments may exist in both the ballot and the comment log.",0,73);
      $additional_text = "\n\n$additional_text";
    }
    $toStr = "To: RFC Editor <rfc-editor\@rfc-editor.org>";
    $ccStr = "Cc: The IESG <iesg\@ietf.org>, <iana\@iana.org>, ietf-announce\@ietf.org";
    $subjectStr = "Subject: Re: $subject_is to be: $filename-$revision.txt";
    ##$mailBody = indent_text2($mailBody,0,73);
    $mailBody .= $additional_text;
    $director = get_mark_by($job_owner,1);
    $co_director = get_co_director($job_owner,$group_acronym_id) unless ($group_acronym_id == 1027);
    $directorStr = "s are $director and $co_director";
    $directorStr = " is $director" unless (my_defined($co_director));

  } else {
    $director = get_mark_by($job_owner,1);
    $co_director = get_co_director($job_owner,$group_acronym_id) unless ($group_acronym_id == 1027);
    $directorStr = "s are $director and $co_director";
    $directorStr = " is $director" unless (my_defined($co_director));
  }
##$subjectStr = indent_text2($subjectStr,9,73);
  $mailBody .= "\n\nThe IESG contact person$directorStr.\n" unless ($cur_state == 33 and  $cur_state==34 and $via_rfc_editor);
  if ($rfc_flag) {
    ($id_document_name,$status_value) = db_select($dbh,"select rfc_name,status_value from rfcs a, rfc_intend_status b where a.rfc_number=$id_document_tag and a.intended_status_id = b.intended_status_id");
    $file_line = "RFC $id_document_tag";
    $url_list .= "http://www.ietf.org/rfc/rfc$id_document_tag.txt\n";
    $id_or_rfc = "RFC";
  } else {
    $url_list .= "http://www.ietf.org/internet-drafts/$filename-$revision.txt\n";
    $id_or_rfc = "Internet-Draft";
  }

  $mailBody .= qq{
A URL of this $id_or_rfc is:
$url_list

};
  $mailBody .= "The process for such documents is described at http://www.rfc-editor.org/indsubs.html.\n\nThank you,\n\nThe IESG Secretary\n" if ($cur_state == 33 or $cur_state==34 or $via_rfc_editor); 
return qq{From: The IESG <iesg-secretary\@ietf.org>
$toStr
$ccStr
$subjectStr

$mailBody
};

}

sub get_co_director {
  my $job_owner = shift;
  my $group_acronym_id = shift;
  my $area_acronym_id = db_select($dbh,"select area_acronym_id from area_group where group_acronym_id = $group_acronym_id");
  my $co_director_id =  db_select($dbh,"select b.id from area_directors a, iesg_login b where a.person_or_org_tag = b.person_or_org_tag and a.area_acronym_id=$area_acronym_id and b.id <> $job_owner");
  return get_mark_by ($co_director_id,1);
}

sub make_last_call_request {
  my $q=shift;
  my $ballot_id = $q->param("ballot_id");
  my $filename = $q->param("filename");
  my $rfc_flag = $q->param("rfc_flag");
  update_state($ballot_id,15,0,$test_mode,$devel_mode,$loginid);
  return notify_ietf($ballot_id,$filename,"last_call",$rfc_flag);
}

sub ballot_writeup {
   my $q = shift;
   my $ballot_id = $q->param("ballot_id");
   my ($cur_state,$job_owner,$id_document_tag,$rfc_flag) = db_select($dbh,"select cur_state,job_owner,id_document_tag,rfc_flag from id_internal where ballot_id = $ballot_id and primary_flag = 1");
   my $filename = db_select($dbh,"select filename from internet_drafts where id_document_tag=$id_document_tag");
   $filename = db_select($dbh,"select rfc_name from rfcs where rfc_number=$id_document_tag") if ($rfc_flag);
   my $count = db_select($dbh,"select count(ballot_id) from ballot_info where ballot_id = $ballot_id");
   unless ($count) {
     my $pre_last_call_text = db_quote(gen_last_call_ann($filename,$ballot_id));
     my $pre_approval_text = db_quote(gen_approval_text($filename,$ballot_id));
     my $pre_ballot_writeup_text = db_quote(gen_ballot_writeup_text());
     $sqlStr = "insert into ballot_info (ballot_id,last_call_text,approval_text,ballot_writeup,active) values ($ballot_id,$pre_last_call_text,$pre_approval_text,$pre_ballot_writeup_text,0)";
     db_update($dbh,$sqlStr,$program_name,$user_name);
   } 
   my ($active,$ballot_writeup,$last_call_text,$approval_text,$an_sent,$ballot_issued) = rm_tr(db_select($dbh,"select active,ballot_writeup,last_call_text,approval_text,an_sent,ballot_issued from ballot_info where ballot_id = $ballot_id"));
   my $admin_form = "";
   my $an_sent_button = "";
   my $make_last_call_button = "";
   my $issue_ballot_button = "Issue this ballot";
   $issue_ballot_button = "Re-Issue this ballot" if ($ballot_issued);
   if ($ADMIN_MODE) { 
      my $checked = numtocheck($active);
      $admin_form = qq {
<b>Activate Ballot</b> <input type="checkbox" name="active" $checked>
<br>
};
   my $button_name = "to_announcement_list";
   my $button_value = "Announce and Approve";
   if ($approval_text =~ /To: RFC Editor/) {
     $button_name = "to_rfc_editor";
     $button_value = "RFC Editor Message";
   }
   if ($approval_text =~ /NOT be published/) {
     $button_name = "do_not_publish";
     $button_value = "RFC Editor Message(DNP)";
   }
     if ($cur_state > 19) { 
       $an_sent_button = qq {
$form_header
<input type="hidden" name="command" value="approve_ballot">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="filename" value="$filename">
<input type="submit" name="$button_name" value="$button_value">
</form>
}; 
     }
     if ($cur_state < 20) {
       $make_last_call_button = qq{
$form_header
<input type="hidden" name="command" value="make_last_call_pre">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="filename" value="$filename">
<input type="submit" value="Make Last Call">
</form>

};
     }
   } 
   my $save_button = "";
   my $filename_set = get_filename_set($ballot_id,1);
   my $status_ok = 1;
   my @List_set = db_select_multiple($dbh,"select rfc_flag,id_document_tag from id_internal where ballot_id=$ballot_id");
   my $invalid_doc_set = "";
   for my $array_ref (@List_set) {
     my ($rfc_flag,$id_document_tag) = @$array_ref;
     my $status_value = "";
     my $filename="";
     
     if ($rfc_flag) {
       $status_value = db_select($dbh,"select status_value from rfc_intend_status a, rfcs b where b.rfc_number=$id_document_tag and b.intended_status_id=a.intended_status_id");
     } else {
       ($status_value,$filename) = db_select($dbh,"select status_value,filename from id_intended_status a, internet_drafts b where b.id_document_tag=$id_document_tag and b.intended_status_id=a.intended_status_id");
     }
     if ($status_value =~ /Request|None/) {
       $status_ok = 0;
       if ($rfc_flag) {
         $invalid_doc_set .= "RFC $id_document_tag ";
       } else {
         $invalid_doc_set .= "$filename ";
       }
     }
   }
   my $lc_request_button = "";
   if ($cur_state < 27) {
   $lc_request_button = qq{<input type=submit value="Request Last Call" name="send_last_call_request" onClick="return check_status();">};
   }
$ballot_writeup =~ s/&/&amp;/g;

# my $approval_text = db_quote(gen_approval_text($filename,$ballot_id));
# db_update($dbh,"update ballot_info set approval_text = $approval_text where ballot_id=$ballot_id",$program_name,$user_name);
    
   my $html_txt = qq|
<script language="javascript">
function check_status () {
  if ($status_ok == 0) {
    alert ("Please select an intended status for $invalid_doc_set and regenerate the last call message first");
    return false;
  }
  return true;
}
</script>
<h1>Last Call and Ballot Write Up</h1>
<h2>$filename_set</h2>
<hr>
<form action="$program_name" method="POST" name="f">
<input type="hidden" name="loginid" value="$loginid">
<input type="hidden" name="command" value="ballot_writeup_confirm">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="filename" value="$filename">
<b>Last Call Announcement Text</b><br>
<b><font color="#008000">MAKE SURE YOUR SUBJECT IS ALL ON ONE LINE!!!</font></b><br>
<b><font color="#FF0000">WHEN REFORMATTING SUBJECT LINE, BE SURE TO CLICK SAVE BEFORE PROCEEDING TO MAKE LAST CALL!!!</font></b><br>
<textarea name="last_call_text" rows="20" cols="124">$last_call_text</textarea>
<br>
<input type=submit value="Save Last Call Text" name="save_last_call">
<input type=submit value="Regenerate Last Call Text" name="regen_last_call">
$lc_request_button
<br>
<b>Ballot Writeup and Notes</b><br>
(Technical Summary, Working Group Summary, Protocol Quality, Note to IRTF, RFC Editor, IESG Note, IANA Note)<br>
The content of this text box will be appended to all announcements and messages to the IRTF or RFC Editor.<br>
<textarea name="ballot_writeup" rows="20" cols="74">$ballot_writeup</textarea><br>
<input type="submit" value="Save Ballot Writeup" name="save_ballot_writeup">
<input type="submit" value="$issue_ballot_button" name="send_ballot">
<br>
<b>Ballot Approval Announcement Text (Sent After Approval)</b><br>
<textarea name="approval_text" rows="20" cols="74">$approval_text</textarea>
<br>
<input type="submit" value="Save Approval Announcement Text" name="save_approval_text">
<input type="submit" value="Regenerate Approval Announcement Text" name="regen_approval_text">
<br>
$admin_form 
</form>
$make_last_call_button
<br>
$an_sent_button
$close_butto
|;
   return $html_txt;
}

sub ballot_writeup_confirm {
  my $q=shift;
  return ballot_writeup_db_old($q) unless ($devel_mode or $test_mode); ## COMMENT WHEN DEPLOY ##
  return ballot_writeup_db($q) if (defined($q->param("regen_last_call")) or defined($q->param("regen_approval_text")));
  my $ballot_id = $q->param("ballot_id");
  my $filename = $q->param("filename");
  my $hidden_value = qq{
<input type="hidden" name="command" value="ballot_writeup_db">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="filename" value="$filename">
};
  my $displaying_text = "";
  my $existing_text = "";
  if (defined($q->param("save_last_call")) or defined($q->param("send_last_call_request"))) {
    $displaying_text = $q->param("last_call_text");
    $existing_text = db_select($dbh,"select last_call_text from ballot_info where ballot_id=$ballot_id");
    if (defined($q->param("save_last_call"))) {
      $hidden_value .= qq{<input type="hidden" name="save_last_call" value="1">
};
    } elsif (defined($q->param("send_last_call_request"))) {
      $hidden_value .= qq{<input type="hidden" name="send_last_call_request" value="1">
};
    }
  } elsif (defined($q->param("save_ballot_writeup")) or defined($q->param("send_ballot"))) {
    $displaying_text = $q->param("ballot_writeup");
    $displaying_text =~ s/&/&amp;/g;
    $existing_text = db_select($dbh,"select ballot_writeup from ballot_info where ballot_id=$ballot_id");
    if (defined($q->param("save_ballot_writeup"))) {
      $hidden_value .= qq{<input type="hidden" name="save_ballot_writeup" value="1">
};
    } else {
      $hidden_value .= qq{<input type="hidden" name="send_ballot" value="1">
};
    }
  } else {
    $displaying_text = $q->param("approval_text");
    $existing_text = db_select($dbh,"select approval_text from ballot_info where ballot_id=$ballot_id");
    $hidden_value .= qq{<input type="hidden" name="save_approval_text" value="1">
};
  }
  $displaying_text =~ s/\r//g;
  
  $existing_text =~ s/\r//g;
  return ballot_writeup_db_old($q) if ($displaying_text eq $existing_text);
  ##$displaying_text = format_comment_text($displaying_text,74);
  $displaying_text =~ s/IETF-Announce :;/ietf-announce\@ietf.org/;
  $displaying_text =~ s/IETF-Announce:;/ietf-announce\@ietf.org/;
  my $row_count = get_line_count($displaying_text);
  my $approval_text_window = "";
  if (defined($q->param("send_ballot"))) {
    #my $approval_text = format_comment_text($q->param("approval_text"),74);
    my $approval_text = $q->param("approval_text");
    my $row_count2 = get_line_count($approval_text);
    $approval_text_window = qq{
<textarea name="approval_text" cols="74" rows="$row_count2">$approval_text</textarea>
};
  }
  return qq{
<font color="red"><b>Please review the text format below and click Confirm button to proceed</b></font><br><br>
$form_header  
$hidden_value
$approval_text_window
<textarea rows="$row_count" cols="74" name="displaying_text" readonly="readonly">$displaying_text</textarea>
<br>
<input type="submit" value=" Confirm ">
</form>
  };
}
sub ballot_writeup_db {
   my $q = shift;
   my $ballot_id = $q->param("ballot_id");
   my $html_txt = "";
   my $filename = $q->param("filename");
   if (defined($q->param("send_ballot"))) {
     my $ballot_writeup = db_quote($q->param("displaying_text"));
     $ballot_writeup =~ s/\r//g;
     my $approval_text = db_quote($q->param("approval_text"));
     $approval_text =~ s/\r//g;
     db_update($dbh,"insert into ballots values (null,$ballot_id,$loginid,1,0,0,0,0,0)") or error_log("insert into ballots values (null,$ballot_id,$loginid,1,0,0,0,0,0)",$program_name,$user_name);
     db_update($dbh,"update ballot_info set active=1,ballot_issued=1,ballot_writeup=$ballot_writeup,approval_text = $approval_text where ballot_id=$ballot_id",$program_name,$user_name);
     notify_iesg($ballot_id,$filename);
     $html_txt = qq{<font color="red"><h2>Ballot has been sent out</h2></font>
<hr>
};
   } elsif (defined($q->param("save_last_call")) or defined($q->param("send_last_call_request"))) {
     my $last_call_text = db_quote($q->param("displaying_text"));
     $last_call_text =~ s/\r//g;
     db_update($dbh,"update ballot_info set last_call_text = $last_call_text where ballot_id=$ballot_id",$program_name,$user_name);
     if (defined($q->param("send_last_call_request"))) {
        my $rfc_flag = db_select($dbh,"select rfc_flag from id_internal where ballot_id=$ballot_id and primary_flag=1");
        update_state($ballot_id,15,0,$test_mode,$devel_mode,$loginid);
        return notify_ietf($ballot_id,$filename,"last_call",$rfc_flag);
     } else {
        $html_txt = qq{<font color="red"><h2>Last Call Text has been saved</h2></font>
<hr>
};
     }
   } elsif (defined($q->param("regen_last_call"))) {
     my  $last_call_text = db_quote(gen_last_call_ann($filename,$ballot_id));
     db_update($dbh,"update ballot_info set last_call_text = $last_call_text where ballot_id=$ballot_id",$program_name,$user_name);
     $html_txt = qq{<font color="red"><h2>Last Call Text has been re-generated</h2></font>
<hr>
};
   } elsif (defined($q->param("save_ballot_writeup"))) {
     my $ballot_writeup = db_quote($q->param("displaying_text"));
     $ballot_writeup =~ s/\r//g;
     db_update($dbh,"update ballot_info set ballot_writeup = $ballot_writeup where ballot_id=$ballot_id",$program_name,$user_name);
     $html_txt = qq{<font color="red"><h2>Writeup has been saved</h2></font>
<hr>
};
   } elsif (defined($q->param("save_approval_text"))) {
     my $approval_text = db_quote($q->param("displaying_text"));
     $approval_text =~ s/IETF-Announce :;/ietf-announce\@ietf.org/;
     $approval_text =~ s/IETF-Announce:;/ietf-announce\@ietf.org/;
     $approval_text =~ s/\r//g;
     db_update($dbh,"update ballot_info set approval_text = $approval_text where ballot_id=$ballot_id",$program_name,$user_name);
     $html_txt = qq{<font color="red"><h2>Approval Text has been saved</h2></font>
<hr>
};
   } elsif (defined($q->param("regen_approval_text"))) {
     my $approval_text = db_quote(gen_approval_text($filename,$ballot_id));
     db_update($dbh,"update ballot_info set approval_text = $approval_text where ballot_id=$ballot_id",$program_name,$user_name);
     $html_txt = qq{<font color="red"><h2>Approval Text has been re-generated</h2></font>
<hr>
};
   }
   db_update($dbh,"update id_internal set event_date=CURRENT_DATE where ballot_id=$ballot_id",$program_name,$user_name);
   $html_txt .= ballot_writeup($q);
   return $html_txt;
}

sub ballot_writeup_db_old {
   my $q = shift;
   my $ballot_id = $q->param("ballot_id");
   my $html_txt = "";
   my $filename = $q->param("filename");
   if (defined($q->param("send_ballot"))) {
     my $ballot_writeup = db_quote(format_comment_text($q->param("ballot_writeup"),74));
     $ballot_writeup =~ s/\r//g;
     my $approval_text = db_quote(format_comment_text($q->param("approval_text"),74));
     $approval_text =~ s/\r//g;
     db_update($dbh,"insert into ballots values (null,$ballot_id,$loginid,1,0,0,0,0,0)",$program_name,$user_name);
     db_update($dbh,"update ballot_info set active=1,ballot_issued=1,ballot_writeup=$ballot_writeup,approval_text = $approval_text where ballot_id=$ballot_id",$program_name,$user_name);
     notify_iesg($ballot_id,$filename);
     $html_txt = qq{<font color="red"><h2>Ballot has been sent out</h2></font>
<hr>
};
   } elsif (defined($q->param("save_last_call")) or defined($q->param("send_last_call_request"))) {
     #my $last_call_text = db_quote(indent_text($q->param("last_call_text"),0));
     #my $last_call_text = db_quote(format_comment_text($q->param("last_call_text"),74));
     my $last_call_text = db_quote($q->param("last_call_text"));
     $last_call_text =~ s/\r//g;
     db_update($dbh,"update ballot_info set last_call_text = $last_call_text where ballot_id=$ballot_id",$program_name,$user_name);
     if (defined($q->param("send_last_call_request"))) {
        my $rfc_flag = db_select($dbh,"select rfc_flag from id_internal where ballot_id=$ballot_id and primary_flag=1");
        update_state($ballot_id,15,0,$test_mode,$devel_mode,$loginid);
        return notify_ietf($ballot_id,$filename,"last_call",$rfc_flag);
     } else {
        $html_txt = qq{<font color="red"><h2>Last Call Text has been saved</h2></font>
<hr>
};
     }
   } elsif (defined($q->param("regen_last_call"))) {
     my  $last_call_text = db_quote(gen_last_call_ann($filename,$ballot_id));
     db_update($dbh,"update ballot_info set last_call_text = $last_call_text where ballot_id=$ballot_id",$program_name,$user_name);
     $html_txt = qq{<font color="red"><h2>Last Call Text has been re-generated</h2></font>
<hr>
};
   } elsif (defined($q->param("save_ballot_writeup"))) {
     my $ballot_writeup = db_quote(format_comment_text($q->param("ballot_writeup"),74));
     $ballot_writeup =~ s/\r//g;
     db_update($dbh,"update ballot_info set ballot_writeup = $ballot_writeup where ballot_id=$ballot_id",$program_name,$user_name);
     $html_txt = qq{<font color="red"><h2>Writeup has been saved</h2></font>
<hr>
};
   } elsif (defined($q->param("save_approval_text"))) {
     my $approval_text = db_quote(format_comment_text($q->param("approval_text"),74));
     $approval_text =~ s/\r//g;
     db_update($dbh,"update ballot_info set approval_text = $approval_text where ballot_id=$ballot_id",$program_name,$user_name);
     $html_txt = qq{<font color="red"><h2>Approval Text has been saved</h2></font>
<hr>
};
   } elsif (defined($q->param("regen_approval_text"))) {
     my $approval_text = db_quote(gen_approval_text($filename,$ballot_id));
     db_update($dbh,"update ballot_info set approval_text = $approval_text where ballot_id=$ballot_id",$program_name,$user_name);
     $html_txt = qq{<font color="red"><h2>Approval Text has been re-generated</h2></font>
<hr>
};
   }
   db_update($dbh,"update id_internal set event_date=CURRENT_DATE where ballot_id=$ballot_id");
   $html_txt .= ballot_writeup($q);
   return $html_txt;
}

sub notify_ietf {
   my $ballot_id = shift;
   my $filename = shift;
   my $type = shift;
   my $rfc_flag = shift;
   my $msg = "New Write up";
   $msg = "Last Call Request" if ($type eq "last_call");
   my $dTag = db_select($dbh,"select id_document_tag from id_internal where ballot_id=$ballot_id and primary_flag = 1");
   my $subject_line = "<$filename>";
   my $filename_set = get_filename_set($ballot_id,0);
   $subject_line = "'$filename'" if ($rfc_flag);
   my $email_address = $IETF_EMAIL;
   my $mail_body = qq|To: $email_address
From: "DraftTracker Mail System" <iesg-secretary\@ietf.org>
Subject: Last Call: $subject_line 

$msg has been submitted for
$filename_set
$SEC_TRACKER_URL?command=view_id&dTag=$dTag&rfc_flag=$rfc_flag
|;
    open MAIL, "| /usr/lib/sendmail -t" or return 0;
   print MAIL <<END_OF_MESSAGE;
$X_MAIL_HEADER
$mail_body
$TEST_MESSAGE
END_OF_MESSAGE

   close MAIL or return "<h2>Could not send notification to IESG Secretariat</h2>";
   mail_log($program_name,"Last Call: $subject_line",$IETF_EMAIL,$user_name);
   my $comment_text = "Last Call was requested";
   add_document_comment($loginid,$ballot_id,$comment_text,1);
   my $html_txt = qq{
<h3>
Your request to issue the Last Call has been submitted to the secretariat.<br>
Note that the Last Call will not actually go out until the secretariat takes<br>
appropriate steps. This may take up to one business day, as it involves a <br>
person taking action.
</h3>
<hr>
$form_header
<input type="hidden" name="command" value="ballot_writeup">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="filename" value="$filename">
<input type="submit" value="Back to Writeup">
</form>   
  $form_header   <input type="hidden" name="command" value="view_id">   <input type="hidden" name="dTag" value="$dTag">
  <input type="hidden" name="rfc_flag" value="$rfc_flag">
  <input type="hidden" name="ballot_id" value="$ballot_id">   <input type="submit" value="Back to I-D">
  </form>

<br><br>
};
  return $html_txt;

}

sub notify_iesg {
   my $ballot_id = shift;
   my $filename = shift;
   my $IDs = "";
   my @idList = db_select_multiple($dbh,"select id_document_tag from id_internal where ballot_id = $ballot_id");
   for $array_ref (@idList) {
     my ($id) = @$array_ref;
     $IDs .= "$id,";
   }
   chop ($IDs);
    $sqlStr2 = qq{ Update internet_drafts
set b_sent_date = $CURRENT_DATE
where id_document_tag in ($IDs)
};
   my $filename_set = get_filename_set($ballot_id);
   my ($dTag,$rfc_flag) = db_select($dbh,"select id_document_tag,rfc_flag from id_internal where ballot_id = $ballot_id and primary_flag=1");
   my $email_address = "iesg\@ietf.org";
   my $ballot_text = `$SOURCE_DIR/gen_ballot_text.pl $ballot_id $test_mode`;
   open MAIL2, "| /usr/lib/sendmail $email_address" or return 0;
   print MAIL2 <<END_OF_MESSAGE2;
$X_MAIL_HEADER
$ballot_text
$TEST_MESSAGE
END_OF_MESSAGE2

   close MAIL2;
   mail_log($program_name,$ballot_text,$ballot_text,$user_name);
   my $comment_text = "Ballot has been issued";
   add_document_comment($loginid,$ballot_id,$comment_text,1);
  ### New request from IANA by Bill Fenner during IETF 64 ###
  send_iana_message($ballot_id,$ballot_text,'drafts-eval');
}

sub send_iana_message {
  my $ballot_id=shift;
  my $msg=shift;
  my $dest=shift;
  my $real_iana="$dest\@icann.org";
  my $iana_email="fenner\@research.att.com $real_iana";
  if ($msg =~ /To: Internet Engineering Steering Group <iesg\@ietf.org>/) {
    $msg =~ s/To: Internet Engineering Steering Group <iesg\@ietf.org>/To: IANA <$real_iana>/;
  } else {
    $msg =~ s/To: IETF-Announce <ietf-announce\@ietf.org>/To: IANA <$real_iana>/;
  }
  $msg =~ s/Reply-to: iesg\@ietf.org\n//;
  $msg =~ s/Reply-To: IESG Secretary <iesg-secretary\@ietf.org>\n//;
  my @List=db_select_multiple($dbh,"select filename,revision from internet_drafts a, id_internal b where a.id_document_tag=b.id_document_tag and b.ballot_id=$ballot_id and rfc_flag=0");
  for my $array_ref (@List) {
    my ($filename,$revision) = @$array_ref;
    open MAIL3,"| /usr/lib/sendmail $iana_email" or return 0;
    print MAIL3 <<EOM3;
X-IETF-Draft-string: $filename
X-IETF-Draft-revision: $revision
Reply-To: noreply\@ietf.org
$X_MAIL_HEADER
$msg
EOM3
    close MAIL3;
  }
  return 1;
}

sub view_writeup {
  my $ballot_id = shift;
  my ($ballot_writeup,$an_sent,$an_sent_date,$an_sent_by) = rm_tr(db_select($dbh,"select ballot_writeup,an_sent,an_sent_date,an_sent_by from ballot_info where ballot_id = $ballot_id"));
 $ballot_writeup = format_textarea($ballot_writeup);
  my $an_sent_text = "";
  my $html_txt = qq {
<h2><a name="writeup">IESG Write Up</a></h2>
$an_sent_text
<hr>
$ballot_writeup
<br>

};
   return $html_txt;

}

sub approve_ballot {
  my $q=shift;
  my $ballot_id = $q->param("ballot_id");
  my $filename = $q->param("filename");

  my $approval_text = db_quote(gen_approval_text($filename,$ballot_id));
  db_update($dbh,"update ballot_info set approval_text = $approval_text where ballot_id=$ballot_id",$program_name,$user_name);

  my $html_txt = qq{ <h1>IETF-Announcement</h1>
<h2>$filename</h2>
<hr>
$form_header_search
<input type="hidden" name="command" value="approve_ballot_db">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="filename" value="$filename">
};
  my $do_not_publish = "";
  $do_not_publish = qq{<input type="hidden" name="do_not_publish" value="1">} if (defined($q->param("do_not_publish")));
  if (defined($q->param("to_rfc_editor")) or defined($q->param("do_not_publish"))) {
    $html_txt .= qq{
<input type="hidden" name="to_rfc_editor" value="1">
$do_not_publish
<br>
<input type="submit" value="Make $filename.ann file, Send message to the RFC Editor and Close ballot">
};
  } else {
    $html_txt .= qq{
<br>
<input type="submit" value="Make $filename.ann file, Send out the Announcement and Close ballot">
};
  }
  $html_txt .= qq{
</form>
<hr>
<center> 
<form>
<input type="button" name="back_button" value="Back to Ballot" onClick="history.go(-1);return true">
</form>  
</center>          

<br><br>
$close_button
};
  return $html_txt;
}

sub approve_ballot_db {
  my $q = shift;
  my $ballot_id = $q->param("ballot_id");
  my $filename = $q->param("filename");
  my $do_not_publish = 0;
  $do_not_publish = 1 if (defined($q->param("do_not_publish")));
  my $to_rfc_editor = 0;
  $to_rfc_editor = 1 if (defined($q->param("to_rfc_editor")));
  my $sqlStr = qq{select a.group_acronym_id,b.email_address from internet_drafts a,
groups_ietf b where a.filename='$filename' and a.group_acronym_id=b.group_acronym_id};
  my ($group_acronym_id,$group_email) = db_select($dbh,$sqlStr) or error_log($sqlStr);
  $group_email = "" if ($group_acronym_id ==  1027);
  if ($group_email =~ /ietf.org/) {
    my @temp = split '\@',$group_email;
    $group_email = "$temp[0]\@odin.ietf.org";
  }

  my ($approval_text,$ballot_writeup) = rm_tr(db_select($dbh,"select approval_text,ballot_writeup from ballot_info where ballot_id=$ballot_id"));
  $approval_text .= "\n\n$ballot_writeup";
  # ballot_writeup will always be added to the announement message, requested by Barbara and Amy, 2004-4-12
  #$approval_text .= "\n\n$ballot_writeup" unless ($to_rfc_editor);
  $approval_text =~ s/\r//g;
  my $mark_by = get_mark_by($loginid,1);
  my $IDs = "";
  my $RFCs = "";
  my @idList = db_select_multiple($dbh,"select a.id_document_tag,b.filename,a.rfc_flag,a.cur_state,b.revision,a.cur_sub_state_id,a.mark_by from id_internal a, internet_drafts b where a.ballot_id = $ballot_id and a.id_document_tag = b.id_document_tag") or error_log("select a.id_document_tag,b.filename,a.rfc_flag,a.cur_state,b.revision,a.cur_sub_state_id,a.mark_by from id_internal a, internet_drafts b where a.ballot_id = $ballot_id and a.id_document_tag = b.id_document_tag");
  for $array_ref (@idList) {
     my ($id,$filename,$rfc_flag,$cur_state,$revision,$cur_sub_state_id,$ad_id) =@$array_ref;
     $revision = "RFC" if ($rfc_flag);
     my $revision2 = $revision;
     $revision = db_quote($revision);
     $IDs .= "$id," unless ($rfc_flag);
     $RFCs .= "$id," if ($rfc_flag);
     my $comment_text2 = "IESG has approved and state has been changed to 'Approved-Announcement sent' by $mark_by.";
     $result_state = 30;
     if ($do_not_publish) {
       $comment_text2 = "DNP note has been sent to RFC Editor and state has been changed to 'Dead'";
       $result_state = 99;
     }
     my $comment_text = db_quote($comment_text2);
     $sqlStr = "insert into document_comments (document_id,rfc_flag,public_flag,comment_date,comment_time,version,comment_text,created_by,result_state,origin_state) values ($id,$rfc_flag,1,CURRENT_DATE,CURRENT_TIME,$revision,$comment_text,$loginid,$result_state,$cur_state)";
     unless (db_update($dbh,$sqlStr,$program_name,$user_name)) {
       return $error_msg;
     }
    $sqlStr = qq{ update id_internal
set cur_state = $result_state,
    prev_state = $cur_state,
    cur_sub_state_id = 0,
    prev_sub_state_id = $cur_sub_state_id,
    event_date = CURRENT_DATE
where id_document_tag = $id
   }; 
   my $filename2 = ($rfc_flag==1)?"RFC $id":"$filename-$revision2.txt";
   unless (db_update($dbh,$sqlStr,$program_name,$user_name)) {
     return $error_msg;
   }
   email_to_AD($filename2,$comment_text2,"",$ad_id,"$TRACKER_URL?command=view_id&dTag=$id&rfc_flag=$rfc_flag",$test_mode,$devel_mode,$loginid);
   notify_state_update($ballot_id,$comment_text2,$test_mode,$devel_mode,"$TRACKER_PUB_URL?command=view_id&dTag=$id&rfc_flag=$rfc_flag");
 }
   chop ($IDs);
   if (my_defined($IDs)) {
     $sqlStr2 = "Update internet_drafts set b_approve_date = CURRENT_DATE where id_document_tag in ($IDs)";
    db_update($dbh,$sqlStr2,$program_name,$user_name);
  }
   if (my_defined($RFCs)) {
     $sqlStr2 = "Update rfcs set b_approve_date = CURRENT_DATE where rfc_number in ($RFCs)";
    db_update($dbh,$sqlStr2,$program_name,$user_name);
  }
  open ANN, ">$REC_DIR/$filename.ann" or return 0;
  print ANN <<END_OF_MESSAGE;
$approval_text
END_OF_MESSAGE

  close ANN or return "<h2>Could not create Announcement</h2>$close_button";
  my $to_addresses = "ietf-announce\@ietf.org iab\@iab.org rfc-editor\@rfc-editor.org $group_email";
  $to_addresses = "rfc-editor\@rfc-editor.org iana\@iana.org iesg\@ietf.org" if ($to_rfc_editor or $do_not_publish);
  $approval_text =~ s/IETF-Announce:;/ietf-announce\@ietf.org/;
    open MAIL, "| /usr/lib/sendmail -t" or return 0;
  $approval_text =~ s/IETF-Announce :;/ietf-announce\@ietf.org/;
  $approval_text =~ s/IETF-Announce:;/ietf-announce\@ietf.org/;
  print MAIL <<END_OF_MESSAGE2;
$X_MAIL_HEADER
$approval_text
$TEST_MESSAGE
END_OF_MESSAGE2

  close MAIL or return "<h2>Could not send notification to IESG Secretariat</h2>";
  mail_log($program_name,$approval_text,$approval_text,$user_name);
  unless (db_update($dbh,"update ballot_info set an_sent=1,an_sent_date=CURRENT_DATE,an_sent_by=$loginid where ballot_id = $ballot_id",$program_name,$user_name)) {
     return $error_msg;
  }
  my $html_txt = qq {
<h2>Announcement file has been created and the Ballot is now closed</h2>
<hr>
$close_button
};
  #system "/usr/local/bin/scp -i /home/mirror/.ssh/id_dsa $REC_DIR/$filename.ann ietf\@stiedprstage1:/$REC_DIR/$filename.ann" unless ($devel_mode);
  unless ($do_not_publish) {
    db_update($dbh,$sqlStr,$program_name,$user_name);
  }
  db_update($dbh,"update id_internal set event_date=CURRENT_DATE where ballot_id=$ballot_id");
  if ($do_not_publish) {
    db_update($dbh,"update id_internal set dnp=1, noproblem=0, dnp_date=CURRENT_DATE where ballot_id=$ballot_id",$program_name,$user_name);
  }
  if ($to_rfc_editor) {
    db_update($dbh,"update id_internal set noproblem=1 where ballot_id=$ballot_id",$program_name,$user_name);
  }
  send_iana_message($ballot_id,$approval_text,'drafts-approval') unless ($to_rfc_editor or $do_not_publish);
  return $html_txt;
}

sub defer_ballot {
   my $q=shift;
   my $ballot_id = $q->param("ballot_id");
   my $defer_by = get_mark_by($loginid,1);
   my $filename_set = get_filename_set($ballot_id,0);
   chomp ($filename_set);
   my $filename = $filename_set;
   $filename =~ s/\n/, /g;
   my $subject = "IESG Deferred Ballot notification: $filename";
## $subject = indent_text2($subject,9,73);
   db_update($dbh,"update ballot_info set defer = 1, defer_by=$loginid, defer_date=$CURRENT_DATE where ballot_id = $ballot_id",$program_name,$user_name);
   update_state($ballot_id,21,0,$test_mode,$devel_mode,$loginid);
   my $telechat_date = db_quote(db_select($dbh,"select date2 from telechat_dates"));
   my $returning = db_select($dbh,"select returning_item from id_internal where ballot_id=$ballot_id");
   db_update($dbh,"update id_internal set agenda=1,returning_item=$returning,telechat_date=$telechat_date,event_date=CURRENT_DATE where ballot_id=$ballot_id",$program_name,$user_name);
   my $email_address = "iesg\@ietf.org";
    open MAIL, "| /usr/lib/sendmail -t" or return 0;
   print MAIL <<END_OF_MESSAGE;
To: $email_address
From: "DraftTracker Mail System" <iesg-secretary\@ietf.org>
Subject: $subject
$X_MAIL_HEADER
 
$TEST_MESSAGE 
Ballot of $filename_set 
has been deferred by $defer_by.
This ballot will be on IESG agenda of $telechat_date

END_OF_MESSAGE

   close MAIL or return "<h2>Could not send notification to IESG</h2>";
   mail_log($program_name,$subject,$email_address,$user_name);
   return open_ballot($q);
}

sub undefer_ballot {
   my $q=shift;
   my $auto = shift;
   my $ballot_id = $q->param("ballot_id");
   my $ad_id = (defined($auto) and $auto)?0:$loginid;

   db_update($dbh,"update ballot_info set defer = 0 where ballot_id = $ballot_id",$program_name,$user_name);
   update_state($ballot_id,20,0,$test_mode,$devel_mode,$ad_id);
   return open_ballot($q);
}

sub open_ballot {
   my $q = shift;
   my $id_document_tag = $q->param("id_document_tag");
   my $html_txt = "";
   my ($filename,$ballot_id,$rfc_flag) = rm_tr(db_select($dbh,"select filename,ballot_id,rfc_flag from internet_drafts id,id_internal ii where id.id_document_tag = $id_document_tag and id.id_document_tag=ii.id_document_tag"));
   $filename = "RFC $id_document_tag" if $rfc_flag;
   my $writeup_str = view_writeup($ballot_id);
   my $print_ballot_button = "";
   my $discuss_str = "<h2><a name=\"discuss\">Discusses and Comments</a> </h2>\n";
   my $user_level = db_select($dbh,"select user_level from iesg_login where id=$loginid");
   my ($defer,$defer_by,$defer_date) = db_select($dbh,"select defer,defer_by,defer_date from ballot_info where ballot_id = $ballot_id");
   my $defer_by = get_mark_by($defer_by,1);
   my $defer_str = qq { $form_header
<input type="hidden" name="command" value="defer_ballot">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="id_document_tag" value="$id_document_tag">
<input type="submit" value="Defer Ballot">
</form>
};

   if ($defer) {
      my $expected_defer_date = db_select($dbh,"select date_sub(CURRENT_DATE,interval 13 day)");
      if ($defer_date eq $expected_defer_date) {
         $q->param(ballot_id => $ballot_id);
         undefer_ballot($q,1);
         $defer = 0;
      } else {
         $defer_str = "<h3>This ballot has been defered by $defer_by on $defer_date</h3>";
         unless ($user_level) {
             $defer_str .= qq {
$form_header
<input type="hidden" name="command" value="undefer_ballot">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="id_document_tag" value="$id_document_tag">
<input type="submit" value="UnDefer Ballot">
</form>
};

         }
      }
   }

   $sqlStr = qq{select first_name,last_name,discuss_text,comment_text,a.id,discuss_date,comment_date 
from iesg_login a left outer join ballots_discuss b on
(a.id = b.ad_id and b.ballot_id=$ballot_id)
left outer join ballots_comment c on (a.id = c.ad_id and c.ballot_id=$ballot_id)
where user_level = 1 or a.id = 107
order by last_name
};
   my @discusses_comments = rm_tr(db_select_multiple($dbh,$sqlStr));
   for $array_ref (@discusses_comments) {
     my ($first_name,$last_name,$discuss,$comment,$ad_id,$discuss_date,$comment_date) = @$array_ref;
     my $discuss_val = db_select($dbh,"select discuss from ballots where ad_id=$ad_id and ballot_id=$ballot_id"); 
     if (length($comment) > 1 or (length($discuss) > 1 and $discuss_val==1)) {
       $comment = format_textarea($comment);
       $discuss = format_textarea($discuss);
       my $ad_name = "$first_name $last_name";
       $discuss_str .= "<b>$ad_name:</b><br>";
       if (length($discuss) > 1 and $discuss_val==1) {
         $discuss_str .= qq{
<b>Discuss:</b><br>
<b>[$discuss_date]</b> $discuss<br><br>
};    
       }
       if (length($comment) > 1) {
         $discuss_str .= qq{
<b>Comment:</b><br>
<b>[$comment_date]</b> $comment<br><br>
};
       }

     }
   }
   $discuss_str .= "<hr>\n";

   unless ($user_level) {
      $print_ballot_button = qq {
$form_header
<input type="hidden" name="command" value="print_ballot">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="filename" value="$filename">
<input type="submit" value="Create $filename.bal">
</form>
};
   }
   my $filename_set = get_filename_set($ballot_id,5);
   my $job_owner = db_select($dbh,"select job_owner from id_internal where ballot_id=$ballot_id and primary_flag=1");
   my $shepher = get_mark_by($job_owner);
   $html_txt .= qq {
  <h1>IESG Discussion</h1>
  <h3>$filename_set</h3>
  <b>Responsible AD: $shepher</b><br><br>
<a href="#discuss">[View Discusses and Comments]</a> 
<a href="#writeup">[View Writeup]</a> 

$print_ballot_button
<hr>
$defer_str<br>
$form_header_search
   <table border="1" >
   <input type="hidden" name="ballot_id" value="$ballot_id">
   <input type="hidden" name="command" value="update_ballot">
   <input type="hidden" name="id_document_tag" value="$id_document_tag">
   <tr><th width="150"></th><th width="100">Yes</th><th width="100">No-Objection</th><th width="100">Discuss</th><th width="100">Abstain</th><th width="100">Recuse</th></tr>
};
   $html_txt .= "</form>\n" if ($ADMIN_MODE);
   my $sqlStr = qq {
select iesg_login.id,first_name,last_name,yes_col,no_col,abstain,discuss,recuse
from iesg_login left outer join ballots on (iesg_login.id = ballots.ad_id and ballots.ballot_id = $ballot_id)
where user_level = 1 and iesg_login.id > 1 order by last_name
};
   my @List = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
   for $array_ref (@List) {
      my ($id,$first_name,$last_name,$yes_col,$no_col,$abstain,$discuss,$recuse) = rm_tr(@$array_ref);
      if ($id == $loginid or $ADMIN_MODE) {
        my $yes_col_val = "";
        my $no_col_val = "";
        my $abstain_val = "";
        my $discuss_val = "";
        my $recuse_val = "";
        $yes_col_val = "checked" if ($yes_col);
        $no_col_val = "checked" if ($no_col);
        $abstain_val = "checked" if ($abstain);
        $discuss_val = "checked" if ($discuss == 1);
        $recuse_val = "checked" if ($recuse);
        my $admin_txt = "";
        if ($ADMIN_MODE) {
          $html_txt .= qq{
   $form_header_search
   <input type="hidden" name="ballot_id" value="$ballot_id">
   <input type="hidden" name="command" value="update_ballot">
   <input type="hidden" name="id_document_tag" value="$id_document_tag">
   <input type="hidden" name="ad_id" value="$id">
  };
          $admin_txt = qq{<td><input type="submit" value="Mark"><input type="reset" value="Reset"></td></form>
$form_header
<input type="hidden" name="command" value="view_update_ballot_comment">
<input type="hidden" name="category" value="comment">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="ad_id" value="$id">
<input type="hidden" name="firstname" value="$first_name">
<input type="hidden" name="filename" value="$filename">
<input type="hidden" name="id_document_tag" value="$id_document_tag">
<td>
<input type="submit" value="Add/Edit DiCo" name="edit_discuss_comment"">
</td></form>
};
        }
        my $d_count = db_select($dbh,"select count(ballot_id) from ballots where ballot_id = $ballot_id and ad_id = $id and discuss = -1");
        my $discuss_cleared = "";
        $discuss_cleared = "<font color=blue><b>Cleared</b></font>"  if ($d_count);
	#$discuss_cleared = "<font color=blue><b>Cleared</b></font>"  if ($d_count and ($yes_col or $no_col or $abstain or $recuse));

        $html_txt .= qq { 
            <tr bgcolor="yellow"><td>$first_name $last_name</td>
            <td align="center"><input type="radio" name="yes_no_abstain_col" value="yes_col" $yes_col_val></td>
            <td align="center"><input type="radio" name="yes_no_abstain_col" value ="no_col" $no_col_val></td>
            <td align="center"><input type="radio" name="yes_no_abstain_col" value="discuss" $discuss_val> $discuss_cleared
</td>
            <td align="center"><input type="radio" name="yes_no_abstain_col" value="abstain" $abstain_val> </td>
            <td align="center"><input type="radio" name="yes_no_abstain_col" value="recuse" $recuse_val>
</td>
$admin_txt
          </tr>
        };
      }
      else {
        my $yes_col_val = "&nbsp;";
        my $no_col_val = "&nbsp;";
        my $abstain_val = "&nbsp;";
        my $recuse_val = "&nbsp;";
        my $discuss_button_str = "&nbsp;";
        my $d_count = db_select($dbh,"select count(ballot_id) from ballots where ballot_id = $ballot_id and ad_id = $id and discuss = -1");
        $discuss_button_str = qq {
<font color=red><b>X</b></font>
} if ($discuss == 1);### Disabled. Discuss will be displayed even if there no text. if ($d_count and $discuss);
        $discuss_button_str = qq {
<font color=blue><b>Cleared</b></font>
} if ($d_count and ($yes_col or $no_col or $abstain or $recuse));

        $yes_col_val = "<font color=red><b>X</b></font>" if ($yes_col);
        $no_col_val = "<font color=red><b>X</b></font>" if ($no_col);
        $abstain_val = "<font color=red><b>X</b></font>" if ($abstain);
        $recuse_val = "<font color=red><b>X</b></font>" if ($recuse);


        $html_txt .= qq {  <tr><td>$first_name $last_name</td><td align="center">$yes_col_val</td><td align="center">$no_col_val</td><td align="center">$discuss_button_str</td><td align="center">$abstain_val</td><td align="center">$recuse_val</td></tr>
};
      }
   }

$sqlStr = qq {
select iesg_login.id,first_name,last_name,yes_col,no_col,abstain,discuss,recuse
from iesg_login,ballots
where user_level = 2 and
iesg_login.id = ballots.ad_id and ballots.ballot_id = $ballot_id
 order by last_name
};
my @List_ex = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
$html_txt .= "<tr><td colspan=\"6\"><br><br></td></tr>\n" if ($#List_ex > -1);
for $array_ref (@List_ex) {
  my ($id,$first_name,$last_name,$yes_col,$no_col,$abstain,$discuss,$recuse) = @$array_ref;
  my $yes_col_val = "&nbsp;";
  my $no_col_val = "&nbsp;";
  my $abstain_val = "&nbsp;";
  my $recuse_val = "&nbsp;";
  my $discuss_button_str = "&nbsp;";
  my $d_count = db_select($dbh,"select count(ballot_id) from ballots where ballot_id = $ballot_id and ad_id = $id and discuss = -1");
  $discuss_button_str = qq {
<font color=red><b>X</b></font>
} if ($discuss == 1);
  $discuss_button_str = qq {
<font color=blue><b>Cleared</b></font>
} if ($d_count and ($yes_col or $no_col or $abstain or $recuse));
                                                                                                   
  $yes_col_val = "<font color=red><b>X</b></font>" if ($yes_col);
  $no_col_val = "<font color=red><b>X</b></font>" if ($no_col);
  $abstain_val = "<font color=red><b>X</b></font>" if ($abstain);
  $recuse_val = "<font color=red><b>X</b></font>" if ($recuse);
                                                                                                   
                                                                                                   
  $html_txt .= qq {  <tr><td>$first_name $last_name</td><td align="center">$yes_col_val</td><td align="center">$no_col_val</td><td align="center">$discuss_button_str</td><td align="center">$abstain_val</td><td align="center">$recuse_val</td></tr>
};


}
my $first_name = rm_tr(db_select($dbh,"select first_name from iesg_login where id=$loginid"));
   $html_txt .= qq{
   <tr><td colspan="6" align="center">
<table><tr><td>
   <input type="button" value="Clear my evaluation" onClick="document.search_form.yes_no_abstain_col[0].checked=0;document.search_form.yes_no_abstain_col[1].checked=0;document.search_form.yes_no_abstain_col[2].checked=0;document.search_form.yes_no_abstain_col[3].checked=0;document.search_form.submit();">
   <input type="hidden" name="filename" value="$filename">
   <input type="submit" value="Save My evaluation" name="vote"><br>
   <input type="submit" value="Add/Edit Discussions and Comments" name="edit_discuss_comment"">
</form></td>                                                            
</tr>
$form_header_post
<input type="hidden" name="command" value="send_ballot_comment_to_iesg">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="filename" value="$filename">
<Tr><td>
<input type="submit" value="Email DISCUSS and COMMENT text to IESG list">
</td></tr>
</form>
</table>
</td></tr>
   </table>
$discuss_str
$writeup_str
<br><br><br>
   $close_button
};

   return $html_txt;

}

sub send_ballot_comment_to_iesg {
  my $q=shift;

  my $ballot_id=$q->param("ballot_id");
  my $filename=$q->param("filename");

  

  my $comment_text = db_select($dbh,"select comment_text from ballots_comment where ballot_id=$ballot_id and ad_id=$loginid");
  my $discuss_text = db_select($dbh,"select discuss_text from ballots_discuss where ballot_id=$ballot_id and ad_id=$loginid");
  my $discuss = db_select($dbh,"select discuss from ballots where ballot_id= $ballot_id and ad_id = $loginid");


  $comment_text = "" unless ($comment_text);
  $discuss_text = "" unless ($discuss_text and $discuss == 1);
  my $subject="DISCUSS";
  my $back_to_ballot=get_back_to_id_button($ballot_id,1);
  return "<i>There is nothing to send</i>$back_to_ballot" unless (my_defined($comment_text) or my_defined($discuss_text));
  if (my_defined($discuss_text)) {
    $discuss_text = "Discuss:\n$discuss_text\n\n";
  } else {
    $subject = "";
  }
  if (my_defined($comment_text)) {
    $comment_text = "Comment:\n$comment_text\n";
    $subject .= " and " if my_defined($discuss_text);
    $subject .= "COMMENT: ";
  } else {
    $subject .= ": ";
  }
  $subject .= $filename;
  my $bgcolor="bgcolor=\"#cccccc\"";
  my $back_to_id=get_back_to_id_button($ballot_id);
  my $state_change_notice_to=db_select($dbh,"select state_change_notice_to from id_internal where ballot_id=$ballot_id");
  $state_change_notice_to = "" unless ($state_change_notice_to);
  my $extra_cc_option="";
  if (my_defined($state_change_notice_to)) {
  $extra_cc_option = "<input type=\"checkbox\" name=\"extra_cc\"> $state_change_notice_to";

  }
  return qq{
<h3>Email DISCUSS and COMMENT text to IESG list<h3>
$table_header
$form_header_post
<input type="hidden" name="command" value="do_send_ballot_comment">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="filename" value="$filename">
<input type="hidden" name="subject" value="$subject">
<Tr $bgcolor><td>From: </td><td>$user_name &lt;$user_email&gt;</td></tr>
<tr><td>To: </td><td>The IESG</td></tr>
<tr $bgcolor><td>Cc: <br><b><i>separated by comma</i></b> </td><td><input type="text" name="cc_val" size="75"><br>$extra_cc_option</td></tr>
<tr><td>Subject: </td><td>$subject</td></tr>
<tr $bgcolor><td>Discuss/Comment Text: &nbsp; </td><td><pre>$discuss_text$comment_text<br></pre></td></tr>
<tr><td colspan="2"><input type="submit" value=" Send this message "></td></tr>
</form>
</table>
$back_to_id
$back_to_ballot
};
}

sub do_send_ballot_comment {
  my $q=shift;
  my $ballot_id=$q->param("ballot_id");
  my $cc_val = $q->param("cc_val");
  my $filename=$q->param("filename");
  my $subject = $q->param("subject");
  if (defined($q->param("extra_cc"))) {
    my $state_change_notice_to=db_select($dbh,"select state_change_notice_to from id_internal where ballot_id=$ballot_id");
    $cc_val .= "," if my_defined($cc_val);
    $cc_val .= $state_change_notice_to;
  }
  my $comment_text = db_select($dbh,"select comment_text from ballots_comment where ballot_id=$ballot_id and ad_id=$loginid");
  my $discuss_text = db_select($dbh,"select discuss_text from ballots_discuss where ballot_id=$ballot_id and ad_id=$loginid");
  my $discuss = db_select($dbh,"select discuss from ballots where ballot_id= $ballot_id and ad_id = $loginid");
  $comment_text = "" unless ($comment_text);
  $discuss_text = "" unless ($discuss_text and $discuss == 1);
  $discuss_text = "Discuss:\n$discuss_text\n\n" if my_defined($discuss_text);
  $comment_text = "Comment:\n$comment_text\n" if my_defined($comment_text);
  $message_body="$discuss_text$comment_text";
  my $back_to_id=get_back_to_id_button($ballot_id);
  my $back_to_ballot=get_back_to_id_button($ballot_id,1);
  if ($devel_mode or $test_mode) {
    return qq{
<b>This program is not running in production mode, and the following message was not actually sent to the recipient(s):</b><br><br>
<pre>
From: $user_name &lt;$user_email&gt;
To: The IESG
Cc: $cc_val
Subject: $subject
-------------------------------------------------
$message_body
</pre>
$back_to_id
$back_to_ballot
};
  }
 else {
 send_mail($program_name,$user_name,"iesg\@ietf.org","$user_name <$user_email>",$subject,$message_body,$cc_val);
    return qq{
<h2>Discuss/Comment text was sent</h2>
$back_to_id
$back_to_ballot
};
  }
}

sub get_back_to_id_button {
  my $ballot_id=shift;
  my $to_ballot=shift;
  $to_ballot=0 unless defined($to_ballot);
  my $id_or_ballot=($to_ballot)?"Ballot":"I-D";
  my $command=($to_ballot)?"open_ballot":"view_id";
  my ($id_document_tag,$rfc_flag) = db_select($dbh,"select id_document_tag, rfc_flag from id_internal where ballot_id=$ballot_id and primary_flag=1"); 
  return qq{
  $form_header_noname
  <input type="hidden" name="command" value="$command">
  <input type="hidden" name="dTag" value="$id_document_tag">
  <input type="hidden" name="id_document_tag" value="$id_document_tag">
  <input type="hidden" name="rfc_flag" value="$rfc_flag">
  <input type="hidden" name="ballot_id" value="$ballot_id">
  <input type="submit" value="Back to $id_or_ballot">
  </form>
};
}

sub print_ballot {
  my $q=shift;
  my $ballot_id = $q->param("ballot_id");
  my $filename = $q->param("filename");
  my $ballot_text = `$SOURCE_DIR/gen_ballot_text.pl $ballot_id $devel_mode`;
  open BAL,">$REC_DIR/$filename.bal";
  print BAL $ballot_text;
  close BAL;
  $ballot_text =~ s/&/&amp;/g;
  $ballot_text =~ s/</&lt;/g;
  $ballot_text =~ s/>/&gt;/g;
  return "<pre>\n$ballot_text\n</pre>\n";
}

sub update_ballot {
  my $q = shift;
  my $ballot_id = $q->param("ballot_id");
  my $id_document_tag = $q->param("id_document_tag");
  my $selected_val = $q->param("yes_no_abstain_col");
  my $ad_id = $loginid;
  $ad_id = $q->param("ad_id") if ($ADMIN_MODE);
  return $error_msg unless do_update_single_ballot($ballot_id,$ad_id,$selected_val);
  my $count = db_select($dbh,"select count(*) from ballots where ballot_id = $ballot_id and ad_id = $ad_id");

  my $discuss = ($count > 0)?db_select($dbh,"select discuss from ballots where ballot_id= $ballot_id and ad_id = $ad_id"):0;

 
  if (defined($q->param("edit_discuss_comment"))){
    $q->param(filename=>$filename);
    $q->param(ad_id=>$loginid);
    $q->param(discuss=>$discuss);

    return view_update_ballot_comment($q);
  } else {
    return open_ballot($q);
  }
}

sub do_update_single_ballot {
  my $ballot_id=shift;
  my $ad_id=shift;
  my $selected_val=shift;
    my $count = db_select($dbh,"select count(*) from ballots where ballot_id = $ballot_id and ad_id = $ad_id");
  my $yes_col = 0;
  my $no_col = 0;
  my $abstain = 0;
  my $recuse = 0;
  my $discuss = ($count > 0)?db_select($dbh,"select discuss from ballots where ballot_id= $ballot_id and ad_id = $ad_id"):0;
  $discuss = -1 if ($discuss == 1);
  my $assign_value = "\$${selected_val} = 1";
  eval($assign_value);
  my $sqlStr = "";
  my $new_position = get_position($yes_col,$no_col,$discuss,$abstain,$recuse);
  my $ad_name = get_mark_by($ad_id);
  if ($count) {
    $sqlStr = "update ballots set yes_col=$yes_col,no_col=$no_col,abstain=$abstain,discuss=$discuss,recuse=$recuse where ballot_id = $ballot_id and ad_id = $ad_id";
    my ($old_yes_col,$old_no_col,$old_discuss,$old_abstain,$old_recuse) = db_select($dbh,"select yes_col,no_col,discuss,abstain,recuse from ballots where ballot_id=$ballot_id and ad_id=$ad_id");
    my $old_position = get_position($old_yes_col,$old_no_col,$old_discuss,$old_abstain,$old_recuse);
    my $comment_text = "[Ballot Position Update] Position for $ad_name has been changed to $new_position from $old_position";
    add_document_comment($loginid,$ballot_id,$comment_text,1) unless ($old_position eq $new_position);
  } elsif ($new_position ne "Undefined") {
    $sqlStr = "insert into ballots values (null,$ballot_id,$ad_id,$yes_col,$no_col,$abstain,0,$discuss,$recuse)";
    my $comment_text = "[Ballot Position Update] New position, $new_position, has been recorded";
    add_document_comment($loginid,$ballot_id,$comment_text,1);
  }
  #return $sqlStr;
  if (my_defined($sqlStr)) {
    return 0 unless (db_update($dbh,$sqlStr,$program_name,$user_name)); 
    db_update($dbh,"update ballots_discuss set active=0 where ballot_id=$ballot_id and ad_id=$ad_id",$program_name,$user_name); 
    db_update($dbh,"update id_internal set event_date=CURRENT_DATE where ballot_id=$ballot_id",$program_name,$user_name);
  }
  return 1;
}
sub get_position {
  my ($yes_col,$no_col,$discuss,$abstain,$recuse) = @_;
  if ($yes_col) {
    return "Yes";
  } elsif ($no_col) {
    return "No Objection";
  } elsif ($discuss==1) {
    return "Discuss";
  } elsif ($abstain) {
    return "Abstain";
  } elsif ($recuse) {
    return "Recuse";
  } else {
    return "Undefined";
  }
  return "Undefined";
}
sub view_update_ballot_comment {
  my $q = shift;
   my $ad_id = $q->param("ad_id");
   my $ballot_id = $q->param("ballot_id");
   my $rfc_flag = db_select($dbh,"select rfc_flag from id_internal where ballot_id=$ballot_id and primary_flag=1");
   my $filename = $q->param("filename");
   my $firstname = $q->param("firstname");
   my $id_document_tag = $q->param("id_document_tag");
   my $result_list=$q->param("result_list");
   my $telechat_date=$q->param("telechat_date");
   my $my_position=$q->param("my_position");
   my $discuss = $q->param("discuss");
#Changes for handling discussion and comments in a single page

   my $sqlDiscussStr = "select discuss_date,revision,discuss_text from ballots_discuss where ballot_id = $ballot_id and ad_id = $ad_id";

   my $sqlCommentStr = "select comment_date,revision,comment_text from ballots_comment where ballot_id = $ballot_id and ad_id = $ad_id";

  my $filename_set = get_filename_set($ballot_id,1);

  my ($discuss_date,$discuss_revision,$discuss_text) = rm_tr(db_select($dbh,$sqlDiscussStr));
  my ($comment_date,$comment_revision,$comment_text) = rm_tr(db_select($dbh,$sqlCommentStr));


  #$comment_text = format_textarea($comment_text);
  unless (my_defined($discuss_revision)) {
    $discuss_date = db_select($dbh,"select CURRENT_DATE");
    $discuss_revision = db_select($dbh,"select revision from internet_drafts where id_document_tag=$id_document_tag");
  }
  $discuss_revision = "RFC" if ($rfc_flag);

  unless (my_defined($comment_revision)) {
    $comment_date = db_select($dbh,"select CURRENT_DATE");
    $comment_revision = db_select($dbh,"select revision from internet_drafts where id_document_tag=$id_document_tag");
  }
  $discuss_revision = "RFC" if ($rfc_flag);
  $comment_revision = "RFC" if ($rfc_flag);
  
  my $discuss_str = "";
  if (($discuss) or ($ADMIN_MODE))
   {
	$discuss_str = qq{<textarea name="discuss_text" rows="10" cols="74">$discuss_text</textarea>};
   }
  else
   { 
	$discuss_str = qq{<font color="red"><h2>Please mark 'Discuss' first to Add/Edit your discuss note</h2></font>
	<textarea name="discuss_text" rows="10" cols="74" disabled="disabled">$discuss_text</textarea>};
    }
   
   my $html_txt = qq {
<h1>IESG Discuss/Comments</h1>
<h2>$filename_set</h2>
};
  $html_txt .= "<h3>$firstname</h3>\n" if ($ADMIN_MODE);
  my $ballot_or_myballots = (my_defined($result_list))?"Update Result Page":"Ballot";
  my $without_saving_command=(my_defined($result_list))?"to_update_discuss_comment":"open_ballot";
  $html_txt .= qq{<hr> 
<h3>Discuss</h3>
Last Edited Date: $discuss_date <br>
<form action="$program_name" method="POST" name="f">
$discuss_str
<h3>Comment</h3>
Last Edited Date: $comment_date <br>
<textarea name="comment_text" rows="10" cols="74">$comment_text</textarea>

<input type="hidden" name="loginid" value="$loginid">
<input type="hidden" name="ad_id" value="$ad_id">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="command" value="discuss_comment_submit">
<input type="hidden" name="id_document_tag" value="$id_document_tag">
<input type="hidden" name="rfc_flag" value="$rfc_flag">
<input type="hidden" name="result_list" value="$result_list">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="my_position" value="$my_position">
<input type="hidden" name="ballot_id" value="$ballot_id">
<input type="hidden" name="filename" value="$filename">
<input type="hidden" name="result_list" value="$result_list">

<br>
<input type="submit" value="Save discuss and comment and Go back to $ballot_or_myballots" onClick="return check_text(document.f.discuss_text.value,document.f.comment_text.value);" name="save_discuss_comment">
<input type="submit" value="Save and Send Email" name="save_and_send_email">

</form>

<Script language = "javascript">
function check_text(discuss_text,comment_text) {
  if (discuss_text.length == 0 && comment_text.length == 0) {
    return confirm ("You are about to save empty text for your notes");
   } 
   else{
    return true;
  }

}
</Script>

<center>
$form_header
<input type="hidden" name="command" value="$without_saving_command">
<input type="hidden" name="id_document_tag" value="$id_document_tag">
<input type="hidden" name="telechat_date" value="$telechat_date">
<input type="hidden" name="my_position" value="$my_position">
<input type="hidden" name="result_list" value="$result_list">
<input type="submit" value="Go back to $ballot_or_myballots without Saving">
</form>
</center>
};
  return $html_txt;
}

sub update_ballot_comment_db {
   my $q = shift;

   my $discuss_text = $q->param("discuss_text");
   my $comment_text = $q->param("comment_text");
   my $id_document_tag = $q->param("id_document_tag");
   my $result_list=$q->param("result_list");
   my $command=(my_defined($result_list))?"to_update_discuss_comment":"open_ballot";
   eval "return $command(\$q)" unless (is_unique_comment($comment_text,$id_document_tag,0));
   eval "return $command(\$q)" unless (is_unique_comment($discuss_text,$id_document_tag,0));


   $comment_text = db_quote($comment_text);
   $discuss_text = db_quote($discuss_text);

   my $ad_id = $q->param("ad_id");
   my $ballot_id = $q->param("ballot_id");
   my $rfc_flag = db_select($dbh,"select rfc_falg from id_internal where id_document_tag=$id_document_tag");
   my $revision = db_quote(db_select($dbh,"select revision from internet_drafts where id_document_tag=$id_document_tag"));
   $revision = db_quote("RFC $id_document_tag") if ($rfc_flag);
   my $rfc_flag = $q->param("rfc_flag");
   my $sqlStr;



#For Discuss Text 
   my $comment_type = 1;
   my $discuss_count = db_select($dbh,"select count(*) from ballots_discuss where ad_id=$ad_id and ballot_id=$ballot_id");
   if ($discuss_count) {
   $sqlStr = "update ballots_discuss set discuss_date=CURRENT_DATE,revision=$revision,discuss_text=$discuss_text,active=1 where ad_id=$ad_id and ballot_id=$ballot_id"; 
   } else {
      $sqlStr = "insert into ballots_discuss values (null,$ballot_id,$ad_id,CURRENT_DATE,$revision,1,$discuss_text)";
   }
   unless (db_update($dbh,$sqlStr,$program_name,$user_name)) {
     return $error_msg;
   }


   $sqlStr = "insert into document_comments (document_id,public_flag,comment_date,comment_time,version,comment_text,created_by,ballot,rfc_flag) values ($id_document_tag,1,CURRENT_DATE,CURRENT_TIME,$revision,$discuss_text,$ad_id,$comment_type,$rfc_flag)";
   unless (db_update($dbh,$sqlStr,$program_name,$user_name)) {
     return $error_msg;
   }


#For Comment Text
   my $comment_type = 2;
   my $comment_count = db_select($dbh,"select count(*) from ballots_comment where ad_id=$ad_id and ballot_id=$ballot_id");
   if ($comment_count) {
     $sqlStr = "update ballots_comment set comment_date=CURRENT_DATE,revision=$revision,comment_text=$comment_text,active=1 where ad_id=$ad_id and ballot_id=$ballot_id";
   } else {
      $sqlStr = "insert into ballots_comment values (null,$ballot_id,$ad_id,CURRENT_DATE,$revision,1,$comment_text)";
   }
   unless (db_update($dbh,$sqlStr,$program_name,$user_name)) {
   return $error_msg;
  }

   $sqlStr = "insert into document_comments (document_id,public_flag,comment_date,comment_time,version,comment_text,created_by,ballot,rfc_flag) values ($id_document_tag,1,CURRENT_DATE,CURRENT_TIME,$revision,$comment_text,$ad_id,$comment_type,$rfc_flag)";
   unless (db_update($dbh,$sqlStr,$program_name,$user_name)) {
   return $error_msg;
 }


  db_update($dbh,"update id_internal set event_date=CURRENT_DATE where ballot_id=$ballot_id");
   eval "return $command(\$q)";

}
###########################################################################
#
# Function get_id_status_option_str
# Parameters :
# return : HTML text to display options of ID intended_status
# 
##########################################################################
sub get_id_status_option_str {
   my $selected_id = shift;
   my $rfc_flag = shift;
   my $html_txt;
   my $table_name = "id_intended_status";
   $table_name = "rfc_intend_status" if ($rfc_flag);
   my @List = db_select_multiple($dbh,"select intended_status_id,status_value from $table_name");
   for $array_ref (@List) {
      my ($id,$val) = @$array_ref;
      my $selected = "";
      $selected = "selected" if ($id == $selected_id);
      $val = rm_tr($val);

      $html_txt .= qq {<option value="$id" $selected>$val</option>
};
   }
   return $html_txt;
}

############################################################################
#
# Function  display_all
# Parameters :
#   @docList - list data to be displayed
# result: HTML text displaying the list
#
############################################################################
sub display_all {
   my $group_acronym_id=shift;
   my $area_acronym_id=shift;
   my @docList = @_;
   my $prev_state = 0;
   my $prev_sub_state = 0;
   my $html_txt = qq{
   $table_header};
   my $row_color = $menu_sColor;
   my $old_ballot = -1;
   my $count = 0;
   for $array_ref (@docList) {
      my ($dTag,$status_date,$event_date,$mark_by,$cur_state,$cur_sub_state,$assigned_to,$rfc_flag,$ballot_id,$all_list) = @$array_ref;
      if ($group_acronym_id > 0) {
        if ($rfc_flag) {
          my $target_group_acronym = db_select($dbh,"select acronym from acronym where acronym_id = $group_acronym_id");
          my $group_acronym = db_select($dbh,"select group_acronym from rfcs where rfc_number=$dTag");
          next unless ($target_group_acronym eq $group_acronym);
        } else {
          my $c_group_acronym_id = db_select($dbh,"select group_acronym_id from internet_drafts where id_document_tag =$dTag");
          next unless ($group_acronym_id == $c_group_acronym_id);
        }
      }

      if ($area_acronym_id > 0) {
        if ($rfc_flag) {
          my $c_area_acronym_id = db_select($dbh,"select a.area_acronym_id from area_group a,acronym b, rfcs c where c.rfc_number=$dTag and c.group_acronym=b.acronym and b.acronym_id = a.group_acronym_id");
          next unless ($c_area_acronym_id == $area_acronym_id);
        } else {
          my $c_area_acronym_id = db_select($dbh,"select a.area_acronym_id from area_group a, internet_drafts b where b.id_document_tag=$dTag and b.group_acronym_id=a.group_acronym_id");
          next unless ($c_area_acronym_id == $area_acronym_id);
        }
      }

      $all_list = 0 unless my_defined($all_list);
      $all_list = 0 unless ($all_list =~ /^\d/);
      $prev_sub_state = 0 if ($prev_sub_state < 0);
      $cur_sub_state = 0 if ($cur_sub_state < 0);
	  $count++;
          if (($cur_state != $prev_state or $cur_sub_state !=  $prev_sub_state) and $old_ballot != $ballot_id) {
             my $cur_state_val = rm_tr(db_select($dbh,"select document_state_val from ref_doc_states_new where document_state_id = $cur_state"));
             $cur_state_val = "I-D Exists" if ($cur_state == 100);
             $cur_state_val = qq {<a href="${program_name}?command=view_state_desc&id=$cur_state">$cur_state_val</a> };
             $prev_state = $cur_state;
             $prev_sub_state = $cur_sub_state;
             my $cur_sub_state_val = "";
             if ($cur_sub_state > 0) {
               $cur_sub_state_val = " :: ";
               $cur_sub_state_val .= qq {<a href="${program_name}?command=view_state_desc&id=$cur_sub_state&sub_state=1">};
               $cur_sub_state_val .= get_sub_state($cur_sub_state);
               $cur_sub_state_val .= "</a>";
             }


                $html_txt .= qq{          
                 </table>
                 <h3>In State: $cur_state_val $cur_sub_state_val</h3>
         <table bgcolor="#DFDFDF" cellspacing="0" cellpadding="0" border="0" width="800">
         <tr bgcolor="A3A3A3"><th>&nbsp;</th><th width="250">Name (Intended Status)</th><th>Ver</th><th>Responsible AD</th><th>Status Date</th><th>Modified (EST)</th></tr>
};

	  }
	  
	  my $pre_list;
	  if ($old_ballot != $ballot_id) {
	     $old_ballot = $ballot_id;
	     $pre_list = "<li>";
    	  if ($row_color eq $menu_fColor) {
	        $row_color = $menu_sColor;
	      } else {
	        $row_color = $menu_fColor;
	      }
	  } else {
	     $pre_list = "<dd><font size=\"-1\">";
	  }
	  my $ballot_list = "";
	  
	  $ballot_list = get_ballot_list_local($ballot_id,$dTag,$row_color) if ($all_list == 1);
      $status_date = convert_date($status_date,1);
	  $event_date = convert_date($event_date,1);
	  $html_txt .= display_one_row($ballot_id,$dTag,$rfc_flag,$assigned_to,$mark_by,$status_date,$event_date,$row_color,$pre_list);
	  $html_txt .= $ballot_list;
   }
   unless ($count) {
      return "";
   }
   $html_txt .= qq {</table>
   };   
   return $html_txt;

}

sub get_ballot_list_local {
   my $ballot_id = shift;
   my $id_document_tag = shift;
   my $row_color = shift;
   my $html_txt = "";
   my $sqlStr;
   $sqlStr = qq {
select it.id_document_tag,id.filename,rfc.rfc_number,it.rfc_flag,it.assigned_to,it.job_owner,
it.status_date,it.event_date
from id_internal it
left outer join internet_drafts id on it.id_document_tag = id.id_document_tag
left outer join rfcs rfc on it.id_document_tag = rfc.rfc_number
where it.ballot_id = $ballot_id and it.id_document_tag <> $id_document_tag
order by id.filename, rfc.rfc_number
};
   my @List = db_select_multiple($dbh,$sqlStr) or error_log($sqlStr);
   my $pre_list = "<dd><font size=\"-1\">";
   for $array_ref (@List) {
      my ($id_document_tag,$filename,$rfc_number,$rfc_flag,$responsible,$job_owner,$status_date,$event_date) = @$array_ref;
	  $responsible = rm_tr($responsible);
	  $html_txt .= display_one_row($ballot_id,$id_document_tag,$rfc_flag,$responsible,$job_owner,$status_date,$event_date,$row_color,$pre_list);
   }
   return $html_txt;
}

sub display_one_row {
   my ($ballot_id,$id_document_tag,$rfc_flag,$responsible,$job_owner,$status_date,$event_date,$row_color,$pre_list) = @_;
   my $command = "view_id";
   my $submit_str = qq {<input type="submit" value="DETAIL">};
   if ($job_owner==100) {
     $submit_str =  qq {<input type="submit" value="ADD">}; 
     $command = "add_id_confirm";
     $ballot_id = 0;
     #$ballot_id = db_select($dbh,"select max(ballot_id) from id_internal");
     #$ballot_id++;
   }
   my ($revision,$filename,$actual_file,$intended_status_str,$ballot_str);
   my $expired_tombstone=0;
   if ($ADMIN_MODE) {
     if ($rfc_flag == 1) {
	     $ballot_str = qq{[$ballot_id] <a href="http://cf.amsl.com/system/rfc/add/search_rfc3.cfm?rfc_number=2613&isnew=no&searchResults=2613,&search_rfc_name=&search_rfc_number=$id_document_tag" 
};
     } else {
	     $ballot_str = qq{[$ballot_id] <a href="http://cf.amsl.com/system/id/add/search_id3.cfm?id_document_tag=$id_document_tag&isnew=no&searchResults=$id_document_tag" 
};
     }
     $ballot_str .= qq{ onMouseOver="window.status='Detail of $id_document_tag';return true;" 
      onMouseOut="window.status='';return true;">[detail]</a>};

   }
   my $status_value = "Active";
   if ($rfc_flag == 1) {
	     $revision = "RFC";
		 $filename = "rfc" . $id_document_tag;
		 $actual_file = "rfc/${filename}.txt";
		 $intended_status_str = db_select($dbh,"select b.status_value from rfcs a, rfc_intend_status b where a.rfc_number = $id_document_tag and a.intended_status_id = b.intended_status_id");
   } else {
	     ($filename,$revision,$expired_tombstone) = rm_tr(db_select($dbh,"select filename,revision,expired_tombstone from internet_drafts where id_document_tag = $id_document_tag"));
		 $actual_file = "internet-drafts/${filename}-${revision}.txt";
		 $intended_status_str = db_select($dbh,"select b.status_value from internet_drafts a, id_intended_status b where a.id_document_tag = $id_document_tag and a.intended_status_id = b.intended_status_id");
     $status_value = db_select($dbh,"select status_value from id_status a, internet_drafts b where b.id_document_tag=$id_document_tag and b.status_id=a.status_id");
   }
   $status_date = convert_date($status_date,1);
   $event_date = convert_date($event_date,1);
   my $link_text = "<a href=\"http://www.ietf.org/$actual_file\">$filename ($intended_status_str)</a>"; 
   unless ($status_value eq "Active") {
     $link_text = "$filename ($intended_status_str)";
     $revision = decrease_revision($revision) unless $expired_tombstone;
   }
   my $mark_by = get_mark_by($job_owner);
   $mark_by = "Not Assigned Yet" if ($job_owner == 100);
   my $replace_info = get_replaced_by_info($status_value,$id_document_tag,"iesg",1);
   $replace_info .= get_replaces_info($id_document_tag,"iesg",1) if ($replaces_ids_list =~ /,$id_document_tag,/);;
   my $html_txt = "";
	  $html_txt .= qq{
	  <tr bgcolor="$row_color">
       $form_header	  
	   <td>
       <input type="hidden" name="command" value="$command">
       <input type="hidden" name="dTag" value="$id_document_tag">
       <input type="hidden" name="rfc_flag" value="$rfc_flag">
       <input type="hidden" name="ballot_id" value="$ballot_id">
       $submit_str
	  </td>
      </form>
	  
	  <td nowrap>$pre_list $link_text $ballot_str$replace_info</td>
          <td align="center">$revision</td><td align="center">$mark_by</td>
	  <td align="center">$status_date</td><td align="center">$event_date</td>
	  </tr>
	  };
   
   return $html_txt;   
}

sub view_id_exists {
  my $q = shift;
  my $id_document_tag = $q->param("dTag");
  my ($filename,$revision) = rm_tr(db_select($dbh,"select filename,revision from internet_drafts where id_document_tag = $id_document_tag"));
  my $html_txt = qq { <h2>This document is not under IESG review yet</h2>
<h3>$filename</h3><br>
<b>Version: $revision<br>
Intended Status: $intended_status<br>
};

  return $html_txt;
}

###########################################################
#
# Function: get_next_state_button_str
# Parameter:
#   $cur_state - record id of current state
# return: HTML text to create next state buttons based on current state
#
# This function generate the HTML text for next state by looking up
# the table ref_next_states_new
#
###########################################################
sub get_next_state_button_str {
   my $cur_state = shift;
   my $html_txt = "";
   my @list = db_select_multiple($dbh,"select next_state_id from ref_next_states_new where cur_state_id = $cur_state");
   for $array_ref (@list) {
      my ($state_id) = @$array_ref;
	  my $state_str = rm_tr(db_select($dbh,"select document_state_val from ref_doc_states_new where document_state_id = $state_id"));
	  $html_txt .= qq {
		  <input type="submit" value="$state_str"  onClick="return check_expired();" name="next_state_button" >
	  };
   }
   return $html_txt;
}


######################################################
#
# Function : add_action
# Parameters:
#   $q - CGI variables
# result: HTML text of search table to add an action
#
######################################################
sub add_action {
   my $q = shift;
   my $ballot_id = $q->param("ballot_id");
   my $dTag = $q->param("dTag");
   my $html_txt = qq {
   <h2>Add an I-D to Ballot</h2>
   };
   my $search_html = search_html($ballot_id,1,$dTag);
   my $action_html = get_action_html($ballot_id); 
   $html_txt .= qq {
   $search_html
   $action_html
   };
   return $html_txt;
}

########################################################
#
# Function: get_resp_optoin_str
# Parameters:
# return: HTML text to display options of "Responsible" Select field
#
########################################################
sub get_resp_option_str {
   my @list = db_select_multiple($dbh,"select ref_resp_val from ref_resp");
   my $resp_option_str = "";
   for $array_ref (@list) {
     my ($resp_val) = @$array_ref;
     $resp_val = rm_tr($resp_val);
     $resp_option_str .= qq{
     <option value="$resp_val">$resp_val
     };
   }
   return $resp_option_str;
}


sub gen_agenda {
   my $q = shift;
   my @List = db_select_multiple($dbh,"select document_state_id,document_state_val from ref_doc_states_new");
%group_name = {};
for $array_ref (@List) {
   my ($flag,$val) = @$array_ref;
   $group_name{$flag} = $val;
}
   my $admin_text = "";
   my $admin_text2 = "";
     $admin_text = qq {
   <table><tr>
   $form_header
   <input type="hidden" name="command" value="action">
   <input type="hidden" name="cat" value="agenda">
   <td><input type="submit" value = "Generate Web Page"></td>
   </form>
   $form_header
   <input type="hidden" name="command" value="clear_agenda">
   <td><input type="submit" value = "Clear All" onClick="return window.confirm('You are about to clear all agenda');"></td>
   </form></tr></table>
   } if ($ADMIN_MODE);
   my $sqlStr = qq{select a.rfc_flag,a.ballot_id,a.id_document_tag,i.filename,i.id_document_name,a.telechat_date,b.document_state_val,a.returning_item
          from id_internal a
          left outer join internet_drafts i on (
             a.id_document_tag = i.id_document_tag
          ), ref_doc_states_new b
          where a.primary_flag = 1 and agenda=1 and a.cur_state = b.document_state_id
      order by telechat_date, filename 
      };
   $admin_text2 = qq{
   $form_header_post
   <input type="hidden" name="command" value="update_agenda">
   $table_header <tr><td>
   <div id="largefont">Documents on upcoming agenda(s):</div>
             <table cellpadding="0" cellspacing="0" border="0">
};
   $admin_text2 .= get_agenda_body($sqlStr,1);   
   $admin_text2 .= "<br><br><br>\n";


 
   my $html_txt = qq{<center><h3>Documents on upcoming agenda(s)</h3></center>
   $admin_text
<br>
<a href="$program_name?command=view_agenda">View Agenda</a><br><br>
   $admin_text2
};
   $html_txt .= $admin_text;
   return $html_txt;
}


sub get_agenda_body {
  my $sqlStr = shift;
  my $admin_flag = shift;
  my $html_txt = "";
  my @List = db_select_multiple($dbh,$sqlStr);
  for $array_ref (@List) {
      my ($rfc_flag,$ballot_id,$document_tag,$filename,$doc_name,$default_telechat_date,$gFlag_name,$agenda_or_returning) = @$array_ref;
      if ($rfc_flag) {
                 $doc_name = db_select($dbh,"Select rfc_name from rfcs where rfc_number = $document_tag");
                 $filename = "rfc${document_tag}.txt";
          }
      if ($oldDate ne $default_telechat_date) {
             $oldDate = $default_telechat_date;
         $html_txt .= qq{
                 </table>
                 <br><hr><br>
             <table cellpadding="0" cellspacing="0" border="0">
};
      }
      my $returning_checkbox = "";
      if ($admin_flag and $agenda_or_returning) {
        $returning_checkbox = qq{
<b>Clear Returning Item?</b> <input type="checkbox" name="returning_$ballot_id">
};
      }
      $checkedStr = "";
      if ($agenda_or_returning or $admin_flag) {
         $checkedStr = "checked";
      }
      my $selected_list = "";
      if (my_defined($default_telechat_date)) {
        $selected_list = "<option value=\"$default_telechat_date\">$default_telechat_date</option>\n";
      }
      if (my_defined($filename)) {
        $html_txt .= qq{<tr><td><input type="checkbox" value="on" name="$ballot_id" $checkedStr></td>
<td><select name="telechat_date_$ballot_id">$selected_list $telechat_date_list</select></td> 
<td><li><a href="${program_name}?dTag=$document_tag&ballot=yes&command=view_id&rfc_flag=$rfc_flag" 

          onMouseOver="window.status='Edit document $document_tag';return true;" 
          onMouseOut="window.status='';return true;"><b>$filename</b><font size=-1>($doc_name) </font></a> in <b>$gFlag_name</b></td></td><td>$returning_checkbox</td></tr>
         <input type="hidden" name="old_telechat_date_$ballot_id" value="$default_telechat_date">
          };
      }
      
     my @List2 = db_select_multiple($dbh,"select filename,a.id_document_tag,rfc_flag,b.id_document_name from id_internal a, internet_drafts b where a.id_document_tag = b.id_document_tag and a.ballot_id=$ballot_id and primary_flag=0");
     if ($#List2 > -1) {
       for $array_ref2 (@List2) {
         my ($filename,$document_tag,$rfc_flag,$doc_name) = @$array_ref2;
         if ($rfc_flag) {
           $filename = "RFC $document_tag";
           $doc_name = db_select($dbh,"select rfc_name from rfcs where rfc_number = $document_tag");
         }
         $html_txt .= qq{<tr><td></td><td></td><td>&nbsp;&nbsp; &nbsp; <a href="${program_name}?dTag=$document_tag&ballot=yes&command=view_id&rfc_flag=$rfc_flag" 
          onMouseOver="window.status='Edit document $document_tag';return true;" 
          onMouseOut="window.status='';return true;"><b>$filename</b><font size=-1>($doc_name) </font></a></td></tr>
};
       }
     }
   }
   $html_txt .= "</table>\n";
   $html_txt .= qq{
<hr>
   <input type="submit" value="UPDATE">
   </form>
   </table>
   };

  return $html_txt;
}




sub clear_agenda {
   my $q = shift;
   my $loginid = get_mark_by($q->param("loginid"));
   my $current_date = get_current_date();
   system "echo Agenda cleared by $loginid on $current_date>> $SOURCE_DIR/LOGS/tracker.log";
   db_update($dbh,"UPDATE id_internal set agenda=0 where 0=0\n",$program_name,$user_name);
   my $html_txt = "</center>\n";
   $html_txt .= gen_agenda($q);
   return $html_txt;
}

sub view_agenda {
  my $q = shift;
  my $date = db_select($dbh,"select date1 from telechat_dates");
  my $html_txt = `/home/henrik/src/db/legacy/iesg/gen_agenda_summary.pl $date $test_mode`;
  $html_txt = html_bracket($html_txt);
  return "<pre> $html_txt </pre>";
}

sub update_agenda {
   my $q = shift;
   my $html_txt = "";
   my @preList = db_select_multiple($dbh,"select id_document_tag from id_internal where agenda = 1");
   db_update($dbh,"UPDATE id_internal set agenda=0 where 0=0\n",$program_name,$user_name);
   foreach ($q->param) {
      if (/^\d/) {
         my $ballot_id = $_;
         my $old_telechat_date = $q->param("old_telechat_date_$ballot_id");
         my $telechat_date = $q->param("telechat_date_$ballot_id");    
         my $clear_returning_item = checktonum($q->param("returning_$ballot_id"));
         my $update_returning_item = "";
         my $update_telechat_date = "";
         if ($old_telechat_date ne $telechat_date) {
           $update_telechat_date = "telechat_date = '$telechat_date', ";
           $update_returning_item = "returning_item = 1, " if (my_defined($old_telechat_date));
         } 
         $update_returning_item = "returning_item=0, " if $clear_returning_item;


	$sqlStr = "update id_internal set $update_telechat_date $update_returning_item agenda=1, event_date = CURRENT_DATE where  ballot_id = $ballot_id\n";
#$html_txt .= "$sqlStr <br>\n";
        db_update($dbh,$sqlStr,$program_name,$user_name);
      }
   }
   $html_txt .= "</center>\n";
#return $html_txt;
   $html_txt .= gen_agenda($q);
   my @preAgenda;
   my @postAgenda;
   my @postList = db_select_multiple($dbh,"select id_document_tag from id_internal where agenda = 1");
   for $array_ref (@preList) {
     my ($id) = @$array_ref;
     push @preAgenda, $id;
   }
   for $array_ref (@postList) {
     my ($id) = @$array_ref;
     push @postAgenda, $id;
   }
  my @off_list = array_diff(\@preAgenda,\@postAgenda);
  my @on_list = array_diff(\@postAgenda,\@preAgenda);
  for $tag (@off_list) {
    my $telechat_date = db_select($dbh,"select telechat_date from id_internal where id_document_tag=$tag");
    my $num_day_telechat_date = db_select($dbh,"select to_days('$telechat_date')");
    my $num_day_current_date = db_select($dbh,"select to_days(current_date)");
    my $valid = $num_day_telechat_date - $num_day_current_date;
    if ($valid > 0) {
      my $comment_text = "Removed from agenda for telechat - $telechat_date";
      add_document_comment($loginid,$tag,$comment_text,0);
    }
  }
  my $result = $#off_list + $#on_list;
  if ($result > -2) {
    my $current_date = db_select($dbh,"select current_date");
    my $log_text = "$current_date|$loginid|@off_list|@on_list";
    open (LOG,">>/a/www/ietf-datatracker/logs/agenda.log");
    print LOG "$log_text\n";
    close LOG;
  }
   return $html_txt;
}

  
sub gen_template {
   my $wg_news_exist = "";
   my $iab_news_exist = "";
   my $m_issue_exist = "";
   my @List1 = db_select_multiple($dbh,"select template_id,template_title,template_text from templates where template_type=1");
   for $array_ref (@List1) {
     my ($template_id,$template_title,$template_text) = @$array_ref;
     $wg_news_exist .= qq{
$form_header_search
<input type="hidden" name="command" value="submit_template">
<input type="hidden" name="template_id" value="$template_id">
<b>Title: </b><input type="text" name="template_title" value="$template_title" size="65"><br>
<textarea name="template_text" cols="74" rows="10" wrap="virtual">$template_text</textarea><br>
<input type="submit" value="Update" name="update_template"><input type="reset" value="Reset"><input type="submit" value="Delete" name="delete_template"><br>
</form>
};
   }

   my @List2 = db_select_multiple($dbh,"select template_id,template_title,template_text from templates where template_type=2");
   for $array_ref (@List2) {
     my ($template_id,$template_title,$template_text) = @$array_ref;
     $iab_news_exist .= qq{
$form_header_search
<input type="hidden" name="command" value="submit_template">
<input type="hidden" name="template_id" value="$template_id">
<b>Title: </b><input type="text" name="template_title" value="$template_title" size="65"><br>
<textarea name="template_text" cols="74" rows="10" wrap="virtual">$template_text</textarea><br>
<input type="submit" value="Update" name="update_template"><input type="reset" value="Reset"><input type="submit" value="Delete" name="delete_template"><br>
</form>
};
   }

   my @List3 = db_select_multiple($dbh,"select template_id,template_title,template_text from templates where template_type=3");
   for $array_ref (@List3) {
     my ($template_id,$template_title,$template_text) = @$array_ref;
     $m_issue_exist .= qq{
$form_header_search
<input type="hidden" name="command" value="submit_template">
<input type="hidden" name="template_id" value="$template_id">
<b>Title: </b><input type="text" name="template_title" value="$template_title" size="65"><br>
<textarea name="template_text" cols="74" rows="10" wrap="virtual">$template_text</textarea><br>
<input type="submit" value="Update" name="update_template"><input type="reset" value="Reset"><input type="submit" value="Delete" name="delete_template"><br>
</form>
};
   }
   my $html_txt .= qq{
   <h2>Templates</h2>
   Please put HTML code for each template<br>
   <h3>Working Group News</h3>
   $wg_news_exist
   $form_header_search
   <input type="hidden" name="command" value="submit_template">
   <input type="hidden" name="template_type" value="1">
   <b>Title:</b> <input type="text" name="template_title" size="65"><br>
   <textarea name="template_text" cols="74" rows="10" wrap="virtual"></textarea><br>   <input type="submit" value="  ADD  ">
   </form>
   <h3>IAB News We can use</h3>
   $iab_news_exist
   $form_header_search
   <input type="hidden" name="command" value="submit_template">
   <input type="hidden" name="template_type" value="2">
   <b>Title:</b> <input type="text" name="template_title" size="65"><br>
   <textarea name="template_text" cols="74" rows="10" wrap="virtual"></textarea><br>
   <input type="submit" value="  ADD  ">
   </form>
   <h3>Agenda Management Item</h3>
   $m_issue_exist
   $form_header_search
   <input type="hidden" name="command" value="submit_template">
   <input type="hidden" name="template_type" value="3">
   <b>Title:</b> <input type="text" name="template_title" size="65"><br>
   <textarea name="template_text" cols="74" rows="10" wrap="virtual"></textarea><br>
   <input type="submit" value=" ADD  ">
   </form>

   };

   return $html_txt;
}

sub submit_template {
  my $q=shift;
  my $template_text = db_quote($q->param("template_text"));
  my $template_type = $q->param("template_type");
  my $template_title = db_quote($q->param("template_title"));
  my $template_id = $q->param("template_id");
  if (defined($q->param("update_template"))) {
    db_update($dbh,"update templates set template_title=$template_title,template_text=$template_text where template_id = $template_id",$program_name,$user_name);
  } elsif (defined($q->param("delete_template"))) {
    db_update($dbh,"delete from templates where template_id=$template_id",$program_name,$user_name);
  } else {
    db_update($dbh,"insert into templates (template_text,template_type,template_title) values ($template_text,$template_type,$template_title)",$program_name,$user_name);
  }
  return gen_template();
}

sub gen_single {
   my $html_txt = qq{Single Page Generated};
   return $html_txt;
}
sub gen_pwg {
   my $q = shift;
   my $html_txt = "$table_header <tr><td>\n";
   $html_txt .= "<center><br><div id=\"largefont\">WG Actions</div><br></center><div id=\"largefont2\">Current List</div><br>";
   $sqlStr=qq{select a.name,a.acronym,g.status_date,g.note,g.group_acronym_id
   from group_internal g, acronym a
   where g.group_acronym_id = a.acronym_id
   order by g.status_date DESC
   };
   my %aID;
   $html_txt .= "$table_header \n";
   my @List = db_select_multiple($dbh,$sqlStr);
   for $array_ref (@List) {
      @row = @$array_ref;
      $ac=rm_tr($row[1]);
      $aID{$ac} = $row[4];
	  $dateStr = $row[2];
	  $dateStr = convert_date($dateStr,2);
	  $dateStr = convert_date($dateStr);
      $html_txt .= qq{
	  $form_header
	  <input type="hidden" name="command" value="edit_delete">
	  <input type="hidden" name="gID" value="$row[4]">
	  <input type="hidden" name="acronym" value="$ac">
	  <input type="hidden" name="title" value="$row[0]">
	  <tr>
	  <td>$dateStr</td><td>$row[0] ($ac)</td>
	  <td><input type="submit" name="edit" value="EDIT"></td>
	  <td><input type="submit" name="delete" value="DELETE"></td>
	  </tr>
	  </form>
	  };
   }
   $html_txt .= "</table>\n";
   $html_txt .= qq{<br>
   <div id="largefont2">Possible List</div><br>
   $table_header
   };
   while ($filename=<$EVAL_DIR/*-charter.txt>) {
      open INFILE,$filename;
      $_ = <INFILE>;
      while (/^\W/) {
         $_ = <INFILE>;
      }
      chomp ($header = $_);
      @headAry = split '\(',$header;
      $name_val = $headAry[0];
      $ac_val = $headAry[1];
      @headAry = split '\)',$ac_val;
      $ac_val = $headAry[0];
      if (!defined($aID{$ac_val})) {
        for ($loop=0;$loop<4;$loop++) {
          chomp($_ = <INFILE>);
        }
        @aryStr = split ':',$_;
        $dateStr = $aryStr[1];
        my $token_list;
        while (<INFILE>) {
          if (/.Area Director./) {
            $line = <INFILE>;
            $line = <INFILE>;
            chomp($line);
            while (length($line)) {
              @temp = split ' ',$line;
              $token_list .= "$temp[0] ";
              $line = <INFILE>;
              chomp($line);
              chop($line);
	      chop($line);
              chop($line);
	      chop($line);
            }
	    last;
          }
	}
        $html_txt .= qq{
$form_header
<input type="hidden" name="command" value="add_delete_pwg">
<input type="hidden" name="acronym" value="$ac_val">
<input type="hidden" name="status_date" value="$dateStr">
<input type="hidden" name="title_val" value="$name_val">
<input type="hidden" name="filename" value="$filename">
<input type="hidden" name="token_list" value="$token_list">
<tr>
<td>$dateStr</td>
<td>$name_val ($ac_val)</td>
<td><input type="submit" value="ADD"></td>
<td><input type="submit" value="PERMANENT DELETE" name="delete"
 onClick="return window.confirm('The file will be permanently removed from server');"></td>
</tr>
</form>
};
     }
     close (INFILE);
   }
   $html_txt .= qq{</table></td></tr></table>};  
   $html_txt .= qq{
$form_header
<input type="hidden" name="command" value="action">
<input type="hidden" name="cat" value="pwg">
<input type="submit" value = "Generate Web Page">
</form>
};
  return $html_txt;
}

sub add_pwg {
   my $q = shift;
   my $ac_val = $q->param("acronym");
   my $status_date = $q->param("status_date");
   my $title_val = $q->param("title_val");
   my $token_list = $q->param("token_list");
   my @list = split " ",$token_list;
   my $select_str = qq{<select name="token_name">};
   foreach $val (@list) {
      $select_str .= qq{
	     <option value="$val">$val<option>
	  };  
   }
   $select_str .= qq{</select>};
   my $pwg_cat_list = get_pwg_cat_list();   
   $ac_val="kitten" if ($ac_val eq "GSS-API Next Generation");
   $html_txt = "";
   $html_txt .= qq{<h4>Adding new PWG list</h4>
   $table_header <tr><td>
   $form_header
   <input type="hidden" name="acronym" value="$ac_val">
   <input type="hidden" name="command" value="add_db">
   <font color="red"><b>$title_val ($ac_val)</b></font><br><br>
   Status Date: <input type="text" name="status_date" value="$status_date"><br>
   Token Name: $select_str<br>
   Agenda Category: <select name="pwg_cat_id">
$pwg_cat_list
</select><br>
   Note: <br>
   <textarea name="note" cols="40" rows="5" wrap="virtual"></textarea><br>
   <input type="submit" value="CONFIRM ADD">
   </form>
   </td></tr></table>
   };
   return $html_txt;
}

sub add_db {
   my $q = shift;
   my $ac_val = $q->param("acronym");
   my $status_date = $q->param("status_date");
   my $note = $q->param("note");
   my $pwg_cat_id = $q->param("pwg_cat_id");
   my $agenda = 1;
   $agenda = 0 if ($pwg_cat_id == 11 or $pwg_cat_id == 21);
   my $token_name = $q->param("token_name");
   my $telechat_date = db_quote(db_select($dbh,"select date1 from telechat_dates"));
   $status_date = y_two_k($status_date);
   $status_date = db_quote($status_date);
   $note = db_quote($note);
   $ac_val = db_quote($ac_val);
   $token_name = db_quote($token_name);
   $sqlStr = "select acronym_id from acronym where acronym = $ac_val";
   my $gID = db_select($dbh,$sqlStr);
   return "<b>ERROR: The group acronym can not be found</b>"  unless $gID;
   $sqlStr = qq{
   insert into group_internal values ($gID,$note,$status_date,$agenda,$token_name,$pwg_cat_id,$telechat_date)
   };
   #return $sqlStr;
   db_update($dbh,$sqlStr,$program_name,$user_name);
   my $html_txt = gen_pwg($q);
   return $html_txt;
}

sub get_pwg_cat_list {
  my $selected_id=shift;
  my $ret_val = "";
  my @List = db_select_multiple($dbh,"select id,pwg_status_val from pwg_cat order by id");
  for $array_ref (@List) {
    my ($id,$val) = rm_tr(@$array_ref);
    my $selected = "";
    $selected = "selected" if ($id == $selected_id);
    $ret_val .= "<option value=\"$id\" $selected>$val</option>\n";
  } 
  return $ret_val;
}

sub edit_pwg {
   my $q = shift;
   my $gID = $q->param("gID");
   my $acronym = $q->param("acronym");
   my $title = $q->param("title");
   my ($status_date,$note,$agenda,$token_name,$pwg_cat_id,$telechat_date) = db_select($dbh,"select status_date,note,agenda,token_name,pwg_cat_id, telechat_date from group_internal where group_acronym_id = $gID");
   $note = rm_tr($note);
   $token_name = rm_tr($token_name);
   my $agenda_str = "";
   if ($agenda) {
     $agenda_str .= qq{
	    <input type="checkbox" checked name="agenda">
};
   } else {
     $agenda_str .= qq{
	    <input type="checkbox" name="agenda">
};

   }
   my $default_telechat_date = "";
   $default_telechat_date = qq{<option value="$telechat_date">$telechat_date</option>} if (my_defined($telechat_date));
   my $pwg_cat_list = get_pwg_cat_list($pwg_cat_id);
   my $token_name_options = "";
   my @List = db_select_multiple($dbh,"select first_name from iesg_login where user_level=1 order by first_name");
   for my $array_ref (@List) {
     my ($first_name) = @$array_ref;
     my $selected = ($token_name eq $first_name)?"selected":"";
     $token_name_options .= qq{"<option value="$first_name" $selected>$first_name</option>
};
   } 
   $html_txt = "";
   $html_txt .= qq{<h4>Edit PWG list</h4>
   $table_header
   <tr><td>
   $form_header
   <input type="hidden" name="acronym_id" value="$gID">
   <input type="hidden" name="command" value="edit_db">
   <font color="red"><b>$title ($acronym)</b></font><br><br>
   Status Date: <input type="text" name="status_date" value="$status_date"><br>
   Token Name: <select name="token_name">
$token_name_options
</select><br>
   Check for Agenda: $agenda_str on <select name="telechat_date">
$default_telechat_date
$telechat_date_list
</select><br>
   Agenda Category: <select name="pwg_cat_id">
$pwg_cat_list
</select><br>
   Note: <br>
   <textarea name="note" cols="40" rows="5" wrap="virtual">$note</textarea><br>
   <input type="submit" value="CONFIRM EDIT">
   </form>
   </td></tr></table>
   };
   return $html_txt;
}

sub edit_db {
   my $q = shift;
   my $gID = $q->param("acronym_id");
   my $status_date = $q->param("status_date");
   my $note = $q->param("note");
   my $pwg_cat_id = $q->param("pwg_cat_id");
   my $agenda = $q->param("agenda");
   my $telechat_date = db_quote($q->param("telechat_date"));
   my $token_name = $q->param("token_name");
   if ($agenda eq "on") {
      $agenda_val = 1;
   } else {
      $agenda_val = 0;
   }
   $agenda_val = 0 if ($pwg_cat_id == 11 or $pwg_cat_id == 21);
   $status_date = y_two_k($status_date);
   $status_date = db_quote($status_date);
   $note = db_quote($note);
   $token_name = db_quote($token_name);
   $sqlStr = qq{update group_internal set note = $note, status_date = $status_date, agenda=$agenda_val, token_name=$token_name, pwg_cat_id=$pwg_cat_id, telechat_date=$telechat_date
   where group_acronym_id = $gID};
   db_update($dbh,$sqlStr,$program_name,$user_name);
   my $html_txt = gen_pwg($q);
   
   return $html_txt;
}

sub delete_pwg {
	     $filename = shift;
		 my $html_txt = "";
		 $cnt = unlink $filename;
         my @str = split '/',$filename;
	     my $filename_simple = $str[$#str];
		 if ($cnt) {
    	     $html_txt .= qq{<b>$filename</b> is deleted<br>};
	     } else {
    	     $html_txt .= qq{<b>$filename</b> cannot be deleted<br>};
		 }
    	return $html_txt;
}


sub discuss_comment_submit {
  my $q = shift;
  my $ballot_id = $q->param("ballot_id");
  my $filename = $q->param("filename");


    $q->param(filename=>$filename);



  
  if (defined($q->param("save_discuss_comment")))
  {
      update_ballot_comment_db($q);

  }
  elsif (defined($q->param("save_and_send_email")))
 	{
	    update_ballot_comment_db($q);
	    send_ballot_comment_to_iesg($q);

	}


}




 

