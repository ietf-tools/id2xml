
// cookie functions used with permission from http://www.elated.com/articles/javascript-and-cookies/
function set_cookie ( name, value, exp_y, exp_m, exp_d, path, domain, secure )
{
    var cookie_string = name + "=" + escape ( value );

    if ( exp_y ) {
	var expires = new Date ( exp_y, exp_m, exp_d );
	cookie_string += "; expires=" + expires.toGMTString();
    }

    if ( path )
        cookie_string += "; path=" + escape ( path );

    if ( domain )
        cookie_string += "; domain=" + escape ( domain );
  
    if ( secure )
        cookie_string += "; secure";
  
    document.cookie = cookie_string;
}
function delete_cookie ( cookie_name )
{
    var cookie_date = new Date ( );  // current date & time
    cookie_date.setTime ( cookie_date.getTime() - 1 );
    document.cookie = cookie_name += "=; expires=" + cookie_date.toGMTString();
}
function get_cookie ( cookie_name )
{
    var results = document.cookie.match ( '(^|;) ?' + cookie_name + '=([^;]*)(;|$)' );

    if ( results )
	return ( unescape ( results[2] ) );
    else
	return null;
}

// set the color of a row to the proper class. optionally set the corresponding cookie.
function setcolor(id, color, skip_cookie)
{
    oneSecond = 1000;
    oneMinute = 60*oneSecond;
    oneHour   = 60*oneMinute;
    oneDay    = 24*oneHour;
    oneWeek   = 7*oneDay;
    oneMonth  = 31*oneDay;
		
    var now = new Date();
    var exp = new Date(now.getTime() + 3*oneMonth);

    var e = $(id);
    if (e) e.className = "bg" + color;
    //if (!skip_cookie) set_cookie(id, color, 2009, 8, 1);
    if (!skip_cookie) set_cookie(id, color, exp.getFullYear(), exp.getMonth(), exp.getDate(),"", ".ietf.org");
}

// return a list of all cookie name/value pairs
function get_cookie_list()
{
    var cookie = document.cookie;
    var cookies = cookie.split(';');
    var cookie_list = [];
    for (var i = 0; i < cookies.length; i++) {
	var cookie_match = cookies[i].match('(^|;) *([^=]*)=([^;]*)(;|$)');
	if (cookie_match) {
	    cookie_list.push(cookie_match[2]);
	    cookie_list.push(cookie_match[3]);
	    // alert("cookie: '" + cookie_match[2] + "'='" + cookie_match[3] + "'");
	}
    }
    return cookie_list;
}

// run through all cookies and set the colors of each row
function set_cookie_colors()
{
    var cl = get_cookie_list();
    for (var i = 0; i < cl.length; i += 2) {
        setcolor(cl[i], cl[i+1], true);
    }
    // alert(get_colortransfer_parm_string());
    var querystring = new QueryString();
    set_all_parm_colors(querystring.get("colors"));
    Element.hide('colorpallet');
}

// the current color being picked by the popup
var curid;

// pop up the pallet to let a color be picked
function pickcolor(id)
{
    curid = id;
    var colorpallet = $('colorpallet');
    if (colorpallet) {
        Element.show(colorpallet);
	Element.absolutize(colorpallet);
	Element.clonePosition(colorpallet, "p-" + id);
    }
}

// pop up the color transfer information
function showcolortransfer()
{
    var colortransfer = $('colortransfer');
    var colortransferurl = $('colortransferurl');
    if (colortransfer && colortransferurl) {
	var url = "" + window.location;
	// alert("url=" + url);
	if (url.indexOf("?")) url = url.substr(0, url.indexOf("?"));
	url += "?colors=" + get_colortransfer_parm_string();
	colortransferurl.innerHTML = "" + url;
        Element.toggle(colortransfer);
    }
}

// called by the pallet popup to set the current color
function setcurcolor(color)
{
    setcolor(curid, color);
    var colorpallet = $('colorpallet');
    if (colorpallet) {
	Element.hide(colorpallet);
    }
}

