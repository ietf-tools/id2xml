#!/usr/bin/perl

##########################################################################
# Copyright © 2004 and 2003, Foretec Seminars, Inc.
##########################################################################
use lib '/a/www/ietf-datatracker/release';
use GEN_DBUTIL_NEW;
use GEN_UTIL;
use IETF;
use CGI;
use CGI_UTIL;
$host = $ENV{SCRIPT_NAME};
$devel_mode = ($host =~ /devel/)?1:0;
$db_name = ($devel_mode)?"develdb":"ietf";
$mode_text = ($devel_mode)?"Development Mode":"";
                                                                                                                
init_database($db_name);
$dbh=get_dbh();
my $q = new CGI;
$program_name="ipr_internal.cgi";
$user_name = $ENV{REMOTE_USER};
$user_name = $q->param("user_name") unless my_defined($user_name);

print qq|Content-type: text/html

<html>
<head><title>IPR Admin Internal Page $mode_text</title></head>
<body>
<script type="text/javascript">
                                                                                                                                                             
function handleEnter (field, event) {
                var keyCode = event.keyCode ? event.keyCode : event.which ? event.which : event.charCode;
                if (keyCode == 13) {
                        var i;
                        for (i = 0; i < field.form.elements.length; i++)
                                if (field == field.form.elements[i])
                                        break;
                        i = (i + 1) % field.form.elements.length;
                        field.form.elements[i].focus();
                        return false;
                }
                else
                return true;
        }
                                                                                                                                                             
</script>
                                                                                                                                                             
|;
############## Global Variables ###################
$STYLE_DEF = "{padding:2px;border-width:1px;border-style:solid;border-color:305076}";
$font_color1 = qq{<font color="000000" face="Arial" Size=3>};
$font_color2 = qq{<font color="333366" face="Arial" Size=2>};
$form_header = qq{<form action=\"ipr_internal.cgi\" method=\"post\">
<input type="hidden" name="user_name" value="$user_name">};
############ Global Variables ######################

my $command = $q->param("command");
my $rfc_number = $q->param("rfc_number");
my $rfc_count = db_select($dbh,"select count(*) from rfcs where rfc_number = $rfc_number");
my $filename = $q->param("filename");
$filename = rm_hd($filename);
$filename = rm_tr($filename);
my $id_document_tag = db_select($dbh,"select id_document_tag from internet_drafts where filename = '$filename'");
my $id_tag_count = db_select($dbh,"select count(*) from internet_drafts where id_document_tag = $id_document_tag");
unless (my_defined($command)) {
  add_ipr();
} else {
  unless (my_defined($q->param("p_h_legal_name"))) {
    display_error("Please Enter your Legal Name");
  }
  unless (my_defined($q->param("document_title"))) {
    display_error("Please Enter IPR title");
  }
}
do_add_ipr($q, $id_document_tag) if (my_defined($q->param("p_h_legal_name")) and my_defined($q->param("document_title")));

print qq {
  </body></html>
};
$dbh->disconnect();

