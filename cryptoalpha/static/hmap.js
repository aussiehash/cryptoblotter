$(document).ready(function() {
    // Format Red and Green Numbers (negative / positive)
    $("td.redgreen").removeClass('red');
    $("td.redgreen").addClass('green');
    $("td.redgreen:contains('-')").removeClass('green');
    $("td.redgreen:contains('-')").addClass('red');

    // Let's create a heatmap on all heatmap values
    // Function to get the max value in an Array
    Array.max = function(array){
        return Math.max.apply(Math,array);
    };

    // Function to get the min value in an Array
    Array.min = function(array){
        return Math.min.apply(Math,array);
    };

    // Get all data values from our table cells making sure to ignore the first column of text
    // Use the parseInt function to convert the text string to a number

    var counts_positive= $('.heatmap').map(function() {
        if (parseInt($(this).text()) > 0) {
        return parseInt($(this).text());
        };
    }).get();

    var counts_negative= $('.heatmap').map(function() {
        if (parseInt($(this).text()) < 0) {
        return parseInt($(this).text());
        };
    }).get();

    // run max value function and store in variable
    var max = Array.max(counts_positive);
    var min = Array.min(counts_negative) * (-1);

    n = 100; // Declare the number of groups

    // Define the ending colour, which is white
    xr = 255; // Red value
    xg = 255; // Green value
    xb = 255; // Blue value

    // Define the starting colour for positives
    yr = 0; // Red value 243
    yg = 135; // Green value 32
    yb = 50; // Blue value 117

    // Define the starting colour for negatives
    nr = 115; // Red value 243
    ng = 0; // Green value 32
    nb = 0; // Blue value 117

    // Loop through each data point and calculate its % value
    $('.heatmap').each(function(){
        if (parseInt($(this).text()) > 0) {
            var val = parseInt($(this).text());
            var pos = parseInt((Math.round((val/max)*100)).toFixed(0));
            red = parseInt((xr + (( pos * (yr - xr)) / (n-1))).toFixed(0));
            green = parseInt((xg + (( pos * (yg - xg)) / (n-1))).toFixed(0));
            blue = parseInt((xb + (( pos * (yb - xb)) / (n-1))).toFixed(0));
            clr = 'rgb('+red+','+green+','+blue+')';
            $(this).css({backgroundColor:clr});
        }
        else {
            var val = parseInt($(this).text()) * (-1);
            var pos = parseInt((Math.round((val/max)*100)).toFixed(0));
            red = parseInt((xr + (( pos * (nr - xr)) / (n-1))).toFixed(0));
            green = parseInt((xg + (( pos * (ng - xg)) / (n-1))).toFixed(0));
            blue = parseInt((xb + (( pos * (nb - xb)) / (n-1))).toFixed(0));
            clr = 'rgb('+red+','+green+','+blue+')';
            $(this).css({backgroundColor:clr});
        }
    });
});
