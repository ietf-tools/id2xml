<?php
/*******************************************************************************************************************
* Script Name : create_proceeding_final.php
* Author Name : Priyanka Narkar
* Date        : 2010/01/24
* Description : create_proceeding_final.php script generates the final Proceedings in the HTML format
* 1) The script requires certail folders such as CSS for stylesheets(ietf.css, ietf2.css, ietf3.css , ietf4.css)
* 2) javascript-> for ietf.js
* 3) images folder -> for various logos
* 4) It uses the HTML header and footer files proceeding_header.html and proceeding_footer.html 
* 5) The proceedings are generated in the meeting folder which has the same name as the meeting number.
* 6) The script uses the constants from constants.php
* 7) The script generates the static page index.html with the final proceedings and all the other related pages in the HTML format.
/**************************************************************************************************************************/

umask(0);
/************GET THE COMMON CONTENTS********/ 

include('constants.php');
require_once('Connections/proceedings_conn.php'); 

/*NEED TO CHANGE DATABASE NAMES*/
#mysql_select_db("ietf", $proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);


/*GET THE MEETING NUMBER*/
$meeting_number = $_POST['hdn_meeting_number'];


/*Get the dir name*/

$query_dir_name="SELECT dir_name from proceedings where meeting_num=$meeting_number";
$recordset_dir_name = mysql_query($query_dir_name) or die(mysql_error());
$row_dir_name = mysql_fetch_assoc($recordset_dir_name);
$dir_name = $row_dir_name['dir_name'];

/*Get the Final proceeding header */
$header_source = fopen($PROCEEDING_HEADER, 'r');  
if (!$header_source) {
echo "<strong>Unable to load $header_sourcepage</strong>";
exit();
}
$html_header = fread($header_source, filesize($PROCEEDING_HEADER));
fclose($header_source);


/*Get the Final proceeding footer */
$footer_source = fopen($PROCEEDING_FOOTER,'r');
if (!$footer_source) {
echo "<strong>Unable to load $footer_sourcepage</strong>";
exit();
}
$html_footer = fread($footer_source, filesize($PROCEEDING_FOOTER));
	

session_start();

// this sets variables in the session
$_SESSION['MEETING_NUMBER']=$meeting_number;
$_SESSION['PROCEEDINGS_CONN']=$proceedings_conn;
$_SESSION['HTML_HEADER']=$html_header;
$_SESSION['HTML_FOOTER']=$html_footer; 
$_SESSION['PROCEEDING_DIR'] = $PROCEEDING_DIR;
$_SESSION['HOST_PROCEEDING']= $HOST_PROCEEDING;
$_SESSION['WEB_PATH']= $WEB_PATH;
$_SESSION['WG_DESCRIPTION']= $WG_DESCRIPTION;
$_SESSION['DIR_PROCEEDING'] = $DIR_PROCEEDING;
$_SESSION['HOST_NAME'] = $HOST_NAME;
$_SESSION['DATABASE'] = $DATABASE;
$_SESSION['DATABASE_AMS'] = $DATABASE_AMS;

/*******END OF COMMON THINGS*********/

/*BEGIN SCRIPT FOR acknowledgement.html generation*/

$acknoledgement_mainContent = genAcknowledgementBody();
/*Write to the Acknowledgement file */
$acknowledgement_html=fopen($PROCEEDING_DIR."/".$meeting_number."/acknowledgement.html",'w');



if (! $acknowledgement_html) die("Error opening file");
fwrite($acknowledgement_html,$html_header);
fwrite($acknowledgement_html,$acknoledgement_mainContent);
fwrite($acknowledgement_html,$html_footer);
fclose($acknowledgement_html);

header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/acknowledgement.html');

/*END SCRIPT FOR acknowledgement.html generation*/
/*BEGIN OF FUNCTION genAcknowledgementBody*/
/**********************************************************************************************************
* Function name : genAcknowledgementBody()
* Description   : Generates HTML Body for the Acknowledgement page
**********************************************************************************************************/

function genAcknowledgementBody(){
/*get the session variable*/
$pass_meeting_number = $_SESSION['MEETING_NUMBER'];
$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
$DATABASE = $_SESSION['DATABASE'];
$DATABASE_AMS = $_SESSION['DATABASE_AMS']; 


/*NEED TO CHANGE DATABASE NAMES*/
#mysql_select_db("ietf_ams", $proceedings_conn);
mysql_select_db($DATABASE_AMS, $proceedings_conn);


$acknowledgement_text = "";
$acknowledgement_text .= "<td id=\"content1\"><div id=\"content2\"><p class=\"ptitle\">IETF"." ".$pass_meeting_number." "."Proceedings </p>";
$acknowledgement_text .= formatMenu();
$acknowledgement_text .= "<h2>Acknowledgements</h2>";

/*Get the Host name from the table*/
$query_host_info = "SELECT host_id, host_name from host_information where meeting_number = $pass_meeting_number";
$recordset_host_info = mysql_query($query_host_info,$proceedings_conn) or die(mysql_error());
$num_of_host = mysql_num_rows($recordset_host_info);


$acknowledgement_text .= "<h3>Host: </h3>";

if ($num_of_host > 0)
{
	$acknowledgement_text .= "<ul>";
	while ($row_host_information = mysql_fetch_assoc($recordset_host_info))
	{
		$host_id = $row_host_information['host_id'];
		$host_name = $row_host_information['host_name'];
		$acknowledgement_text .= "<li>$host_name</li>";
	}
	$acknowledgement_text .= "</ul>";
}
else
{
	 $acknowledgement_text .= " "; 
}


/*Get the Sponsor from the table*/
$query_sponsor_info = "SELECT sponsor_f_name, sponsor_l_name, status from sponsors where meeting_number = $pass_meeting_number";
$recordset_sponsor_info = mysql_query($query_sponsor_info,$proceedings_conn) or die(mysql_error());
$num_of_sponsor = mysql_num_rows($recordset_sponsor_info);

$sponsor_text = "";
if ($num_of_sponsor > 0)
{  
$first_time_green= 0;
$first_time_half = 0;

	while ($row_sponsor_information = mysql_fetch_assoc($recordset_sponsor_info))
	{
		$sponsor_text_head = "";
		$sponsor_f_name = $row_sponsor_information['sponsor_f_name'];
		$sponsor_l_name = $row_sponsor_information['sponsor_l_name'];
		$status = $row_sponsor_information['status'];
		
		if ($status == 1 && $first_time_green == 0)
		{
#			$status_verbal = "Green dot";
			$sponsor_text_head .= "<h3>Green dot Sponsors</h3><ul>"; 
			$first_time_green = 1;
		}
	
		if ($status == 2 && $first_time_half == 0)
		{
#			$status_verbal = "Half dot";
			$sponsor_text_head .= "</ul><h3>Half dot Sponsors</h3><ul>"; 
			$first_time_half = 1;
		}
		$acknowledgement_text .= $sponsor_text_head ;
		$acknowledgement_text .= "<li>$sponsor_f_name $sponsor_l_name</li>";
	}
	$acknowledgement_text .= "</ul>";
}
else
{
	$acknowledgement_text .= "";
}





/*Get the NOC contractor from the table*/       
$query_noc_info = "SELECT noc_id, noc_name from noc_contractor where meeting_number = $pass_meeting_number";
$recordset_noc_info = mysql_query($query_noc_info,$proceedings_conn) or die(mysql_error());
$num_of_noc = mysql_num_rows($recordset_noc_info);


if ($num_of_noc > 0)
{
	$acknowledgement_text .= "<h3>NOC Contractor: </h3>";
	$acknowledgement_text .= "<ul>";
	while ($row_noc_information = mysql_fetch_assoc($recordset_noc_info))
	{
		$noc_id = $row_noc_information['noc_id'];
		$noc_name = $row_noc_information['noc_name'];
		$acknowledgement_text .= "<li>$noc_name</li>";
	}
	$acknowledgement_text .= "</ul>";
}
else
{
	 $acknowledgement_text .= " "; 
}



#$acknowledgement_text .= "<h3>Network Operations: </h3>";
$acknowledgement_text .= "<h3>People: </h3>";


/*Now get the Network operations people information from people table for the current meeting */

#$query_people = "SELECT people_f_name, people_l_name, company_name from people where meeting_number = $pass_meeting_number and host_id = $host_id";
$query_people = "SELECT people_f_name, people_l_name, company_name from people where meeting_number = $pass_meeting_number";
$recordset_people = mysql_query($query_people,$proceedings_conn) or die(mysql_error());
$num_of_people = mysql_num_rows($recordset_people);
if ($num_of_people > 0)
{
	$acknowledgement_text .= "<ul>";
	while($row_people = mysql_fetch_assoc($recordset_people))
	{
		$people_fname = $row_people['people_f_name']; 
		$people_lname = $row_people['people_l_name'];
		$people_company = $row_people['company_name'];
		
                if ($people_company != ''){
                    $acknowledgement_text .="<li>$people_fname $people_lname, $people_company</li>";
                }
                else
                {
                    $acknowledgement_text .="<li>$people_fname $people_lname</li>";
                }

	}
	
	$acknowledgement_text .= "</ul>";
}
else
{
	$acknowledgement_text .= " ";
}


/*Get the Volunteers list*/
/*Changed as per request by Ray on 05/04/2011*/

/*$acknowledgement_text .= "<h3>Volunteers: </h3>";
#$query_volunteer = "SELECT volunteer_f_name, volunteer_l_name, company_name from volunteer where meeting_number = $pass_meeting_number and host_id = $host_id";
$query_volunteer = "SELECT volunteer_f_name, volunteer_l_name, company_name from volunteer where meeting_number = $pass_meeting_number";
$recordset_volunteer = mysql_query($query_volunteer,$proceedings_conn) or die(mysql_error());
$num_of_volunteer = mysql_num_rows($recordset_volunteer);
if ($num_of_volunteer > 0)
{
	$acknowledgement_text .= "<ul>";
	while($row_volunteer = mysql_fetch_assoc($recordset_volunteer))
	{
		$volunteer_fname = $row_volunteer['volunteer_f_name']; 
		$volunteer_lname = $row_volunteer['volunteer_l_name'];
		$volunteer_company = $row_volunteer['company_name'];
		
		$acknowledgement_text .="<li>$volunteer_fname $volunteer_lname, $volunteer_company</li>";
	}
	
	$acknowledgement_text .= "</ul>";
}
else
{
	$acknowledgement_text .= " ";
}
*/

$indvidual_ack_text = "";
$individual_first_record = "1";/*Flag set to identify the first record of voluteer under individual company name*/
$ietf_ack_text = "<h3>IETF Volunteers:</h3>";
$last_company_name = "";
$query_volunteer = "SELECT volunteer_f_name, volunteer_l_name, company_name, is_ietf from volunteer where meeting_number = '$pass_meeting_number' order by company_name";
$recordset_volunteer = mysql_query($query_volunteer,$proceedings_conn) or die(mysql_error());
$num_of_volunteer = mysql_num_rows($recordset_volunteer);
if ($num_of_volunteer > 0)
{
#$indvidual_ack_text = "<ul>";
	$ietf_ack_text .= "<ul>";
	while($row_volunteer = mysql_fetch_assoc($recordset_volunteer))
	{
		$volunteer_fname = $row_volunteer['volunteer_f_name']; 
		$volunteer_lname = $row_volunteer['volunteer_l_name'];
		$volunteer_company = $row_volunteer['company_name'];


		if ($row_volunteer['is_ietf']){
			$ietf_ack_text .= "<li>$volunteer_fname $volunteer_lname, $volunteer_company</li>";
		}else {
			if ($last_company_name != $volunteer_company){
				if (!($individual_first_record)){ 
					$individual_ack_text .= "</ul>"; /*If not the first record of voluteer under individual company name then only add*/
				}
				$individual_first_record = "0";	/*Undet the Flag set to identify the first record of voluteer under individual company name */
				$individual_ack_text .= "<h3>$volunteer_company Volunteers:</h3>";
				$individual_ack_text .= "<ul>";
				$individual_ack_text .="<li>$volunteer_fname $volunteer_lname</li>";
		        }else{
				$individual_ack_text .="<li>$volunteer_fname $volunteer_lname</li>";
			} 
		}
		$last_company_name = $volunteer_company;	
	}
	$ietf_ack_text .= "</ul>";
	$individual_ack_text .= "</ul>";
        $acknowledgement_text .= $individual_ack_text;
        $acknowledgement_text .= $ietf_ack_text;

}
else
{
	$acknowledgement_text .= " ";
}


/*Now get the AMS Staff*/
$acknowledgement_text .= "<h3>AMS Staff: </h3>";


/*Change the database name*/
#mysql_select_db("ietf", $proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);


$query_ams_staff = "SELECT first_name, last_name FROM iesg_login WHERE user_level =0 ORDER BY last_name";

$recordset_ams_staff = mysql_query($query_ams_staff,$proceedings_conn) or die(mysql_error());
$num_of_ams_staff = mysql_num_rows($recordset_ams_staff);
if ($num_of_ams_staff > 0)
{
	$acknowledgement_text .= "<ul>";
	while($row_ams_staff = mysql_fetch_assoc($recordset_ams_staff))
	{
		$ams_staff_fname = $row_ams_staff['first_name']; 
		$ams_staff_lname = $row_ams_staff['last_name'];
#		$acknowledgement_text .="<li>$ams_staff_fname $ams_staff_lname</li>";
	        if (($ams_staff_fname != 'Henrik') AND ($ams_staff_lname != 'Levkowetz'))
                {
                        $acknowledgement_text .="<li>$ams_staff_fname $ams_staff_lname</li>";
                
		}
	}
	
	$acknowledgement_text .= "</ul>";
}
else
{
	$acknowledgement_text .= " ";
}



$acknowledgement_text .= "</div></td></tr>";
return $acknowledgement_text;
}
/*END OF FUNCTION genAcknowledgementBody*/

/*BEGIN SCRIPT FOR overview.html generation*/
$overview_mainContent = getOverviewBody();
/*Write to the Overview file */

$overview_html=fopen($PROCEEDING_DIR."/".$meeting_number."/overview.html",'w');

if (! $overview_html) die("Error opening file");
fwrite($overview_html,$html_header);
fwrite($overview_html,$overview_mainContent);
fwrite($overview_html,$html_footer);
fclose($overview_html);

header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/overview.html');

/*END SCRIPT FOR overview.html generation*/
/*BEGIN OF FUNCTION genOverviewBody*/
/**********************************************************************************************************
* Function name : getOverviewBody()
* Description   : Generates HTML Body for the Overview page
**********************************************************************************************************/
function getOverviewBody(){
// Gets the value from the Session
$pass_meeting_number = $_SESSION['MEETING_NUMBER'];
$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
$DATABASE = $_SESSION['DATABASE'];
$DATABASE_AMS = $_SESSION['DATABASE_AMS']; 



/*NEED TO CHANGE DATABASE NAMES*/
#mysql_select_db("ietf", $proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);

/* GET THE HTML TEXT VALUE FROM GENERAL INFO TABLE*/

/*OVERVIEW1*/
$query_overview1 = "select info_text from general_info where info_name= 'overview1'";
$recordset_overview1 = mysql_query($query_overview1, $proceedings_conn) or die(mysql_error());
$row_overview1 = mysql_fetch_assoc($recordset_overview1);
$text_val1 = (html_entity_decode($row_overview1['info_text'])); 

/*OVERVIEW2*/
$query_overview2 = "select info_text from general_info where info_name= 'overview2'";
$recordset_overview2 = mysql_query($query_overview2, $proceedings_conn) or die(mysql_error());
$row_overview2 = mysql_fetch_assoc($recordset_overview2);
$text_val2 = (html_entity_decode($row_overview2['info_text'])); 

/*IETF CHAIR*/
$query_ietf_chair = "SELECT first_name, last_name, person_or_org_tag FROM person_or_org_info WHERE person_or_org_tag IN(SELECT person_or_org_tag FROM chairs WHERE chair_name = 'IETF')";
$recordset_ietf_chair = mysql_query($query_ietf_chair,$proceedings_conn) or die(mysql_error());
$row_ietf_chair = mysql_fetch_assoc($recordset_ietf_chair);
$ietf_chair = $row_ietf_chair['first_name']." ".$row_ietf_chair['last_name'];
$person_or_org_tag_chair = $row_ietf_chair['person_or_org_tag'];


/*OTHER iesg CHAIRS*/
$iesg_list = "";
$query_other_chairs = "SELECT first_name,last_name,person_or_org_tag from iesg_login where user_level=1 and person_or_org_tag <> $person_or_org_tag_chair and id <> 1 order by last_name";
$recordset_other_chairs = mysql_query($query_other_chairs ,$proceedings_conn) or die(mysql_error());
while ($row_other_chairs = mysql_fetch_assoc($recordset_other_chairs)) 
{
	$first_name = $row_other_chairs['first_name'];
	$last_name = $row_other_chairs['last_name'];
	$person_or_org_tag = $row_other_chairs['person_or_org_tag'];

	$query_iesg_area_name = "SELECT name from acronym a, area_directors b, areas c where b.person_or_org_tag= $person_or_org_tag and b.area_acronym_id=acronym_id and b.area_acronym_id=c.area_acronym_id	 and c.status_id=1";
	$recordset_iesg_area_name = mysql_query($query_iesg_area_name,$proceedings_conn) or die(mysql_error());
	$row_iesg_area_name = mysql_fetch_assoc($recordset_iesg_area_name);
	$iesg_area_name = $row_iesg_area_name['name'];
	$iesg_area_name = str_replace("Area","",$iesg_area_name);
	$other_email = get_email($person_or_org_tag,0);
    $iesg_list .= "<tr><td valign=\"Top\" width=\"191\">$first_name $last_name</td><td valign=\"Top\" width=\"204\">$iesg_area_name</td><td valign=\"Top\" width=\"216\">$other_email</td></tr>";

}




$overview_text = "";
$overview_text .= "<td id=\"content1\"><div id=\"content2\"><p class=\"ptitle\">IETF"." ".$pass_meeting_number." "."Proceedings </p>";
$overview_text .= formatMenu();
$overview_text .= "<h2>IETF Overview</h2></h2>";
#$overview_text .= $text_val1;


$overview_text .="<p>The Internet Engineering Task Force (IETF) provides a forum for working groups to coordinate technical development of new protocols. Its most important function is the development and selection of standards within the Internet protocol suite.</p>";

$overview_text .= "<p>The IETF began in January 1986 as a forum for technical coordination by contractors for the then US Defense Advanced Research Projects Agency (DARPA), working on the ARPANET, US Defense Data Network (DDN), and the Internet core gateway system. Since that time, the IETF has grown into a large open international community of network designers, operators, vendors, and researchers concerned with the evolution of the Internet architecture and the smooth operation of the Internet.</p>";

$overview_text .="<p>The IETF mission includes:</p>";

$overview_text .="<ul><li>Identifying and proposing solutions to pressing operational and technical problems in the Internet </li><li>Specifying the development or usage of protocols and the near-term architecture, to solve technical problems for the Internet </li><li>Facilitating technology transfer from the Internet Research Task Force (IRTF) to the wider Internet community;and</li><li>Providing a forum for the exchange of relevant information within the Internet community between vendors, users, researchers, agency contractors, and network managers.</li></ul>";

$overview_text .="<p>Technical activities in the IETF are addressed within working groups. All working groups are organized roughly by function into seven areas. Each area is led by one or more Area Directors who have primary responsibility for that one area of IETF activity. Together with the Chair of the IETF/IESG, these Area Directors comprise the Internet Engineering Steering Group (IESG).</p>";

$overview_text .= "<p><table cellspacing=\"1\" cellpadding=\"1\" border=\"1\">";
#$overview_text .= "<tbody><tr><td valign=\"Top\" width=\"191\"><p align=\"Left\">Name</p></td><td valign=\"Top\" width=\"204\"><p align=\"Left\">Area</p></td><td valign=\"Top\" width=\"216\"><p align=\"Left\">Email</p></td></tr><tr><td valign=\"Top\" width=\"191\"><p align=\"Left\">";
#$overview_text .= $ietf_chair."</p></td><td valign=\"Top\" width=\"204\"><p align=\"Left\">IETF Chair</p></td><td valign=\"Top\" width=\"216\"><p align=\"Left\">chair@ietf.org</p></td></tr>";
$overview_text .= "<tbody><tr><td valign=\"Top\" width=\"191\">Name</td><td valign=\"Top\" width=\"204\">Area</td><td valign=\"Top\" width=\"216\">Email</td></tr><tr><td valign=\"Top\" width=\"191\">";

$overview_text .= $ietf_chair."</td><td valign=\"Top\" width=\"204\">IETF Chair</td><td valign=\"Top\" width=\"216\">chair@ietf.org</td></tr>";
$overview_text .= $iesg_list;
$overview_text .= "</table>";

#$overview_text .= $text_val2;


#$overview_text .="<p>Liaison and ex-office members include: </p><p><table border=\"0\"><tbody><tr><td valign=\"Top\" width=\"216\"><p align=\"Left\">Olaf Kolkman</p></td><td valign=\"Top\" width=\"216\"><p align=\"Left\">IAB Chair</p></td><td valign=\"Top\" width=\"216\"><p align=\"Left\"><iab-chair@iab.org></p></td></tr><tr><td valign=\"Top\" width=\"216\"><p align=\"Left\">Loa Andersson</p></td><td valign=\"Top\" width=\"216\"><p align=\"Left\">IAB Liaison</p></td><td valign=\"Top\" width=\"216\"><p align=\"Left\"><loa@pi.nu></p></td></tr><tr><td valign=\"Top\" width=\"216\"><p align=\"Left\">Michelle Cotton</p></td><td valign=\"Top\" width=\"216\"><p align=\"Left\">IANA Liaison</p></td><td valign=\"Top\" width=\"216\"><p align=\"Left\"><iana@iana.org></p></td></tr><tr><td valign=\"Top\" width=\"216\"><p align=\"Left\">Sandy Ginoza</p></td><td valign=\"Top\" width=\"216\"><p align=\"Left\">RFC Editor Liaison</p></td><td valign=\"Top\" width=\"216\"><p align=\"Left\"><rfc-editor@rfc-editor.org></p></td></tr><tr><td valign=\"Top\" width=\"216\"><p align=\"Left\">Alexa Morris</p></td><td valign=\"Top\" width=\"216\"><p align=\"Left\">IETF Secretariat Liaison</p></td><td valign=\"Top\" width=\"216\"><p align=\"Left\"><exec-director@ietf.org></p></td></tr></tbody></table>";

$overview_text .="<p>Liaison and ex-officio members include: </p><p><table border=\"1\"><tbody><tr><td valign=\"Top\" width=\"216\">Olaf Kolkman</td><td valign=\"Top\" width=\"216\">IAB Chair</td><td valign=\"Top\" width=\"216\">iab-chair@iab.org</td></tr><tr><td valign=\"Top\" width=\"216\">Danny McPherson</td><td valign=\"Top\" width=\"216\">IAB Liaison</td><td valign=\"Top\" width=\"216\">loa@pi.nu</td></tr><tr><td valign=\"Top\" width=\"216\">Michelle Cotton</td><td valign=\"Top\" width=\"216\">IANA Liaison</p></td><td valign=\"Top\" width=\"216\">iana@iana.org</td></tr><tr><td valign=\"Top\" width=\"216\">Sandy Ginoza</td><td valign=\"Top\" width=\"216\">RFC Editor Liaison</td><td valign=\"Top\" width=\"216\">rfc-editor@rfc-editor.org</td></tr><tr><td valign=\"Top\" width=\"216\">Alexa Morris</td><td valign=\"Top\" width=\"216\">IETF Secretariat Liaison</td><td valign=\"Top\" width=\"216\">exec-director@ietf.org</td></tr></tbody></table>";

$overview_text .= "<p>The IETF has a Secretariat, which is managed by Association Management Solutions, LLC (AMS) in Fremont, California.";
$overview_text .= "The IETF Executive Director is Alexa Morris <a href=\"mailto:exec-director@ietf.org\">(exec-director@ietf.org)</a>.</p><br>Other personnel that provide full-time support to the Secretariat include:<br><br>";

#$overview_text .="<table border=\"0\"><tbody><tr><td valign=\"Top\" width=\"264\"><p>Senior Meeting Planner</p></td><td valign=\"Top\" width=\"180\"><p>Marcia Beaulieu  </p></td></tr><tr>   <td valign=\"Top\" width=\"264\"><p>Meeting Coordinator</p></td><td valign=\"Top\" width=\"180\"><p>Wanda Lo </p></td></tr><tr><td valign=\"Top\" width=\"264\"><p>Meeting Registrar</p></td><td valign=\"Top\" width=\"180\"><p>Stephanie McCammon</p></td></tr><tr><td valign=\"Top\" width=\"264\"><p>Project Manager </p></td><td valign=\"Top\" width=\"180\"><p>Cindy Morgan </p></td>   </tr><tr><td valign=\"Top\" width=\"264\"><p>Project Manager</p></td><td valign=\"Top\" width=\"180\"><p>Amy Vezza  </p></td></tr></tbody></table></p>";



$overview_text .="<table border=\"1\"><tbody><tr><td valign=\"Top\" width=\"264\">Senior Meeting Planner</td><td valign=\"Top\" width=\"180\">Marcia Beaulieu</td></tr><tr><td valign=\"Top\" width=\"264\">Meeting Coordinator</td><td valign=\"Top\" width=\"180\">Wanda Lo </td></tr><tr><td valign=\"Top\" width=\"264\">Meeting Registrar</td><td valign=\"Top\" width=\"180\">Stephanie McCammon</td></tr><tr><td valign=\"Top\" width=\"264\">Project Manager</td><td valign=\"Top\" width=\"180\">Cindy Morgan</td></tr><tr><td valign=\"Top\" width=\"264\">Project Manager</td><td valign=\"Top\" width=\"180\">Amy Vezza</td></tr></tbody></table></p>";

$overview_text .="<p>To contact the Secretariat, please refer to the addresses and URLs provided on the <a href=\"http://www.ietf.org/secretariat.html\">IETF Secretariat</a> Web page. </p>";

$overview_text .="<p>The IETF also has a general Administrative Support Activity headed by the IETF Administrative Director, Ray Pelletier <a href=\"mailto:iad@ietf.org\">iad@ietf.org</a></p>
<p>The working groups conduct their business during the tri-annual IETF meetings, at interim working group meetings, and via electronic mail on mailing lists established for each group. The tri-annual IETF meetings are 4.5 days in duration, and consist of working group sessions, training sessions, and plenary sessions.  The plenary sessions include technical presentations, status reports, and an open IESG meeting.</p><p>Following each meeting, the IETF Secretariat publishes meeting proceedings, which contain reports from all of the groups that met, as well as presentation slides, where available.  The proceedings also include a summary of the standards-related activities that took place since the previous IETF meeting.</p><p>Meeting minutes, working group charters (including information about the working group mailing lists), and general information on current IETF activities are available on the IETF Web site at <a href=\"http://www.ietf.org\">http://www.ietf.org</a>.</p></font>";

$overview_text .= "</div></td></tr>";
return $overview_text;
}
/*END OF FUNCTION genOverviewBody*/
/*BEGIN SCRIPT FOR progress-report.html generation*/

