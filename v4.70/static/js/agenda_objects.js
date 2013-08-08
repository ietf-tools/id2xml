/*
,----
|
|   FILE: agenda_objects.js
|
|   AUTHOR: Justin Hornosty ( justin@credil.org )
|     Orlando Project <-> Credil, 2012 ( credil.org )
|
|   Description:
|      Contains the objects relating to django's models.
|      Manulaption and helper functions are also located here.
|      Display logic should be contained in credil_agenda.js ( this should be renamed )
|
|   Functions:
|      - check_delimiter(inp)
|      - upperCaseWords(inp)
|
|
|      - event_obj:
|          - short_string()
|
`----
*/


function createLine(x1,y1, x2,y2){
    var length = Math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2));
  var angle  = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
  var transform = 'rotate('+angle+'deg)';

    var line = $('<div>')
        .appendTo('#meetings')
        .addClass('line')
        .css({
          'position': '',
          'transform': transform
        })
        .width(length)
        .offset({left: x1, top: y1});

    return line;
}


function empty_callback(inp){
//    console.log('inp:', inp);
}

function get_all_constraints(){
    for(s in meeting_objs){
	show_non_conflicting_spots(s)
    }

}

function display_conflicts(){
    get_all_conflicts();
    show_all_conflicts();
}

var all_conflicts = [];

function show_all_conflicts(){
    clear_conflict_classes();
    for(var i =0; i<all_conflicts.length;i++){
	if(all_conflicts[i][0].attr('class').split(' ').indexOf('show_conflict_specific_box') < 0){
	    //console.log(all_conflicts[i][0]);
	    all_conflicts[i][0].addClass("show_conflict_specific_box");
	    all_conflicts[i][1].addClass("show_conflict_specific_box");
	}
	else{
	    //console.log(all_conflicts[i][0].attr('class').split(' '));
	    }

    }
}
function hide_all_conflicts(){
   for(var i =0; i<all_conflicts.length;i++){
	    all_conflicts[i][0].removeClass("show_conflict_specific_box");
	    all_conflicts[i][1].removeClass("show_conflict_specific_box");
    }

}


var CONFLICT_LOAD_COUNT = 0;

function get_all_conflicts(){
    console.log("get_all_conflicts()");
    for(s in meeting_objs){
	try{
	    meeting_objs[s].retrieve_constraints_by_session(then_this,
							    function(){
								CONFLICT_LOAD_COUNT++;
								console.log(CONFLICT_LOAD_COUNT+"/"+meeting_objs_length);

							    });
	}
	catch(err){
	   // console.log(err);
	}

    }
}

var __DEBUG_SHOW_CONSTRAINT = null;
function then_this(inp){
    //console.log(inp);
    try{
	var vertical_location = "."+$("#"+inp.slot_status_key).attr('class').split(' ')[1];  // the timeslot for all rooms.
	}
    catch(err){
    }

    if(inp.constraints.conflict != null){
	$.each(inp.constraints.conflict, function(i){
	    classes=inp.constraints.conflict[i].column_class();
	    if(classes != null){
		$.each(classes, function(index,value){
		    if(value[1] == vertical_location){
			// there is a conflict!
			__DEBUG_SHOW_CONSTRAINT = $("#"+value[0]).children()[0];
			var conflict_pair = [$("#session_"+inp.session_id),$("#"+value[0])];
			all_conflicts.push(conflict_pair);
		    }

		});
	    }
	});
    }

}


function show_non_conflicting_spots(ss_id){
    var conflict_spots = []
    $.each(conflict_classes, function(key){
	conflict_spots.push(conflict_classes[key].session.slot_status_key);
    });
    var empty_slots = find_empty_slots();
    conflict_spots.forEach(function(val){
	empty_slots.forEach(function(s){
	    if(val == s.key){
	    }
	});
    });
}

function find_empty_slots(){
    var empty_slots = [];
    $.each(slot_status, function(key){
	for(var i =0; i<slot_status[key].length; i++){
	    if(slot_status[key][i].empty == "True" || slot_status[key][i].empty == true){
		var pos = { "index" :i, key:key } ;
		empty_slots.push(pos);
	    }
	}
    });
    return empty_slots;
}


