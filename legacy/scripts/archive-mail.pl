#!/usr/bin/perl -w
use strict;
umask 0;


## Rather than use the Mailman archive system directly, this script
## is used by Mailman to create a text-based and web-based archive
## for mailing lists.  It is invoked as follows:
##
##   $0 LIST_NAME ARCHIVE_STYLE
##
## LIST_NAME is the name of the list, which is often the working
## group acronym.  If LIST_NAME is a new list then all directories
## and infrastructure needed is created automatically **BUT KEEP
## READING**.
##
## ARCHIVE_STYLE was added in the new system and should be either:
## -public or -private.  This creates both the text and web archive
## in either the unsecure or secure location, respectively.  For
## backwards compatibility we recognize "-text", "-textsecure",
## "-web" and "-websecure" and create either the text or the web
## archive accordingly.  If ARCHIVE_STYLE has any other value or is
## missing then "-public" is assumed.


## This script is careful to exit with one of two values: 0 or
## EX_TEMPFAIL as defined in <sysexits.h>.  This is appropriate for
## postfix in particular but also most Sendmail-like mail systems.
##
## What this means is that if something "bad" happens the message
## should stay in the queue and will continue to get retried
## according to the mail system queue processing.  Of course, if the
## "bad" thing was temporary this is exactly what you would like.
## If the "bad" thing was bad and permanent then I sure hope you're
## monitoring your email system.


## NOTE WELL: A secure web archive does *NOT* exist.  There is some
## code here for it (if it should come into existence) but it is not
## guaranteed to work.  It is more of a placeholder that needs to be
## carefully reviewed and tested if it is to be used.  All attempts
## to create a secure web archive are silently ignored.


BEGIN {

    ## this needs to be set to the location of Lock.pm and Tmpfil.pm 

    unshift @INC, ".";
}


use Lock;
use Tmpfil;


## some global constants


## this is defined in <sysexits.h>

my ($EX_TEMPFAIL);

$EX_TEMPFAIL = 75;


## These specify the base directory for both the secure and unsecure
## versions of both the text and web archives.  THEY *MUST* BE A
## ROOTED PATH.  THEY *MUST* EXIST.  WE *DO NOT* CHECK.  The
## LIST_NAME will be appended to this to form the base directory for
## a list's archive.

my ($UNSECURE_ARCHIVE,     $SECURE_ARCHIVE,
    $UNSECURE_WEB_ARCHIVE, $SECURE_WEB_ARCHIVE);

$UNSECURE_ARCHIVE = "/a/www/ietf-mail-archive/text";
$SECURE_ARCHIVE   = "/a/www/ietf-mail-archive/text-secure";

$UNSECURE_WEB_ARCHIVE = "/a/www/ietf-mail-archive/web";
$SECURE_WEB_ARCHIVE   = "/a/www/ietf-mail-archive/web-secure";


## This is the template directory for a web archive of a mailing
## list.  It *MUST* have the default MHonArc configuration file and
## the default "index" files that the web server needs.  WE *DO NOT*
## CHECK.
##
## However, the directory infrastructure used for the web and text
## archive need not exist.  We check this and fix as needed.

my ($WEB_TEMPLATE_DIR);

$WEB_TEMPLATE_DIR = "/a/www/ietf-mail-archive/web/000TEMPLATE";


## copydir - recursively copies the contents of $fromdir to $todir.
## by default we only allow 10 recursive calls, which can be
## changed by setting $depth, the optional third parameter.
##
## if $depth is set to 0 (distinct from undefined) then no recursion
## is allowed.
##
## if $depth is set to a value less than 0 then the recursion is
## infinite (almost :-).  $fromdir must exist but $todir will be
## created if it does not exist.
##
## RETURNS
##   1 if successful
##   0 otherwise and writes using warn

sub copydir ( $$;$ ) {
    my $fromdir = shift;
    my $todir   = shift;
    my $depth   = shift;

    my (@copys, $copy);


    $depth = 10 if ! defined $depth;


    opendir FROMDIR, $fromdir or do {
	warn "$fromdir: opendir: $!";
	return 0;
    };

    @copys = readdir FROMDIR or do {
	warn "$fromdir: readdir: $!";

	closedir FROMDIR;
	return 0;
    };

    closedir FROMDIR or do {
	warn "$fromdir: closedir: $!";
	return 0;
    };


    if ( ! -e $todir) {
	mkdir $todir, 0777 or do {
	    warn "$todir: mkdir: $!";
	    return 0;
	};
    } elsif ( ! -d $todir) {
	warn "$todir: not a directory";
	return 0;
    }
    # else we are all set


    foreach $copy ( @copys ) {
	if ( -d "$fromdir/$copy") {
	    if ($depth) {
		--$depth;

		&copydir("$fromdir/$copy", "$todir/$copy", $depth) or do {
		    warn "$fromdir/$copy $todir/$copy: copydir failed";
		    return 0;
		};
	    } else {
		warn "$fromdir/$copy: infinite recursion";
		return 0;
	    };

	    next;
	}
	# else we copy the file

	open TO, ">$todir/$copy" or do {
	    warn ">$todir/$copy: open: $!";
	    return 0;
	};

	open FROM, "$fromdir/$copy" or do {
	    warn "$fromdir/$copy: open: $!";
	    close TO;
	    return 0;
	};

	print TO while <FROM> or do {
	    warn "$fromdir $todir/$copy: print: $!";
	    close FROM;
	    close TO;
	    return 0;
	};

	close FROM or do {
	    warn "$fromdir/$copy: close: $!";
	    close TO;
	    return 0;
	};

	close TO or do {
	    warn ">$todir/$copy: close: $!";
	    return 0;
	};
    }


    return 1;
}


