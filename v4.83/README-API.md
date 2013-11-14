-*- markdown -*-

# IETF Datatracker Meeting Agenda API #

This documents the series of URLs that can be used to invoke various
functions.  Some just return HTML, while others can return HTML or JSON.

## /meeting/   ##
## /meeting/XX ##
## /meeting/agenda/  ##
## /meeting/agenda-utc/ ##
## /meeting/agenda/?_testiphone=1  ##
## /meeting/agenda.html  ##
## /meeting/agenda.txt ##
## /meeting/83/agenda/wlo@amsl.com/mtg:83/edit  ##
## /meeting/83/agenda/edit ##
## /meeting/83/agendas/  ##
## /meeting/83/agendas ##
## /meeting/83/timeslots/edit  ##
## /meeting/83/rooms  ##
## /meeting/83/room/206.json  ##
## /meeting/83/timeslots  ##
## /meeting/83/timeslot/2371.json  ##
## /meeting/(?P<num>\d+)/room/(?P<roomid>\d+).json$' ##
## /meeting/(?P<num>\d+)/timeslots$' ##
## /meeting/(?P<num>\d+)/timeslot/(?P<slotid>\d+).json$' ##
## /meeting/(?P<num>\d+)/agendas/(?P<schedule_name>[A-Za-z0-9-:_]+).json$' ##
## /meeting/(?P<num>\d+)/agendas$' ##
## /meeting/(?P<num>\d+)/session/(?P<sessionid>\d+).json'              ##
## /meeting/(?P<num>\d+)/session/(?P<sessionid>\d+)/constraints.json'  ##

## /meeting/(?P<meeting_num>\d+).json$'     ##

Methods supported: GET, PUT, POST.

### GET method. ###

Returns JSON description of the meeting.
<pre><code>
    {
        "agenda_href": "http://thesiteurl/meeting/83/agendas/mtg:83.json",
        "break_area": "Hall Maillot A",
        "city": "Paris",
        "country": "FR",
        "date": "2012-03-25",
        "href": "http://thesiteurl/meeting/83.json",
        "name": "83",
        "reg_area": "Hall Maillot A",
        "submission_correction_date": "2012-05-16",
        "submission_cut_off_date": "2012-04-27",
        "submission_start_date": "2011-12-26",
        "time_zone": "Europe/Paris",
        "venue_name": "",
        "venus_addr": ""
    }
</code></pre>

#### href ####

Canonical URL of this object.

#### agenda_href ####

URL for the official agenda.

#### break_area ####

What room are the breaks in.

### PUT method.

Accepts JSON or "application/x-www-form-urlencoded" dictionary.
Accepts one argument which is the name of the agenda that should become
official.  The special name "None" or an empty string will set the agenda
empty.

This call must be authenticated by a user with secretariat role, and the
agenda must be already marked public, or an HTTP 406 will be returned.

The result of this call, if successful, is the updated JSON of the meeting.

### POST method.

Identical at present to the PUT method.




### /meeting/(?P<meeting_num>\d+)/materials.html$', views.show_html_materials),
### /meeting/agenda/$',          views.agenda_html_request),
### /meeting/agenda-utc(?:.html)?$', views.html_agenda_utc),
### /meeting/agenda(?:.html)?$', views.agenda_html_request),
### /meeting/agenda/edit$', views.edit_agenda),
### /meeting/requests.html$', redirect_to, {"url": '/meeting/requests', "permanent": True}),
### /meeting/requests$', views.meeting_requests),
### /meeting/agenda.txt$', views.text_agenda),
### /meeting/agenda/agenda.ics$', views.ical_agenda),
### /meeting/agenda.ics$', views.ical_agenda),
### /meeting/agenda.csv$', views.csv_agenda),
### /meeting/agenda/week-view.html$', views.week_view),
### /meeting/week-view.html$', views.week_view),
### /meeting/(?P<num>\d+)/schedule/edit$',        views.edit_agenda),
### /meeting/(?P<num>\d+)/schedule/(?P<schedule_name>[A-Za-z0-9-:_]+)/edit$',      views.edit_agenda),
### /meeting/(?P<num>\d+)/schedule/(?P<schedule_name>[A-Za-z0-9-:_]+)/details$',   views.edit_agenda_properties),
### /meeting/(?P<num>\d+)/schedule/(?P<schedule_name>[A-Za-z0-9-:_]+)(?:.html)?/?$', views.agenda_html_request),
### /meeting/(?P<num>\d+)/agenda(?:.html)?/?$',     views.agenda_html_request),
### /meeting/(?P<num>\d+)/agenda-utc(?:.html)?/?$', views.html_agenda_utc),
### /meeting/(?P<num>\d+)/requests.html$', redirect_to, {"url": '/meeting/%(num)s/requests', "permanent": True}),
### /meeting/(?P<num>\d+)/requests$', views.meeting_requests),
### /meeting/(?P<num>\d+)/agenda.txt$', views.text_agenda),
### /meeting/(?P<num>\d+)/agenda.ics$', views.ical_agenda),
### /meeting/(?P<num>\d+)/agenda.csv$', views.csv_agenda),
### /meeting/(?P<num>\d+)/agendas/edit$',                       views.edit_agendas),
### /meeting/(?P<num>\d+)/timeslots/edit$',                     views.edit_timeslots),
### /meeting/(?P<num>\d+)/rooms$',                              ajax.timeslot_roomsurl),
### /meeting/(?P<num>\d+)/week-view.html$', views.week_view),
### /meeting/(?P<num>\d+)/agenda/week-view.html$', views.week_view),
### /meeting/(?P<num>\d+)/agenda/(?P<session>[A-Za-z0-9-]+)-drafts.pdf$', views.session_draft_pdf),
### /meeting/(?P<num>\d+)/agenda/(?P<session>[A-Za-z0-9-]+)-drafts.tgz$', views.session_draft_tarfile),
### /meeting/(?P<num>\d+)/agenda/(?P<session>[A-Za-z0-9-]+)/?$', views.session_agenda),

