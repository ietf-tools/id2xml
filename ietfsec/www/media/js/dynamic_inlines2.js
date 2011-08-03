/*
  dynamic-inlines.js

  Script to process create button to display additional fields for each inline formset.

*/

function add_inline_form(name) {
    var count = 0;
}

function add_phone() {
    phone_count = phone_count + 1;
    $("#phoneTable tr").eq(phone_count).show();
    // remove button if max reached
}

// Add all the "Add Another" links to the bottom of each inline group
$(function() {
    // global variables
    phone_count = init_phone_rows;

    // local variables
    var init_phone_rows = parseInt($("#id_phone-INITIAL_FORMS").val());
    var count = $("#phoneTable tr").length;
    var html_template = '<ul class="tools">'+
        '<li>'+
            '<a class="add" href="#" onclick="return add_inline_form(\'{{prefix}}\')">'+
            'Add another</a>'+
        '</li>'+
    '</ul>'

    $('.inline-group').each(function(i) {
        //prefix is in the name of the input fields before the "-"
        var prefix = $("input[type='hidden']", this).attr("name").split("-")[0]
        $(this).append(html_template.replace("{{prefix}}", prefix))
    })

    // hide extra fields
    // $("#phoneTable tr").slice(init_phone_rows + 1,count).hide();
})

