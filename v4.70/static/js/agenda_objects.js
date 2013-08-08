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

var all_conflicts = {};

function show_all_conflicts(){
    //console.log("all conflicts");
    $.each(all_conflicts, function(key) {
        conflict = all_conflicts[key];
        //console.log("session:", conflict.title, conflict.session_id);
        $("#session_" + conflict.session_id).addClass("actual_conflict");
    });
}

// not really used anymore
function hide_all_conflicts(){
    $.each(all_conflicts, function(key) {
        conflict = all_conflicts[key];
        $("#" + conflict.session_id).removeClass("actual_conflict");
    });
}

var CONFLICT_LOAD_COUNT = 0;
function increment_conflict_load_count() {
    CONFLICT_LOAD_COUNT++;
    //console.log(CONFLICT_LOAD_COUNT+"/"+meeting_objs_length);
}

function get_all_conflicts(){
    //console.log("get_all_conflicts()");
    for(s in meeting_objs){
       try {
           meeting_objs[s].retrieve_constraints_by_session(find_and_populate_conflicts,
                                                            increment_conflict_load_count);
       }
       catch(err){
          console.log(err);
       }

    }
}

function calculate_real_conflict(conflict, vertical_location, room_tag, session_obj) {
    //console.log("  conflict check:", conflict.othergroup.acronym, "me:", vertical_location);

    var osessions = conflict.othergroup.all_sessions;
    //console.log("ogroup: ", conflict.othergroup.href, "me: ", session_obj.group_obj.href);
    if(conflict.othergroup === session_obj.group_obj) {
        osessions = conflict.thisgroup.all_sessions;
    }
    if(osessions != null) {
        $.each(osessions, function(index) {
            osession = osessions[index];
            var value = osession.column_class;
            if(value != undefined) {
                //console.log("    vs: ",index, "session_id:",osession.session_id," at: ",value.column_tag);
                if(value.column_tag == vertical_location &&
                   value.room_tag   != room_tag) {
                    console.log("real conflict:",session_obj.title," with: ",conflict.othergroup.acronym," #session_",session_obj.session_id);
                    // there is a conflict!
                    __DEBUG_SHOW_CONSTRAINT = $("#"+value[0]).children()[0];
                    all_conflicts[session_obj.session_id] = session_obj;
                }
            }
        });
    }
}

