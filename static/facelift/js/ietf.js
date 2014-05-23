// See http://stackoverflow.com/questions/8878033/how-to-make-twitter-bootstrap-menu-dropdown-on-hover-rather-than-click
// Tweaked here, so it only expands on hover for non-collapsed navbars, and works for submenus

function hoverin() {
	var navbar = $(this).closest('.navbar');
	if (navbar.size() === 0 || navbar.find('.navbar-toggle').is(':hidden')) {
		$(this).addClass('open');
	}
}

function hoverout() {
	var navbar = $(this).closest('.navbar');
	if (navbar.size() === 0|| navbar.find('.navbar-toggle').is(':hidden')) {
		$(this).removeClass('open');
	}
}

$('ul.nav li.dropdown').hover(hoverin, hoverout);
$('ul.nav li.dropdown-submenu').hover(hoverin, hoverout);


// This used to be in doc-search.js; consolidate all JS in one file.

$(function () {
	// search form
	var form = $("#search_form");

	function anyAdvancedActive() {
		var advanced = false;
		var by = form.find("input[name=by]:checked");

		if (by.length > 0) {
			by.closest(".search_field").find("input,select").not("input[name=by]").each(function () {
				if ($.trim(this.value)) {
					advanced = true;
				}
			});
		}

		var additional_doctypes = form.find("input.advdoctype:checked");
		if (additional_doctypes.length > 0) {
			advanced = true;
			return advanced;
		}
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
	$('.addtolist a').click(function(e) {
		e.preventDefault();
		var trigger = $(this);
		$.ajax({
			url: trigger.attr('href'),
			type: 'GET',
			cache: false,
			dataType: 'json',
			success: function(response){
				if (response.success) {
					trigger.replaceWith('<span class="glyphicon glyphicon-tag text-danger"></span>');
				}
			}
		});
	});
});


// This used to be in js/history.js
$(".snippet .show-all").click(function () {
	$(this).parents(".snippet").addClass("hidden").siblings(".full").removeClass("hidden");
});


// This used to be in js/iesg-discusses.js
// AND IT'S BROKEN: causes document history to be hidden
// $("label.btn:has(input)").click(function () {
//	val = $(this).children().attr("value");
//	if (val == "all") {
//		$("tr").show();
//	} else {
//		$("tr").filter("." + val).show();
//		$("tr").not("." + val).hide();
//	}
// });

// Store the shown/hidden state for the search form collapsible persistently
// Not such a great idea after all, comment out for now.
// $('#searchcollapse').on('hidden.bs.collapse', function() {
//	localStorage.removeItem(this.id);
// }).on('shown.bs.collapse', function() {
//	localStorage[this.id] = "show";
// }).each(function() {
//	if (localStorage[this.id] === "show") {
//		$(this).collapse('show');
//	} else {
//		$(this).collapse('hide');
//	}
// });


function to_disp(t) {
	return _.unescape(t).replace(/[<>]/g, function (m) {
		return {
			'<': '(',
			'>': ')'
		}[m];
	});
}


function from_disp(t) {
	var s = t.split(",");
	var i, length;

	for (i = 0, length = s.length; i < length; i++) {
		s[i] = s[i].replace(/.*\((.*)\).*/g, "$1");
	}
	return s.join(", ");
}


$(".tokenized-form").submit(function (e) {
	e.preventDefault();

	$(this).find(".tokenized-field").each(function () {
		var x, length;
		var f = $(this);
		var io = f.data("io");
		var format = f.data("format");
		var display = f.data("display");
		var result = f.data("result");
		var url = f.data("ajax-url");
		var s = $.grep(f.val().split(","), function (n, i) {
			return !n.match(/^\s+$/);
		});

		var empty = true;
		for (x = 0, length = s.length; x < length; x++) {
			console.log(x, s[x]);

			// need to use a closure here
			(function (i) {
				console.log(i, s[i]);
				s[i] = from_disp(s[i].trim());
				if (s[i]) {
					empty = false;
					console.log("ajax", i, s[i]);
					$.ajax({
						url: url + s[i]
					}).done(function(data) {
						console.log("done", i, s[i], data);
						if (data[0] && s[i] === data[0][display]) {
							s[i] = data[0][result];
							console.log("done", i, s[i]);
						}
					});
				}
			})(x);
		}
		console.log(x);

		if (empty) {
			$(".tokenized-form").unbind('submit').submit();
		} else {
			console.log("waiting");
			$(document).ajaxStop(function() {
				if (format === "json") {
					f.val(JSON.stringify(s));
				} else if (format === "csv") {
					f.val(s.join(", "));
				} else {
					console.log("unknown format");
					f.val(s.join(" "));
				}

				if (io) {
					$(io).val(f.val());
				}
				console.log("final: " + f.val());
				$(".tokenized-form").unbind('submit').submit();
			});
		}
	});
});


$(".tokenized-field").each(function () {
	// which field of the JSON are we supposed to display
	var display = $(this).data("display");
	if (!display) {
		display = "name";
	}
	console.log("display: ", display);
	$(this).data("display", display)

	// which field of the JSON are we supposed to return
	var result = $(this).data("result");
	if (!result) {
		result = "id";
	}
	console.log("result: ", result);
	$(this).data("result", result);

	// what kind of data are we returning (json or csv)
	var format = $(this).data("format");
	if (!format) {
		format = "csv";
	}
	console.log("format: " + format);
	$(this).data("format", format);

	// in which field ID are we expected to place the result
	// (we also read the prefill information from there
	var io = $(this).data("io");
	var raw = "";
	if (io) {
		raw = $(io).val();
	} else {
		io = "#" + this.id;
		raw = $(this).val();
	}
	console.log("io: ", io);
	console.log("raw: ", raw);
	$(this).data("io", io);

	if (raw) {
		raw = $.parseJSON(raw);
		var pre = "";
		if (!raw[0] || !raw[0][display]) {
			$.each(raw, function(k, v) {
				console.log(k, v);
				pre += to_disp(v) + ", ";
			});
		} else {
			for (var i in raw) {
				pre += to_disp(raw[i][display]) + ", ";
			}
		}
		$(this).val(pre);
	}
	console.log("pre: ", pre);

	// check if the ajax-url contains a query parameter, add one if not
	var url = $(this).data("ajax-url");
	if (url.indexOf("?") === -1) {
		url += "?q=";
	}
	$(this).data("ajax-url", url)
	console.log("ajax-url: ", url);

	var bh = new Bloodhound({
		datumTokenizer: function (d) {
			return Bloodhound.tokenizers.nonword(d[display]);
		},
		queryTokenizer: Bloodhound.tokenizers.nonword,
		limit: 20,
		remote: {
			url: url + "%QUERY",
			filter: function (data) {
				return $.map($.grep(data, function (n, i) {
					return true;
				}), function (n, i) {
					n["value"] = to_disp(n[display]);
					return n;
				});
			}
		}
	});
	bh.initialize();
	$(this).tokenfield({
		typeahead: [{
			highlight: true,
			minLength: 3,
			hint: true,
		}, {
			source: bh.ttAdapter(),
		}],
		createTokensOnBlur: true,
		beautify: true,
		delimiter: [',', ';']
	});
});
