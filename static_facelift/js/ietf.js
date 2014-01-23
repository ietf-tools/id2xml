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


// This used to be in doc-search.js; consolidate all JS in one file.

$(function () {
    // search form
    var form = jQuery("#search_form");

    function anyAdvancedActive() {
        var advanced = false;

        var by = form.find("input[name=by]:checked");
        if (by.length > 0)
            by.closest(".search_field").find("input,select").not("input[name=by]").each(function () {
                if ($.trim(this.value))
                    advanced = true;
            });

	var additional_doctypes = form.find("input.advdoctype:checked");
	if (additional_doctypes.length > 0)
	    advanced = true;

        return advanced;
    }

    function toggleSubmit() {
        var nameSearch = $.trim($("#id_name").val());
        form.find("button[type=submit]").get(0).disabled = !nameSearch && !anyAdvancedActive();
    }

    function updateAdvanced() {
        form.find("input[name=by]:checked").closest(".search_field").find("input,select").not("input[name=by]").each(function () {
            this.disabled = false;
            this.focus();
        });

        form.find("input[name=by]").not(":checked").closest(".search_field").find("input,select").not("input[name=by]").each(function () {
            this.disabled = true;
        });

        toggleSubmit();
    }

    if (form.length > 0) {
        form.find(".search_field input[name=by]").closest(".search_field").find("label,input").click(updateAdvanced);

        form.find(".search_field input,select")
            .change(toggleSubmit).click(toggleSubmit).keyup(toggleSubmit);

        form.find(".toggle_advanced").click(function () {
            var advanced = $(this).next();
            advanced.find('.search_field input[type="radio"]').attr("checked", false);
            updateAdvanced();
        });

        updateAdvanced();
    }

    // search results
    $('.search-results .addtolist a').click(function(e) {
        e.preventDefault();
        var trigger = $(this);
        $.ajax({
            url: trigger.attr('href'),
            type: 'POST',
            cache: false,
            dataType: 'json',
            success: function(response){
                if (response.success) {
                    trigger.replaceWith('<span class="glyphicon glyphicon-star"></span>');
                }
            }
        });
    });

    $("a.ballot-icon").click(function (e) {
    	// find the name of the ID in the current table row
    	var id = $(this).closest("tr").find("td.doc a:first-child").text().trim();

        e.preventDefault();
        $.ajax({
            url: $(this).data("popup"),
            success: function (data) {
                showModalBox(id, data);
            },
            error: function () {
                console.log("Error retrieving popup content");
            }
        });
    }).each(function () {
        // bind right-click shortcut
        var editPositionUrl = $(this).data("edit");
        if (editPositionUrl) {
            $(this).bind("contextmenu", function (e) {
                e.preventDefault();
                window.location = editPositionUrl;
            });
        }
    });
});

function showModalBox(title, content) {
	// set the modal title based on the ID name
	var c = $(content);
	c.find("#modal-label").text("Ballot Positions: " + title);
	$("body").append(c);

	// remove the modal from the DOM on hide
	$('#modal-overlay').on('hidden.bs.modal', function () { $(this).remove(); });

	// show the modal
	$('#modal-overlay').modal();
}
