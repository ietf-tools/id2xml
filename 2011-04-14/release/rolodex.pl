#!/usr/local/bin/perl
##########################################################################
# Copyright © 2002, Foretec Seminars, Inc.
##########################################################################
use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL;
use IETF;

init_database("ietf");


$switch = $ARGV[0];
my %address_type;

$sqlStr = qq{
SELECT a.person_or_org_tag,a.first_name,a.last_name,b.affiliated_company
from person_or_org_info a left outer join postal_addresses b on
(a.person_or_org_tag = b.person_or_org_tag and
a.address_type = b.address_type)
WHERE 1 = 1
};

if (defined($ARGV[1]) and $ARGV[1] eq "-f") {
   $first_arg = 2;
   $second_arg = 3;
   $third_arg = 4;
} else {
   $first_arg = 1;
   $second_arg = 2;
   $third_arg = 3;
}
if ($switch eq "-locate" or $switch eq "-phone" or $switch eq "-email") {
   if (defined($ARGV[$second_arg])) {
      $uFirstName = uc($ARGV[$first_arg]);
      $sqlStr .= qq{AND first_name_key LIKE '$uFirstName%'\n};
      $uLastName = uc($ARGV[$second_arg]);
      $sqlStr .= qq{AND last_name_key LIKE '$uLastName%'\n};
   } else {
      $uLastName = uc($ARGV[$first_arg]);
      $sqlStr .= qq{AND last_name_key LIKE '$uLastName%'\n};
   } 
} else {
   if (defined($ARGV[$third_arg])) {
      $uFirstName = uc($ARGV[$first_arg]);
      $sqlStr .= qq{AND first_name_key LIKE '$uFirstName%'\n};
      $uLastName = uc($ARGV[$second_arg]);
      $sqlStr .= qq{AND last_name_key LIKE '$uLastName%'\n};
   } else {
      $uLastName = uc($ARGV[$first_arg]);
      $sqlStr .= qq{AND last_name_key LIKE '$uLastName%'\n};
   } 
}
$sqlStr .= "ORDER BY a.last_name, a.first_name\n";

#print $sqlStr;
#exit(1);
$person_or_org_tag = getTag($sqlStr);
if ($person_or_org_tag < 0) {
   die "This person is NOT located in the database!\n";
} elsif ($person_or_org_tag == 0) {
   print "Good Bye...\n";
   exit(1);
} else {
   if ($switch eq "-view") {
      view_record($person_or_org_tag);
   }
   elsif ($switch eq "-locate") {
      display_name($person_or_org_tag);
      locate_record($person_or_org_tag);
   }
   elsif ($switch eq "-phone") {
      display_name($person_or_org_tag);
      display_phone_numbers($person_or_org_tag);
   }
   elsif ($switch eq "-email") {
      display_name($person_or_org_tag);
      display_email_addresses($person_or_org_tag);
   }
   elsif ($switch eq "-change_email") {
      change_email($person_or_org_tag);
   }
   elsif ($switch eq "-change_phone") {
      change_phone($person_or_org_tag);
   }
   elsif ($switch eq "-change_fax") {
      change_fax($person_or_org_tag);
   }
   elsif ($switch eq "-change_comp_name") {
      change_comp_name($person_or_org_tag);
   }
   elsif ($switch eq "-change_name") {
      change_name($person_or_org_tag);
   }
   else {
      die "Unknown switch: $switch\n";
   }
}

exit;


