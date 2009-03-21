#!/usr/bin/perl

use Time::ParseDate;
use Time::CTime;

$year=2006;
$oneday=(60 * 60 * 24);
$template="%Y-%m-%d";
$mend=13;

$month=1;
while ( $month < $mend ){
    if ( $month < 10 ){
	$mtxt="0$month";
    }else{
	$mtxt=$month;
    }
    $nextmonth=$month + 1;
    if ( $nextmonth < 10 ){
	$ntxt="0$nextmonth";
    }else{
	$ntxt=$nextmonth;
    }
    $stime=parsedate("$year-$mtxt-01");
    $begintime=strftime($template, localtime($stime));
    $etime=parsedate("$year-$ntxt-01");
    $etime=$etime-$oneday;
    $endtime=strftime($template, localtime($etime));
    print "./monthlyreport-args ";
    print $begintime," ";
    print $endtime,"\n";
#    print $endtime," > monthlies/$endtime\n";

    $month++;
}