function slot(){
}


/* tests short_string */
function test_ss(){
    e = meeting_objs['2656'];
    return e.short_string();
}

/*
   check_delimiter(inp), where inp is a string.
       returns char.

   checks for what we should split a string by.
   mainly we are checking for a '/' or '-' character

   Maybe there is a js function for this. doing 'a' in "abcd" does not work.
 */
function check_delimiter(inp){
    for(var i =0; i<inp.length; i++){
	if(inp[i] == '/'){
	    return '/';
	}
	else if(inp[i] == '-'){
	    return '-';
	}
    }
    return ' ';

}

/*
   upperCaseWords(inp), where inp is a string.
       returns string

   turns the first letter of each word in a string to uppercase
   a word is something considered be something defined by the function
   check_delimiter(). ( '/' , '-' , ' ' )
*/
function upperCaseWords(inp){
    var newStr = "";
    var split = inp.split(check_delimiter(inp));

	for(i=0; i<split.length; i++){
		newStr = newStr+split[i][0].toUpperCase();
		newStr = newStr+split[i].slice(1,split[i].length);

		if(i+1 < split.length){ // so we don't get a extra space
			newStr = newStr+" ";
		}
    }

	return newStr;

}

var daysofweek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

// ScheduledSession is DJANGO name for this object, but needs to be renamed.
// It represents a TimeSlot that can be assigned in this schedule.
//   { "scheduledsession_id": "{{s.id}}",
//     "empty": "{{s.empty_str}}",
//     "timeslot_id":"{{s.timeslot.id}}",
//     "session_id" :"{{s.session.id}}",
//     "room"       :"{{s.timeslot.location|slugify}}",
//     "time"       :"{{s.timeslot.time|date:'Hi' }}",
//     "date"       :"{{s.timeslot.time|date:'Y-m-d'}}",
//     "domid"      :"{{s.timeslot.js_identifier}}"}

function ScheduledSlot(){
}

ScheduledSlot.prototype.initialize = function(json) {
    for(var key in json) {
	this[key]=json[key];
    }

    /* this needs to be an object */
    this.column_class=[this.room+"_"+this.date+"_"+this.time,
                       ".agenda-column-"+this.date+"-"+this.time];

    var d = new Date(this.date);
    var t = d.getUTCDay();
    if(this.room == "Unassigned"){
	this.short_string = "Unassigned";
    }
    else{
	this.short_string = daysofweek[t] + ", "+ this.time + ", " + upperCaseWords(this.room);
    }
    if(!this.domid) {
    	this.domid = json_to_id(this);
        //console.log("gen "+timeslot_id+" is domid: "+this.domid);
    }
    //console.log("extend "+this.domid+" with "+JSON.stringify(this));

    // the key so two sessions in the same timeslot
    if(slot_status[this.domid] == null) {
	slot_status[this.domid]=[];
    }
    slot_status[this.domid].push(this);
};

ScheduledSlot.prototype.session = function() {
    if(this.session_id != undefined) {
	return meeting_objs[this.session_id];
    } else {
	return undefined;
    }
};

function make_ss(json) {
    var ss = new ScheduledSlot();
    ss.initialize(json);
}


// SESSION OBJECTS
// really session_obj.
function Session() {
    this.constraints = {};
    this.last_timeslot_id = null;
    this.slot_status_key = null;
    this.href       = false;
    this.group_obj  = undefined;
}

function event_obj(title, description, session_id, owner, group_id, area,duration) {
    session = new Session();

    // this.slug = slug;
    session.title = title;
    session.description = description;
    session.session_id = session_id;
    session.owner = owner;
    session.area  = area;
    session.group_id = group_id;
    session.loaded = false;
    session.href       = meeting_base_url+'/session/'+session_id+".json";
    session.group_href = site_base_url+'/group/'+title+".json";
    session.duration = duration;
    return session;
};


