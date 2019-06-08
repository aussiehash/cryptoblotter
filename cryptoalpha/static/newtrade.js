$(document).ready(function() {
    hideandshow();
    calccf();
    $('#submit_button').hide()
});


$(function() {
    $('#submit_button').click(function(){
        var $this = $(this);
        $('#submit_button').hide()
        $('#submit_button').attr('value', 'Please wait. Including transaction...');


    });
});

$(function() {
    $("#tradeaccount").autocomplete({
      source: function( request, response) {
        $.ajax( {
                  url: "/aclst?",
                  dataType: "json",
                  data: {
                    term: request.term
                  },

                  success: function( data ) {
                      response($.map(data, function(item) {
                          return {
                            label: item,
                            value: item
                          }
                    }));
                }

                });
            },
                minLength: 2
            });
        });

$(function() {
    $("#cashaccount").autocomplete({
      source: function( request, response) {
        $.ajax( {
                  url: "/aclst?",
                  dataType: "json",
                  data: {
                    term: request.term
                  },

                  success: function( data ) {
                      response($.map(data, function(item) {
                          return {
                            label: item,
                            value: item
                          }
                    }));
                }

                });
            },
                minLength: 2
            });
        });



$( function() {
    $("#tickerauto").autocomplete({
      source: function(request, response) {
        $.ajax( {
          url: "/cryptolist?json=true&q=&",
          dataType: "json",
          data: {
            term: request.term
          },

          success: function( data ) {
              response($.map(data, function(item) {
                  return {
                    label: item.symbol+" | "+item.name,
                    value: item.symbol
                  }
              }));
          }
        } );
      },
      minLength: 2
    } );
  } );


function hideandshow() {

              if($('#trade_select').val() == '1') {
                  $('#trade_asset_ticker').show();
                  $('#trade_operation').show();
                  $('#trade_quantity').show();
                  $('#trade_price').show();
                  $('#trade_fees').show();
                  $('#trade_account').show();
                  $('#cash_account').show();
                  $('#trade_notes').show();
                  $('#cash_value').show();
                  $('#submit').show();
                  $('#cash').prop("readonly",true);
                  $('#BSDW').html(' \
                    <option value="B">Buy</option> \
                    <option value="S">Sell</option> \
                  ');

                  $('#transdesc').text('You are buying or selling something and withdrawing or depositing cash. \
                  Asset and Cash Transactions have two transactions \
                  (one for the purchase or sale; another for the cash withdraw or deposit).\
                   Please note that two transactions will be included in the database.');

                   $('#submit_button').show()


              } else if ($('#trade_select').val() == '2') {
                  $('#trade_asset_ticker').show();
                  $('#trade_operation').show();
                  $('#trade_quantity').show();
                  $('#trade_price').show();
                  $('#trade_fees').show();
                  $('#trade_account').show();
                  $('#cash_account').hide();
                  $('#trade_notes').show();
                  $('#cash_value').hide();
                  $('#submit').show();
                  $('#cash').prop("readonly",true);
                  $('#BSDW').html(' \
                    <option value="B">Buy</option> \
                    <option value="S">Sell</option> \
                    <option value="D">Deposit</option> \
                    <option value="W">Withdraw</option> \
                  ');
                  $('#transdesc').text('You are buying something but cash is not debited from any account. Only one transaction is included in the database (i.e. Bought 0.05 BTC from account XYZ)');
                  $('#submit_button').show()

              } else if ($('#trade_select').val() == '3') {
                  $('#trade_asset_ticker').hide();
                  $('#trade_operation').show();
                  $('#trade_quantity').hide();
                  $('#trade_price').hide();
                  $('#trade_fees').hide();
                  $('#trade_account').hide();
                  $('#cash_account').show();
                  $('#trade_notes').show();
                  $('#cash_value').show();
                  $('#submit').show();
                  $('#BSDW').html(' \
                    <option value="D">Deposit</option> \
                    <option value="W">Withdraw</option> \
                  ');
                  $('#cash').prop("readonly",false);
                  $('#transdesc').text('This is a cash only transaction (i.e. cash is being deposited or witdrawn from account XYZ.)');
                  $('#submit_button').show()

              } else {
                  $('#trade_asset_ticker').hide();
                  $('#trade_operation').hide();
                  $('#trade_quantity').hide();
                  $('#trade_price').hide();
                  $('#trade_fees').hide();
                  $('#trade_account').hide();
                  $('#cash_account').hide();
                  $('#trade_notes').hide();
                  $('#cash_value').hide();
                  $('#cash').prop("readonly",true);
                  $('#submit').hide();
                  $('#transdesc').text('PLEASE CHOOSE AN OPTION');
                  $('#submit_button').hide()

              }


}


  $(function() {
      $('#trade_select').change(function(){
          hideandshow();
      });
  });

function calccf() {

    var q = 0
    var p = 0
    var f = 0

    q = parseFloat($('#quant').val());
    p = parseFloat($('#price').val());
    f = parseFloat($('#fees').val());

    fin = (q * p) + f
    if (isNaN(fin)) {
        fin = 0
    }

    // fin = fin.value().toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })
    $('#cash').val("$"+fin.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2}));

}

  $(function() {
      $('#trade_select, #trade_price, #trade_fees, #trade_quantity, #trade_operation').change(function(){
        calccf();
      });
  });