##
## MAIN
##


## main variables

my ($now, $wg, $astyle);
my ($headers, $body);

my ($TEXT_TARGET_DIR,     $WEB_TARGET_DIR);
my ($WG_TEXT_ARCHIVE_DIR, $WG_WEB_ARCHIVE_DIR);


$now = time;


## get command line arguments

if (@ARGV == 2) {
    $wg     = shift @ARGV;
    $astyle = shift @ARGV;
} elsif (@ARGV == 1) {
    $wg     = shift @ARGV;
    $astyle = "-public";
} else {
    print STDERR <<HELP;

$0 LIST_NAME ARCHIVE_STYLE

LIST_NAME is often the working group acronym

ARCHIVE_STYLE is optional or one of the preferred options
    "-private" or "-public"
It may be one of the older options of:
    "-textsecure", "-text", "-websecure", or "-web"
The default is "-public" if it is absent or unrecognized.

HELP

    exit $EX_TEMPFAIL;
}


## grab the entire message.  we grab the headers and body
## separately because we need access to each separately.

# to grab just the headers we slurp them all at once by changing the
# read delimiter.  note that the slurping retains the "extra"
# newline that is needed to separate the headers from the body.

$/       =  "";                 # slurp it all at once
$headers =  <STDIN>;
$/       =  "\n";               # no more slurping
$headers =~ s/\n\s+/ /go;       # fold up continuation lines

$body    =  join "", <STDIN>;


## we want to skip SPAM and the unfortunate password reminders that
## we get.  we take care of this right away so we can just exit if
## we are done.  we check the headers for the spam flag and the body
## for the password reminder.

{
    my ($ignore);

    $ignore = 0;

    $headers =~ /^X\-Spam\-Status: Yes/imo                   and $ignore = 1;
    $body    =~ /This is a reminder, sent out once a month/o and $ignore = 1;

    if ($ignore) {
	exit 0;
    }
}


## setup the target base for the parent of the archive.  this sets
## the "target" directory based on whether it is a secure archive or
## not.  the LIST_NAME will be appended to this to form the base of
## the actual archive.
##
## there are two targets: one for text and one for the web.  if we
## are invoked with one of the old arguments then we setup for only
## the indicated archive.

if ($astyle eq "-public") {
    $TEXT_TARGET_DIR=$UNSECURE_ARCHIVE;
    $WEB_TARGET_DIR=$UNSECURE_WEB_ARCHIVE;

} elsif ($astyle eq "-private") {
    $TEXT_TARGET_DIR=$SECURE_ARCHIVE;
    ## $WEB_TARGET_DIR=$SECURE_WEB_ARCHIVE;

} elsif ($astyle eq "-text") {
    $TEXT_TARGET_DIR=$UNSECURE_ARCHIVE;

} elsif ($astyle eq "-textsecure") {
    $TEXT_TARGET_DIR=$SECURE_ARCHIVE;

} elsif ($astyle eq "-web") {
    $WEB_TARGET_DIR=$UNSECURE_WEB_ARCHIVE;

} elsif ($astyle eq "-websecure") {
    # $WEB_TARGET_DIR=$SECURE_WEB_ARCHIVE

} else {

    ## we assume "-public" in all other cases

    $TEXT_TARGET_DIR=$UNSECURE_ARCHIVE;
    $WEB_TARGET_DIR=$UNSECURE_WEB_ARCHIVE;
}


## first step is to create the base directories for a list's
## archive.  this is normally only done once when a list is first
## created.

if ($TEXT_TARGET_DIR) {

    ## setup the text archive directory

    $WG_TEXT_ARCHIVE_DIR = "$TEXT_TARGET_DIR/$wg";

    if ( ! -d $WG_TEXT_ARCHIVE_DIR) {
	mkdir $WG_TEXT_ARCHIVE_DIR, 0777 or do {
	    warn "$WG_TEXT_ARCHIVE_DIR: mkdir: $!";
	    exit $EX_TEMPFAIL;
	};
    }
}

