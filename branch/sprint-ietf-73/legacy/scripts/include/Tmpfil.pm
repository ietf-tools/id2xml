
package Tmpfil;
use Exporter ();
@ISA = qw(Exporter);

@EXPORT = qw(tmpfil);


## some global variables

my ($TMPDIR, $TMPPRE, $CNTFIL);

$TMPDIR      = "/tmp";
$TMPPRE      = "tf$$";
$CNTFIL      = "aa";


## tmpfil creates a new unique filename.  by default files are created
## in /tmp with a name of "tf" concatenated with our PID.  the optional
## argument will be used in place of "tf" unless it begins with "/" in
## which case it will replace all of /tmp/tf.
##
## the filename returned is tested for existence, which should be
## sufficient since the PID is part of the name.

sub tmpfil ( ;$ ) {
    my $prefix = shift;

    my $tmpfil;


    if ($prefix) {
	if ($prefix =~ m|^/|o) {
	    $tmpfil = sprintf "%s%d", $prefix, $$;
	} else {
	    $tmpfil = sprintf "%s/%s%d", $TMPDIR, $prefix, $$;
	}
    } else {
	$tmpfil = join "/", $TMPDIR, $TMPPRE;
    }


    while ( -e ($tmpfil = join "", $tmpfil, $CNTFIL++) ) {
	; # empty body
    }


    return $tmpfil;
}

1;
