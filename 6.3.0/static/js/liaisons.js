$(document).ready(function () {
    function setupAttachmentWidget() {
        var button = $(this);
        var config = {};
        var count = 0;

        var readConfig = function() {
            var buttonFormGroup = button.parents('.form-group');
            var disabledLabel = buttonFormGroup.find('.attachDisabledLabel');

            if (disabledLabel.length) {
                config.disabledLabel = disabledLabel.html();
                var required = [];
                buttonFormGroup.find('.attachRequiredField').each(function(index, field) {
                    required.push('#' + $(field).text());
                });
                config.basefields = $(required.join(","));
            }

            config.showOn = $('#' + buttonFormGroup.find('.showAttachsOn').html());
            config.showOnDisplay = config.showOn.find('.attachedFiles');
            count = config.showOnDisplay.find('.initialAttach').length;
            config.showOnEmpty = config.showOn.find('.showAttachmentsEmpty').html();
            config.enabledLabel = buttonFormGroup.find('.attachEnabledLabel').html();
        };

        var setState = function() {
            var enabled = true;
            config.fields.each(function() {
                if (!$(this).val()) {
                    enabled = false;
                    return;
                }
            });
            if (enabled) {
                button.removeAttr('disabled').removeClass('disabledAddAttachment');
                button.val(config.enabledLabel);
            } else {
                button.attr('disabled', 'disabled').addClass('disabledAddAttachment');
                button.val(config.disabledLabel);
            }
        };

        var cloneFields = function() {
            var html = '<div class="attachedFileInfo">';
            if (count) {
                html = config.showOnDisplay.html() + html;
            }
            config.fields.each(function() {
                var field = $(this);
                var container= $(this).parents('.form-group');
                if (container.find(':file').length) {
                    html += ' (' + field.val() + ')';
                } else {
                    html += ' ' + field.val();
                }
                html += '<span style="display: none;" class="removeField">';
                html += container.attr('id');
                html += '</span>';
                container.hide();
            });
            html += ' <a href="" class="removeAttach glyphicon glyphicon-remove text-danger"></a>';
            html += '</div>';
            config.showOnDisplay.html(html);
            count += 1;
            initFileInput();
        };

        var doAttach = function() {
            cloneFields();    
            setState();
        };

        var removeAttachment = function() {
            var link = $(this);
            var attach = $(this).parent('.attachedFileInfo');
            var fields = attach.find('.removeField');
            fields.each(function() {
                $('#' + $(this).html()).remove();
            });
            attach.remove();
            if (!config.showOnDisplay.html()) {
                config.showOnDisplay.html(config.showOnEmpty);
                count = 0;
            }
            return false;
        };

        var initTriggers = function() {
            config.showOnDisplay.on('click', 'a.removeAttach', removeAttachment);
            button.click(doAttach);
        };

        var initFileInput = function() {
            var fieldids = [];
            config.basefields.each(function(i) {
                var field = $(this);
                var oldcontainer= $(this).parents('.form-group');
                var newcontainer= oldcontainer.clone();
                var newfield = newcontainer.find('#' + field.attr('id'));
                newfield.attr('name', newfield.attr('name') + '_' + count);
                newfield.attr('id', newfield.attr('id') + '_' + count);
                newcontainer.attr('id', 'container_id_' + newfield.attr('name'));
                oldcontainer.after(newcontainer);
                oldcontainer.hide();
                newcontainer.show();
                fieldids.push('#' + newfield.attr('id'));
            });
            config.fields = $(fieldids.join(","));
            config.fields.change(setState);
            config.fields.keyup(setState);
        };

        var initWidget = function() {
            readConfig();

            initFileInput();
            initTriggers();

            setState();
        };

        initWidget();
    }

    $('form.liaisons-form').each(function() {
        var form = $(this);
        var from_groups = form.find('#id_from_groups');
        var from_contact = form.find('#id_from_contact');
        var to_groups = form.find('#id_to_groups');
        var to_contacts = form.find('#id_to_contacts');
        var cc = form.find('#id_cc_contacts');
        var purpose = form.find('#id_purpose');
        var deadline = form.find('#id_deadline');
        var submission_date = form.find('#id_submitted_date');
        var approval = form.find('#id_approved');
        var initial_approval_label = form.find("label[for='id_approved']").text();
        var cancel = form.find('#id_cancel');
        var cancel_dialog = form.find('#cancel-dialog');
        var config = {};
        var related_trigger = form.find('.id_related_to');
        var related_url = form.find('#id_related_to').parent().find('.listURL').text();
        var related_dialog = form.find('#related-dialog');
        var unrelate_trigger = form.find('.id_no_related_to');

        var render_mails_into = function(container, person_list, as_html) {
            console.log('calling render_mails');
            var html='';

            $.each(person_list, function(index, person) {
                if (as_html) {
                    html += person[0] + ' &lt;<a href="mailto:'+person[1]+'">'+person[1]+'</a>&gt;<br />';
                } else {
                    //html += person[0] + ' &lt;'+person[1]+'&gt;\n';
                    html += person + '\n';
                }
            });
            container.html(html);
        };

        var toggleApproval = function(needed) {
            console.log('called toggle' + needed);
            if (!approval.length) {
                return;
            }
            if (!needed) {
                approval.prop('checked',true);
                approval.hide();
                //$("label[for='id_approved']").text("Approval not required");
                var nodes = $("label[for='id_approved']:not(.control-label)")[0].childNodes;
                nodes[nodes.length-1].nodeValue= 'Approval not required';
                return;
            }
            if ( needed && !$('#id_approved').is(':visible') ) {
                approval.prop('checked',false);
                approval.show();
                //$("label[for='id_approved']").text(initial_approval_label);
                var nodes = $("label[for='id_approved']:not(.control-label)")[0].childNodes;
                nodes[nodes.length-1].nodeValue=initial_approval_label;
                return;
            }
        };

        var checkPostOnly = function(post_only) {
            if (post_only) {
                $("input[name=send]").hide();
            } else {
                $("input[name=send]").show();
            }
        };

        var updateInfo = function(first_time, sender) {
            var from_ids = from_groups.val();
            var to_ids = to_groups.val();
            console.log(Object.keys(sender));
            console.log(sender.id);
            console.log(sender.attr('id'));
            console.log('calling ajax');
            var url = form.data("ajaxInfoUrl");
            $.ajax({
                url: url,
                type: 'GET',
                cache: false,
                async: true,
                dataType: 'json',
                data: {from_groups: from_ids,
                       to_groups: to_ids},
                success: function(response){
                    if (!response.error) {
                        if (!first_time || !cc.text()) {
                            render_mails_into(cc, response.cc, false);
                        }
                        //render_mails_into(poc, response.poc, false);
                        if ( sender.attr('id') == 'id_to_groups' ) {
                            console.log('inside to_groups');
                            console.log(response.poc);
                            to_contacts.val(response.poc);
                        }
                        if ( sender.attr('id') == 'id_from_groups' ) {
                            toggleApproval(response.needs_approval);
                        }
                        checkPostOnly(response.post_only);
                        // if (sender.hasClass('from-group-field')) {userSelect(sender,response.full_list);}
                    }
                }
            });
            return false;
        };

        //var updateFrom = function() {
        //   var reply_to = reply.val();
        //    form.find('a.from_mailto').attr('href', 'mailto:' + reply_to);
        //};

        var updatePurpose = function() {
            var deadlinecontainer = deadline.closest('.form-group');
            //var othercontainer = other_purpose.closest('.form-group');

            var value = purpose.val();
            console.log(value);
            
            if (value == 'action' || value == 'comment') {
                deadline.prop('required',true);
                deadlinecontainer.show();
            } else {
                deadline.prop('required',false);
                deadlinecontainer.hide();
                deadline.val('');
            }
        };

        //var checkOtherSDO = function() {
        //    var entity = organization.val();
        //    if (entity=='othersdo') {
        //        other_organization.closest('.form-group').show();
        //        other_organization.prop("required", true);
        //    } else {
        //        other_organization.closest('.form-group').hide();
        //        other_organization.prop("required", false);
        //    }
        //};

        var cancelForm = function() {
            cancel_dialog.dialog("open");
        };

        var getRelatedLink = function() {
            var link = jQuery(this).text();;
            var pk = jQuery(this).nextAll('.liaisonPK').text();
            var widget = related_trigger.parent();
            var newwidget = widget.clone()
            related_dialog.dialog('close');
            newwidget.find('.id_related_to').click(selectRelated);
            newwidget.find('.id_no_related_to').click(selectNoRelated);
            newwidget.find('.relatedLiaisonWidgetTitle').text(link);
            newwidget.find('.relatedLiaisonWidgetValue').val(pk);
            newwidget.find('.noRelated').hide();
            newwidget.find('.id_related_to').hide();
            newwidget.find('.id_no_related_to').show();
            widget.before(newwidget);
            return false;
        };

        var selectNoRelated = function() {
            var widget = jQuery(this).parent();
            widget.remove();
            return false;
        };

        var selectRelated = function() {
            var trigger = jQuery(this);
            var widget = jQuery(this).parent();
            var url = widget.find('.listURL').text();
            var title = widget.find('.relatedLiaisonWidgetTitle');
            related_dialog.html('<img src="/images/ajax-loader.gif" />');
            related_dialog.dialog('open');
            jQuery.ajax({
                url: url,
                type: 'GET',
                cache: false,
                async: true,
                dataType: 'html',
                success: function(response){
                    related_dialog.html(response);
                    related_dialog.find("#LiaisonListTable").tablesorter({
                        sortList: [[0, 1]],
                        widgets: ["ietf"]
                    });
                    related_dialog.find('td a').click(getRelatedLink);
                }
            });
            return false;
        };

        var checkFrom = function(first_time,target) {
            // adjust to group options based on selected from group
            //console.log(Object.getOwnPropertyNames($(this)));
            //console.log(Object.getOwnPropertyNames(e));
            //console.log(target.id);
            var reduce_options = form.find('.reducedToOptions');
            if (!reduce_options.length) {
                updateInfo(first_time, target);
                return;
            }
            var to_select = organization;
            var from_entity = from.val();
            if (!reduce_options.find('.full_power_on_' + from_entity).length) {
                to_select.find('optgroup').eq(1).hide();
                to_select.find('option').each(function() {
                    if (!reduce_options.find('.reduced_to_set_' + $(this).val()).length) {
                        $(this).hide();
                    } else {
                        $(this).show();
                    }
                });
                if (!to_select.find('option:selected').is(':visible')) {
                    to_select.find('option:selected').removeAttr('selected');
                }
            } else {
                to_select.find('optgroup').show();
                to_select.find('option').show();
            }
            updateInfo(first_time, target);
        };

        var checkSubmissionDate = function() {
            var date_str = submission_date.val();
            if (date_str) {
                var sdate = new Date(date_str);
                var today = new Date();
                if (Math.abs(today-sdate) > 2592000000) {  // 2592000000 = 30 days in milliseconds
                    return confirm('Submission date ' + date_str + ' differ more than 30 days.\n\nDo you want to continue and post this liaison using that submission date?\n');
                }
                return true;
            }
            else
                return false;
        };


        // init form
        $('#id_from_groups').select2();
        $('#id_to_groups').select2();
        to_groups.change(function() { updateInfo(false,$(this)); });
        from_groups.change(function() { updateInfo(false,$(this)); });
        //to_groups.change(checkOtherSDO);
        //from_groups.change(function(e) { checkFrom(false,$(e.target)); });
        //reply.keyup(updateFrom);
        purpose.change(updatePurpose);
        //related_trigger.click(selectRelated);
        //unrelate_trigger.click(selectNoRelated);
        form.submit(checkSubmissionDate);

        //updateFrom();
        $('.from-group-field').each(function() {
            checkFrom(true,$(this));
        });
        //checkFrom(true);
        updatePurpose();
        //checkOtherSDO();

        form.find('.addAttachmentWidget').each(setupAttachmentWidget);
    });
    
    // use traditional style URL parameters
    $.ajaxSetup({ traditional: true });


    // search form, based on doc search feature
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
        return advanced;
    }
    
    function toggleSubmit() {
        var textSearch = $.trim($("#id_text").val());
        form.find("button[type=submit]").get(0).disabled = !textSearch && !anyAdvancedActive();
    }
    
    if (form.length > 0) {
        // form.find(".search_field input[name=by]").closest(".search_field").find("label,input").click(updateAdvanced);
        form.find(".search_field input,select").change(toggleSubmit).click(toggleSubmit).keyup(toggleSubmit);
    }
    
});
