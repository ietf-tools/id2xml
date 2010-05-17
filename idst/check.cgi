#!/usr/bin/perl -w

#############################################################################
#      Program: check.cgi
#
#      Author : Shailendra Singh Rathore
#
#      Last Modified Date: 2/14/2007
#
#      This application runs Henrik's tool on the uploaded Internet Draft
#############################################################################


use lib '/a/www/ietf-datatracker/release/';
use CGI(':standard');
use DBI;
use GEN_UTIL;
use GEN_DBUTIL_NEW;
use IETF;

$script_loc=$ENV{SCRIPT_NAME};
$http_host=$ENV{HTTP_HOST};
$devel_mode = ($script_loc =~ /devel/)?1:0;
$qa_mode = 0;
$dbname = "ietf";
$query = new CGI;
                                                                                     
if ($devel_mode) 
{
   $qa_mode = ($http_host =~ /datatracker/)?1:0;
   $rUser = $ENV{REMOTE_USER};
   $dbname=($qa_mode)?"ietf_qa":"test_idst";
   $title_text = ($qa_mode)?"QA Mode":"Development Mode";
}

#Connecting to the database

init_database($dbname);
$dbh = get_dbh();
                                                                                     

#Check if any parameter is being sent through a query string

if (length ($ENV{'QUERY_STRING'}) > 0)
{
   $buffer = $ENV{'QUERY_STRING'};
   @pairs = split(/&/, $buffer);
   foreach $pair (@pairs)
   {
      ($name, $value) = split(/=/, $pair);
      $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
      $in{$name} = $value;
   }
}

$sub_id = $in{'submission_id'};
error_idst ($query,"Possible SQL Injection detected.") if ($sub_id =~ /\D/);
$henriks_tool = "/a/www/ietf-datatracker/release/idnits --submitcheck";


$sql = "select status_id,filename,revision from id_submission_detail where submission_id = ?";
($status_id,$filename,$revision) = db_select_secure($dbh,$sql,$sub_id);

#Check for the submission id and valid status id

if (($sub_id) && ($status_id == 1))
{

   #Fetching value from id_submission_env

   $sql = "select staging_path from id_submission_env";
   $stg_path = db_select($dbh,$sql);
   $file = $stg_path."$filename-$revision.txt";
   $output = `$henriks_tool --nitcount $file`;
        $output =~ s/Run idnits with the --verbose option for more detailed information.//; 
   if ($output =~ /\s+Summary:\s+0\s+|No nits found/) #IDNITs Passed
   {
      $status_id =2;
      $output_q = db_quote($output);
      $sql = "update id_submission_detail set status_id = '$status_id',idnits_message = $output_q   where submission_id = '$sub_id'";
      db_update($dbh,$sql); 
   }else{ #IDNITs failed
      $status_id =203;
      $error_message=1;
      $output_q = db_quote($output);
      $sql = "update id_submission_detail set status_id='$status_id',idnits_message = $output_q,idnits_failed=1 where submission_id=$sub_id";
      db_update($dbh,$sql);
   }
   print $query->redirect(-uri => "validate.cgi?submission_id=$sub_id");
   exit;
}else{
   if(!sub_id) 
   {
      #If submission id is not found
      $status_id = 108;
      $sql = "update id_submission_detail set status_id ='$status_id'  where submission_id = '$sub_id'";
      db_update($dbh,$sql); 
      print $query->redirect(-uri => "status.cgi?submission_id=$sub_id&redirect=1");
      exit;
   }else{
      #Draft is not in an appropriate status for the requsted page
      $status_id = 107;
      $sql = "update id_submission_detail set status_id ='$status_id'  where submission_id = '$sub_id'";
      db_update($dbh,$sql); 
      print $query->redirect(-uri => "status.cgi?submission_id=$sub_id&redirect=1");
      exit;
   }
}
$dbh->disconnect();
