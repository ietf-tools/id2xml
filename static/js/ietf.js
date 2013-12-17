// See http://stackoverflow.com/questions/8878033/how-to-make-twitter-bootstrap-menu-dropdown-on-hover-rather-than-click
jQuery('ul.nav li.dropdown').hover(function() {
	jQuery(this).closest('.dropdown-menu').stop(true, true).show();
	jQuery(this).addClass('open');
}, function() {
	jQuery(this).closest('.dropdown-menu').stop(true, true).hide();
	jQuery(this).removeClass('open');
});
