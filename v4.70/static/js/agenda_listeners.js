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

function resize_listeners() {
    for(i = 0; i<days.length;i++){
        $("#resize-"+days[i]+"-spacer").resizable({maxHeight:10,
						   handles: "e, s",
						   minWidth:2,

						  });

    }

}



/* this function needs to be renamed... it should only deal with listeners who need to be unbound prior to rebinding. */
function listeners(){
    //$(".agenda_slot td").not(".meeting_event ui-draggable").unbind('click');
    //$(".agenda_slot td").not(".meeting_event ui-draggable").click(function(event){ console.log("#meetings clicked"); console.log(event); });
    // $($("#meetings").not('.meeting_event').not('.ui-draggable')).click(function(){ console.log("#meetings clicked") }); //show_all_conflicts);
    $("#meetings").unbind('click');
    $("#meetings").click(all_click);

    $('.meeting_event').unbind('click'); // If we don't unbind it, things end up getting stacked, and tons of ajax things are sent.
    $('.meeting_event').click(meeting_event_click);

    $('#info_location_select').unbind('change');
    $('#info_location_select').change(info_location_select_change);

    $('#info_name_select').unbind('change');
    $('#info_name_select').change(info_name_select_change);

    $('.color_checkboxes').unbind('click');
    $('.color_checkboxes').click(color_legend_click);

    resize_listeners()

    $('#find_free').unbind('click');
    $('#find_free').click(function(event){ find_free(); });


    /* listener for when one clicks the 'show all' checkbox */
    $('.cb_all_conflict').unbind('click');
    $('.cb_all_conflict').click(cb_all_conflict);

    /* hiding rooms */
    $(".close_room").unbind('click');
    $(".close_room").click(close_room)

    /* hiding days */
    $(".close_day").unbind('click');
    $(".close_day").click(close_day);


    // $("#show_hidden_days").unbind('click');
    // $("#show_hidden_days").click(show_hidden_days);
    // $("#show_hidden_rooms").unbind('click');
    // $("#show_hidden_rooms").click(show_hidden_rooms);


    $("#show_all_area").unbind('click');
    $("#show_all_area").click(show_all_area);

    $("#show_all_button").unbind('click');
    $("#show_all_button").click(show_all);


}

function all_click(event){
    var classes = $(event.srcElement).attr('class').split(' ');
    console.log(classes);
    if(classes.indexOf('meeting_obj') < 0){
	show_all_conflicts();
    }
    // console.log(this);
    // console.log($(this));
}

/************ click functions *********************************************************************/
function cb_all_conflict(event){
    var conflict_clicked = $(event.target).attr('id');
    try{
	var conflict_clicked = conflict_clicked.substr(3);
    }catch(err){

    }
    $("."+conflict_clicked+" input").click();


}

function close_room(event){
    var close_room = $(event.target).attr('id');
    close_room =  close_room.substr(6);
    console.log(close_room);
    $("#"+close_room).hide("fast");
    hidden_rooms.push("#"+close_room);
    $("#hidden_rooms").html((hidden_rooms.length.toString()+"/"+total_rooms.toString()));
}

function show_hidden_rooms(event){
    $.each(hidden_rooms, function(index,room){
	$(room).show("fast");
    });
    hidden_rooms = [];
    $("#hidden_rooms").html(hidden_rooms.length.toString()+"/"+total_rooms.toString());
}

function close_day(event){
    var close_day = $(event.target).attr('id');
    close_day = close_day.substr(6);
    close_day = ".day_"+close_day;
    $(close_day).hide("slow");
    hidden_days.push(close_day);
    $("#hidden_days").html(hidden_days.length.toString()+"/"+total_days.toString());
}

function show_all(){
    show_hidden_days();
    show_hidden_rooms();
}

function show_hidden_days(event){
    $.each(hidden_days, function(index,room){
	$(room).show("fast");
    });
    hidden_days = [];
    $("#hidden_days").html(hidden_days.length.toString()+"/"+total_days.toString());

}

function show_all_area(event){
    var areas = find_same_area($("#info_area").children().text());
    console.log(areas);
    $.each(areas, function(index,obj){

	var selector = $("#"+obj.slot_status_key);
	if(slot_item_hidden(selector) ){
	    $("#"+obj.slot_status_key).effect("highlight", {color:"lightcoral"}, 2000);
	}
    });
}


/************ END click functions *********************************************************************/

function slot_item_hidden(selector){
// checking if the thing we will visually display is hidden. (performing effects will break the previous hide)
    var show = true;

    $.each(hidden_days, function(index,value){
	if(selector.hasClass(value.substr(1))){
	    show=false;
	    return show;
	}
    });
    return show;
}




