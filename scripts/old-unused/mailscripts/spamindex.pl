#!/usr/bin/perl
# $Id: spamindex.pl,v 1.5 2004/02/09 04:00:42 sra Exp $

# Hack to write a simple html index for a maildir and clean out old
# messages.  Intended usage is generating a public listing of recent
# messages rejected by spam filtering.  No doubt the HTML could use
# some prettification.

use strict;
use Mail::Folder::Maildir;
use Date::Parse;
use Date::Format;
use Getopt::Long;
use HTML::Entities;

my $usage = "usage: $0 (defaults in parentheses)
	--maildir	maildir to index (no default)
	--index		html file to write (no default)
	--title		title for html file (maildir)
	--prefix_del	prefix to strip from maildir filenames (none)
	--prefix_add	prefix to prepend to maildir filenames (none)
	--ageout	how many days a message stays in maildir (forever)
	--seconds	ageout in seconds, not days (false)
	--debug		dry run (false)
";

# Figure out what we're trying to do.

my %opt;
die($usage) unless GetOptions(\%opt,
		      qw(maildir=s index=s title=s
			 prefix_del=s prefix_add=s
			 ageout=i seconds! debug!))
    and $opt{maildir} and $opt{index};

$opt{ageout} *= 60 * 60 * 24
    unless ($opt{seconds});

$ENV{TZ} = 'GMT';

my $now = time;

# Open the maildir and a temporary output file.

open(F, ">$opt{index}.$$")
    or die("Couldn't open $opt{index}.$$: $!");

my $f = Mail::Folder->new(maildir => $opt{maildir})
    or die("Couldn't open $opt{maildir}: $!");

# Write page header.

print(F "<html>\n<head>\n<title>",
      encode_entities($opt{title} || $opt{maildir}),
      "</title>\n</head>\n<body>\n",
      "<table>\n<tr><td>Date</td><td>From</td><td>Subject</td></tr>\n")
    or die("Couldn't write $opt{index}.$$: $!");

# Sort mailbox, punt messages that are too old,
# print a table row for each message remaining.

for my $m (sort { $a <=> $b } $f->message_list) {
    my $fn = $f->get_message_file($m);
    if ($opt{ageout}) {
	my $t = $now - (stat($fn))[10];
	if ($t > $opt{ageout}) {
	    $f->delete_message($m)
		unless ($opt{debug});
	    next;
	}
    }
    chomp(my ($date, $from, $subject)
	  = $f->get_fields($m, qw(date from subject)));
    $date = time2str("%Y%m%d%H%M%SZ", str2time($date));
    $fn =~ s{^$opt{prefix_del}}{$opt{prefix_add}};
    print(F "<tr>\n<td>", encode_entities($date), "</td>\n",
	  "<td>", encode_entities($from), "</td>\n",
	  "<td><a href=\"", $fn, "\">",
	  encode_entities($subject),
	  "</a></td>\n</tr>\n")
	or die("Couldn't write $opt{index}.$$: $!");
}

# Write page trailer.

print(F "</table>\n<br>\nIndex generated at ",
      time2str("%Y%m%d%H%M%SZ", $now),
      "\n</body>\n</html>\n")
    or die("Couldn't write $opt{index}.$$: $!");

# Close and install the output file.

close(F)
    or die("Couldn't close $opt{index}.$$: $!");

rename("$opt{index}.$$", $opt{index})
    or die("Couldn't rename $opt{index}.$$: $!");

# Force maildir changes out to disk, then we're done.

$f->sync
    unless ($opt{debug});
$f->close;
