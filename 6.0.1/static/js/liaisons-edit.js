function setupFromGroupRows() {
    if($('.from-row:visible').length == 1) {
        $('.from-row:visible').find(".btn-delete").hide();
    }
        
    $('.btn-delete').click(function() {
        var container = $(this).parents('.form-group');
        var dinput = container.find("input[id$='DELETE']");
        dinput.prop('checked', true);
        container.hide();
        // if one row left remove delete button
        if($('.from-row:visible').length == 1) {
            $('.from-row:visible').find(".btn-delete").hide();
        }
    });
}

$(document).ready(function() {
    var form = $("form.liaisons-form");

    var template = form.find('.from-row.template');

    var templateData = template.clone();

    setupFromGroupRows();
    
    $('.from-add-row').click(function() {
        var el = template.clone(true);
        var totalField = $('#id_form-TOTAL_FORMS');
        var total = +totalField.val();

        el.find(':input').each(function() {
            var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
            var id = 'id_' + name;
            $(this).attr({'name': name, 'id': id}).val('');
        });

        el.find('label').each(function() {
            var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
            $(this).attr('for', newFor);
        });

        ++total;

        totalField.val(total);

        template.before(el);
        el.removeClass("template");
    
        el.find(".select2-field").each(function () {
            setupSelect2Field($(this));
        });
        
        // show all delete buttons
        $('.from-row:visible').find(".btn-delete").show();
    });
    
    
    
});
