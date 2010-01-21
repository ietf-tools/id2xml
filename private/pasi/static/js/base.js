// Copyright (C) 2009-2010 Nokia Corporation and/or its subsidiary(-ies).
// All rights reserved. Contact: Pasi Eronen <pasi.eronen@nokia.com>
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions
// are met:
//
//  * Redistributions of source code must retain the above copyright
//    notice, this list of conditions and the following disclaimer.
//
//  * Redistributions in binary form must reproduce the above
//    copyright notice, this list of conditions and the following
//    disclaimer in the documentation and/or other materials provided
//    with the distribution.
//
//  * Neither the name of the Nokia Corporation and/or its
//    subsidiary(-ies) nor the names of its contributors may be used
//    to endorse or promote products derived from this software
//    without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
// LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

function showBallot(draftName, trackerId) {

    var handleEditPosition = function() {
        IETF.ballotDialog.hide();
        var tid = document.getElementById("ballot_dialog_id").innerHTML;
        window.open("https://datatracker.ietf.org/cgi-bin/idtracker.cgi?command=open_ballot&id_document_tag="+tid);
    }; 
    var handleClose = function() {
        IETF.ballotDialog.hide();
    };
    var el;

    if (!IETF.ballotDialog) {
        el = document.createElement("div");
        el.innerHTML = '<div id="ballot_dialog" style="visibility:hidden;"><div class="hd">Positions for <span id="ballot_dialog_name">draft-ietf-foo-bar</span><span id="ballot_dialog_id" style="display:none;"></span></div><div class="bd">  <div id="ballot_dialog_body" style="overflow-y:scroll; height:500px;"></div>   </div></div>';
        document.getElementById("ietf-extras").appendChild(el);

        var buttons = [{text:"Close", handler:handleClose, isDefault:true}];
	if (("Area_Director" in IETF.user_groups) ||
	    ("Secretariat" in IETF.user_groups)) {
	    buttons.unshift({text:"Edit Position", handler:handleEditPosition});
	}
	var kl = [new YAHOO.util.KeyListener(document, {keys:27}, handleClose)]						 
        IETF.ballotDialog = new YAHOO.widget.Dialog("ballot_dialog", {
            visible:false, draggable:false, close:true, modal:true,
            width:"860px", fixedcenter:true, constraintoviewport:true,
            buttons: buttons, keylisteners:kl});
        IETF.ballotDialog.render();
    }
    document.getElementById("ballot_dialog_name").innerHTML = draftName;
    document.getElementById("ballot_dialog_id").innerHTML = trackerId;

    IETF.ballotDialog.show();

    el = document.getElementById("ballot_dialog_body");
    el.innerHTML = "Loading...";
    YAHOO.util.Connect.asyncRequest('GET', 
          "/doc/"+draftName+"/_ballot.data",
          { success: function(o) { el.innerHTML = (o.responseText !== undefined) ? o.responseText : "?"; }, 
            failure: function(o) { el.innerHTML = "Error: "+o.status+" "+o.statusText; },
            argument: null
   	  }, null);
}
function editBallot(trackerId) {
    window.open("https://datatracker.ietf.org/cgi-bin/idtracker.cgi?command=open_ballot&id_document_tag="+trackerId);
}

IETF.Dialog = function(id, userConfig) {
    IETF.Dialog.superclass.constructor.call(this, id, {
        visible:false, draggable:false, close:true, modal:true, 
        fixedcenter:true, constraintoviewport:true, 
	keylisteners:new YAHOO.util.KeyListener(document, {keys:27}, {fn:function() { this.hide(); }, scope:this, correctScope:true})
	});
    this.cfg.applyConfig(userConfig);
    this.render("ietf-extras");
};
YAHOO.lang.extend(IETF.Dialog, YAHOO.widget.Dialog);

