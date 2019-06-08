$(function() {
    $('#importbutton').click(function(){
        var $this = $(this);
	    $this.text('Please wait. Importing can take a few moments...');
        $this.attr('disabled', 'disabled');
    });
});