$progrep_mainContent = genProgRepBody();

/*Write to the Acknowledgement file */
$progrep_html=fopen($PROCEEDING_DIR."/".$meeting_number."/progress-report.html",'w');


if (! $progrep_html) die("Error opening file");
fwrite($progrep_html,$html_header);
fwrite($progrep_html,$progrep_mainContent);
fwrite($progrep_html,$html_footer);
fclose($progrep_html);

header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/progress-report.html');

/*END SCRIPT FOR progress-report.html.html generation*/
/*BEGIN OF FUNCTION genAcknowledgementBody*/
/**********************************************************************************************************
* Function name : genProgRepBody()
* Description   : Generates HTML Body for the Progress report page
**********************************************************************************************************/
#function genProgRepBody($meeting_number,$proceedings_conn)
function genProgRepBody()
{

// Gets the value from the Session
$meeting_number = $_SESSION['MEETING_NUMBER'];
$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
$DATABASE = $_SESSION['DATABASE'];
$DATABASE_AMS = $_SESSION['DATABASE_AMS']; 

#mysql_select_db("ietf", $proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);


/*Get the Meeting start date and end date*/

$query_progress_report = "SELECT pr_from_date,pr_to_date from proceedings where meeting_num=$meeting_number";
$recordset_progress_report = mysql_query($query_progress_report, $proceedings_conn) or die(mysql_error());
$row_progress_report = mysql_fetch_assoc($recordset_progress_report);

$pr_from_date = $row_progress_report['pr_from_date']; 
$pr_to_date = $row_progress_report['pr_to_date']; 


$start_date = $row_progress_report['pr_from_date']; 
$end_date = $row_progress_report['pr_to_date']; 

/*Format the start date in proper format*/
$format = "dFy";
$start_date = formatDate($start_date,$format);

/*Format the end date in proper format*/
$format = "dFy";
$end_date = formatDate($end_date,$format);

/*GET THE VARIOUS COUNTS*/
#  IESG Protocol Action
$query_protocol_count = "SELECT count(id_document_tag) as COUNT from internet_drafts where b_approve_date >= '$pr_from_date' and b_approve_date <= '$pr_to_date' and b_approve_date is not null and b_approve_date <> ''";
$recordset_protocol_count = mysql_query($query_protocol_count, $proceedings_conn) or die(mysql_error());
$row_protocol_count = mysql_fetch_assoc($recordset_protocol_count);
$protocol_count = $row_protocol_count['COUNT'];


#IESG Last Call Issued to the IETF
$query_lastcall_count = "SELECT count(id_document_tag) as COUNT from internet_drafts where lc_sent_date >= '$pr_from_date' and lc_sent_date <= '$pr_to_date' and lc_sent_date is not null and lc_sent_date <> ''";
$recordset_lastcall_count = mysql_query($query_lastcall_count, $proceedings_conn) or die(mysql_error());
$row_lastcall_count = mysql_fetch_assoc($recordset_lastcall_count);
$lastcall_count = $row_lastcall_count['COUNT'];


#Internet-Drafts Actions
$query_internetdraft_count="select count(id_document_tag) as COUNT from internet_drafts where revision_date >= '$pr_from_date' and revision_date <= '$pr_to_date' and revision_date is not null and revision_date <> '' and filename not like 'rfc%'";
$recordset_internetdraft_count = mysql_query($query_internetdraft_count, $proceedings_conn) or die(mysql_error());
$row_internetdraft_count = mysql_fetch_assoc($recordset_internetdraft_count);
$internetdraft_count = $row_internetdraft_count['COUNT'];

#New Working Groups
$query_newworkgrp_count = "SELECT count(group_acronym_id) as COUNT from groups_ietf where start_date >= '$pr_from_date' and start_date <= '$pr_to_date' and start_date is not null and start_date <> '' and group_type_id = 1";
$recordset_newworkgrp_count = mysql_query($query_newworkgrp_count, $proceedings_conn) or die(mysql_error());
$row_newworkgrp_count = mysql_fetch_assoc($recordset_newworkgrp_count);
$newworkgrp_count = $row_newworkgrp_count['COUNT'];

/*GET THE NEW WORKING GROUPS NAMES*/
$group_text = "";
$query_new_workgroup ="SELECT acronym,name from groups_ietf, acronym where group_acronym_id = acronym_id and start_date >= '$pr_from_date' and start_date <= '$pr_to_date' and start_date is not null and start_date <> '' and group_type_id = 1";
$recordset_new_workgroup = mysql_query($query_new_workgroup, $proceedings_conn) or die(mysql_error());
$rowcount_new_workgroup = mysql_num_rows($recordset_new_workgroup);

while ($row_new_workgroup = mysql_fetch_assoc($recordset_new_workgroup)) 
{
	$group_acronym = $row_new_workgroup['acronym'];
	$group_name = $row_new_workgroup['name']; 
	$group_text .= "&nbsp;&nbsp;&nbsp;$group_name ($group_acronym)<br>";

}

#Concluded Working Groups
$query_concludeworkgrp_count = "SELECT count(group_acronym_id) as COUNT from groups_ietf where concluded_date >= '$pr_from_date' and concluded_date <= '$pr_to_date' and concluded_date is not null and concluded_date <> ''";

$recordset_concludeworkgrp_count = mysql_query($query_concludeworkgrp_count, $proceedings_conn) or die(mysql_error());
$rowcount_concludeworkgrp_count = mysql_num_rows($recordset_concludeworkgrp_count);
$row_concludeworkgrp_count = mysql_fetch_assoc($recordset_concludeworkgrp_count);
$concludeworkgrp_count = $row_concludeworkgrp_count['COUNT'];

/*GET THE CONCLUDEING WORKING GROUP TEXT*/

$concluded_group_text = "";
$query_concluded_workgroup = "SELECT acronym,name from groups_ietf, acronym where group_acronym_id = acronym_id and concluded_date >= '$pr_from_date' and concluded_date <= '$pr_to_date' and concluded_date is not null and concluded_date <> ''";

$recordset_concluded_workgroup = mysql_query($query_concluded_workgroup, $proceedings_conn) or die(mysql_error());
$rowcount_concluded_workgroup = mysql_num_rows($recordset_concluded_workgroup);

while ($row_concluded_workgroup = mysql_fetch_assoc($recordset_concluded_workgroup)) 
{
	$group_acronym = $row_concluded_workgroup['acronym'];
	$group_name = $row_concluded_workgroup['name']; 
	$concluded_group_text .= "&nbsp;&nbsp;&nbsp;$group_name ($group_acronym)<br>";

}

#RFC Produced
$query_rfcproduced_count  = "SELECT count(rfc_number) as COUNT from rfcs where rfc_published_date >= '$pr_from_date' and rfc_published_date <= '$pr_to_date' and rfc_published_date is not null and rfc_published_date <> ''";

$recordset_rfcproduced_count = mysql_query($query_rfcproduced_count, $proceedings_conn) or die(mysql_error());
$rowcount_rfcproduced_count = mysql_num_rows($recordset_rfcproduced_count);
$row_rfcproduced_count = mysql_fetch_assoc($recordset_rfcproduced_count);
$rfcproduced_count = $row_rfcproduced_count['COUNT'];

/*GET THE RFC PRODUCED GROUPS TEXT*/
$rfc_produced_text = "";
$rfc_produced_text .= "<table cellpadding=\"3\" cellspacing=\"2\" border=\"0\" width=\"100%\"><tbody>";

$status_array = array('','PS','DS','S ','E ','I ','B ','H ','N ');

$query_rfc_published = "SELECT rfc_number,status_id,group_acronym,rfc_published_date,rfc_name from rfcs where rfc_published_date >= '$pr_from_date' and rfc_published_date <= '$pr_to_date' and rfc_published_date is not null and rfc_published_date <> ''";

$recordset_rfc_published = mysql_query($query_rfc_published, $proceedings_conn) or die(mysql_error());

/*Initialize the count*/
$s_count = 0;
$bcp_count = 0;
$e_count = 0;
$i_count = 0;

while ($row_rfc_published = mysql_fetch_assoc($recordset_rfc_published)) 
{
    $rfc_number = $row_rfc_published['rfc_number'];
	$status_id = $row_rfc_published['status_id'];
	$group_acronym = $row_rfc_published['group_acronym'];
	$pDate = $row_rfc_published['rfc_published_date'];
	$rfc_name = $row_rfc_published['rfc_name'];

	/*Format the start date in proper format*/
	$format = "FY";
	$p_start_date = formatDate($pDate,$format);


    if ($status_id > 0 and $status_id <= 3) {
      $s_count++;
    } else if ($status_id == 4) {
      $e_count++;
    } else if ($status_id == 5) {
      $i_count++;
    } else if ($status_id == 6) {
      $bcp_count++;
    }
    $si = $status_array[$status_id];
    $group_acronym = "(".$group_acronym.")";

    $rfc_produced_text .= "<tr><td valign=\"middle\">";
	$rfc_produced_text .= "<a href=\"ftp://ftp.ietf.org/rfc/rfc".$rfc_number.".txt\" target=\"_blank\">RFC".$rfc_number."</a>";
	$rfc_produced_text .= "</td><td>".$si."</td><td>".$group_acronym."</td><td width=\"50\">".$p_start_date."</td><td>".$rfc_name."</td></tr>";
}
$rfc_produced_text .= "</table>\n";
$rfc_produced_text .= $s_count." Standards Track "."; ".$bcp_count." BCP"."; ".$e_count." Experimental"."; ".$i_count." Informational"."<br><br>";

/*FORM THE FINAL HTML FOR PROGRESS REPORT*/
$progrep_text = "";
$progrep_text .= "<td id=\"content1\"><div id=\"content2\"><p class=\"ptitle\">IETF"." ".$meeting_number." "."Proceedings </p>";
$progrep_text .= formatMenu();
$progrep_text .= "<h2>IETF Progress Report</h2>";

$progrep_text .="<h4>".$start_date." "."to"." ".$end_date."</h4>";
$progrep_text .= "&nbsp;&nbsp;&nbsp;".$protocol_count." "."IESG Protocol and Document Actions this period<br>";
$progrep_text .= "&nbsp;&nbsp;&nbsp;".$lastcall_count." "."IESG Last Calls issued to the IETF this period<br>";
$progrep_text .= "&nbsp;&nbsp;&nbsp;".$internetdraft_count." "."new or revised Internet-Drafts this period";
$progrep_text .= "<h4>".$newworkgrp_count." "." New Working Group(s) formed this period</h4>";
$progrep_text .= $group_text;
$progrep_text .= "<h4>".$concludeworkgrp_count." "." Working Group(s) concluded this period</h4>";
$progrep_text .= $concluded_group_text;
$progrep_text .= "<h4>".$rfcproduced_count." "." RFC(s) concluded this period</h4>";
$progrep_text .= $rfc_produced_text;
$progrep_text .= "</div></td></tr>";
return $progrep_text;
}
/*END OF FUNCTION genProgRepBody*/

/*BEGIN SCRIPT FOR agenda.html generation*/



/*WRITE THE TEXT AGENDA FIRST*/
$text_agendamanContent = genTextAgendaBody($dir_name);
$agenda_text_file=fopen($PROCEEDING_DIR."/".$meeting_number."/agenda.txt",'w');


if (! $agenda_text_file) die("Error opening file");
#fwrite($agenda_text,$html_header);
fwrite($agenda_text_file,$text_agendamanContent);
#fwrite($agenda_html,$html_footer);
fclose($agenda_text_file);

#header('Location: http://devp.amsl.com/proceedings/'.$meeting_number.'/agenda.text');
header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/agenda.text');


/*END OF TEXT AGENDA SCRIPT*/
$agenda_mainContent = genAgendaBody($dir_name);

/*Write to the Agenda file */
$agenda_html=fopen($PROCEEDING_DIR."/".$meeting_number."/agenda.html",'w');


if (! $agenda_html) die("Error opening file");
fwrite($agenda_html,$html_header);
fwrite($agenda_html,$agenda_mainContent);
fwrite($agenda_html,$html_footer);
fclose($agenda_html);

header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/agenda.html');

/*END SCRIPT FOR agenda.html.html generation*/

