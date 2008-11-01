#!/usr/bin/perl -w
use strict;
umask 0;


## this script expects to be called at some regular interval from
## cron.  it steps through all lists and adds all messages that have
## arrived since the last invocation to the web archive.
## optionally, list names may be specified on the command line, in
## which case only those lists will be processed.
##
## when processing lists we explicitly ignore "." files and
## $WEB_TEMPLATE_DIR.


BEGIN {

    ## this needs to be set to the location of MHsingle

    unshift @INC, ".";
}


use MHsingle;


## some global constants


## This specifies the base directory for the unsecure web archives.
## IT *MUST* BE A ROOTED PATH.  The LIST_NAME will be appended to
## this to form the base directory for a list's archive.

my ($UNSECURE_WEB_ARCHIVE);

$UNSECURE_WEB_ARCHIVE = "/a/www/ietf-mail-archive/web";


## This is the template directory for a web archive of a mailing
## list.

my ($WEB_TEMPLATE_DIR);

$WEB_TEMPLATE_DIR = "/a/www/ietf-mail-archive/web/000TEMPLATE";


##
## MAIN
##


## main variables

my (@lists, $list);


while (@ARGV) {
    $_ = shift @ARGV;

    push @lists, $_;
}


## load up all lists if none were specified on the command line.

if ( ! @lists) {
    opendir WEB, $UNSECURE_WEB_ARCHIVE or do {
	die "$UNSECURE_WEB_ARCHIVE: opendir: $!";
    };

    @lists = sort grep /^[^\.]/o, readdir WEB;

    closedir WEB or do {
	die "$UNSECURE_WEB_ARCHIVE: closedir: $!";
    };
}
# else lists were specified on the command line


## process each list

foreach $list ( @lists ) {
    MHsingle "$UNSECURE_WEB_ARCHIVE/$list", $list or do {
	warn "$UNSECURE_WEB_ARCHIVE/$list: MHsingle failed, cont.";
	next;
    };
}


## yeah, success!

exit 0;
