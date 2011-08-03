<?php
/****************************************************************************************************
* Script Name : redirect.php
* Author Name : Priyanka Narkar
* Date        : 2009/12/10
* Description : Two functions


1)check_data : Validates the input data send by user and sets the data status depends on the value
2)redirect : The redirect function redirects the program flow d epending upon the link value passed
                from the calling script.
/****************************************************************************************************/
function check_data($data,$datatype,$data_name){
/* check data validates the input data to the form by striping the special characters and slashes*/
$data_status = 0;	
	switch($datatype){
	case "1":
         /*case 1 : checks if the data enter is not empty and its numeric */	
	     if ($data == ""){
   	         $data_status = 1;
			 $data_message = "$data_name"." is empty";
		 }	 
		 elseif	(!is_numeric($data)){
		     $data_status = 1;
			 $data_message = "$data_name"." is not numeric";
		 }
	break;
	case "2":
	     /*case 2 : checks if the data enter is not empty and its a date */	
	     if ($data == ""){
   	         $data_status = 1;
			 $data_message = "$data_name"." is empty";			 
		 }	 
		 else{
  		     $aDate_parts = preg_split("/[\s-]+/", $data);
             if (!is_numeric($aDate_parts[0])){
		          $data_status = 1;
  			      $data_message = "$data_name"." is not numeric";				  
			 } 
		 }
	break;
	case "3":
	     /*case 3 : checks if the data enter is not empty and its ALPHABETIC */	
	     if ($data == ""){
   	         $data_status = 1;
			 $data_message = "$data_name"." is empty";			 
		 }
		 elseif (!is_alpha($data)){
		     $data_status = 1;
			 $data_message = "$data_name"." is not alphabetic";
		 }	 
		 
		 
	break;
	default:
	break;
	}
return array($data_status,$data_message);
}

/*Redirects the flow as per the link value passed*/

function redirect($link){
    switch ($link) {
    case "create_proceeding":
      $dest_link = "create_proceeding_main.php";
      break;    
    case "open_meeting":
      $dest_link = "open_meeting.php";
      break;
	 default:
	  break;
    }
  return $dest_link;
}


/* Checks if a string contains only alpha characters.*/

function is_alpha($someString)
{
return (preg_match("/[A-Z\s_]/i", $someString) > 0) ? true : false;
}
?>
</body>
</html>