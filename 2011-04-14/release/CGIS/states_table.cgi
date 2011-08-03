#!/usr/local/bin/perl -

use lib '/export/home/mlee/RELEASE/';
use CGI;
use IETF_UTIL;
use IETF_DBUTIL;

#$ENV{"DBPATH"} = "/usr/informix/databases";
$ENV{"DBNAME"} = "ietf";

$program_name = "states_table.cgi";
########## End Pre Populate Option lists ###################
$table_header = qq{<table cellpadding="1" cellspacing="0" border="1" width="500">
};
$form_header = qq{<form action="$program_name" method="POST" name="form1">
};
$html_top = qq{
<html>
<HEAD><TITLE>IESG ID Tracker -- State List</title>
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
   <h2>State List</h2>
   $table_header
   <tr>
   <th>State Name</th><th>Next State(s)</th>
   </tr>
   };
   my @List = db_select_multiple("select document_state_id,document_state_val from ref_doc_states_new");
   for $array_ref (@List) {
      my ($state_id,$state_name) = rm_tr(@$array_ref);
	  my $next_states = "";
	  $sqlStr = qq { select a.document_state_val from ref_doc_states_new a,ref_next_states_new b
	  where b.cur_state_id = $state_id and b.next_state_id = a.document_state_id
	  };
	  my @nextList = db_select_multiple($sqlStr);
	  for $array_ref_next (@nextList) {
	     my ($val) = rm_tr(@$array_ref_next);
		 $next_states .= "<li>$val <br>\n";
	  }
	  $html_txt .= qq {
	  <tr>
	  <td width="250">$state_name</td><td width="250">$next_states</td>
	  </tr>
	  };
   }

   $html_txt .= qq {
   </table>
   };
   
   return $html_txt;
}
