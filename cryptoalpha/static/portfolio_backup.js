
$(document).ready(function() {

    console.log("-------------------------------");
    console.log("Page Loaded");
    console.log("Starting jQuery Portfolio function");
    console.log("-------------------------------");
    $('#storage').data("chartdone", false);
    // Start the dataTables function
    $(document).ready( function () {
        $('#transactionstable').DataTable();
    } );

    // Grab BTC Prices and store
    var id = "1";
    $.ajax({
        type: 'GET',
        url: 'https://api.coinmarketcap.com/v2/ticker/' + id + '/',
        dataType: 'json',
        success: function (data) {
            $('#storage').data("btcprice", data.data.quotes.USD.price);
            $('#storage').data("btc24chg", data.data.quotes.USD.percent_change_24h);
            $('#storage').data("lastupd", data.data.last_updated);
        }
    });


    populateprices();

    setInterval(function () {
        populateprices();
    },60000);

    var notload = true;

    setInterval(function () {
        var sumprod = 0;


        $('#portfolio tr').each(function () {
            var ticker = $(this).children("th").html();
            var pos = $('#position'+ticker).data('position');
            var pct = (pos / $('#storage').data('portfolio')) * 100

            if(isNaN(pct)) {
            notload = true;
            } else {
                notload = false;
                $('#percent'+ticker).html(pct.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2})+'%');
                sumprod = sumprod + (pos * ($('#chg24'+ticker).data('chg')));
            }
            $("td.redgreen").removeClass('red');
            $("td.redgreen").addClass('green');
            $("td.redgreen:contains('-')").removeClass('green');
            $("td.redgreen:contains('-')").addClass('red');
        });


        if (notload == false) {
            var tmp = $('#storage').data('portfolio').toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 0, minimumFractionDigits : 0});
            $('#pvalue').html("$"+tmp);
            var tmp2 = ($('#storage').data('portfolio') * 100);
            $('#chg1').html((sumprod/tmp2*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2})+'%');
            $('#chg2').html("$"+(tmp2/10000*(sumprod/tmp2*100)).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2}));
            var tmp3 = (tmp2/100/($('#storage').data('btcprice')));
            $('#pvaluebtc').html("\u0E3F"+tmp3.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2}));
            var tmp4 = ($('#storage').data('lastupd'))*1000;
            tmp4 = new Date(tmp4);
            $('#lstupd').html(tmp4.toLocaleString("en-US"));

            createcharts();

        };


    },1000);

});

// Function to update prices for the Table
// Source of prices is CoinMarketCap API
// This also updates price dependent data on the portfolio table

function populateprices() {
        $('#portfolio tr').each(function () {
            $('#storage').data("portfolio", 0);

            var ticker = $(this).children("th").html();
            var id = $(this).attr('id');
                $.ajax({
                type: 'GET',
                url: 'https://api.coinmarketcap.com/v2/ticker/' + id + '/',
                dataType: 'json',
                success: function (data) {
                    var price = data.data.quotes.USD.price;
                    var pricef = price.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 4, minimumFractionDigits : 4 });
                    var hourChanges = data.data.quotes.USD.percent_change_1h;
                    var dayChanges =  data.data.quotes.USD.percent_change_24h;
                    var weekChanges = data.data.quotes.USD.percent_change_7d;
                    var lastupdate = data.data.last_updated
                    var image = "";

                    if (dayChanges > .50 && dayChanges < 9) {
                        image = '<img src="static/images/btc_up.png" width="10" height="10" ></img>';
                    }
                    else if (dayChanges < -.50 && dayChanges > -9) {
                        image = '<img src="static/images/btc_down.png" width="10" height="10" ></img>';
                    }
                    else if (dayChanges <= -9) {
                        image = '<img src="static/images/btc_crash.gif" width="15" height="15" ></img>';
                    }
                    else if (dayChanges >= 9.00) {
                        image = '<img src="static/images/mooning.gif" width="45" height="45" ></img>';
                    }
                    else {
                        image = '<img src="static/images/btc_straight.png" width="15" height="15" ></img>';
                    }

                    $('#img'+ticker).html(image);
                    $('#price'+ticker).html(`${pricef}`);
                    $('#chg24'+ticker).html(dayChanges.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2})+"%");


                    var quantity = $('#quantity'+ticker).text().replace(/,/g, '');
                    var pos = quantity * price;
                    pfolio = $('#storage').data('portfolio')
                    pfolio = pfolio + pos
                    $('#storage').data("portfolio", pfolio);

                    $('#position'+ticker).html("$"+pos.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 0, minimumFractionDigits : 0 }));
                    $('#position'+ticker).data("position",pos);
                    $('#chg24'+ticker).data("chg", dayChanges);
                    var tmp = $('#storage').data('portfolio').toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 0, minimumFractionDigits : 0});
                    $('#pvalue').html("$"+tmp);

                    var qbuys = parseFloat($('#cost'+ticker).data('qbuys'));
                    var qsells = parseFloat($('#cost'+ticker).data('qsells'));
                    var buynotional = parseFloat($('#cost'+ticker).data('buynotional'));
                    var sellnotional = parseFloat($('#cost'+ticker).data('sellnotional'));
                    var fees = parseFloat($('#cost'+ticker).data('fees'));
                    var cost = (buynotional + sellnotional - fees) / (qbuys + qsells);
                    var ret = ((price / cost) - 1) * 100;

                    var pnl = pos - buynotional - sellnotional - fees;

                    $('#cost'+ticker).html(cost.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 0, minimumFractionDigits : 0 }));
                    $('#return'+ticker).html(ret.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+"%");
                    $('#fees'+ticker).html("$"+(fees).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 }));
                    $('#pnl'+ticker).html("$"+(pnl).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 0, minimumFractionDigits : 0 }));
                }
              });

            });

};


function createcharts() {

    // Create the plot data
    chartdata = []

    if ($('#storage').data('chartdone') == false) {

        $('#storage').data("chartdone", true);
        $('#portfolio tr').each(function () {
            var ticker = $(this).children("th").html();
            var pos = $('#position'+ticker).data('position');
            var pct = (pos / $('#storage').data('portfolio')) * 100

            notload2 = false;
            tmp = {};
            var allocation = pct;
            tmp["name"] = ticker;
            tmp["y"] = allocation;
            chartdata.push(tmp);

            var myChart = Highcharts.chart('piechart', {
            credits: {
                text: "CryptoBlotter | Allocation"
            },
            legend: {
                enabled: false
            },
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                width: 400,
                backgroundColor:"#FAFAFA",
                // Edit chart spacing
                spacingBottom: 0,
                spacingTop: 0,
                spacingLeft: 0,
                spacingRight: 0,

                type: 'pie'
            },
            title: {
                text: false
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: true,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true
                    },
                    showInLegend: true
                }
            },
            series: [{
                name: 'Allocation',
                colorByPoint: true,
                data: chartdata
            }]
            });
    });
    };



}
