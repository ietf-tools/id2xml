<?php
/****************************************************************************************************
* Script Name : proceedings_generator.php
* Author Name : Priyanka Narkar
* Date        : 2009/12/07
* Description : This is the HTML form for Proceeding Generator
/****************************************************************************************************/


include('header.php'); 
require_once('Connections/proceedings_conn.php'); 
include('redirect.php');
include('constants.php');
?>

<!--JAVASCRIPT BEGINS-->
<SCRIPT language="javascript">
function send(selectboxName)
{
	var chosen;
	chosen = selectboxName.options[selectboxName.selectedIndex].value
	document.frmproceeding_generator.hdn_meeting_number.value = chosen;

}
</SCRIPT>
<!--JAVASCRIPT ENDS-->
<?php
/*CHECK IF THE USER IS AUTHORIZE TO VIEW THE PAGE*/
/*session_start();
if(!isset($_SESSION["USERNAME"]))
{
/*IF NOT THROW LOGIN PAGE*/
/*   header('Location: login_proceedings.php');
   exit;
}
else
{ */  
#   mysql_select_db($database_proceedings_conn, $proceedings_conn);
   mysql_select_db($database_proceedings_conn, $proceedings_conn);

	
	$query_meeting_num = "SELECT proceedings.meeting_num, dir_name FROM proceedings ORDER BY proceedings.meeting_num";
	$recordset_meeting_num = mysql_query($query_meeting_num, $proceedings_conn) or die(mysql_error());
	
	while ($row_meeting_num = mysql_fetch_assoc($recordset_meeting_num))
	{
		$meeting_number = $row_meeting_num['meeting_num'];
		$dir_name = $row_meeting_num['dir_name'];
		$options.="<OPTION VALUE=\"$meeting_number\">".$meeting_number; 
	}

?>

<form name="frmproceeding_generator" action="create_proceeding_final.php" method="post">
<tr><td width="10%"><h2 class="small">Select Meeting :</h2></td><td width="90%"><select name="selMeeting" onChange="return send(this)"><?php echo $options; ?></select></td></tr>
<tr><td colspan="2"><p>
  <input type="submit" value="Generate final proceedings">
</p>
    <p>&nbsp;</p>
    <p>&nbsp;</p>
    <p>&nbsp;</p>
    <p>&nbsp;</p>
    <p>&nbsp;</p>
    <p>&nbsp;</p>
    <p>&nbsp;</p>
    <p>&nbsp;</p>
    <p>&nbsp;</p>
    <p>&nbsp; </p></td></tr>
<tr><td colspan="2"></td></tr>
<tr><td colspan="2"></td></tr>
<tr><td colspan="2"></td></tr>
<tr><td colspan="2"></td></tr>
<?php
  include('footer.php');
?>
</table>
<input type="hidden" name="hdn_meeting_number">
<?php
	mysql_free_result($recordset_meeting_num);

//}//End of else for if(!isset($_SESSION["USERNAME"]))
?>
</form>
</body>
</html>
