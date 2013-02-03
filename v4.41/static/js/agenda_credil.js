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
    sort_js();
    log("sort_js() ran");
    load_events();
    log("load_events() ran");
}


var meeting_objs = [];

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
    
    /* function declerations */
    this.print_out = function() {
	console.log("---- Django id:"+this.django_id+" ------------------------------");
	console.log("title:"+this.title);
	console.log("description:"+this.description);
	console.log("room:"+this.room);
	console.log("time:"+this.time);
	console.log("date:"+this.date);

    }
}


/* this pushes every event into the calendars */
function load_events(){
    for(var i = 0; i<meeting_objs.length; i++){
	populate_events(meeting_objs[i].title,
		        meeting_objs[i].description, 
			meeting_objs[i].room, 
			meeting_objs[i].time, 
			meeting_objs[i].date,
			meeting_objs[i].django_id
		       );
    }
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

function sort_js(){
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
		$(this).css("background","");
		log("found:");
		log($(this).attr('id'));
		log($(this).find(".meeting_event"));
		$(this).find(".ui-state-default").remove();
		
//		log("html>>");

		log(ui.draggable.attr('id'));
		
		var table_code = "<table class='meeting_event'>";
		table_code = table_code+ui.draggable.html()+"</table>";
	
/*	
		log("----------------------");
		log(table_code);
		log("----------------------");
*/
		$(this).append(table_code);
		log($(this).html());
//		log(ui.draggable.html());

/*
		log($(this).css("height"));
		var height = $(this).css("height")

		log("to");
		log(height);
*/

		ui.draggable.remove();
		sort_js(); // we need to run this again to toggle the new listeners
	
		
	    }

	});
    });

}



function eventClicked(event){
    log("event clicked");
    log(event);

    $("#event_StartDate").val(event.start);
    $("#event_EndDate").val(event.end);
    $("#event_Title").val(event.title);
    
    var all_day = null;
    
}

function select_function(start,end,allDay){
    var name = "select_function:";
    log(name+"  start:["+start+"] End:["+end+"] allday:["+allDay+"]");
    $("#event_StartDate").val(start);
    $("#event_EndDate").val(end);
    
}


var cal_events = [ ];



	

/*
function add_event(){
    var startdate = $("#event_StartDate").val();
    var enddate = $("#event_EndDate").val();
    var title = $("#event_Title").val();
    
    var y_checked = $("#event_AllDay_yes").attr('checked');
    var n_checked = $("#event_AllDay_no").attr('checked');
    var all_day = null;
    if(y_checked == "checked" && n_checked == null){
	all_day = true;
    }
    else if(n_checked == "checked" && y_checked == null){
	all_day = false;
    }
    if(startdate != "" && enddate != "" && title != "" && all_day != null){
	log(title +" "+startdate + " " + enddate +  " " + all_day);
	var new_event = { 
	    "title": title,
	    "start": startdate,
	    "end": enddate,
	    "allDay": all_day
	};
	cal_events.push(new_event);

	$('#calendar').fullCalendar('refetchEvents');
	log("pushed new event:"+new_event);


    }
    else{
	log("missing some values...");
	log("title:"+title+"|startdate:"+startdate+"|enddate:"+enddate+"|allday:"+all_day);
    }
    
}
*/


/*
function clicker(){
    $("#0800").click(function() {
	//log($(this).find("td"));
	//log("#0800");
    });
    $(".cells").click(function() {
//	insert_cell("#0800", "td.Salon.C", "bla");
	$(this).each(function(){
//	    log($(this).html());
	});
    });
    
}
*/

	

/*
function test_js(){
    $(function() {
        $(".obj").draggable({
	    revert:true,
	    snap:true,
	    snapMode:"both",
	    distance: 2,
	    opacity: true,
	    grid: [128,128],


	});
	$(".timeslot").droppable({
	    
	    over: function() {
		//d = $(this).get(0);
		d = $(this);
	    },
	    drop: handelDrop,
	   
	});
});


}
*/
