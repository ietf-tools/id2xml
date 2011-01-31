/* utils.js - utility functions */


//returns the requested GET parameter from the URL
function get_param(param) {
    var regex = '[?&]' + param + '=([^&#]*)';
    var results = (new RegExp(regex)).exec(window.location.href);
    if(results) return results[1];
    return '';
}

function restripe(id) {
      $(id + ' tbody tr:visible:even').removeClass('row1 row2').addClass('row1');
      $(id + ' tbody tr:visible:odd').removeClass('row1 row2').addClass('row2');
}

function init_area_table() {
  // add "Show All" button
  $("#areas-button-list").append('<li><button type="button" id="areas-list-toggle" value="Show All">Show All</button></li>');
  // register button
  $("#areas-list-toggle").click(function() {
      if (this.value == "Show All") {
          $('#areas-list-table tbody tr:not(.active)').show();
          $(this).val("Show Active");
          $(this).text("Show Active");
      } else if (this.value == "Show Active") {
          $('#areas-list-table tbody tr:not(.active)').hide();
          $(this).val("Show All");
          $(this).text("Show All");
      }
      // restripe the table
      restripe('#areas-list-table');
  });
  // hide non-active areas
  $('#areas-list-table tbody tr:not(.active)').hide();
  restripe('#areas-list-table');
}

function style_current_tab() {
    path_array = window.location.pathname.split('/');
    page = path_array[path_array.length-2];
    id = "#nav-" + page;
    $(id + ' a').addClass('current');
}


/*********************************
/*Functions : For Proceedings    */
/*********************************/
function init_proceedings_table() {
  // add "Show All" button
  $("#proceedings-button-list").append('<li><button type="button" id="proceedings-list-toggle" value="Show All">Show All</button></li>');
  // register button
  $("#proceedings-list-toggle").click(function() {
      if (this.value == "Show All") {
          $('#proceedings-list-table tbody tr:not(.0)').show();
          $(this).val("Show Active");
          $(this).text("Show Active");
      } else if (this.value == "Show Active") {
          $('#proceedings-list-table tbody tr:not(.0)').hide();
          $(this).val("Show All");
          $(this).text("Show All");
      }
      // restripe the table
      restripe('#proceedings-list-table');
  });
  // hide non-active areas
  $('#proceedings-list-table tbody tr:not(.0)').hide();
  restripe('#proceedings-list-table');

}



$(document).ready(function() {
  // in general set focus on first input field
  $("input:text:visible:enabled:first").focus();

  // set focus on first new_email field for bulk update
  if ( ("form[id^=bulk-update-form]").length > 0){
      $("input[id^=id_new_email]:first").focus();
  }

  // set focus for group role assignment
  if ( ("form[id^=group-role-assignment-form]").length > 0){
      $("#id_role_type").focus();
  }

  // unset Primary Area selection unless it appears as URL parameter 
  //if (($('#id_primary_area').length) && (get_param('primary_area') == '')) {
  //    $('#id_primary_area')[0].selectedIndex = -1;

  // special features for area list page
  if ($('#areas-button-list').length) {
      init_area_table();
  }
  // Setup autocomplete for adding names 
  if ($('input.name-autocomplete').length) {
      $('input.name-autocomplete').autocomplete({
          source: "/sec/areas/getpeople/",
          minLength: 3,
          select: function(event, ui) {
            text = ui.item.value;
            text = text.replace(/.*[ ]([^ ]+@[^ ]+)[ ].*/, "$1");
            $('#id_login').val(text);
            // alert(text);
          }
      });
  }

  // nav bar setup
  if ($('ul#list-nav').length) {
      style_current_tab();
  }

  // auto populate Area Director List when primary area selected (add form)
  $('#id_primary_area').change(function(){
      $.getJSON('/sec/groups/get_ads/',{"area":$(this).val()},function(data) {
          $('#id_primary_area_director option').remove();
          $.each(data,function(i,item) {
              $('#id_primary_area_director').append('<option value="'+item.id+'">'+item.value+'</option>');
          });
      });
  });

  // auto populate Area Director List when area selected (edit form)
  $('#id_ietfwg-0-primary_area').change(function(){
      $.getJSON('/sec/groups/get_ads/',{"area":$(this).val()},function(data) {
          $('#id_ietfwg-0-area_director option').remove();
          $.each(data,function(i,item) {
              $('#id_ietfwg-0-area_director').append('<option value="'+item.id+'">'+item.value+'</option>');
          });
      });
  });

  // special features for Proceedings list page
  if ($('#proceedings-button-list').length) {
      init_proceedings_table();
  }



});

