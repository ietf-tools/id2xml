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


function print_all(){
    console.log("all");
    console.log(meeting_objs.length);
    for(var i=0; i<meeting_objs.length; i++){
		meeting_objs[i].print_out();
    }
}

function find_title(title){
    $.each(meeting_objs, function(key){
	if (meeting_objs[key].title == title) {
	    console.log(meeting_objs[key]);
	}
    });
}
function find_session_id(session_id){
    $.each(meeting_objs, function(key){
	if (meeting_objs[key].session_id == session_id) {
	    console.log(meeting_objs[key]);
	}
    });
}


/* this pushes every event into the agendas */
function load_events(){
    console.log("load events...");

    /* first delete all html items that might have gotten saved if
     * user save-as and went offline.
     */
    $.each(slot_status, function(key) {
        ssid = slot_status[key];
        insert_cell(ssid.domid, "", true);
    });

    
    $.each(slot_status, function(key) {
        ssid_arr = slot_status[key]
	if(key == "sortable-list"){
	    console.log("sortable list");
	}else{
	
	for(var q = 0; q<ssid_arr.length; q++){
	    ssid = ssid_arr[q];
            slot_id = ("#"+ssid.domid);
            $(slot_id).css('background-color',color_droppable_empty_slot ); //'#006699'
            session = meeting_objs[ssid.session_id];
            if (session != null) {
	       	session.slot_status_key = key;

                session.placed = true;

		// connect to the group.
		session.group();
		
                populate_events(key,
                                session.title,
                                session.description, 
                                session.session_id,
                                session.owner, session.area);
		//log("setting "+slot_id+" as used");

		// note in the group, what the class of column is.
		// this is an array, as the group might have multiple
		// sessions.
		group = session.group();
		group.add_column_class(ssid.column_class);

            } else {
		//log("ssid: "+key+" is null");
		   
            }
	}
	}
    });

}


function populate_events(js_room_id, title, description, session_id, owner, area){
    var eTemplate =     event_template(title, description, session_id, area);
    var t = title+" "+description;
    insert_cell(js_room_id, eTemplate, false);
}

function event_template(event_title, description, session_id, area){
    //console.log("area:"+area)
    return "<table class='meeting_event' id='session_"+session_id+"'><tr id='meeting_event_title'><th class='"+area+"-scheme'>"+event_title+"</th></tr>";
}

function check_free(inp){
    var empty = false;
    slot = slot_status[inp.id];
    if(slot == null){
//	console.log("\t from check_free, slot is null?", inp,inp.id, slot_status[inp.id]);
	return false;
    }
    for(var i =0;i<slot.length; i++){
	if (slot[i].empty == false || slot[i].empty == "False"){
	    return false;
	}
    }
    return true;

}

/* clears any background highlight colors of scheduled sessions */
function clear_highlight(inp_arr){ // @args: array from slot_status{}
    if(inp_arr == null){
	return false;
    }
    for(var i =0; i<inp_arr.length; i++){
	$("#session_"+inp_arr[i].session_id).css('background-color','');
    }
    return true;

}