// <span id='77-mon-0900-apparea' style='padding: 2px 0 0 0;'><a href="venue/?room=california-b" title="Room map" onclick="javascript: window.open('venue/?room=california-b', 'IETF meeting rooms','scrollbars=no,toolbar=no,width=692,height=564'); return false;">California B</a>     APP   <a name="apparea"></a>apparea   <img src="/images/docs/blank.png" alt="" />&nbsp;<img src="/images/docs/blank.png" alt="" />&nbsp;<a href="http://videolab.uoregon.edu/events/ietf/ietf772.m3u" style="border: 0" title="Audio stream from California B"><img src="/images/audio.gif" alt="audio"/></a>&nbsp;<img src="/images/docs/blank.png" alt="" />&nbsp;<a href="xmpp:apparea@jabber.ietf.org?join" style="border: 0" title="apparea jabber room"><img alt="jabber" src="/images/jabber.png"/></a>&nbsp;<a href="http://jabber.ietf.org/logs/apparea" style="border: 0" title="apparea jabber logs"><img alt="jabber" src="/images/jabberlog.png"/></a>&nbsp;<img src="/images/color-palette-4x4.gif" id="p-77-mon-0900-apparea" onclick='pickcolor("77-mon-0900-apparea")' alt='color tagger' title='colour tag this line'/>&nbsp;<span title='Applications Area Open Meeting'>Applications Area Open Meeting</span>       </span>

function get_colortransfer_parm_string()
{
   var cl = get_cookie_list();
   var alphabet = "abcdefghijklmnopqrstuvwxyz";
   var daymap = { sun: "S", mon: "M", tue: "T", wed: "W", thu: "R", fri: "F", sat: "Y" };
   var colormap = {
            aqua: "a", black: "b", blue: "b", fuchsia: "f", gray: "G", green: "g",
            lime: "l", maroon: "m", navy: "n", none: "N", olive: "v", orange: "o",
            purple: "p", red: "r", silver: "s", teal: "t", white: "w", yellow: "y" };

   var clp = "";
   var sep = "";
   var ietf = "";
   for (var i = 0; i < cl.length; i += 2) {
      var mtg = cl[i].split("-");
      if (mtg.length != 4) continue;
      ietf = mtg[0];
      var day = mtg[1];
      var hour = mtg[2].substr(0,2) * 1;
      var min = mtg[2].substr(2) * 1;
      var area = mtg[3];
      var color = cl[i+1];
      var mappedcolor = (typeof(colormap[color]) == "string") ? colormap[color] : "N";
      if (mappedcolor == "N") continue;
      // alert("color=" + color + "=>" + colormap[color] + "-" + cl[i] + "/" + typeof(color) + "/" + typeof(colormap[color]));
      clp += sep + mappedcolor + daymap[day] + alphabet.substr(hour,1) + alphabet.substr(min/5, 1) + area;
      sep = "-";
   }
   return ietf + "-" + clp;
}

// 77-lMjaapparea-gMnaoauth-rMpemboned-yMrialto-lMrieai-yTjavwrap-lTnamarf-lTpenewprep-lTrisieve-yTrihttpstate-yWkgrydeirde-rWpcyam-yWnahybi-yRjacore-lRpcmorg-yFjairi-yFnadecade-yFoddecade
// a list of color+roomID sets. list[0] is the IETF#, which prefixes all subsequent entries.
// char[0] l color
// char[1] M day
// char[2] j hour
// char[3] a min
// rest      area
function set_all_parm_colors(parmstring)
{
    if (!parmstring) return;
    var entries = parmstring.split("-");
    var alphabet = "abcdefghijklmnopqrstuvwxyz";
    var daymap = { S: "sun", M: "mon", T: "tue", W: "wed", R: "thu", F: "fri", Y: "sat" };
    var colormap = {
            a: "aqua", b: "black", b: "blue", f: "fuchsia", G: "gray", g: "green",
            l: "lime", m: "maroon", n: "navy", N: "none", v: "olive", o: "orange",
            p: "purple", r: "red", s: "silver", t: "teal", w: "white", y: "yellow" };
    var ietf = entries[0];
    for (var i = 1; i < entries.length; i++) {
	var entry = entries[i];
	var ccolor = entry.substr(0,1);
	var cday = entry.substr(1,1);
	var chour = entry.substr(2,1);
	var cmin = entry.substr(3,1);
	var area = entry.substr(4);

	var color = colormap[ccolor];
	var day = daymap[cday];
	var hour = 1 * alphabet.indexOf(chour);
	if (hour < 10) hour = "0" + hour;
	var min = 5 * alphabet.indexOf(cmin);
	if (min < 10) min = "0" + min;

	var id = ietf + "-" + day + "-" + hour + min + "-" + area;
	setcolor(id, color, true);
    }
}

// open up a new window showing the given room
function venue(room)
{
    window.open('venue/?room=' + room, 'IETF meeting rooms',
	'scrollbars=no,toolbar=no,width=621,height=560');
    return false;
}

