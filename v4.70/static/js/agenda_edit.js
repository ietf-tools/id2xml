
/*
*   agenda_listeners.js
*
*   Orlando Project: Credil 2013 ( http://credil.org/ )
*   Author: Justin Hornosty ( justin@credil.org )
*
*
*   This file should contain functions relating to
*   jquery ui droppable ( http://jqueryui.com/droppable/ )
*   and other interactions.
*
*/




//////////////-GLOBALS----////////////////////////////////////////

var meeting_objs = {};    // contains a list of session objects
var slot_status = {};     // the status of the slot, in format { room_year-month-day_hour: { free: t/f, timeslotid: id } }

var group_objs = {};      // list of working groups

var days = [];
var legend_status = {};   // agenda area colors.

var duplicate_sessions = {};
/********* colors ************************************/

var highlight = "red"; // when we click something and want to highlight it.
var highlight_free = "green"
var dragging_color = "blue"; // color when draging events.
var none_color = '';  // when we reset the color. I believe doing '' will force it back to the stylesheet value.
var color_droppable_empty_slot = 'rgb(0, 102, 153)';

// these are used for debugging only.
var last_json_txt   = "";   // last txt from a json call.
var last_json_reply = [];   // last parsed content

var hidden_rooms = [];
var total_rooms = 0; // the number of rooms
var hidden_days = [];
var total_days = 0; // the number of days

var bucketlist = "sortable-list" // for if/when the id for bucket list changes.
/****************************************************/

/////////////-END-GLOBALS-///////////////////////////////////////

/* refactor this out into the html */
$(document).ready(function() {
    initStuff();

   $("#CLOSE_IETF_MENUBAR").click();

});

/* initStuff()
   This is ran at page load and sets up the entire page.
*/
function initStuff(){
    log("initstuff() ran");
    setup_slots();
    log("setup_slots() ran");
    droppable();
    log("droppable() ran");
    load_events();
    log("load_events() ran");
    load_all_groups();        // should be in a single big block.
    log("groups loaded");
    find_meeting_no_room();
    listeners();
    static_listeners();
    log("listeners() ran");
    calculate_name_select_box();
    duplicate_sessions = find_double_timeslots();

    start_spin();

    meeting_objs_length = Object.keys(meeting_objs).length;

    /* Comment this out for fast loading */
    get_all_conflicts();
    do_work(function(){ return CONFLICT_LOAD_COUNT >= meeting_objs_length }, function(){ stop_spin(); display_conflicts(); });

}


function dajaxice_callback(message){
    /* if the message is empty, we got nothing back from the server, which probably
       means you are offline.
    */
    console.log("callback: "+message);
    if(message == ""){
	console.log("No response from server....");
    }
    /* do something more intelligent here like if the server returned invalid, we would revert the move */
    else{
	stop_spin();
    }
}

function print_all_ss(objs){
    console.log(objs)
}
function get_ss(){
    Dajaxice.ietf.meeting.get_scheduledsessions(print_all_ss);
}


/*
 * Local Variables:
 * c-basic-offset:4
 * End:
 */

