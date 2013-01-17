/* logging helper function */
function log(text){
    console.log(text);
}

/* refactor this out into the html */
$(document).ready(function() {
    initStuff();

});

/* initStuff() 
   This is ran at page load and sets up the entire page. 
*/
function initStuff(){
    log("initstuff() ran");
    listeners();
    log("listeners() ran");
    setup_slots();
    log("setup_slots() ran");
    droppable();
    log("droppable() ran");
    load_events();
    log("load_events() ran");
    //print_all();
    //console.log(slot_status);
}

////////////// GLOBALS    ////////////////////////////////////////
var meeting_objs = {};  // contains a list of event_obj's
var slot_status = {}; 
///////////// END GLOBALS ///////////////////////////////////////

function print_all(){
    console.log("all");
    console.log(meeting_objs.length);
    for(var i=0; i<meeting_objs.length; i++){
	meeting_objs[i].print_out();
    }
    console.log("done");
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
    $('#ToggleCalendar').click(function(){
	$('#calendar').toggle();
    });
    
    // button to add event
    $('#AddEvent').click(function(){
	add_event();
    });

    // Radio buttons
    $('#event_AllDay_yes').click(function(){
	$('#event_AllDay_no').attr('checked',false);
    });
    $('#event_AllDay_no').click(function(){
	$('#event_AllDay_yes').attr('checked',false);
    });

}




function insert_cell(time,date,room,text){
    slot_id = ("#"+room+"_"+date+"_"+time);
    slot_id_status = (room+"_"+date+"_"+time);
    try{
	var found = $(slot_id).append(text);
	$(slot_id).css('background','');
	//slot_status[slot_id_status] = true;
	if(found.length == 0){
	 //   log(slot_id);
	 //   log(text)
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
    var part2 = "<table class='meeting_event' id='"+session_id+"'><tr><th>"+event_title+"</th></tr><tr><td style='height:10px'> .."+description+" ..</td></tr></table>"
    return $(part1+part2+part3);
}
    

function check_free(inp){
    var empty = false;
    try{
	
	console.log("trying...");
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

function dajaxice_callback(message){
    //console.log("dajaxice says:"+message);
}
function json_to_id(j){
     return (j.room+"_"+j.date+"_"+j.time);
}
function id_to_json(id){
    var split = id.split('_');
    return {"room":split[0],"date":split[1],"time":split[2]}
}

/* following functions are for droppable, they should be reusable */
function drop_over(event, ui){
//    $(this).css("background","red");
    if(check_free(this)){
	$(this).css("background","red");
    }
    $(ui.draggable).css("background","blue");
    $(event.draggable).css("background","blue");
}
function drop_activate(event, ui){
    $(event.draggable).css("background","blue");

//    show_free();
}

function drop_out(event, ui){
    if(check_free(this)){
	$(this).css("background","");
    }
}

function drop_create(event,ui){
//    console.log("create");
}

function drop_drop(event, ui){
    console.log("drop_drop");
    //$(this).css("background",""); // remove the highlighting from the activate
    var temp_id = ui.draggable.attr('id');
    var event_json = id_to_json($(this).attr('id')); // make a json with the new values to inject into the event
//    var slot_id = "#"+$(this).attr('id');
    var slot_idd = $(this).attr('id');
    new_event = meeting_objs[temp_id];
    var old_id = json_to_id(new_event);
    /* create the template */
    
    // try{
    // 	var empty = slot_status[slot_idd].empty;
    // }
    // catch(err){
    // 	empty = false;
    // }
    //console.log("slot_idd:"+slot_idd);
    var empty = check_free(this);
    if(empty){
	$(this).css("background","");
	var eTemplate = event_template(new_event.title, 
				       new_event.description,
				       new_event.time, 
				       new_event.session_id,
				       new_event.timeslot_id
				      );
	console.log(new_event);
	new_event.time = event_json.time;
	new_event.room = event_json.room;
	new_event.date = event_json.date;
	

	
	$(this).append(eTemplate); // add the html code to the new slot.
	//    console.log($(this).attr('id'));
	ui.draggable.remove(); // remove the old one. 
	droppable(); // we need to run this again to toggle the new listeners
	if(slot_idd == "sortable-list"){
	    console.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
	}
	slot_status[slot_idd].empty = false;
	console.log("slot_status["+slot_idd+"] set to:"+ slot_status[slot_idd].empty);

	slot_status[old_id].empty = true;
	console.log("slot_status["+old_id+"] set to:"+ slot_status[old_id].empty);
	new_event.timeslot_id = slot_status[slot_idd].timeslot_id
	if ((new_event.last_timeslot_id == null) || (new_event.last_timeslot_id != new_event.timeslot_id)){
	    new_event.last_timeslot_id = slot_status[old_id].timeslot_id
	}
	meeting_objs[temp_id] = new_event;
	console.log(meeting_objs);
	console.log(meeting_objs[temp_id]);
	Dajaxice.ietf.meeting.update_timeslot(dajaxice_callback,{'new_event':new_event});
    }
    else{ // happens when you are moving the item to somewhere that has something in it.
	console.log("this is not empty");
	ui.draggable.css("background",""); // remove the old one. 	
    }
    // }catch(err){ // happens when you move the object to a slot that never had something in it. 
    // 	console.log("there was a error, but really we are indicating the slot is not empty");
    // 	console.log("the error was:"+err);
    // 	ui.draggable.css("background",""); // if we don't do this, it will stay highlighted blue
    // }
    console.log("done drop_drop");

}

/* end droppable fucntions */


function drop_bucket(event, ui){
    
    console.log("drop_bucket");
    var temp_id = ui.draggable.attr('id'); // the django
    new_event = meeting_objs[temp_id];
    var old_id = json_to_id(new_event);
    var slot_idd = $(this).attr('id');
    console.log("temp_id:"+temp_id);
    console.log("slot_id:"+slot_idd);
    var slot_status_obj = slot_status[old_id];
    //slot_status_obj.empty = true;
    slot_status[old_id].empty = true;
    console.log("-----------------------------------------");
    console.log(new_event);
    console.log("slot_status["+old_id+"] set to:"+ slot_status[old_id].empty);
    console.log(slot_status[old_id]);
    console.log("-----------------------------------------");
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
    console.log(meeting_objs[temp_id]);
    console.log("done drop_bucket");
    
}

function droppable(){
    $(function() {
	/* the thing that is draggable */
	$( ".meeting_event").draggable({
	    appendTo: "body",
	    helper: "clone",
	});

	$( "#sortable-list").droppable({
	    over : drop_over,
	    activate: drop_activate,
	    out : drop_out,
	    drop : drop_bucket,
	})
    
	$("#meetings td").droppable({
	    over :drop_over,
	    activate:drop_activate,
	    out :drop_out,
	    drop : drop_drop,
	    create: drop_create,

	}); // end $(#meetings td).droppable
    }); // end function()
} // end droppable()



// not implemented
function show_free(){
    // $("#meetings td").click(function(){
    // 	try{
    // 	$.each(slot_status, function(key) {
    // 	    if(slot_status[key] == false){
    // 		console.log("false");
    // 	    }
    // 	    else{
    // 	    }
    // 	});
    // 	}
    // 	catch(err){
    // 	    console.log(err);
    // 	}
		  
    // })

}