sub add_ipr {
  my $max_id = db_select($dbh,"select max(ipr_id) from ipr_detail");
  my $comply_info = qq{
  <table border="1" cellpadding="4" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1<strong><b>Complies with RFC 3979?</b></strong></td>
    <td bgcolor="EBEBEB">
YES <input type="radio" name="comply" value="1"><br>
NO <input type="radio" name="comply" value="0"><br>
N/A <input type="radio" name="comply" value="-1"><br>
</td></tr>
  </table>
};
  my $update_info = qq{
  <table border="1" cellpadding="4" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="#EBEBEB">$font_color1<strong><b>IPR ID that is updated by this IPR: </b></strong></td>
    <td bgcolor="#EBEBEB"><input type="text" name="updated" value="0">
</td></tr>
    <tr><td bgcolor="#EBEBEB">Remove old IPR?</td>
    <td bgcolor="#EBEBEB"><input type="radio" name="remove_old_ipr" value="1"> YES
    <input type="radio" name="remove_old_ipr" value="0" checked> NO</td></tr>
  </table>
};

  print qq{
  $form_header
  <blockquote>
<h2>Add New IPR</h2>
  <hr width="100%">
  <br>
  <table border="1" cellpadding="2" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="DDDDDD" width="18%">$font_color1 IPR Title :</font></td>
    <td bgcolor="DDDDDD"><input type="text" onkeypress="return handleEnter(this, event)" name="document_title" size="70"></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1 Old IPR URL :</td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="old_ipr_url" size="80"></font></td></tr>
  </table>
  <table border="1" cellpadding="2" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1 IPR Note or Addendum :</td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="additional_old_title1" size="100"></font></td></tr>
  </table>
  <table border="1" cellpadding="2" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1 URL for Note / Addendum Text :</td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="additional_old_url1" size="80"></font></td></tr>
  </table>
  <table border="1" cellpadding="2" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1 Additional Old Titile2 :</td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="additional_old_title2" size="100"></font></td></tr>
  </table>

   <table border="1" cellpadding="2" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1 Additional Old URL2 :</td>    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="additional_old_url2" size="80"></font></td></tr>
  </table>

  <table border="1" cellpadding="4" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1<strong><b>Submitted Date </b></strong><small>(YYYY-MM-DD)</samll><b> :</b></td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="submitted_date" size="20"></font></td></tr>
  </table>

  <table border="1" cellpadding="4" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1<strong><b>Third Party Notification?</b></strong></td>
    <td bgcolor="EBEBEB"><input type="checkbox" name="third_party"></font></td></tr>
  </table>
  <table border="1" cellpadding="4" cellspacing="0" style="$STYLE_DEF">
    <tr>
    <td bgcolor="EBEBEB">$font_color1<strong><b>Generic IPR?</b></strong></td>
    <td bgcolor="EBEBEB"><input type="checkbox" name="generic" $generic_checked></font></td></tr>
  </table>
$comply_info
$update_info

  </blockquote>
  <blockquote>
  <table border="1" cellpadding="4" cellspacing="0" style="$STYLE_DEF" width="710">
    <tr>
    <td bgcolor="C1BCA7" colspan=2>$font_color2<strong> I. Patent Holder/Applicant ("Patent Holder")</strong></td></tr>
    <tr>
  <td bgcolor="EEEEE3" width="15%">$font_color1<small>Legal Name :</small></font></td>
  <td bgcolor="EEEEE3">$font_color1<input type="text" onkeypress="return handleEnter(this, event)" name="p_h_legal_name" size="40"></font></td></tr>     
  </table>
  </blockquote>
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" style="$STYLE_DEF" width="710">
    <tr>
    <td bgcolor="AAAAAA" colspan=2>$font_color2<strong>II. Patent Holder's Contact for License Application </strong></font></td></tr>
    <tr>
    <td bgcolor="DDDDDD" width="15%">$font_color1<small>Name :</small></font></td>
    <td bgcolor="DDDDDD">$font_color1<small><input type="text" onkeypress="return handleEnter(this, event)" name="ph_name"  size="25"></small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Title :</small></font></td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="ph_title" size="80"></td></tr>
    <tr>
    <td bgcolor="DDDDDD">$font_color1<small>Department :</small></font></td>
    <td bgcolor="DDDDDD"><input type="text" onkeypress="return handleEnter(this, event)" name="ph_department" size="80"></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Address1 :</small></font></td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="ph_address1" size="80"></td></tr>
    <tr>
    <td bgcolor="DDDDDD">$font_color1<small>Address2 :</small></font></td>
    <td bgcolor="DDDDDD"><input type="text" onkeypress="return handleEnter(this, event)" name="ph_address2" size="80"></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Telephone :</small></font></td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="ph_telephone" size="25"></td></tr>
    <tr>
    <td bgcolor="DDDDDD">$font_color1<small>Fax :</small></font></td>
    <td bgcolor="DDDDDD"><input type="text" onkeypress="return handleEnter(this, event)" name="ph_fax" size="25"></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Email :</small></font></td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="ph_email" size="35"></td></tr>
  </table>
  </blockquote>
  <blockquote>
  <table  border="0" cellpadding="4" cellspacing="0" style="$STYLE_DEF" width="710">
    <tr>
    <td bgcolor="C1BCA7" colspan=2>$font_color2<strong>III. Contact Information for the IETF Participant Whose Personal 
   Belief Triggered the Disclosure in this Template (Optional):</strong></font> </td></tr>
    <tr>
    <td bgcolor="E2DFD3" width="15%">$font_color1<small> Name :</small></td>
    <td bgcolor="E2DFD3"><input type="text" onkeypress="return handleEnter(this, event)" name="ietf_name" size="25"></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Title :</small></td>
    <td bgcolor="EEEEE3"><input type="text" onkeypress="return handleEnter(this, event)" name="ietf_title" size="80"></td></tr>
    <tr>
    <td bgcolor="E2DFD3">$font_color1<small>Department :</small></td>
    <td bgcolor="E2DFD3"><input type="text" onkeypress="return handleEnter(this, event)" name="ietf_department" size="80"></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Address1 :</small></td>
    <td bgcolor="EEEEE3"><input type="text" onkeypress="return handleEnter(this, event)" name="ietf_address1" size="80"></td></tr>
    <tr>
    <td bgcolor="E2DFD3">$font_color1<small>Address2 :</small></td>
    <td bgcolor="E2DFD3"><input type="text" onkeypress="return handleEnter(this, event)" name="ietf_address2" size="80"></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Telephone :</small></td>
    <td bgcolor="EEEEE3"><input type="text" onkeypress="return handleEnter(this, event)" name="ietf_telephone" size="25"></td></tr>
    <tr>
    <td bgcolor="E2DFD3">$font_color1<small>Fax :</small></td>
    <td bgcolor="E2DFD3"><input type="text" onkeypress="return handleEnter(this, event)" name="ietf_fax" size="25"></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Email :</small></td>
    <td bgcolor="EEEEE3"><input type="text" onkeypress="return handleEnter(this, event)" name="ietf_email" size="35"></td></tr>
  </table>
  </blockquote>
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" style="$STYLE_DEF" width="710">
    <tr>
    <td bgcolor="AAAAAA" colspan=2>$font_color2<strong>IV. IETF Document or Working Group Contribution to Which Patent 
     Disclosure Relates </strong></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>RFC Number :</small></td>
    <td bgcolor="EBEBEB"><textarea name="rfc_number" rows="3" cols="8"></textarea></td></tr>
    <tr>
    <td bgcolor="DDDDDD">$font_color1<small>I-D filename (draft-ietf...) :</small></td>
    <td bgcolor="DDDDDD"><textarea name="filename" rows="3" cols="50"></textarea></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>Other Designations :</small></td>
    <td bgcolor="EBEBEB"><input type="text" onkeypress="return handleEnter(this, event)" name="other_designations" size="70"></td></tr>
  </table>
  </blockquote>
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" style="$STYLE_DEF" width="710">
    <tr>
    <td bgcolor="C1BCA7" colspan=2>$font_color2<strong> V. Disclosure of Patent Information (i.e., patents or patent 
   applications required to be disclosed by Section 6 of RFC XXXX)</strong></font></td></tr>
    <td bgcolor="E2DFD3" colspan=2>$font_color1<small> A. For granted patents or published pending patent applications,
   please provide the following information:</small></font> </td></tr>
    <td bgcolor="E2DFD3">$font_color1<small>Patent, Serial, Publication, Registration, or Application/File number(s) :</small></font></td>
    <td bgcolor="E2DFD3"><input type="text" onkeypress="return handleEnter(this, event)" name="p_applications" size="40"> </td></tr>
    <tr>
    <td bgcolor="E2DFD3">$font_color1<small> Date(s) granted or applied for (YYYY-MM-DD):</small></font></td>
    <td bgcolor="E2DFD3"> <input type="text" onkeypress="return handleEnter(this, event)" name="date_applied" size="25"></td></tr>
    <tr>
    <td bgcolor="E2DFD3">$font_color1<small> Country :</small></font></td>
    <td bgcolor="E2DFD3"> <input type="text" onkeypress="return handleEnter(this, event)" name="country" value="$country" size="25"></td></tr>
    <tr>
    <td bgcolor="E2DFD3" colspan=2>$font_color1 <small>Additional Notes : </small></font></td></tr>
    <tr>
    <td  bgcolor="E2DFD3" colspan=2><textarea name="p_notes" rows=4 cols=80>$p_notes</textarea></td></tr>
    <tr>
    <td bgcolor="EEEEE3" colspan=2>$font_color1<small>B. Does your disclosure relate to an unpublished pending patent application? </small></font></td></tr>
    <tr>
    <td bgcolor="EEEEE3" colspan=2>$font_color1<small>Select one :
    <input type="radio" name="selecttype" value="1">Yes
    <input type="radio" name="selecttype" value="0">No</small></font></td></tr>
    <tr>
    <td bgcolor="E2DFD3" colspan=2 width="650">$font_color1<small> C. If an Internet-Draft or RFC includes multiple parts and it is not 
   reasonably apparent which part of such Internet-Draft or RFC is alleged 
   to be covered by the patent information disclosed in Section
   V(A) or V(B), it is helpful if the discloser identifies here the sections of<br>
   the Internet-Draft or RFC that are alleged to be so 
   covered.</small></font>  </td></tr>
    <tr>
    <td bgcolor="E2DFD3" colspan=3><textarea name="disclouser_identify" rows=8 cols=80></textarea></td></tr>
  </table>
  </blockquote>
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" style="$STYLE_DEF" width="710">
    <tr>
    <td bgcolor="AAAAAA" colspan=2>$font_color2<strong>VI. Licensing Declaration </strong></td></tr>
    <tr>
    <td bgcolor="DDDDDD">$font_color1<small>The Patent Holder states that 
       its position with respect to licensing any patent claims contained in the
       patent(s) or patent application(s) disclosed above that would necessarily be infringed by
       implementation of the technology required by the relevant IETF specification ("Necessary Patent Claims"),       for the purpose of implementing such specification,
       is as follows(select one licensing declaration option only): 
         </small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>a) <input type="radio" name="licensing_option" value="1"> No License Required for Implementers.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="checkbox" name="lic_opt_a_sub"> This licensing declaration is limited solely to standards-track IETF documents. </small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>b) <input type="radio" name="licensing_option" value="2"> Royalty-Free, Reasonable and Non-Discriminatory License to All Implementers.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="checkbox" name="lic_opt_b_sub"> This licensing declaration is limited solely to standards-track IETF documents.</small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>c) <input type="radio" name="licensing_option" value="3"> Reasonable and Non-Discriminatory License to All Implementers with Possible Royalty/Fee.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<input type="checkbox" name="lic_opt_c_sub"> This licensing declaration is limited solely to standards-track IETF documents.</small></font></td></tr>

    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>d) <input type="radio" name="licensing_option" value=4> Licensing Declaration to be Provided Later (implies a  
      willingness to commit to the provisions of<br> &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp a), b), or c) above to all implementers; otherwise, the next option 
     "Unwilling to Commit to the<br> &nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp Provisions of a), b), or c) Above" - must be selected)</small></font></td></tr>
    <tr>
    <td bgcolor="EBEBEB">$font_color1<small>e) <input type="radio" name="licensing_option" value=5> Unwilling to Commit to the Provisions 
      of a), b), or c) Above </small></font></td></tr>
     <tr>
    <td bgcolor="EBEBEB">$font_color1<small>f ) <input type="radio" name="licensing_option" value=6> See text box below for licensing declaration.</small></font></td></tr>
    <tr>
    <td bgcolor="DDDDDD">$font_color1<small>Licensing information, comments, notes or URL for further information :</small></font></td></tr> 
    <tr>
    <td bgcolor="DDDDDD"><textarea name="comments" rows=5 cols=80></textarea></td></tr> 
    <tr>
    <td bgcolor="DDDDDD">$font_color1<small><input type="checkbox" name="lic_checkbox" $lic_checkbox_checked>The individual submitting this template represents and warrants that all terms and conditions that must be satisfied for implementers of any covered IETF specification to obtain a license have been disclosed in this IPR disclosure statement.</small></font></td></tr>
  </table>
  </blockquote>
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" style="$STYLE_DEF" width="710">
    <tr>
    <td bgcolor="C1BCA7" colspan=2>$font_color2<strong>VII. Contact Information of Submitter of this Form (if different from
   IETF Participant in Section III above)</strong> </td></tr>
    <tr>
    <td bgcolor="E2DFD3" width="15%">$font_color1<small>Name :</small></font></td>
    <td bgcolor="E2DFD3"><input type="text" onkeypress="return handleEnter(this, event)" name="sub_name" size="25"></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Title :</td>
    <td bgcolor="EEEEE3"><input type="text" onkeypress="return handleEnter(this, event)" name="sub_title" size="80"></td></tr>
    <tr>
    <td bgcolor="E2DFD3">$font_color1<small>Department :</small></font></td>
    <td bgcolor="E2DFD3"><input type="text" onkeypress="return handleEnter(this, event)" name="sub_department" size="80"></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Address1 :</td>
    <td bgcolor="EEEEE3"><input type="text" onkeypress="return handleEnter(this, event)" name="sub_address1" size="80"></td></tr>
    <tr>
    <td bgcolor="E2DFD3">$font_color1<small>Address2 :</td>
    <td bgcolor="E2DFD3"><input type="text" onkeypress="return handleEnter(this, event)" name="sub_address2" size="80"></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Telephone :</small></font></td>
    <td bgcolor="EEEEE3"><input type="text" onkeypress="return handleEnter(this, event)" name="sub_telephone" size="25"></td></tr>
    <tr>
    <td bgcolor="E2DFD3">$font_color1<small>Fax :</td>
    <td bgcolor="E2DFD3"><input type="text" onkeypress="return handleEnter(this, event)" name="sub_fax" size="25"></td></tr>
    <tr>
    <td bgcolor="EEEEE3">$font_color1<small>Email :</small></font></td>
    <td bgcolor="EEEEE3"><input type="text" onkeypress="return handleEnter(this, event)" name="sub_email" size="35"></td></tr>
  </table>
  </blockquote>
  <blockquote>
  <table border="0" cellpadding="4" cellspacing="0" style="$STYLE_DEF" width="710">
    <tr>
    <td bgcolor="AAAAAA" colspan=2>$font_color2<strong>VIII. Other Notes: </strong></font></td></tr>
    <tr>
    <td  bgcolor=DDDDDD><textarea name="other_notes" rows=8 cols=80></textarea></td></tr>
  </table>
  </blockquote>
  <center>
  <table>
    <tr>
    <td>
    <input type="hidden" name="status" value="0">
    <input type="hidden" name="command" value="do_add_ipr">
    <input type="submit" name="submit" value="Submit">
    </td></tr>
  </table></center>
  </form>
  <blockquote>
  <hr>
  <a href="./ipr_admin.cgi"><img src="/images/blue.gif" hspace="3" border="0">IPR Admin page</a><br>
  <a href="https://datatracker.ietf.org/public/ipr_disclosure.cgi"><img src="/images/blue.gif" hspace="3" border="0">IPR Disclosure page</a><br>
  <a href="https://datatracker.ietf.org/public/ipr_list.cgi"><img src="/images/blue.gif" hspace="3" border="0">View IPR Disclosures</a><br><br>
  </blockquote>

};

}