function find_empty_slot(){
    var free_slots = []
    $.each($(".free_slot"), function(index,item){
	if(!$(item).hasClass("show_conflict_view_highlight")){
	    free_slots.push(item);
	}
    });

    if(free_slots.length > 0){
	return free_slots[0]; // just return the first one.
    }
    else{
	return null;
    }

}

function find_free(){
    var empty_slot = find_empty_slot();
    if(empty_slot != null){
	$(empty_slot).effect("highlight", {},3000);
	if(current_item != null){
	    $(current_item).addClass('ui-effects-transfer');
	    $(current_item).effect("transfer", {to: $(empty_slot) }, 1000);
	}
	$(current_item).removeClass('ui-effects-transfer');
    }
}

function find_free(){
    var empty_slot = find_empty_slot();
    if(empty_slot != null){
	$(empty_slot).effect("highlight", {},3000);
	if(current_item != null){
	    $(current_item).addClass('ui-effects-transfer');
	    $(current_item).effect("transfer", {to: $(empty_slot) }, 1000);
	}
	$(current_item).removeClass('ui-effects-transfer');
    }
}


function expand_spacer(target) {
    var current_width = $(target).css('min-width');
    current_width = current_width.substr(0,current_width.search("px"));
    current_width = parseInt(current_width) + 20;
    $(target).css('min-width',current_width);
    $(target).css('width',current_width);

}

function expand_spacer(target) {
    var current_width = $(target).css('min-width');
    current_width = current_width.substr(0,current_width.search("px"));
    current_width = parseInt(current_width) + 20;
    $(target).css('min-width',current_width);
    $(target).css('width',current_width);

}

/* the functionality of these listeners will never change so they do not need to be run twice  */
function static_listeners(){
    $('#CLOSE_IETF_MENUBAR').click(hide_ietf_menu_bar);
}

function color_legend_click(event){
    var clicked = $(event.target).attr('id');
    if(legend_status[clicked]){
	legend_status[clicked] = false;
    }
    else{
	legend_status[clicked] = true;
    }
    set_transparent();
}

var conflict_status = {};

function conflict_click(event){
    var clicked = $(event.target).attr('id');
    var constraint = find_conflict(clicked);
    if(conflict_status[clicked]){
	conflict_status[clicked] = false;
	constraint.clear_conflict_view();
	constraint.checked = "checked";
    }
    else{
	conflict_status[clicked] = true;
	constraint.show_conflict_view();
    }
}


function set_transparent(){
    $.each(meeting_objs, function(key){
	$.each(legend_status, function(k){
	    if(meeting_objs[key].area == k){
		if(legend_status[k] == true){
		    if(meeting_objs[key].slot_status_key == null){
			$("#session_"+key).show();
		    }
		    else{
			$("#session_"+key).css({'opacity':1});
			$("#session_"+key).draggable("option","cancel",null);
		    }
		}
		else{
		    if(meeting_objs[key].slot_status_key == null){
			$("#session_"+key).hide();
		    }
		    else{
			$("#session_"+key).css({'opacity':0.1});
			$("#session_"+key).draggable("option","cancel",".meeting_event");
		    }
		}
	    }

	})
    })

}

var clicked_event;
var __DEBUG__SESSION_OBJ;
var __DEBUG__SLOT_OBJ;
var current_item = null;
var current_timeslot = null;
function meeting_event_click(event){
    hide_all_conflicts();
    try{
	clear_highlight(find_friends(current_item));
    }catch(err){ }

    $(last_item).css("background-color", '');
    $(last_item).removeClass('free_slot');

    /* clear set ot conflict views */
    clear_conflict_classes();
    conflict_classes = {};
    var slot_id = $(event.target).closest('.agenda_slot').attr('id');
    var meeting_event_id = $(this).attr('id');

    clicked_event = event;

    slot = slot_status[slot_id];
    meeting_event_id = meeting_event_id.substring(8,meeting_event_id.length);
    var session = meeting_objs[meeting_event_id];

    if(slot == null){ // not in a real slot...
	var slot_obj = {   slot_id: meeting_event_id ,
            scheduledsession_id:meeting_event_id,
            timeslot_id: null,
            session_id: meeting_event_id,
         }
	session.load_session_obj(fill_in_session_info, slot_obj);
	return;
    }

    for(var i = 0; i<slot.length; i++){
	session_id = slot[i].session_id;
	if(session_id == meeting_event_id){
	    $("#session_"+session_id).css('background-color',highlight);
	    current_item = "#session_"+session_id;

	    current_timeslot = slot[i].timeslot_id;

	    empty_info_table();
	    session.load_session_obj(fill_in_session_info, slot[i]);
	}
	__DEBUG__SLOT_OBJ = slot[i];
	__DEBUG__SESSION_OBJ = session;
    }

}

