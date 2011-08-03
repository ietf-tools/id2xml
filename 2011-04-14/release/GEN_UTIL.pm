##########################################################################
# Copyright © 2004 and 2002, Foretec Seminars, Inc.
##########################################################################

package GEN_UTIL;

require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(rm_tr rm_hd my_defined convert_date get_current_date get_current_time clear_screen text_to_html unformat_textarea indent_text indent_text2 validate_date reduce_text reduce_text_plain add_spaces numtocheck checktonum full_status_value get_date_select_html array_diff y_two_k format_textarea format_comment_text format_comment_text_test send_mail get_line_count gen_random is_valid_email is_valid_phone is_valid_url is_valid_email_b mail_log format_date get_verbal_number get_number_ordered remove_dq restore_dq html_bracket de_html_bracket html_dq de_html_dq parse_email_list get_time_stamp make_one_per_line my_crypt check_sql_injection generate_random_string fileuploader);

use POSIX; 

sub fileuploader {
   my $upload_filehandle=shift;
   my $upload_path=shift;
   open (UPLOADFILE, ">$upload_path") || return 0;

   binmode UPLOADFILE;

   while( <$upload_filehandle>)
   {
      print UPLOADFILE;
   }

   close UPLOADFILE;
   return 1;
}

############################################################
# Function Name: generate_random_string
# Function Description: Generates 32 length of random string
# Input Parameters: 
#   param1: None
# Output: 32 length of string 
# Commented by: Shailendra Singh
# Commented date: 2/15/07
############################################################

sub generate_random_string
{
   my $length_of_randomstring=shift; # the length of the random string to generate
 
   my @chars=('a'..'z','A'..'Z','0'..'9');
     my $random_string;
     foreach (1..$length_of_randomstring)
     {
          $random_string.=$chars[rand @chars];
     }
     return $random_string;
}

$FORMAT_LINE = 80;
$INDENT_LINE = $FORMAT_LINE - 1;
$LOG_PATH = "/a/www/ietf-datatracker/logs";

sub check_sql_injection {
  my @args=@_;
  for my $array_ref (@args) {
    return 1 if ($array_ref=~/\/|\;|\||\*|\s|\&|\$/);
  }
  return 0;
}

sub my_crypt {
  my $text=shift;
  return crypt($text,"dd");
}

sub make_one_per_line {
  my $val=shift;
#  $val =~ s/ //g;
  $val =~ s/,/\n/g;
  $val =~ s/\n /\n/g;
  $val =~ s/ahref/a href/g;
  return $val;
}

sub get_time_stamp {
  my $date =shift;
  my @date = split '-',$date;
  my $year = $date[0] - 1900;
  my $mon = $date[1] - 1;
  my $day = $date[2];
  my $wday = 0;
  return mktime(0,0,0,$day,$mon,$year,$wday,0,-1);
}

sub parse_email_list {
  my $contact_text = shift;
  my @fields = split /,/, $contact_text;
  my $ret_val="";
  for my $array_ref (@fields) {
    $array_ref =~ s/"//g;
    $array_ref =~ s/<//g;
    $array_ref =~ s/>//g;
    my @sub_fields = split ' ',$array_ref;
    my $each_item = "";
    my $email_address = "";
    for my $array_ref_sub (@sub_fields) {
      if ($array_ref_sub =~ /@/) {
        $each_item = "$array_ref_sub " unless my_defined($each_item);
        $email_address = $array_ref_sub;
      } else {
        $each_item .= "$array_ref_sub ";
      }
    }
    chop($each_item);
    $ret_val .= "<a href=\"mailto:$email_address\">$each_item</a>,";
  }
  chop($ret_val);
  return $ret_val;
}

sub html_dq {
  my @list = @_;
  for ($loop=0;$loop<=$#list;$loop++) {
    $list[$loop] =~ s/"/&#34;/g;
  }
   if ($#list == 0) {
     return $list[0];
   } else {
     return @list;
   }

}

sub de_html_dq {
  my @list = @_;
  for ($loop=0;$loop<=$#list;$loop++) {
    $list[$loop] =~ s/&#34;/"/g;
  }
   if ($#list == 0) {
     return $list[0];
   } else {
     return @list;
   }
}

