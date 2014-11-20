//---------------------------------------
// Setup date time modal views
//---------------------------------------

$(document).ready(function() {
    $('.appbuilder_datetime').datetimepicker();
    $('.appbuilder_date').datetimepicker({
        pickTime: false });
    //remove part after the / 
    var url = document.URL.toString()
    //Pretty sure there is better way
    var blueprint_level = url.indexOf('/')
    for (i = 0; i < 3; i++) {
        blueprint_level = url.indexOf('/', blueprint_level + 1)
    }
    url = url.slice(0, blueprint_level)
    $(".my_select2").each(function (index) {
        $(this).select2({
            placeholder: "Select a State", allowClear: true,
            ajax: { // instead of writing the function to execute the request we use Select2's convenient helper
                url: url + '/get_ajax_select/' + $(this).attr('id').toString(),
                dataType: 'json',
                quietMillis: 250,
                contentType: 'application/json;charset=UTF-8',
                data: function (term, page) {
                    //Parse the form as json to be accessed in request
                    return $(this).closest("form").serialize() // search term
                    ;
                },
                results: function (data, page) { // parse the results into the format expected by Select2.
                    // since we are using custom formatting functions we do not need to alter the remote JSON data
                    return data;
                },
                cache: true
            }

        });
    });


    $("a").tooltip({ 'selector': '', 'placement': 'bottom' });


});


$( ".my_change" ).on("change", function(e) {
 var theForm=document.getElementById("model_form");
  theForm.action = "";
  theForm.method = "get";
  theForm.submit();
 })


//---------------------------------------
// Bootstrap modal, javascript alert
//---------------------------------------
function ab_alert(text) {
    $('#modal-alert').on('show.bs.modal', function(e) {
            $('.modal-text').text(text);
        }
    );
    $('#modal-alert').modal('show');
};


//---------------------------------------
// Modal confirmation JS support
//---------------------------------------

// On link attr "data-text" is set to the modal text
$(document).ready(function(){
    $(".confirm").click(function() {
        $('.modal-text').text($(this).data('text'));
    });
});

// If positive confirmation on model follow link
$('#modal-confirm').on('show.bs.modal', function(e) {
    $(this).find('#modal-confirm-ok').attr('href', $(e.relatedTarget).data('href'));
});

