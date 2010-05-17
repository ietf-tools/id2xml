#!/usr/bin/perl
##########################################################################
#      Copyright (c) 2007 Neustar Secretariat Services, Inc.
#
#      Program: 
#      Author : Sang-Hee Lee, Neustar Secretariat Services
#      Last Modified Date: 2/11/2007
#
#      This Web application provides ... 
#
#####################################################
use lib '/a/www/ietf-datatracker/release';
use GEN_DBUTIL_NEW;
use GEN_UTIL;
use IETF;
use CGI;
use CGI_UTIL;

$script_loc=$ENV{SCRIPT_NAME};
$http_host=$ENV{HTTP_HOST};
$devel_mode = ($script_loc =~ /devel/)?1:0;
$qa_mode = 0;
$dbname = "ietf";

if ($devel_mode) {
  $qa_mode = ($http_host =~ /datatracker/)?1:0;
  $rUser = $ENV{REMOTE_USER};
  $dbname=($qa_mode)?"ietf_qa":"test_idst";
  $mode_text = ($qa_mode)?"QA Mode":"Development Mode";
}
init_database($dbname);
$dbh = get_dbh();
my $q = new CGI;
$style_url="https://www1.ietf.org/css/base.css";
$program_name = "manual_post.cgi";
$program_title = "IETF Internet-Draft Manual Post Tool";
$program_title .= " db: $dbname" if ($devel_mode);
$table_header = qq{<table cellpadding="1" cellspacing="1" border="0">
};
$table_header2 = qq{<table cellpadding="1" cellspacing="1" border="0" width="800">
};
$form_header_post = qq{<form action="$program_name" method="POST" name="form_post">};
$form_header_post2 = qq{<form action="$program_name" method="POST" name="form_post2">};
$form_header_post3 = qq{<form action="$program_name" method="POST" name="form_post3">};
$form_header_bottom = qq{<form action="$program_name" method="POST" name="form_post_bottom">};
$form_header_get = qq{<form action="$program_name" method="GET">};
$form_header_noname = qq{<form action="$program_name" method="GET">
};
$bc="{";
$ec="}";
$color1="#cccccc";
$color2="#eeeeee";
$rUser=$ENV{REMOTE_USER};
$loginid = db_select($dbh,"select person_or_org_tag from iesg_login where login_name='$rUser'") unless $loginid;
$user_name=get_name($loginid);
error ($q,"Invalid User, $rUser") unless $loginid;
$html_top = qq|
<link rel="stylesheet" type="text/css" href="$style_url" />
<blockquote>
<h2><center>$program_title <font color="red"><i>$mode_text</i></font></center></h2>
<i>$user_name</i> logged on
<hr>

|;
$html_bottom = qq{
<hr>
<li>If you require assistance in using this tool, or wish to report a bug, then please send a message to <a href="mailto:ietf-action\@ietf.org">ietf-action\@ietf.org</a>.</li>

</blockquote>
};

$asterisk = "<font color=\"red\"><b>*</b></font>";
$html_body = get_html_body($q);
print $q->header("text/html"),
      $q->start_html(-title=>$program_title),
      $q->p($html_top),
      $q->p($html_body),
      $q->p($html_bottom),
      $q->end_html;

$dbh->disconnect();
exit;

sub get_html_body {
   my $q = shift;
   my $command = $q->param("command");
   my $html_txt = "";
   unless (my_defined($command)) {
     $html_txt .= main_screen();
   } else {
     my $func = "$command(\$q)";
     $html_txt .= eval($func);
   }
   $html_txt .= qq{
$form_header_bottom
<input type="submit" value=" User's First Screen ">
</form>
} if (my_defined($command));
   return $html_txt;
}

sub main_screen {
  my $msg=shift;
  my @List=db_select_multiple($dbh,"select submission_id,filename,revision from id_submission_detail where status_id=5 order by filename");
  my $list_html="";
  for my $array_ref (@List) {
    my ($submission_id,$filename,$revision)=@$array_ref;
    $list_html .= qq{$form_header_get
<input type="hidden" name="command" value="mark_posted">
<input type="hidden" name="submission_id" value="$submission_id">
<Tr><td>$filename-$revision</td><td><input type="submit" value="Mark as Posted"></td></tr>
</form>
};
 
  }
  my @doneList=db_select_multiple($dbh,"select filename,revision,man_posted_by,man_posted_date from id_submission_detail where status_id=-2 order by filename");
  my $done_list_html="";
  for my $array_ref (@doneList) {
    my ($filename,$revision,$man_posted_by,$man_posted_date) = @$array_ref;
    $done_list_html .= "$filename-$revision posted by $man_posted_by on $man_posted_date<br>\n";
  }
  return qq{
<font color="red"><pre>$msg</pre></font><br><br>
<h3>Manual Post Requsted</h3>
$table_header
$list_html
</table>
<hr>
<h3>Manualy Posted</h3>
$done_list_html



};

}

sub mark_posted {
  my $q=shift;
  my $submission_id=$q->param("submission_id");
  my ($filename,$revision) = db_select($dbh,"select filename,revision from id_submission_detail where submission_id=$submission_id");
  db_update($dbh,"update id_submission_detail set status_id=-2,man_posted_by='$rUser',man_posted_date=current_date where submission_id=$submission_id");
  return main_screen("$filename-$revision was successfully marked as POSTED by $rUser");
 
}
