/* See http://stackoverflow.com/questions/8878033/how-to-make-twitter-bootstrap-menu-dropdown-on-hover-rather-than-click and http://www.fourfront.us/blog/jquery-window-width-and-media-queries and http://stackoverflow.com/questions/1974788/combine-onload-and-onresize-jquery
*/

$(window).on("debouncedresize", function() {	
	if ($(".navbar .btn-navbar").css("display") == "none" ) {
		jQuery('ul.nav li.dropdown').hover(function() {
			jQuery(this).closest('.dropdown-menu').stop(true, true).show(); 
			jQuery(this).addClass('open'); }, function() {
				jQuery(this).closest('.dropdown-menu').stop(true, true).hide(); 
				jQuery(this).removeClass('open');
			}
		);
	} else {
		jQuery('ul.nav li.dropdown').off();
	}
}).trigger("debouncedresize");