/* based on any meeting object, it finds any other objects inside the same timeslot. */
function find_friends(inp){
    var ts = $(inp).parent().attr('id');
    var ss_arr = slot_status[ts];
    if (ss_arr != null){
	return ss_arr;
    }
    else{
	console.log("find_friends("+inp+") did not find anything");
	return null;
    }
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

/* Mainly for the case where we didn't get any data back from the server */ 
function empty_info_table(){
    $("#info_grp").html("");
    $("#info_name").html("");
    $("#info_area").html("");
    $("#info_duration").html("");
    $("#info_location").html(generate_select_box()+"<button id='info_location_set'>Set</button>");
    $("#info_location_select").val("");
    $("#info_location_select").val($("#info_location_select_option_"+current_timeslot).val());
    $("#info_responsible").html("");
    $("#info_requestedby").html("");
}


var temp_1;
/* creates the 'info' table that is located on the right side. 
   takes in a json. 
*/

var room_select_html = "";
function calculate_room_select_box() {
    var html = "<select id='info_location_select'>";

    var keys = Object.keys(slot_status)
    var sorted = keys.sort(function(a,b) {
			     a1=slot_status[a];
			     b1=slot_status[b];
			     if (a1.date != b1.date) {
			       return a1.date-b1.date;
			     }
			     return a1.time - b1.time;
			   });

    for (n in sorted) {
        var k1 = sorted[n];
        var val_arr = slot_status[k1];
		
        /* k1 is the slot_status key */
        /* v1 is the slot_obj */
	for(var i = 0; i<val_arr.length; i++){
	    var v1 = val_arr[i];
            html=html+"<option value='"+k1;
            html=html+"' id='info_location_select_option_";
            html=html+v1.timeslot_id+"'>";
            html=html+v1.short_string;
            html=html+"</option>";
	}
    }
    html = html+"</select>";
    room_select_html = html;
    
}
var name_select_html = "";
var temp_sorted = null;
function calculate_name_select_box(){
    var html = "<select id='info_name_select'>";
    var keys = Object.keys(meeting_objs)
    var mobj_array = []
    $.each(meeting_objs, function(key, value){ mobj_array.push(value) });
    mobj_array2 = mobj_array.sort(function(a,b) { return a.title.localeCompare(b.title); });
    temp_sorted =mobj_array;
    for(var i = 0; i < mobj_array.length; i++){
	//console.log("select box mobj["+i+"]="+mobj_array[i]);
	html=html+"<option value='"+mobj_array[i].slot_status_key;
        html=html+"' id='info_name_select_option_";
	ts_id = "err";
	try{
	    ts_id = slot_status[mobj_array[i].slot_status_key][0].timeslot_id;
	    //console.log("ts_id="+ts_id);
	}catch(err){
	}
        html=html+ts_id+"'>";
    

	try{
	    html=html+mobj_array[i].title; // + " (" + mobj_array[i].description + ")";
	} catch(err) {
	    html=html+"ERRROR!!!";
	}
        html=html+"</option>";
    }

    html = html+"</select>";
    name_select_html = html;
 

}



function generate_select_box(){
    return room_select_html;
}




function insert_cell(js_room_id, text, replace){
    slot_id = ("#"+js_room_id);
    try{
	var found;
        if(replace) {
	    found = $(slot_id).html(text);
        } else {
            found = $(slot_id).append($(text));
	    
        }
        $(slot_id).css('background','');
        if(found.length == 0){
            // do something here, if length was zero... then?
        }
	
    }
    catch(err){
	log("error");
	log(err);
    } 
}


function find_empty_test(){
    $.each(slot_status, function(key){
	ss_arr = slot_status[key];
	for(var i = 0; i < ss_arr.length; i++){
	    if(ss_arr[i].scheduledsession_id == null || ss_arr[i].session_id == null){
		console.log(ss_arr[i]);
	    }
	}
    })

}


function find_meeting_no_room(){
    $.each(meeting_objs, function(key){ 
	if(meeting_objs[key].slot_status_key == null) {
	    session = meeting_objs[key]
	    session.slot_status_key = null;
	    populate_events("sortable-list",
                            session.title,
                            session.description, 
                            session.session_id,
                            session.owner, session.area);
	}
    })
}


/* in some cases we have sessions that span over two timeslots.
   so we end up with two slot_status pointing to the same meeting_obj. 
   this this occures when someone requests a session that is extra long
   which will then fill up the next timeslot. 
   
   this functions finds those cases.

   returns a json{ 'ts': arr[time_slot_ids] }

*/
function find_double_timeslots(){
    var duplicate = {};
    
    $.each(slot_status, function(key){
	for(var i =0; i<slot_status[key].length; i++){
	    // goes threw all the slots
	    var ss_id = slot_status[key][i].session_id;
	    if(duplicate[ss_id]){
		duplicate[ss_id]['count']++;
		duplicate[ss_id]['ts'].push(key);
	    }
	    else{
		duplicate[ss_id] = {'count': 1, 'ts':[key]};
		
	    }
	}
    });

    var dup = {};
    // console.log(duplicate);
    $.each(duplicate, function(key){
	if(duplicate[key]['count'] > 1){
	    dup[key] = duplicate[key]['ts'];
	    
	}
    });
    return dup;
	   
}


var child = null;
/* removes a duplicate timeslot. completely. it's gone. */
function remove_duplicate(timeslot_id, ss_id){
    children = $("#"+timeslot_id).children();
    child = children;
    console.log(children);
    for(var i = 0; i< children.length; i++){ // loop to 
	if($(children[i]).attr('id') == "session_"+ss_id){ // make sure we only remove duplicate.
	    try{
		$(children[i]).remove();
	    }catch(exception){
		console.log(exception);
	    }
	}
    }

}



function auto_remove(){
    dup = find_double_timeslots();
    $.each(dup, function(key){
	remove_duplicate(dup[key][1], key);
    })
}


/*
 * Local Variables:
 * c-basic-offset:4
 * End:
 */