sub getTag {
   my $sqlStr = shift;
   my @List = db_select_multiple($sqlStr);
   my @nList;
   for $array_ref (@List) {
      my @row = @$array_ref;
      push @nList, [ @row ];
   }
   if ($#nList == -1) {
      
      return -1;
   }
   elsif ($#nList == 0) {
      return $nList[0]->[0];
   }
   else {
      $count = 0;
      for $array_ref ( @nList ) {
         my $fName = $array_ref->[1];
         my $lName = $array_ref->[2];
         my $cName = $array_ref->[3];
         $_ = $fName;
         s/(\w+) +(\s*)/$1/;
         $fName = $_;
         $_ = $lName;
         s/(\w+) +(\s*)/$1/;
         $lName = $_;
         if (defined($cName)) {
            $_ = $cName;
            s/((\w+\s)+) +(\s*)/$1/;
            s/(.*\.) +(\s*)/$1/;
            $cName = $_;
         } else {
            $cName = "";
         }
         $count++;
	 format STDOUT =
@<<<<<< @<<<<<<<<<<<<<<< @<<<<<<<<<<<<<<<<<<< @<<<<<<<<<<<<<<<<<<<<<<<<<
$count, $fName,          $lName,              $cName
.
         write STDOUT;
         if ($count%10 == 0) {
            print "\n[N]ext  [S]elect  [Q]uit > ";
            chomp($option = uc(<STDIN>));
            $_ = $option;
            if ($option eq "N") {
               print "---------------------------------------------------------\n";
               next;
            }
            elsif ($option eq "S") {
               $selected = 1;
               last;
            }
            elsif (/\d/) {
               return $nList[$option-1]->[0];
            }
            else { return 0; }
         }
      }
      unless (defined($selected)) {
         print "\n[S]elect  [Q]uit > ";
         chomp($choice = uc(<STDIN>));
      } else {$choice = " ";}
      $_ = $choice;
      if ($choice eq "S" || defined($selected)) {
        print "Select Record Number> ";
        chomp($recNum = <STDIN>);
        return $nList[$recNum-1]->[0];
      }
      elsif (/\d/) {
         return $nList[$choice-1]->[0];
      }
      else {
        return 0;
      }
   }    
   return 0;
   
}
format STDOUT_TOP =
Rec #   First Name       Last Name            Company Name
--------------------------------------------------------------------
.

sub view_record {
   my $tag = shift;

   $sqlStr = qq{SELECT address_type,person_title,affiliated_company,department,
   staddr1,staddr2,mail_stop,city,state_or_prov,postal_code,country
   FROM postal_addresses
   WHERE person_or_org_tag = $tag AND address_priority = 1
   };
   my ($address_type,$person_title,$cName,$dept,$staddr1,$staddr2,$mailstop,$city,
   $state_or_prove,$postal_code,$country) = db_select($sqlStr);

   $sqlStr = qq{SELECT name_prefix,first_name,middle_initial,last_name,name_suffix
   FROM person_or_org_info
   WHERE person_or_org_tag = $tag
   };
   my ($prefix,$fName,$mI,$lName,$suffix) = db_select($sqlStr);

   $sqlStr = qq{SELECT email_type,email_address,email_comment
   FROM email_addresses
   WHERE person_or_org_tag = $tag AND email_priority = 1
   };
   my ($email_type,$email_address,$email_comment) = db_select($sqlStr);

   $sqlStr = qq{SELECT phone_type,phone_number,phone_comment
   FROM phone_numbers
   WHERE person_or_org_tag = $tag and phone_priority = 1
   };
   my ($phone_type,$phone_number,$phone_comment) = db_select($sqlStr);

   $sqlStr = qq{SELECT phone_type,phone_number,phone_comment
   FROM phone_numbers
   WHERE person_or_org_tag = $tag and (phone_type = 'WF' OR phone_type = 'HF')
   };
   my ($fax_type,$fax_number,$fax_comment) = db_select($sqlStr);

   $suffix = rm_tr($suffix);
   $staddr2 = rm_tr($staddr2);
   $mail_stop = rm_tr($mail_stop);
   $email_comment = rm_tr($email_comment);
   $phone_comment = rm_tr($phone_comment);
   format VIEWALL =
 Prefix    First Name          M.I.   Last Name              Suffix   Tag
[@<<<<<<]  [@<<<<<<<<<<<<<<<] [@<<]  [@<<<<<<<<<<<<<<<<<<<] [@<<<<<] [@>>>>>>]
$prefix,    $fName,           $mI,   $lName,                $suffix, $tag

Address: [@<<<<]
$address_type
 Title:    [@<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<]
 $person_title
 Org:      [@<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<]
 $cName
 Dept:     [@<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<]
 $dept
 Addr 1:   [@<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<]
 $staddr1
 Addr 2:   [@<<<<<<<<<<<<<<<<<<<<<]  M/S [@<<<<<<<<<<]
 $staddr2, $mail_stop
 City [@<<<<<<<<<<<<<<<]  St [@<<<<<<<<]  Zip [@<<<<<<<<<<<]  Co [@<<<<<<<<<<<<<]
 $city,$state_or_prove,$postal_code,$country
 
Phone: [@<<<<]  Num: [@<<<<<<<<<<<<<<<<]   Fax: [@<<<<]  Num: [@<<<<<<<<<<<<<<<<]
$phone_type,$phone_number,$fax_type,$fax_number
 Cmts: [@<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<]    Cmts: [@<<<<<<<<<<<<<<<<<<<<<<<<<<<<]
$phone_comment,$email_comment

Email: [@<<<<]  [@<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<]
$email_type,$email_address
 Comments: [@<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<]
$email_comment 


.
   clear_screen();
   open VIEWALL,">&STDOUT";
   write VIEWALL;
   close VIEWALL;
   return -1;
}

