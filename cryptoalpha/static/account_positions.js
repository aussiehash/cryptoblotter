$(document).ready( function () {

    var ticker=""
    var account=""
    var dust=""
    var quant=""

    $('.editable').click(function() {
        ticker=($(this).data('ticker'));
        account=($(this).data('account'));
        quant=($(this).data('quant'));
        dust=($(this).data('dust'));
        var dust_html='The account '+account+' holds a dust ammount of '+ticker+'</br>This dust position is: '+quant.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 20, minimumFractionDigits : 5})

            if (dust=='False') {
                $('#editNotDustModal').modal('show');
                $('#modal_nd_account').html(account);
                $('#modal_nd_ticker').html(ticker);
                $('#modal_nd_quant').html(quant.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 18, minimumFractionDigits : 2}));
            } else {
                $('#editDustModal').modal('show');
                // send details to modal
                $('#modal_account').html(account);
                $('#modal_ticker').html(ticker);
                $('#modal_quant').html(quant.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 18, minimumFractionDigits : 2}));
            };
        });

        // Here we start the different functions for dealing with dust / no-dust and user actions

        // When delete Dust button is clicked
        $('#deleteDustButton').click(function() {
            var action="delete_dust"
            $('#editDustModal').modal('hide');
            $('#confirmationModal').modal('show');
            html_show="<h4>Please confirm that DUST will be removed from "+account+"</h4>"+"<p class='text-warning'>All positions in this account will be closed at a price of zero.</p><p class='text-secondary'>This usually doesn't impact the portfolio since dust ammounts are really small but proceed with caution.</p>"
            $('#confirmationText').html(html_show);
            $('#confirmationYES').click(function() {
                $('#confirmationModal').modal('hide');
                // Send Ajax request to server
                arguments="?action="+action+"&from_account="+account+"&quant_before="+quant+"&ticker="+ticker;
                make_adjustments_ajax(arguments);
            });
            });

        // When MOVE Dust button is clicked
        $('#moveDustButton').click(function() {
            var action="move_dust"
            var to_account = $('#inputGroupSelectAccount').val()
            $('#editDustModal').modal('hide');
            $('#confirmationModal').modal('show');
            html_show="<h4>Please confirm that DUST will be moved from "+account+" to "+to_account+"</h4>"+"<p class='text-warning'>Logging a withdraw from one account and a deposit into the other</p>"
            $('#confirmationText').html(html_show);
            $('#confirmationYES').click(function() {
                $('#confirmationModal').modal('hide');
                // Send Ajax request to server
                arguments="?action="+action+"&from_account="+account+"&quant_before="+quant+"&ticker="+ticker+"&to_account="+to_account
                make_adjustments_ajax(arguments);
                });
            });


        // When ADJUST Dust button is clicked
        $('#adjustDustButton').click(function() {
            var action="adjust_dust"
            var to_quant = $('#dust_new_quant').val()
            $('#editDustModal').modal('hide');
            $('#confirmationModal').modal('show');
            html_show="<h4>Please confirm that the "+ticker+" position at account "+account+" is being adjusted from "+quant+" to "+to_quant+"</h4>"+"<p class='text-warning'>This adjustment is being done by logging a purchase or sale at a price of zero</p><p class='text-secondary'>This usually doesn't impact the portfolio since dust ammounts are really small but proceed with caution.</p>"
            $('#confirmationText').html(html_show);
            $('#confirmationYES').click(function() {
                $('#confirmationModal').modal('hide');
                // Send Ajax request to server
                arguments="?action="+action+"&from_account="+account+"&quant_before="+quant+"&ticker="+ticker+"&to_quant="+to_quant
                make_adjustments_ajax(arguments);
                });
            });


        // When ADJUST NOT Dust button is clicked
        $('#adjustNDButton').click(function() {
            var action="position_adjust"
            var to_quant = $('#ND_new_quant').val()
            $('#editNotDustModal').modal('hide');
            $('#confirmationModal').modal('show');
            html_show="<h4>Please confirm that the "+ticker+" position at account "+account+" is being adjusted from "+quant+" to "+to_quant+"</h4>"+"<p class='text-warning'>This adjustment is being done by logging a purchase or sale at a price of zero</p><p class='text-secondary'>This can have significant impact on portfolio performance. Proceed with a lot of caution.</p>"
            $('#confirmationText').html(html_show);
            $('#confirmationYES').click(function() {
                $('#confirmationModal').modal('hide');
                // Send Ajax request to server
                arguments="?action="+action+"&from_account="+account+"&quant_before="+quant+"&ticker="+ticker+"&to_quant="+to_quant
                make_adjustments_ajax(arguments);
                });
            });

        // When MOVE NOT Dust button is clicked
        $('#moveNDButton').click(function() {
            var action="position_move"
            var to_account = $('#inputGroupSelectAccountND').val()
            $('#editNotDustModal').modal('hide');
            $('#confirmationModal').modal('show');
            html_show="<h4>Please confirm that this "+ticker+" position will be moved from "+account+" to "+to_account+"</h4>"+"<p class='text-warning'>Logging a withdraw from one account and a deposit into the other</p>"
            $('#confirmationText').html(html_show);
            $('#confirmationYES').click(function() {
                $('#confirmationModal').modal('hide');
                // Send Ajax request to server
                arguments="?action="+action+"&from_account="+account+"&quant_before="+quant+"&ticker="+ticker+"&to_account="+to_account
                make_adjustments_ajax(arguments);
                });
            });
});

function make_adjustments_ajax(arguments) {
    // Send action details to server via GET
    $.ajax({
        type: 'GET',
        url: "/manage_custody"+arguments,
        dataType: 'json',
        success: function (data) {
            $('#messagealert').html(data+"<br><strong>Reloading page in a moment...</strong>");
            $('#messagealert').show();
            // // Wait a few seconds so message can be read by user
            setTimeout(function(){
                        location.reload()
                    }, 4500);
        },
        });
};
