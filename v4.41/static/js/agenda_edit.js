//////////////-GLOBALS----////////////////////////////////////////

var meeting_objs = {};    // contains a list of event_obj's
var slot_status = {};     // the status of the slot, in format { room_year-month-day_hour: { free: t/f, timeslotid: id } }
var days = [];
/////////////-END-GLOBALS-///////////////////////////////////////

/* refactor this out into the html */
$(document).ready(function() {
    initStuff();

});

function dajaxice_callback(message){

}


/* logging helper function */
function log(text){
    console.log(text);
}

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

/* hide_empty()
   looks for the rooms with no events in them and hides them.
   This is mostly a temp fix for hiding stuff. DOMs should just
   never be created. Allowing the toggle may be a nice feature though
*/
function hide_empty(){

    for(i=0;i<days.length;i++){
	var childs = ($("#"+days[i]+"tbody").children());
	for(k=0;k<childs.length;k++){
	    if($(childs[k]).find(".meeting_event").length == 0){
	    	$(childs[k]).toggle();
	    }
	}
    }

}



function print_all(){
    console.log("all");
    console.log(meeting_objs.length);
    for(var i=0; i<meeting_objs.length; i++){
	meeting_objs[i].print_out();
    }
}

/* this pushes every event into the calendars */
function load_events(){
    $.each(meeting_objs, function(key) {
	    meeting_json = meeting_objs[key];
	    populate_events(meeting_json.title,
		        meeting_json.description, 
			meeting_json.room, 
			meeting_json.time, 
			meeting_json.date,
			meeting_json.session_id,
			meeting_json.timeslot_id,
			meeting_json.owner
		);
	});
}

/* Dump listeners into here */
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


/* returns a the html for a row in a table 
   as: <tr><td>title</td><td>data</td></tr>
*/
function gen_tr_td(title,data){
    var trtd = [];
    
    trtd.push("<tr>");
    trtd.push("<td>");
    trtd.push(title);
    trtd.push("</td>");
    trtd.push("<td>");
    trtd.push(data);
    trtd.push("</td>");
    trtd.push("</tr>");
    
    return trtd.join(' ');
}

function generate_info_table(inp){
    var html = [];
    html.push("<table>");
    
    html.push(gen_tr_td("Group", inp.group));
    html.push(gen_tr_td("name", inp.name));
    html.push(gen_tr_td("Requested Time", inp.requested_time));
    html.push(gen_tr_td("Requested By", inp.requested_by));
    html.push(gen_tr_td("Time", inp.ts_time));
    html.push(gen_tr_td("Duration", inp.ts_duration));
    
    html.push(gen_tr_td("Room:", inp.room));
    

    html.push("</table>");
    return html.join(' ');

}

function fill_in_info(inp){
    $('#ss_info').html(generate_info_table(inp));
}

function print_all_ss(objs){
    console.log(objs)
}
function get_ss(){
    Dajaxice.ietf.meeting.get_scheduledsessions(print_all_ss);
}

function insert_cell(time,date,room,text){
    slot_id = ("#"+room+"_"+date+"_"+time);
    slot_id_status = (room+"_"+date+"_"+time);
    try{
	var found = $(slot_id).append(text);
	$(slot_id).css('background','');
	if(found.length == 0){
	    // do something here....
	}
    }
    catch(err){
	log("error");
	log(err);
    } 
}

function populate_events(title,description,room, time,date, session_id){
    var eTemplate =     event_template(title, description,time, session_id);
    var t = title+" "+description;
    var good = insert_cell(time,date, room.split(/[ ]/).join('.'), eTemplate);
    if(good < 1){
	event_template(title, description,time).appendTo("#sortable-list");
    }
}

function event_template(event_title, description, time, session_id){
    var part1 = "";
    var part2 = "";
    var part3 = "";
    var part2 = "<table class='meeting_event' id='"+session_id+"'><tr id='meeting_event_title'><th>"+event_title+"</th></tr><tr><td> .."+description+" ..</td></tr></table>"
    // var part2 = "<table class='meeting_event' id='"+session_id+"'><tr id='meeting_event_title'><th>"+event_title+"</th></tr><tr><td style='height:10px'> .."+description+" ..</td></tr></table>"
    return $(part1+part2+part3);
}

