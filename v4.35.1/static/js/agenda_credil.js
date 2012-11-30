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
}


var meeting_objs = {};  // contains a list of event_obj's

function print_all(){
    console.log("all");
    console.log(meeting_objs.length);
    for(var i=0; i<meeting_objs.length; i++){
	meeting_objs[i].print_out();
    }
    console.log("done");
}


function event_obj(title,description,room, time,date,django_id){
    this.title = title;
    this.description = description;
    this.room = room;
    this.time = time;
    this.date = date;
    this.django_id = django_id;
}


    /* function declerations */
 /*   this.print_out = function() {
	console.log("---- Django id:"+this.django_id+" ------------------------------");
	console.log("title:"+this.title);
	console.log("description:"+this.description);
	console.log("room:"+this.room);
	console.log("time:"+this.time);
	console.log("date:"+this.date);

    } */
//}


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
    try{
	var found = $(slot_id).append(text);
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

function id_to_json(id){
    var split = id.split('_');
    
    return {"location":split[0],"date":split[1],"time":split[2]}
}

function droppable(){
    $(function() {
	$("#accordion").accordion();
	$( "#sortable-list li").draggable({
	    appendTo: "body",
	    helper: "clone",
	});
	$( ".meeting_event").draggable({
	    appendTo: "body",
	    helper: "clone",
	});
	$("#meetings td").droppable({
	    over : function(event, ui){
		$(this).css("background","red");
		$(ui.draggable).css("background","blue");
		$(event.draggable).css("background","blue");
	    },
	    activate: function(event, ui){
		$(event.draggable).css("background","blue");
	    },
	    out : function(event, ui){
		$(this).css("background","");
	    },
	    drop : function(event, ui){
		$(this).css("background",""); // remove the highlighting from the activate
		var event_json = id_to_json($(this).attr('id')); // make a json with the new values to inject into the event		
		var temp_id = ui.draggable.attr('id'); // the django

		/* set things to the new values */
		new_event = meeting_objs[temp_id];

		new_event.time = event_json.time;
		new_event.room = event_json.room;
		new_event.date = event_json.date;

		
		/* create the template */
		var eTemplate = event_template(new_event.title, 
					       new_event.description,
					       new_event.time, 
					       new_event.django_id
					      );
		
		Dajaxice.ietf.meeting.update_timeslot(dajaxice_callback,{'new_event':new_event});
		$(this).append(eTemplate); // add the html code to the new slot.
		ui.draggable.remove(); // remove the old one. 
		droppable(); // we need to run this again to toggle the new listeners
	
		
	    } // end drop

	}); // end droppable
    }); // end function()

} // end sort_js