var last_item = null; // used during location change. we make the background color
// of the timeslot highlight because it is being set into that slot.
function info_location_select_change(){
    if(last_item != null){
	$(last_item).css('background-color','');
    }
    last_item = '#'+$('#info_location_select').val();
    $(last_item).css('background-color',highlight);
}

var last_name_item = null;
function info_name_select_change(){
    $(last_item).css("background-color", '');
    $(current_item).css('background-color','');
    if(last_name_item != null){
	$(last_name_item).css('background-color','');
    }
    if(current_item != null){
	$(current_item).css('background-color','');
     }
    last_name_item = '#'+$('#info_name_select').val();
    var slot_id = last_name_item.substring(1,last_name_item.length);
    var ssk = meeting_objs[slot_id].slot_status_key
    current_item = "#session_"+slot_id; //slot_status_obj[0].session_id;
    if(ssk != null){
	var slot_status_obj = slot_status[ssk];
	current_timeslot = slot_status_obj[0].timeslot_id;
	ss = slot_status_obj[0];
	session = ss.session();
	// now set up the call back that might have to retrieve info.
	session.load_session_obj(fill_in_session_info, ss);

    }
    else{
	ss = meeting_objs[slot_id];
	ss.load_session_obj(fill_in_session_info,ss);
    }
    $(current_item).css('background-color',highlight);
    // $('#'+$('#info_name_select').val()).css('background-color',highlight);

    // now find the relevant session.  The session may be found by
    // calling ss.session().

}

function XMLHttpGetRequest(url, sync) {
    var oXMLHttpRequest = new XMLHttpRequest;
    oXMLHttpRequest.open('GET', url, sync);
    oXMLHttpRequest.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    oXMLHttpRequest.setRequestHeader("X-CSRFToken", Dajaxice.get_cookie('csrftoken'));

    return oXMLHttpRequest;
}

function retrieve_session_by_id(session_id) {
    var session_obj = {};
    var oXMLHttpRequest = XMLHttpGetRequest(meeting_base_url+'/session/'+session_id+".json", false);
    oXMLHttpRequest.send();
    if(oXMLHttpRequest.readyState == XMLHttpRequest.DONE) {
        try{
            last_json_txt = oXMLHttpRequest.responseText;
            session_obj   = JSON.parse(oXMLHttpRequest.responseText);
            last_json_reply = session_obj;
        }
        catch(exception){
            console.log("retrieve_session_by_id("+session_id+") exception: "+exception);
        }
    }
    return session_obj;
}

function fill_in_constraints(session_obj, success, constraint_list, andthen)
{
    if(!success || constraint_list['error']) {
        console.log("failed to get constraints for session_id: "+session_obj.session_id, constraint_list['error']);
        return false;
    }

    var i = 10;
    $.each(constraint_list, function(key){
	       thing = constraint_list[key];
	       session_obj.add_constraint_obj(thing);
           });
    session_obj.sort_constraints();

    // now draw the constraints on the screen.
    andthen(session_obj);
}


function dajaxice_error(a){
    console.log("dajaxice_error");
}

function fill_in_session_info(session, success, extra) {
    if(session == null || session == "None" || !success){
	empty_info_table();
    }
    $('#ss_info').html(session.generate_info_table(extra));
    session.retrieve_constraints_by_session(draw_constraints);
}

function group_name_or_empty(constraint) {
    if(constraint == undefined) {
	return "";
    } else {
	return constraint.conflict_view();
    }
}

