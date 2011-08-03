#!/usr/local/bin/perl

use lib '/a/www/ietf-datatracker/release/';
use GEN_UTIL;
use GEN_DBUTIL_NEW;
use IETF;
$devel_mode = 0;
$dbname = "ietf";
$dbname="develdb" if ($devel_mode);
init_database($dbname);
$dbh=get_dbh();
$iesg_password_file = "/a/www/ietf-datatracker/release/.htpasswd_iesg";
$ls_password_file = "/a/www/ietf-datatracker/release/.htpasswd_ls";
$master_password_file = "/a/www/ietf-datatracker/release/.htpasswd_master";
$wg_access_file = "/tmp/.htaccess";
$ls_access_file_temp = "/a/www/ietf-datatracker/release/.htaccess_ls";
$iesg_access_file_temp = "/a/www/ietf-datatracker/release/.htaccess_iesg";
$ls_access_file = "/tmp/.htaccess";
$iesg_access_file = "/tmp/.htaccess";
$access_header = qq{AuthUserFile /a/www/ietf-datatracker/release/.htpasswd_master
AuthGroupFile /dev/null
AuthName ByPassword
AuthType Basic
                                                                                               
<Limit GET POST>
};

######## Create IESG users list ###############
my $iesg_user_list = `cat $iesg_access_file_temp`;
open ACCESS_IESG, ">$iesg_access_file";
print ACCESS_IESG qq{$access_header
$iesg_user_list
</Limit>
};
close ACCESS_IESG;




######## Create WG and LS users and master passwords list #################
my $ls_user_list = `cat $ls_access_file_temp`;
my $prev_tag=0;
system "cat $iesg_password_file > $master_password_file";
system "cat $ls_password_file >> $master_password_file";
open PASSWD,">>$master_password_file";
open ACCESS_WG,">$wg_access_file";
open ACCESS_LS, ">$ls_access_file";
print ACCESS_WG $access_header;
print ACCESS_LS $access_header;
print ACCESS_LS $ls_user_list;

my @List_iesg = db_select_multiple($dbh,"select login_name from iesg_login where user_level in (0,1,4,5)");
for my $array_ref (@List_iesg) {
  my ($login_name) = @$array_ref;
  print ACCESS_WG "require user $login_name\n";
  print ACCESS_LS "require user $login_name\n";
}

my @List = db_select_multiple($dbh,"select person_or_org_tag,password,login_name from wg_password");
for my $array_ref (@List) {
  my ($person_or_org_tag,$password,$login_name) = @$array_ref;
  my $password_line = "";
  if ($password =~ /^dd/) {
  } else {
    #$password_line = `/usr/bin/htpasswd -nb $email $password`;
    #chomp($password_line);
    $password=my_crypt($password);
  } 
  $password_line = "$login_name:$password\n";
  print ACCESS_WG "require user $login_name\n";
  print ACCESS_LS "require user $login_name\n";
  print PASSWD "$password_line";
}

print ACCESS_WG "</Limit>\n";
print ACCESS_LS "</Limit>\n";
close ACCESS_WG;
close ACCESS_LS;
close PASSWD;
$dbh->disconnect();
exit;

