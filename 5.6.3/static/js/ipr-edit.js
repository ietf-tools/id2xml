function cloneMore(selector, type) {
    var newElement = $(selector).clone(true);
    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    newElement.find(':input').each(function() {
        var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
        $(this).attr('for', newFor);
    });
    $(selector).find('a[id$="add_link"]').remove();
    total++;
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    $(selector).after(newElement);
}

$(function() {
    $('#draft_add_link').click(function() {
        cloneMore('#id_contribution tr.draft_row:last','draft');
    });
    $('#rfc_add_link').click(function() {
        cloneMore('#id_contribution tr.rfc_row:last','rfc');
    });
    
    $('input.draft-autocomplete').autocomplete({
        source: "/doc/ajax/internet_draft/?",
        minLength: 3,
    });

})