/*BEGIN FUNCTION genTextAgendaBody*/
/**********************************************************************************************************
* Function name : genTextAgendaBody()
* Description   : Generates HTML Body for the Progress report page
**********************************************************************************************************/
function genTextAgendaBody($dir_name)
{
// Gets the value from the Session
$meeting_number = $_SESSION['MEETING_NUMBER'];
$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
$host_proceeding = $_SESSION['HOST_PROCEEDING'];
$DATABASE = $_SESSION['DATABASE'];
$DATABASE_AMS = $_SESSION['DATABASE_AMS']; 

$text_agenda = "";

#mysql_select_db("ietf", $proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);


/*Get the Meeting start date and end date*/
$query_session_count = "SELECT count(session_id) as COUNT from wg_meeting_sessions where meeting_num=$meeting_number and meeting_num > 64";

$recordset_session_count = mysql_query($query_session_count, $proceedings_conn) or die(mysql_error());
$row_session_count = mysql_fetch_assoc($recordset_session_count);
$meeting_exist = $row_session_count['COUNT'];
 
/*CHECK IF THE MEETING HAS AGENDA*/ 
if ($meeting_exist == 0) {
	$text_agenda .= "No Agenda for found for IETF meeting $meeting_number";
}/*END OF MEETING EXIST IF*/
else {


/*Now create a Temporary table to hold the meeting sessions information for each of the Meeting day */
/*This temporary table will be used only for this script and will be removed after the script execution*/

/**********************************************/
/*CHANGE THE DATABASE NAME LATER*/
#mysql_select_db("ietf_ams", $proceedings_conn);
mysql_select_db($DATABASE_AMS, $proceedings_conn);

/**********************************************/

/*Get the hit count from meeting_agenda_count*/
$query_hit_count = "SELECT hit_count from meeting_agenda_count";
$recordset_hit_count = mysql_query($query_hit_count,$proceedings_conn) or die(mysql_error());
$row_hit_count = mysql_fetch_assoc($recordset_hit_count);
$table_id = $row_hit_count['hit_count'];
/*Increment the hit count*/
$table_id++;
/*Now update table meeeting_agenda_count with new count*/
$query_update_hit_count = "UPDATE meeting_agenda_count set hit_count=$table_id";
$result_update_hit_count = mysql_query($query_update_hit_count,$proceedings_conn) or die(mysql_error());

/*Create temprory table to hold sessions data*/

#$query_temp_table = "CREATE TABLE `ietf_ams`.`temp_agenda$table_id` (`id` INT(4) NOT NULL AUTO_INCREMENT PRIMARY KEY, `time_desc` VARCHAR(50) NOT NULL, `sessionname` VARCHAR(255) NOT NULL, `room_name` VARCHAR(255) NOT NULL, `area` VARCHAR(5) NOT NULL, `group_acronym_id` INT(8) NOT NULL, `group_acronym` VARCHAR(20) NOT NULL, `group_name` VARCHAR(255) NOT NULL, `special_agenda_note` VARCHAR(255) NOT NULL) ENGINE = MyISAM;";


$query_temp_table = "CREATE TABLE `temp_agenda$table_id` (`id` INT(4) NOT NULL AUTO_INCREMENT PRIMARY KEY, `time_desc` VARCHAR(50) NOT NULL, `sessionname` VARCHAR(255) NOT NULL, `room_name` VARCHAR(255) NOT NULL, `area` VARCHAR(5) NOT NULL, `group_acronym_id` INT(8) NOT NULL, `group_acronym` VARCHAR(20) NOT NULL, `group_name` VARCHAR(255) NOT NULL, `special_agenda_note` VARCHAR(255) NOT NULL) ENGINE = MyISAM;";

$result_temp_table = mysql_query($query_temp_table,$proceedings_conn) or die(mysql_error());

/**********************************************/
/*CHANGE THE DATABASE NAME LATER*/
#mysql_select_db("ietf", $proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);

/**********************************************/

/*WRITE AGENDA BOTTOM*/	
/*Get the meeting information*/
		$query_meeting_info = "SELECT start_date,end_date from meetings where meeting_num=$meeting_number";
		$recordset_meeting_info = mysql_query($query_meeting_info, $proceedings_conn) or die(mysql_error());
		$row_meeting_info = mysql_fetch_assoc($recordset_meeting_info);

		/*GET THE TIME FRAME OF THE MEETING CHECK IF START MONTH END MONTH IS SAME OR NOT*/
		$period = getPeriod($row_meeting_info['start_date'],$row_meeting_info['end_date']);
		$agenda_start_date = $row_meeting_info['start_date'];


		$text_agenda .= "Agenda of  IETF $meeting_number $period\n";
		/*GET THE AREA DIRECTORS PORTION AT THE END*/
		$text_agenda_bottom = "";
		$text_agenda_bottom = "============================AREA DIRECTORS===================================\n";
		/*Get the area names*/
		$query_area = "SELECT area_acronym_id, name, acronym from areas a, acronym b where status_id=1 and area_acronym_id=acronym_id order by acronym";
		$recordset_area = mysql_query($query_area,$proceedings_conn) or die(mysql_error());

		/*GET THE area names for geting the AD's*/
		while ($row_area = mysql_fetch_assoc($recordset_area))
		{
			$area_acronym_id = $row_area['area_acronym_id'];
			$name = $row_area['name'];
			$acronym = $row_area['acronym'];
			$acronym = strtoupper($acronym);
			$ads_text = "";
		/*Get the Area directors for the Areas*/	
			$query_ads = "SELECT first_name,last_name,affiliated_company from area_directors a, person_or_org_info b, postal_addresses c where area_acronym_id=$area_acronym_id and a.person_or_org_tag=b.person_or_org_tag and a.person_or_org_tag=c.person_or_org_tag and address_priority=1";
			$recordset_ads = mysql_query($query_ads,$proceedings_conn) or die(mysql_error());
			$row_ad_count = mysql_num_rows($recordset_ads);
			$count = 0;	
			while ($row_ads = mysql_fetch_assoc($recordset_ads))	
			{
			 $first_name = $row_ads['first_name'];
			 $last_name = $row_ads['last_name'];
			 $company = $row_ads['affiliated_company'];
			 $count++;
			 $ads_text .= " ".$first_name." ".$last_name."/".$company." ";
			 if ($row_ad_count == $count)
				 {
					$ads_text .= "";
				 }else
				 {
					$ads_text .= "&";
				 }
			}/*END OF WHILE FOR ADs*/
			chop($ads_text);
			$text_agenda_bottom .= "$acronym  $name \t$ads_text\n";

		}/*END OF WHILE FOR area*/

/*END OF THE AGENDA BOTTOM SCRIPT*/	

/*GET THE AGENDA BODY*/
$days= array('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday');
$text_agenda_body = "";
$query_cbreak_time="SELECT time_desc from non_session where meeting_num=$meeting_number and non_session_ref_id=2";
$recordset_cbreak_time = mysql_query($query_cbreak_time,$proceedings_conn) or die(mysql_error());
$row_cbreak_time = mysql_fetch_assoc($recordset_cbreak_time);
$cbreak_time = $row_cbreak_time['time_desc'];

$query_break_time="SELECT time_desc from non_session where meeting_num=$meeting_number and non_session_ref_id=3";
$recordset_break_time = mysql_query($query_break_time,$proceedings_conn) or die(mysql_error());
$row_break_time = mysql_fetch_assoc($recordset_break_time);
$break_time = $row_break_time['time_desc'];

$query_meeting_venue ="SELECT reg_area_name,break_area_name from meeting_venues where meeting_num=$meeting_number";
$recordset_meeting_venue = mysql_query($query_meeting_venue,$proceedings_conn) or die(mysql_error());
$row_meeting_venue = mysql_fetch_assoc($recordset_meeting_venue);
$reg_area_name = $row_meeting_venue['reg_area_name'];
$break_area_name = $row_meeting_venue['break_area_name'];



/*NOW GET THE DATA FOR ALL DAYS*/

for ($day_id=0;$day_id<6;$day_id++) {

#mysql_select_db("ietf",$proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);


/*Now get the proper date format such as Month, YYYY for entire meeting days(Week)*/
$day=strtoupper($days[$day_id]);
$query_date_add = "SELECT date_add('$agenda_start_date',interval $day_id day) as date_add";
$recordset_date_add = mysql_query($query_date_add,$proceedings_conn) or die(mysql_error());
$row_date_add = mysql_fetch_assoc($recordset_date_add);
$date_add= $row_date_add['date_add'];
$format = "FdY";
$format_date = formatDate($date_add,$format);

/*DAYNAME AND DATE FOR EACH SESSION DAY like Monday November8, 2009*/
$text_agenda_body .= "\n$day, $format_date\n";

/*Get the reg_time from non_session table*/
$query_reg_time ="SELECT time_desc from non_session where meeting_num=$meeting_number and day_id=$day_id and non_session_ref_id=1";
$recordset_reg_time = mysql_query($query_reg_time,$proceedings_conn) or die(mysql_error());
$row_reg_time = mysql_fetch_assoc($recordset_reg_time);
$reg_time = $row_reg_time['time_desc'];

/**********************************************/
/*Change the database to ietf_ams for temp table*/
#mysql_select_db("ietf_ams",$proceedings_conn);
mysql_select_db($DATABASE_AMS, $proceedings_conn);

/**********************************************/
/*Remove any data from temp_agenda table*/
$query_update_tempagenda = "DELETE from temp_agenda$table_id";
$recordset_update_tempagenda = mysql_query($query_update_tempagenda,$proceedings_conn) or die(mysql_error());


/*********************************************************************************************************************/
/*This section handles getting all the sessions data and inserting it to temp_agenda table*/
/*********************************************************************************************************************/
/**********************************************/
/*Change the database back to ietf*/
#mysql_select_db("ietf",$proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);

/**********************************************/

/*For session1*/
$query_session = "SELECT irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_number and sched_time_id1=time_id and day_id=$day_id and a.sched_room_id1=room_id UNION select irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_number and sched_time_id2=time_id and day_id=$day_id and a.sched_room_id2=room_id UNION select irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_number and sched_time_id3=time_id and day_id=$day_id and a.sched_room_id3=room_id UNION select irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_number and combined_time_id1=time_id and day_id=$day_id and a.combined_room_id1=room_id UNION select irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_number and combined_time_id2=time_id and day_id=$day_id and a.combined_room_id2=room_id";


$recordset_session = mysql_query($query_session,$proceedings_conn) or die(mysql_error());


/*Get the data from recordset*/
while ($row_session = mysql_fetch_assoc($recordset_session))
{
	 $irtf = $row_session['irtf'];
	 $session_name_id = ($row_session['session_name_id']);
	 $time_desc = $row_session['time_desc'];
	 $group_acronym_id = $row_session['group_acronym_id'];
	 $room_name = ($row_session['room_name']);
	 $special_agenda_note = ($row_session['special_agenda_note']);
	
#	mysql_select_db("ietf",$proceedings_conn);
	mysql_select_db($DATABASE, $proceedings_conn);

	/*Get the group acronym and name*/
	$query_acronym_detail = "SELECT acronym,name from acronym where acronym_id=$group_acronym_id";
	$recordset_acronym_detail = mysql_query($query_acronym_detail,$proceedings_conn) or die(mysql_error());
	$row_acronym_detail = mysql_fetch_assoc($recordset_acronym_detail);
		$group_acronym =($row_acronym_detail['acronym']);
		$group_name = ($row_acronym_detail['name']);

	
	/*Get the area name from acronym id*/
	$query_area_name = "SELECT acronym from acronym a, area_group b where area_acronym_id=acronym_id and group_acronym_id=$group_acronym_id";
	$recordset_area_name = mysql_query($query_area_name,$proceedings_conn) or die(mysql_error());
	$row_area_name = mysql_fetch_assoc($recordset_area_name);
	$area_name = ($row_area_name['acronym']);
	/*Check if its a IRTF*/
		if ($irtf) {
		  $area_name="IRTF";
		  $query_irtf_acronym = "SELECT irtf_acronym,irtf_name from irtf where irtf_id=$group_acronym_id";
		  $recordset_irtf_acronym = mysql_query($query_irtf_acronym,$proceedings_conn) or die(mysql_error());
		  $row_irtf_acronym = mysql_fetch_assoc($recordset_irtf_acronym);
			$group_acronym = ($row_irtf_acronym['irtf_acronym']);
			$group_name = ($row_irtf_acronym['irtf_name']);		
		}//End of irtf if
		 else {
		  $irtf=0;
		}//End of irtf else
	
	$area_name=strtoupper($area_name);
	
	/*Get the session name from session_id*/
	$query_session_name = "SELECT session_name from session_names where session_name_id=$session_name_id";
	$recordset_session_name = mysql_query($query_session_name,$proceedings_conn) or die(mysql_error());
	$row_session_name = mysql_fetch_assoc($recordset_session_name);
	$session_name = ($row_session_name['session_name']);
	
	/*Before inserting to database check if the values are null or Empty */
	
	if  (is_null($time_desc))
	{
	 $time_desc = NULL;
	}
	else if ($time_desc == "")
	{
	 $time_desc = " ";
	}
	if  (is_null($session_name))
	{
	$session_name = NULL;
	}
	else if ($session_name == "")
	{
	 $session_name = " ";
	}
	if  (is_null($area_name))
	{
	$area_name = NULL;
	}
	else if ($area_name == "")
	{
	 $area_name = " ";
	}
	
	if  (is_null($group_acronym_id))
	{
	$group_acronym_id = NULL;
	}
	else if ($group_acronym_id == "")
	{
	 $group_acronym_id = " ";
	}
	
	if  (is_null($group_acronym))
	{
	$group_acronym = NULL;
	}
	else if ($group_acronym == "")
	{
	 $group_acronym = " ";
	}
	
	if  (is_null($group_name))
	{
	$group_name = NULL;
	}
	else if ($group_name == "")
	{
	 $group_name = " ";
	}
	if  (is_null($special_agenda_note))
	{
	$special_agenda_note = NULL;
	}
	else if ($special_agenda_note == "")
	{
	 $special_agenda_note = " ";
	}
	if  (is_null($room_name))
	{
	$room_name = NULL;
	}
	else if ($room_name == "")
	{
	 $room_name = " ";
	}
	
	/**********************************************/
	/*Change the database to ietf_ams for temp table*/
#	mysql_select_db("ietf_ams",$proceedings_conn);
	mysql_select_db($DATABASE_AMS, $proceedings_conn);

	/**********************************************/
	/*Insert all the data to temp_agenda table*/
	
	
	$time_desc = mysql_real_escape_string($time_desc);
	$session_name = mysql_real_escape_string($session_name);
	$area_name = mysql_real_escape_string($area_name);
	$group_acronym_id = mysql_real_escape_string($group_acronym_id);
	$group_acronym = mysql_real_escape_string($group_acronym);
	$group_name = mysql_real_escape_string($group_name);
	$special_agenda_note = mysql_real_escape_string($special_agenda_note);
	$room_name = mysql_real_escape_string($room_name);
	
	$query_insert_temp_agenda = "INSERT into temp_agenda$table_id (time_desc,sessionname,room_name,area,group_acronym_id,group_acronym,group_name,special_agenda_note) values('$time_desc','$session_name','$room_name','$area_name','$group_acronym_id','$group_acronym','$group_name','$special_agenda_note')";
	#$recordset_insert_temp_agenda = mysql_query($query_insert_temp_agenda,$proceedings_conn) or die(mysql_error());
	$recordset_insert_agenda = mysql_query($query_insert_temp_agenda,$proceedings_conn) or dir(mysql_error());
	
	
	/*********************************************************************************************************************/
	/*END OF section handling all the sessions data and inserting it to temp_agenda table*/
	/*********************************************************************************************************************/
	
} //END of mysql_fetch_assoc($recordset_session)) while

/*******************************************************************************************************************/
/*SUNDAY SESSION*/
/*Prepare HTML session information for the Sunday sessions*/
/*******************************************************************************************************************/
if ($day_id == "0")
{
/**********************************************/
/*Change the database to ietf_ams for temp table*/
#mysql_select_db("ietf_ams",$proceedings_conn);
mysql_select_db($DATABASE_AMS, $proceedings_conn);

/**********************************************/
  	$text_agenda_body .= "$reg_time IETF Registration - $reg_area_name \n" ;
	$query_temp_agenda_sunday = "SELECT time_desc,group_name,room_name,special_agenda_note from temp_agenda$table_id order by time_desc";
    $recordset_temp_agenda_sunday = mysql_query($query_temp_agenda_sunday,$proceedings_conn) or die(mysql_error());
	while ($row_temp_agenda_sunday = mysql_fetch_assoc($recordset_temp_agenda_sunday))
	{
	    $time_desc = $row_temp_agenda_sunday['time_desc'];
		$group_name = $row_temp_agenda_sunday['group_name'];
		$room_name = $row_temp_agenda_sunday['room_name'];
		$special_agenda_note = $row_temp_agenda_sunday['special_agenda_note'];
	    $text_agenda_body .= "$time_desc  $group_name - $room_name";
		if ($special_agenda_note)
		{
         $text_agenda_body .= " - $special_agenda_note";
		}
	  	$text_agenda_body .= "\n";

    }//End of  while ($row_temp_agenda_sunday
}//End of Sunday session if
else
{
/*Prepare HTML session information for rest of the sessions*/
/**********************************************/
#mysql_select_db("ietf",$proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);

/**********************************************/

/*Get theReg time, area , break time and area*/	
	$query_arbreaktime1 = "SELECT time_desc from non_session where meeting_num=$meeting_number and non_session_ref_id='4' and day_id=$day_id";
	$recordset_arbreaktime1 = mysql_query($query_arbreaktime1,$proceedings_conn) or die(mysql_error());
	$row_arbreaktime1 = mysql_fetch_assoc($recordset_arbreaktime1);
	$arbreak_time1 = $row_arbreaktime1['time_desc'];
	
	
	$query_arbreaktime2 = "SELECT time_desc from non_session where meeting_num=$meeting_number and non_session_ref_id='5' and day_id=$day_id";
	$recordset_arbreaktime2 = mysql_query($query_arbreaktime2,$proceedings_conn) or die(mysql_error());
	$row_arbreaktime2 = mysql_fetch_assoc($recordset_arbreaktime2);
	$arbreak_time2 = $row_arbreaktime1['time_desc'];
	
	if ($reg_time)
	{
     $text_agenda_body .= "$reg_time IETF Registration - $reg_area_name\n";
	}
    $text_agenda_body .= "$cbreak_time Continental Breakfast - $break_area_name\n";

/*Get the session details in proper order from temp table*/	

/**********************************************/
#mysql_select_db("ietf_ams",$proceedings_conn);
mysql_select_db($DATABASE_AMS, $proceedings_conn);

/**********************************************/

	$query_sessions_detail = "SELECT time_desc,group_acronym_id,sessionname, room_name,special_agenda_note,area,group_name,group_acronym from temp_agenda$table_id order by time_desc, area, group_name";
	$recordset_sessions_detail = mysql_query($query_sessions_detail,$proceedings_conn) or die(mysql_error());
	$prev_session_name = "";


	while ($row_sessions_detail = mysql_fetch_assoc($recordset_sessions_detail))
	{
       $group_acronym_id = $row_sessions_detail['group_acronym_id'];
	   $session_name = $row_sessions_detail['sessionname'];
	   $room_name = $row_sessions_detail['room_name'];
	   $special_agenda_note = $row_sessions_detail['special_agenda_note'];
	   $area = $row_sessions_detail['area'];
	   $group_name = $row_sessions_detail['group_name'];
	   $group_acronym = $row_sessions_detail['group_acronym'];
	   $time_desc = $row_sessions_detail['time_desc'];
	   
/**********************************************/
#mysql_select_db("ietf",$proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);

/**********************************************/
		$query_group_type_id="SELECT group_type_id from groups_ietf where group_acronym_id=$group_acronym_id";
        $recordset_group_type_id = mysql_query($query_group_type_id,$proceedings_conn) or die(mysql_error());
		$row_group_type_id = mysql_fetch_assoc($recordset_group_type_id);
		$group_type_id = $row_group_type_id['group_type_id'];
		

		if ($group_type_id== '3')
		{
	      $group_name .= " BOF" ;
		}
		if ($group_type_id== '1'){
		      $group_name .= " WG" ;
			  }
    
	   $irtf=($group_acronym_id >0 and $group_acronym_id < 30)?1:0;


	/*Now check if the group_acronym contains plenary*/   
	   $myplenary = 'plenary';
	   $pos = "";
	   $pos = strpos($group_acronym,$myplenary);	   

	  if ($pos === false) {
			}
			else
			{
//Locate the planary file NEED TO CHECK THIS CODE
	/*			$pfile = "/a/www/www6s/proceedings/$meeting_number/agenda/$group_acronym.txt";
				
				//Check if the file esists
				if (file_exists($pfile))
				{
				 $p_file_data = file_get_contents($pfile);	 
				}
				else
				{
				 $p_file_data = "THE AGENDA HAS NOT BEEN UPLOADED YET";			
				}
*/			
			
				$p_file_data = "THE AGENDA HAS NOT BEEN UPLOADED YET";			
				$text_agenda_body .= "\n";
				if ($prev_session_name == "Afternoon Session II" && $arbreak_time2)
					{
					$text_agenda_body .= "\n$arbreak_time2 Afternoon Refreshment Break - $break_area_name\n" ;
					}	
				$text_agenda_body .= "$time_desc $session_name - $room_name $p_file_data";

//				next;
		}	//End of $pos if(plenary)

	   if ($session_name != $prev_session_name) 
	   		{
	        	if ($prev_session_name != "")
				 {
          			$text_agenda_body .= "\n";
        		 }
				 
				if ($session_name == "Afternoon Session I")
				 {
			       $text_agenda_body .= "$break_time Break\n" ;
				 }	

				if ($prev_session_name == "Afternoon Session I" && ($arbreak_time1))
				 {
			       $text_agenda_body .= "$arbreak_time1 Afternoon Refreshment Break - $break_area_name\n";
				 } 
			    if ($prev_session_name == "Afternoon Session II" && ($arbreak_time2))
				 {
				   $text_agenda_body .= "$arbreak_time2 Afternoon Refreshment Break - $break_area_name\n";
                 }
				 $prev_session_name=$session_name;
        		 $text_agenda_body .= "$time_desc $session_name\n";

    
		    }//End of if $session_name != $prev_session_name
				 
				 $space = " ";
				$max_length = 16;
				$room_length = strlen($room_name);
				
				if ($room_length < $max_length)
				{
					$diff_length = $max_length - $room_length;
					for ($loop =0;$loop < $diff_length; $loop++)
					{
					$room_name .= " "; 
					}
				}	
			      $one_line = "$room_name $area  $group_acronym \t $group_name";
				  
				  if ($special_agenda_note)
				  {
			        $one_line .= " - $special_agenda_note";
				  }	
				
			      $one_line .= "\n";
			      $text_agenda_body .= $one_line;

				
		
	}//End of while ($row_sessions_detail 

}//ENd of Sunday session else*/

}//END OF FOR LOOP FOR DAYS for ($day_id=0;$day_id<6;$day_id++) 


/**********************************************/
/*CHANGE THE DATABASE NAME LATER*/
#mysql_select_db("ietf_ams", $proceedings_conn);
mysql_select_db($DATABASE_AMS, $proceedings_conn);

/**********************************************/

$query_temp_table_drop = "DROP TABLE temp_agenda$table_id";
$result_temp_table_drop = mysql_query($query_temp_table_drop,$proceedings_conn) or die(mysql_error());


/*END OF THE AGENDA BODY SCRIPT*/



/*Attached agenda_bottom to rest of the agenda*/
	$text_agenda .= $text_agenda_body;
	$text_agenda .= "\n";
	$text_agenda .= $text_agenda_bottom;
	
     }
	 
return 	 $text_agenda;
}
/*END OF FUNCTION genTextAgendaBody*/

