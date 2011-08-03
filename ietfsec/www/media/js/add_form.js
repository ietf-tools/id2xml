/* add-form.js
   This script creates a "Add Another" link to specified formsets so the user
   can dynamically add items to a form.  It looks for divs with 
   "add-form" class, then hides all empty child rows but one.  When Add Another
   is clicked a new row is shown.  Once all available rows are visible the 
   Add Another link is removed
*/
function addForm(prefix) {
    $('.add-form').find('tr:hidden:first').show();
    if (!$('.add-form').find('tr:hidden').length) {
        $('.addlink').hide();
    }
}

// Add all the "Add Another" links to the bottom of each inline group
$(function() {
    var html_template = '<ul class="tools">'+
        '<li>'+
            '<a class="addlink" href="#" onclick="return addForm(\'{{prefix}}\')">'+
            'Add another</a>'+
        '</li>'+
    '</ul>'
    $('.add-form').each(function(i) {
        //prefix is in the name of the input fields before the "-"
        var prefix = $("input[type='hidden']", this).attr("name").split("-")[0]
        $(this).append(html_template.replace("{{prefix}}", prefix))
        // hide extra forms
        var formINITIAL = parseInt($('#id_' + prefix + '-INITIAL_FORMS').val());
        counter = 0;
        $(this).find("tr").each(function() {
            var test = $(this).find('input[value!=""][type!="hidden"]');
            if (counter > formINITIAL) {
                if ((!$(this).find('input[value!=""][type!="hidden"]').length) && (!$(this).find('select[value!=""]').length)) {
                    $(this).addClass('hidden').hide();
                }
            }
            counter++;
        });
    })
})
