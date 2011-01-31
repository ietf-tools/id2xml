<?php
/****************************************************************************************************
* Script Name : proceedings_conn.php
* Author Name : Priyanka Narkar
* Date        : 2009/12/07
* Description : This is Database Connection details page. 
                It connects to the database using all the constants from constants.php
*               If need to change any constants please make changes to constants.php
/****************************************************************************************************/
include('constants.php');

$hostname_proceedings_conn = $HOSTNAME;
$database_proceedings_conn = $DATABASE;
$username_proceedings_conn = $USERNAME;
$password_proceedings_conn = $PASSWORD;
$proceedings_conn = mysql_pconnect($hostname_proceedings_conn, $username_proceedings_conn, $password_proceedings_conn) or trigger_error(mysql_error(),E_USER_ERROR); 


?>