/**********************************************************************************************************
* Function name : format_room_name()
* Description   : Formats the session output for text agenda
**********************************************************************************************************/
function  format_room_name($room_name)
{
  $max_len=16;
}
/*End of  function format_room_name*/
/*BEGIN OF FUNCTION genAgendaBody*/
/**********************************************************************************************************
* Function name : genAgendaBody()
* Description   : Generates HTML Body for the Progress report page
**********************************************************************************************************/
#function genAgendaBody($meeting_number,$proceedings_conn,$dir_name)
function genAgendaBody($dir_name)
{
// Gets the value from the Session
$meeting_number = $_SESSION['MEETING_NUMBER'];
$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
$host_proceeding = $_SESSION['HOST_PROCEEDING'];
$DIR_PROCEEDING = $_SESSION['DIR_PROCEEDING'];
#$HOST_PRIYANKA = $_SESSION['HOST_PRIYANKA'];
$HOST_NAME = $_SESSION['HOST_NAME'];
$DATABASE = $_SESSION['DATABASE'];
$DATABASE_AMS = $_SESSION['DATABASE_AMS']; 

$agenda_text = "";
/*NEED TO CHANGE DATABASE NAMES*/

#mysql_select_db($database_proceedings_conn, $proceedings_conn);
#mysql_select_db("ietf", $proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);


/*Get the Meeting start date and end date*/
$query_session_count = "SELECT count(session_id) as COUNT from wg_meeting_sessions where meeting_num=$meeting_number and meeting_num > 64";

$recordset_session_count = mysql_query($query_session_count, $proceedings_conn) or die(mysql_error());
$row_session_count = mysql_fetch_assoc($recordset_session_count);
$meeting_exist = $row_session_count['COUNT'];
 
/*CHECK IF THE MEETING HAS AGENDA*/ 
if ($meeting_exist == 0) {
	$agenda_text .= "<h3>No Agenda for found for IETF meeting"." ".$meeting_number ."</h3>";
}/*END OF MEETING EXIST IF*/
else {
/*Now create a Temporary table to hold the meeting sessions information for each of the Meeting day */
/*This temporary table will be used only for this script and will be removed after the script execution*/

/**********************************************/
/*CHANGE THE DATABASE NAME LATER*/
#mysql_select_db("ietf_ams", $proceedings_conn);
mysql_select_db($DATABASE_AMS, $proceedings_conn);

/**********************************************/

/*Get the hit count from meeting_agenda_count*/
$query_hit_count = "SELECT hit_count from meeting_agenda_count";
$recordset_hit_count = mysql_query($query_hit_count,$proceedings_conn) or die(mysql_error());
$row_hit_count = mysql_fetch_assoc($recordset_hit_count);
$table_id = $row_hit_count['hit_count'];
/*Increment the hit count*/
$table_id++;
/*Now update table meeeting_agenda_count with new count*/
$query_update_hit_count = "UPDATE meeting_agenda_count set hit_count=$table_id";
$result_update_hit_count = mysql_query($query_update_hit_count,$proceedings_conn) or die(mysql_error());

/*Create temprory table to hold sessions data*/

#$query_temp_table = "CREATE TABLE `ietf_ams`.`temp_agenda$table_id` (`id` INT(4) NOT NULL AUTO_INCREMENT PRIMARY KEY, `time_desc` VARCHAR(50) NOT NULL, `sessionname` VARCHAR(255) NOT NULL, `room_name` VARCHAR(255) NOT NULL, `area` VARCHAR(5) NOT NULL, `group_acronym_id` INT(8) NOT NULL, `group_acronym` VARCHAR(20) NOT NULL, `group_name` VARCHAR(255) NOT NULL, `special_agenda_note` VARCHAR(255) NOT NULL) ENGINE = MyISAM;";

$query_temp_table = "CREATE TABLE `temp_agenda$table_id` (`id` INT(4) NOT NULL AUTO_INCREMENT PRIMARY KEY, `time_desc` VARCHAR(50) NOT NULL, `sessionname` VARCHAR(255) NOT NULL, `room_name` VARCHAR(255) NOT NULL, `area` VARCHAR(5) NOT NULL, `group_acronym_id` INT(8) NOT NULL, `group_acronym` VARCHAR(20) NOT NULL, `group_name` VARCHAR(255) NOT NULL, `special_agenda_note` VARCHAR(255) NOT NULL) ENGINE = MyISAM;";

$result_temp_table = mysql_query($query_temp_table,$proceedings_conn) or die(mysql_error());

/**********************************************/
/*CHANGE THE DATABASE NAME LATER*/
#mysql_select_db("ietf", $proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);

/**********************************************/



/*Get the meeting information*/
$query_meeting_info = "SELECT start_date,end_date from meetings where meeting_num=$meeting_number";
$recordset_meeting_info = mysql_query($query_meeting_info, $proceedings_conn) or die(mysql_error());
$row_meeting_info = mysql_fetch_assoc($recordset_meeting_info);

/*GET THE TIME FRAME OF THE MEETING CHECK IF START MONTH END MONTH IS SAME OR NOT*/
$period = getPeriod($row_meeting_info['start_date'],$row_meeting_info['end_date']);
$agenda_start_date = $row_meeting_info['start_date'];

/*GET THE AREA DIRECTORS PORTION AT THE END*/
$agenda_bottom = "";
$agenda_bottom = "<center><b>AREA DIRECTORS</b></center><br><table border=\"0\" width=\"800\">";
/*Get the area names*/
$query_area = "SELECT area_acronym_id, name, acronym from areas a, acronym b where status_id=1 and area_acronym_id=acronym_id order by acronym";
$recordset_area = mysql_query($query_area,$proceedings_conn) or die(mysql_error());

/*GET THE area names for geting the AD's*/
while ($row_area = mysql_fetch_assoc($recordset_area))
{
	$area_acronym_id = $row_area['area_acronym_id'];
	$name = $row_area['name'];
	$acronym = $row_area['acronym'];
	$acronym = strtoupper($acronym);
	$ads_text = "";
/*Get the Area directors for the Areas*/	
	$query_ads = "SELECT first_name,last_name,affiliated_company from area_directors a, person_or_org_info b, postal_addresses c where area_acronym_id=$area_acronym_id and a.person_or_org_tag=b.person_or_org_tag and a.person_or_org_tag=c.person_or_org_tag and address_priority=1";
    $recordset_ads = mysql_query($query_ads,$proceedings_conn) or die(mysql_error());
	$row_ad_count = mysql_num_rows($recordset_ads);
	$count = 0;	
	while ($row_ads = mysql_fetch_assoc($recordset_ads))	
	{
	 $first_name = $row_ads['first_name'];
	 $last_name = $row_ads['last_name'];
	 $company = $row_ads['affiliated_company'];
	 $count++;
 	 $ads_text .= " ".$first_name." ".$last_name."/".$company." ";
	 if ($row_ad_count == $count)
		 {
		  	$ads_text .= "";
		 }else
		 {
		 	$ads_text .= "&";
		 }
	}/*END OF WHILE FOR ADs*/
	chop($ads_text);
    $agenda_bottom .= "<tr valign=\"top\"><td width=\"65\">".$acronym."</td><td width=\"140\">".$name."</td><td>".$ads_text."</td></tr>";

}/*END OF WHILE FOR area*/
$agenda_bottom .= "</table>";
/*END OF THE AGENDA BOTTOM SCRIPT*/

/*GET THE AGENDA BODY*/
$days= array('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday');
$agenda_body = "";
$query_cbreak_time="SELECT time_desc from non_session where meeting_num=$meeting_number and non_session_ref_id=2";
$recordset_cbreak_time = mysql_query($query_cbreak_time,$proceedings_conn) or die(mysql_error());
$row_cbreak_time = mysql_fetch_assoc($recordset_cbreak_time);
$cbreak_time = $row_cbreak_time['time_desc'];

$query_break_time="SELECT time_desc from non_session where meeting_num=$meeting_number and non_session_ref_id=3";
$recordset_break_time = mysql_query($query_break_time,$proceedings_conn) or die(mysql_error());
$row_break_time = mysql_fetch_assoc($recordset_break_time);
$break_time = $row_break_time['time_desc'];

$query_meeting_venue ="SELECT reg_area_name,break_area_name from meeting_venues where meeting_num=$meeting_number";
$recordset_meeting_venue = mysql_query($query_meeting_venue,$proceedings_conn) or die(mysql_error());
$row_meeting_venue = mysql_fetch_assoc($recordset_meeting_venue);
$reg_area_name = $row_meeting_venue['reg_area_name'];
$break_area_name = $row_meeting_venue['break_area_name'];



/*NOW GET THE DATA FOR ALL DAYS*/

for ($day_id=0;$day_id<6;$day_id++) {

#mysql_select_db("ietf",$proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);


/*Now get the proper date format such as Month, YYYY for entire meeting days(Week)*/
$day=strtoupper($days[$day_id]);
$query_date_add = "SELECT date_add('$agenda_start_date',interval $day_id day) as date_add";
$recordset_date_add = mysql_query($query_date_add,$proceedings_conn) or die(mysql_error());
$row_date_add = mysql_fetch_assoc($recordset_date_add);
$date_add= $row_date_add['date_add'];
$format = "FdY";
$format_date = formatDate($date_add,$format);

/*DAYNAME AND DATE FOR EACH SESSION DAY like Monday November8, 2009*/
$agenda_body .= "<b>".$day." ".$format_date."</b><br>";

/*Get the reg_time from non_session table*/
$query_reg_time ="SELECT time_desc from non_session where meeting_num=$meeting_number and day_id=$day_id and non_session_ref_id=1";
$recordset_reg_time = mysql_query($query_reg_time,$proceedings_conn) or die(mysql_error());
$row_reg_time = mysql_fetch_assoc($recordset_reg_time);
$reg_time = $row_reg_time['time_desc'];

/**********************************************/
/*Change the database to ietf_ams for temp table*/
#mysql_select_db("ietf_ams",$proceedings_conn);
mysql_select_db($DATABASE_AMS, $proceedings_conn);

/**********************************************/
/*Remove any data from temp_agenda table*/
$query_update_tempagenda = "DELETE from temp_agenda$table_id";
$recordset_update_tempagenda = mysql_query($query_update_tempagenda,$proceedings_conn) or die(mysql_error());


/*********************************************************************************************************************/
/*This section handles getting all the sessions data and inserting it to temp_agenda table*/
/*********************************************************************************************************************/
/**********************************************/
/*Change the database back to ietf*/
#mysql_select_db("ietf",$proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);

/**********************************************/

/*For session1*/
$query_session = "SELECT irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_number and sched_time_id1=time_id and day_id=$day_id and a.sched_room_id1=room_id UNION select irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_number and sched_time_id2=time_id and day_id=$day_id and a.sched_room_id2=room_id UNION select irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_number and sched_time_id3=time_id and day_id=$day_id and a.sched_room_id3=room_id UNION select irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_number and combined_time_id1=time_id and day_id=$day_id and a.combined_room_id1=room_id UNION select irtf,session_name_id,time_desc,group_acronym_id,room_name,special_agenda_note from wg_meeting_sessions a,meeting_times b, meeting_rooms d where a.meeting_num=$meeting_number and combined_time_id2=time_id and day_id=$day_id and a.combined_room_id2=room_id";


$recordset_session = mysql_query($query_session,$proceedings_conn) or die(mysql_error());


/*Get the data from recordset*/
while ($row_session = mysql_fetch_assoc($recordset_session))
{
	 $irtf = $row_session['irtf'];
	 $session_name_id = ($row_session['session_name_id']);
	 $time_desc = $row_session['time_desc'];
	 $group_acronym_id = $row_session['group_acronym_id'];
	 $room_name = ($row_session['room_name']);
	 $special_agenda_note = ($row_session['special_agenda_note']);
	
	#mysql_select_db("ietf",$proceedings_conn);
	mysql_select_db($DATABASE, $proceedings_conn);

	
	/*Get the group acronym and name*/
	$query_acronym_detail = "SELECT acronym,name from acronym where acronym_id=$group_acronym_id";
	$recordset_acronym_detail = mysql_query($query_acronym_detail,$proceedings_conn) or die(mysql_error());
	$row_acronym_detail = mysql_fetch_assoc($recordset_acronym_detail);
		$group_acronym =($row_acronym_detail['acronym']);
		$group_name = ($row_acronym_detail['name']);

	
	/*Get the area name from acronym id*/
	$query_area_name = "SELECT acronym from acronym a, area_group b where area_acronym_id=acronym_id and group_acronym_id=$group_acronym_id";
	$recordset_area_name = mysql_query($query_area_name,$proceedings_conn) or die(mysql_error());
	$row_area_name = mysql_fetch_assoc($recordset_area_name);
	$area_name = ($row_area_name['acronym']);
	/*Check if its a IRTF*/
		if ($irtf) {
		  $area_name="IRTF";
		  $query_irtf_acronym = "SELECT irtf_acronym,irtf_name from irtf where irtf_id=$group_acronym_id";
		  $recordset_irtf_acronym = mysql_query($query_irtf_acronym,$proceedings_conn) or die(mysql_error());
		  $row_irtf_acronym = mysql_fetch_assoc($recordset_irtf_acronym);
			$group_acronym = ($row_irtf_acronym['irtf_acronym']);
			$group_name = ($row_irtf_acronym['irtf_name']);		
		}//End of irtf if
		 else {
		  $irtf=0;
		}//End of irtf else
	
	$area_name=strtoupper($area_name);
	
	/*Get the session name from session_id*/
	$query_session_name = "SELECT session_name from session_names where session_name_id=$session_name_id";
	$recordset_session_name = mysql_query($query_session_name,$proceedings_conn) or die(mysql_error());
	$row_session_name = mysql_fetch_assoc($recordset_session_name);
	$session_name = ($row_session_name['session_name']);
	
	/*Before inserting to database check if the values are null or Empty */
	
	if  (is_null($time_desc))
	{
	 $time_desc = NULL;
	}
	else if ($time_desc == "")
	{
	 $time_desc = " ";
	}
	if  (is_null($session_name))
	{
	$session_name = NULL;
	}
	else if ($session_name == "")
	{
	 $session_name = " ";
	}
	if  (is_null($area_name))
	{
	$area_name = NULL;
	}
	else if ($area_name == "")
	{
	 $area_name = " ";
	}
	
	if  (is_null($group_acronym_id))
	{
	$group_acronym_id = NULL;
	}
	else if ($group_acronym_id == "")
	{
	 $group_acronym_id = " ";
	}
	
	if  (is_null($group_acronym))
	{
	$group_acronym = NULL;
	}
	else if ($group_acronym == "")
	{
	 $group_acronym = " ";
	}
	
	if  (is_null($group_name))
	{
	$group_name = NULL;
	}
	else if ($group_name == "")
	{
	 $group_name = " ";
	}
	if  (is_null($special_agenda_note))
	{
	$special_agenda_note = NULL;
	}
	else if ($special_agenda_note == "")
	{
	 $special_agenda_note = " ";
	}
	if  (is_null($room_name))
	{
	$room_name = NULL;
	}
	else if ($room_name == "")
	{
	 $room_name = " ";
	}
	
	/**********************************************/
	/*Change the database to ietf_ams for temp table*/
	#mysql_select_db("ietf_ams",$proceedings_conn);
	mysql_select_db($DATABASE_AMS, $proceedings_conn);

	/**********************************************/
	/*Insert all the data to temp_agenda table*/
	
	
	$time_desc = mysql_real_escape_string($time_desc);
	$session_name = mysql_real_escape_string($session_name);
	$area_name = mysql_real_escape_string($area_name);
	$group_acronym_id = mysql_real_escape_string($group_acronym_id);
	$group_acronym = mysql_real_escape_string($group_acronym);
	$group_name = mysql_real_escape_string($group_name);
	$special_agenda_note = mysql_real_escape_string($special_agenda_note);
	$room_name = mysql_real_escape_string($room_name);
	
	$query_insert_temp_agenda = "INSERT into temp_agenda$table_id (time_desc,sessionname,room_name,area,group_acronym_id,group_acronym,group_name,special_agenda_note) values('$time_desc','$session_name','$room_name','$area_name','$group_acronym_id','$group_acronym','$group_name','$special_agenda_note')";
	#$recordset_insert_temp_agenda = mysql_query($query_insert_temp_agenda,$proceedings_conn) or die(mysql_error());
	$recordset_insert_agenda = mysql_query($query_insert_temp_agenda,$proceedings_conn) or dir(mysql_error());
	
	
	/*********************************************************************************************************************/
	/*END OF section handling all the sessions data and inserting it to temp_agenda table*/
	/*********************************************************************************************************************/
	
} //END of mysql_fetch_assoc($recordset_session)) while

/*******************************************************************************************************************/
/*SUNDAY SESSION*/
/*Prepare HTML session information for the Sunday sessions*/
/*******************************************************************************************************************/
if ($day_id == "0")
{
/**********************************************/
/*Change the database to ietf_ams for temp table*/
#mysql_select_db("ietf_ams",$proceedings_conn);
mysql_select_db($DATABASE_AMS, $proceedings_conn);

/**********************************************/
  	$agenda_body .= "<br>$reg_time IETF Registration - $reg_area_name <br>" ;
	$query_temp_agenda_sunday = "SELECT time_desc,group_name,room_name,special_agenda_note from temp_agenda$table_id order by time_desc";
    $recordset_temp_agenda_sunday = mysql_query($query_temp_agenda_sunday,$proceedings_conn) or die(mysql_error());
	while ($row_temp_agenda_sunday = mysql_fetch_assoc($recordset_temp_agenda_sunday))
	{
	    $time_desc = $row_temp_agenda_sunday['time_desc'];
		$group_name = $row_temp_agenda_sunday['group_name'];
		$room_name = $row_temp_agenda_sunday['room_name'];
		$special_agenda_note = $row_temp_agenda_sunday['special_agenda_note'];
	    $agenda_body .= "$time_desc  $group_name - $room_name";
		if ($special_agenda_note)
		{
         $agenda_body .= " - <b>$special_agenda_note</b><br>";
		}
		else
		{
		  $agenda_body .= "<br>";
		}  
    }//End of  while ($row_temp_agenda_sunday
}//End of Sunday session if
else
{
/*Prepare HTML session information for rest of the sessions*/
/**********************************************/
#mysql_select_db("ietf",$proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);

/**********************************************/

/*Get theReg time, area , break time and area*/	
	$query_arbreaktime1 = "SELECT time_desc from non_session where meeting_num=$meeting_number and non_session_ref_id='4' and day_id=$day_id";
	$recordset_arbreaktime1 = mysql_query($query_arbreaktime1,$proceedings_conn) or die(mysql_error());
	$row_arbreaktime1 = mysql_fetch_assoc($recordset_arbreaktime1);
	$arbreak_time1 = $row_arbreaktime1['time_desc'];
	
	
	$query_arbreaktime2 = "SELECT time_desc from non_session where meeting_num=$meeting_number and non_session_ref_id='5' and day_id=$day_id";
	$recordset_arbreaktime2 = mysql_query($query_arbreaktime2,$proceedings_conn) or die(mysql_error());
	$row_arbreaktime2 = mysql_fetch_assoc($recordset_arbreaktime2);
	$arbreak_time2 = $row_arbreaktime1['time_desc'];
	
	if ($reg_time)
	{
     $agenda_body .= "<br>$reg_time IETF Registration - $reg_area_name";
	}
    $agenda_body .= "<br>\n$cbreak_time Continental Breakfast - $break_area_name<br>";

/*Get the session details in proper order from temp table*/	

/**********************************************/
#mysql_select_db("ietf_ams",$proceedings_conn);
mysql_select_db($DATABASE_AMS, $proceedings_conn);

/**********************************************/

	$query_sessions_detail = "SELECT time_desc,group_acronym_id,sessionname, room_name,special_agenda_note,area,group_name,group_acronym from temp_agenda$table_id order by time_desc, area, group_name";
	$recordset_sessions_detail = mysql_query($query_sessions_detail,$proceedings_conn) or die(mysql_error());
	$prev_session_name = "";


	while ($row_sessions_detail = mysql_fetch_assoc($recordset_sessions_detail))
	{
       $group_acronym_id = $row_sessions_detail['group_acronym_id'];
	   $session_name = $row_sessions_detail['sessionname'];
	   $room_name = $row_sessions_detail['room_name'];
	   $special_agenda_note = $row_sessions_detail['special_agenda_note'];
	   $area = $row_sessions_detail['area'];
	   $group_name = $row_sessions_detail['group_name'];
	   $group_acronym = $row_sessions_detail['group_acronym'];
	   $time_desc = $row_sessions_detail['time_desc'];
	   
/**********************************************/
#mysql_select_db("ietf",$proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);

/**********************************************/
		$query_group_type_id="SELECT group_type_id from groups_ietf where group_acronym_id=$group_acronym_id";
        $recordset_group_type_id = mysql_query($query_group_type_id,$proceedings_conn) or die(mysql_error());
		$row_group_type_id = mysql_fetch_assoc($recordset_group_type_id);
		$group_type_id = $row_group_type_id['group_type_id'];
		

		if ($group_type_id== '3')
		{
	      $group_name .= " BOF" ;
		}
		if ($group_type_id== '1'){
		      $group_name .= " WG" ;
			  }
    
	   $irtf=($group_acronym_id >0 and $group_acronym_id < 30)?1:0;


/***********************************************************/
/*Get the agenda file names*/
/***********************************************************/
       $query_agenda_file_name = "SELECT filename from wg_agenda where group_acronym_id=$group_acronym_id and meeting_num=$meeting_number and irtf=$irtf";
	   $recordset_agenda_file_name = mysql_query($query_agenda_file_name,$proceedings_conn) or die(mysql_error());
	   
	   $row_agenda_file_name = mysql_fetch_assoc($recordset_agenda_file_name);
	   $agenda_filename = $row_agenda_file_name['filename'];
	   

	   if ($agenda_filename){
#     		$group_name = "<a href=\"$host_proceeding/$meeting_number/agenda/$agenda_filename\">$group_name</a>";
       		$group_name = "<a href=\"/$DIR_PROCEEDING/$meeting_number/agenda/$agenda_filename\">$group_name</a>";
	   }

	/*Now check if the group_acronym contains plenary*/   
	   $myplenary = 'plenary';
	   $pos = "";
	   $pos = strpos($group_acronym,$myplenary);	   

	  if ($pos === false) {
			}
			else
			{
//Locate the planary file NEED TO CHECK THIS CODE
	/*			$pfile = "/a/www/www6s/proceedings/$meeting_number/agenda/$group_acronym.txt";
				
				//Check if the file esists
				if (file_exists($pfile))
				{
				 $p_file_data = file_get_contents($pfile);	 
				}
				else
				{
				 $p_file_data = "THE AGENDA HAS NOT BEEN UPLOADED YET";			
				}
*/			
			
				$p_file_data = "THE AGENDA HAS NOT BEEN UPLOADED YET";			
				$agenda_body .= "</table>\n";
				if ($prev_session_name == "Afternoon Session II" && $arbreak_time2)
					{
					$agenda_body .= "<br>\n$arbreak_time2 Afternoon Refreshment Break - $break_area_name<br>\n" ;
					}	
				$agenda_body .= "<b>$time_desc $session_name - $room_name</b><br><pre>$p_file_data</pre><table>";

//				next;
		}	//End of $pos if(plenary)

	   if ($session_name != $prev_session_name) 
	   		{
	        	if ($prev_session_name != "")
				 {
          			$agenda_body .= "</table><br>";
        		 }
				 
				if ($session_name == "Afternoon Session I")
				 {
			       $agenda_body .= "$break_time Break<br>" ;
				 }	

				if ($prev_session_name == "Afternoon Session I" && ($arbreak_time1))
				 {
			       $agenda_body .= "$arbreak_time1 Afternoon Refreshment Break - $break_area_name<br>";
				 } 
			    if ($prev_session_name == "Afternoon Session II" && ($arbreak_time2))
				 {
				   $agenda_body .= "$arbreak_time2 Afternoon Refreshment Break - $break_area_name<br>";
                 }
				 $prev_session_name=$session_name;
        		 $agenda_body .= "<b>$time_desc $session_name</b>\n<table border=\"0\" cellspacing=\"0\" cellpadding=\"0\" width=\"800\">\n";

    
		    }//End of if $session_name != $prev_session_name
	             $query_session_group_id = "SELECT group_type_id from groups_ietf where group_acronym_id=$group_acronym_id";
                 $recordset_session_group_id = mysql_query($query_session_group_id,$proceedings_conn)  or die(mysql_error());  
				 $row_session_group_id = mysql_fetch_assoc($recordset_session_group_id);
                 $group_type_id = $row_session_group_id['group_type_id'];
				 
				 if ($group_acronym_id > '30' && $group_type_id ==  '1')
				  {
#				      $group_acronym = "<a href=\"http://www.ietf.org/dyn/wg/charter/$group_acronym-charter.html\">$group_acronym</a>" ;
#  				      $group_acronym = "<a href=\"$HOST_NAME/$DIR_PROCEEDING/$meeting_number/$group_acronym.html\">$group_acronym</a>" ;
   				      $group_acronym = "<a href=\"/$DIR_PROCEEDING/$meeting_number/$group_acronym.html\">$group_acronym</a>" ;

				  }
				 $agenda_body .= "<tr><td width=\"200\">$room_name</td><td width=\"50\">$area</td><td width=\"100\">$group_acronym</td><td>$group_name";
				
				if ($special_agenda_note)
				  {
			        $agenda_body .= " - <b>$special_agenda_note</b>";
				  }	
				
				 $agenda_body .= " </td></tr>\n";
	
		
	}//End of while ($row_sessions_detail 
$agenda_body .= "</table>\n<br>\n";	
}//ENd of Sunday session else*/

}//END OF FOR LOOP FOR DAYS for ($day_id=0;$day_id<6;$day_id++) 


/**********************************************/
/*CHANGE THE DATABASE NAME LATER*/
#mysql_select_db("ietf_ams", $proceedings_conn);
mysql_select_db($DATABASE_AMS, $proceedings_conn);

/**********************************************/

$query_temp_table_drop = "DROP TABLE temp_agenda$table_id";
$result_temp_table_drop = mysql_query($query_temp_table_drop,$proceedings_conn) or die(mysql_error());


/*END OF THE AGENDA BODY SCRIPT*/


/*FORM THE FINAL HTML FOR AGENDA PAGE*/
$agenda_text = "";
$agenda_text .= "<td id=\"content1\"><div id=\"content2\"><p class=\"ptitle\">IETF"." ".$meeting_number." "."Proceedings </p>";
$agenda_text .= formatMenu();
$agenda_text .= "<h3>Agenda of IETF "." ".$meeting_number."</h3>".$period."<br>";
$agenda_text .= "(<a href=\"agenda.txt\">Plain Text Agenda</a>)<br>";
$agenda_text .= "<p>*** Click on an acronym of the group to get a charter page ***<br>*** Click on a name of the group to get a meeting agenda ***</p>";


$agenda_text .= $agenda_body;
$agenda_text .= $agenda_bottom;
$agenda_text .= "</div></td></tr>";
}/*END OF MEETING EXIST ELSE*/

return $agenda_text;
}

