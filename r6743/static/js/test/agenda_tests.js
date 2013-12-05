// globals needed for tests cases.
var agenda_globals;
function reset_globals() {
    // hack to reach in and manipulate global specifically.
    window.agenda_globals = new AgendaGlobals();
}

function three_by_eight_grid() {
    var rooms = ["apple", "orange", "grape", "pineapple",
             "tomato","squash", "raisin","cucumber" ]
    var times = [{"time":"0900", "date":"2013-12-02"},
             {"time":"1300", "date":"2013-12-02"},
             {"time":"0900", "date":"2013-12-03"}]
    var slots = [{}];
    var slotid= 1;
    for(var room in rooms) {
        for(var time in times) {
            slot = make_timeslot({"timeslot_id": slotid,
                                  "room" : room,
                                  "date" : time.date,
                                  "time" : time.time,
                                  "domid": "room" + slotid + "_" + time.date + "_" + time.time
                                 });
            slots[slotid] = slot;
            slotid += 1;
        }
    }
    return slots;
}

function make_6_sessions() {
    var monarchs = ["henry", "george", "richard", "victoria", "william", "elizabeth"];
    for(var monarch in monarchs) {
        var group = create_group_by_href("http://localhost:8000/group/"+monarch+".json");
        group.name = monarch;
        group.group_id = 1
    }

    var sessions = [{}];
    var sessionid = 1;
    for(var monarch in monarchs) {
        sessions[sessionid] =
            session_obj({"title": monarch,
                         "session_id": sessionid,
                         "duration":   3600,
                         "group_href": "http://localhost:8000/group/"+monarch+".json"
                        });
        sessionid += 1;
    }
    return sessions;
}

function place_6_sessions(slots, sessions) {
    var ss_id = 1;
    make_ss({"scheduledsession_id": ss_id,
             "timeslot_id":         slots[3].timeslot_id,
             "session_id":          sessions[1].session_id});
    make_ss({"scheduledsession_id": ss_id,
             "timeslot_id":         slots[20].timeslot_id,
             "session_id":          sessions[2].session_id});
    make_ss({"scheduledsession_id": ss_id,
             "timeslot_id":         slots[4].timeslot_id,
             "session_id":          sessions[3].session_id});
    make_ss({"scheduledsession_id": ss_id,
             "timeslot_id":         slots[9].timeslot_id,
             "session_id":          sessions[4].session_id});
    make_ss({"scheduledsession_id": ss_id,
             "timeslot_id":         slots[14].timeslot_id,
             "session_id":          sessions[5].session_id});
    // last session is unscheduled.
}



test( "hello test", function() {
  ok( 1 == "1", "Passed!" );
});

test( "TimeSlot Create test", function() {
    reset_globals();
    var nts = make_timeslot({"timeslot_id":"123",
                             "room"       :"Regency A",
                             "time"       :"0900",
                             "date"       :"2013-11-04",
                             "domid"      :"regencya_2013-11-04_0900"});
    equal(nts.slot_title(), "id#123 dom:regencya_2013-11-04_0900", "slot_title correct");
});

asyncTest("Load Timeslots", function() {
    reset_globals();
    expect( 1 );     // expect one assertion.

    var ts_promise = load_timeslots("/meeting/83/timeslots.json");
    ts_promise.done(function() {
        equal(Object.keys(agenda_globals.timeslot_byid).length, 179, "179 timeslots loaded");
        start();
    });
});

asyncTest("Load Sessions", function() {
    reset_globals();
    expect( 1 );     // expect one assertion.

    var session_promise = load_sessions("/meeting/83/sessions.json");
    session_promise.done(function() {
        equal(Object.keys(agenda_globals.meeting_objs).length, 145, "145 sessions loaded");
        start();
    });
});

function full_83_setup() {
    reset_globals();
    var ts_promise      = load_timeslots("/meeting/83/timeslots.json");
    var session_promise = load_sessions("/meeting/83/sessions.json");
    var ss_promise      = load_scheduledsessions(ts_promise, session_promise, "/meeting/83/schedule/mtg_83/sessions.json")
    return ss_promise;
}

asyncTest("Load ScheduledSlot", function() {
    expect( 1 );     // expect one assertion.

    var ss_promise = full_83_setup();
    ss_promise.done(function() {
        equal(Object.keys(agenda_globals.slot_objs).length, 150, "150 scheduled sessions loaded");
        start();
    });
});

test( "3x8 grid create", function() {
    reset_globals();

    t_slots = three_by_eight_grid();
    t_sessions = make_6_sessions();
    place_6_sessions(t_slots, t_sessions);
});

