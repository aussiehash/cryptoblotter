$(document).ready(function() {
    // Loop through all elements with trade_id and get
    // the trade details
    $('[id^=tradeid_]').each(function() {
        var hp = $(this).data("hp");
        var q = $(this).data("q");
        var number = this.id.split('_').pop();
        tradedetails(number, hp, q);

    });
} );

// AJAX function to get the trade details and report back to
// the trade_id element
  function tradedetails (id, hp, q) {
  $.ajax({
          type: "GET",
          dataType: 'json',
          url: "/tradedetails?id="+id+"&tradesonly=true",
          success: function(response){
              var tdate = new Date(response.trade_date[id])
              tdate = formatDate(tdate)

              var myvar = '<tr><td>'+tdate+'</td>'
              myvar = myvar + '<td>'+response.trade_asset_ticker[id]+'</td>'
              myvar = myvar + '<td>'+response.trade_operation[id]+'</td>'
              myvar = myvar + '<td>'+response.trade_quantity[id].toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 4, minimumFractionDigits : 4 });+'</td>'
              myvar = myvar + '<td>'+response.trade_price[id].toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 4, minimumFractionDigits : 4 });+'</td>'
              myvar = myvar + '<td>'+response.trade_account[id]+'</td>'
              myvar = myvar + '<td>$'+response.cash_value[id].toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 });+'</td>'
              if (typeof q != "undefined") {
                  myvar = myvar + "<td>"+q.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 4, minimumFractionDigits : 4})+"</td>"
                };

              if (typeof hp != "undefined") {
                  if (hp < 365) {
                      var hptxt = "Short Term"
                  } else {
                      var hptxt = "Long Term"
                  }
                  myvar = myvar + "<td>"+hptxt+" ("+hp+" days)</td>"
              };

              myvar = myvar + "</tr>";
              $('#tradeid_'+id).append(myvar);
                }
        });

    };


function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;

    return [year, month, day].join('-');
}
