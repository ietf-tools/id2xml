#!/usr/local/bin/perl

######################################################
#              
#      Program: pidtracker.cgi
#      Author : Michael Lee, Foretec Seminars, Inc
#      Last Modified Date: 9/25/2002
#  
#      This Web application provides ID Draft Tracking and Maintaining 
#      capability to IETF Members
#
#####################################################

use lib '/export/home/mlee/RELEASE';
use CGI;
use IETF_UTIL;
use IETF_DBUTIL;

$ENV{"PROG_NAME"} = "pidtracker.cgi";    #ENV Variable to be used by lib. files
$LOG_PATH = "/export/home/mlee/LOGs";
my $q = new CGI;
$program_name = $ENV{"PROG_NAME"};

$fColor = "7DC189";
$sColor = "CFE1CC";
$menu_fColor = "F8D6F8";
$menu_sColor = "E2AFE2";

$table_header = qq{<table cellpadding="1" cellspacing="1" border="0">
};
$form_header = qq{<form action="$program_name" method="POST" name="form1">
};
$form_header_search = qq{<form action="$program_name" method="POST" name="search_form">
};
$error_msg = qq{
<h2>There is a fatal error raised while processing your request</h2>
};


$db_mode = 0;    # To determine which database engine should be used
$MYSQL = 2;      # Use MySQL DB Engine
$CURRENT_DATE = "CURRENT_DATE"; # "TODAY" for Informix, "CURRENT_DATE" for MySQL
$CONVERT_SEED = 1; # To convert date format to fit into the current database engine
my $html_txt;


($db_mode,$CURRENT_DATE,$CONVERT_SEED,$is_null) = init_database($MYSQL);




