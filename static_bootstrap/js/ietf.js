// See http://stackoverflow.com/questions/8878033/how-to-make-twitter-bootstrap-menu-dropdown-on-hover-rather-than-click
// Tweaked here, so it only expands on hover for non-collapsed navbars, and works for submenus

function hoverin() {
	navbar = $(this).closest('.navbar');
	if (navbar.size() == 0 || navbar.find('.navbar-toggle').is(':hidden')) {
		$(this).addClass('open');
	}
}

function hoverout() {
	navbar = $(this).closest('.navbar');
	if (navbar.size() == 0|| navbar.find('.navbar-toggle').is(':hidden')) {
		$(this).removeClass('open');
	}
}

$('ul.nav li.dropdown').hover(hoverin, hoverout);
$('ul.nav li.dropdown-submenu').hover(hoverin, hoverout);
