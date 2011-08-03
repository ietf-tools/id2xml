#!/usr/bin/perl -w

##########################################################################
#      Program: upload.cgi
#      Author : Shailendra Singh Rathore
#      Last Modified Date: 2/15/2007
#
#      This application provides an interface to upload an Internet Draft 
#      and also checks the draft for its validity 
#
##########################################################################

use lib '/a/www/ietf-datatracker/release';
use CGI qw(':standard');
use CGI_UTIL;
use GEN_UTIL;
use GEN_DBUTIL_NEW;
use IETF;

$script_loc=$ENV{SCRIPT_NAME};
$http_host=$ENV{HTTP_HOST};
$devel_mode = ($script_loc =~ /devel/)?1:0;
$qa_mode = 0;
$db_name = "ietf";
$query = new CGI;
$tester_email_msg="";
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

$user_email = ($devel_mode)?db_select($dbh,"select email_address from email_addresses a, iesg_login b where login_name='$rUser' and a.person_or_org_tag=b.person_or_org_tag and email_priority=1"):"";
$tester_email_msg = "<font size=\"-1\">Tester's email address: $user_email</font><br>\n" if $devel_mode;

$flag=0;
$wgn = 0;
$rev_flag = 0;

$fname = $query->param("text");
$fname =~ s/.*[\/\\](.*)/$1/;

$filename="";
$revision="";
#Check for the running mode 

if (!defined($fname))
{
	print_html();
}else{
	new_upload();
}

#Function to upload a draft on the server
 