$html_top = qq{
<html>
<HEAD><TITLE>IETF ID Tracker v1.0 -- $browser_version</title>
<STYLE TYPE="text/css">
<!--

	  TD {text-decoration: none; color: #000000; font: 9pt arial;} 
	  A:Link {color: #0000ff; text-decoration:underline}
	  A:Hover {color: #ff0000; text-decoration:underline}
      A:visited {color: #0000ff; text-decoration:underline}
	  #largefont {font-weight: bold; color: #000000; font: 18pt arial}
	  #largefont2 {color: #000000; font: 14pt verdana}
	  #largefont3 {color: #000000; font: 13pt verdana}
	  #largefont_red {font-weight: bold; color: #ff0000; font: 16pt arial}
-->
</STYLE>

</head>
<body link="blue" vlink="blue">
};
$html_bottom = qq{
<!-- begin new footer -->
<HR>
<p>
<i>This page produced by the <A HREF="mailto:iesg-secretary\@ietf.org">IETF Secretariat</a> 
for the <A HREF="mailto:iesg\@ietf.org">IESG</A></i>
<p>
</body>
</html>
};
$html_body = get_html_body($q);

#Main body of HTML

print <<END_HTML;
Content-type: text/html
$html_top
$html_body
$html_bottom
END_HTML



###########################################
#
#  Function : get_html_body
#  parameters:
#    $q : main cgi variable
#  result : body of HTML text
#
#  get_html_body calls appropriate function to generate the body of HTML.
#  get_html_body calls functions based on "command" cgi variable
#
########################################### 
sub get_html_body {
   my $q = shift;   # CGI variable
   my $command = $q->param("command");
   my $switch = "-deploy";
   my $html_txt;
   unless (my_defined($command)) { # If no command passed, display login screen
      return main_menu();
   }
   elsif ($command eq "search_list") { # Display Search page
      if (defined($q->param("search_button"))) {
	     $html_txt = search_list ($q);
	  } elsif (defined($q->param("add_button"))) {
	     $html_txt = add_id_search ($q);
	  }
      
   }
   elsif ($command eq "main_menu") { # Display Main page
      return main_menu ();
   }
   elsif ($command eq "view_comment") { # Display Comment popup window
      return view_comment ($q);
   }
   else { # Generate a page depends on "command"
      my $func = "${command}(\$q)";
	  $html_txt = eval($func);
   }

# Display footer with "main" and "go back" button
   $html_txt .= qq {
   $form_header
   <input type="hidden" name="command" value="main_menu">
   <input type="submit" value="Main Menu">
   <input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true">
   </form>
   };
   return $html_txt;
}


#########################################################
#
#   Function main_menu
#   Parameters:
#   return: HTML text of main screen with Search table and 
#           Draft list which's been assigned to current user
#
#########################################################
sub main_menu {
   my $html_txt = "";
   my $search_html = search_html();
   $html_txt .= qq{<CENTER>
   <img src="http://www.ietf.org/images/ietflogo2e.gif" border=0><br>
   <h1>DRAFT TRACKER</h1>

$search_html</CENTER>};
   
   return $html_txt;
}

#########################################################
#
#   Function : search_html
#   Parameters:
#      $ballot_id - ballot_id, optional
#      $add_sub_flag - To indicate adding sub action, optional
#   return : HTML text to display search table
#
########################################################
sub search_html {
   my $button_str;
   my $msg_str = "";
   
   my $default_job_owner = $q->param("search_job_owner");
   my $default_group_acronym = $q->param("search_group_acronym");
   my $default_area_acronym = $q->param("search_area_acronym");
   my $default_filename = $q->param("search_filename");
   my $default_rfcnumber = $q->param("search_rfcnumber");
   my $default_cur_state = $q->param("search_cur_state");
   my $default_sub_state_id = $q->param("sub_state_id");
   my $default_status_id = $q->param("search_status_id");
   my $area_option_str = get_area_option_str($default_area_acronym);
   my $state_option_str = get_option_str("ref_doc_states_new",$default_cur_state);
   my $status_option_str = get_option_str("id_status",$default_status_id);
   my $sub_state_option_str = get_sub_state_select($default_sub_state_id);
   my $max_id = db_select("select max(sub_state_id) from sub_state");
   $max_id++;

      $button_str = qq {
<TD ALIGN="CENTER" colspan="2"><INPUT TYPE="submit" VALUE="SEARCH" name="search_button">
<input type="button" value="Clear Fields" onClick="clear_fields();">
</TD>
};
      $msg_str = qq {<font color="red" size="-1">**Just click 'SEARCH' button to view entire list of active draft**</font>};
   my $ad_option_str = get_ad_option_str($default_job_owner); # HTML SELECT OPTIONS for Area Directors
   my $html_txt = qq {
   <script language="javascript">
   function validate_input () {
          filename = document.search_form.search_filename.value;
	  temp_val = filename.substring(0,1);
	  if (temp_val == " ") {
	     alert("File name cannot start with a space");
	     return false;
	  }

   	  if ( (document.search_form.search_filename.value == "" || document.search_form.search_filename.value == "null")
		&& (document.search_form.search_rfcnumber.value == "" || document.search_form.search_rfcnumber.value == "null") ){
		 alert("Either File Name or RFC Number field must be filled");
		 return false;
	  }
      return true;
   }
   
   function clear_fields() {
      document.search_form.search_job_owner.selectedIndex=0;
      document.search_form.search_status_id.selectedIndex=0;
      document.search_form.search_area_acronym.selectedIndex=0;
      document.search_form.search_cur_state.selectedIndex=0;
      document.search_form.sub_state_id.selectedIndex=$max_id;
	  document.search_form.search_group_acronym.value = "";
	  document.search_form.search_filename.value = "";
	  document.search_form.search_rfcnumber.value = "";
      return true;
   }
   </script>
		$form_header_search
        $table_header
<input type="hidden" name="command" value="search_list">
<TR BGCOLOR="silver"><Th colspan="2">ID - Search Criteria</Th></TR>
<TR><TD colspan="2">
$table_header
  <TR><TD ALIGN="right">
  <B>Shepherding AD:</B></TD>
  <TD><select name="search_job_owner">
  <option value="0"></option>
  $ad_option_str</select>&nbsp;&nbsp;&nbsp;<B>WG Acronym:</B><INPUT TYPE="text" NAME="search_group_acronym" VALUE="$default_group_acronym" SIZE="6" MAXLENGTH="10">
  &nbsp;&nbsp;&nbsp;
  <B>Status:</B><SELECT NAME="search_status_id"><OPTION VALUE="">All</OPTION>
  $status_option_str</SELECT>
  </TD></TR>
  <TR><TD ALIGN="right"><B>Draft State:</B></TD>
  <TD><SELECT NAME="search_cur_state"><OPTION VALUE="">
  $state_option_str
  </SELECT>&nbsp;&nbsp;&nbsp;
  <b>sub state</b>: $sub_state_option_str
  </TD></TR>
  <TR><TD ALIGN="right"><B>Filename:</B>                          </TD>
  <TD><INPUT TYPE="text" NAME="search_filename" SIZE="15" MAXLENGTH="60" VALUE="$default_filename">
  &nbsp;&nbsp;&nbsp;<B>RFC Number:</B><INPUT TYPE="text" NAME="search_rfcnumber" SIZE="5" MAXLENGTH="10" VALUE="$default_rfcnumber">
  <B>Area Acronym:</B><select name="search_area_acronym">
  <option value=""></option>
  $area_option_str
  </select>

  </TD></TR>
</TABLE>
</TD></TR>
<TR BGCOLOR="silver">$button_str
</TR>
</TABLE>
</FORM>
<HR>
   };
   return $html_txt;
}

##########################################################################
# 
#   Function : search_list
#   Parameters :
#     $q : CGI variables
#   return : HTML text of search resulted list of draft
#
#########################################################################
sub search_list {
   my $q = shift;
   my $search_html = search_html();
   my $html_txt .= qq{<CENTER>$search_html</CENTER>};
   $html_txt .= "<b>Search Result</b><br>\n";
   my @idList;
   my @rfcList;
   if (my_defined($q->param("search_filename"))) {
      $_ = $q->param("search_filename");
	  s/-\d\d.txt//;
	  $q->param(search_filename => $_);
   }
   if (my_defined($q->param("search_group_acronym"))) {
      my $group_acronym = lc($q->param("search_group_acronym"));
      $group_acronym = db_quote($group_acronym);
	  my $gID = db_select("select acronym_id from acronym where acronym = $group_acronym");
	  unless ($gID) {
	     return "<h3>Fatal Error: Invalid WG $group_acronym</h3>";
      }
   }

   my @docList;
    
   if (my_defined($q->param("search_filename"))) {  # Searching ID
      $sqlStr = process_id ($q);
	  #return $sqlStr; 
	  @docList = db_select_multiple($sqlStr);
   } elsif (my_defined($q->param("search_rfcnumber"))) {  # Searching RFC
      $sqlStr = process_rfc ($q);
	  #return $sqlStr; 
	  @docList = db_select_multiple($sqlStr);
   } else {   #searching both ID and RFC
      if ( my_defined($q->param("search_group_acronym")) or my_defined($q->param("search_status_id")) or my_defined($q->param("search_area_acronym")) ) {  
         $sqlStr = process_id ($q);
	     #return $sqlStr; 
	     my @idList = db_select_multiple($sqlStr);
         $sqlStr = process_rfc ($q);
	     #return $sqlStr; 
	     my @rfcList = db_select_multiple($sqlStr);
         #Combine IDs and RFCs result
         push @docList, @idList;
         push @docList, @rfcList;
	  } else {
	    $sqlStr = process_id_rfc($q);
		#return $sqlStr;
		@docList = db_select_multiple($sqlStr);
	  }
   }  
   my $ret_val = display_all(@docList);
   unless ($ret_val) {
      if (my_defined($q->param("search_filename"))) {
          my $filename .= rm_hd(rm_tr($q->param("search_filename")));
          $filename = db_quote($filename);
          my ($revision,$iid) = rm_tr(db_select("select revision,intended_status_id from internet_drafts where filename = $filename"));
          if (my_defined($revision)) {
             my $status_val = get_id_status_option_str($iid,0); 
             $html_txt .= qq{<h2>This document is not under IESG review yet</h2>
<h3>$filename</h3>
<b>Revision: $revision<br>Intended Status: $status_val<br></b><br><br>
};
          } else {
             $html_txt .= "<h2>No Record Found</h2>\n";
          }
         
      } else {
         $html_txt .= "<h2>No Record Found</h2>\n";
      }
   }
   else { 
      $html_txt .= $ret_val;
   }
   return $html_txt;
}

#############################################################
#
#   Function process_id
#   parameters :
#     $q : CGI variables
#   return : SQL statement which performs search on IDs

#############################################################
sub process_id {
   my $q = shift;
   my $sqlStr = qq{
   select state.id_document_tag, state.status_date,state.event_date,state.job_owner,
   state.cur_state,state.cur_sub_state_id,state.assigned_to,state.rfc_flag,state.ballot_id,id.filename
   from id_internal state, internet_drafts id};
   my $where_clause = qq {
   where id.id_document_tag = state.id_document_tag
   AND state.rfc_flag = 0
   };
   if (my_defined($q->param("search_filename"))) {
      my $filename = "%";
	  $filename .= rm_hd(rm_tr($q->param("search_filename")));
	  $filename .= "%";
      $filename = db_quote($filename);
	  $where_clause .= "AND id.filename like $filename and state.rfc_flag = 0\n";
   }
   if (my_defined($q->param("search_group_acronym"))) {
      my $group_acronym = lc($q->param("search_group_acronym"));
      $group_acronym = db_quote($group_acronym);
	  my $gID = db_select("select acronym_id from acronym where acronym = $group_acronym");
	  $where_clause .= "AND id.group_acronym_id = $gID\n";
   }
   if (my_defined($q->param("search_cur_state"))) {
	  my $cur_state .= $q->param("search_cur_state");
	  $where_clause .= "AND state.cur_state = $cur_state\n";
          if (my_defined($q->param("sub_state_id"))) {
             my $max_id = db_select("select max(sub_state_id) from sub_state");
             my $sub_state_id .= $q->param("sub_state_id");
             if ($sub_state_id <= $max_id) {
                $where_clause .= "AND state.cur_sub_state_id = $sub_state_id\n";
             }
          }
   }

   if (my_defined($q->param("search_status_id"))) {
	  my $status_id .= $q->param("search_status_id");
	  $where_clause .= "AND id.status_id = $status_id\n";
   }
   if ($q->param("search_job_owner") > 0) {
      my $job_owner = $q->param("search_job_owner");
	  $where_clause .= "AND state.job_owner = $job_owner\n";
   }
   if (my_defined($q->param("search_area_acronym"))) {
      my $area_acronym_id = $q->param("search_area_acronym");
	  my $group_id_set = "";
	  my @groupList = db_select_multiple("select group_acronym_id from area_group where area_acronym_id = $area_acronym_id");
	  my @group_id_set;
	  for $array_ref (@groupList) {
	     my ($val) = @$array_ref;
		 push @group_id_set,$val;
	  }
	  $group_id_set = join ",",@group_id_set;
	  $where_clause .= qq { AND ((id.group_acronym_id = 1027 AND state.area_acronym_id = $area_acronym_id) OR 
	  (id.group_acronym_id <> 1027 AND id.group_acronym_id in ($group_id_set))) 
	  };
   }
   $sqlStr .= $where_clause;
   $sqlStr .= "\n order by state.cur_state, state.cur_sub_state_id,id.filename\n";
   return $sqlStr;
}


sub process_id_rfc {
   my $q = shift;
   my $sqlStr;
   my $where_clause;
      $sqlStr = qq{
      select state.id_document_tag, state.status_date,state.event_date,state.job_owner,
      state.cur_state,state.cur_sub_state_id,state.assigned_to,state.rfc_flag,state.ballot_id,1,id.filename
      from id_internal state left outer join internet_drafts id on id.id_document_tag = state.id_document_tag};
      $where_clause = qq {
      where state.primary_flag = 1 
      };
   if (my_defined($q->param("search_filename"))) {
      my $filename = "%";
	  $filename .= rm_hd(rm_tr($q->param("search_filename")));
	  $filename .= "%";
      $filename = db_quote($filename);
	  $where_clause .= "AND id.filename like $filename and state.rfc_flag = 0\n";
   }
   if (my_defined($q->param("search_rfcnumber"))) {
	     $_ = $q->param("search_rfcnumber");
  	     s/(\D+)(\d+)(\D+)/$2/;
		 my $rfc_number = $_;
         $where_clause .= "AND state.id_document_tag = $rfc_number and state.rfc_flag = 1\n";
   }
   if (my_defined($q->param("search_cur_state"))) {
	  my $cur_state .= $q->param("search_cur_state");
	  $where_clause .= "AND state.cur_state = $cur_state\n";
   
          if (my_defined($q->param("sub_state_id"))) {
             my $max_id = db_select("select max(sub_state_id) from sub_state");
             my $sub_state_id .= $q->param("sub_state_id");
             if ($sub_state_id <= $max_id) {
                $where_clause .= "AND state.cur_sub_state_id = $sub_state_id\n";
             }
          }
   }

   if (my_defined($q->param("search_status_id"))) {
	  my $status_id .= $q->param("search_status_id");
	  $where_clause .= "AND id.status_id = $status_id\n";
	  if ($status_id == 2) {
	     $where_clause .= "AND state.rfc_flag = 0\n";
      }
   }
   if ($q->param("search_job_owner") > 0) {
      my $job_owner = $q->param("search_job_owner");
	  $where_clause .= "AND state.job_owner = $job_owner\n";
   }
   $sqlStr .= $where_clause;
   $sqlStr .= "\n order by state.cur_state, state.cur_sub_state_id,id.filename\n";
   return $sqlStr;
}




##################################################
#
#   Function : process_rfc
#   Parameters :
#      $q : CGI variables
#   return : SQL statement which will perform search on RFCs
#
##################################################
sub process_rfc {
   my $q = shift;
   my $dName = uc($q->param("search_id_document_name"));
   my $gAcronym = $q->param("search_group_acronym");
   my $filename = $q->param("search_rfcnumber");
   my $sqlStr = qq{
   select state.id_document_tag, state.status_date,state.event_date,state.job_owner,
   state.cur_state,state.cur_sub_state_id,state.assigned_to,state.rfc_flag,state.ballot_id,rfc.rfc_number
   from id_internal state, rfcs rfc
   };
   my $where_clause = qq {
   where rfc.rfc_number = state.id_document_tag
   AND state.rfc_flag = 1
   };
      if (my_defined($dName)) {
         $dName = rm_hd(rm_tr($dName));
	 $dName .= "%";
         $dName = db_quote($dName);
         $where_clause .= "AND rfc_name_key like $dName\n";
      }
      if (my_defined($gAcronym)) {
         $gAcronym = db_quote($gAcronym);
         $where_clause .= "AND group_acronym = $gAcronym\n";
      }
      if (my_defined($filename)) {
	     $_ = $filename;
  	     s/(\D+)(\d+)(\D+)/$2/;
		 $rfc_number = $_;
         $where_clause .= "AND rfc_number = $rfc_number\n";
      }
   if (my_defined($q->param("search_cur_state"))) {
	  my $cur_state .= $q->param("search_cur_state");
	  $where_clause .= "AND state.cur_state = $cur_state\n";
          if (my_defined($q->param("sub_state_id"))) {
             my $max_id = db_select("select max(sub_state_id) from sub_state");
             my $sub_state_id .= $q->param("sub_state_id");
             if ($sub_state_id <= $max_id) {
                $where_clause .= "AND state.cur_sub_state_id = $sub_state_id\n";
             }
          }
   }


   if ($q->param("search_job_owner") > 0) {
      my $job_owner = $q->param("search_job_owner");
	  $where_clause .= "AND state.job_owner = $job_owner\n";
   }
   if (my_defined($q->param("search_status_id"))) {
	  my $status_id .= $q->param("search_status_id");
	  if ($status_id == 2) {
	     $where_clause .= "AND rfc.rfc_number = 999999\n";
      }
   }
   if (my_defined($q->param("search_area_acronym"))) {
      my $area_acronym_id = $q->param("search_area_acronym");
	  $where_clause .= qq {AND  state.area_acronym_id = $area_acronym_id
	  };
   }
   $sqlStr .= $where_clause;
   $sqlStr .= "\n order by state.cur_state, state.cur_sub_state_id, rfc.rfc_number\n";
   return $sqlStr;
}


#######################################################
#
#   Function : get_ad_option_str
#   Parameters:
#      $id - record id
#   return : HTML text to display options of Area Directors
#
#######################################################
sub get_ad_option_str {
   my $id = shift;
   my $ad_option_str = "";
   $sqlStr = qq{
select id, first_name,last_name from iesg_login where user_level = 1 or user_level = 3 order by first_name
};
   my @list = db_select_multiple($sqlStr);
   for $array_ref (@list) {
     my ($pID,$first_name,$last_name) = rm_tr(@$array_ref);
         my $selected = "";
         if (defined($id)) {
            if ($pID == $id) {
               $selected = "selected";
        }
         }
     $ad_option_str .= qq{
      <option value="$pID" $selected>$first_name $last_name</option>
     };
   }
   return $ad_option_str;
}



################################################################
#
# Function : get_option_str
# Parameters:
#   $table_name : Table where the data pulled from
#   $selected_id : currently selected record id
# return : HTML text of options of SELECT tag
#
################################################################
sub get_option_str {
   my $table_name = shift;
   my $selected_id = shift;
   $selected_id = 0 unless my_defined($selected_id);
   $option_str = "";
   $sqlStr = qq{
   select * from $table_name order by 1
   };
   my @list = db_select_multiple($sqlStr);
   for $array_ref (@list) {
     my ($id,$val) = @$array_ref;
      if (defined($selected_id) and $selected_id == $id) {
         $selected = "selected";
      } else {
         $selected = "";
      }
      $option_str .= qq{
      <option value="$id" $selected>$val</option>
      };
   }
   return $option_str;
}

############################################################
#
# Function : get_mark_by
# Parameters:
#   $id - login id of current user
# return : string of first name and last name pulled from iesg_login table
#
############################################################
sub get_mark_by {
   my $id = shift;
   my ($fName,$lName) = rm_tr(db_select("select first_name,last_name from iesg_login where id = $id"));
   my $new_mark_by = "$fName $lName";
   return $new_mark_by;
}


############################################################
#
# Function : view_id
# Parameters:
#   $q : CGI variables
# return : HTML text to view draft
#
# Many main feature of this application can be performed within this page.
# One can change state of draft, update any information, view action group
# if existed, add a draft to current action group, detach current draft from its
# action group, add a comment about current draft, and view any previous comment.
#
############################################################
sub view_id {
   my $q = shift;
   my $dTag = $q->param("dTag");
   my $rfc_flag = $q->param("rfc_flag");
   my $from_field = "";
   if ($rfc_flag == 1) {
	   $sqlStr = qq{
	   select rfc.rfc_name, rfc.online_version, state.status_date,state.note,state.agenda,state.event_date,state.area_acronym_id,
	   state.cur_state,state.prev_state,state.cur_sub_state_id,state.prev_sub_state_id,state.group_flag,state.assigned_to,state.job_owner,state.ballot_id, rfc.intended_status_id
	   
	   from rfcs rfc ,
	   id_internal state
	   where rfc.rfc_number = state.id_document_tag
	   AND state.id_document_tag = $dTag
	   AND state.rfc_flag = 1
	   };

   } else {
	   $sqlStr = qq{
	   select id.filename, id.revision, state.status_date,state.note,state.agenda,state.event_date,state.area_acronym_id,
	   state.cur_state,state.prev_state,state.cur_sub_state_id,state.prev_sub_state_id,state.group_flag,state.assigned_to,state.job_owner,state.ballot_id,id.intended_status_id
	   from internet_drafts id,
	   id_internal state
	   where id.id_document_tag = state.id_document_tag
	   AND state.id_document_tag = $dTag
	   AND state.rfc_flag = 0
	   };
   }
   #return $sqlStr;
   my ($filename,$revision,$status_date,$note,$agenda,$event_date,$area_acronym_id,$cur_state,$prev_state,$cur_sub_state_id,$prev_sub_state_id,$group_flag,$assigned_to,$job_owner,$ballot_id,$status_id) = rm_tr(db_select($sqlStr));
   my $id_status_option_str = get_id_status_option_str($status_id,$rfc_flag); 
   if ($rfc_flag == 1) {
      $revision = "RFC";
   }
   $note = unformat_textarea($note);
   my $checked = "No";
   $checked = "Yes" if ($agenda == 1);
   my $ballot_count = db_select("select count(*) from id_internal where ballot_id = $ballot_id");
   my $ad_option_str = get_mark_by($job_owner); #Get Area Directors List
   my $action_html = "";
   my $action_list_html = "";
   my $detach_button = "";
   if ($ballot_count > 1) { # If an action group existed
      # Create a short cut to action list
      $action_list_html = "<div align=\"right\"><a href=\"#action\">Action List</a></div>";
      # Create an action list
      $action_html .= "<a name=\"action\"></a><table border=\"1\" bgcolor=\"black\"> <tr><td><font color=\"white\"><h3>Actions</h3></font>\n";
      if ($db_mode == $MYSQL) {
         $from_field = qq {from id_internal state left outer join internet_drafts id
	 on state.id_document_tag = id.id_document_tag
	 left outer join rfcs rfc on state.id_document_tag = rfc.rfc_number};
         $outer_where = "";
      } 
      my $sqlStr = qq{
      select state.id_document_tag, state.status_date,state.event_date,state.job_owner,
      state.cur_state,state.cur_sub_state_id,state.assigned_to,state.rfc_flag,state.ballot_id,1,id.filename
      $from_field
      where state.ballot_id = $ballot_id
      AND state.primary_flag = 1
      $outer_where
      };
      #return $sqlStr;
	  my @action_list = db_select_multiple($sqlStr);
	  $action_html .= display_all(@action_list);
	  $action_html .= "</td></tr></table>";
   }
   my $html_txt = "";
   my $cur_state_txt = db_select("select document_state_val from ref_doc_states_new where document_state_id = $cur_state");
   if ($cur_sub_state_id > 0) {
     my $cur_sub_state = get_sub_state($cur_sub_state_id);
     $cur_state_txt .= " -- $cur_sub_state";
   }

   my $row_color = $fColor;

   

   my $ballot_link = "Not Available";
   my $ballot_exist = 0;
   my $ballot_name = $filename;
   if ($rfc_flag==1) {
      $ballot_name = "rfc${dTag}";
   }
   if (-e "/usr/local/etc/httpd/htdocs/IESG/EVALUATIONS/${ballot_name}.bal") {
      $ballot_link = "<a href=\"https://www.ietf.org/IESG/EVALUATIONS/${ballot_name}.bal\" TARGET=\"_blank\">Available</a>";
	  $ballot_exist = 1;
   }
   $status_date = convert_date($status_date,1);
   my $length_validate = "";
   my $length_validate_form = "";
   $html_txt .= qq{
	<SCRIPT Language="JavaScript">   
	function MM_openBrWindow(theURL,winName,features) { //v2.0
	  window.open(theURL,winName,features);
	}
	function MM_closeBrWindow(winName) { //v2.0
	  window.close(winName);
	}
	</script>
   <table width="600" cellpading=1 cellspacing=0>
   <tr><td bgcolor="000000">
   <table width="598" cellspacing=0 cellpading = 5>
   <tr bgcolor="BEBEBE" align="center"><th colspan="2"><div id="largefont">View Draft</div> $action_list_html</th></tr>
   <tr bgcolor="white"><td><div id="largefont3">Draft Name: </td><td><div id="largefont3"><a href="http://www.ietf.org/internet-drafts/$filename-$revision.txt">$filename</a></td></tr>
   <tr bgcolor="white"><td><div id="largefont3"><div id="largefont3">IESG Discussion:</td><td>$ballot_link</td>
   <tr bgcolor="white"><td><div id="largefont3">Version: </td><td><div id="largefont3">$revision</td></tr>
   <tr bgcolor="white"><td><div id="largefont3">Intended Status: </td>
   <td><div id="largefont3">
   $id_status_option_str
   </td></tr>
   <tr bgcolor="white"><td><div id="largefont3">
   On Next Agenda? </td><td><div id="largefont3"> $checked
   </td></tr>
   <tr bgcolor="white"><td><div id="largefont3">Current State: </td>
   <td><div id="largefont3">
   $cur_state_txt
   </td></tr>
   <tr bgcolor="white">
   <td><div id="largefont3">Shepherding AD:</td>
   <td><div id="largefont3">
   $ad_option_str
   </td>
   </tr>
   <tr bgcolor="white">
   <td><div id="largefont3">Due Date:</td>
   <td><div id="largefont3">$status_date
   </td>
   </tr>
   <tr bgcolor="white"><td><div id="largefont3">Web Note:</td><td>
   <div id="largefont3">$note
   </td></tr>
   <tr bgcolor="white">
   <td width="140"></td>
   <td>
       $table_header
       <tr>
       $form_header
       <input type="hidden" name="command" value="main_menu">
       <td><input type="submit" value="Main Menu"></td></form>
       </tr>
       </table>
   </td>
   </tr>
   </table>
   </td></tr> 
   </table>
 $action_html 
   <h3>Comment Log</h3>
   $table_header
   <tr bgcolor="$fColor"><th>Date</th><th>Version</th><th>Comment</th></tr>
   };
   $sqlStr = qq{
   select id,comment_date,version,comment_text,created_by from document_comments
   where document_id = $dTag and public_flag = 1
   order by 1 desc
   };
   my @commentList = db_select_multiple($sqlStr);
   for $array_ref (@commentList) {
      my ($id,$comment_date,$version,$comment_text,$created_by) = @$array_ref;
	  $comment_date = convert_date($comment_date,1);
          $comment_text = format_textarea($comment_text); 
          $comment_text = reduce_text($comment_text,4);
	  if ($row_color eq $fColor) {
	     $row_color = $sColor;
	  } else {
	     $row_color = $fColor;
	  }
	  $html_txt .= qq {
	  <tr bgcolor="$row_color"><td>$comment_date</td><td align="center">$version</td><td>$pre_str $comment_text</td>
	  <form>
	  <td>
	  <input type="button" value="View Detail" onClick="window.open('${program_name}?command=view_comment&id=$id',null,'height=250,width=500,status=no,toolbar=no,menubar=no,location=no,resizable=yes,scrollbars=yes');">
	  </td>
	  </form>
	  </tr>
	  };
   }
   $html_txt .= "</table><br>\n";
   return $html_txt;
}


############################################################
#
# Function : view_comment
# Paramters:
#   $q - CGI variables
# return: HTML text to display detail information of selected comment
#
###########################################################
sub view_comment {
   my $q = shift;
   my $id = $q->param("id");
   my $html_txt = "";
   
   my $sqlStr = qq {
   select document_id,rfc_flag,public_flag,comment_date,comment_time,
   version,comment_text,created_by,result_state,origin_state
   from document_comments
   where id = $id
   };
   #return $sqlStr;
   my ($document_id,$rfc_flag,$public_flag,$comment_date,$comment_time,$version,$comment_text,$created_by,$result_state,$origin_state) = db_select($sqlStr);
   my $origin_state_txt = db_select("select document_state_val from ref_doc_states_new where document_state_id = $origin_state");
   my $result_state_txt = db_select("select document_state_val from ref_doc_states_new where document_state_id = $result_state");
   $comment_date = convert_date($comment_date,1);
   my $created_by_str = get_mark_by($created_by);
   $html_txt .= qq {
   $table_header
   <tr><td><b>Date and Time:</td><td>$comment_date, $comment_time</td></tr>
   <tr><td><b>Version:</td><td>$version</td></tr>
   <tr><td><b>Commented by:</td><td>$created_by_str</td></tr>
   <tr><td><b>State before Comment:</td><td>$origin_state_txt</td></tr>
   <tr><td><b>State after Comment:</td><td>$result_state_txt</td></tr>
   <Tr><td><b>Comment:</td><td>$comment_text</td></tr>
   </table>
   <center><form>
   <input type="button" value="close" onClick="window.close();">
   </form></center>
   };
   return $html_txt;
}


###########################################################################
#
# Function get_id_status_option_str
# Parameters :
# return : HTML text to display options of ID intended_status
# 
##########################################################################
sub get_id_status_option_str {
   my $selected_id = shift;
   my $rfc_flag = shift;
   my $html_txt;
   my $table_name = "id_intended_status";
   $table_name = "rfc_intend_status" if ($rfc_flag);
   $html_txt = rm_tr(db_select("select status_value from $table_name where intended_status_id = $selected_id"));
   return $html_txt;
}

############################################################################
#
# Function  display_all
# Parameters :
#   @docList - list data to be displayed
# result: HTML text displaying the list
#
############################################################################
sub display_all {
   my @docList = @_;
   my $prev_state = 0;
   my $prev_sub_state = 0;
   my $html_txt = qq{
   $table_header};
   my $row_color = $menu_sColor;
   my $old_ballot = 0;
   my $count = 0;
   for $array_ref (@docList) {
      my ($dTag,$status_date,$event_date,$mark_by,$cur_state,$cur_sub_state,$assigned_to,$rfc_flag,$ballot_id,$all_list) = @$array_ref;
      $all_list = 0 unless my_defined($all_list);
      $all_list = 0 unless ($all_list =~ /^\d/);
	  $count++;
	  if (($cur_state != $prev_state or $cur_sub_state !=  $prev_sub_state) and $old_ballot != $ballot_id) {
             if ($cur_state != $prev_state) {
                my $cur_state_val = rm_tr(db_select("select document_state_val from ref_doc_states_new where document_state_id = $cur_state"));
                $html_txt .= qq{                 
                 </table>
                 <h3>In State: $cur_state_val $cur_sub_state_val</h3>
         <table bgcolor="#DFDFDF" cellspacing="0" cellpadding="0" border="0" width="800">
         <tr bgcolor="A3A3A3"><th>&nbsp;</th><th width="250">Name (Intended Status)</th><th>Ver</th><th>Shepherding AD</th><th>Due Date</th><th>Modified (EST)</th></tr>
               };
            }

	     $prev_state = $cur_state;
             $prev_sub_state = $cur_sub_state;
             my $cur_sub_state_val = "";
             if ($cur_sub_state > 0) {
               $cur_sub_state_val = " -- ";
               $cur_sub_state_val .= get_sub_state($cur_sub_state); 
             }
	  }
	  
	  my $pre_list;
	  if ($old_ballot != $ballot_id) {
	     $old_ballot = $ballot_id;
	     $pre_list = "<li>";
    	  if ($row_color eq $menu_fColor) {
	        $row_color = $menu_sColor;
	      } else {
	        $row_color = $menu_fColor;
	      }
	  } else {
	     $pre_list = "<dd><font size=\"-1\">";
	  }
	  my $ballot_list = "";
	  
	  $ballot_list = get_ballot_list($ballot_id,$dTag,$row_color) if ($all_list == 1);
      $status_date = convert_date($status_date,1);
	  $event_date = convert_date($event_date,1);
	  $html_txt .= display_one_row($ballot_id,$dTag,$rfc_flag,$assigned_to,$mark_by,$status_date,$event_date,$row_color,$pre_list);
	  $html_txt .= $ballot_list;
   }
   unless ($count) {
      return 0;
   }
   $html_txt .= qq {</table>
   };   
   return $html_txt;

}

sub get_ballot_list {
   my $ballot_id = shift;
   my $id_document_tag = shift;
   my $row_color = shift;
   my $html_txt = "";
   my $sqlStr;
   if ($db_mode == $MYSQL) {
      $sqlStr = qq {
select it.id_document_tag,id.filename,rfc.rfc_number,it.rfc_flag,it.assigned_to,it.job_owner,
it.status_date,it.event_date
from id_internal it
left outer join internet_drafts id on it.id_document_tag = id.id_document_tag
left outer join rfcs rfc on it.id_document_tag = rfc.rfc_number
where it.ballot_id = $ballot_id and it.id_document_tag <> $id_document_tag
order by id.filename, rfc.rfc_number
};
   } else {
      $sqlStr = qq {
select it.id_document_tag,id.filename,rfc.rfc_number,it.rfc_flag,it.assigned_to,it.job_owner,
it.status_date,it.event_date
from id_internal it, outer internet_drafts id, outer rfcs rfc
where it.ballot_id = $ballot_id
AND it.id_document_tag = id.id_document_tag and it.id_document_tag <> $id_document_tag
AND it.id_document_tag = rfc.rfc_number
order by id.filename, rfc.rfc_number
	  };
   }
   my @List = db_select_multiple($sqlStr);
   my $pre_list = "<dd><font size=\"-1\">";
   for $array_ref (@List) {
      my ($id_document_tag,$filename,$rfc_number,$rfc_flag,$responsible,$job_owner,$status_date,$event_date) = @$array_ref;
	  $responsible = rm_tr($responsible);
	  $html_txt .= display_one_row($ballot_id,$id_document_tag,$rfc_flag,$responsible,$job_owner,$status_date,$event_date,$row_color,$pre_list);
   }
   return $html_txt;
}

sub display_one_row {
   my ($ballot_id,$id_document_tag,$rfc_flag,$responsible,$job_owner,$status_date,$event_date,$row_color,$pre_list) = @_;
   my ($revision,$filename,$actual_file,$intended_status_str,$ballot_str);
   if ($ADMIN_MODE) {
	     $ballot_str = qq{[$ballot_id] <a href="http://cf.amsl.com/system/id/add/search_id3.cfm?id_document_tag=$id_document_tag&isnew=no&searchResults=$id_document_tag" 
		 onMouseOver="window.status='Detail of $id_document_tag';return true;" 
		 onMouseOut="window.status='';return true;"
		 TARGET="_blank">[detail]</a>};
   }
   if ($rfc_flag == 1) {
	     $revision = "RFC";
		 $filename = "rfc" . $id_document_tag;
		 $actual_file = "rfc/${filename}.txt";
		 $intended_status_str = db_select("select b.status_value from rfcs a, rfc_intend_status b where a.rfc_number = $id_document_tag and a.intended_status_id = b.intended_status_id");
   } else {
	     ($filename,$revision) = rm_tr(db_select("select filename,revision from internet_drafts where id_document_tag = $id_document_tag"));
		 $actual_file = "internet-drafts/${filename}-${revision}.txt";
		 $intended_status_str = db_select("select b.status_value from internet_drafts a, id_intended_status b where a.id_document_tag = $id_document_tag and a.intended_status_id = b.intended_status_id");
   }
   $status_date = convert_date($status_date,1);
   $event_date = convert_date($event_date,1);
   
   
   
   
   
   my $mark_by = get_mark_by($job_owner);
   my $html_txt = "";
	  $html_txt .= qq{
	  <tr bgcolor="$row_color">
       $form_header	  
	   <td>
       <input type="hidden" name="command" value="view_id">
	   <input type="hidden" name="dTag" value="$id_document_tag">
	   <input type="hidden" name="rfc_flag" value="$rfc_flag">
       <input type="submit" value="VIEW">
	  </td>
      </form>
	  
	  <Td nowrap>$pre_list <a href="http://www.ietf.org/$actual_file" TARGET=_BLANK>$filename ($intended_status_str)</a> $ballot_str</td>
          <td>$revision</td><td>$mark_by</td>
	  <td>$status_date</td><td>$event_date</td>
	  </tr>
	  };
   
   return $html_txt;   
}



########################################################
#
# Function get_area_optio_str
# Parameters:
# result: HTML text to display the options of "Area" field
#
########################################################
sub get_area_option_str {
   my $select_id = shift;
   $select_id = 0 unless my_defined($select_id);
   my $area_option_str = "";
   @list = db_select_multiple("select a.area_acronym_id,b.acronym from areas a,acronym b where a.area_acronym_id = b.acronym_id AND a.status_id = 1");
   for $array_ref (@list) {
      my $selected = "";
      my ($aid,$aval) = @$array_ref;
	  $selected = "selected" if ($aid == $select_id);
      $aval = rm_tr($aval);
      $area_option_str .= qq {<option value="$aid" $selected>$aval</option>
      };
   }
   return $area_option_str;
}


sub get_sub_state {
  my $id = shift;
  return rm_tr(db_select("select sub_state_val from sub_state where sub_state_id = $id"));
}

sub get_sub_state_select {
  my $default_id = shift;
  my $default_str = "No Problem";
  my $html = qq {<select name="sub_state_id">
};
  if ($default_id == -1) {
    $html .= qq{ <option value="-1">--Select Sub State</option>
};
  }
  $html .= qq{
  <option value=0>$default_str</option>
};
  my @List = rm_tr(db_select_multiple("select sub_state_id,sub_state_val from sub_state order by 1"));
  for $array_ref (@List) {
    my ($id,$val) = @$array_ref;
    my $selected = "";
    $selected = "selected" if ($id == $default_id);
    $html .= "  <option value=$id $selected>$val</option>\n";
  }
  if ($default_id > -1) {
    my $max_id = db_select("select max(sub_state_id) from sub_state");
    $max_id++;
    $html .= "<option value=$max_id selected>--All Substates</option>\n";
  }
  $html .= "</select>\n";
  return $html;
}
  
sub y_two_k {
   my $ret_val = shift;
   return "" unless (my_defined($ret_val));
   $_ = $ret_val;
   if (/\//) {
      my @temp = split '\/';
	  if ($temp[2] < 50) {
		 $temp[2] = 2000 + $temp[2];
	  } 
	  $ret_val = join '/', @temp;
   } else {
      my @temp = split '-';
	  if ($temp[2] < 50) {
	     $temp[2] = $temp[2] + 2000;
	  } 
	  $ret_val = join '-', @temp;
   }
   return $ret_val;
}
