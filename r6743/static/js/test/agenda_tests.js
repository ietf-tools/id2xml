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

asyncTest("Load ScheduledSlot", function() {
    expect( 1 );     // expect one assertion.

    var ss_promise = full_83_setup();
    ss_promise.done(function() {
        equal(Object.keys(agenda_globals.slot_objs).length, 150, "150 scheduled sessions loaded");
        start();
    });
});

test( "3x8 grid create", function() {
    expect(0);        // just make sure things run without error
    reset_globals();

    t_slots = three_by_eight_grid();
    t_sessions = make_6_sessions();
    place_6_sessions(t_slots, t_sessions);
});

test( "calculate conflict columns for henry", function() {
    expect(10);

    var henry = henry_setup();
    equal(henry.session_id, 1);
    
    equal(henry.column_class_list.length, 1);
    equal(henry.column_class_list[0].room, "apple");
    equal(henry.column_class_list[0].time, "0900");
    equal(henry.column_class_list[0].date, "2013-12-03");

    equal(henry.conflicts.length, 2);

    var conflict0 = henry.conflicts[0];
    equal(conflict0.conflict_groupP(), true);

    var classes = conflict0.column_class_list();
    var cc00 = classes[0];
    equal(cc00.th_tag, ".day_2013-12-02-1300");

    var conflict1 = henry.conflicts[1];
    equal(conflict1.conflict_groupP(), true);

    var classes = conflict1.column_class_list();
    var cc10 = classes[0];
    equal(cc10.th_tag, ".day_2013-12-02-1300");
});

test( "re-calculate conflict columns for henry", function() {
    expect(5);
    reset_globals();

    agenda_globals.__debug_session_move = true;

    var henry = henry_setup();
    equal(henry.session_id, 1);

    var richard = richard_move();
    var conflict0 = henry.conflicts[0];
    equal(conflict0.conflict_groupP(), true);

    var classes = conflict0.column_class_list();
    var cc00 = classes[0];
    equal(cc00.th_tag, ".day_2013-12-02-1300");

    var conflict1 = henry.conflicts[1];
    equal(conflict1.conflict_groupP(), true);

    var classes = conflict1.column_class_list();
    var cc10 = classes[0];
    equal(cc10.th_tag, ".day_2013-12-02-0900");
});

