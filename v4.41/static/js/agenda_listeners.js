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

// this function needs to be renamed, it should only deal with this one listener.
function listeners(){
    $('.meeting_event').unbind('click'); // If we don't unbind it, things end up getting stacked, and tons of ajax things are sent. 
    $('.meeting_event').click(meeting_event_click)
}

/* When one clicks something contained inside a 'meeting_event' we 
   traverse up the dom looking for the thing that contained the 
   .meeting_event class. In all cases, it should be a table with an 
   id. From this ID we are able to get the json object from 'meeting_objs'
   and from there ask django for more information
*/
function meeting_event_click(event){
    var ME_id = $(event.target).closest('.meeting_event').attr('id');
    Dajaxice.ietf.meeting.get_info(fill_in_info,{'meeting_obj':meeting_objs[ME_id]} );
}
function fill_in_info(inp){
    $('#ss_info').html(generate_info_table(inp));
}


/* create the droppable */
function droppable(){
    $(function() {
	/* the thing that is draggable */
	$( ".meeting_event").draggable({
	    appendTo: "body",
	    helper: "clone",
	    drag: drag_drag,
	});

	$( "#sortable-list").droppable({
	    over : drop_over,
	    activate: drop_activate,
	    out : drop_out,
	    drop : drop_bucket,
	    start: drop_start,
	})
    
	$("#meetings td").droppable({
	    over :drop_over,
	    activate:drop_activate,
	    out :drop_out,
	    drop : drop_drop,
	    create: drop_create,
	    start: drop_start,

	}); // end $(#meetings td).droppable
    }); // end function()
} // end droppable()


/* what happens when we drop the meeting_event onto a timeslot. */
function drop_drop(event, ui){
    var temp_id = ui.draggable.attr('id');
    var event_json = id_to_json($(this).attr('id')); // make a json with the new values to inject into the event
    var slot_idd = $(this).attr('id');
    new_event = meeting_objs[temp_id];
    var old_id = json_to_id(new_event);
    var empty = check_free(this);
    
    if(empty){
	$(this).css("background","");
	var eTemplate = event_template( new_event.title, 
				        new_event.description,
				        new_event.time, 
				        new_event.session_id,
				        new_event.timeslot_id
				       );
	
	new_event.time = event_json.time;
	new_event.room = event_json.room;
	new_event.date = event_json.date;
	
	$(this).append(eTemplate); // add the html code to the new slot.


	console.log($(this));

	ui.draggable.remove(); // remove the old one. 
	droppable(); // we need to run this again to toggle the new listeners

	slot_status[slot_idd].empty = false;
	slot_status[old_id].empty = true;
	new_event.timeslot_id = slot_status[slot_idd].timeslot_id
	if ((new_event.last_timeslot_id == null) || (new_event.last_timeslot_id != new_event.timeslot_id)){
	    new_event.last_timeslot_id = slot_status[old_id].timeslot_id
	}
	meeting_objs[temp_id] = new_event;
	Dajaxice.ietf.meeting.update_timeslot(dajaxice_callback,{'new_event':new_event});
    }
    else{ // happens when you are moving the item to somewhere that has something in it.
	ui.draggable.css("background",""); // remove the old one. 	
    }
    listeners();
}

/* what happens when we drop the meeting_event onto the bucket list (thing named "unassigned events") */
function drop_bucket(event, ui){
    var temp_id = ui.draggable.attr('id'); // the django
    new_event = meeting_objs[temp_id];
    var old_id = json_to_id(new_event);
    var slot_idd = $(this).attr('id');

    var slot_status_obj = slot_status[old_id];

    slot_status[old_id].empty = true;
    var eTemplate = event_template( new_event.title, 
				    new_event.description,
				    new_event.time, 
				    new_event.session_id,
				    new_event.timeslot_id
				   );
    var free = []
    $.each(slot_status, function(sskey) {
	ss = slot_status[sskey];
	var usable = true;
	if(ss.empty == true){
	    $.each(meeting_objs, function(mkey){
		if(meeting_objs.timeslot_id == ss.timeslot_id){
		    usable = false; 
		}
	    });
	    if(usable){
		new_event.timeslot_id = ss.timeslot_id;
	    }
	}
    });
    
    meeting_objs[temp_id] = new_event;
    $(this).append(eTemplate); // add the html code to the new slot.
    ui.draggable.remove(); // remove the old one. 
    
    Dajaxice.ietf.meeting.update_timeslot(dajaxice_callback,{'new_event':new_event}); /* dajaxice_callback does nothing */ 
    
    droppable(); // we need to run this again to toggle the new listeners
    listeners();
}


/* first thing that happens when we grab a meeting_event */
function drop_activate(event, ui){
    $(event.draggable).css("background","blue");
}


/* what happens when moving a meeting event over something that is 'droppable' */
function drop_over(event, ui){
    if(check_free(this)){
	$(this).css("background","red");
    }
    $(ui.draggable).css("background","blue");
    $(event.draggable).css("background","blue");
}

/* when we have actually dropped the meeting event */
function drop_out(event, ui){
    if(check_free(this)){
	$(this).css("background","");
    }
}


/* functions here are not used at the moment */
function drop_create(event,ui){
}

function drop_start(event,ui){
}

function drag_drag(event, ui){
}

/* ??? */
function handelDrop(event, ui){
    $(d).append(ui.draggable);
}