sub de_html_bracket {
  my @list = @_;
  for ($loop=0;$loop<=$#list;$loop++) {
    $list[$loop] =~ s/&lt;/</g;
    $list[$loop] =~ s/&gt;/>/g;
  }
   if ($#list == 0) {
     return $list[0];
   } else {
     return @list;
   }
}


sub html_bracket {
  my @list = @_;
  for ($loop=0;$loop<=$#list;$loop++) {
    $list[$loop] =~ s/</&lt;/g;
    $list[$loop] =~ s/>/&gt;/g;
  }
   if ($#list == 0) {
     return $list[0];
   } else {
     return @list;
   }
}

sub remove_dq {
  my $text = shift;
  $text =~ s/"/^/g;
  return $text;
}

sub restore_dq {
  my $text=shift;
  $text =~ s/\^/"/g;
  return $text;
}
sub get_number_ordered {
  my $number=shift;
  if ($number > 10 and $number < 14) {
    return "${number}th";
  }
  my $last_digit_position=length($number)-1;
  my $last_digit=substr($number,$last_digit_position,1);
  if ($last_digit == 1) {
    return "${number}st";
  } elsif ($last_digit == 2) {
    return "${number}nd";
  } elsif ($last_digit == 3) {
    return "${number}rd";
  } else {
    return "${number}th";
  }
  return "UNKNOWN";
}
sub get_verbal_number {
  my $number=shift;
  my $to_digit=shift;
  if (defined($to_digit)) {
    my $factor= substr($number,length($number)-1,1);
    if ($factor eq "1") {
      return "${number}st";
    } elsif ($factor eq "2") {
      return "${number}nd";
    } elsif ($factor eq "3") {
      return "${number}rd";
    } else {
      return "${number}th";
    }
  }
  my $verbal_number="";
  if ($number == 100) {
    return "ONE HUNDREDTH";
  } elsif ($number > 100) {
    $verbal_number = "ONE HUNDRED ";
    $number = $number % 100;
  }
  if ($number < 20 and $number > 9) {
    my $ret_val = "";
    if ($number == 11) {
      $ret_val = "ELEVENTH";
    } elsif ($number == 12) {
      $ret_val = "TWELVTH";
    } elsif ($number == 13) {
      $ret_val = "THIRTEENTH";
    } elsif ($number == 14) {
      $ret_val = "FOURTEENTH";
    } elsif ($number == 15) {
      $ret_val="FIFTEENTH";
    } elsif ($number == 16) {
      $ret_val = "SIXTEENTH";
    } elsif ($number == 17) {
      $ret_val="SEVENTEENTH";
    } elsif ($number == 18) {
      $ret_val="EIGHTEENTH";
    } elsif ($number == 19) {
      $ret_val="NINTEENTH";
    } elsif ($number == 10) {
      $ret_val="TENTH";
    }
    return $verbal_number.$ret_val;
  }
  if ($number >= 90 ) {
    $verbal_number .= "NINET";
  } elsif ($number >= 80) {
    $verbal_number .= "EIGHT";
  } elsif ($number >= 70) {
    $verbal_number .= "SEVENT";
  } elsif ($number >= 60) {
    $verbal_number .= "SIXT";
  } elsif ($number >= 50) {
    $verbal_number .= "FIFT";
  } elsif ($number >= 40) {
    $verbal_number .= "FOURT";
  } elsif ($number >= 30) {
    $verbal_number .= "THIRT";
  } elsif ($number >= 20) {
    $verbal_number .= "TWENT";
  }
  my $prefix = ($number > 10)?"Y-":"";
  my $second_digit = $number % 10;
  if ($second_digit == 0) {
    $verbal_number .= "IETH";
  } elsif ($second_digit == 1) {
    $verbal_number .= "${prefix}FIRST";
  } elsif ($second_digit == 2) {
    $verbal_number .= "${prefix}SECOND";
  } elsif ($second_digit == 3) {
    $verbal_number .= "${prefix}THIRD";
  } elsif ($second_digit == 4) {
    $verbal_number .= "${prefix}FOURTH";
  } elsif ($second_digit == 5) {
    $verbal_number .= "${prefix}FIFTH";
  } elsif ($second_digit == 6) {
    $verbal_number .= "${prefix}SIXTH";
  } elsif ($second_digit == 7) {
    $verbal_number .= "${prefix}SEVENTH";
  } elsif ($second_digit == 8) {
    $verbal_number .= "${prefix}EIGHTH";
  } elsif ($second_digit == 9) {
    $verbal_number .= "${prefix}NINTH";
  }
  return $verbal_number;
}

                                                                                         
sub mail_log {
  my $program_name=shift;
  my $subject=shift;
  my $to=shift;
  my $sender=shift;
  $sender = "SYSTEM" unless my_defined($sender);
  my $c_time = get_current_time();
  my $c_date = get_current_date();
  if ($subject =~ /Subject:/) {
    $_ = $subject;
    /Subject:\s+(.*)\n/;
    $subject = $1;
  }
  if ($to =~ /To:/) {
    $_ = $to;
    /To:\s+(.*)\n/;
    $to=$1;
  }
  open LOG,">>$LOG_PATH/mail.log";
  print LOG "[$c_time, $c_date]$program_name|$subject|$to|$sender\n";
  close LOG;
}