var __DEBUG_SHOW_CONSTRAINT = null;
function find_and_populate_conflicts(session_obj) {
    //console.log("populating conflict:", session_obj.title);

    var vertical_location = null;
    var room_tag = null;
    if(session_obj.column_class != null) {
        vertical_location = session_obj.column_class.column_tag;
        room_tag = session_obj.column_class.room_tag;
    }

    if(session_obj.constraints.conflict != null){
        $.each(session_obj.constraints.conflict, function(i){
            var conflict = session_obj.constraints.conflict[i];
            calculate_real_conflict(conflict, vertical_location, room_tag, session_obj);
        });
    }
    if(session_obj.constraints.conflic2 != null){
        $.each(session_obj.constraints.conflic2, function(i){
            var conflict = session_obj.constraints.conflic2[i];
            calculate_real_conflict(conflict, vertical_location, room_tag, session_obj);
        });
    }
    if(session_obj.constraints.conflic3 != null){
        $.each(session_obj.constraints.conflic3, function(i){
            var conflict = session_obj.constraints.conflic3[i];
            calculate_real_conflict(conflict, vertical_location, room_tag, session_obj);
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

// ColumnClass is an object that knows about columns, but also about
// columns + room (so it can identify a single slot, or a column of them)
function ColumnClass(room,date,time) {
    this.room = room;
    this.date = date;
    this.time = time;
    this.room_tag   = this.room+"_"+this.date+"_"+this.time;
    this.th_time    = this.date+"-"+this.time;
    this.column_tag = ".agenda-column-"+this.th_time;
};


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
    this.column_class=new ColumnClass(this.room, this.date, this.time);

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
    this.constraint_load_andthen_list = [];
    this.constraints_loaded = false;
    this.last_timeslot_id = null;
    this.slot_status_key = null;
    this.href       = false;
    this.group_obj  = undefined;
    this.column_class = undefined;     //column_class will be filled by in load_events
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

Session.prototype.selectit = function() {
    clear_all_selections();
    // mark self as selected
    $("." + this.title).addClass("same_group");
    $("#session_"+session_id).removeClass("save_group");
    $("#session_"+session_id).addClass("selected_group");
};
Session.prototype.unselectit = function() {
    clear_all_selections();
};



function andthen_alert(object, result, arg) {
    alert("result: "+result+" on obj: "+object);
};

Session.prototype.generate_info_table = function(ss) {
    $("#info_grp").html(name_select_html);
    $("#info_name_select").val($("#info_name_select_option_"+this.session_id).val());
    $("#info_name").html(this.description);
    $("#info_area").html("<span class='"+this.area.toUpperCase()+"-scheme'>"+this.area+"</span>");
    $("#info_duration").html(this.requested_duration);

    if(!read_only) {
        $("#info_location").html(generate_select_box()+"<button id='info_location_set'>set</button>");
    }

    this.selectit();

    if(ss.timeslot_id == null){
       $("#info_location_select").val(meeting_objs[ss.scheduledsession_id]);
    }else{
       $("#info_location_select").val(ss.timeslot_id); // ***
    }
    $("#info_location_select").val($("#info_location_select_option_"+ss.timeslot_id).val());

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
    //console.log("4 retrieve loaded:", this.constraints_loaded, "loading:", this.constraints_loading);
    if(this.constraints_loaded) {
       /* everything is good, call continuation function */
       andthen(this);
    } else {
        this.constraint_load_andthen_list.push(andthen);
        if(this.constraints_loading) {
            return;
        }

        this.constraints_loading = true;
        var session_obj = this;
        var href = meeting_base_url+'/session/'+session_obj.session_id+"/constraints.json";
        $.getJSON( href, "", function(constraint_list) {
            session_obj.fill_in_constraints(constraint_list);
            session_obj.constraints_loaded  = true;
            session_obj.constraints_loading = false;
        }).done(success);
    }
};

Session.prototype.fill_in_constraints = function(constraint_list) {
    if(constraint_list['error']) {
        console.log("failed to get constraints for session_id: "+this.session_id, constraint_list['error']);
        return false;
    }

    var session_obj = this;
    $.each(constraint_list, function(key){
       thing = constraint_list[key];
       session_obj.add_constraint_obj(thing);
    });
    this.sort_constraints();

    $.each(this.constraint_load_andthen_list, function(index, andthen) {
        andthen(session_obj);
    });
    this.constraint_load_andthen_list = [];
};

// GROUP OBJECTS
function Group() {
    this.andthen_list = [];
    this.all_sessions = [];
}

Group.prototype.loaded_andthen = function() {
    $.each(this.andthen_list, function(index, andthen) {
        andthen(this);
    });
    this.andthen_list = [];
};
Group.prototype.load_group_obj = function(andthen) {
    //console.log("group ",this.href);
    var group_obj = this;

    if(!this.loaded && !this.loading) {
        this.loading = true;
        this.andthen_list.push(andthen);
        $.getJSON( this.href, "", function(newobj) {
            if(newobj) {
                $.extend(group_obj, newobj);
                group_obj.loaded = true;
            }
            group_obj.loading = false;
            group_obj.loaded_andthen();
        });
    } else {
        if(!this.loaded) {
            // queue this continuation for later.
            this.andthen_list.push(andthen);
        } else {
            andthen(group_obj);
        }
    }
};

Group.prototype.add_session = function(session) {
    if(this.all_sessions == undefined) {
        this.all_sessions = [];
    }
    this.all_sessions.push(session);
};
Group.prototype.add_column_class = function(column_class) {
    if(this.column_class_list == undefined) {
       this.column_class_list = [];
    }
    this.column_class_list.push(column_class);
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
        //console.log("loading group href", href);
       g.load_group_obj(function(obj) {});
    }
    return g;
}

// Constraint Objects
function Constraint() {
// fields: (see ietf.meeting.models Constraint.json_dict)
//
//  -constraint_id
//  -href
//  -name
//  -person/_href
//  -source/_href
//  -target/_href
//  -meeting/_href
//
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

Constraint.prototype.column_class_list = function() {
    return this.othergroup.column_class_list;
};

// red is arbitrary here... There should be multiple shades of red for
// multiple types of conflicts.



var __CONSTRAINT_DEBUG = null;

// one can get here by having the conflict boxes enabled/disabled.
// but, when a session is selected, the conflict boxes are filled in,
// and then they are all clicked in order to highlight everything.
Constraint.prototype.show_conflict_view = function() {
    classes=this.column_class_list()
    //console.log("show_conflict_view", this);
    __CONSTRAINT_DEBUG = this;
    //console.log("viewing", this.href, this.thisgroup.href);

    // this highlights the column headings of the sessions that conflict.
    for(ccn in classes) {
       var cc = classes[ccn];   // cc is a ColumnClass now

        if(cc != undefined) {
            /* this extracts the day from this structure */
           var th_time = ".day_"+cc.th_time;
           //console.log("299", th_time);
           $(th_time).addClass("show_conflict_view_highlight");
        }
    }

    // this highlights the conflicts themselves
    //console.log("make box", this.thisgroup.href);
    sessions = this.othergroup.all_sessions
    if(sessions) {
      $.each(sessions, function(key) {
          //console.log("2 make box", key);
          var nid = "#session_"+this.session_id;
          //console.log("279", this.session_id, nid);
          $(nid).addClass("show_conflict_specific_box");
      });
    }
    //console.log("viewed", this.thisgroup.href);
};

Constraint.prototype.clear_conflict_view = function() {
    classes=this.column_class_list()
    //console.log("hiding", this.thisgroup.href);
    for(ccn in classes) {
       var cc = classes[ccn];
        if(cc != undefined) {
           var th_time = ".day_" + cc.th_time;
           $(th_time).removeClass("show_conflict_view_highlight"); //css('background-color',"red");
        }
    }

    //console.log("boxes for", this.thisgroup.href);
    sessions = this.othergroup.all_sessions
    if(sessions) {
      $.each(sessions, function(key) {
          var nid = "#session_"+this.session_id;
          //console.log("269", this.session_id, nid);
          $(nid).removeClass("show_conflict_specific_box");
      });
    }
    //console.log("hid", this.thisgroup.href);
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


var __DEBUG__OTHERGROUP;
Constraint.prototype.conflict_view = function() {
    this.dom_id = "constraint_"+this.constraint_id;

    var theconstraint = this;
    if(!this.othergroup.loaded) {

        __DEBUG__OTHERGROUP = this;
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
        obj.othergroup = find_group_by_href(obj.target_href);
       ogroupname = obj.target_href;
    } else {
        obj.thisgroup  = this.group();
        obj.othergroup = find_group_by_href(obj.source_href);
       ogroupname = obj.source_href;
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

