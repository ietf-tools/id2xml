function QueryString()
// Create a QueryString object
{
    // get the query string, ignore the ? at the front.
    var querystring = location.search.substring(1);


    // parse out name/value pairs separated via &
    var args = querystring.split('&');

    // split out each name = value pair
    for (var i = 0; i < args.length; i++) {
        var pair = args[i].split('=');

        // Fix broken unescaping
        var temp = unescape(pair[0]).split('+');
        var name_ = temp.join(' ');

        var value_ = '';
        if (typeof pair[1] == 'string') {
            temp = unescape(pair[1]).split('+');
            value_ = temp.join(' ');
        }

        this[name_] = value_;
    }

    this.get = function(nm, def) {
        var value_ = this[nm];
        if (value_ == null) return def;
        else return value_;
    };
} // end QueryString()