sub display_error {
  my $msg = shift;
  print qq {
  <br><br>
  <center><font size=4 color="red">$msg</font> <br>
  Use the back button on your browser to go back to the previous page</center><br>
    };
  }


sub display_error2 {
  my $msg = shift;
  print qq {
  <br><br>
  <center><font size=4 color="red">$msg</font> <br>
  Use the back button on your browser to go back to the previous page</center><br>
    };
  }


sub do_add_ipr {
  my $q = shift;
  my $id_document_tag = shift;
  my $old_ipr_url = $q->param("old_ipr_url");
  my $additional_old_title1 = $q->param("additional_old_title1");
  my $additional_old_url1 = $q->param("additional_old_url1");
  my $additional_old_title2 = $q->param("additional_old_title2");
  my $additional_old_url2 = $q->param("additional_old_url2");
  my $submitted_date = $q->param("submitted_date");
  my $status = $q->param("status");
  my $p_h_legal_name = $q->param("p_h_legal_name");
  my $document_title = $q->param("document_title");
  my $rfc_number = $q->param("rfc_number");
  my $filename = $q->param("filename");
  my $other_designations = $q->param("other_designations");
  my $p_applications = $q->param("p_applications");
  my $date_applied = $q->param("date_applied");
  my $country = $q->param("country");
  my $p_notes = $q->param("p_notes");
  my $selecttype = $q->param("selecttype");
  my $disclouser_identify = $q->param("disclouser_identify");
  my $licensing_option = $q->param("licensing_option");
  my $lic_checkbox = checktonum($q->param("lic_checkbox"));
  my $comments = $q->param("comments");
  my $other_notes = $q->param("other_notes");
  my $contact_id = $q->param("contact_id");
  my $contact_type = $q->param("contact_type");
  my $ph_name = $q->param("ph_name");
  my $ph_title = $q->param("ph_title");
  my $ph_department = $q->param("ph_department");
  my $ph_telephone = $q->param("ph_telephone");
  my $ph_fax = $q->param("ph_fax");
  my $ph_email = $q->param("ph_email");
  my $ph_address1 = $q->param("ph_address1");
  my $ph_address2 = $q->param("ph_address2");
  my $ietf_name = $q->param("ietf_name");
  my $ietf_title = $q->param("ietf_title");
  my $ietf_department = $q->param("ietf_department");
  my $ietf_telephone = $q->param("ietf_telephone");
  my $ietf_fax = $q->param("ietf_fax");
  my $ietf_email = $q->param("ietf_email");
  my $ietf_address1 = $q->param("ietf_address1");
  my $ietf_address2 = $q->param("ietf_address2");
  my $sub_name = $q->param("sub_name");
  my $sub_title = $q->param("sub_title");
  my $sub_department = $q->param("sub_department");
  my $sub_telephone = $q->param("sub_telephone");
  my $sub_fax = $q->param("sub_fax");
  my $sub_email = $q->param("sub_email");
  my $sub_address1 = $q->param("sub_address1");
  my $sub_address2 = $q->param("sub_address2");
  my $third_party = checktonum($q->param("third_party"));
  my $generic = checktonum($q->param("generic"));
  my $comply = (my_defined($q->param("comply")))?$q->param("comply"):-1;
  my $updated=(defined($q->param("updated")))?$q->param("updated"):0;
  my $lic_opt_a_sub = (my_defined($q->param("lic_opt_a_sub")))?checktonum($q->param("lic_opt_a_sub")):0;
  my $lic_opt_b_sub = (my_defined($q->param("lic_opt_b_sub")))?checktonum($q->param("lic_opt_b_sub")):0;   
  my $lic_opt_c_sub = (my_defined($q->param("lic_opt_c_sub")))?checktonum($q->param("lic_opt_c_sub")):0; 
  my @rfc_temp;
  my @id_temp;
  my $error_message  = "";
  if (my_defined($rfc_number)) {
    $rfc_number =~ s/RFC//g;
    @rfc_temp = split '\n',$rfc_number;
    for my $array_ref (@rfc_temp) {
      chomp($array_ref);
      $array_ref =~ s/\r//;
      $error_message .= "RFC $array_ref is not valid (1)<br>\n" unless (db_select($dbh,"select count(*) from rfcs where rfc_number = $array_ref"));
    }
  }
  if (my_defined($filename)) {
    my @temp = split '\n',$filename;
    for my $array_ref (@temp) {
      chomp($array_ref);
      $_ = $array_ref;       s/\r//;       s/.txt$//;       /(\S+)-(\d\d$)/;
      my $revision = $2;
      s/-\d\d$//;
      my $id_document_tag = db_select($dbh,"select id_document_tag from internet_drafts where filename = '$_'"); 
      $error_message .= "ID '$array_ref' is not valid<br>\n" unless ($id_document_tag);
      push @id_temp,"$id_document_tag-$revision";
    }
  }

  $error_message .= "Submitted Date is missing <br>\n" unless my_defined($submitted_date);
  if (my_defined($error_message)) {
    print $error_message;
    return 0;
  }
  my $remove_old_ipr = $q->param("remove_old_ipr");     
  my $status_to_be = ($remove_old_ipr)?3:1;
  if ($updated > 0) {
    db_update($dbh,"update ipr_detail set status=$status_to_be where ipr_id=$updated");
    my $ipr_id = db_select($dbh,"select max(ipr_id) from ipr_detail");
    $ipr_id++;
    db_update($dbh,"insert into ipr_updates (ipr_id,updated,status_to_be,processed) values ($ipr_id,$updated,$status_to_be,0)");
  }

  ($old_ipr_url,$additional_old_title1,$additional_old_url1,$additional_old_title2,$additional_old_url2, $submitted_date,$p_h_legal_name,$document_title,$disclouser_identify,$other_notes,$comments,$p_notes,$country) = db_quote($old_ipr_url,$additional_old_title1,$additional_old_url1,$additional_old_title2,$additional_old_url2,$submitted_date,$p_h_legal_name,$document_title,$disclouser_identify,$other_notes,$comments,$p_notes,$country);
  $selecttype = '2' unless (my_defined($selecttype));
  $licensing_option = '0' unless (my_defined($licensing_option));
  my $new_ipr_detail = "insert into ipr_detail (old_ipr_url,additional_old_title1,additional_old_url1,additional_old_title2,additional_old_url2,submitted_date,status,p_h_legal_name, document_title, other_designations, p_applications, date_applied, selecttype, disclouser_identify,licensing_option, other_notes,comments, p_notes,country,third_party,generic,comply,lic_opt_a_sub,lic_opt_b_sub,lic_opt_c_sub,lic_checkbox) values ($old_ipr_url,$additional_old_title1,$additional_old_url1,$additional_old_title2,$additional_old_url2,$submitted_date, $status,$p_h_legal_name, $document_title, '$other_designations', '$p_applications', '$date_applied',$selecttype, $disclouser_identify,$licensing_option, $other_notes,$comments, $p_notes,$country,$third_party,$generic,$comply,$lic_opt_a_sub,$lic_opt_b_sub,$lic_opt_c_sub,$lic_checkbox)";
   db_update($dbh,$new_ipr_detail,$program_name,$user_name); 
#print $new_ipr_detail;
  my $ipr_id = db_select($dbh,"select max(ipr_id) from ipr_detail");
  if (my_defined($rfc_number)) {
    for my $array_ref (@rfc_temp) {
      chomp($array_ref);
      db_update($dbh,"insert into ipr_rfcs (ipr_id,rfc_number) values ($ipr_id,$array_ref)",$program_name,$user_name);
    }
  }
  if (my_defined($filename)) {
    for my $array_ref (@id_temp) {
      chomp($array_ref);
      my @temp=split '-',$array_ref;
      my $id_document_tag=$temp[0];
      my $revision=$temp[1];
      db_update($dbh,"insert into ipr_ids (ipr_id,id_document_tag,revision) values ($ipr_id,$id_document_tag,'$revision')",$program_name,$user_name);
    }
  }

  my ($ph_name,$ph_address1,$ph_address2,$ph_title,$ph_department) = db_quote($ph_name,$ph_address1,$ph_address2,$ph_title,$ph_department); 
  my $ipr_id = db_select($dbh,"select max(ipr_id) from ipr_detail");
  my $new_ipr_contacts = "insert into ipr_contacts (ipr_id, contact_type, name, title, department, telephone, fax, email, address1, address2) values ($ipr_id,1, $ph_name, $ph_title, $ph_department, '$ph_telephone', '$ph_fax', '$ph_email', $ph_address1, $ph_address2)";
  db_update($dbh,$new_ipr_contacts,$program_name,$user_name);
  if (my_defined($ietf_name)) {
    my ($ietf_name,$ietf_address1,$ietf_address2,$ietf_title,$ietf_department) = db_quote($ietf_name,$ietf_address1,$ietf_address2,$ietf_title,$ietf_department);
    my $new_ipr_contacts = "insert into ipr_contacts (ipr_id, contact_type, name, title, department, telephone, fax, email, address1, address2) values ($ipr_id, 2, $ietf_name, $ietf_title, $ietf_department, '$ietf_telephone', '$ietf_fax', '$ietf_email', $ietf_address1, $ietf_address2)";
    db_update($dbh,$new_ipr_contacts,$program_name,$user_name);
  }
  if (my_defined($sub_name)) {
    my ($sub_name,$sub_address1,$sub_address2,$sub_title,$sub_department) = db_quote($sub_name,$sub_address1,$sub_address2,$sub_title,$sub_department);
    my $new_ipr_contacts = "insert into ipr_contacts (ipr_id, contact_type, name, title, department, telephone, fax, email, address1, address2) values ($ipr_id, 3, $sub_name, $sub_title, $sub_department, '$sub_telephone', '$sub_fax', '$sub_email', $sub_address1, $sub_address2)";
    db_update($dbh,$new_ipr_contacts,$program_name,$user_name);
  }

  print qq{
  <br>
  <center><font size=4 >This IPR disclosure is now in the queue.<br>
  <a href="ipr_admin.cgi">Go to IPR Admin page to post this IPR disclosure</a><br><br><br>
  <a href="./ipr_internal.cgi"><font size=3>Back to IPR Internal page</a></font></center>
  };

}


  
