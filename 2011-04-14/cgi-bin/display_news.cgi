#!/usr/bin/perl
##########################################################################
# Copyright © 2003, Foretec Seminars, Inc.
##########################################################################

use lib '/a/www/ietf-datatracker/release';
use CGI;
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

init_database("ietf");
my $q = new CGI;
my $template_type = $q->param("template_type");
my $title = "";
if ($template_type == 1) {
  $title = "Working Group News";
} elsif ($template_type == 2) {
  $title = "IAB News We can use";
} elsif ($template_type == 3) {
  $title = "Management Issues";
} else {
  $title = "Unknown";
}
my $html_body = get_html_body();

print <<END_HTML;
Content-type: text/html

<HTML>
<HEAD><TITLE>$title</TITLE></HEAD>
<BODY>
<h2>$title</h2>
$html_body
</BODY>
</HTML>
END_HTML


sub get_html_body {
  my $html_body = "";
  my @List = db_select_multiple("select template_title,template_text from templates where template_type=$template_type");
  for $array_ref (@List) {
    my ($template_title,$template_text) = @$array_ref;
    $html_body .= qq{
<b><li> $template_title</b>
<pre>
$template_text
</pre>
<p>
};

  }
  return $html_body;
}