// augument to jQuery.getJSON( url, [data], [callback] )
Session.prototype.load_session_obj = function(andthen, arg) {
    if(!this.loaded) {
	start_spin();
	var oXMLHttpRequest = XMLHttpGetRequest(this.href, true);
	var session = this; // because below, this==XMLHTTPRequest
	oXMLHttpRequest.onreadystatechange = function() {
	    if (this.readyState == XMLHttpRequest.DONE) {
		try{
		    last_json_txt = this.responseText;
		    session_obj   = JSON.parse(this.responseText);
		    last_json_reply = session_obj;
		    $.extend(session, session_obj);
		    session.loaded = true;
		    if(andthen != undefined) {
			andthen(session, true, arg);
		    }
		    stop_spin();
		}
		catch(exception){
		    console.log("exception: "+exception);
		    if(andthen != undefined) {
			andthen(session, false, arg);
		    }
		}
	    }
	};
	oXMLHttpRequest.send();
    } else {
	if(andthen != undefined) {
	    andthen(this, true, arg);
	}
    }
};

function andthen_alert(object, result, arg) {
    alert("result: "+result+" on obj: "+object);
};

Session.prototype.generate_info_table = function(ss) {
    $("#info_grp").html(name_select_html);
    $("#info_name").html(this.description);
    $("#info_area").html("<span class='"+this.area.toUpperCase()+"-scheme'>"+this.area+"</span>");
    $("#info_duration").html(this.requested_duration);

    $("#info_location").html(generate_select_box()+"<button id='info_location_set'>set</button>");

    // XXX we use *GLOBAL* current_timeslot rather than ss.timeslot_id!!!
    // when it's coming from the bucket list, the ss.timeslot_id will be null and thus not pick a value. here we put the logic.
    // if(ss.timeslot_id == null){
	$("#info_name_select").val(ss.session_id);
//    }
    // else{
    // 	$("#info_name_select").val(ss.timeslot_id);
    //	$("#info_name_select").val($("#info_name_select_option_"+current_timeslot).val());
    // }

    //var temp_1 = $("#info_name_select_option_"+current_timeslot).val();
    $("#info_name_select_option_"+ss.scheduledsession_id).css('background-color',highlight);

    if(ss.timeslot_id == null){
	$("#info_location_select").val(meeting_objs[ss.scheduledsession_id]);
    }else{
	$("#info_location_select").val(ss.timeslot_id); // ***
    }
    $("#info_location_select").val($("#info_location_select_option_"+ss.timeslot_id).val());

    $("#"+ss.timeslot_id).css('background-color',highlight);

    listeners();

    $("#info_responsible").html(this.responsible_ad);
    $("#info_requestedby").html(this.requested_by +" ("+this.requested_time+")");
};


Session.prototype.group = function(andthen) {
    if(this.group_obj == undefined) {
	this.group_obj = find_group_by_href(this.group_href);
    }
    return this.group_obj;
};

function load_all_groups() {
    for(key in meeting_objs) {
        session = meeting_objs[key];
        // load the group object
        group = session.group(null);
        group.add_session(session);
        log("group: ", group, "has session: ", session.session_id);
    }
}

var __DEBUG_THIS_SLOT;
Session.prototype.retrieve_constraints_by_session = function(andthen, success) {
    __DEBUG_THIS_SLOT = this;
    if("constraints" in this && "conflict" in this.constraints) {
	/* everything is good, call continuation function */
	andthen(this);
    } else {
       var session_obj = this;
       var href = meeting_base_url+'/session/'+session_obj.session_id+"/constraints.json";
       $.getJSON( href, "", function(constraint_list) {
                      fill_in_constraints(session_obj, true,  constraint_list, andthen);
       }).done(success);
    }
};


Session.prototype.retrieve_contraint = function(){
    var session_obj = this;
    var href = meeting_base_url+'/session/'+session_obj.session_id+"/constraints.json";
    $.getJSON( href, "", function(constraint_list) {
//	console.log(constraint_list);
	andthen();
	// fill_in_constraints(session_obj, true,  constraint_list, andthen);
    });

}







