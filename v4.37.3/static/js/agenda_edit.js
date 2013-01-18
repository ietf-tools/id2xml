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

var meeting_objs = {};    // contains a list of event_obj's
var slot_status = {};     // the status of the slot, in format { room_year-month-day_hour: { free: t/f, timeslotid: id } }
var days = [];
/////////////-END-GLOBALS-///////////////////////////////////////

/* refactor this out into the html */
$(document).ready(function() {
    initStuff();

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

    listeners();
    log("listeners() ran");
    hide_empty();

}


function dajaxice_callback(message){

}

function print_all_ss(objs){
    console.log(objs)
}
function get_ss(){
    Dajaxice.ietf.meeting.get_scheduledsessions(print_all_ss);
}