sub new_upload
{
	$warning_message = "";

	#Check for the other file formats

	if($xml_fname = $query->param("xml"))
	{
		$xml = ",.xml";
		$xml_flag = 1;
	}
	$xml_fname =~ s/.*[\/\\](.*)/$1/;

	if($ps_fname = $query->param("ps"))
	{
		$ps = ",.ps";
		$ps_flag = 1;
	}
	$ps_fname =~ s/.*[\/\\](.*)/$1/;

	if($pdf_fname = $query->param("pdf"))
	{
		$pdf = ",.pdf";
		$pdf_flag = 1;
	}
	$pdf_fname =~ s/.*[\/\\](.*)/$1/;

	#Check if filename exist

	if ($fname)
	{
		#Check if other files are in valid format

		if ((($xml_fname ne "") && ($xml_fname !~ /.*.xml$/)) || (($ps_fname ne "") && ($ps_fname !~ /.*.ps$/)) || (($pdf_fname ne "")&&($pdf_fname !~ /.*.pdf$/)))
		{
			$error_message  = qq{Other format of a document should be in XML, PDF, or PS.<br>
Please go back to <a href=\"upload.cgi\">Upload Page</a> and re-submit your draft.<br>
};
			#print_html($error_message);
                        error_idst ($query,$error_message);
			exit;
		}

  
		$upload_filehandle = $query->upload("text");
		seek($upload_filehandle,0,2);
		$size = tell($upload_filehandle);
		seek($upload_filehandle,0,0);

		# Checking size of the document 

		if ($size <= 6000000)
		{
			$random = generate_random_string(5);
			open(UPLOADFILE, "> /tmp/$random.txt") || error_idst ($query, "could not create the file\n");  #UPLOADING FILE IN TMP AREA
			binmode UPLOADFILE;
			while (<$upload_filehandle>)
			{
				print UPLOADFILE;
			}
			close UPLOADFILE;

			#VALIDATE FILE FORMAT

			$res = `file /tmp/$random.txt | grep "ASCII" | wc -l`;
			$unknown_char = `file -i /tmp/$random.txt | grep "charset=unknown" | wc -l`;
			$warning_message .= "* Unknown character set was detected. Meta-data may not be parsed correctly.\n" if ($unknown_char==1);

			if ($res==1) #Document is in text format
			{ 
				open (FH , "/tmp/$random.txt") || error_idst ($query, "Could not open $random.txt\n"); 
                                $flag=0;
                                $line_count=0;
				while( <FH>)
				{
                                        $line_count++;
                                        if (/(draft-\S+)/ and !$flag)  {
                                          $_ = $1;
                                          s/^\W+//;
                                          s/\W+$//;
                                          s/\.txt$//;
                                          $filename = $_;
                                          $revision=$1 if (/.*-(\d+)$/);
                                          $filename =~ s/-\d+$//;
                                          $wgn=1 if ($filename =~ /^draft-ietf-/);
                                          $flag=1;
                                          last;
                                        }
                                        last if ($line_count > 80);
				}
  
                                unless ($flag) { #Not an I-D. Reject it
                                   unlink "/tmp/$random.txt";
                                   $error_message = db_select($dbh,"select status_value from id_submission_status where status_id=111");
                                        $error_message .= qq{<br>
Your submission has been cancelled.<br>
<a href="upload.cgi">[Back to upload page]</a>
};
                                        error_idst ($query,$error_message);
                                        exit;
                                }
#				if ($flag == 0) # Draft title not found
#				{
#					$warning_message  .= "* Could not find draft title.\n";
#					#print_html($warning_message);
#					#exit;
#				}
#                      
				#Extracting group acronym from the document name
                                $_="$filename-$revision";
                                #Scan for WG document status of submission who's filename doesn't look like a WG document
                                $acronym_id=db_select($dbh,"select group_acronym_id from internet_drafts where filename='$filename'");
                                unless ($acronym_id) {
                                  my @temp = split '-';
                                  if ($temp[1] eq "ietf") {
  					$group_acronym = $temp[2];
					$sql = "select acronym_id from acronym a, groups_ietf b where acronym = '$group_acronym' and group_acronym_id=acronym_id and status_id=1";
					$acronym_id = db_select($dbh,$sql);
                                        error_idst ($query,"Invalid WG ID, $group_acronym.") unless $acronym_id;
				  }else{
				    $acronym_id = 1027;
				  }
                                }
				#date as per the MYSQL date format
  
				$current_date = get_current_date(1);
				@dt = split(/\//,$current_date);
				$mysql_date = join '/',($dt[2],$dt[0],$dt[1]);

				$current_time = get_current_time();
				$auth_key = generate_random_string(32);  
				$ip = $ENV{REMOTE_ADDR};
				$file_type = ".txt".$xml.$ps.$pdf;
				check_dos_threshhold ($filename,$revision,$ip,$size,$random,$acronym_id);
				$warning_message = db_quote($warning_message);

				#Check for the valid revision id

				my $invalid_revision=0;

				$tmp_sub_id = db_select($dbh,"select submission_id  from id_submission_detail where filename = '$filename' and status_id > -3 and status_id < 100");
				if ($tmp_sub_id) 
				{
					$status_id = 103;
					#$sql = "insert into id_submission_detail (status_id,last_updated_time,filename,remote_ip,revision,wg_submission,filesize) values('$status_id','$current_time','$filename','$ip','$revision','$wgn',$size)";
					#db_update($dbh,$sql);
					#$sql = "select max(submission_id) from id_submission_detail";
					#$sub_id = db_select($dbh,$sql);
					#print $query->redirect("status.cgi?submission_id=$sub_id");
                                        $error_message = db_select($dbh,"select status_value from id_submission_status where status_id=103");
                                        $error_message .= qq{<br>
<a href="status.cgi?submission_id=$tmp_sub_id">[View status of existing submission]</a><br><br>
Your submission has been cancelled.<br>
<a href="upload.cgi">[Back to upload page]</a>
};
                                        error_idst ($query,$error_message,$tmp_sub_id);
					exit;
				}

				($temp_id_document,$revision_tmp,$expired_tombstone_tmp,$status_id_tmp,$replaced_by) = db_select($dbh,"select id_document_tag,revision,expired_tombstone,status_id,replaced_by from internet_drafts where filename = '$filename'");
				if ($revision eq "00")
				{
					if ($temp_id_document)
					{
						$invalid_revision=1;
					}else{
						$rev_flag=1;
					}
				}else{
					if(!$temp_id_document)
					{
						$invalid_revision=1;
					}else{
                                                if ($status_id_tmp > 3) {
                                                  my $error_msg = "";
                                                  if ($status_id == 5) {
                                                     my ($filename_r,$revision_r) = db_select($dbh,"select filename,revision from internet_drafts where id_document_tag=$replaced_by");
                                                     $error_msg = "$filename has been replaced by $filename_r-$revision_r.";
                                                  } else {
                                                     $error_msg = "$filename has been withdrawn.";
                                                  } 
                                                  error_idst($query,$error_msg);
                                                }
    
						if (($status_id_tmp ==1) || ($expired_tombstone_tmp == 1))
						{
							$d_revision = decrease_revision($revision);
							if (!($revision_tmp eq $d_revision))
							{
								$invalid_revision=1;
							}
						}else{
							if (!($revision_tmp eq $revision))
							{
								$invalid_revision=1;
							}
						}
					}
				}

				if ($rev_flag ==1) # If document has a valid revision number
				{
					$sth = $dbh->prepare("select MAX(id_document_tag) as ID from internet_drafts") or error_idst ($query, $dbh->errstr);
					$row = $sth->execute();
					$row = $sth->fetchrow_hashref();
					$id = $row->{'ID'};

					$sth = $dbh->prepare("select MAX(temp_id_document_tag) as ID from id_submission_detail") or error_idst ($query,$dbh->errstr);
					$row = $sth->execute();
					$row = $sth->fetchrow_hashref();
					$tmp_id = $row->{'ID'};

					if ($id > $tmp_id)
					{
						$temp_id_document = $id + 1;
					}else{
						$temp_id_document = $tmp_id + 1;
					}
  
				}

				#Fetching value from id_submission_env table

				$sth1 = "select staging_path,max_interval from id_submission_env"; 
				@results = db_select($dbh,$sth1);
				$upload_dir = $results[0];
				$max_interval = $results[1];


				#Moving draft to staging area 

				`mv /tmp/$random.txt $upload_dir/$filename-$revision.txt`;
                                 `chmod a+r $upload_dir/$filename-$revision.txt`;
  

				#Uploading other formats to the staging area

				if ($xml_flag == 1)
				{
					$temp = "$filename-$revision.xml";
					upload_file('xml',$upload_dir,$temp);
				}
				if ($ps_flag == 1)
				{
					$temp = "$filename-$revision.ps";
					upload_file('ps',$upload_dir,$temp);
				}
				if ($pdf_flag ==1)
				{
					$temp = "$filename-$revision.pdf";
					upload_file('pdf',$upload_dir,$temp);
				}

				#Inserting uploaded file information into database.

				$sql = "INSERT INTO id_submission_detail(temp_id_document_tag,status_id,last_updated_date,last_updated_time,group_acronym_id,filename,submission_date,remote_ip,revision,auth_key,file_type,warning_message,wg_submission,filesize) VALUES ('$temp_id_document','1','$mysql_date','$current_time','$acronym_id','$filename','$mysql_date','$ip','$revision','$auth_key','$file_type',$warning_message,$wgn,$size)" ;
				db_update($dbh,$sql);

				$sql = "select max(submission_id) from id_submission_detail";
				$sub_id = db_select($dbh,$sql);

				#If revision number is invalid

				if ($invalid_revision) 
				{
					$error_message = 2;
					db_update($dbh,"update id_submission_detail set error_message = '$error_message' where submission_id = '$sub_id'");
				}
   
    
				print $query->redirect(-uri => "check.cgi?submission_id=$sub_id");
				exit;

			}else{
				#Document is not in a text format
				$error_message  = qq{A plain text document must be submitted.<br>
Please go back to <a href=\"upload.cgi\">Upload Page</a> and re-submit your draft.<br>
};
                                error_idst ($query,$error_message);
				#print_html($error_message);
				exit;
			}
		}else{
			#Document size is more than 10 MB
			#$status_id = 102;
			#$sql = "insert into id_submission_detail (status_id,last_updated_time,filename,remote_ip,revision,wg_submission,filesize) values('$status_id','$current_time','$filename','$ip','$revision','$wgn',$size)";
			#db_update($dbh,$sql);
			#$sql = "select max(submission_id) from id_submission_detail";
			#$sub_id = db_select($dbh,$sql);
			#print $query->redirect("status.cgi?submission_id=$sub_id");
                        $error_message = db_select($dbh,"select status_value from id_submission_status where status_id=102");
                        $error_message .= qq{<br>
Your submission has been cancelled.<br>
<a href="upload.cgi">[Back to upload page]</a>
};
                                        error_idst ($query,$error_message);

			exit;
		}
	}else{
		#Filename field is empty 
		$error_message  = qq{Text file required, please select the file.<br>
Please go back to <a href=\"upload.cgi\">Upload Page</a> and re-submit your draft.<br>
            
};
                error_idst ($query,$error_message);
		#print_html($error_message);
		exit;
	}
	print $query->end_html();
	$dbh->disconnect();
}


#Function to display the HTML page

sub print_html
{
	my $error_message = shift;
	my @results = db_select($dbh,"select side_bar_html,top_bar_html,bottom_bar_html  from id_submission_env");
	my $sidebar = $results[0];
	my $topbar = $results[1];
	my $bottombar = $results[2];
	$topbar =~ s/<a href="upload.+>Upload<\/a>/Upload/;
	$topbar =~ s/\?submission_id=##submission_id##//;
	#$topbar =~ s/<a href="status.+>Status<\/a>/Status/;
	my $msg = "<p><font face=Arial size=4 color=#F20000><strong>$error_message</strong></font></p>";
	print $query->header("text/html");
        print $query->start_html(-title=>"Upload $title_text");
print <<HTML;
  <table height="598" border="0">
    <tr valign="top">
HTML
print $sidebar;
print $topbar;
print $msg;
print <<HTML;
$tester_email_msg
        <!-- Body content starts-->
         <div align="left">
             <table border="0" width="657" vspace="0">
               <tr valign="top">
                <td width="651">
                     <!-- InstanceBeginEditable name="Body text" -->
                  <font face="Arial" size="2">
                  <p>This page is used to submit IETF Internet-Drafts to the Internet-Draft repository. The list of current Internet-Drafts can be accessed at <a href="http://www.ietf.org/ietf/1id-abstracts.txt">http://www.ietf.org/ietf/1id-abstracts.txt</a></p>
                  <p>Internet-Drafts are working documents of the Internet Engineering Task Force (IETF), its areas, and its working groups. Note that other group may also distribute working documents as Internet-Drafts.</p>
                  <p>Internet-Drafts are draft documents, and are valid for a maximum of six months. They may be updated, replaced, or obsoleted by other documents at any time.</p>
                  <p>If you run into problems when submitting an Internet-Draft using this and the following pages, you may alternatively submit your draft by email to<a href="mailto:internet-drafts\@ietf.org"> internet-drafts\@ietf.org</a>. However, be advised that manual processing always takes additional time.</p>
                  </font>
                  <hr color="#999999">
                 </td></tr>
                 <tr bgcolor="#ddddff"><td>
                  <font face="Arial" size="4"><strong>Upload a draft</font></strong></font>
                 <form action="upload.cgi" method="post" enctype="multipart/form-data">
                 <table width="600">
                  <tr>
                  <td>.txt format:<font color="red">*</font></td><td><input type="file" name="text" size="50"></td>
                  </tr>
                  <tr><td>.xml format:</font></td><td><input type="file" name="xml" size="50"></td>
                  </tr>
                  <tr><td>.pdf format:</font></td><td><input type="file" name="pdf" size="50"></td>
                  </tr>
                  <tr><td>.ps format:</font></td><td><input type="file" name="ps" size="50"></td>
                  </tr>
                 </table>
<font color="red">* Required</font>
                  <p> 
                    <input type="submit" value="Upload" name="upload">
                  </p>
                  </form>
                  <!-- InstanceEndEditable -->              
                </td>
               </tr>
            </table>
        </div>
        <!-- Body content ends-->
HTML
        
print $bottombar;
print <<HTML;
       </td>
     </tr>
  </table>
</body>
<!-- InstanceEnd --></html>
HTML
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

############################################################
# Function Name: upload_file
# Function Description: Uploads file into staging area
# Input Parameters:
#   param1: Control name
#   param2: Upload path 
#   param1: Filename
# Output: returns true value if file is sucessfully uploaded
# Commented by: Shailendra Singh
# Commented date: 2/15/07
############################################################

sub upload_file
{
	$control_name = shift;
	$upload_dir = shift;
	$flname = shift;

	$upload_filehandle = $query->upload("$control_name");

	open (UPLOADFILE, ">$upload_dir/$flname") || error_idst ($query, "Could not create $flname\n");

	binmode UPLOADFILE;

	while( <$upload_filehandle>)
	{
		print UPLOADFILE;
	}

	close UPLOADFILE;
	return;
}

#####################################
# Function Name: check_dos_threshhold 
# Function Description:
# Input Parameters:
#   param1:
# Output: 
# Commented by:
# Commented date: 2/00/07
#####################################

sub check_dos_threshhold 
{
	my ($filename,$revision,$ip,$size,$temp_file,$group_acronym_id) = @_;
	my $error_message="";
	($max_same_draft_name,$max_same_draft_size,$max_same_submitter,$max_same_submitter_size,$max_same_wg_draft,$max_same_wg_draft_size,$max_daily_submission,$max_daily_submission_size) = db_select($dbh,"select max_same_draft_name,max_same_draft_size,max_same_submitter,max_same_submitter_size,max_same_wg_draft,max_same_wg_draft_size,max_daily_submission,max_daily_submission_size from id_submission_env");
	$max_same_draft_size *= 1000000;
	$max_same_submitter_size *= 1000000;
	$max_same_wg_draft_size *= 1000000;
	$max_daily_submission_size *= 1000000;
	$cur_same_draft_count = db_select($dbh,"select count(submission_id) from id_submission_detail where filename='$filename' and revision='$revision' and submission_date=current_date");
	$error_message .= "* A same I-D cannot be submitted more than $max_same_draft_name times a day. <br>\n" if ($cur_same_draft_count >= $max_same_draft_name);
	$cur_same_draft_size = db_select($dbh,"select sum(filesize) from id_submission_detail where filename='$filename' and revision='$revision' and submission_date=current_date");
	$error_message .= "* A same I-D submission cannot exceed more than $max_same_draft_size MByte a day. <br>\n" if ($cur_same_draft_size >= $max_same_draft_size);
	$cur_same_submitter_count = db_select($dbh,"select count(submission_id) from id_submission_detail where remote_ip='$ip' and submission_date=current_date");
	$error_message .= "* The same submitter cannot submit more than $max_same_submitter I-Ds a day. <br>\n" if ($cur_same_submitter_count >= $max_same_submitter);
	$cur_same_submitter_size = db_select($dbh,"select sum(filesize) from id_submission_detail where remote_ip='$ip' and submission_date=current_date");
	$error_message .= "* A same submitter cannot submit more than $max_same_submitter I-Ds a day. <br>\n" if ($cur_same_submitter_size >= $max_same_submitter_size);
	$cur_same_wg_draft_count = db_select($dbh,"select count(submission_id) from id_submission_detail where group_acronym_id=$group_acronym_id and group_acronym_id <> 1027 and submission_date=current_date");
	$error_message .= "* A same working group I-Ds cannot be submitted more than $max_same_wg_draft times a day. <br>\n" if ($cur_same_wg_draft_count >= $max_same_wg_draft);
	$cur_same_wg_draft_size = db_select($dbh,"select sum(filesize) from id_submission_detail where group_acronym_id=$group_acronym_id and group_acronym_id <> 1027 and submission_date=current_date");
	$error_message .= "* Total size of same working group I-Ds cannot exceed $max_same_wg_draft_size MByte a day. <br>\n" if ($cur_same_wg_draft_size >= $max_same_wg_draft_size);
	$cur_daily_count = db_select($dbh,"select count(submission_id) from id_submission_detail where submission_date=current_date");
	$error_message .= "* The total number of today's submission has reached the maximum number of submission per day. <br>\n" if ($cur_daily_count >= $max_daily_submission);
	$cur_daily_size = db_select($dbh,"select sum(filesize) from id_submission_detail where submission_date=current_date");
	$error_message .= "* The total size of today's submission has reached the maximum size of submission per day. <br>\n" if ($cur_daily_size >= $max_daily_submission_size);
	if (my_defined($error_message)) 
	{
		unlink "/tmp/$temp_file.*";
		$error_message = "<h2>DoS Attack Warning</h2>\n$error_message<br><br><br><br>\n<a href=\"upload.cgi\">Go back to Upload screen</a><br><br>\n";
		error_idst ($query,$error_message);
	}
}