// GROUP OBJECTS
function Group() {}
Group.prototype.load_group_obj = function(andthen) {
    //console.log("group ",this.href);
    var group_obj = this;

    if(!this.loaded) {
        this.loading = true;
        $.getJSON( this.href, "", function(newobj) {
                       if(newobj) {
                           $.extend(group_obj, newobj);
                           group_obj.loaded = true;
                       }
                       group_obj.loading = false;
                       andthen(group_obj);
               });
    } else {
        andthen(group_obj);
    }
};

Group.prototype.add_session = function(session) {
    if(this.all_sessions == undefined) {
        this.all_sessions = [];
    }
    this.all_sessions.push(session);
};
Group.prototype.add_column_class = function(column_class) {
    if(this.column_class == undefined) {
	this.column_class = [];
    }
    this.column_class.push(column_class);
};

function find_group_by_href(href) {
    if(group_objs[href] == undefined) {
	group_objs[href]=new Group();
	g = group_objs[href];
        g.loaded = false;
        g.loading= false;
    }
    g = group_objs[href];
    if(!g.loaded) {
        g.href = href;
	g.load_group_obj(function(obj) {});
    }
    return g;
}

// Constraint Objects
function Constraint() {
}

var conflict_classes = {};

function clear_conflict_classes() {
    $("#cb_conflict1").prop('checked',false);
    $("#cb_conflict2").prop('checked',false);
    $("#cb_conflict3").prop('checked',false);
    $.each(conflict_classes, function(key) {
	       constraint = conflict_classes[key];
	       constraint.clear_conflict_view();
	   });
    conflict_classes = {};
}
function find_conflict(domid) {
    return conflict_classes[domid];
}

Constraint.prototype.column_class = function() {
    return this.othergroup.column_class;
};

// red is arbitrary here... There should be multiple shades of red for
// multiple types of conflicts.



var __CONSTRAINT_DEBUG = null;
Constraint.prototype.show_conflict_view = function() {
    classes=this.column_class()
    //console.log("show_conflict_view", this);
    __CONSTRAINT_DEBUG = this;
//    console.log("viewing", this.thisgroup.href);

    for(ccn in classes) {
	var cc = classes[ccn];

        /* this extracts the day from this structure */
	var th_time = ".day_"+cc[1].substr(15);
//        console.log("299", th_time);
	$(th_time).addClass("show_conflict_view_highlight");
    }

//    console.log("make box", this.thisgroup.href);
    sessions = this.othergroup.all_sessions
    if(sessions) {
      $.each(sessions, function(key) {
  //             console.log("2 make box", key);
               var nid = "#session_"+this.session_id;
//               console.log("279", this.session_id, nid);
               $(nid).addClass("show_conflict_specific_box");
           });
    }
//    console.log("viewed", this.thisgroup.href);
};

Constraint.prototype.clear_conflict_view = function() {
    classes=this.column_class()
    //console.log("hiding", this.thisgroup.href);
    for(ccn in classes) {
	var cc = classes[ccn];
	var th_time = ".day_"+cc[1].substr(15);
//        console.log("259", th_time);
	$(th_time).removeClass("show_conflict_view_highlight"); //css('background-color',"red");
    }

  //  console.log("boxes for", this.thisgroup.href);
    sessions = this.othergroup.all_sessions
    if(sessions) {
      $.each(sessions, function(key) {
               var nid = "#session_"+this.session_id;
//               console.log("269", this.session_id, nid);
               $(nid).removeClass("show_conflict_specific_box");
           });
    }
//    console.log("hid", this.thisgroup.href);
};


Constraint.prototype.build_conflict_view = function() {
    var bothways = "&nbsp;&nbsp;&nbsp;";
    if(this.bothways) {
	bothways=" &lt;-&gt;";
    }
    //this.checked="checked";

    var checkbox_id = "conflict_"+this.dom_id;
    conflict_classes[checkbox_id] = this;
    return "<div class='conflict conflict-"+this.conflict_type+"' id='"+this.dom_id+
           "'><input class='conflict_checkboxes' type='checkbox' id='"+checkbox_id+
           "' value='"+this.checked+"'>"+this.othergroup_name+bothways+"</div>";

};

