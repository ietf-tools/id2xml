<?php
/****************************************************************************************************
* Script Name : verify.php
* Author Name : Priyanka Narkar
* Date        : 2009/12/14
* Description : The verify.php scripts verifies that user is an authorized secretariat member to visit the
                Proceeding manager.
/****************************************************************************************************/
include('header.php');
require_once('Connections/proceedings_conn.php'); 

#$page = "proceeding_main.php";
$page = "proceeding_generator.php";

mysql_select_db("ietf", $proceedings_conn);

#mysql_select_db($database_proceedings_conn, $proceedings_conn);

#user_level = 0 ==> SECRETARIAT MEMBER
$query_login = "SELECT login_name,password FROM iesg_login where user_level = 0";
$recordset_login = mysql_query($query_login, $proceedings_conn) or die(mysql_error());
$row_login = mysql_fetch_assoc($recordset_login);

$found = 0;
while ($row_login = mysql_fetch_assoc($recordset_login)){ 

  if ($row_login['login_name'] == $_POST["user_name"])
	$found = 1;
}
if ($found == 0)
{
   header('Location: login_proceedings.php?login_error=1');
   exit;
}

if($found == 1)
{
   session_start();
   $_SESSION["USERNAME"]=$_POST["user_name"];
   $_SESSION["PASSWORD"] = $_POST["password"];
   header('Location: '.$page);
   exit;
}
else
{
   header('Location: login_proceedings.php?login_error=1');
   exit;
}

?>

</body>
</html>