/*END OF FUNCTION genAgendaBody*/

/*BEGIN SCRIPT FOR attendee.html generation*/

$attendee_mainContent = genAttendeeBody();

/*Write to the Acknowledgement file */
$attendee_html=fopen($PROCEEDING_DIR."/".$meeting_number."/attendee.html",'w');


if (! $attendee_html) die("Error opening file");
fwrite($attendee_html,$html_header);
fwrite($attendee_html,$attendee_mainContent);
fwrite($attendee_html,$html_footer);
fclose($attendee_html);

header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/attendee.html');

/*END SCRIPT FOR attendee.html.html generation*/

/**********************************************************************************************************/
/*genAttendeeBody :: Generates the Attendee list
/**********************************************************************************************************/

function genAttendeeBody()
{

// Gets the value from the Session
$meeting_number = $_SESSION['MEETING_NUMBER'];
$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
$html_header= $_SESSION['HTML_HEADER'];
$html_footer= $_SESSION['HTML_FOOTER']; 
$PROCEEDING_DIR = $_SESSION['PROCEEDING_DIR'];
$DATABASE = $_SESSION['DATABASE'];
$DATABASE_AMS = $_SESSION['DATABASE_AMS']; 

$attendee_text = "";
   
$attendee_text = "";
$attendee_text .= "<td id=\"content1\"><div id=\"content2\"><p class=\"ptitle\">IETF"." ".$meeting_number." "."Proceedings </p>";
/*Get the menu bar*/
$attendee_text .= formatMenu();
$attendee_text .= "<h3>Attendee List of IETF $meeting_number meeting</h3>";
$attendee_text .= "<p><table border=\"1\" cellpadding=\"4\" cellspacing=\"0\">";
#$attendee_text .= "<tr><td><strong>Last Name</strong></td><td><strong>First Name</strong></td><td><strong>Organization</strong></td><td><strong>ISO 3166 Code</strong></td><td><strong>Paid</strong></td><tr>";
$attendee_text .= "<tr><td><strong>Last Name</strong></td><td><strong>First Name</strong></td><td><strong>Organization</strong></td><td><strong>ISO 3166 Code</strong></td><tr>";


/*SELCT THE DATABASE*/
mysql_select_db("ietf$meeting_number",$proceedings_conn);

$query_attendee_list = "SELECT  lname, fname, company, country ,paid FROM registrations ORDER BY  lname,fname";
$recordset_attendee_list = mysql_query($query_attendee_list,$proceedings_conn) or die(mysql_error());
while($row_attendee_list = mysql_fetch_assoc($recordset_attendee_list ))
{
	$fname = $row_attendee_list['fname'];
	$lname = $row_attendee_list['lname'];
	$paid = $row_attendee_list['paid'];
	$company = $row_attendee_list['company'];
	$country = $row_attendee_list['country'];
	if ($paid == 1) 
	{
		$paid_status = "YES";
	}
	else
	{
		$paid_status = "NO";
	}
#	$attendee_text .= "<tr><td>$lname</td><td>$fname</td><td>$company</td><td>$country</td><td>$paid_status</td><tr>";
	$attendee_text .= "<tr><td>$lname</td><td>$fname</td><td>$company</td><td>$country</td><tr>";
}//End of while($row_attendee_list = mysql_fetch_assoc($recordset_attendee_list ))

$attendee_text .= "</table>";
return $attendee_text;
}
/*ENd of FUNCTION genAttendeeBody*/

/**********************************************************************************************************/
/*BEGIN SCRIPT FOR GENERATING INDIVISUAL CHARTER PAGES*/
/**********************************************************************************************************/
/*********************************************************************************************************/
/*genArea :: Gets the area names from the database table
/*********************************************************************************************************/

function genArea()
{

// Gets the value from the Session
$meeting_number = $_SESSION['MEETING_NUMBER'];
$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
$html_header= $_SESSION['HTML_HEADER'];
$html_footer= $_SESSION['HTML_FOOTER']; 
$PROCEEDING_DIR = $_SESSION['PROCEEDING_DIR'];
$DATABASE = $_SESSION['DATABASE'];
$DATABASE_AMS = $_SESSION['DATABASE_AMS']; 


/*SELCT THE DATABASE*/
#mysql_select_db("ietf",$proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);

include('constants.php');

$section_number = 0;
$area_text = "<ul>";

$query_area_name = "select acronym, name,acronym_id from areas a, acronym b where a.area_acronym_id=b.acronym_id and a.status_id=1 order by acronym";
$recordset_area_name = mysql_query($query_area_name,$proceedings_conn) or die(mysql_error());

while ($row_area_name = mysql_fetch_assoc($recordset_area_name))
{
  $section_number++;
  /*Get the Area details for every area*/
  $area_acronym = $row_area_name['acronym'];
  $area_name = $row_area_name['name'];
  $area_acronym_id = $row_area_name['acronym_id'];
  /*Now create an area html page with all the details*/

  $area_mainContent = genAreaBody($section_number,$area_name,$area_acronym_id,$area_acronym);



  /*Write the the Area file */
  $area_html=fopen($PROCEEDING_DIR."/".$meeting_number."/$area_acronym.html",'w');


	if (! $area_html) die("Error opening file");
	fwrite($area_html,$html_header);
	fwrite($area_html,$area_mainContent);
	fwrite($area_html,$html_footer);
	fclose($area_html);

	 header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/$area_acronym.html');
 
  
  $area_text .="<li><a href=\"$area_acronym.html\">2.$section_number. $area_name</a></li>";

}

$area_text .="</ul><hr />";

return $area_text;
}//End of genArea function

/*********************************************************************************************************/
/*genAreaBody :: Gets the area names from the database table and gets the group information for each area
and arrange it in proper manner
/*********************************************************************************************************/
function genAreaBody($section_number,$area_name,$area_acronym_id,$area_acronym)
{

// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
	$html_header= $_SESSION['HTML_HEADER'];
	$html_footer= $_SESSION['HTML_FOOTER']; 
	$PROCEEDING_DIR = $_SESSION['PROCEEDING_DIR'];
	$DATABASE = $_SESSION['DATABASE'];
	$DATABASE_AMS = $_SESSION['DATABASE_AMS']; 

//Print the HTML fro the Area page	
	$area_body_text = "";
	$area_body_text .= "<td id=\"content1\"><div id=\"content2\"><p class=\"ptitle\">IETF"." ".$meeting_number." "."Proceedings </p>";
	$area_body_text .= formatMenu();
	$area_body_text .= "<h2>2.$section_number $area_name</h2>";
	$area_body_text .="<h3>Groups that met at IETF $meeting_number</h3>";
#	$area_body_text .="<ul>";

//Get the area details from the database for groups that met
   #$query_groups_meet = "SELECT acronym,name,acronym_id,group_type_id from acronym a, area_group b, groups_ietf c where b.area_acronym_id=$area_acronym_id and b.group_acronym_id=a.acronym_id and b.group_acronym_id=c.group_acronym_id and c.meeting_scheduled_old='YES' and c.status_id = 1 order by acronym";
   
#   $query_groups_meet = "SELECT acronym,name,acronym_id,group_type_id from acronym a, area_group b, groups_ietf c where b.area_acronym_id=$area_acronym_id and b.group_acronym_id=a.acronym_id and b.group_acronym_id=c.group_acronym_id and c.meeting_scheduled_old='YES' and c.status_id = 1 order by group_type_id,acronym";

   $query_groups_meet = "SELECT acronym,name,acronym_id,group_type_id from acronym a, area_group b, groups_ietf c where b.area_acronym_id=$area_acronym_id and b.group_acronym_id=a.acronym_id and b.group_acronym_id=c.group_acronym_id and c.meeting_scheduled_old='YES' order by group_type_id,acronym";

   
   $recordset_groups_meet = mysql_query($query_groups_meet,$proceedings_conn) or die(mysql_error());
   $row_count_groups_meet = mysql_num_rows($recordset_groups_meet);

   $WG_text = "<h4>Working Groups</h4> <ul>";
   $PWG_text = "<h4>Proposed Working Groups</h4> <ul>";
   $BOF_text = "<h4>BoFs</h4> <ul>";
   $AG_text = "<h4>Area Group</h4> <ul>";
   $TEAM_text = "<h4>TEAM</h4> <ul>";
   
/*Check if some records aew present and print accordingly*/   
   if ($row_count_groups_meet > 0)
   {
       $WG_count = 0;
	   $PWG_count = 0;
   	   $BOF_count = 0;
	   $AG_count = 0;
	   $TEAM_count = 0;
	   	
	   while ($row_groups_meet = mysql_fetch_assoc($recordset_groups_meet))
	   {
			$group_acronym = $row_groups_meet['acronym'];
			$group_name = $row_groups_meet['name'];
			$group_acronym_id = $row_groups_meet['acronym_id'];
			$group_type_id = $row_groups_meet['group_type_id'];
			  /*Now create an charter html page for the group with all the details*/
			  
			/*Get the group type name from the group type table to show the groups in the category as per group type*/  
			$query_get_groupname = "SELECT group_type from g_type where group_type_id = $group_type_id";  
			$recordset_get_groupname = mysql_query($query_get_groupname,$proceedings_conn) or die(mysql_error());
			$row_get_groupname = mysql_fetch_assoc($recordset_get_groupname);
			$grouptype = $row_get_groupname['group_type'];

			switch($grouptype)
			  {
				 case "WG":
				 	 $WG_text .= "<li><a href=\"$group_acronym.html\">$group_name ($group_acronym)</a></li>";
					 $WG_count++;
		  			 break;
				case "PWG":	
				 	 $PWG_text .= "<li><a href=\"$group_acronym.html\">$group_name ($group_acronym)</a></li>";
					 $PWG_count++;
		         	 break;
				 case "BOF":	
				 	 $BOF_text .= "<li><a href=\"$group_acronym.html\">$group_name ($group_acronym)</a></li>";
					 $BOF_count++;
		         	 break;
				case "AG":	
				 	 $AG_text .= "<li><a href=\"$group_acronym.html\">$group_name ($group_acronym)</a></li>";
					 $AG_count++;
		         	 break;
				case "TEAM":	
				 	 $TEAM_text .= "<li><a href=\"$group_acronym.html\">$group_name ($group_acronym)</a></li>";
					 $TEAM_count++;
		         	 break;
				 default:
				  	 break;
  			 }

  			$charter_mainContent = genCharterBody($group_name,$group_acronym,$group_acronym_id,$area_name,$area_acronym_id,$group_type_id,$grouptype);
			  /*Write the the charter file */
		    $charter_html=fopen($PROCEEDING_DIR."/".$meeting_number."/$group_acronym.html",'w');


			if (! $charter_html) die("Error opening file");
			fwrite($charter_html,$html_header);
			fwrite($charter_html,$charter_mainContent);
			fwrite($charter_html,$html_footer);
			fclose($charter_html);

#			header('Location: http://devp.amsl.com/proceedings/'.$meeting_number.'/$group_acronym.html');
			header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/$group_acronym.html');

	   }//End of    while ($row_groups_meet = mysql_fetch_assoc($recordset_groups_meet))
	   
   }
   else
   {
	   $area_body_text .="<li>No Groups Present</li>";
      
   }
   
   $WG_text .= "</ul>";
   if ($WG_count !=0)
   {   
      $area_body_text .= $WG_text;
   }
   else
   {
   	  $WG_text = "";	
      $area_body_text .= $WG_text;
   }	  
   
   
   $PWG_text .= "</ul>";
   if ($PWG_count != 0)
   {
	   $area_body_text .= $PWG_text;
   }
   else
   {
	  $PWG_text = ""; 
      $area_body_text .= $PWG_text;
   }   
   
   
   $BOF_text .= "</ul>";
      if ($BOF_count != 0)
   {
   		$area_body_text .= $BOF_text;
   }
   else
   {
   		$BOF_text = "";
		$area_body_text .= $BOF_text;
   }
   
      		
   $AG_text .= "</ul>";
   if ($AG_count !=0)
   {
	   $area_body_text .= $AG_text;
   }
   else
   {
   	   $AG_text = "";
   	   $area_body_text .= $AG_text;
   }   
   
   $TEAM_text .= "</ul>";
   if ($TEAM_count != 0)
   {
   		$area_body_text .= $TEAM_text;
   }
   else
   {
   		$TEAM_text = "";
   		$area_body_text .= $TEAM_text;
   }	

   $area_body_text .="<h3>Groups that did not meet at IETF $meeting_number</h3>";
   
//Get the area details from the database for groups that did not meet   
   
#   $query_groups_not_meet = "SELECT acronym,name,acronym_id,group_type_id from acronym a, area_group b, groups_ietf c where b.area_acronym_id=$area_acronym_id and b.group_acronym_id=a.acronym_id and b.group_acronym_id=c.group_acronym_id and c.status_id = 1 and c.meeting_scheduled_old <> 'YES' order by group_type_id,acronym";

   $query_groups_not_meet = "SELECT acronym,name,acronym_id,group_type_id from acronym a, area_group b, groups_ietf c where b.area_acronym_id=$area_acronym_id and b.group_acronym_id=a.acronym_id and b.group_acronym_id=c.group_acronym_id and c.status_id = 1 and c.meeting_scheduled_old <> 'YES' and group_type_id = 1 order by group_type_id,acronym";


  
   $recordset_groups_not_meet = mysql_query($query_groups_not_meet,$proceedings_conn) or die(mysql_error());
   $row_count_groups_not_meet = mysql_num_rows($recordset_groups_not_meet);

   
   $WG_text = "<h4>Working Groups</h4> <ul>";
   $PWG_text = "<h4>Proposed Working Groups</h4> <ul>";
   $BOF_text = "<h4>BoFs</h4> <ul>";
   $AG_text = "<h4>Area Group</h4> <ul>";
   $TEAM_text = "<h4>TEAM</h4> <ul>";
   
/*Check if some records aew present and print accordingly*/      
   if ($row_count_groups_not_meet > 0)
   {
   
      $WG_not_count = 0;
	  $PWG_not_count = 0;
	  $BOF_not_count = 0;
	  $AG_not_count = 0;
	  $TEAM_not_count = 0;
	  		
      while ($row_groups_not_meet = mysql_fetch_assoc($recordset_groups_not_meet))
      {
  		$group_not_acronym = $row_groups_not_meet['acronym'];
		$group_not_name = $row_groups_not_meet['name'];
		$group_not_acronym_id = $row_groups_not_meet['acronym_id'];
		$group_not_type_id = $row_groups_not_meet['group_type_id'];
		
					  /*Now create an charter html page for the group with all the details*/


			/*Get the group type name from the group type table to show the groups in the category as per group type*/  
			$query_get_groupnotname = "SELECT group_type from g_type where group_type_id = $group_not_type_id";  
			$recordset_get_groupnotname = mysql_query($query_get_groupnotname,$proceedings_conn) or die(mysql_error());
			$row_get_groupnotname = mysql_fetch_assoc($recordset_get_groupnotname);
			$groupnottype = $row_get_groupnotname['group_type'];

			switch($groupnottype)
			  {
				 case "WG":
				 	 $WG_text .= "<li><a href=\"$group_not_acronym.html\">$group_not_name ($group_not_acronym)</a></li>";
					 $WG_not_count++;
		  			 break;
				case "PWG":	
				 	 $PWG_text .= "<li><a href=\"$group_not_acronym.html\">$group_not_name ($group_not_acronym)</a></li>";
					 $PWG_not_count++;
		         	 break;
				 case "BOF":	
				 	 $BOF_text .= "<li><a href=\"$group_not_acronym.html\">$group_not_name ($group_not_acronym)</a></li>";
					 $BOF_not_count++;
		         	 break;
				case "AG":	
				 	 $AG_text .= "<li><a href=\"$group_not_acronym.html\">$group_not_name ($group_not_acronym)</a></li>";
					 $AG_not_count++;
		         	 break;
				case "TEAM":	
				 	 $TEAM_text .= "<li><a href=\"$group_not_acronym.html\">$group_not_name ($group_not_acronym)</a></li>";
					 $TEAM_not_count++;
		         	 break;
				 default:
				  	 break;
  			 }




  			$charter_mainContent = genCharterBody($group_not_name,$group_not_acronym,$group_not_acronym_id,$area_name,$area_acronym_id,$group_not_type_id,$groupnottype);
			  /*Write the the charter file */
		    $charter_html=fopen($PROCEEDING_DIR."/".$meeting_number."/$group_not_acronym.html",'w');


			if (! $charter_html) die("Error opening file");
			fwrite($charter_html,$html_header);
			fwrite($charter_html,$charter_mainContent);
			fwrite($charter_html,$html_footer);
			fclose($charter_html);

#			header('Location: http://devp.amsl.com/proceedings/'.$meeting_number.'/$group_not_acronym.html');
			header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/$group_not_acronym.html');			

      }//End of        while ($row_groups_not_meet = mysql_fetch_assoc($recordset_groups_not_meet))
	}  
  else
   {
	    $area_body_text .= "<li>No Groups present</li>";
   } 

   $WG_text .= "</ul>";
   if ($WG_not_count !=0)
   {
	   $area_body_text .= $WG_text;
	}
	else
	{
	   $WG_text = "";
	   $area_body_text .= $WG_text;
	}   

   
   $PWG_text .= "</ul>";
	if ($PWG_not_count != 0)
	{
	   $area_body_text .= $PWG_text;	
	}
	else
	{
	   $PWG_text = "";
	   $area_body_text .= $PWG_text;		
	}


   
   $BOF_text .= "</ul>";
   if ($BOF_not_count !=0)
   {
   		$area_body_text .= $BOF_text;
	}
	else
	{
		$BOF_text = "";
   		$area_body_text .= $BOF_text;
	}	
   
   
   $AG_text .= "</ul>";
   if ($AG_not_count != 0)
   {
	   $area_body_text .= $AG_text;
   }
   else
   {
   	   $AG_text = "";	
  	   $area_body_text .= $AG_text;
   }
   
   
   $TEAM_text .= "</ul>";
   if ($TEAM_not_count !=0)
   {
	   $area_body_text .= $TEAM_text;
   }
   else
   {
   	   $TEAM_text = "";	
	   $area_body_text .= $TEAM_text;   
   }	   

	  
 return $area_body_text;
}//End of function genArea_body

