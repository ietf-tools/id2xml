#!/usr/local/bin/perl -w

use lib '/export/home/mlee/RELEASE/';
use IETF_UTIL;

if (defined($ARGV[0])) {
   $input_file2 = $ARGV[0];
} else {
   print qq{
   USAGE: format <unformatted last_call file without extension ".lastcall">

};
   exit(2);
}
my @temp = split '\.', $input_file2;
my $type = $temp[1];
$input_file = $temp[0];
my $ext;
if ($type eq "lastcall") {
   $ext = "last_call";
} elsif ($type eq "ballot") {
   $ext = "rec";
} else {
   $ext = "formatted";
}

unless (-e $input_file2) {
   die "FATAL ERROR: File does not exist\n";
}

open (INFILE,$input_file2);
open (OUTFILE,">${input_file}.${ext}");
my $line_count = 0;
while ($line = <INFILE>) {
   chomp($line);
   $line_count++;
   $line = rm_tr($line);
   $line = format_line($line,$line_count);
 
 
   if (/The IESG contact person/) {
      my $next_line = <INFILE>;
	  chomp($line);
	  $line .= " ";
	  while (1) {
  	     chomp($next_line);
		 my $next_line_formatted = rm_tr($next_line);
		 $next_line = <INFILE>;
		 if (length($next_line) > 3) {
		     $line .= rm_hd($next_line_formatted) . ", ";
		 } else {
		     $line .= rm_hd($next_line_formatted);
			 last;
		 }
      }
	  $line .= "\n";
   }


   print OUTFILE "$line";
}
close (OUTFILE);
close(INFILE);
exit(1);

sub format_line {
   my $line = shift;
   my $line_count = shift;
   my $new_line = "";
   $_ = $line;
   my $space = "";
   if (/Subject:/ or /SUBJECT:/) {
      $space = "         ";
   };
   if ($line_count == 1 and length($line) == 0) {
      return "";
   }
   while (length($line) > 75) {
      $pos = 75;
	  $chr = "temp";
	  my $extra_long = 0;
	  while ($chr ne " " and $extra_long == 0) {
	     $pos--;
		 unless ($pos < 0) {
		    $chr = substr($line,$pos,1);
	     } else {
		    $extra_long = 1;
			last;
		 }
	  }
	  my $eol = 0;
	  if ($extra_long == 1) {
         $pos = 75;
   	     $chr = "temp";
	     while ($chr ne " " and $eol == 0) {
	        $pos++;
			if ($pos == length($line)) {
			   $eol = 1;
			   last;
			} else {
			   $chr = substr($line,$pos,1);
			}
	     }
	  }
	  unless ($eol == 1) {
         $new_line .= substr($line,0,$pos+1);
	     $line = "\n${space}" . substr($line,$pos+1);
	  } else {
	     $new_line .= $line;
		 $line = "\n${space}";
	  }
   }
   $new_line .= "$line\n";
   return $new_line;
}
