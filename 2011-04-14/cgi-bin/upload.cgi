#!/usr/bin/perl
##########################################################################
# Copyright © 2004, Foretec Seminars, Inc.
##########################################################################
use lib '/a/www/ietf-datatracker/release';
use GEN_DBUTIL;
use GEN_UTIL;
use IETF;
use CGI;
use CGI_UTIL;

use constant BUFFER_SIZE => 16_384;
use constant MAX_FILE_SIZE => 8_388_608;
use constant MAX_DIR_SIZE => 100 * 1_048_576;
use constant MAX_OPEN_TRIES => 100;
$CGI::DISABLE_UPLOADS = 0;
$CGI::POST_MAX = MAX_FILE_SIZE;
$host=$ENV{SCRIPT_NAME};
$devel_mode = ($host =~ /ls_demo/)?1:0;
$test_mode = ($host =~ /test/)?1:0;
$dbname = "ietf";
$mode_text = "";
if ($devel_mode) {
  $dbname="develdb";
  $mode_text = "Development Mode";
} elsif ($test_mode) {
  $dbname="testdb";
  $mode_text = "Test Mode";
}
init_database($dbname);
#$up_dir_local = "/a/www/ietf-datatracker/htdocs/documents/LIAISON";
$up_dir_local = "/a/www/ietf-datatracker/documents/LIAISON";

#$up_dir = "/usr/local/etc/httpd/htdocs/IESG/LIAISON";
my $q = new CGI;
$q->cgi_error and error ($q, "Error transferring file:. " . $q->cgi_error );
my $file = $q->param("file")  || error ($q,"No file received.");
my $fh = $q->upload("file", -override=>1);
unless ($fh) {
  error ($q,"Invalid File - $file, $fh");
}
my $type=$q->uploadInfo($fh)->{'Content-Type'};
seek($fh,0,2);
my $size=tell($fh);
seek($fh,0,0);
my $buffer = "";
my $filename = $q->param("file");

my $person_or_org_tag = $q->param("person_or_org_tag");
my $detail_id = $q->param("detail_id");
my $file_title = $q->param("file_title");
$file_title = db_quote($file_title);
my @temp = split '\.',$filename;
my $file_extension = "";
$file_extension = "." . $temp[$#temp] if ($#temp > 0);
my $sqlStr = "insert into uploads (file_title,person_or_org_tag,file_extension,detail_id) values ($file_title,$person_or_org_tag,'$file_extension',$detail_id)";
db_update ($sqlStr,"upload.cgi","Upload User");
my $file_number = db_select("select max(file_id) from uploads");
$filename = "file${file_number}${file_extension}";

$form_header_main = qq{<form action="liaison_interim.cgi" method="POST">};

open OUTPUT,">$up_dir_local/$filename" or error($q,"can not open the file - $filename");
binmode $fh;
binmode OUTPUT;
                                                                                                
while (read($fh,$buffer,BUFFER_SIZE)) {
  print OUTPUT $buffer;
}

my $success_text = qq{
<br>
<hr>
<blockquote>
<center><font size=4 color="#CC3300">File has been uploaded successfully</font><br>
Input: $fh, $type, $size<br>
$form_header_main
<input type="hidden" name="file_id">
<input type="hidden" name="person_or_org_tag" value="$person_or_org_tag">
<a href="liaison_interim.cgi?&person_or_org_tag=$person_or_org_tag"><input type="submit" name="submit" value="Main Screen"></a>
</form>
</center>
</blockquote>
};

#system "/usr/local/bin/scp -i /.ssh/id_dsa $up_dir/$filename ietfadm\@odin.ietf.org:$up_dir/$filename";  #DEPLOY
#unless ($devel_mode) {
#  chdir $up_dir_local;
#  open FTP,"| /usr/bin/ftp -n" or return "Can't execute ftp\n\n";
#  print FTP <<END_OF_TRANSPORT
#open odin
#user ietfadm h0t3l;cal
#cd $up_dir
#put $filename
#quit
#                                                                                                         
#END_OF_TRANSPORT
#;
#  close FTP;
#}

close OUTPUT and msg($q,$success_text);
                                                                                                
error ($q,"Uploading was UNSUCCESSFUL... - $filename<br>-$fh-<br>");



sub dir_size {
  my $dir=shift;
  my $dir_size=0;
  opendir DIR, $dir or die "Unable to open $dir: $!";
  while ( readdir DIR ) {
    $dir_size += -s "$dir/$_";
  }
  return $dir_size;
}
                                                                                                
sub error {
  my ($q,$reason)=@_;
                                                                                                
  print $q->header("text/html"),
        $q->start_html("Error"),
        $q->h1("Error"),
        $q->p("Your upload was not proceed because the following error ",
              "occured: "),
        $q->p($q->i($reason)),
        $q->end_html;
  exit;
}
                                                                                                
sub msg {
  my ($q,$text)=@_;
                                                                                                
  print $q->header("text/html"),
        $q->start_html("File Upload Result"),
        $q->h1("File Upload Result $mode_text"),
        $q->p($text),
        $q->end_html;
  exit;
}