function draw_constraints(session) {
    $("#conflict_table_body").html("");

    if(!"conflicts" in session) {
        return;
    }

    var conflict1_a = session.conflicts[1][0];
    var conflict1_b = session.conflicts[1][1];
    var conflict2_a = session.conflicts[2][0];
    var conflict2_b = session.conflicts[2][1];
    var conflict3_a = session.conflicts[3][0];
    var conflict3_b = session.conflicts[3][1];

    for(var i=0; i<=session.conflict_half_count; i++) {
        $("#conflict_table_body").append("<tr><td class='conflict1'>"+
                                         group_name_or_empty(conflict1_a[i])+
                                         "</td>"+
                                         "<td class='conflict1'>"+
                                         group_name_or_empty(conflict1_b[i])+
                                         "</td><td class='border'></td>"+
                                         "<td class='conflict2'>"+
                                         group_name_or_empty(conflict2_a[i])+
                                         "</td>"+
                                         "<td class='conflict2'>"+
                                         group_name_or_empty(conflict2_b[i])+
                                         "</td><td class='border'></td>"+
                                         "<td class='conflict3'>"+
                                         group_name_or_empty(conflict3_a[i])+
                                         "</td>"+
                                         "<td class='conflict3'>"+
                                         group_name_or_empty(conflict1_b[i])+
                                         "</tr>");
	// console.log("draw", i,
	// 	    group_name_or_empty(conflict1_a[i]),
	// 	    group_name_or_empty(conflict1_b[i]),
	// 	    group_name_or_empty(conflict2_a[i]),
	// 	    group_name_or_empty(conflict2_b[i]),
	// 	    group_name_or_empty(conflict3_a[i]),
	// 	    group_name_or_empty(conflict3_b[i]));
    }

    // setup check boxes for conflicts
    $('.conflict_checkboxes').unbind('click');
    $('.conflict_checkboxes').click(conflict_click);

    $('.conflict_checkboxes').click();

}

var menu_bar_hidden = false;
function hide_ietf_menu_bar(){
    $('#IETF_MENUBAR').toggle('slide',"",100);
    if(menu_bar_hidden){
	menu_bar_hidden = false;
	$('.wrapper').css('width','auto');
	$('.wrapper').css('margin-left','160px');
	$('#CLOSE_IETF_MENUBAR').html("<");

    }
    else{
	menu_bar_hidden = true;
	$('.wrapper').css('width','auto');
	$('.wrapper').css('margin-left','0px');
	$('#CLOSE_IETF_MENUBAR').html(">");
    }
}



