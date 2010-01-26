##########################################################################
# Copyright © 2004, Foretec Seminars, Inc.
##########################################################################

package CGI_UTIL;
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(error add_cgi_message registered_command);

use lib '/home/henrik/src/db/legacy/iesg/';
use GEN_UTIL;

sub registered_command {
  my $command=shift;
  my $command_set=shift;
  $command_set = " $command_set ";
  return 0 unless ($command_set =~ / $command /);
}

sub error {
  my ($q,$reason,$partial_html)=@_;
  my $bottom = qq{
<HR>
<i>Please send problem reports to</i> <A HREF="mailto:ietf-action\@ietf.org">ietf-action\@ietf.org</A>.
};
  if (defined($partial_html)) {
    unless ($partial_html == 2) {
      print $q->h1("Error"),
        $q->p("Your request was not processed due to the following error(s): "),
        $q->p($q->i($reason)),
        $q->p($bottom);
    } else {
      print $q->h3("Please return to the previous screen and confirm that you are authorized to update this IPR disclosure.");
      print qq{<form>
<input type="button" value=" Return to Previous Screen " onClick="history.go(-1);return true;">
</form>
<br><br><br>
};
    }
    print $q->end_html;
  } else {
    print $q->header("text/html"),
        $q->start_html("Error"),
        $q->h1("Error"),
        $q->p("Your request was not processed due to the following error(s): "),
        $q->p($q->i($reason)),
        $q->p($bottom),
        $q->end_html;
  }
  exit;
}

sub add_cgi_message {
  my $q=shift;
  my $message = shift;
  $q->param('message'=>"$message");
  return $q;
}