/*********************************************************************************************************/
/*genCharterBody :: Generates the body of the charter page
/*********************************************************************************************************/

function genCharterBody($group_name,$group_acronym,$group_acronym_id,$area_name,$area_acronym_id,$group_type_id)
{

// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
	$host_proceeding = $_SESSION['HOST_PROCEEDING'];
	$DIR_PROCEEDING = $_SESSION['DIR_PROCEEDING'];
	$DATABASE = $_SESSION['DATABASE'];
	$DATABASE_AMS = $_SESSION['DATABASE_AMS']; 

//Print the HTML fro the charter page	
  $charter_body_text = "";
  $charter_body_text .= "<td id=\"content1\"><div id=\"content2\"><p class=\"ptitle\">IETF"." ".$meeting_number." "."Proceedings </p>";
  $charter_body_text .= formatMenu();
  
  $group_type = "";
  switch($group_type_id)
  {
  case "1":
		 $group_type = "(WG)";
  		 break;
  case "2":
		 $group_type = "(PWG)";
  		 break;
  case "3":
  		 $group_type = "(BoF)";
         break;
  case "4":
		 $group_type = "(AG)";
  		 break;
  case "5":
		 $group_type = "(TEAM)";
  		 break;
  default:
  break;
  }
  $charter_body_text .= "<h2>$group_name ($group_acronym) $group_type</h2>";


/*Get the meeting minutes file information*/


  $meeting_minute_text = getMeetingMinutes($group_acronym_id,$group_acronym,0,0);  

/*ABSOLUTE PATH NEED CHANGE*/
 if ($meeting_minute_text != "")
 {
# 	$meeting_minute_path ="$host_proceeding/$meeting_number/minutes/$meeting_minute_text";
 	$meeting_minute_path ="/$DIR_PROCEEDING/$meeting_number/minutes/$meeting_minute_text";	
	$meeting_minute_html = "<a href=\"$meeting_minute_path\">Minutes</a>";
 }
 else
 {
 	$meeting_minute_html ="No Minutes Submitted";
 }	

 $audio_logs_path = "/audio/ietf$meeting_number/"; 


/* $charter_body_text .="<h3>$meeting_minute_html&nbsp;&nbsp;|&nbsp; Audio Archives&nbsp;&nbsp;|&nbsp;&nbsp;<a href=\"http://jabber.ietf.org/logs/$group_acronym/\">Jabber Logs</a>&nbsp;&nbsp;|&nbsp;&nbsp;<a href=\"http://www.ietf.org/mail-archive/web/$group_acronym/current/maillist.html\">Mailing
List Archives</a></h3>";
*/

 $charter_body_text .="<h3>$meeting_minute_html&nbsp;&nbsp;|&nbsp;<a href=\"$audio_logs_path\">Audio Archives</a>&nbsp;&nbsp;|&nbsp;&nbsp;<a href=\"http://jabber.ietf.org/logs/$group_acronym/\">Jabber Logs</a>&nbsp;&nbsp;|&nbsp;&nbsp;<a href=\"http://www.ietf.org/mail-archive/web/$group_acronym/current/maillist.html\">Mailing
List Archives</a></h3>";


/*Get the additional web information from wg.www.pages table*/
 $charter_body_text .= getAdditionalWeb($group_acronym); 

/*Get the meeting slide file information*/
$meeting_slide_text = "";
$meeting_slide_text = getMeetingSlides($group_acronym_id,$group_acronym,0,0);

#$charter_body_text .="<table width=\"100%\" border=\"0\" cellspacing=\"2\" cellpadding=\"2\"><tr><td valign=\"top\" width=\"60%\"><h3>Meeting Slides</h3>$meeting_slide_text</td>";
$charter_body_text .="<table width=\"60%\" border=\"0\" cellspacing=\"2\" cellpadding=\"2\"><tr>";

/*Get the chairs name*/
$chair_text = "";
$chair_text = getChair($group_acronym_id);
#$charter_body_text .="<td bgcolor=\"#EEEEFF\" width=\"40%\"><h3>Chair(s):</h3>$chair_text";
$charter_body_text .="<td bgcolor=\"#EEEEFF\"><h3>Chair(s):</h3>$chair_text";

/*Get the area directors*/
#$charter_body_text .="<h3>Applications Area Director(s):</h3> <ul><li> <a href=\"mailto:Lisa.Dusseault@messagingarchitects.com\">Lisa Dusseault</a> <br /></li><li> <a href=\"mailto:alexey.melnikov@isode.com\">Alexey Melnikov</a> <br /></li></ul><h3>Applications Area Advisor:</h3><ul><li> <a href=\"mailto:Lisa.Dusseault@messagingarchitects.com\">Lisa Dusseault</a></li></ul></td></tr>";

$area_director_text = "";
$area_director_text = getDirectors($area_acronym_id);
$charter_body_text .="<h3>$area_name Director(s):</h3>$area_director_text"; 

if ($area_acronym_id==1683)
{
 $charter_body_text .="<p>* The Real-time Applications and Infrastructure Area Directors were seated during the IETF 65.</p>";
}

/*Get Applications and area Advisor*/
$area_advisor_text = "";

/*For area advisor we need to have area director id value from groups ietf table so we are querying table grousp_ietf*/
/*Get the AD information */

$query_ad_information ="SELECT status_id,last_modified_date,group_type_id,area_director_id,email_address,email_subscribe,email_keyword,email_archive from groups_ietf where group_acronym_id = $group_acronym_id";

$recordset_ad_information = mysql_query($query_ad_information,$proceedings_conn) or die(mysql_error());

$row_ad_information = mysql_fetch_assoc($recordset_ad_information);
$group_status_id = $row_ad_information['status_id'];
$last_modified_date = $row_ad_information['last_modified_date'];
$group_type_id = $row_ad_information['group_type_id'];
$ad_id = $row_ad_information['area_director_id'];
$email_address = $row_ad_information['email_address'];
$email_subscribe = $row_ad_information['email_subscribe'];
$email_keyword = $row_ad_information['email_keyword'];
$email_archive = $row_ad_information['email_archive'];

$area_advisor_text = getAreaAdvisors($ad_id);
$charter_body_text .= "<h3>$area_name Advisor:</h3>$area_advisor_text";

/*Get the Technical Advisor */
$technical_advisor = getTechnicalAdvisor($group_acronym_id);
$len_tech = strlen($technical_advisor);
if ($len_tech > 9)
{
 $charter_body_text .= "<h3>Technical Advisor(s):</h3>$technical_advisor";
}

/*Get the Group Editors*/
$editor_text = "";
$editor_text = getEditor($group_acronym_id);
$len_editor = strlen($editor_text);
if ($editor_text > 9)
{
 $charter_body_text .= "<h3>Editor(s):</h3>$editor_text";
}
/*Get the Group Secretaries*/
$secretary_text = getSecretary($group_acronym_id);
$len_secretary = strlen($secretary_text);
if ($len_secretary > 9)
{
 $charter_body_text .= "<h3>Secretary(ies):</h3>$secretary_text";
}

$charter_body_text .="</td></tr></table>";


$charter_body_text .= "<h3>Meeting Slides</h3>$meeting_slide_text";

/****************************************************************************************************/
/* CALL SCRIPT TO FETCH THE RESPECTED RFCS AND INTERNET DRAFT FROM FTP TO THE PROPER PLACE FOR EVERY	*/
/* MEETING                                                                                            */
/****************************************************************************************************/

/*If Charter is a Working Group then only print the following information*/
if($group_type_id != 3)
{

	/*Get Internet draft information */
	$internet_draft_text = getInternetDraft($group_acronym_id);
	$charter_body_text .= $internet_draft_text;
	
	/*Get RFC information */
	
	$RFC_text = getRFC($group_acronym);
	$charter_body_text .= $RFC_text;
	
	
	/*Get the Descriptions*/
	$wg_description = getDescription($group_acronym);
	$charter_body_text .= "<h3>Charter (as of $last_modified_date)</h3>";
	$charter_body_text .= "<p>$wg_description</p>";
	
	/*Get goals and milestones*/
	$gm_description = genGM($group_acronym_id);
	$charter_body_text .= "<h3>Goals and Milestones:</h3>$gm_description";
}
 return $charter_body_text;
}

/*********************************************************************************************************/
/*getAdditionalWeb :: Generates additional web information from wg.wwww.pages table
/*********************************************************************************************************/

function getAdditionalWeb($group_acronym)
{

// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
	$html_header= $_SESSION['HTML_HEADER'];
	$html_footer= $_SESSION['HTML_FOOTER']; 
	$PROCEEDING_DIR = $_SESSION['PROCEEDING_DIR'];
	$DATABASE = $_SESSION['DATABASE'];
	$DATABASE_AMS = $_SESSION['DATABASE_AMS']; 


	$additional_web_html = "";

	$query_wg_www = "SELECT area_Name, url, description from wg_www_pages order by area_Name";
    $recordset_wg_www = mysql_query($query_wg_www,$proceedings_conn) or die(mysql_error());
	
	while($row_wg_www = mysql_fetch_assoc($recordset_wg_www))
	{
     	$area_name = $row_wg_www['area_Name'];
		$url_value = $row_wg_www['url'];
		$url_name = $row_wg_www['description'];
		
#		$additional_web_html .= "<p>The area name , url value and names are as $area_name,$url_value,$url_name";

/*       if ($group_acronym == $area_name)
            {
                  if ($area_name == 'ccamp')
				  {
                  $additional_web_html = "<hr>";
                  }
			}	  
       else{

              $additional_web_html = "<p>In addition to this official charter maintained by the IETF Secretariat, there is additional information about this working group on the Web at:<br><a href=\"$url_value\">$url_name</a></p>";
            }

*/


       if ($group_acronym == $area_name)
            {
                  if ($area_name == 'ccamp')
				  {
                  $additional_web_html = "<hr>";
                  }
		       	  else
				  {
	              $additional_web_html = "<p>In addition to this official charter maintained by the IETF Secretariat, there is additional information about this working group on the Web at:<br><a href=\"$url_value\">$url_name</a></p>";
            	  }
				
			}	
            
    }

	$additional_web_html .= "<p>Additional information is available at <a href=\"http://tools.ietf.org/wg/$group_acronym\">tools.ietf.org/wg/$group_acronym</a>";
	


return $additional_web_html;
}
/*********************************************************************************************************/
/*getMeetingMinutes :: Generates the minutes file location for the charter
/*********************************************************************************************************/
function getMeetingMinutes($group_acronym_id,$group_acronym,$irtf,$interim)
{
// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
	$html_header= $_SESSION['HTML_HEADER'];
	$html_footer= $_SESSION['HTML_FOOTER']; 
	$PROCEEDING_DIR = $_SESSION['PROCEEDING_DIR'];

//Get the minute file name from the table

	  $query_minute_file = "SELECT filename from minutes where meeting_num=$meeting_number and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim";
	  
	  $recordset_minute_file = mysql_query($query_minute_file,$proceedings_conn) or die(mysql_error());
	  $row_minute_file = mysql_fetch_assoc($recordset_minute_file);
	  $minute_file = $row_minute_file['filename'];


#$minute_file = $query_minute_file;
  if (!($minute_file))
  {
  	$minute_file = "";
   }	
  
  return $minute_file;

}
/*********************************************************************************************************/
/*getMeetingMinutes :: Generates the slides file location for the charter
/*********************************************************************************************************/
function getMeetingSlides($group_acronym_id,$group_acronym,$irtf,$interim)
{

// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
	$html_header= $_SESSION['HTML_HEADER'];
	$html_footer= $_SESSION['HTML_FOOTER']; 
	$PROCEEDING_DIR = $_SESSION['PROCEEDING_DIR'];
	$host_proceeding = $_SESSION['HOST_PROCEEDING'];
	$DIR_PROCEEDING = $_SESSION['DIR_PROCEEDING'];
//Get the slide file name from the table
    $slide_file = "";
	
#    $query_slide_file = "SELECT slide_num,slide_type_id,slide_name from slides where meeting_num=$meeting_number and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim and in_q=0 order by order_num";
    $query_slide_file = "SELECT slide_num,slide_type_id,slide_name from slides where meeting_num=$meeting_number and group_acronym_id=$group_acronym_id and irtf=$irtf and interim=$interim order by order_num";

	$recordset_slide_file = mysql_query($query_slide_file,$proceedings_conn) or die(mysql_error());

	$num_of_slides = mysql_num_rows($recordset_slide_file);

		
	if ($num_of_slides != 0)
	{
	    $slide_file = "<ul>";
	  while ($row_slide_file = mysql_fetch_assoc($recordset_slide_file))
	  { 
	    $slide_num = $row_slide_file['slide_num'];
	    $slide_type_id = $row_slide_file['slide_type_id'];
	    $slide_name = $row_slide_file['slide_name'];


/*WIth the new conversion mechanism the files are converted to PDF in one strecg but no entry is made to
the Slides table so we need to identify the slides with the slide_type_id for PPT but read them as PDF as
they are already converted to PDF by external script ie slide_type_id 4 and 6*/

/*	    if ($slide_type_id==2)
		{
			$slide_type = "pdf";
		}
	    else
		{
			$slide_type = "txt";
		}
*/


	    switch($slide_type_id){
        	case( $slide_type_id == "4" || $parse_draft == "6"):
			$slide_type = "pdf";
	        break;
		case "2":
			$slide_type = "pdf";
 		break;
		case "3":
			$slide_type = "txt";
 		break;
		case "5":
			$slide_type = "doc";
 		break;
		case "7":
			$slide_type = "wav";
 		break;
		case "8":
			$slide_type = "avi";
 		break;
		case "9":
			$slide_type = "mp3";
 		break;
		default:
		break;
	    }	



	    $slide_url = $group_acronym;   	

	    if ($group_acronym_id== -1)
			{
	          $slide_url = "plenaryw";
    	    } 
		if ($group_acronym_id== -2)
		   {
              $slide_url = "plenaryt";
           }
	    if ($slide_type_id==1) 
		   {
	          $slide_url="$group_acronym-$slide_num/$group_acronym-$slide_num.htm";
    	   } 
		else 
			{
	          $slide_url = "$slide_url-$slide_num.$slide_type";
        	}
			
     	if ($interim)		
		{
	        $slide_url = "i$slide_url";
		}
		
/*ABSOLUTE PATH NEED CHANGE LATER*/		

#        $slide_path = "$host_proceeding/$meeting_number/slides/$slide_url";
        $slide_path = "/$DIR_PROCEEDING/$meeting_number/slides/$slide_url";
        $slide_file .= "<li><a href=\"$slide_path\" target=\"_blank\">$slide_name</a></li>";
	  }//End of while ($row_slide_file = mysql_fetch_assoc($recordset_slide_file))
	  $slide_file .= "</ul>";
	}//End of if ($num_of_slides != 0)
	else
	{
		$slide_file = "No Slides Present";
	}

	return $slide_file;

}
/*********************************************************************************************************/
/*getChair :: Gets the Chiar information for the charter
/*********************************************************************************************************/
function getChair($group_acronym_id)
{
// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];

	
	$chairs_text = "";
	$query_chairs = "SELECT person_or_org_tag from g_chairs where group_acronym_id = $group_acronym_id";
	$recordset_chairs = mysql_query($query_chairs,$proceedings_conn) or die(mysql_error());
	$chairs_text .= "<ul>";
	while ($row_chairs = mysql_fetch_assoc($recordset_chairs))
	{
	   $chair_tag = $row_chairs['person_or_org_tag'];
	   $chair_name = get_name($chair_tag,0);
	   $chair_email = get_email($chair_tag,0);
	   $chairs_text .= "<li><a href=\"mailto:$chair_email\">$chair_name</a></li>";
	}

	$chairs_text .= "</ul>";
	
   return $chairs_text;
}
/*********************************************************************************************************/
/*getDirectors :: Gets the area director information for the charter
/*********************************************************************************************************/
function getDirectors($area_acronym_id)
{
// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
	
	$directors_text = "";
	
    $query_area_directors = "SELECT person_or_org_tag from area_directors where area_acronym_id = $area_acronym_id";
    $recordset_area_directors = mysql_query($query_area_directors,$proceedings_conn) or die(mysql_error());
	$directors_text .= "<ul>";
	while($row_area_directors = mysql_fetch_assoc($recordset_area_directors))
	{
    	$ad_tag = $row_area_directors['person_or_org_tag'];
		$ad_name = get_name($ad_tag,0);
		$ad_email = get_email($ad_tag,0);
		$directors_text .= "<li><a href=\"mailto:$ad_email\">$ad_name</a></li>";
    }
	$directors_text .="</ul>";
	
	return $directors_text;
}
/*********************************************************************************************************/
/*getAreaAdvisors :: Gets the area advisor information for the charter
/*********************************************************************************************************/

function getAreaAdvisors($ad_id)
{
// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];

	$advisors_text = "";
	$advisors_text .="<ul>";
	$query_area_advisor ="SELECT person_or_org_tag from area_directors where id=$ad_id";
	$recordset_area_advisor = mysql_query($query_area_advisor,$proceedings_conn) or die(mysql_error());

	while($row_area_advisor = mysql_fetch_assoc($recordset_area_advisor))
	{
 	$ad_adv_tag = $row_area_advisor['person_or_org_tag'];
	$ad_adv_name = get_name($ad_adv_tag,0);
	$ad_adv_email = get_email($ad_adv_tag,0);
	
	$advisors_text .= "<li><a href=\"mailto:$ad_adv_email\">$ad_adv_name</a></li>";
	}
	$advisors_text .="</ul>";
	return 	$advisors_text;
}
/*********************************************************************************************************/
/*getTechnicalAdvisor :: Gets the Technical advisor information for the charter
/*********************************************************************************************************/

function getTechnicalAdvisor($group_acronym_id)
{
// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];

	$technical_adv_text = "";
	$technical_adv_text .="<ul>";
	$query_technical_advisor ="SELECT person_or_org_tag from g_tech_advisors where group_acronym_id = $group_acronym_id";
	$recordset_technical_advisor = mysql_query($query_technical_advisor,$proceedings_conn) or die(mysql_error());

	while($row_technical_advisor = mysql_fetch_assoc($recordset_technical_advisor))
	{
 	$technical_adv_tag = $row_technical_advisor['person_or_org_tag'];
	$technical_adv_name = get_name($technical_adv_tag,0);
	$technical_adv_email = get_email($technical_adv_tag,0);
	
	$technical_adv_text .= "<li><a href=\"mailto:$technical_adv_email\">$technical_adv_name</a></li>";
	}
	$technical_adv_text .="</ul>";
	return 	$technical_adv_text;

}
/*********************************************************************************************************/
/*getEditor( :: Gets the group Editor information for the charter
/*********************************************************************************************************/

function getEditor($group_acronym_id)
{
// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];

	$editor_text = "";
	$editor_text .="<ul>";
	$query_editor ="SELECT person_or_org_tag from  g_editors where group_acronym_id = $group_acronym_id";
	$recordset_editor = mysql_query($query_editor,$proceedings_conn) or die(mysql_error());

	while($row_editor = mysql_fetch_assoc($recordset_editor))
	{
 	$editor_tag = $row_editor['person_or_org_tag'];
	$editor_name = get_name($editor_tag,0);
	$editor_email = get_email($editor_tag,0);
	
	$editor_text .= "<li><a href=\"mailto:$editor_email\">$editor_name</a></li>";
	}
	$editor_text .="</ul>";
	return 	$editor_text;

}
/*********************************************************************************************************/
/*getEditor( :: Gets the group Editor information for the charter
/*********************************************************************************************************/

function getSecretary($group_acronym_id)
{
// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];

	$secretary_text = "";
	$secretary_text .="<ul>";
	$query_secretary ="SELECT person_or_org_tag from  g_secretaries where group_acronym_id = $group_acronym_id";
	$recordset_secretary = mysql_query($query_secretary,$proceedings_conn) or die(mysql_error());

	while($row_secretary = mysql_fetch_assoc($recordset_secretary))
	{
 	$secretary_tag = $row_secretary['person_or_org_tag'];
	$secretary_name = get_name($secretary_tag,0);
	$secretary_email = get_email($secretary_tag,0);
	
	$secretary_text .= "<li><a href=\"mailto:$secretary_email\">$secretary_name</a></li>";
	}
	$secretary_text .="</ul>";
	return 	$secretary_text;

}

