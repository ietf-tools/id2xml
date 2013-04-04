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
function ScheduledSlot() {}

function slot_obj(scheduledsession_id, empty, timeslot_id, session_id, room, time, date, domid) {
    ss = new ScheduledSlot();
    ss.scheduledsession_id = scheduledsession_id;
    ss.empty       = empty;
    ss.timeslot_id = timeslot_id;
    ss.session_id  = session_id;
    ss.date        = date;
    ss.time        = time;
    ss.room        = room;

    ss.column_class= ".agenda-column-"+date+"-"+time;

    var d = new Date(ss.date);
    var t = d.getUTCDay();
    //console.log("short_string "+ss.date+" gives "+t);
    if(ss.room == "Unassigned"){
	ss.short_string = "Unassigned";
    }
    else{
	ss.short_string = daysofweek[t] + ", "+ ss.time + ", " + upperCaseWords(ss.room);
    }
    if(domid) {
	ss.domid = domid;
    } else {
	ss.domid = json_to_id(this);
	console.log("gen "+timeslot_id+" is domid: "+ss.domid);
    }
    return ss;
}

ScheduledSlot.prototype.session = function() {
    if(this.session_id != undefined) {
	return meeting_objs[this.session_id];
    } else {
	return undefined;
    }
};


// SESSION OBJECTS
// really session_obj.
function Session() {
    this.constraints = {};
    this.last_timeslot_id = null;
    this.slot_status_key = null;
    this.href       = false;
    this.group_obj  = undefined;
}

function event_obj(title, description, session_id, owner, group_id, area) {
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
    return session;
};


// augument to jQuery.getJSON( url, [data], [callback] )
Session.prototype.load_session_obj = function(andthen, arg) {
    if(!this.loaded) {
	var oXMLHttpRequest = XMLHttpGetRequest(this.href, true);
	var session = this; // because below, this==XMLHTTPRequest
	oXMLHttpRequest.onreadystatechange = function() {
	    if (this.readyState == XMLHttpRequest.DONE) {
		try{
		    last_json_txt = this.responseText;
		    session_obj   = JSON.parse(this.responseText);
		    //console.log("parsed: "+constraint_list);
		    last_json_reply = session_obj;
		    $.extend(session, session_obj);
		    session.loaded = true;
		    if(andthen != undefined) {
			andthen(session, true, arg);
		    }
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
    $("#info_name_select").val(ss.timeslot_id);
    $("#info_name_select").val($("#info_name_select_option_"+current_timeslot).val());

    var temp_1 = $("#info_name_select_option_"+current_timeslot).val();
    $("#info_name_select_option_"+ss.scheduledsession_id).css('background-color',highlight);

    $("#info_location_select").val(ss.timeslot_id);
    //console.log("git "+"#info_location_select_option_"+this.timeslot_id);
    $("#info_location_select").val($("#info_location_select_option_"+ss.timeslot_id).val());

    $("#"+ss.timeslot_id).css('background-color',highlight);

    listeners();

    $("#info_responsible").html(this.responsible_ad);
    $("#info_requestedby").html(this.requested_by +" ("+this.requested_time+")");
};


Session.prototype.group = function(andthen) {
    if(this.group_obj == undefined) {
	console.log("finding session", this.group_href);
	this.group_obj = find_group_by_href(this.group_href);
    }
    return this.group_obj;
};

function load_all_groups() {
    $.each(meeting_objs, function(key) {
	       session = meeting_objs[key];
	       // console.log("all_groups session", session);
	       // load the group object
	       session.group();
	   });
}

Session.prototype.retrieve_constraints_by_session = function(andthen) {
    if("constraints" in this && "conflicts" in this.constraints) {
        console.log("constraints already loaded");
	/* everything is good, call continuation function */
	andthen(this);

    } else {
       var session_obj = this;

       var href = meeting_base_url+'/session/'+session_obj.session_id+"/constraints.json";
       $.getJSON( href, "", function(constraint_list) {
                      fill_in_constraints(session_obj, true,  constraint_list, andthen);
                  });
    } 
};



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
}

Group.prototype.add_column_class = function(column_class) {
    if(this.column_class == undefined) {
	this.column_class = [];
    }
    this.column_class.push(column_class);
};

function find_group_by_href(href) {
    //console.log("group href", href, group_objs[href]);
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
Constraint.prototype.show_conflict_view = function() {
    //console.log("show conflict", this.constraint_id);
    classes=this.column_class()
    for(ccn in classes) {
	cc = classes[ccn];
	//console.log("show class", cc);
	$(cc).css("background", "red");
    }
};
Constraint.prototype.clear_conflict_view = function() {
    classes=this.column_class()
    for(ccn in classes) {
	cc = classes[ccn];
	//console.log("clear class", cc);
	$(cc).css("background", "");
    }
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
        //console.log("loading group", this.othergroup);
        this.othergroup_name = "...";
        this.othergroup.load_group_obj(function (obj) {
                                           theconstraint.othergroup = obj;
                                           //console.log("updating group", theconstraint.othergroup);
                                           //console.log("for constraint", theconstraint.dom_id);
                                           theconstraint.build_othername();
                                           $("#"+theconstraint.dom_id).html(theconstraint.build_conflict_view());
                                       });
    } else {
        //console.log("used loaded group", this.othergroup);
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
	//console.log("session "+this.session_id,"target "+obj.target);
        obj.othergroup = find_group_by_href(obj.target);
	ogroupname = obj.target;
    } else {
        obj.thisgroup  = this.group();
	//console.log("session "+this.session_id,"source "+obj.source);
        obj.othergroup = find_group_by_href(obj.source);
	ogroupname = obj.source;
    }

    //console.log("ogroupname", ogroupname);
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
    console.log("things", keys);
    var keys1 = keys.sort(function(a,b) {
				     return constraint_compare(things[a],things[b]);
				 });
    console.log("sorted", keys1);
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
	console.log("conflic1", big);
    }

    if("conflic2" in this.constraints) {
	var c2 = Object.keys(this.constraints.conflic2).length;
	console.log("conflic2", c2, big);
	if(c2 > big) {
	    big = c2;
	}
    }

    if("conflic3" in this.constraints) {
	var c3 = Object.keys(this.constraints.conflic3).length;
	console.log("conflic3", c3, big);
	if(c3 > big) {
	    big = c3;
	    console.log("conflic3", big);
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