Constraint.prototype.build_othername = function() {
    this.othergroup_name = this.othergroup.acronym;
};


Constraint.prototype.conflict_view = function() {
    this.dom_id = "constraint_"+this.constraint_id;

    var theconstraint = this;
    if(!this.othergroup.loaded) {

        this.othergroup_name = "...";
        this.othergroup.load_group_obj(function (obj) {
                                           theconstraint.othergroup = obj;
                                           theconstraint.build_othername();
                                           $("#"+theconstraint.dom_id).html(theconstraint.build_conflict_view());
                                       });
    } else {
        this.build_othername();
    }

    return this.build_conflict_view();
};


// SESSION CONFLICT OBJECTS
// take an object and add attributes so that it becomes a session_conflict_obj.
Session.prototype.add_constraint_obj = function(obj) {
    // turn this into a Constraint object
    //console.log("session: ",JSON.stringify(this));
    //console.log("add_constraint: ",JSON.stringify(obj));

    obj2 = new Constraint();
    $.extend(obj2, obj);

    obj = obj2;
    obj.session   = this;

    var ogroupname;
    if(obj.source == this.group_href) {
        obj.thisgroup  = this.group();
        obj.othergroup = find_group_by_href(obj.target);
	ogroupname = obj.target;
    } else {
        obj.thisgroup  = this.group();
        obj.othergroup = find_group_by_href(obj.source);
	ogroupname = obj.source;
    }

    var listname = obj.name;
    obj.conflict_type = listname;
    if(this.constraints[listname]==undefined) {
	this.constraints[listname]={};
    }

    if(this.constraints[listname][ogroupname]) {
	this.constraints[listname][ogroupname].bothways = true;
    } else {
	this.constraints[listname][ogroupname]=obj;
    }
};

function split_list_at(things, keys, place) {
    var half1 = [];
    var half2 = [];
    var len = keys.length;
    var i=0;
    for(i=0; i<place; i++) {
	var key  = keys[i];
	half1[i] = things[key];
    }
    for(;i<len; i++) {
	var key  = keys[i];
	half2[i-place] = things[key];
    }
    return [half1, half2];
}

function constraint_compare(a, b)
{
    if(a==undefined) {
	return -1;
    }
    if(b==undefined) {
	return 1;
    }
    return (a.othergroup.href > b.othergroup.href ? 1 : -1);
}

function split_constraint_list_at(things, place) {
    var keys = Object.keys(things);
    var keys1 = keys.sort(function(a,b) {
				     return constraint_compare(things[a],things[b]);
				 });
    var sorted_conflicts = split_list_at(things, keys1, place);
    return sorted_conflicts;
}

// this sorts the constraints into two columns such that the number of rows
// is half of the longest amount.
Session.prototype.sort_constraints = function() {
    // find longest amount
    var big = 0;
    if("conflicts" in this.constraints) {
	big = Object.keys(this.constraints.conflict).length;
    }

    if("conflic2" in this.constraints) {
	var c2 = Object.keys(this.constraints.conflic2).length;
	if(c2 > big) {
	    big = c2;
	}
    }

    if("conflic3" in this.constraints) {
	var c3 = Object.keys(this.constraints.conflic3).length;
	if(c3 > big) {
	    big = c3;
	}
    }

    this.conflict_half_count = Math.floor((big+1)/2);
    var half = this.conflict_half_count;

    this.conflicts = [];
    this.conflicts[1]=[[],[]]
    this.conflicts[2]=[[],[]]
    this.conflicts[3]=[[],[]]

    if("conflict" in this.constraints) {
	var list1 = this.constraints.conflict;
	this.conflicts[1] = split_constraint_list_at(list1, half);
    }

    if("conflic2" in this.constraints) {
	var sort2 = this.constraints.conflic2;
	this.conflicts[2] = split_constraint_list_at(sort2, half);
    }

    if("conflic3" in this.constraints) {
	var sort3 = this.constraints.conflic3;
	this.conflicts[3] = split_constraint_list_at(sort3, half);
    }

};


/*
 * Local Variables:
 * c-basic-offset:4
 * End:
 */