if ($WEB_TARGET_DIR) {

    ## setup the web archive directory

    $WG_WEB_ARCHIVE_DIR = "$WEB_TARGET_DIR/$wg";

    if ( ! -d $WG_WEB_ARCHIVE_DIR) {
	mkdir $WG_WEB_ARCHIVE_DIR, 0777 or do {
	    warn "$WG_WEB_ARCHIVE_DIR: mkdir: $!";
	    exit $EX_TEMPFAIL;
	};


	## in the case of the web archive we have to copy the
	## template directory

	copydir $WEB_TEMPLATE_DIR, $WG_WEB_ARCHIVE_DIR or do {
	    warn "$WEB_TEMPLATE_DIR $WG_WEB_ARCHIVE_DIR: copydir failed";
	    exit $EX_TEMPFAIL;
	};
    }

    # if the web archive directory does exist we check to make sure
    # the subdirectories we need exist.  this is for backwards
    # compatibility.

    else {
	if ( ! -d "$WG_WEB_ARCHIVE_DIR/current") {
	    mkdir "$WG_WEB_ARCHIVE_DIR/current", 0777 or do {
		warn "$WG_WEB_ARCHIVE_DIR/current: mkdir: $!";
		exit $EX_TEMPFAIL;
	    };
	}

	if ( ! -d "$WG_WEB_ARCHIVE_DIR/incoming") {
	    mkdir "$WG_WEB_ARCHIVE_DIR/incoming", 0777 or do {
		warn "$WG_WEB_ARCHIVE_DIR/incoming: mkdir: $!";
		exit $EX_TEMPFAIL;
	    };
	}
    }
}


## append the message to the archive(s).  we are careful to do the
## web archive first because we need to edit the message to put it
## in the raw text archive.


if ($WG_WEB_ARCHIVE_DIR) {
    my ($msgfil, $tmpfil);


    ## we include the current time in the file name so the messages
    ## will sort and can be added to the web archive in the order
    ## they arrive.

    ## NOTE WELL: the script that does the call to MHONARC requires
    ## that message file names begin with "msg".

    $msgfil = tmpfil sprintf "%s%d", "$WG_WEB_ARCHIVE_DIR/incoming/msg", $now;


    ## what we want is to create the message file in a way that
    ## ensures it will not be used by the actual archive process
    ## until it is ready.  easy way to do this is to create the file
    ## as a "." file and to have the archive process ignore "."
    ## files.

    $tmpfil =  $msgfil;
    $tmpfil =~ s|^(.*/)(.*)$|$1\.$2|o;


    ## output the message.  do not need to lock this first because
    ## it is a guaranteed unique file for my process.

    open MSG, ">$tmpfil" or do {
	warn ">$tmpfil: open: $!";
	exit $EX_TEMPFAIL;
    };

    # $headers has the extra newline needed to separate it from the body

    print MSG $headers, $body or do {
	warn ">$tmpfil: print: $!";
	exit $EX_TEMPFAIL;
    };

    close MSG or do {
	warn ">$tmpfil: close: $!";
	exit $EX_TEMPFAIL;
    };


    ## now we rename $tmpfil as $msgfil.  this is guaranteed to be
    ## an atomic operation as long as $tmpfil and $msgfil are in the
    ## same file system, which they since $tmpfil is just a "dot
    ## file" copy of $msgfil.

    rename $tmpfil, $msgfil or do {
	warn "$tmpfil $msgfil: rename: $!";
	exit $EX_TEMPFAIL;
    };
}