sub locate_record {
   my $tag = shift;
   display_addresses($tag);
   display_phone_numbers($tag);
   display_email_addresses($tag);
   return -1;
}

sub display_name {
   my $tag = shift;
   
   $sqlStr = qq{SELECT name_prefix,first_name,middle_initial,last_name,name_suffix
   FROM person_or_org_info
   WHERE person_or_org_tag = $tag
   };
   my ($prefix,$fName,$mI,$lName,$suffix) = db_select($sqlStr);
   $prefix = rm_tr($prefix);
   $fName = rm_tr($fName);
   $lName = rm_tr($lName);
   $suffix = rm_tr($suffix);
   $mI = rm_tr($mI);
   print "$prefix $fName $mI $lName $suffix ($tag)\n";

   return -1;
} 

sub display_addresses {
   my $tag = shift;
   
   $sqlStr = qq{SELECT address_type,person_title,affiliated_company,department,
   staddr1,staddr2,mail_stop,city,state_or_prov,postal_code,country
   FROM postal_addresses
   WHERE person_or_org_tag = $tag
   };
   my @List = db_select_multiple($sqlStr);
   my @addrList;
   for $array_ref (@List) {
      my @row = @$array_ref;
      push @addrList, [ @row ];
   }
   for $array_ref ( @addrList ) {
 
      my ($address_type,$person_title,$cName,$dept,$staddr1,$staddr2,$mailstop,$city,
      $state_or_prove,$postal_code,$country) = @$array_ref;
      $city = rm_tr($city);
      $address_type = rm_tr($address_type);
      $state_or_prove = rm_tr($state_or_prove);
      $person_title = rm_tr($person_title) if my_defined($person_title);
      $cName = rm_tr($cName) if my_defined($cName);
      $dept = rm_tr($dept) if my_defined($dept);
      if ($address_type eq "W") {      
         print "  Work Address\n";
      } elsif ($address_type eq "H") {
         print "  Home Address\n";
      } else {
         print "  Extra Address\n";
      }
         print "    Title:	$person_title\n" if my_defined($person_title);
         print "    Company:	$cName\n" if my_defined($cName);
         print "    Department:	$dept\n" if my_defined($dept);
         print "                $staddr1\n";
         print "		$staddr2\n" if my_defined($staddr2);
         print "		$city, $state_or_prove  $postal_code\n";
         print "         	$country\n";
   }
   
   return -1;
}

sub display_phone_numbers {
   my $tag = shift;
   my $phList;
   %phType = (
      W => 'Work Phone',
      H => 'Home Phone',
      WF => 'Work Fax',
      HF => 'Home Fax',
      HT => 'Home TDD',
      WT => 'Work TDD',
      MP => 'Mobile',
      PG => 'Pager'
   );
   $sqlStr = qq{SELECT phone_type,phone_number,phone_comment
   FROM phone_numbers
   WHERE person_or_org_tag = $tag
   };
   my @List = db_select_multiple($sqlStr);
   for $array_ref (@List) {
      my @row = @$array_ref;
      push @phList, [ @row ];
   }
   for $array_ref (@phList) {
      my ($phone_type,$phone_number,$phone_comment) = @$array_ref;
      $phone_type = rm_tr($phone_type);
      $phone_number = rm_tr($phone_number) if my_defined($phone_number);
      if (my_defined($phone_comment)) {
         $phone_comment = rm_tr($phone_comment) ;
      } else {
         $phone_comment = " ";
      }
      if (defined($phType{$phone_type})) {
         print "    $phType{$phone_type}:";
      } else {
         print "    Unknown:";
      }
      print "\t$phone_number\t$phone_comment\n";
   }
   
   return -1;
}