/* create the droppable */
function droppable(){
    $(function() {
	/* the thing that is draggable */
	$( ".meeting_event").draggable({
	    appendTo: "body",
	    helper: "clone",
	    drag: drag_drag,
	    start: drag_start,
	});

	$( "#sortable-list").droppable({
	    over : drop_over,
	    activate: drop_activate,
	    out : drop_out,
	    drop : drop_drop,
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


var arr_key_index = null;
function update_to_slot(meeting_id, to_slot_id, force){
    var to_slot = slot_status[to_slot_id];

    var found = false;
    for(var i=0; i<to_slot.length; i++){
	if(to_slot[i].empty == "True" || to_slot[i].empty == true){ // we found a empty place to put it.
	    // setup slot_status info.
	    to_slot[i].session_id = meeting_id;

	    to_slot[i].empty = false;

	    // update meeting_obj
	    //meeting_objs[meeting_id].slot_status_key = to_slot[i].domid
	    arr_key_index = i;
	    meeting_objs[meeting_id].placed = true;
	    found = true;
	    // update from_slot

	    return found;
	}
    }

    if(!found && force){
	to_slot.push(new slot_obj(to_slot[0].scheduledsession_id, to_slot[0].empty, to_slot[0].timeslot_id,meeting_id,to_slot[0].room, to_slot[0].time,to_slot[0].date,to_slot[0].domid));
	found = true;
	return found;
    }
    return found;
}


function update_from_slot(meeting_id, from_slot_id){

    var from_slot = slot_status[meeting_objs[meeting_id].slot_status_key]; // remember this is an array...
    var found = false;

    if(from_slot_id != null){ // it will be null if it's coming from a bucketlist
	for(var k = 0; k<from_slot.length; k++){
	    if(from_slot[k].session_id == meeting_id){
		found = true;
		from_slot[k].empty = true;
		from_slot[k].session_id = null;
		return found;
	    }
	}
    }
    else{
	found = true; // this may be questionable. It deals with the fact that it's coming from a bucketlist.
	return found;
    }
    return found;
}



function drop_drop(event, ui){

    var meeting_id = ui.draggable.attr('id'); // the meeting id.
    meeting_id = meeting_id.substring(8,meeting_id.length); // it has session_ infront of it. so make it this.

    var to_slot_id = $(this).attr('id'); // where we are dragging it.
    var to_slot = slot_status[to_slot_id]

    var from_slot_id = meeting_objs[meeting_id].slot_status_key;
    var from_slot = slot_status[meeting_objs[meeting_id].slot_status_key]; // remember this is an array...

    bucket_list = (to_slot_id == "sortable-list");
    if(!check_free({id:to_slot_id}) ){
	console.log("not free...");
	if(!bucket_list){
	    return
	}
    }
    var update_to_slot_worked = false;

    if(bucket_list){
	update_to_slot_worked = update_to_slot(meeting_id, to_slot_id, true);
    }
    else{
	update_to_slot_worked = update_to_slot(meeting_id, to_slot_id);
    }

    if(update_to_slot_worked){
	if(update_from_slot(meeting_id, from_slot_id)){
	    remove_duplicate(from_slot_id,meeting_id);
	    // do something
	}
	else{
	    console.log("issue updateing from_slot");
	    console.log("from_slot_id",from_slot_id, slot_status[from_slot_id]);
	    return;
	}
    }
    else{
	console.log("issue updateing to_slot");
	console.log("to_slot_id",to_slot_id, slot_status[to_slot_id]);
	return;
    }
    meeting_objs[meeting_id].slot_status_key = to_slot[arr_key_index].domid
    //*****  do dajaxice call here  ****** //

    var eTemplate = event_template(meeting_objs[meeting_id].title, meeting_objs[meeting_id].description, meeting_objs[meeting_id].session_id,meeting_objs[meeting_id].area);
    $(this).append(eTemplate)

    ui.draggable.remove();



    /* set colors */
    $(this).removeClass('highlight_free_slot');
    if(check_free({id:to_slot_id}) ){
	// $(this).css('background-color', color_droppable_empty_slot)
	$(this).addClass('free_slot')
    }
    else{
	// $(this).css('background-color',none_color);
	$(this).removeClass('free_slot')
    }

    if(check_free({id:from_slot_id}) ){
	// $("#"+from_slot_id).css('background-color', color_droppable_empty_slot)
	$("#"+from_slot_id).addClass('free_slot');
    }
    else{
	// $("#"+from_slot_id).css('background-color',none_color);
	$("#"+from_slot_id).removeClass('free_slot');
    }
    // $("#"+"sortable-list").css('background-color',none_color);
    $("#"+"sortable-list").removeClass('free_slot');
    /******************************************************/

    var schedulesession_id = null;
    for(var i =0; i< to_slot.length; i++){
	if (to_slot[i].session_id == meeting_id){
	    schedulesession_id = to_slot[i].scheduledsession_id;
	    break;
	}
    }
    if(schedulesession_id != null){
	start_spin();
	Dajaxice.ietf.meeting.update_timeslot(dajaxice_callback,
					      {
						  'session_id':meeting_objs[meeting_id].session_id,
						  'scheduledsession_id': schedulesession_id,
					      });

    }
    else{
	console.log("issue sending ajax call!!!");
    }

    droppable();
    listeners();
}

/* what happens when we drop the session onto the bucket list
   (thing named "unassigned events") */
function drop_bucket(event,ui){

    var meeting_id = ui.draggable.attr('id');
    meeting_id = meeting_id.substring(8,meeting_id.length); // it has session_ infront of it. so make it this.

    var to_slot_id = $(this).attr('id'); // where we are dragging it.
    var from_slot_id = meeting_objs[meeting_id].slot_status_key;

    if(to_slot_id == "sortable-list"){ // it's being moved to the bucketlist so update where it's coming from.

	if (!update_from_slot(meeting_id, from_slot_id)){
	    console.log(slot_status[from_slot_id]);
	    console.log("issue updating from_slot");
	    return;
	}
    }
    else{ // moving from bucket list to a slot, so update it's dest.

	if (!update_to_slot(meeting_id, to_slot_id)){
	    console.log("issue updating to_slot");
	    return;
	}
	meeting_objs[meeting_id].slot_status_key = to_slot[arr_key_index].domid

    }


    //*****  do dajaxice call here  ****** //

    var eTemplate = event_template(meeting_objs[meeting_id].title, meeting_objs[meeting_id].description, meeting_objs[meeting_id].session_id);
    $(this).append(eTemplate)

    ui.draggable.remove();

    droppable();
    listeners();

}

/* first thing that happens when we grab a meeting_event */
function drop_activate(event, ui){
    $(event.draggable).css("background",dragging_color);
}


/* what happens when moving a meeting event over something that is 'droppable' */
function drop_over(event, ui){
    if(check_free(this)){
	$(this).addClass('highlight_free_slot');
    }
    // $(ui.draggable).css("background",dragging_color);
    // $(event.draggable).css("background",dragging_color);
}

/* when we have actually dropped the meeting event */
function drop_out(event, ui){
    if(check_free(this)){
	if($(this).attr('id') != bucketlist){
	    $(this).addClass("free_slot");
	}
    }
    $(this).removeClass('highlight_free_slot');
}


/* functions here are not used at the moment */
function drop_create(event,ui){
}

function drop_start(event,ui){
}

function drag_drag(event, ui){
}

function drag_start(event, ui){
    return;
}

/* ??? */
function handelDrop(event, ui){
    $(d).append(ui.draggable);
}

/*
 * Local Variables:
 * c-basic-offset:4
 * End:
 */
