#!/usr/local/bin/perl 

$target_dir = "/usr/local/etc/httpd/htdocs/IESG/EVALUATIONS";
$target_file = "*.bal";

open FTP,"| /usr/bin/ftp -n" or die "Can't execute ftp\n\n";

print FTP <<END_OF_TRANSPORT
open odin 
user mlee sunny0hm
cd $target_dir 
prompt
mget $target_file
quit

END_OF_TRANSPORT
;
close FTP;

exit;