function check_free(inp){
    var empty = false;
    try{
	empty = slot_status[inp.id].empty;
    }
    catch(err){
	empty = false;
	console.log(err);
    }
    return empty;
}

function handelDrop(event, ui){
    log(ui.draggable);
    log(d);
    $(d).append(ui.draggable);
}

function json_to_id(j){
     return (j.room+"_"+j.date+"_"+j.time);
}

function id_to_json(id){
    if(id != null){
	var split = id.split('_');
	return {"room":split[0],"date":split[1],"time":split[2]}
    }
    else{
	return null;
    }
}

/* following functions are for droppable, they should be reusable */
function drop_over(event, ui){
    if(check_free(this)){
	$(this).css("background","red");
    }
    $(ui.draggable).css("background","blue");
    $(event.draggable).css("background","blue");
}

function drop_activate(event, ui){
    $(event.draggable).css("background","blue");
    

}

function drop_out(event, ui){
    if(check_free(this)){
	$(this).css("background","");
    }
}

function drop_create(event,ui){

}

function drop_start(event,ui){
}

function drop_drop(event, ui){
    
    var temp_id = ui.draggable.attr('id');
    var event_json = id_to_json($(this).attr('id')); // make a json with the new values to inject into the event
    var slot_idd = $(this).attr('id');
    new_event = meeting_objs[temp_id];
    var old_id = json_to_id(new_event);
    var empty = check_free(this);
    
    if(empty){
	$(this).css("background","");
	var eTemplate = event_template(new_event.title, 
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
//	console.log("slot_status["+slot_idd+"] set to:"+ slot_status[slot_idd].empty);

	slot_status[old_id].empty = true;
//	console.log("slot_status["+old_id+"] set to:"+ slot_status[old_id].empty);
	new_event.timeslot_id = slot_status[slot_idd].timeslot_id
	if ((new_event.last_timeslot_id == null) || (new_event.last_timeslot_id != new_event.timeslot_id)){
	    new_event.last_timeslot_id = slot_status[old_id].timeslot_id
	}
	meeting_objs[temp_id] = new_event;
//	console.log(meeting_objs);
//	console.log(meeting_objs[temp_id]);
	Dajaxice.ietf.meeting.update_timeslot(dajaxice_callback,{'new_event':new_event});
    }
    else{ // happens when you are moving the item to somewhere that has something in it.
	ui.draggable.css("background",""); // remove the old one. 	
    }
    listeners();
}

function drop_bucket(event, ui){
    var temp_id = ui.draggable.attr('id'); // the django
    new_event = meeting_objs[temp_id];
    var old_id = json_to_id(new_event);
    var slot_idd = $(this).attr('id');

    var slot_status_obj = slot_status[old_id];

    slot_status[old_id].empty = true;
    // console.log("-----------------------------------------");
    // console.log(new_event);
    // console.log("slot_status["+old_id+"] set to:"+ slot_status[old_id].empty);
    // console.log(slot_status[old_id]);
    // console.log("-----------------------------------------");
    var eTemplate = event_template(new_event.title, 
				   new_event.description,
				   new_event.time, 
				   new_event.session_id,
				   new_event.timeslot_id
				  );
    // give me any id at all, so we don't have timeslots in limbo if the page refreshes.
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
    
    Dajaxice.ietf.meeting.update_timeslot(dajaxice_callback,{'new_event':new_event});
    
    droppable(); // we need to run this again to toggle the new listeners
    listeners();
    // console.log(meeting_objs[temp_id]);
    // console.log("done drop_bucket");
    
}

/* end droppable fucntions */

function drag_drag(event, ui){
    // console.log("draggiung...");
    // console.log(this);
    // $(this).css("background","red");
    // console.log($(this));
}
var ee; 
function droppable_clone(event){
    console.log("--------------------------");
    console.log(event);
    ee = event
    var evnt = $(event.target.parentNode.parentNode.parentNode.parentNode);
    // $(evnt).children();
    $(evnt).css("width","100px");
    // console.log(evnt.attr('id'));
    console.log(evnt.html());
    return $(evnt) //.html();
    // return $(event.target.parentNode.parentNode.parentNode.parentNode).html()
    // console.log("--------------------------");
}

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



