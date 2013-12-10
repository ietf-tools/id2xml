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

asyncTest("Load ScheduledSlot (ticket 1210)", function() {
    expect( 1 );     // expect one assertion.

    var ss_promise = full_83_setup();
    ss_promise.done(function() {
        equal(Object.keys(agenda_globals.slot_objs).length, 150, "150 scheduled sessions loaded");
        start();
    });
});

asyncTest( "move a session using the API (ticket 1211)", function() {
    expect(4);

    var ss_promise = full_83_setup();
    ss_promise.done(function() {
        equal(Object.keys(agenda_globals.slot_objs).length, 150, "150 scheduled sessions loaded");

        // now move a session.. like selenium test, move forced from Monday to Friday:
        // monday_room_253  = is #room208_2012-03-26_1510
        // friday_room_252A = is #room209_2012-03-30_1230

        var forces_list  = agenda_globals.sessions_objs["forces"];
        var forces       = forces_list[0];
        var from_slot_id = "room208_2012-03-26_1510";
        var from_slot    = agenda_globals.timeslot_bydomid[from_slot_id];
        var to_slot_id   = "room209_2012-03-30_1230";
        var to_slot      = agenda_globals.timeslot_bydomid[to_slot_id];
        var ui           = mock_ui_draggable();
        var dom_obj      = "#" + to_slot_id;

        /* current situation was tested in above test, so go ahead */
        /* and move "richard" to another slot  */

        var move_promise = move_slot({"session": forces,
                                      "to_slot_id":  to_slot_id,
                                      "to_slot":     to_slot,
                                      "from_slot_id":from_slot_id,
                                      "from_slot":   [from_slot],
                                      "bucket_list": false,
                                      "ui":          ui,
                                      "dom_obj":     dom_obj,
                                      "force":       true});
        notEqual(move_promise, undefined);

        if(move_promise != undefined) {
            // now we need to check that it is all been done.
            move_promise.done(function() {
                // see that the placed is right.
                equal(forces.slot.domid, to_slot_id);

                // now move the item back again.

                var return_promise = move_slot({"session": forces,
                                                "to_slot_id":  from_slot_id,
                                                "to_slot":     from_slot,
                                                "from_slot_id":to_slot_id,
                                                "from_slot":   [to_slot],
                                                "bucket_list": false,
                                                "ui":          ui,
                                                "dom_obj":     dom_obj,
                                                "force":       true});

                return_promise.done(function() {
                    // see that the placed is right.
                    equal(forces.slot.domid, from_slot_id);
                    start();
                });
            });
        } else {
            // it is not legitimate to wind up here, but it does
            // keep the test cases from hanging.
            start();
        }
    });
});

test( "3x8 grid create (ticket 1212 - part 1)", function() {
    expect(0);        // just make sure things run without error
    reset_globals();

    t_slots = three_by_eight_grid();
    t_sessions = make_6_sessions();
    place_6_sessions(t_slots, t_sessions);
});

test( "calculate conflict columns for henry (ticket 1212 - part 2)", function() {
    expect(10);

    scheduledsession_post_href = "/test/agenda_ui.html";

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

test( "re-calculate conflict columns for henry (ticket 1213)", function() {
    expect(5);
    reset_globals();

    scheduledsession_post_href = "/test/agenda_ui.html";
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