sub display_email_addresses {
   my $tag = shift;
   my $emailList;
   $sqlStr = qq{SELECT email_type,email_address,email_comment
   FROM email_addresses
   WHERE person_or_org_tag = $tag
   };
   my @List = db_select_multiple($sqlStr);
   for $array_ref (@List) {
      my @row = @$array_ref;
      push @emailList, [ @row ];
   }
   for $array_ref (@emailList) {
      my ($email_type,$email_address,$email_comment) = @$array_ref;
      #$email_type = rm_tr($email_type);
      $email_address = rm_tr($email_address);
      print "    ${email_type}:\t$email_address\n";
      if (my_defined($email_comment)) {
         $email_comment = rm_tr($email_comment) ;
         print "\t\t$email_comment\n";
      }
      
   }
   
   return -1;
}

sub change_name {
   my $tag = shift;

   $new_name = $ARGV[$#ARGV];
   @fullName = split '_', $new_name;
   unless ($ARGV[1] eq "-f") {
      print "Do you want to change name to @fullName? > ";
      chomp($option = <STDIN>);
      unless (uc($option) eq "Y") {
         return 0;
      }
   }
   if ($#fullName == 1) {  #No Middle Initial
      ($fName,$lName) = @fullName;
      $mName = "";
      $mName_key = "";   
   } else {
      ($fName,$mName,$lName) = @fullName;
      $mName_key = uc($mName);
   }
   $fName_key = uc($fName);
   $lName_key = uc($lName);
   $sqlStr = qq{UPDATE person_or_org_info
   SET first_name = '$fName',
       first_name_key = '$fName_key',
       middle_initial = '$mName',
       middle_initial_key = '$mName_key',
       last_name = '$lName',
       last_name_key = '$lName_key'
   WHERE person_or_org_tag = $tag
   };
   db_update($sqlStr);
   return -1;
}

sub change_comp_name {
   my $tag = shift;

   $new_name = $ARGV[$#ARGV];
   @fullName = split '_', $new_name;
   unless ($ARGV[1] eq "-f") {
      print "Do you want to change company name to @fullName? > ";
      chomp($option = <STDIN>);
      unless (uc($option) eq "Y") {
         return 0;
      }
   }
   $sqlStr = qq{UPDATE postal_addresses
   SET affiliated_company = '@fullName'
   WHERE person_or_org_tag = $tag AND address_priority=1
   };
   db_update($sqlStr);
   return -1;
}

sub change_email {
   my $tag = shift;

   $new_email = $ARGV[$#ARGV];
   unless ($ARGV[1] eq "-f") {
      print "Do you want to change email address to $new_email? > ";
      chomp($option = <STDIN>);
      unless (uc($option) eq "Y") {
         return 0;
      }
   }
   $sqlStr = qq{UPDATE email_addresses
   SET email_address = '$new_email'
   WHERE person_or_org_tag = $tag AND email_priority=1
   };
   db_update($sqlStr);
   return -1
}

sub change_phone {
   my $tag = shift;

   $new_phone = $ARGV[$#ARGV];
   unless ($ARGV[1] eq "-f") {
      print "Do you want to change phone number to $new_phone? > ";
      chomp($option = <STDIN>);
      unless (uc($option) eq "Y") {
         return 0;
      }
   }
   $sqlStr = qq{UPDATE phone_numbers
   SET phone_number = '$new_phone'
   WHERE person_or_org_tag = $tag AND phone_priority=1
   };
   db_update($sqlStr);
   return -1;
}

sub change_fax {
   my $tag = shift;

   $new_phone = $ARGV[$#ARGV];
   unless ($ARGV[1] eq "-f") {
      print "Do you want to change fax number to $new_phone? > ";
      chomp($option = <STDIN>);
      unless (uc($option) eq "Y") {
         return 0;
      }
   }
   $sqlStr = qq{UPDATE phone_numbers
   SET phone_number = '$new_phone'
   WHERE person_or_org_tag = $tag AND (phone_type = 'WF' OR phone_type = 'HF')
   };
   db_update($sqlStr);
   return -1;
}

sub change_mailing {
   my $tag = shift;

   return -1;
}