if ($WG_TEXT_ARCHIVE_DIR) {
    my ($msgfil, $year, $mon, $tmpfil, $file);

    ($year, $mon) = (localtime $now)[4..5];

    $year += 1900;
    $mon  += 1;

    $msgfil = sprintf "%s/%04d-%02d.mail", $WG_TEXT_ARCHIVE_DIR, $year, $mon;
    $tmpfil = tmpfil $msgfil;


    ## for backwards compatibility we look to see if a file called
    ## "current" exists.  under the old system all messages were
    ## collected there and then a separate process ran monthly to
    ## put messages into a monthly collection.  in this new system
    ## we skip that step and put the messages in the monthly
    ## collection straight away.


    ## if "current" exists we first move it into the file $msgfil to
    ## convert it to the new system.  if it turns out that both
    ## "current" and $msgfil exist then we have a situation that
    ## requires manual intervention.


    ## transition the "old" current if it exists

    if ( -e "$WG_TEXT_ARCHIVE_DIR/current") {

	## we check for this just to be safe

	if ( -e $msgfil) {
	    warn "$msgfil: SHOULD NOT EXIST, HELP";
	    exit $EX_TEMPFAIL;
	}


	## we assume that it's not fatal for the lock to fail, i.e.,
	## perhaps we are just busy and we'll get it next time, so
	## we exit leaving the message in the queue.  if this is not
	## true then messages should be collecting in the email
	## queue, which will get noticed eventually and the problem
	## will get attention.

	lock_file "$WG_TEXT_ARCHIVE_DIR/current" or do {
	    warn "$WG_TEXT_ARCHIVE_DIR/current: lock_file failed";
	    exit $EX_TEMPFAIL;
	};

	rename "$WG_TEXT_ARCHIVE_DIR/curent", $msgfil or do {
	    warn "$WG_TEXT_ARCHIVE_DIR/curent $msgfil: rename: $!";

	    unlock_file "$WG_TEXT_ARCHIVE_DIR/current";
	    exit $EX_TEMPFAIL;
	};

	unlock_file "$WG_TEXT_ARCHIVE_DIR/current" or do {
	    warn "$WG_TEXT_ARCHIVE_DIR/current: unlock_file failed, cont.";
	};
    }


    ## append this message to the monthly collection: $msgfil.  we
    ## assume that it's not fatal for the lock to fail, i.e.,
    ## perhaps we are just busy and we'll get it next time, so we
    ## exit leaving the message in the queue.  if this is not true
    ## then messages should be collecting in the email queue, which
    ## will get noticed eventually and the problem will get
    ## attention.


    ## we go to a lot of trouble here to avoid corrupting our
    ## archive.  this works as long as rename is both atomic and it
    ## unlinks the destination if it exists.  this is true on UNIX
    ## systems as long as the old and new files are both on the same
    ## file system.  the logic is as follows.
    ##
    ## copy archive to temporary file
    ## append message to temporary file
    ## hard link archive to backup file
    ## rename temporary to archive
    ## remove backup file


    lock_file $msgfil or do {
	warn "$msgfil: lock_file failed";
	exit $EX_TEMPFAIL;
    };

    open TMPFIL, ">$tmpfil" or do {
	warn ">$tmpfil: open: $!";
	unlock_file $msgfil;
	exit $EX_TEMPFAIL;
    };

    if ( -e $msgfil) {
	open MSGFIL, $msgfil or do {
	    warn "$msgfil: open: $!";
	    unlock_file $msgfil;
	    exit $EX_TEMPFAIL;
	};

	print TMPFIL while <MSGFIL> or do {
	    warn ">$tmpfil: print: $!";
	    unlock_file $msgfil;
	    exit $EX_TEMPFAIL;
	};

	close MSGFIL or do {
	    warn "$msgfil: close: $!";
	    unlock_file $msgfil;
	    exit $EX_TEMPFAIL;
	};

	# TMPFIL needs to remain open
    }

    # else nothing to copy, leave TMPFIL open


    ## unfortunately, we use UNIX style mbox files to store the raw
    ## message monthly collections.  this means we are at risk for
    ## parsing problems when messages have lines in their body
    ## beginning with "From " because lines with that syntax delimit
    ## messages.  to avoid this conflict the accepted solution is to
    ## change all such lines in the body that begin "From " to
    ## ">From ".  it's ugly but what can you do.  we need this just
    ## in case we ever recreate the web archives from the raw
    ## messages or ever use some other mbox tool on these
    ## collections.  also, we need to make sure all message
    ## delimiters start a new line so we insert one.

    $body =~ s/^From />From /omg;

    print TMPFIL "\n", $headers, $body or do {
	warn ">$tmpfil: print: $!";
	unlock_file $msgfil;
	exit $EX_TEMPFAIL;
    };

    close TMPFIL or do {
	warn ">$tmpfil: close: $!";
	unlock_file $msgfil;
	exit $EX_TEMPFAIL;
    };


    ## we have a new archive with the new message.  we backup the
    ## existing archive and move the new archive into its place.

    link $msgfil, "$msgfil.bak$$" or do {
	warn "$msgfil->.bak$$: link: $!";
	unlock_file $msgfil;
	exit $EX_TEMPFAIL;
    };

    rename $tmpfil, $msgfil or do {
	warn "$tmpfil $msgfil: rename: $!";
	unlock_file $msgfil;
	exit $EX_TEMPFAIL;
    };


    ## success!  clean up the backup file and we are done.
    unlink "$msgfil.bak$$" or do {
	warn "$msgfil.bak$$: unlink: $!, cont.";
	unlock_file $msgfil;
	exit $EX_TEMPFAIL;
    };


    ## there's nothing to be done if this fails, nor is it fatal.
    ## the lock may delay delivery of a few messages but it will
    ## eventually become stale and we'll move on.

    unlock_file $msgfil or do {
	warn "$msgfil: unlock_file failed, cont.";
    };

}


## YEAH!  We succeeded.

exit 0;
