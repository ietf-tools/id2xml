// globals needed for tests cases.
var agenda_globals;
function reset_globals() {
    // hack to reach in and manipulate global specifically.
    window.agenda_globals = new AgendaGlobals();
}

function three_by_eight_grid() {
    var rooms = ["apple", "orange", "grape", "pineapple",
                 "tomato","squash", "raisin","cucumber" ];
    var times = [
        {"time":"0900", "date":"2013-12-02"},
        {"time":"1300", "date":"2013-12-02"},
        {"time":"0900", "date":"2013-12-03"}
    ];
    var slots = [{}];
    var slotid= 1;
    for(var roomkey in rooms) {
        var room = rooms[roomkey];
        for(var timekey in times) {
            var time = times[timekey];
            //console.log("data", room, time.date, time.time);
            slot = make_timeslot({"timeslot_id": slotid,
                                  "room" : room,
                                  "roomtype" : "session",
                                  "date" : time.date,
                                  "time" : time.time,
                                  "domid": "room" + roomkey + "_" + time.date + "_" + time.time
                                 });
            slots[slotid] = slot;
            slotid += 1;
        }
    }
    return slots;
}

function make_6_sessions() {
    monarchs = ["henry", "george", "richard", "victoria", "william", "elizabeth"];
    $.each(monarchs, function(index) {
        monarch = monarchs[index];
        console.log("monarch", monarch);
        var group = create_group_by_href("http://localhost:8000/group/"+monarch+".json");
        group.name = monarch;
        group.group_id = 1
    });

    var sessions = {};
    var sessionid = 1;
    $.each(monarchs, function(index) {
        monarch = monarchs[index];
        //console.log("session id", sessionid);
        sessions[monarch] =
            session_obj({"title":      monarch,
                         "session_id": sessionid,
                         "duration":   "1.0",
                         "area" :      "TSV",
                         "group_href": "http://localhost:8000/group/"+monarch+".json"
                        });
        sessionid += 1;
    });
    return sessions;
}

function place_6_sessions(slots, sessions) {
    var ss_id = 1;
    make_ss({"scheduledsession_id": ss_id,
             "timeslot_id":         slots[3].timeslot_id,
             "session_id":          sessions["henry"].session_id});
    ss_id += 1;
    make_ss({"scheduledsession_id": ss_id,
             "timeslot_id":         slots[20].timeslot_id,
             "session_id":          sessions["george"].session_id});
    ss_id += 1;
    make_ss({"scheduledsession_id": ss_id,
             "timeslot_id":         slots[4].timeslot_id,
             "session_id":          sessions["richard"].session_id});
    ss_id += 1;
    make_ss({"scheduledsession_id": ss_id,
             "timeslot_id":         slots[9].timeslot_id,
             "session_id":          sessions["victoria"].session_id});
    ss_id += 1;
    make_ss({"scheduledsession_id": ss_id,
             "timeslot_id":         slots[14].timeslot_id,
             "session_id":          sessions["william"].session_id});
    // last session is unscheduled.
}

function conflict_4_sessions(sessions) {
    // fill in session constraints

    $.each(sessions, function(index) {
        var session = sessions[index];

        var deferred = $.Deferred();
        session.constraints_promise = deferred;
        deferred.resolve({});
    });

    sessions["henry"].fill_in_constraints([
        {    "constraint_id": 21046, 
             "href": "http://localhost:8000/meeting/83/constraint/21046.json", 
             "meeting_href": "http://localhost:8000/meeting/83.json", 
             "name": "conflict", 
             "source_href": "http://localhost:8000/group/henry.json", 
             "target_href": "http://localhost:8000/group/george.json"
        },
        {    "constraint_id": 21047, 
             "href": "http://localhost:8000/meeting/83/constraint/21047.json", 
             "meeting_href": "http://localhost:8000/meeting/83.json", 
             "name": "conflic2", 
             "source_href": "http://localhost:8000/group/henry.json", 
             "target_href": "http://localhost:8000/group/richard.json"
        }]);
    find_and_populate_conflicts(sessions["henry"]);
}


function full_83_setup() {
    reset_globals();
    var ts_promise      = load_timeslots("/meeting/83/timeslots.json");
    var session_promise = load_sessions("/meeting/83/sessions.json");
    var ss_promise      = load_scheduledsessions(ts_promise, session_promise, "/meeting/83/schedule/mtg_83/sessions.json")
    return ss_promise;
}

