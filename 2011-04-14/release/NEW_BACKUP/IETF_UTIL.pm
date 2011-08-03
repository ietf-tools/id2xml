package IETF_UTIL;
 
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(rm_tr rm_hd my_defined convert_date get_current_date get_current_time clear_screen format_textarea unformat_textarea indent_text indent_text2 validate_date reduce_text add_spaces numtocheck checktonum);

sub rm_tr {
   #$_ = shift;
   #return "" unless my_defined($_);
   #chop if (/\r$/);
   #s/\s+$//;
   #return $_;
   my @list = @_;
   for (my $loop=0;$loop<=$#list;$loop++) {
      $_ = $list[$loop];
      unless (my_defined($_)) {
         $list[$loop] = "";
         next;
      }
      chop if (/\r$/);
      s/\s+$//;
      $list[$loop] = $_;
   }
   if ($#list == 0) {
     return $list[0];
   } else {
     return @list;
   }


}

sub rm_hd {
   $_ = shift;
   return "" unless my_defined($_);
   s/^\s+//;
   return $_;
}


sub my_defined {
   $_ = shift;
   return 0 unless defined;
   return 1 if (/.\w./);
   return 0 if (/^\s/);
   return 0 if (length == 0);
   return 1;
}

sub convert_date {
   $dateStr = shift;
   $option = shift;
   my %months_h = (
   '01' => 'JAN',
   '02' => 'FEB',
   '03' => 'MAR',
   '04' => 'APR',
   '05' => 'MAY',
   '06' => 'JUN',
   '07' => 'JUL',
   '08' => 'AUG',
   '09' => 'SEP',
   '1' => 'JAN',
   '2' => 'FEB',
   '3' => 'MAR',
   '4' => 'APR',
   '5' => 'MAY',
   '6' => 'JUN',
   '7' => 'JUL',
   '8' => 'AUG',
   '9' => 'SEP',
   '10' => 'OCT',
   '11' => 'NOV',
   '12' => 'DEC'
   );
   $_ = $dateStr;
   return "" unless (my_defined($_));
   return "" if ($_ eq "00/00/0000" or $_ eq "0000-00-00");
   if (/\//) {
      @str = split '/',$dateStr;
   } else {
      @str = split '-',$dateStr;
   }
   $dayStr = $str[1];
   if (substr($dayStr,0,1) eq "0") {
      $dayStr = substr($dayStr,1,1);
   }
   $yearStr = $str[2];
   if (length($yearStr) > 2) {
      $yearStr = substr($yearStr,2,2);
   }
   if (defined($option) and $option == 1) { ## convert MM/DD/YYYY to YYYY-MM-DD ##
      
      return $_ if (/-/);
      $dateStr = "$str[2]-$str[0]-$str[1]";
   } 
   elsif (defined($option) and $option == 2) { ## convert YYYY-MM-DDto MM/DD/YYYY ##
      return $_ if (/\//);
      $dateStr = "$str[1]/$str[2]/$str[0]";
   } 
   elsif (defined($option) and $option == 3) { ## convert to MMM YY ##
      $dateStr = "$months_h{$str[0]} $yearStr";
   }
   elsif (defined($option) and $option == 4) { ## convert to DD-MMM-YY ##
      $dateStr = "$str[1]-$months_h{$str[0]}-$yearStr";
   }
   else { 								## convert to MMM DD ##
      $dateStr = "$months_h{$str[0]} $dayStr";
   }
   return $dateStr;
}

sub get_current_date {
   my $option = shift;
   my $interval= shift;
   unless (defined($interval)) {
      $interval = 0;
   }
   $interval = $interval * 3600 * 24;
   my $dateStr;
   my %months_h = (
   1 => 'January',
   2 => 'February',
   3 => 'March',
   4 => 'April',
   5 => 'May',
   6 => 'June',
   7 => 'July',
   8 => 'August',
   9 => 'September',
   10 => 'October',
   11 => 'November',
   12 => 'December'
   );
   @dates = localtime(time+$interval);
   $local_day = $dates[3];
   $local_month = $dates[4] + 1;
   $local_year = $dates[5] + 1900;
   if (defined($option) and $option == 1) {
      $dateStr = "${local_month}/${local_day}/${local_year}";
   } else {
      $dateStr = "$months_h{$local_month} $local_day, $local_year";
   }
   return $dateStr;
}

sub get_current_time {
   my $dateStr;
   my @dates = localtime(time);
   
   $second = $dates[0];
   $minute = $dates[1];
   $hour = $dates[2];
   $dateStr = "${hour}:${minute}:${second}";
   return $dateStr;
}

sub clear_screen {
    system "clear";
    print "\n\n\n";
}

sub format_textarea {
   my $textarea = shift;
   $_ = $textarea;
   s/</&lt;/g;
   s/>/&gt;/g;
   s/&lt;b&gt;/<b>/g;
   s/&lt;\/b&gt;/<\/b>/g;
   s/&lt;br&gt;/<br>/g;

  
   s/\r//g;
   s/\n/<br>/g;
   #s/\s\s+/ /g;
   s/  /&nbsp; /g;
   $textarea = $_;
 
   return $textarea;
}

sub unformat_textarea {
   my $comment = shift;
   $_ = $comment;
   s/<br>/\n/g;
   s/\s\s+/ /g;
   #s/'/''/g;
   s/<b>//g;
   s/<\/b>//g;
   return $_;
}


sub indent_text {
   my $text = shift;
   my $indent_number = shift;
   my $spaces = "";
   for (my $loop=0;$loop<$indent_number;$loop++) {
      $spaces .= " ";
   }
   $text =~ s/\n/ /g;
   $text =~ s/\r//g;
   my @str = split ' ',$text;
   my $ret_val = "";
   my $one_line = $spaces;
   for ($loop=0;$loop<=$#str;$loop++) {
      unless ((length($one_line)+length($str[$loop])) <= 75) {
         $ret_val .= "$one_line\n";
         $one_line = $spaces;
      }
      $one_line .= "$str[$loop] ";
   }
   $ret_val .= "$one_line";
   return $ret_val;
}

sub indent_text2 {
   my $text = shift;
   my $indent_number = shift;
   my $spaces = "";
   for (my $loop=0;$loop<$indent_number;$loop++) {
      $spaces .= " ";
   }
   $text =~ s/\n/ /g;
   $text =~ s/\r//g;
   my @str = split ' ',$text;
   my $ret_val = "";
   my $one_line = "";
   my $line_num = 0;
   for ($loop=0;$loop<=$#str;$loop++) {
      my $extra = 0;
      $extra = $indent_number if ($line_num == 0);
      unless ((length($one_line)+length($str[$loop])+$extra) <= 75) {
         $ret_val .= "$one_line\n";
         $one_line = $spaces;
         $line_num++;
      }
      $one_line .= "$str[$loop] ";
   }
   $ret_val .= "$one_line";
   return $ret_val;
}


sub validate_date {
  my $date = shift;
  return 1 unless (my_defined($date));
  return 0 unless ($date =~ /\d\d\d\d-\d+-\d+/);
  return 1;
  my ($year,$month,$day) = split '-',$date;
  my @dates = localtime(time);
  my $local_year = $dates[5] + 1900;
  return 0 if ($year < $local_year or $year > ($local_year+2));
  return 0 if ($month > 12);
  return 0 if ($day > 31);
  return 1;
}

sub reduce_text {
  my $text = shift;
  my $len = shift;
  my @temp = split '<br>', $text;
  if ($#temp > $len) {
    my @temp2;
    for (my $loop=0;$loop<$len;$loop++) {
      $temp2[$loop] = $temp[$loop];
    }
    $text = join '<br>', @temp2;
    $text .= "<br>\n\n<b>and more ...</b>";
  }
  return $text;
}

sub add_spaces {
  my $word = shift;
  my $target_size = shift;
  my $cur_length = length($word);
  my $space_num = $target_size - $cur_length;
  my $ret_val = $word;
  for ($loop = 0;$loop<$space_num;$loop++) {
    $ret_val .= " ";
  }
  return $ret_val;
}

sub numtocheck {
  my $num = shift;
  my $ret_val = "";
  $ret_val = "checked" if ($num);
  return $ret_val;
}

sub checktonum {
  my $checked =shift;
  my $ret_val = 0;
  $ret_val = 1 if (lc($checked) eq "on");
  return $ret_val;
}