sub is_valid_url {
  my $url = shift;
  return 1 if ($url =~ /(\S+)\.(\S+)/);
  return 0;
}

sub is_valid_email {
  my $email = shift;
  $email =~ s/,/\n/g;
  my @emails = split '\n',$email;
  for my $each_email (@emails) {
    return 0 unless ($each_email =~ /(\S+)@(\S+)\.(\S+)/);
  }
  return 1;
}

sub is_valid_email_b {
  my $email = shift;
  return 1 if ($email =~ /<(\S+)@(\S+)\.(\S+)>/);
  return -1 if ($email =~ /(\S+)@(\S+)\.(\S+)/);
  return 0;
}

sub is_valid_phone {
  my $var = shift;
  chomp($var);
  $var =~ s/\d//g;
  $var =~ s/\+//g;
  $var =~ s/\(//g;
  $var =~ s/\)//g;
  $var =~ s/x//g;
  $var =~ s/X//g;
  $var =~ s/\-//g;
  $var =~ s/\.//g;
  $var =~ s/ //g;
  return 0 if (length($var));
  return 1;
}
 
sub get_line_count {
  my $text = shift;
  my @temp = split '\n', $text;
  return $#temp;
}

sub gen_random {
  my $rand_num = rand 21;
  $rand_num =~ s/\./A/g;
  $rand_num =~ s/3/z/g;
  $rand_num =~ s/5/q/g;
  $rand_num =~ s/1/b/;
  $rand_num =~ s/7/p/;
  return $rand_num;
  return $random;
}

