#!/usr/local/bin/perl -

use lib '/export/home/mlee/RELEASE/';
use CGI;
use IETF_UTIL;
use IETF_DBUTIL;

my $cwd = `pwd`;
my $warnning_msg = "";
chomp($cwd);
$_ = $cwd;
$devel = "";
if (/devel/) {
   $ENV{"DBPATH"} = "/export/home/mlee/database";
   $ENV{"DBNAME"} = "testdb";
   $devel = "devel/";
} else {
   $ENV{"DBPATH"} = "/usr/informix/databases";
   $ENV{"DBNAME"} = "people";
}
if (defined($ENV{HTTP_USER_AGENT})) {
   my $user_agent = $ENV{HTTP_USER_AGENT};
   @version_temp = split ' ',$user_agent;
   $browser_version = $version_temp[0];
} else {
   $browser_version = "Unknown Version";
}
my $q = new CGI;
$program_name = "request.cgi";

$fColor = "7DC189";
$sColor = "CFE1CC";
$menu_fColor = "F8D6F8";
$menu_sColor = "E2AFE2";
########## End Pre Populate Option lists ###################
$table_header = qq{<table cellpadding="1" cellspacing="0" border="1" width="800">
};
$form_header = qq{<form action="$program_name" method="POST" name="form1">
};
$html_top = qq{
<html>
<HEAD><TITLE>IESG ID Tracker version control-- $browser_version</title>
<STYLE TYPE="text/css">
<!--

	  TD {text-decoration: none; color: #000000; font: 10pt arial;} 
	  A:Link {color: #0000ff; text-decoration:underline}
	  A:Hover {color: #ff0000; text-decoration:underline}
      A:visited {color: #0000ff; text-decoration:underline}
	  #largefont {font-weight: bold; color: #000000; font: 16pt arial}
	  #largefont_red {font-weight: bold; color: #ff0000; font: 16pt arial}
-->
</STYLE>

</head>
<body link="blue" vlink="blue">
$warnning_msg
};
$html_bottom = qq{
</body>
</html>
};

$html_body = get_html_body($q);

print <<END_HTML;
Content-type: text/html
$html_top
$html_body
$html_bottom
END_HTML




sub get_html_body {
   my $q = shift;
   my $html_txt = qq {
   <h2>IESG DraftTracker Version Control and Requests Status</h2>
   <h3>Requests</h3>
   <a href="#version">Go To Version Control</a><br>
   $table_header
   <tr>
   <th>Description</th><th>Requested By</th><th>Request Date</th><th>Current Version</th><th>Status</th>
   </tr>
   };
   my @List = db_select_multiple("select a.done_flag,a.id,a.desc,b.first_name,b.last_name,a.request_date,a.cur_version,a.status from dt_request a,iesg_login b where a.request_by = b.id order by a.done_flag, a.request_date DESC");
   for $array_ref (@List) {
      my ($done_flag,$id,$desc,$request_by_f,$request_by_l,$request_date,$cur_version,$status) = @$array_ref;
	  $desc = rm_tr($desc);
	  $status = rm_tr($status);
	  $request_by_f = rm_tr($request_by_f);
	  $request_by_l = rm_tr($request_by_l);
	  $html_txt .= qq {
	  $form_header
	  <input type="hidden" name="command" value="update">
	  <input type="hidden" name="req_id" value="$id">
	  <tr>
	  <td>$desc</td><td>$request_by_f $request_by_l</td><td>$request_date</td><td>$cur_version</td><td>$status</td>
	  </tr>
	  </form>
	  };
   }

   $html_txt .= qq {
   </table>
   <p>
   <a href="#request">Go To Requests</a>
   <a name="version"></a>
   <h3>Version Control</h3>
   $table_header
   <tr>
   <th>Version</th><th>New Features</th><th>Deployed Date</th>
   </tr>
   <tr valign="top">
   <td>3.2</td>
   <td>
1. The tool will notify AD when a comment added to the draft<br><br>
2. ADs' full names are replaced by their login names<br><br>
3. New button "assign to me"<br><br>
4. RFCs and IDs are combined in the search result list in case of following search criteria are not defined:<br>
<dd><li> Group Acronym
<dd><li> Area Acronym
<dd><li> Status<br><br>
5. Search result list is in alphabetical order within states<br><br>
6. All search fields values get carried over to result page<br><br>
7. Some java scripts are rewritten in CGI script so a non-java browser can handle the process with any critical error.<br><br>
   </td>
   <td>5/3/02</td>
   </tr>
   <tr valign="top">
   <td>3.1</td>
   <td>
1. IESG can set an area acronym for indivisual submissions.<br><br>
2. Search on individual submissions as well when "search by area acronym"<br><br>
3. Automatically enter a note into the history whenever an ID being tracked is updated<br><br>
4. The search form rearranged to reduce the height of the form, so more space can be provided to the result list<br><br>
5. A link created to display states tables with possible next states.<br><br>
6. The tool now detects an invalid WG acronym and displays proper error message.<br><br>
7. When a ballot avaliable, the tool displays "[Open Ballot]" text as a hyper link to the actual ballot file.<br><br>
8. ALL changes to an AD's IDs not made by that AD are now emailed to the AD when the change is made.<br><br>
9. New state "In WG" added. Any draft belong to this state will not show on public web page.<br><br>
   </td>
   <td>4/26/02</td>
   </tr>
   <tr valign="top">
   <td>3.0</td>
   <td>
1. New features added for IETF Secretariat<br>
<dd>-Agendas Management
<dd>-Proposed Working Groups Management<br><br>
2. States will be converted to "Summarized Status" for IESG internal web page only by a system.<br><br>
3. No draft can be removed from database by an user
   </td>
   <td>4/10/02</td>
   </tr>
   <tr valign="top">
   <td>2.5</td>
   <td>
1. When adding a draft, the matching function can automatically drop
"-NN.txt" to allow cut and paste of draft names.<br><br>
 
2. New states added: "request rejected", "discuss fix received", and "discusses cleared, wait for approval".<br><br>

3. Display draft's intended status on search result list.<br><br>
   </td>
   <td>3/29/02</td>
   </tr>
   <tr valign="top">
   <td>2.4</td>
   <td>
1. In the list of draft, the name of draft is now a link to actual text.<br><br>

2. In the View Draft page, one can change the Intended Status value.<br><br>

3. The tool searches "Requested draft"
   </td>
   <td>3/25/02</td>
   </tr>
   <tr valign="top">
   <td>2.3</td>
   <td>
1. In search result list, "Assigned To" replaced "Marked By" field.<br><br>

2. In View ID page, "Marked By" field added.<br><br>

3. New Date format -- "YYYY-MM-DD".<br><br>

4. The main expansion in this version is <b>Comapatibility with MySQL DB engine.</b><br>
All the ENV variables and MySQL version of SQL statments have been implemented.<br>
The site has been tested in LINUX platform with Apache httpd server version 2.0.32 beta and
MySQL version 3.23<BR>
   </td>
   <td>3/13/02</td>
   </tr>
   <tr valign="top">
   <td>2.2</td>
   <td>
1. Each draft's intended Status is displayed in view draft page.<br><br>

2. New Search Criteria -- "Assigned To"<br><br>

3. New Search Criteria -- "Area Acronym"<br><br>

4. In Search Criteria, radio fields "ID" and "RFC" has been removed.<br>
One just need to fill in either Filename to search from IDs or RFC number to search from RFCs.<br>
If both fields left blank, search will perform on both criteria.<br><br>
   </td>
   <td>3/5/02</td>
   </tr>
   <tr valign="top">
   <td>2.1</td>
   <td>
1. You can change "private/public" field of comment if you are the owner
of the comment.<br><br>

2. You can "ungroup" any actions. -- In View Draft page, you will see
the button "Separate from Action" if the selected draft has action
group.<br><br>

3. You can add active draft to the current actions -- Previous version
displayed "EXIST" text instead of "Add" button if the draft is already
active.  In new version, you won't see "EXIST" text if you're trying to
add an action, instead you can click "Add to Action" button.  If select
draft is active, the application directly add it to the current action
group and displays the "View Draft" page of newly added draft.
Otherwise (if not active), you will need to enter additional information
(just like add new draft).<br><br>

4. If you're trying to insert a comment larger than 256 character, a
alert message will pop up and won't process the request. A later version
will be able to accept a comment in any length.<br><br>

5. In search criteria, "Responsible" field is now a combination of
"select" and "text" field. If you click on the text field, any previous
string will be removed and you'll need to retype a string.  If you
select an option from the select field, the text field value will
changed to the selected value.  The DB will take a value from text field
for further process.

   
   </td>
   <td>3/1/02</td>
   </tr>
   </table>
   <a href="#request">Go To Requests</a><br>
   <a href="#version">Go To Version Control</a>
   };
   
   return $html_txt;
}
