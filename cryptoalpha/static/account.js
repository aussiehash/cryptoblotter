
$(function() {
    $('#DELETE').change(function(){
        if ($('#DELETE').val() == "DELETE") {
            $('#DELETEBUTTON').prop('disabled', false);
        }
    });
});