sub send_mail {
  my ($program_name,$user_name,$to,$from,$subject,$body,$cc,$extra,$content_type) = @_;
  my $dateStr = get_current_date();
  my $timeStr = get_current_time();
  $content_type = "text/plain; charset=\"utf-8\"" unless my_defined($content_type);
  my $email_addresses = "";
  $subject = indent_text2($subject,9,73);
  my $tempto = $to;
  if ($to eq "IETF ANNOUNCEMENT") {
    $tempto = "ietf-announce\@ietf.org";
  }
  my $tempcc = $cc;
  my $extra_header = "";
  $extra = $tempcc if ($tempcc =~ /=/);
  if (my_defined($extra)) {
    my @temp1 = split '\^', $extra;
    $extra_header ="\n";
    for my $array_ref (@temp1) {
      $extra_header .= "$array_ref\n";
      my $tempto = $array_ref;
      $tempto =~ s/,/ /g;
      $tempto =~ s/;/ /g;
      $tempto =~ s/"//g;
      $tempto =~ s/<//g;
      $tempto =~ s/>//g;
      my @temp = split ' ', $tempto;
      for my $array_ref2 (@temp) {
        $email_addresses .= "$array_ref2 " if ($array_ref2 =~ /\@/);
      }
    }
    chomp($extra_header);
  }
  $tempto =~ s/,/ /g;
  $tempto =~ s/;/ /g;
  $tempto =~ s/"//g;
  $tempto =~ s/<//g;
  $tempto =~ s/>//g;
  $tempcc =~ s/,/ /g;
  $tempcc =~ s/;/ /g;
  $tempcc =~ s/"//g;
  $tempcc =~ s/<//g;
  $tempcc =~ s/>//g;

  my @temp = split ' ', $tempto;
  my @temp2 = split ' ',$tempcc;
  for $array_ref (@temp) {
    $email_addresses .= "$array_ref " if ($array_ref =~ /@/);
  }
  for $array_ref (@temp2) {
    $email_addresses .= "$array_ref " if ($array_ref =~ /@/);
  }
  $body =~ s/\r//g;
  #$email_addresses  =~ /^([a-zA-Z0-9\._\@]+)$/ and return 0;
  open MAIL, "| /usr/sbin/sendmail $email_addresses" or return 0; 
  print MAIL <<END_OF_MESSAGE;
From: $from
To: $to
END_OF_MESSAGE
   if (length($cc) > 2) { print MAIL "Cc: $cc\n"; }
  print MAIL <<END_OF_MESSAGE;
Subject: $subject$extra_header
Content-Type: $content_type
Mime-Version: 1.0

$body
END_OF_MESSAGE
  close MAIL or return 0;
  mail_log($program_name,$subject,$email_addresses,$user_name);
  return 1;
}

