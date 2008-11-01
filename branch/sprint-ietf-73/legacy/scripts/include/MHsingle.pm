
package MHsingle;
use Exporter ();
@ISA = qw(Exporter);

@EXPORT = qw(MHsingle);


use Lock;


## some locally global constants


## the MHonArc command itself

my ($MHONARC);

$MHONARC = "/usr/bin/mhonarc";


## the MHonArc configuration file

my ($MHONARCRC);

$MHONARCRC = "mhonarc.rcfile";


## MHsingle - $archive is expected to be the rooted path to a list's
## web archive.  The tail of this path is used as the name of the
## list.  Optionally, the name of the list can be specified as the
## second argument $list.
##
## Note that $archive is the "top" of the list's web archive, where
## we expect to find the $MHONARC configuration file for the list,
## i.e., $MHONARCRC.  we look in the "incoming" subdirectory of
## $archive to see if there are messages to process.  each message
## is passed to $MHONARC one at a time.
##
## RETURNS
##   1 if successful
##   0 otherwise and writes with warn

sub MHsingle ( $;$ ) {
    my $archive = shift;
    my $list    = shift;

    my ($incoming, @msgs, $msg, $precmd);


    if ( ! $list) {
	if ($archive =~ m|.*?/(.+)$|o) {
	    $list = $1;
	} else {
	    warn "$archive: not a rooted path";
	    return 0;
	}
    }
    # else $list is the name of the list


    $incoming = "$archive/incoming";

    if ( ! -e $incoming) {

	## this should never happen but we decide it is not fatal

	return 1;
    }
    # else we have something called incoming

    if ( ! -d $incoming) {
	warn "$incoming: not a directory";
	return 0;
    }
    # else we have our incoming directory of messages


    ## last thing before we start is to set a cooperative lock to
    ## ensure that not more than one of us attempts to add messages
    ## to the web archive at a time.  it doesn't make sense to lock
    ## each message file individually because $MHONARC has a
    ## cooperative lock for itself that prevents more than one of
    ## itself from adding messages to an archive.  we are just
    ## getting ahead of that by having our own.

    lock_file "$archive/.MHsingle" or do {

	## since our lock file seems to be busy we'll just move on.
	## if there are any messages to be processed they'll be
	## picked up next time.

	return 1;
    };


    ## if the file exists then we assume the archive is busy and
    ## simply move on.  that's the cooperative lock we want.
    ## there's always the chance that some prior execution exited
    ## abruptly and without cleaning up, but we're going to assume
    ## that gets noticed in some out-of-band way and the lock file
    ## would thus be cleaned up manually.

    if ( -e "$archive/.MHsingle") {
	unlock_file "$archive/.MHsingle";
	return 1;
    };

    open MHlock, ">$archive/.MHsingle" or do {
	warn ">$archive/.MHsingle: open: $!";
	unlock_file "$archive/.MHsingle";
	return 0;
    };


    ## we write our PID into the lock file, to help manual
    ## intervention.

    print MHlock sprintf "%d\n", $$;

    close MHlock or do {
	warn ">$archive/.MHsingle: close: $!";
	unlock_file "$archive/.MHsingle";
	return 0;
    };

    unlock_file "$archive/.MHsingle" or do {
	warn "$archive/.MHsingle: unlock_file failed";

	## this really should never happen.  it's uncertain if we
	## should remove our lock file here.  we should have a lock
	## that needs to be removed but if we failed to remove it
	## perhaps something else bad has happened and we no longer
	## "own" the file.  best to leave things for manual cleanup.

	return 0;
    };


    ## the cooperative lock is all set.  let's get to it.  from this
    ## point forward make sure to remove the lock file before
    ## returning.

    opendir IN, $incoming or do {
	warn "$incoming: opendir: $!";
	unlink "$archive/.MHsingle";
	return 0;
    };


    ## NOTE WELL: the prefix "msg" is set by the ARCHIVE-MAIL script

    @msgs = sort grep /^msg/o, readdir IN;

    closedir IN or do {
	warn "$incoming: closedir: $!";
	unlink "$archive/.MHsingle";
	return 0;
    };


    ## if there's nothing to do we're done

    if ( ! @msgs) {
	unlink "$archive/.MHsingle";
	return 1;
    }


    ## setup the static part of the MHONARC command.  note that
    ## MHONARC must read single messages from STDIN in order to add
    ## it to an archive.  this is consistent with its Sendmail
    ## history since it would have been at the end of a pipe in an
    ## alias file.  do not use the "-single" option of MHONARC
    ## because it does not add to an archive it just dumps the
    ## conversion to STDOUT.

    $precmd = join " ",
    $MHONARC,
    "-umask 000",
    "-outdir $archive/current",
    "-definevar list-name=$list",
    "-rcfile $archive/$MHONARCRC",
    "-quiet",
    "-add",
    "<";

    ## process each message

    foreach $msg ( @msgs ) {
	if (system join " ", $precmd, "$incoming/$msg") {
	    warn sprintf "%s %s/%s: returned 0x%#04x",
	    $precmd, $incoming, $msg, $?;

	    ## we choose to just leave the message and try again
	    ## next time.  if we're really worried about messages
	    ## not being processed the thing to do is check the age
	    ## of the message files -- with some external process --
	    ## and report files that appear to be "old".

	    ## the other issue here is that it's possible $MHONARC
	    ## had a real problem, like perhaps it's cooperative
	    ## lock file got left around.  this means that we're not
	    ## processing any messages and we're wasting time
	    ## starting up $MHONARC just so it can unceremoniously
	    ## exit.  well, you can't account for everything.  we
	    ## will at least behave sanely and wait for the problem
	    ## to get noticed in some other way and then get fixed.

	    next;
	}
	# else fall through


	## since we have successfully added the message to the
	## archive let's remove it from the incoming folder.

	unlink "$incoming/$msg" or do {
	    warn "$incoming/$msg: unlink: $!";

	    ## we decide this is not fatal and just move on.  if the
	    ## file is left around and processed again, $MHONARC is
	    ## smart in that it won't add a message to an archive
	    ## more than once.  so, if the failure is temporary the
	    ## file will get removed next time.  if not then yes, we
	    ## are spinning our wheels on this one message file,
	    ## unless there's some deeper problem.  in the latter
	    ## case hopefully it will get noticed in some external
	    ## way and addressed.  we at least do our best to behave
	    ## sanely.
	};
    }


    ## yeah, we processed all messages and we're done.

    unlink "$archive/.MHsingle" or do {
	warn "$archive/.MHsingle: unlink: $!";

	## we decide this is not fatal.  even if we wanted it to be
	## fatal what is there to be done?

    };


    return 1;
}

1;