/*********************************************************************************************************/
/*get_name :: Gets the name of the person with person_or_org_tag value
/*********************************************************************************************************/
function get_name($person_or_org_tag,$reverse)
{
// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];

   $query_name = "SELECT first_name,last_name from person_or_org_info where person_or_org_tag = $person_or_org_tag";
   $recordset_name = mysql_query($query_name,$proceedings_conn) or die(mysql_error());
   $row_name = mysql_fetch_assoc($recordset_name);
   $firstname = $row_name['first_name'];
   $lastname = $row_name['last_name'];
   
   if ($reverse)
   {
   		return "$lastname, $firstname";
   }
   else
   {
	   return "$firstname $lastname";
   }
}

/*********************************************************************************************************/
/*get_email :: Gets the email of the person with person_or_org_tag value
/*********************************************************************************************************/
function get_email($person_or_org_tag,$email_priority)
{
// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];

	   $email_priority = 1 ;
   
   
   $query_email= "SELECT email_address from email_addresses where person_or_org_tag = $person_or_org_tag and email_priority=$email_priority";
   $recordset_email = mysql_query($query_email,$proceedings_conn) or die(mysql_error());
   $row_email = mysql_fetch_assoc($recordset_email);
   $email_address = $row_email['email_address'];
   
   return $email_address;

}

/*********************************************************************************************************/
/*getInternetDraft :: Gets the internet draft information 
/*********************************************************************************************************/
function getInternetDraft($group_acronym_id)
{
// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
	$host_proceeding = $_SESSION['HOST_PROCEEDING'];
	$PROCEEDING_DIR = $_SESSION['PROCEEDING_DIR'];
#	$HOST_PRIYANKA = $_SESSION['HOST_PRIYANKA'];
	$HOST_NAME = $_SESSION['HOST_NAME'];
	$DIR_PROCEEDING = $_SESSION['DIR_PROCEEDING'];
	
    $query_internet_draft = "SELECT id_document_name,filename,revision,start_date,revision_date from internet_drafts where group_acronym_id = $group_acronym_id and status_id = 1 and filename <> 'rfc%' order by start_date";
	$recordset_internet_draft = mysql_query($query_internet_draft,$proceedings_conn) or die(mysql_error());
	
	$internet_draft_text = "";

	$count_internet_draft = mysql_num_rows($recordset_internet_draft);
	if ($count_internet_draft > 0)
	{
		$internet_draft_text = "<h3>Internet-Drafts:</h3>";
		$internet_draft_text .= "<ul>";
		while ($row_internet_draft = mysql_fetch_assoc($recordset_internet_draft))
		{
			$id_document_name = $row_internet_draft['id_document_name'];
			$filename = $row_internet_draft['filename'];
			$revision = $row_internet_draft['revision'];
		    $text_file = "$filename-$revision.txt";
/*NEED TO CHANGE TO RELATIVE PATH*/			

			/*Now get the file size in bytes*/
			/*PHP function stat returns an array with files statistics*/
			
/*The internet draft for each charter is stored at ietf-ftp */			
/*Need to copy the respected files from source to destination*/

		    $file_copy_text = "";
			
			$ID_source_file = "/a/www/ietf-ftp/internet-drafts/$text_file";
#			$ID_destination_file = "$PROCEEDING_DIR/$meeting_number/IDs/$text_file";
			$ID_destination_file = "$PROCEEDING_DIR/$meeting_number/id/$text_file";			

			if (!copy($ID_source_file, $ID_destination_file)) {
			    $file_copy_text = "Failed to copy $ID_source_file";
			}
			else
			{
				chmod($ID_destination_file,0744);		
			}
						
#			$stat_file = stat ("/a/www/ietf-ftp/internet-drafts/$text_file");
#			$stat_file = stat ("$PROCEEDING_DIR/$meeting_number/IDs/$text_file");
			$stat_file = stat ("$PROCEEDING_DIR/$meeting_number/id/$text_file");			
			$filesize = $stat_file[7];
			if (!($filesize))    
			  {
				$filesize = 0;
			  }
#   		   $internet_draft_text .= "<li><a href=\"/$DIR_PROCEEDING/$meeting_number/IDs/$text_file\">$id_document_name</a> ($filesize bytes)  $file_copy_text</li>";
   		   $internet_draft_text .= "<li><a href=\"/$DIR_PROCEEDING/$meeting_number/id/$text_file\">$id_document_name</a> ($filesize bytes)  $file_copy_text</li>";			
		}
		$internet_draft_text  .= "</ul>";
	}
	else
	{
 	  $internet_draft_text = "<h3>No Current Internet-Drafts<h3>";
	}
	
	return $internet_draft_text;
}

/*********************************************************************************************************/
/*getRFC :: Gets the RFC information 
/*********************************************************************************************************/

function getRFC($group_acronym)
{

// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
	$host_proceeding = $_SESSION['HOST_PROCEEDING'];
	$PROCEEDING_DIR = $_SESSION['PROCEEDING_DIR'];
#	$HOST_PRIYANKA = $_SESSION['HOST_PRIYANKA'];
	$HOST_NAME = $_SESSION['HOST_NAME'];	
	$DIR_PROCEEDING = $_SESSION['DIR_PROCEEDING'];
	
	$RFC_text = "";


	$query_RFC	="SELECT a.rfc_number,b.status_value,a.rfc_name from rfcs a, rfc_status b where a.group_acronym = '$group_acronym' and a.status_id = b.status_id order by a.rfc_published_date";
#	$RFC_text = $query_RFC;
	
	$recordset_RFC = mysql_query($query_RFC,$proceedings_conn) or die(mysql_error());
	$count_RFC = mysql_num_rows($recordset_RFC);
	
	if ($count_RFC > 0)
	{
		$RFC_text = "<h3>Request for Comments:</h3>";
		$RFC_text .="<ul>";
		
	 	while ($row_RFC = mysql_fetch_assoc($recordset_RFC))
		{
		
			$rfc_number = $row_RFC['rfc_number'];
			$status_value = $row_RFC['status_value'];
			$rfc_name = $row_RFC['rfc_name'];
	
			/*Get the shortform status value*/
			#$status_value_short = getStatus($status_value);		
			
			/*Now get the file size in bytes*/
			/*PHP function stat returns an array with files statistics*/
			

/*The internet draft for each charter is stored at ietf-ftp */			
/*Need to copy the respected files from source to destination*/

		    $rfc_file_copy_text = "";
			
			$RFC_source_file = "/a/www/ietf-ftp/rfc/rfc$rfc_number.txt";
#			$RFC_destination_file = "$PROCEEDING_DIR/$meeting_number/RFCs/rfc$rfc_number.txt";
			$RFC_destination_file = "$PROCEEDING_DIR/$meeting_number/rfc/rfc$rfc_number.txt";			

			if (!copy($RFC_source_file, $RFC_destination_file)) {
			    $rfc_file_copy_text = "Failed to copy $RFC_source_file";
			}
			else
			{
				chmod($RFC_destination_file,0744);		
			}

	
			
			$text_file = "/rfc/rfc$rfc_number.txt";
			$stat_file = stat ("/a/www/ietf-ftp$text_file");
			$filesize = $stat_file[7];
			if (!($filesize))    
			  {
				$filesize = 0;
			  }
	
			/*Form the "obsolete" text*/
			$obs_text = "";
			$obs_query = "SELECT rfc_acted_on from rfcs_obsolete where action='Obsoletes' and rfc_number=$rfc_number";
			$recordset_obs = mysql_query($obs_query) or die(mysql_error());
			$count_obs = mysql_num_rows($recordset_obs);
			if ($count_obs > 0)
			{
				  $obs_text .= "<font color=\"orange\"> obsoletes ";
				  while ($row_obs = mysql_fetch_assoc($recordset_obs))
				  {
				  
					$rfc_acted_on = $row_obs['rfc_acted_on'];
					$obs_text .= "RFC $rfc_acted_on,";
				  }
				$obs_text = substr("$obs_text", 0, -1);
				$obs_text .= "</font>/";
			}
			
			/*Form the "obsoleted by" text*/
			$obs_by_query = "select rfc_number from rfcs_obsolete where action='Obsoletes' and rfc_acted_on=$rfc_number";
			$recordset_obs_by = mysql_query($obs_by_query) or die(mysql_error());
			$count_obs_by = mysql_num_rows($recordset_obs_by);
			if ($count_obs_by > 0)
			{
				 $obs_text .= "<font color=\"red\"> obsoleted by ";
				 while($row_obs_by = mysql_fetch_assoc($recordset_obs_by))
				 {
					$rfc_acted_on = $row_obs_by['rfc_number'] ;
					$obs_text .= "RFC $rfc_acted_on,";
				}
	
				$obs_text = substr("$obs_text", 0, -1);
				$obs_text .= "</font>/";
			}
		
			/*Form the "Updates" text*/
			$obs_updates_query = "select rfc_acted_on from rfcs_obsolete where action='Updates' and rfc_number=$rfc_number";
			$recordset_obs_updates = mysql_query($obs_updates_query) or die(mysql_error());
			$count_obs_updates = mysql_num_rows($recordset_obs_updates);
			if ($count_obs_updates > 0)
			{
				 $obs_text .= "<font color=\"orange\"> Updates ";
				 while($row_obs_updates = mysql_fetch_assoc($recordset_obs_updates))
				 {
					$rfc_acted_on = $row_obs_updates['rfc_acted_on'] ;
					$obs_text .= "RFC $rfc_acted_on,";
				}
	
				$obs_text = substr("$obs_text", 0, -1);
				$obs_text .= "</font>/";
			}
		
		
			/*Form the "Update By" text*/
			$obs_updatedby_query = "select rfc_number from rfcs_obsolete where action='Updates' and rfc_acted_on=$rfc_number";
			$recordset_obs_updatedby = mysql_query($obs_updatedby_query) or die(mysql_error());
			$count_obs_updatedby = mysql_num_rows($recordset_obs_updatedby);
			if ($count_obs_updatedby > 0)
			{
				 $obs_text .= "<font color=\"orange\"> updated by ";
				 while($row_obs_updatedby = mysql_fetch_assoc($recordset_obs_updatedby))
				 {
					$rfc_acted_on = $row_obs_updatedby['rfc_number'] ;
					$obs_text .= "RFC $rfc_acted_on,";
				}
	
				$obs_text = substr("$obs_text", 0, -1);
				$obs_text .= "</font>/";
			}
			
			if ($obs_text)		
			{
				$obs_text = substr("$obs_text", 0, -1);
			}

			  
#		    $RFC_text .= "<li><a href=\"/$DIR_PROCEEDING/$meeting_number/RFCs/rfc$rfc_number.txt\">$rfc_name (RFC $rfc_number)</a> ($filesize bytes) $obs_text 	$rfc_file_copy_text</li>";
		    $RFC_text .= "<li><a href=\"/$DIR_PROCEEDING/$meeting_number/rfc/rfc$rfc_number.txt\">$rfc_name (RFC $rfc_number)</a> ($filesize bytes) $obs_text 	$rfc_file_copy_text</li>";			

	
		}//End of while ($row_RFC = mysql_fetch_assoc($recordset_RFC))
  	   $RFC_text .= "</ul>"; 
	}
	
	else
	{
	$RFC_text .= "<h3>No Request For Comments</h3>"; 
	}
	
  return $RFC_text;
}


/*********************************************************************************************************/
/*getStatus :: Gets the status value short depending upon the value passed
/*********************************************************************************************************/

function getStatus($status_value)
{
  $status_out = "";
		/*Get the correct status value*/		
	switch($status_value){
	case "Proposed Standard":
			   $status_out = "PS";    
				break;
	case "Draft Standard":
			   $status_out = "DS";    
			   break;
	case "Full":
			   $status_out = "S";
			   break;		   
	case "Historic":
		       $status_out = "H";
			   break;			 
	case "Informational":
		       $status_out = "I";
			   break;			 
	case "Experimental":
		       $status_out = "E";
			   break;			 
	default:
	break;
	}
	return $status_out;
}
/*********************************************************************************************************/
/*getDescription :: Get the working group description from the file at the specifiled location
/*********************************************************************************************************/
function getDescription($group_acronym)
{
// Gets the value from the Session

	$web_path = $_SESSION['WEB_PATH'];
	$wg_description = $_SESSION['WG_DESCRIPTION'];
	
	$wg_description_text = "";
	
	$description_filepath = "$web_path/$wg_description/$group_acronym.desc.txt";
	$description_source = fopen($description_filepath,'r');
	if (!$description_source)
	{
		$wg_description_text = "<p>No description available</p>";
	}	
	else
	{
		while(!feof($description_source))
  		{
		   $line = fgets($description_source,5012);
		   $wg_description_text .= "$line<br>";
  		}


		fclose($description_source);
	}
	
    return $wg_description_text;

}
/*********************************************************************************************************/
/*genGM :: Gets the Goals and Milestone information for the working group
/*********************************************************************************************************/

function genGM($group_acronym_id)
{
// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
	$host_proceeding = $_SESSION['HOST_PROCEEDING'];
	
	$GM_text = "";

	$query_GM = "SELECT description,expected_due_date,done,done_date from goals_milestones where group_acronym_id = $group_acronym_id order by expected_due_date,done_date";
    $recordset_GM = mysql_query($query_GM,$proceedings_conn) or die(mysql_error());
	$count_GM = mysql_num_rows($recordset_GM);
	
	if ($count_GM > 0) 
	{
		$GM_text = "<table>";
		while($row_GM = mysql_fetch_assoc($recordset_GM))
		{
		  $description = $row_GM['description'];
		  $expected_due_date = $row_GM['expected_due_date'];
		  $done = $row_GM['done'];

		/*Format the expected date in proper format*/
		  $format = "MY";
		  $f_expected_due_date = formatDate($expected_due_date,$format);
		  $GM_text .= "<tr ALIGN=left VALIGN=\"top\"><td WIDTH=70 VALIGN=\"top\">";
		  if (($done == "Yes")||($done == "YES")||($done == "yes")||($done == "Done")||($done == "DONE")||($done == "done")) 		  
		  	{
      			$GM_text .= "Done";
    		}
		  else 
		    {
      			$GM_text .= "$f_expected_due_date";
    		}
    	  $GM_text .= "</td><td>&nbsp;&nbsp;</td><td>$description</td></tr>";

		}
		$GM_text .= "</table>";	
	}//End of count greater than 0 
	
	return $GM_text;
}
/**********************************************************************************************************/
/*END SCRIPT FOR GENERATING INDIVIDUAL CHARTER PAGES*/
/**********************************************************************************************************/


/*BEGIN SCRIPT FOR admin_plenary.html generation*/


/**********************************************/
/*SELECT THE DATABASE NAME LATER*/
#mysql_select_db("ietf", $proceedings_conn);
$DATABASE = $_SESSION['DATABASE'];
$DATABASE_AMS = $_SESSION['DATABASE_AMS']; 

mysql_select_db($DATABASE, $proceedings_conn);

/**********************************************/

$administrative_plenary_mainContent = genPlenaryBody(-1);

/*Write to the Acknowledgement file */
$administrative_plenary_html=fopen($PROCEEDING_DIR."/".$meeting_number."/administrative-plenary.html",'w');


if (! $administrative_plenary_html) die("Error opening file");
fwrite($administrative_plenary_html,$html_header);
fwrite($administrative_plenary_html,$administrative_plenary_mainContent);
fwrite($administrative_plenary_html,$html_footer);
fclose($administrative_plenary_html);

header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/administrative-plenary.html');

/*END SCRIPT FOR admin_plenary.html generation*/

/**********************************************************************************************************/
/*genPlenaryBody():: Generates the Attendee list
/**********************************************************************************************************/

function genPlenaryBody($group_acronym_id)
{

// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
	$web_path = $_SESSION['WEB_PATH'];
	$dir_proceeding = $_SESSION['DIR_PROCEEDING'];
	$HOST_PROCEEDING = $_SESSION['HOST_PROCEEDING'];

   $plenary_text = "";
   
   /*FORM THE FINAL HTML FOR ADMIN PLENARY PAGE*/

$plenary_text = "";
$plenary_text .= "<td id=\"content1\"><div id=\"content2\"><p class=\"ptitle\">IETF"." ".$meeting_number." "."Proceedings </p>";
/*Get the menu bar*/
$plenary_text .= formatMenu();


/*Get the Correct Planary Name*/
switch($group_acronym_id){
case "-1":
			$plenary_text .= "<h2>Administrative Plenary</h2>";
		 	break;
case "-2":
			$plenary_text .= "<h2>Technical Plenary</h2>";
			break;
default:			
break;
}



/*NEW CODE*/

	$minute_filename = getMeetingMinutes($group_acronym_id,0,0,0);
	$minute_filepath = "/$dir_proceeding/$meeting_number/minutes/$minute_filename";
	$plenary_text .= "<h3><a href=\"$minute_filepath\">Meeting Minutes</a></h3>";	

/*NEW CODE*/



/*OLD CODE*/
/*
$plenary_text .= "<h3>Current Meeting Report</h3>";
$plenary_text .= "<table border=1 bordercolor=\"#0000FF\" width=100% ><tr><td bgcolor=\"#FFFFFF\">";


/*Get the Minutes and Slides for plenary*/

/*$query_minutes_file = "SELECT filename from minutes where meeting_num = $meeting_number and group_acronym_id = '$group_acronym_id'"; 
$recordset_minutes_file = mysql_query($query_minutes_file,$proceedings_conn) or die(mysql_error());

$row_minutes_file = mysql_fetch_assoc($recordset_minutes_file);
$minute_file = $row_minutes_file['filename'];



$minute_filepath = "$web_path/$dir_proceeding/$meeting_number/minutes/$minute_file";
$minute_source = fopen($minute_filepath,'r');
if (!$minute_source)
	{
		$plenary_text .= "<p>No Minutes Available</p>";
	}	
	else
	{
		while(!feof($minute_source))
		{
		  $plenary_line = fgets($minute_source,5012);
		  $plenary_text .=  "$plenary_line<br>";  
		}
		fclose($minute_source);

	}

$plenary_text .= "</td></tr></table>";
*/
/*OLD CODE*/

	
/*Get the slides for Plenary*/

$plenary_text .="<h3>Slides</h3>";
$query_slide_info = "SELECT slide_num,slide_type_id,slide_name from slides where meeting_num=$meeting_number and group_acronym_id=$group_acronym_id order by order_num";
$recordset_slide_info = mysql_query($query_slide_info,$proceedings_conn) or die(mysql_error());
$counts_slide_info = mysql_num_rows($recordset_slide_info);

if ($counts_slide_info > 0)
{
	while($row_slide_info = mysql_fetch_assoc($recordset_slide_info))
	{
		$slide_num = $row_slide_info['slide_num'];
		$slide_type_id = $row_slide_info['slide_type_id'];
		$slide_name = $row_slide_info['slide_name'];
		$slide_type = ($slide_type_id==2)?"pdf":"txt";
        $slide_url = "";
        if ($group_acronym_id == -1)
		{
          $slide_url = "plenaryw";
        } 
		if ($group_acronym_id==-2) 
		{
          $slide_url = "plenaryt";
        }
		
/*NEED TO CHECK THE LOGIC FOR SLIDE TYPE ID*/		
       if ($slide_type_id==1) 
	   	{
          $slide_url="$slide_url-$slide_num/$slide_url-$slide_num.htm";
        }
		else
		{
          $slide_url = "$slide_url-$slide_num.$slide_type";
        }

		$plenary_text  .= "<a href=\"/$dir_proceeding/$meeting_number/slides/$slide_url\" target=\"_blank\">$slide_name</a><br>";
		

	}//End of while

}
else
{
	$plenary_text .= "<p>None received</p>";
}

return $plenary_text;
}
/********END of FUNCTION genPlenaryBody*********/

/*BEGIN SCRIPT FOR tech_plenary.html generation*/

$technical_plenary_mainContent = genPlenaryBody(-2);

/*Write to the Acknowledgement file */
$technical_plenary_html=fopen($PROCEEDING_DIR."/".$meeting_number."/technical-plenary.html",'w');


if (! $technical_plenary_html) die("Error opening file");
fwrite($technical_plenary_html,$html_header);
fwrite($technical_plenary_html,$technical_plenary_mainContent);
fwrite($technical_plenary_html,$html_footer);
fclose($technical_plenary_html);

#header('Location: http://devp.amsl.com/proceedings/'.$meeting_number.'/technical-plenary.html');
header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/technical-plenary.html');

/*END SCRIPT FOR technical-plenary.html generation*/

/**********************************************************************************************************/
/*genTraining():: Generates the Training Sections 
/**********************************************************************************************************/

function genTraining()
{
// Gets the value from the Session
$meeting_number = $_SESSION['MEETING_NUMBER'];
$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
$html_header= $_SESSION['HTML_HEADER'];
$html_footer= $_SESSION['HTML_FOOTER']; 
$PROCEEDING_DIR = $_SESSION['PROCEEDING_DIR'];


$tr_section_number = 0;
$training_text = "<ul>";

$query_training_name = "SELECT group_acronym_id,acronym,name from acronym a, wg_meeting_sessions b where group_acronym_id=acronym_id and group_acronym_id < '-2' and meeting_num=$meeting_number and group_acronym_id not in (-16,-14,-13,-8,-23,-26)";
$recordset_training_name = mysql_query($query_training_name,$proceedings_conn) or die(mysql_error());

while ($row_training_name = mysql_fetch_assoc($recordset_training_name))
{
  $tr_section_number++;
  /*Get the Area details for every area*/
  $group_acronym_id = $row_training_name['group_acronym_id'];
  $acronym = $row_training_name['acronym'];
  $name = $row_training_name['name'];
  /*Now create an Training html page with all the details*/

#  $training_mainContent = genTrainingBody($section_number,$area_name,$area_acronym_id,$area_acronym);
  $training_mainContent = genTrainingBody($tr_section_number,$group_acronym_id,$acronym,$name);


  /*Write the the Training file */
  $training_html=fopen($PROCEEDING_DIR."/".$meeting_number."/$acronym.html",'w');


	if (! $training_html) die("Error opening file");
	fwrite($training_html,$html_header);
	fwrite($training_html,$training_mainContent);
	fwrite($training_html,$html_footer);
	fclose($training_html);

#	header('Location: http://devp.amsl.com/proceedings/'.$meeting_number.'/$acronym.html');
   header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/$acronym.html');	
 
  
  $training_text .="<li><a href=\"$acronym.html\">4.$tr_section_number. $name </a></li>";

}

$training_text .="</ul><hr />";

return $training_text;
}
/*End of genTraining()

/**********************************************************************************************************/
/*genTrainingBody():: Generates the Individual Training Pages
/**********************************************************************************************************/