function editData() {
    var handleSubmit = function() {
        IETF.editDialog.hide();
    }; 
    if (!IETF.editDialog) {
      var buttons = [{text:"Save", handler:handleSubmit},
		     {text:"Cancel", handler:function() { this.hide(); },
		      isDefault:true}];
      IETF.editDialog = new IETF.Dialog("doc_edit_dialog", {
	      width:"700px", buttons: buttons});
      IETF.editDialog.setHeader("Edit State");
      IETF.editDialog.setBody('<div><label style="width:130px;float:left;">Intended status:</label><select style="width:150px;"><option value="1" >BCP</option><option value="2" >Draft Standard</option><option value="3" >Experimental</option><option value="5" >Informational</option><option value="6" selected>Proposed Standard</option></select></div><div style="margin-top:4px;"><label style="width:130px;float:left;">Responsible AD:</label><select style="width:150px;"><option value="49" >Arkko, Jari</option><option value="59" >Bonica, Ron</option><option value="51" selected>Callon, Ross</option></select></div><div  style="margin-top:4px;"><label style="width:130px;float:left;">Notice emails:</label><input type="text" style="width:530px;" value="ipsecme-chairs@tools.ietf.org, draft-ietf-ipsecme-aes-ctr-ikev2@tools.ietf.org"/></div><div  style="margin-top:4px;"><label style="width:130px;float:left;">IESG Note:</label><textarea rows="2" style="width:530px;">Foo Bar (foo.bar@example.org) is the document shepherd.</textarea></div><div  style="margin-top:4px;"><label style="width:130px;float:left;">Telechat date:</label><select><option value="49" >(not on agenda)</option><option value="59" >2010-01-21</option><option value="51" selected>2010-02-04</option></select> <input type="checkbox"/> Returning item</div>');
    }
    IETF.editDialog.show();
}

function changeState() {
    var handleSubmit = function() {
        this.hide();
    }; 
    if (!IETF.stateDialog) {
      var buttons = [
          {text:"Save", handler:handleSubmit},
          {text:"Cancel", handler:function () {this.hide();}, isDefault:true}];
      IETF.stateDialog = new IETF.Dialog("doc_state_dialog", {
            width:"350px", buttons: buttons});
      IETF.stateDialog.setHeader("Change State");
      IETF.stateDialog.setBody('<div><label style="width:130px;float:left;">State:</label><select style="width:200px;"><option value="10" >Publication Requested</option> <option value="11">AD Evaluation</option> <option value="12" >Expert Review</option><option value="15" >Last Call Requested</option><option value="16" >In Last Call</option><option value="18" >Waiting for Writeup</option><option value="19" >Waiting for AD Go-Ahead</option><option value="20" >IESG Evaluation</option><option value="21" >IESG Evaluation - Defer</option><option value="27" >Approved-announcement to be sent</option></select></div><div><label style="width:130px;float:left;">Substate:</label><select style="width:200px;"><option value=0>(none)</option><option value=1 >Point Raised - writeup needed</option><option value=2 >AD Followup</option>  <option value=3 >External Party</option>  <option value=5 >Revised ID Needed</option></select></div><div style="margin-top:8px;"><img src="http://tools.ietf.org/images/22x22/actions/next.png" style="vertical-align:middle;"/> <a href="">To AD Evaluation::Revised ID Needed</a><br/><img src="http://tools.ietf.org/images/22x22/actions/next.png" style="vertical-align:middle;"/> <a href="">To IETF Last Call</a></div>');
    }
    IETF.stateDialog.show();
}

function addComment() {
    var handleSubmit = function() {
	this.hide();
    }; 
    if (!IETF.commentDialog) {
	var buttons = [{text:"Add Comment", handler:handleSubmit},
          {text:"Cancel", handler:function () {this.hide();}, isDefault:true}];
	IETF.commentDialog = new IETF.Dialog("doc_comment_dialog", {width:"560px", buttons:buttons});
	IETF.commentDialog.setHeader("Add Comment");
	IETF.commentDialog.setBody('<textarea rows="2" style="width:530px;"></textarea>');
    }
    IETF.commentDialog.show();
}

function editPosition() {
    var handleSubmit = function() {

    }; 
    if (!IETF.positionDialog) {
      var buttons = [{text:"Save+Send Email", handler:handleSubmit},{text:"Save", handler:handleSubmit},
          {text:"Cancel", handler:function () {this.hide();}, isDefault:true}];
      IETF.positionDialog = new IETF.Dialog("doc_position_dialog", {
	      width:"630px", buttons: buttons});
      IETF.positionDialog.setHeader("Change Position");
      IETF.positionDialog.setBody('<div><input type="radio" name="position" value="Yes"/> Yes <input type="radio" name="position" value="No Objection" checked="checked"/> No Objection <input type="radio" name="position" value="Discuss"/> Discuss    <input type="radio" name="position" value="Abstain"/> Abstain <input type="radio" name="position" value="Recuse"/> Recuse <input type="radio" name="position" value=""/> No record </div><div style="margin-top:8px;"><label>Discuss text:</label><br /><textarea name="discussText" style="width: 600px; height:150px; font-family:monospace;"></textarea><br/><label>Comment text:</label><br /><textarea style="width: 600px; height:150px; font-family:monospace;" name="commentText"></textarea></div>');
    }
    IETF.positionDialog.show();
}
