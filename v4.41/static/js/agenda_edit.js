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

function event_obj(title,description,room, time,date,django_id,session_id){
    this.title = title;
    this.description = description;
    this.room = room;
    this.time = time;
    this.date = date;
    this.django_id = django_id;
    this.session_id = session_id
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
			meeting_json.django_id
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
	slot_status[slot_id_status] = true;
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
function populate_events(title,description,room, time,date, django_id){
    var eTemplate =     event_template(title, description,time, django_id);
    var t = title+" "+description;
    var good = insert_cell(time,date, room.split(/[ ]/).join('.'), eTemplate);
    if(good < 1){
	event_template(title, description,time).appendTo("#sortable-list");
    }
}


function event_template(event_title, description, time, django_id){
    var part1 = "";
    var part2 = "";
    var part3 = "";
    var part2 = "<table class='meeting_event' id='"+django_id+"'><tr><th>"+event_title+"</th></tr><tr><td style='height:10px'> .."+description+" ..</td></tr></table>"
    return $(part1+part2+part3);
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
    $(this).css("background","red");
    $(ui.draggable).css("background","blue");
    $(event.draggable).css("background","blue");
}
function drop_activate(event, ui){
    $(event.draggable).css("background","blue");

//    show_free();
}

function drop_out(event, ui){
    $(this).css("background","");
}

function drop_create(event,ui){
//    console.log("create");
}

function drop_drop(event, ui){
    $(this).css("background",""); // remove the highlighting from the activate

    var temp_id = ui.draggable.attr('id'); // the django
    try{
	var event_json = id_to_json($(this).attr('id')); // make a json with the new values to inject into the event	
	var slot_id = "#"+$(this).attr('id');
	var slot_idd = $(this).attr('id');

	/* set things to the new values */
	new_event = meeting_objs[temp_id];
	var old_id = json_to_id(new_event);
//	console.log("oldid:" +old_id);
//	console.log(slot_status[slot_idd]);
	var str_slot_idd = slot_status[slot_idd];
	var str_slot_old_id = slot_status[old_id];	
        slot_status[slot_idd] = true;
	try{
            slot_status[old_id] = false;
//	    console.log(slot_status[old_id]);	
	}catch(err){
	    console.log(err);
	    console.log(slot_status);
	}
//	console.log("slot_idd("+slot_idd+") was:"+ str_slot_idd + " but now is: "+ slot_status[slot_idd]);
//	console.log("old_id("+old_id+") was:"+ str_slot_old_id + " but now is: "+ slot_status[old_id]);
	new_event.time = event_json.time;
	new_event.room = event_json.room;
	new_event.date = event_json.date;
    }
    catch(err){ // probably got null, the typical case would be when we are dragging to the sortable list (so it doesn't have any of these properties)
	new_event = meeting_objs[temp_id];
    
	new_event.time = null; // something more intelligent that reflects that there is no time should be put here. 
	new_event.room = null;
	new_event.date = null;

    }

    /* create the template */
    var eTemplate = event_template(new_event.title, 
				   new_event.description,
				   new_event.time, 
				   new_event.django_id
				  );
    Dajaxice.ietf.meeting.update_timeslot(dajaxice_callback,{'new_event':new_event});
    $(this).append(eTemplate); // add the html code to the new slot.
//    console.log($(this).attr('id'));
    ui.draggable.remove(); // remove the old one. 
    droppable(); // we need to run this again to toggle the new listeners

}
/* end droppable fucntions */

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
	    drop : drop_drop,
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