function genTrainingBody($tr_section_number,$group_acronym_id,$acronym,$name)
{
// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
	$html_header= $_SESSION['HTML_HEADER'];
	$html_footer= $_SESSION['HTML_FOOTER']; 
	$HOST_PROCEEDING = $_SESSION['HOST_PROCEEDING'];
	$DIR_PROCEEDING = $_SESSION['DIR_PROCEEDING'];
	
//Print the HTML fro the Training page	
	$training_body_text = "";
	$training_body_text .= "<td id=\"content1\"><div id=\"content2\"><p class=\"ptitle\">IETF"." ".$meeting_number." "."Proceedings </p>";
	$training_body_text .= formatMenu();
	$training_body_text .= "<h2>4.$tr_section_number $name Training</h2>";
	$training_body_text .= "<h3>Slides</h3>";

	$query_training_slide_info = "SELECT slide_num,slide_type_id,slide_name from slides where meeting_num=$meeting_number and group_acronym_id=$group_acronym_id order by order_num";
	$recordset_training_slide_info = mysql_query($query_training_slide_info,$proceedings_conn) or die(mysql_error());
	$counts_training_slide_info = mysql_num_rows($recordset_training_slide_info);

	if ($counts_training_slide_info > 0)
	{
		while($row_training_slide_info = mysql_fetch_assoc($recordset_training_slide_info))
		{
				$slide_num = $row_training_slide_info['slide_num'];
				$slide_type_id = $row_training_slide_info['slide_type_id'];
				$slide_name = $row_training_slide_info['slide_name'];
				$slide_type = ($slide_type_id==2)?"pdf":"txt";
				$slide_url = $acronym;
				
		/*NEED TO CHECK THE LOGIC FOR SLIDE TYPE ID*/		
			   if ($slide_type_id==1) 
				{
				  $slide_url="$slide_url-$slide_num/$slide_url-$slide_num.htm";
				}
				else
				{
				  $slide_url = "$slide_url-$slide_num.$slide_type";
				}
		
				$training_body_text  .= "<a href=\"/$DIR_PROCEEDING/$meeting_number/slides/$slide_url\" target=\"_blank\">$slide_name</a><br>";

	}//End of while

}
else
{
		$training_body_text .= "<p>None received</p>";
}
return $training_body_text;

}
/*End of genTrainingBody()*/


/**********************************************************************************************************/
/*genIRTF():: Generates the IRTF Sections 
/**********************************************************************************************************/
function genIRTF()
{

// Gets the value from the Session
$meeting_number = $_SESSION['MEETING_NUMBER'];
$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
$html_header= $_SESSION['HTML_HEADER'];
$html_footer= $_SESSION['HTML_FOOTER']; 
$PROCEEDING_DIR = $_SESSION['PROCEEDING_DIR'];


/*Get the IRTF section information from the database table*/

$query_IRTF = "SELECT info_text from general_info where info_name='irtf'";
$recordset_IRTF = mysql_query($query_IRTF,$proceedings_conn) or die(mysql_error());
$row_IRTF = mysql_fetch_assoc($recordset_IRTF);
$info_text = (html_entity_decode($row_IRTF['info_text']));

$irtf_info_mainContent = genIrtfInfoBody($info_text);
/*Now create the IRTF.html conatining the IRTF information from the database.*/

$irtf_info_html=fopen($PROCEEDING_DIR."/".$meeting_number."/irtf.html",'w');

	if (! $irtf_info_html) die("Error opening file");
	fwrite($irtf_info_html,$html_header);
	fwrite($irtf_info_html,$irtf_info_mainContent);
	fwrite($irtf_info_html,$html_footer);
	fclose($irtf_info_html);

#	header('Location: http://devp.amsl.com/proceedings/'.$meeting_number.'/irtf.html');
   header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/irtf.html');	
 




/*Now Get the remaining IRTF groups associated with the respective meeting in seperate HTML*/
$rg_irtf_mainContent = genRGIRTFBody();


$rg_irtf_html =fopen($PROCEEDING_DIR."/".$meeting_number."/rg_irtf.html",'w');

	if (! $rg_irtf_html) die("Error opening file");
	fwrite($rg_irtf_html,$html_header);
	fwrite($rg_irtf_html,$rg_irtf_mainContent);
	fwrite($rg_irtf_html,$html_footer);
	fclose($rg_irtf_html);

#	header('Location: http://devp.amsl.com/proceedings/'.$meeting_number.'/irtf.html');
   header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/rg_irtf.html');	

$IRTF_text = "";
$IRTF_text .= "<ul>";
$IRTF_text .= "<li><a href=\"irtf.html\">5.1. IRTF introduction</a></li>";
$IRTF_text .= "<li><a href=\"rg_irtf.html\">5.2. Research Groups</a></li>";




/*Now Print the remaining IRTF groups associated with the respective meeting*/
/*$query_irtf_name = "SELECT irtf_id, irtf_acronym, irtf_name FROM irtf a, wg_meeting_sessions b WHERE b.group_acronym_id = a.irtf_id AND b.meeting_num = $meeting_number AND b.irtf = '1'";
$recordset_irtf_name = mysql_query($query_irtf_name,$proceedings_conn) or die(mysql_error());

while ($row_irtf_name = mysql_fetch_assoc($recordset_irtf_name))
{
  $irtf_section_number++;

  /*Get the IRTF details */
  /*$irtf_id = $row_irtf_name['irtf_id'];
  $irtf_acronym = $row_irtf_name['irtf_acronym'];
  $irtf_name = $row_irtf_name['irtf_name'];
*/
  /*Now create an IRTF html page with all the details*/
  //$irtf_mainContent = genIRTFBody($irtf_section_number,$irtf_id,$irtf_acronym,$irtf_name);

  /*Write the the Training file */
  //$irtf_html=fopen($PROCEEDING_DIR."/".$meeting_number."/$irtf_acronym.html",'w');


	/*if (! $irtf_html) die("Error opening file");
	fwrite($irtf_html,$html_header);
	fwrite($irtf_html,$irtf_mainContent);
	fwrite($irtf_html,$html_footer);
	fclose($irtf_html);
*/
#	header('Location: http://devp.amsl.com/proceedings/'.$meeting_number.'/$irtf_acronym.html');
  #  header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/$irtf_acronym.html');

#  $IRTF_text .="<li><a href=\"$irtf_acronym.html\">5.$irtf_section_number. $irtf_name ($irtf_acronym)</a></li>";

//}



$IRTF_text .="</ul><hr />";

return $IRTF_text;

}
/*End of functiongenIRTF()*/

/**********************************************************************************************************/
/*genIrtfInfoBody:: Generates the IRTF Information Page
/**********************************************************************************************************/

function genIrtfInfoBody($info_text)
{
// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
	$html_header= $_SESSION['HTML_HEADER'];
	$html_footer= $_SESSION['HTML_FOOTER']; 
	$HOST_PROCEEDING = $_SESSION['HOST_PROCEEDING'];
	
	
//Print the HTML fro the Training page	
	$IrtfInfo_body_text = "";
	$IrtfInfo_body_text .= "<td id=\"content1\"><div id=\"content2\"><p class=\"ptitle\">IETF"." ".$meeting_number." "."Proceedings </p>";
	$IrtfInfo_body_text .= formatMenu();
	$IrtfInfo_body_text .= $info_text;

return $IrtfInfo_body_text;

}


/**********************************************************************************************************/
/*genRGIRTFBody:: Generates the Research Group IRTF Pages
/**********************************************************************************************************/
function genRGIRTFBody()
{
	
// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
	$html_header= $_SESSION['HTML_HEADER'];
	$html_footer= $_SESSION['HTML_FOOTER']; 
	$HOST_PROCEEDING = $_SESSION['HOST_PROCEEDING'];
	$DIR_PROCEEDING = $_SESSION['DIR_PROCEEDING'];
    $HOST_NAME = $_SESSION['HOST_NAME'];
	$PROCEEDING_DIR = $_SESSION['PROCEEDING_DIR'];
	
//Print the HTML fro the Training page	
	$rg_irtf_text = "";
	$rg_irtf_text .= "<td id=\"content1\"><div id=\"content2\"><p class=\"ptitle\">IETF"." ".$meeting_number." "."Proceedings </p>";
	$rg_irtf_text .= formatMenu();
	$rg_irtf_text .= "<h2>5.2 Research Groups </h2>";
	$rg_irtf_text .= "<ul>";


	$query_irtf_name = "SELECT irtf_id, irtf_acronym, irtf_name FROM irtf a, wg_meeting_sessions b WHERE b.group_acronym_id = a.irtf_id AND b.meeting_num = $meeting_number AND b.irtf = '1'";
	$recordset_irtf_name = mysql_query($query_irtf_name,$proceedings_conn) or die(mysql_error());

while ($row_irtf_name = mysql_fetch_assoc($recordset_irtf_name))
{

  /*Get the IRTF details */
  $irtf_id = $row_irtf_name['irtf_id'];
  $irtf_acronym = $row_irtf_name['irtf_acronym'];
  $irtf_name = $row_irtf_name['irtf_name'];


  /*Now create an IRTF html page with all the details*/
  $irtf_mainContent = genIRTFBody($irtf_section_number,$irtf_id,$irtf_acronym,$irtf_name);

  /*Write the the Training file */
  $irtf_html=fopen($PROCEEDING_DIR."/".$meeting_number."/$irtf_acronym.html",'w');


	if (! $irtf_html) die("Error opening file");
	fwrite($irtf_html,$html_header);
	fwrite($irtf_html,$irtf_mainContent);
	fwrite($irtf_html,$html_footer);
	fclose($irtf_html);

#	header('Location: http://devp.amsl.com/proceedings/'.$meeting_number.'/$irtf_acronym.html');
    header('Location: $HOST_NAME/$DIR_PROCEEDING/'.$meeting_number.'/$irtf_acronym.html');

    $rg_irtf_text .="<li><a href=\"$irtf_acronym.html\"> $irtf_name ($irtf_acronym)</a></li>";

}//End of While ($row_irtf_name = mysql_fetch_assoc($recordset_irtf_name))
	
	
	$rg_irtf_text .= "</ul>";
	
	return $rg_irtf_text;
}/*End of function genIRTFBody*/


/**********************************************************************************************************/
/*genIRTFBody:: Generates the IRTF Pages
/**********************************************************************************************************/
function genIRTFBody($irtf_section_number,$irtf_id,$irtf_acronym,$irtf_name)
{

// Gets the value from the Session

	$meeting_number = $_SESSION['MEETING_NUMBER'];
	$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
	$html_header= $_SESSION['HTML_HEADER'];
	$html_footer= $_SESSION['HTML_FOOTER']; 
	$HOST_PROCEEDING = $_SESSION['HOST_PROCEEDING'];
	$DIR_PROCEEDING = $_SESSION['DIR_PROCEEDING'];

	
	
	
//Print the HTML fro the Training page	
	$irtf_body_text = "";
	$irtf_body_text .= "<td id=\"content1\"><div id=\"content2\"><p class=\"ptitle\">IETF"." ".$meeting_number." "."Proceedings </p>";
	$irtf_body_text .= formatMenu();
	$irtf_body_text .= "<h2>5.$irtf_section_number $irtf_name ($irtf_acronym)</h2>";


/*Get the Minutes file information from getMeetingMinutes*/
	$irtf = $irtf_id;
	$irtf_minutes_filename = getMeetingMinutes($irtf_id,$irtf_acronym,$irtf,0);
	$minute_filepath = "/$DIR_PROCEEDING/$meeting_number/minutes/$irtf_minutes_filename";
	$irtf_body_text .= "<h3><a href=\"$minute_filepath\">Meeting Minutes</a></h3>";	
	
/*Get the IRTF slide file information*/
	$irtf_slide_text = "";
	$irtf_slide_text = getMeetingSlides($irtf_id,$irtf_acronym,$irtf_id,0);
	$irtf_body_text .="<h3>Meeting Slides</h3>$irtf_slide_text";


return $irtf_body_text;

}/*End of function genIRTFBody*/



/****************MAIN PAGE CODE****************************************************************************/

/**********************************************************************************************************/
/*BEGIN SCRIPT FOR GENERATING THE MAIN PROCEEDING HTML PAGE*/
/**********************************************************************************************************/


/*Now get the name of proper proceeding file */
$PROCEEDING_FILENAME = "index.html";

$DIR_PROCEEDING = $_SESSION['DIR_PROCEEDING'] ;
#$HOST_PRIYANKA = $_SESSION['HOST_PRIYANKA'];
$HOST_NAME = $_SESSION['HOST_NAME'];

/*Get the main body of the final proceeding*/
#$html_mainContent = get_body($meeting_number,$proceedings_conn,$html_header,$html_footer);
$html_mainContent = get_body();		
/*Write to the final Proceeding HTML file */

$proceeding_html=fopen($PROCEEDING_DIR."/".$meeting_number."/".$PROCEEDING_FILENAME,'w');

if (! $proceeding_html) die("Error opening file");
fwrite($proceeding_html,$html_header);
fwrite($proceeding_html,$html_mainContent);
fwrite($proceeding_html,$html_footer);
fclose($proceeding_html);

header('Location: http://www.ietf.org/proceedings/'.$meeting_number.'/'.$PROCEEDING_FILENAME);


session_destroy(); 
exit;

/*END SCRIPT FOR GENERATING THE MAIN PROCEEDING HTML PAGE*/

/**********************************************************************************************************
* Function name : get_body()
* Description   : Generates HTML Body for the Final Proceedings main page
**********************************************************************************************************/

#function get_body($meeting_number,$proceedings_conn,$html_header,$html_footer)
function get_body()
{

// Gets the value from the Session
$meeting_number = $_SESSION['MEETING_NUMBER'];
$proceedings_conn = $_SESSION['PROCEEDINGS_CONN'];
$html_header= $_SESSION['HTML_HEADER'];
$html_footer= $_SESSION['HTML_FOOTER']; 
$PROCEEDING_DIR = $_SESSION['PROCEEDING_DIR'];
$DATABASE = $_SESSION['DATABASE'];
$DATABASE_AMS = $_SESSION['DATABASE_AMS']; 

/**********************************************/
/*SELECT THE DATABASE NAME LATER*/
#mysql_select_db("ietf", $proceedings_conn);
mysql_select_db($DATABASE, $proceedings_conn);

/**********************************************/
$query_meeting_details = "select start_date,end_date,city,state,country from meetings where meeting_num= $meeting_number";
$recordset_meeting_details = mysql_query($query_meeting_details, $proceedings_conn) or die(mysql_error());
$row_meeting_details = mysql_fetch_assoc($recordset_meeting_details);
$totalRows_meeting_details = mysql_num_rows($recordset_meeting_details);

/*GET THE LOCATION OF THE MEETING AND FOR OUTSIDE US NO STATE VALUE*/

if ($row_meeting_details['state'] != ""){
	$location = $row_meeting_details['city'].", ".$row_meeting_details['state'].", ".$row_meeting_details['country'];
}else {
$location = $row_meeting_details['city'].", ".$row_meeting_details['country'];
}

/*GET THE TIME FRAME OF THE MEETING CHECK IF START MONTH END MONTH IS SAME OR NOT*/

$period = getPeriod($row_meeting_details['start_date'],$row_meeting_details['end_date']);

/*GET THE TABLE OF CONTEEND INFORMATION*/

$body_text ="<title>IETF"." ".$meeting_number." "."Proceedings"."</title>";
$body_text .= "<td id=\"content1\"><div id=\"content2\"><p class=\"ptitle\">IETF"." ".$meeting_number." "."Proceedings </p>";
$body_text .=  "<h2>".$location ."<br />". $period." </h2>";
$body_text .=  "<h3>Table of Contents</h3>";

$body_text .= formatMenu();
$body_text .= "<hr>";
#$body_text .= "<h3><a name=\"intro\" id=\"intro\"></a>1. Introduction </h3><ul><li><a href=\"acknowledgement.html\">1.1. Acknowledgements</a></li><li><a href=\"overview.html\">1.2. IETF Overview</a></li><li><a href=\"progress-report.html\">1.3. Progress Report</a></li><li><a href=\"agenda.html\">1.4. Agenda</a></li><li><a href=\"attendee.html\">1.5. Attendees</a></li><li><a href=\"http://www.ietf76.jp/special_events/\">1.6. Social Event Information</a></li></ul><hr />";
$body_text .= "<h3><a name=\"intro\" id=\"intro\"></a>1. Introduction </h3><ul><li><a href=\"acknowledgement.html\">1.1. Acknowledgements</a></li><li><a href=\"overview.html\">1.2. IETF Overview</a></li><li><a href=\"progress-report.html\">1.3. Progress Report</a></li><li><a href=\"agenda.html\">1.4. Agenda</a></li><li><a href=\"attendee.html\">1.5. Attendees</a></li></ul><hr />";

$body_text .="<h3><a name=\"wgreports\" id=\"wgreports\"></a>2. Area, Working Group and BoF Reports </h3>";



/*Now get the different areaa from function genArea*/
$body_text .= genArea();

$body_text.="<h3><a name=\"plenary\" id=\"plenary\"></a>3. Plenaries</h3><ul><li><a href =\"administrative-plenary.html\">3.1.  Administrative Plenary</a></li>";
$body_text.="<li><a href=\"technical-plenary.html\">3.2.  Technical Plenary</a></li></ul><hr />";

/*Now get the training sessions*/
$body_text.="<h3><a name=\"training\" id=\"training\">4. Training</h3>";
$body_text.= genTraining();


$body_text.= "<h3><a name=\"irtf\" id=\"irtf\">5. Internet Research Task Force </h3>";

/*Now get the IRTF*/
$body_text .= genIRTF();
$body_text .= "</div></td></tr>";

return $body_text;
} 
/*End of function get_body*/

/**********************************************************************************************************/
/*BEGIN SCRIPT FOR GENERATING THE MAIN PROCEEDING HTML PAGE*/
/**********************************************************************************************************/

/*SOME COMMON FUNCTIONS*/
/*********************************************************************************************************/
/*formatDate :: Splits the date into array and adjusts to the desired timestamp format format */
/*********************************************************************************************************/
function formatDate($inputDate,$format){

$input_date_parts = explode("-",$inputDate);
$formated_input_date = mktime(12,0,0,$input_date_parts[1],$input_date_parts[2],$input_date_parts[0]);

	switch($format){
	case "dFy":
			   $output_date = date('d-F-y',$formated_input_date);    
				break;
	case "FY":
			   $output_date = date('F Y',$formated_input_date);    
			   break;
	case "F":
			   $output_date = date('F',$formated_input_date);
			   break;		   
	case "FdY":
		       $output_date = date('F d,Y',$formated_input_date);
			   break;			 
	case "MY":
		       $output_date = date('M Y',$formated_input_date);
			   break;			 
			   
	default:
	break;
	}
return $output_date;

}/*END OF formatDate*/
/*********************************************************************************************************/
/*formatDate :: Splits the date into array and adjusts to the desired timestamp format format */
/*********************************************************************************************************/

function getPeriod($inputdate1,$inputdate2){
$start_date = explode("-",$inputdate1);
$end_date = explode("-",$inputdate2);
if ($start_date[1] == $end_date[1])
{
	/*Format the date in proper format*/
	$format = "F";
	$month_verbal = formatDate($inputdate1,$format);
 	$period = $month_verbal." ".$start_date[2]."-".$end_date[2].", ".$start_date[0];
}
else{
	$format = "F";
	$month_verbal_start = formatDate($inputdate1,$format);
	$month_verbal_end = formatDate($inputdate2,$format);

 $period = $month_verbal_start." ".$start_date[2]."-".$month_verbal_end.$end_date[2].", ".$start_date[0];
}

return $period;
}/*END OF getPeriod*/

/*********************************************************************************************************/
/*formatMenu :: formats the menu 
/*********************************************************************************************************/
function formatMenu(){
$menu_text = "";
$proceeding_html = "index.html";
$menu_text .= "<p><a href=\"$proceeding_html#intro\">Introduction</a>&nbsp;&nbsp;|&nbsp; <a href=\"$proceeding_html#wgreports\">Area, Working Goup &amp; BoF Reports</a>&nbsp;&nbsp;|&nbsp; <a href=\"$proceeding_html#plenary\">Plenaries</a>&nbsp;&nbsp;|&nbsp; <a href=\"$proceeding_html#training\">Training</a>&nbsp;&nbsp;|&nbsp; <a href=\"$proceeding_html#irtf\">Internet Research Task Force</a></p>";
return $menu_text;



}/*END OF FUNCTION formatMenu*/



?>