sub format_textarea {
   my $textarea = shift;
   $_ = $textarea;
   s/&/&amp;/g;
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

sub y_two_k {
   my $ret_val = shift;
   return "" unless (my_defined($ret_val));
   $_ = $ret_val;
   if (/\//) {
      my @temp = split '\/';
          if ($temp[2] < 50) {
                 $temp[2] = 2000 + $temp[2];
          }
          $ret_val = join '/', @temp;
   } else {
      my @temp = split '-';
          if ($temp[0] < 50) {
             $temp[0] = $temp[0] + 2000;
          }
          $ret_val = join '-', @temp;
   }
   return $ret_val;
}

#################
# returns values from first array that do not exist in the second array
################
sub array_diff {
  my $first_array = shift;
  my $second_array = shift;
  my @first_array = @$first_array;
  my @second_array = @$second_array;
  my @ret_val;
  for $first_array_ref (@first_array) {
    my $found = 0;
    for $second_array_ref (@second_array) {
      $found = 1 if ($second_array_ref == $first_array_ref);
    }
    push @ret_val,$first_array_ref unless ($found);
  }
  return @ret_val;
}


sub get_date_select_html {
  my $field_name = shift;
  my $selected_date = shift;
  my $default_year = shift;
  my $selected_year = 0;
  my $selected_month = 0;
  my $selected_day = 0;
  ($selected_year,$selected_month,$selected_day) = split '-',$selected_date if (defined($selected_date));
  my @months = ("January","February","March","April","May","June","July","August","September","October","November","December");
  my $month_select = "<select name=\"${field_name}_month\"><option value=\"0\">-MONTH-</option>\n";
  my $selected = "";
  for ($loop=0;$loop<12;$loop++) {
    my $month_val = $loop+1;
    $selected = "";
    $selected = "selected" if ($month_val==$selected_months);
    $month_select .= "<option value=\"$month_val\" $selected>$months[$loop]</option>\n";
  }
  $month_select .= "</select>\n";
   my @dates = localtime(time+$interval);
   my $current_year = $dates[5] + 1900;

  my $year_select = "<select name=\"${field_name}_year\"><option value=\"0\">-YEAR-</option>\n";
  unless (defined($default_year)) {
    for ($loop=0;$loop<5;$loop++) {
      $selected = "";
      $selected = "selected" if ($current_year == $selected_year);
      $year_select .= "<option value=\"$current_year\" $selected>$current_year</option>\n";
      $current_year++;
    }
  } else {
    for ($loop=0;$loop<$default_year;$loop++) {
      $year_select .= "<option value=\"$current_year\">$current_year</option>\n";
      $current_year--;
    }

  }
  $year_select .= "</select>\n";
  my $day_select = "<select name=\"${field_name}_day\"><option value=\"0\">-DAY-</option>\n";
  for ($loop=1;$loop<32;$loop++) {
    $selected = "";
    $selected = "selected" if ($loop == $selected_day);
    $day_select .= "<option value=\"$loop\" $selected>$loop</option>\n";
  }
  $day_select .= "</select>\n";
  return "$month_select$day_select$year_select";
}

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
   '01' => 'Jan',
   '02' => 'Feb',
   '03' => 'Mar',
   '04' => 'Apr',
   '05' => 'May',
   '06' => 'Jun',
   '07' => 'Jul',
   '08' => 'Aug',
   '09' => 'Sep',
   '1' => 'Jan',
   '2' => 'Feb',
   '3' => 'Mar',
   '4' => 'Apr',
   '5' => 'May',
   '6' => 'Jun',
   '7' => 'Jul',
   '8' => 'Aug',
   '9' => 'Sep',
   '10' => 'Oct',
   '11' => 'Nov',
   '12' => 'Dec'
   );
   my %months_h3 = (
   'Jan' => '01',
   'Feb' => '02',
   'Mar' => '03',
   'Apr' => '04',
   'May' => '05',
   'Jun' => '06',
   'Jul' => '07',
   'Aug' => '08',
   'Sep' => '09',
   'Oct' => '10',
   'Nov' => '11',
   'Dec' => '12'
   );

   my %months_h2 = (
   '01' => 'January',
   '02' => 'February',
   '03' => 'March',
   '04' => 'April',
   '05' => 'May',
   '06' => 'June',
   '07' => 'July',
   '08' => 'August',
   '09' => 'September',
   '1' => 'January',
   '2' => 'February',
   '3' => 'March',
   '4' => 'April',
   '5' => 'May',
   '6' => 'June',
   '7' => 'July',
   '8' => 'August',
   '9' => 'September',
   '10' => 'October',
   '11' => 'November',
   '12' => 'December'
   );

   $_ = $dateStr;
   return "" unless (my_defined($_));
   return "" if ($_ eq "00/00/0000" or $_ eq "0000-00-00");
   if (/\//) {
      @str = split '/',$dateStr;
      $dayStr = $str[1];
      $yearStr = $str[2];
      $monthStr = $str[0];
   } else {
      @str = split '-',$dateStr;
      $dayStr = $str[2];
      $yearStr = $str[0];
      $monthStr = $str[1];
   }
   if (substr($dayStr,0,1) eq "0") {
      $dayStr = substr($dayStr,1,1);
   }
   if (length($yearStr) > 2) {
      $yearStr_short = substr($yearStr,2,2);
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
      $dateStr = "$months_h{$monthStr} $yearStr";
   }
   elsif (defined($option) and $option == 4) { ## convert to DD-MMM-YY ##
      $dateStr = "$dayStr-$months_h{$monthStr}-$yearStr_short";
   }
   elsif (defined($option) and $option == 5) { ## convert to MMMM DD, YYYY ##
      $dateStr = "$months_h2{$monthStr} $dayStr, $yearStr";
   }
   elsif (defined($option) and $option == 6) { ## convert to MMMM YYYY ##
      $dateStr = "$months_h2{$monthStr} $yearStr";
   }
   elsif (defined($option) and $option == 7) { ## convert DD/MMM/YYYY to YYYY-MM-DD
     $dayStr = $str[0];
     $monthStr = $str[1];
     $dateStr = "$yearStr-$months_h3{$monthStr}-$dayStr";
   }
   else { 				## convert to MMM DD ##
      $dateStr = "$months_h{$monthStr} $dayStr";
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

sub format_date {
   my $date = shift;
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
   @dates = split '-',$date;
   $local_day = $dates[2];
   $local_month = $dates[1];
   $local_month =~ s/^0//;
   $local_day =~ s/^0//;
   $local_year = $dates[0];
   $dateStr = "$months_h{$local_month} $local_day, $local_year";
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

sub text_to_html {
   my $textarea = shift;
   $_ = $textarea;
   s/&/&amp;/g;
   s/</&lt;/g;
   s/>/&gt;/g;
   s/&lt;b&gt;/<b>/g;
   s/&lt;\/b&gt;/<\/b>/g;
   s/&lt;br&gt;/<br>/g;

  
   s/\r//g;
   s/\n/<br>\n/g;
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
   #$text =~ s/\n/ /g;
   #$text =~ s/\r//g;
   my @str = split ' ',$text;
   my $ret_val = "";
   my $one_line = $spaces;
   for ($loop=0;$loop<=$#str;$loop++) {
      unless ((length($one_line)+length($str[$loop])) <= $INDENT_LINE) {
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
   my $new_position=shift;
   $INDENT_LINE = $new_position if defined($new_position);

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
      unless ((length($one_line)+length($str[$loop])+$extra) <= $INDENT_LINE) {
         $ret_val .= "$one_line\n";
         $one_line = $spaces;
         $line_num++;
      }
      $one_line .= "$str[$loop] ";
   }
   $ret_val .= "$one_line";
   return $ret_val;
}
sub format_comment_text_test {
  my $comment_text = shift;
  my $new_position=shift;
  $FORMAT_LINE = $new_position if defined($new_position);
  my $ret_val = "";
  $comment_text =~ s/\r//g;
  my $num_space=0;
  for ($loop=0;$loop<$FORMAT_LINE;$loop++) {
    my $cur_char = substr($comment_text,$loop,1);
    $num_space++ if ($cur_char eq " ");
    if ($cur_char eq "\n") { #CR detected
      $ret_val .= substr($comment_text,0,$loop+1);
      $comment_text = substr($comment_text,$loop+1);
      #$comment_text =~ s/^(\s)(\S.*)/$2/g;
      #$ret_val =~ s/\s\n$/\n/g;
      $loop = 0;
      $num_space=0;
      next;
    } elsif ($loop == $FORMAT_LINE-1) { #pointer is in the 80the position
      my $next_char=substr($comment_text,$FORMAT_LINE,1);
      if ($cur_char =~ /\S/ and $next_char =~/\S/) { #80th character is within a word
        if ($num_space) {
          while ($cur_char =~ /\S/) {
            $loop--;
            $cur_char = substr($comment_text,$loop,1);
            last unless ($loop);
          }
        } else {  #a word longer than 80
          while ($cur_char =~ /\S/) {
            $loop++;
            $cur_char = substr($comment_text,$loop,1);
            last if (length($comment_text) <= $loop);
          }
        }
                                                                                
        $ret_val .= substr($comment_text,0,$loop+1);
        $ret_val .= "\n";
        $comment_text = substr($comment_text,$loop+1);
                                                                                
        $comment_text =~ s/^(\s)(\S.*)/$2/g;
        $ret_val =~ s/\s\n$/\n/g;
        $loop = 0;
        next;
#      } elsif ($cur_char =~ /\S/ and $next_char =~/\s/) { # next character is space
#        $ret_val .= substr($comment_text,0,$FORMAT_LINE);
#        $comment_text = substr($comment_text,$FORMAT_LINE);
#        $ret_val .= "\n" unless (substr($comment_text,0,1) eq "\n");
#        $comment_text =~ s/^\n// if ($comment_text =~ /^\n\S/);
#        $comment_text =~ s/^(\s)(\S.*)/$2/g;
#        $ret_val =~ s/\s\n$/\n/g;
#        $loop = 0;
#        next;
#
      } else {  #80th character is a space
        $ret_val .= substr($comment_text,0,$FORMAT_LINE);
        $comment_text = substr($comment_text,$FORMAT_LINE);
        $ret_val .= "\n" unless (substr($comment_text,0,1) eq "\n");
        $ret_val .= "\n" if ($next_char eq "\n");
        $comment_text =~ s/^\n// if ($comment_text =~ /^\n\S/);
        $comment_text =~ s/^(\s)(\S.*)/$2/g;
        $ret_val =~ s/\s\n$/\n/g;
        $loop = 0;
        next;
      }
    }
    if (length($comment_text) <= $FORMAT_LINE) {
      $ret_val .= $comment_text;
      last;
    }
  }
  return $ret_val;
}

sub format_comment_text {
  my $comment_text = shift;
  my $new_position=shift;
  $FORMAT_LINE = $new_position if defined($new_position);
  my $ret_val = "";
  $comment_text =~ s/\r//g;
  my $num_space=0;
  for ($loop=0;$loop<$FORMAT_LINE;$loop++) {
    my $cur_char = substr($comment_text,$loop,1);
    $num_space++ if ($cur_char eq " ");
    if ($cur_char eq "\n") { #CR detected
      $ret_val .= substr($comment_text,0,$loop+1);
      $comment_text = substr($comment_text,$loop+1);
      #$comment_text =~ s/^(\s)(\S.*)/$2/g;
      #$ret_val =~ s/\s\n$/\n/g;
      $loop = 0;
      $num_space=0;
      next;
    } elsif ($loop == $FORMAT_LINE-1) { #pointer is in the 80the position
      my $next_char=substr($comment_text,$FORMAT_LINE,1);
      if ($cur_char =~ /\S/ and $next_char =~/\S/) { #80th character is within a word
        if ($num_space) {
          while ($cur_char =~ /\S/) {
            $loop--;
            $cur_char = substr($comment_text,$loop,1);
            last unless ($loop);
          }
 #       unless ($loop) {
 #         $ret_val .= substr($comment_text,0,$FORMAT_LINE);
 #         $ret_val .= "\n";
 #         $comment_text = substr($comment_text,$FORMAT_LINE);
 #       } else {
#          $ret_val .= substr($comment_text,0,$loop+1);
#          $ret_val .= "\n";
#          $comment_text = substr($comment_text,$loop+1);
#        }
        } else {  #a word longer than 80
          while ($cur_char =~ /\S/) {
            $loop++;
            $cur_char = substr($comment_text,$loop,1);
            last if (length($comment_text) <= $loop);
          }
        }

        $ret_val .= substr($comment_text,0,$loop+1);
        $ret_val .= "\n";
        $comment_text = substr($comment_text,$loop+1);

        $comment_text =~ s/^(\s)(\S.*)/$2/g;
        $ret_val =~ s/\s\n$/\n/g;
        $loop = 0;
        next;
      } else {  #80th character is a space
        $ret_val .= substr($comment_text,0,$FORMAT_LINE);
        $comment_text = substr($comment_text,$FORMAT_LINE);
        $ret_val .= "\n" unless (substr($comment_text,0,1) eq "\n"); 
        $ret_val .= "\n" if ($next_char eq "\n");
        $comment_text =~ s/^\n// if ($comment_text =~ /^\n\S/);
        $comment_text =~ s/^(\s)(\S.*)/$2/g;
        $ret_val =~ s/\s\n$/\n/g;
        $loop = 0;
        next;
      }
    }
    if (length($comment_text) <= $FORMAT_LINE) {
      $ret_val .= $comment_text;
      last;
    }
  }
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
sub reduce_text_plain {
  my $text = shift;
  my $len = shift;
  my @temp = split '\n', $text;
  if ($#temp > $len) {
    my @temp2;
    for (my $loop=0;$loop<$len;$loop++) {
      $temp2[$loop] = $temp[$loop];
    }
    $text = join "\n", @temp2;
    $text .= "\n\nand more ...";
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
  $ret_val = "checked" if ($num == 1);
  return $ret_val;
}

sub checktonum {
  my $checked =shift;
  return 0 unless my_defined($checked);
  my $ret_val = 0;
  $ret_val = 1 if (lc($checked) eq "on");
  return $ret_val;
}

sub full_status_value {
  $_ = shift;
  return "" unless (my_defined($_));
  if (/Informational/) {
    return "an Informational RFC";
  } elsif (/Experimental/) {
    return "an Experimental RFC";
  } elsif (/Proposed/) {
    return "a Proposed Standard";
  } elsif (/Draft/) {
    return "a Draft Standard";
  } elsif (/BCP/) {
    return "a BCP";
  } elsif (/Standard/) {
    return "a Full Standard";
  } elsif (/Request|None/) {
    return "*** YOU MUST SELECT AN INTENDED STATUS FOR THIS DRAFT AND REGENERATE THIS TEXT ***";
  } else {
    return "a $_";
  }
}

