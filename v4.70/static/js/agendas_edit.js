/*
*   agendas_edit.js
*
*   Orlando Project: Credil 2013 ( http://credil.org/ )
*   Author: Justin Hornosty    <justin@credil.org>
*   Author: Michael Richardson <mcr@sandelman.ca>
*
*
*   This file should contain functions relating to
*   editing a list of agendas
*
*/




//////////////-GLOBALS----////////////////////////////////////////


/////////////-END-GLOBALS-///////////////////////////////////////

$(document).ready(function() {
    init_agendas_edit();

    /* hide the side bar by default. */
    $("#CLOSE_IETF_MENUBAR").click();
});

/*
   init_timeslot_editf()
   This is ran at page load and sets up appropriate listeners
*/
function init_agendas_edit(){
    log("initstuff() ran");
    static_listeners();

    $(".agenda_visible").unbind('click');
    $(".agenda_visible").click(toggle_visible);

    $(".agenda_public").unbind('click');
    $(".agenda_public").click(toggle_public);

    $(".agenda_delete").unbind('click');
    $(".agenda_delete").click(delete_room);

    $(".agenda_official_mark").unbind('click');
    $(".agenda_official_mark").click(toggle_official);
}

function delete_room(event) {
    var agenda_url    = $(event.target).closest('tr').attr('href');
    event.preventDefault();

    $("#agenda_delete_dialog").dialog({
      buttons : {
        "Confirm" : function() {
	    $.ajax({
		url: agenda_url,
	       type: 'DELETE',
	    success: function(result) {
			window.location.reload(true);
                 }
            });
            $(this).dialog("close");
        },
        "Cancel" : function() {
            $(this).dialog("close");
        }
      }
    });

    $("#room_delete_dialog").dialog("open");
}

function toggle_public(event) {
    var span_to_replace = event.target;
    var current_value   = $(event.target).html();
    var agenda_url      = $(event.target).closest('tr').attr('href');

    var new_value = 1;
    log("value "+current_value)
    if(current_value == "public") {
        new_value = 0
    }
    event.preventDefault();

    $.ajax({ "url": agenda_url,
             "type": "PUT",
             "data": { "public" : new_value },
             "dataType": "json",
             "success": function(result) {
                 /* result is a json object */
                 value = result["public"]
                 log("new value "+value)
                 $(span_to_replace).html(value)
             }});
}

function toggle_visible(event) {
    var span_to_replace = event.target;
    var current_value   = $(event.target).html();
    var agenda_url      = $(event.target).closest('tr').attr('href');

    var new_value = 1;
    log("value "+current_value)
    if(current_value == "visible") {
        new_value = 0
    }
    event.preventDefault();

    $.ajax({ "url": agenda_url,
             "type": "PUT",
             "data": { "visible" : new_value },
             "dataType": "json",
             "success": function(result) {
                 /* result is a json object */
                 value = result["visible"]
                 log("new value "+value)
                 $(span_to_replace).html(value)
             }});
}

function toggle_official(event) {
    var agenda_url    = $(event.target).closest('tr').attr('href');
    var agenda_name   = $(event.target).closest('tr').attr('agenda_name');
    var agenda_id     = $(event.target).closest('tr').attr('id');
    var meeting_url   = $(".agenda_list_title").attr('href');
    event.preventDefault();

    /*
     * if any of them are clicked, then go through all of them
     * and set them to "unofficial", then based upon the return
     * we might this one to official.
     */

    /* if agenda_official is > 1, then it is enabled */
    var value = 0;
    if($(event.target).html() == "official") {
        value = 1;
    }
    var new_value = agenda_name;
    var new_official = 1;
    if(value > 0) {
        new_value    = "None";
        new_official = 0;
    }

    var rows = $(".agenda_list tr:gt(0)");
    rows.each(function(index) {
                  log("row: "+this);
		  /* this is now the tr */
		  $(this).removeClass("agenda_official_row");
		  $(this).addClass("agenda_unofficial_row");

		  /* not DRY, this occurs deep in the model too */
		  $(this).find(".agenda_official_mark").html("unofficial");
	      });

    log("clicked on "+agenda_url+" sending to "+meeting_url);

    $.ajax({ "url": meeting_url,
             "type": "PUT",
             "data": { "agenda" : new_value },
             "dataType": "json",
             "success": function(result) {
                   /* result is a json object */
                   if(new_official) {
                       $("#"+agenda_id).find(".agenda_official_mark").html("official");
                       $("#"+agenda_id).addClass("agenda_official_row");
                   }}});
}


/*
 * Local Variables:
 * c-basic-offset:4
 * End:
 */

