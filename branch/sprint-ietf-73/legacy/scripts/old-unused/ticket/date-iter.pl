#!/usr/bin/perl

use Time::ParseDate;
use Time::CTime;
use DBI;

$stime=parsedate("Jan 1 2006");
$template="%Y-%m-%d";
$oneweek=(60 * 60 * 24 * 7);
# $oneyear=(60 * 60 * 24 * 7 * 52) + $lastweek;
# $oneyear=parsedate("Jan 28 2007");
$oneyear=parsedate("Jan 8 2006");
$oneyear=parsedate("Dec 31 2006");
$etime=$stime + $oneweek;
# $ttime=parsedate("today");

$begintime=strftime($template, localtime(0)); 
# $today=strftime($template, localtime($ttime)); 

my $dsn = 'DBI:mysql:rt3:localhost';
my $db_user_name = 'rt_user';
my $db_password = 'rt_pass';
my ($id, $password);
my $dbh = DBI->connect($dsn, $db_user_name, $db_password);
my %alltotal;
my %allqueue;

while ( $stime < $oneyear ){
    $etime=$stime + $oneweek;
    $lastweek=strftime($template, localtime($stime)); 
    $thisweek=strftime($template, localtime($etime)); 
    open(FOO,">/tmp/report/$thisweek") || die "Can't open /tmp/report/$thisweek";
    print FOO "Report for $lastweek to $thisweek\n";
    print "Doing Report for $lastweek to $thisweek\n";
    
    $header="Incoming :";
    my $sth = $dbh->prepare(qq{
	SELECT count(*) FROM Tickets WHERE DATE_SUB(Created, INTERVAL 8 HOUR) BETWEEN \'$lastweek\' AND \'$thisweek\'
	});
    $sth->execute();
    while (my ($total) = $sth->fetchrow_array()){
	if ( $total == "" ){
	    print FOO "$header 0\n";
	}else{
	    print FOO "$header ",$total,"\n";
	}
    }
    $sth->finish();

#    SELECT count(*) FROM Tickets WHERE (Status='resolved' OR Status='deleted' ) AND DATE_SUB(Resolved, INTERVAL 8 HOUR) BETWEEN \'$lastweek\' AND \'$thisweek\'
    $header="Resolved :";
    my $sth = $dbh->prepare(qq{
	SELECT count(*) FROM Tickets WHERE Status='resolved' AND DATE_SUB(Resolved, INTERVAL 8 HOUR) BETWEEN \'$lastweek\' AND \'$thisweek\'
	});
    $sth->execute();
    while (my ($total) = $sth->fetchrow_array()){
	if ( $total == "" ){
	    print FOO "$header 0\n";
	}else{
	    print FOO "$header ",$total,"\n";
	}
    }
    $sth->finish();

#    SELECT count(*) FROM Tickets WHERE (Status='resolved' OR Status='deleted' ) AND DATE_SUB(Resolved, INTERVAL 8 HOUR) BETWEEN \'$lastweek\' AND \'$thisweek\'
    $header="Deleted :";
    my $sth = $dbh->prepare(qq{
	SELECT count(*) FROM Tickets WHERE Status='deleted' AND DATE_SUB(Resolved, INTERVAL 8 HOUR) BETWEEN \'$lastweek\' AND \'$thisweek\'
	});
    $sth->execute();
    while (my ($total) = $sth->fetchrow_array()){
	if ( $total == "" ){
	    print FOO "$header 0\n";
	}else{
	    print FOO "$header ",$total,"\n";
	}
    }
    $sth->finish();

    $header="Stalled :";
    my $sth = $dbh->prepare(qq{
	SELECT count(*) FROM Tickets WHERE Status='stalled' AND DATE_SUB(Resolved, INTERVAL 8 HOUR) BETWEEN \'$lastweek\' AND \'$thisweek\'
	});
    $sth->execute();
    while (my ($total) = $sth->fetchrow_array()){
	if ( $total == "" ){
	    print FOO "$header 0\n";
	}else{
	    print FOO "$header ",$total,"\n";
	}
    }
    $sth->finish();

#    SELECT count(*) FROM Tickets WHERE (Status='resolved' OR Status='deleted' ) AND DATE_SUB(Resolved, INTERVAL 8 HOUR) BETWEEN \'$lastweek\' AND \'$thisweek\'
#    SELECT id, Subject, Queue, Owner, Created, Creator FROM Tickets WHERE (Status='resloved' OR Status='deleted') \
#	AND DATE_SUB(Created, INTERVAL 8 HOUR) BETWEEN \'$thisweek\' AND '$begintime' 
#	AND DATE_SUB(Resolved, INTERVAL 8 HOUR) BETWEEN \'$thisweek\' AND '2006-12-31' 
#	;
# $header="Backlog :";
# my $sth = $dbh->prepare(qq{
#    SELECT count(*) FROM Tickets WHERE (Status='open' OR Status='new') \
# });
# $sth->execute();
# while (my ($id,$subject,$queue, $owner, $created, $creator) = $sth->fetchrow_array()){
#     print FOO "$header $id $subject $queue $owner $created $creator\n";
# }
# $sth->finish();

# $header="Backlog Detail :";
# my $sth = $dbh->prepare(qq{
#     SELECT id, Subject, Queue, Owner, Created, Creator FROM Tickets WHERE (Status='open' OR Status='new') \
# });
# $sth->execute();
# while (my ($id,$subject,$queue, $owner, $created, $creator) = $sth->fetchrow_array()){
#     print FOO "$header $id $subject $queue $owner $created $creator\n";
# }
# $sth->finish();

    $header="Backlog:";
#    SELECT id, Subject, Queue, Owner, Created, Creator FROM Tickets WHERE 
#	AND DATE_SUB(Resolved, INTERVAL 8 HOUR) BETWEEN \'$thisweek\' AND '2006-12-31' 
    my $sth = $dbh->prepare(qq{
#	SELECT count(*) FROM Tickets WHERE 
#	    DATE_SUB(Created, INTERVAL 8 HOUR) BETWEEN  \'$begintime\' AND \'$thisweek\'
#	    AND ((Status='open' OR Status='new') OR NOT
#		 ((Status='deleted' OR Status='resolved') AND 
#		  (DATE_SUB(Resolved, INTERVAL 8 HOUR) BETWEEN  \'$begintime\' AND \'$lastweek\' OR
#		   (DATE_SUB(Resolved, INTERVAL 8 HOUR) BETWEEN  \'$thisweek\' AND \'$today\'))))
#	    ;
	SELECT count(*) FROM Tickets t, Users u, Users r WHERE 
	    t.Owner = u.id AND
	    t.Creator = r.id AND
	    DATE_SUB(t.Created, INTERVAL 8 HOUR) BETWEEN  \'$begintime\' AND \'$thisweek\'
	    AND ((t.Status='open' OR t.Status='new') OR NOT
		 ((t.Status='deleted' OR t.Status='resolved') AND 
		  (DATE_SUB(t.Resolved, INTERVAL 8 HOUR) BETWEEN  \'$begintime\' AND \'$lastweek\' OR
		   (DATE_SUB(t.Resolved, INTERVAL 8 HOUR) BETWEEN  \'$thisweek\' AND \'2006-12-31\'))))
	    ;

    });
    $sth->execute();
    while (my ($total) = $sth->fetchrow_array()){
	if ( $total == "" ){
	    print FOO "$header 0\n";
	}else{
	    print FOO "$header ",$total,"\n";
	}
    }
    $sth->finish();
#    while (my ($id,$subject,$queue, $owner, $created, $creator) = $sth->fetchrow_array()){
#	print FOO "$header $id $subject $queue $owner $created $creator\n";
#    }
#    $sth->finish();

    $header="";
    my $sth = $dbh->prepare(qq{
	SELECT t.id, t.Subject, u.Name, t.Created, r.name FROM Tickets t, Users u, Users r WHERE 
	    t.Owner = u.id AND
	    t.Creator = r.id AND
	    DATE_SUB(t.Created, INTERVAL 8 HOUR) BETWEEN  \'$begintime\' AND \'$thisweek\'
	    AND ((t.Status='open' OR t.Status='new') OR NOT
		 ((t.Status='deleted' OR t.Status='resolved') AND 
		  (DATE_SUB(t.Resolved, INTERVAL 8 HOUR) BETWEEN  \'$begintime\' AND \'$lastweek\' OR
		   (DATE_SUB(t.Resolved, INTERVAL 8 HOUR) BETWEEN  \'$thisweek\' AND \'2006-12-31\'))))
	    ;
    });
    $sth->execute();
    $mycount=1;
    while (my ($id,$subject, $owner, $created, $creator) = $sth->fetchrow_array()){
	$ptime= parsedate($created, FUZZY => 1);
	$fcreated = strftime("%m/%d/%Y",localtime($ptime));
#    printf "Ticket#: $id\nSubject: $subject\nCreator: $creator\nDate Opened: $created\nDays in Queue: %d\nOwner: $owner\n",(($etime - $ptime) / 60 / 60 / 24);
	printf FOO "$mycount,$id,\"$subject\",$creator,$fcreated,%d,$owner\n",(($etime - $ptime) / 60 / 60 / 24);
	$mycount++;
    }
    $sth->finish();

    close(FOO);

    $stime += $oneweek;
}

$dbh->disconnect();

