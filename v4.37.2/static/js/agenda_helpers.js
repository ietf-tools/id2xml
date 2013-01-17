/*
*   agenda_helpers.js
*
*   Orlando Project: Credil 2013 ( http://credil.org/ )
*   Author: Justin Hornosty ( justin@credil.org )
* 
*   Should contain miscellaneous commonly used functions.
*   
*   
*/

/* logging helper function */
function log(text){
    console.log(text);
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


/* returns a the html for a row in a table 
   as: <tr><td>title</td><td>data</td></tr>
*/
function gen_tr_td(title,data){
    return "<tr><td>"+title+"</td><td>"+data+"</td></tr>";
}

/* creates the 'info' table that is located on the right side. 
   takes in a json. 
*/
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
