
package Lock;
use Exporter ();
@ISA = qw(Exporter);

@EXPORT = qw(lock_file unlock_file);


## Both lock_file and unlock_file expect a rooted pathname to the file
## to be locked or unlocked.  Locking is accomplished by creating a
## ".lck" file along side the real file which is open'ed and flock'ed.
## Unlocking removes the file and then closes it.
##
## It is essential that files are explicitly unlocked to ensure that the
## lock file droppings are cleaned up.
##
## The default lock age is 15 minutes (900 seconds), after which it
## is considered droppings and cleaned up.
##
## RETURN
#    1 if successful
##   0 otherwise


## some global values

my ($SRAND, $MAXTRIES, $OLD);
my ($LOCK_SH, $LOCK_EX, $LOCK_NB, $LOCK_UN, $EWOULDBLOCK);

$SRAND    = 0;		   # set to 1 after srand is called first time

# maximum times to try lock; 2 ** 7 is 128, which is 256 seconds of
# sleep the last time, which is 512 seconds total and thus 8 minutes

$MAXTRIES = 7;

# maximum age of lock_file, after which it should be removed

$OLD      = 900;

# arguments to flock

$LOCK_SH = 1;
$LOCK_EX = 2;
$LOCK_NB = 4;
$LOCK_UN = 8;

# errno values

$ENOENT      = 2;		# no such file or directory
$EWOULDBLOCK = 11;		# for non-blocking call to flock


## some global variables

my (%locks);		     # maintains the filehandles of locked files


## unlock_file expects a rooted path to the file to be unlocked.
##
## if the file is not currently locked we check for an old lock file and
## remove it if necessary.  if it is removed we return true, that is the
## unlock is considered successful.  calling routines can check for an
## old lock file by knowing they do not have it locked and calling
## unlock_file to see if it returns true.
##
## the age to permit on the lock file can be set with the optional
## second argument.  the default is $OLD.  to always remove the lock
## file, if it exists, set the age to 0.
##
## RETURN 1 if successful 0 otherwise

sub unlock_file ( $;$ ) {
    my $lock   = shift;
    my $old_in = shift;

    my $locker = "$lock.lck";
    my $my_old = $OLD;


    $my_old = $old_in if defined $old_in;

    if ($locks{$lock}) {

	# must unlink first to avoid race conditions

	unlink $locker or do {
	    warn "$locker: unlink: $!, continuing";
	};

	unlink "$locker.$$" or do {
	    warn "$locker.$$: unlink: $!, continuing";
	};

	close  $locks{$lock} or do {
	    warn "$locker: close: $!, continuing";
	};

	delete $locks{$lock};

	return 1;
    }

    if ( -e $locker) {
	my ($mtime, $old);

	$mtime = (stat $locker)[9];

	# it is possible the file disappeared between -e and stat.  in
	# that case the lock is gone and we choose to return success so
	# the calling routine can move ahead quickly (instead of
	# potentially sleeping).

	if ( ! $mtime) {
	    warn "$locker: unlock_file: lock disappeared, continuing";
	    return 1;
	}

	$old = time - $mtime;

	if ($old >= $my_old) {
	    warn "$locker: unlock_file: age($old) >= $my_old, unlinking";

	    unlink $locker or do {
		warn "$locker: unlock_file: unlink: $!, continuing";
	    };

	    return 1;
	}
    }

    return 0;
}


## lock_file expects a rooted path to the file to be locked.  the
## optional second argument allows the caller to specify the number of
## times to try to lock the file, which implicitly affects the wait
## time.  the default is $MAXTRIES; setting $tries to 0 ensures only 1
## attempt to lock the file.
##
## RETURN 1 if successful 0 otherwise

sub lock_file ( $;$ ) {
    my $lock  = shift;
    my $tries = shift;

    my $locker   = "$lock.lck";
    my $loop     = 0;
    my $start    = time();
    my $my_tries = $MAXTRIES;

    local *LOCK;


    ## if we already have this lock complain about the double

    if ($locks{$lock}) {
	my ($package, $filename, $line);

	($package, $filename, $line) = caller;

	warn "$lock: lock_file: already locked, from $filename line $line";
	return 1;
    }


    $my_tries = $tries if defined $tries;


    if ( ! $SRAND) {
	srand(time() ^ ($$ + ($$ << 15))); # from Perl book in srand
	$SRAND = 1;
    }


    while (1) {
	open LOCK, "$locker" or do {

	    ## the file does not exist so the lock is available

	    open LOCK, ">$locker" or do {
		my ($msg, $package, $fname, $line);

		$msg = "$!";

		($package, $fname, $line) = caller;

		## this can not be good

		warn ">$locker: lock_file: open: $msg, from $fname line $line";
		return 0;
	    };

	    flock LOCK, ($LOCK_EX | $LOCK_NB) or do {
		my ($msg, $package, $fname, $lin);


		## to be here means we got beat to the lock.  we will
		## wait a short while and try again.

		if ($! == $EWOULDBLOCK) {
		    close LOCK;	# do this inside to keep flock errno

		    if ($loop >= $my_tries) {
			my $end = time();
			my $min;

			$min = int(($end - $start) / 60);

			warn sprintf "%s: lock_file: failed %d tries (%dm%ds)",
			$lock, ++$loop, $min, (($end - $start) - ($min * 60));

			return 0;
		    }

		    sleep((++$loop ** 2) + int(rand 60) + 1);
		    next;
		}


		## else no idea what the problem is so give up

		$msg = "$!";

		($package, $fname, $lin) = caller;

		warn ">$locker: lock_file: flock: $msg, from $fname line $lin";

		close LOCK;

		return 0;
	    };

	    # we win.  make a record for use by unlock_file and us

	    $locks{$lock} = *LOCK;

	    link "$locker", "$locker.$$" or do {
		warn "$locker $$: link: , continuing";
	    };

	    return 1;
	};


	## if were able to open the file for reading then it exists and
	## someone else has it locked.  so we close it and try again.

	close LOCK or do {
	    my ($msg, $package, $filename, $line);

	    $msg = "$!";

	    ($package, $filename, $line) = caller;

	    ## this can not be good

	    warn "$locker: lock_file: close: $!, from $filename line $line";
	    return 0;
	};

	if ($loop >= $my_tries) {
	    my $end = time();
	    my $min;

	    $min = int(($end - $start) / 60);

	    warn sprintf "%s: lock_file: failed %d tries (%dm%ds)",
	    $lock, ++$loop, $min, (($end - $start) - ($min * 60));

	    return 0;
	}


	## check with unlock to see if the lock is old but only if we
	## are not the one who already has it

	if ($locks{$lock}) {
	    # is this even possible??
	    warn "HUH?? $lock: lock_file: already locked";
	    return 0;
	}
	# else

	if (unlock_file $lock) {
	    warn "$lock: lock_file: unlock_file cleared lock";
	    next;
	}
	# else lock not old so sleep and try again

	sleep((++$loop ** 2) + int(rand 10) + 1);
	next;
    }
}

1;
