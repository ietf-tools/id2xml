
/* refactor this out into the html */
$(document).ready(function() {
    initStuff();

});


function initStuff(){
    log("initstuff() ran");
    listeners();
    log("listeners() ran");
//    populate_events("event 2");
//    CreateCalendar();
//    test_js();
    clicker()
    setup_slots();
    sort_js();
    log("sort_js() ran");

 
}



/* logging helper function */
function log(text){
    console.log(text);
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

function insert_cell(time,date, room, text){
    //log()//.find(room))
//    log("#"+time+" "+room+" "+text);
//    log(time+" "+room+" "+text+" "+date);
    if(date == "2012-11-03"){
	log(time+" "+room+" "+text+" "+date);
    }


    room = "td."+room;
    time = "#"+time;
    date = "."+date;

    try{
	var temp = $(date).find(".cells");
	temp = $(temp).find(time);
	temp = temp.find(room);
	if(temp.length == 0 ){
	    //log("null");
	}
	else{	
	    temp.append(text);
	    return 1;
	
	}
    }
    catch(err){
	log("err....");
//	log(room);
	log(err);
	return -1;
    }
   
}


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

function event_template(event_title, description, time){

    var part1 = "";
    var part2 = "";
    var part3 = "";
    var part2 = "<table class='meeting_event'><tr><th>"+event_title+"</th></tr><tr><td style='height:10px'> .."+description+" ..</td></tr></table>"
    return $(part1+part2+part3);
}
    


function populate_events(title,description,room, time,date){
    var eTemplate =     event_template(title, description,time);
    var t = title+" "+description;
    //log("split:"+room);
//    log(room.split());
    var good = insert_cell(time,date, room.split(/[ ]/).join('.'), eTemplate);
    if(good < 1){
	event_template(title, description,time).appendTo("#sortable-list");
    }
 //   log("title:" + title);
  //  log(" description:" + description);
  //  log("time:" +time);

}


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

function handelDrop(event, ui){
    log(ui.draggable);
    log(d);

    $(d).append(ui.draggable);
    
}

function sort_js(){
    $(function() {
//	$("#accordion").accordion();
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
//		log($(this));
		log("found:");
		log($(this).find(".meeting_event"));
		$(this).find(".ui-state-default").remove();
		
		
//		$( "<div class='meeting_event'></div>").text(ui.draggable.text() ).appendTo(this);
//		(ui.draggable.html() ).appendTo(this);
		log("html>>");

		log(ui.draggable.html());
		
		var table_code = "<table class='meeting_event'>";
		table_code = table_code+ui.draggable.html()+"</table>";
		
		log("----------------------");
		log(table_code);
		log("----------------------");
		$(this).append(table_code);
		log($(this).html());
//		log(ui.draggable.html());

		log($(this).css("height"));
		var height = $(this).css("height")

		log("to");
		log(height);


		ui.draggable.remove();
		sort_js(); // we need to run this again to toggle the new listeners
	
		
	    }

	});
    });

}




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



	
	