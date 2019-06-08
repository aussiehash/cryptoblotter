
$(document).ready(function() {
    console.log("----H-O-D-L----");
    console.log("00000080   01 04 45 54 68 65 20 54  69 6D 65 73 20 30 33 2F   ..EThe Times 03/");
    console.log("00000090   4A 61 6E 2F 32 30 30 39  20 43 68 61 6E 63 65 6C   Jan/2009 Chancel");
    console.log("000000A0   6C 6F 72 20 6F 6E 20 62  72 69 6E 6B 20 6F 66 20   lor on brink of ");
    console.log("000000B0   73 65 63 6F 6E 64 20 62  61 69 6C 6F 75 74 20 66   second bailout f");
    console.log("000000C0   6F 72 20 62 61 6E 6B 73  FF FF FF FF 01 00 F2 05   or banksÿÿÿÿ..ò.");
    console.log("----H-O-D-L----");

    $('#storage').data("chartdone", false);
    $('#storage').data("custodydone", false);
    // Start the dataTables function

    // Hide small positions on the Tables
    $(function() {
        $('#showsmall').click(function(){
        var $rowsNo = $('#positionstable tbody tr').filter(function () {
           return $.trim($(this).find('td').eq(11).text()) === "---"
        }).toggle();

        var table_look = $('#custodytable');
        var idx = table_look.find('th.total0').index();

        var $rowsNo = $('#custodytable tbody tr').filter(function () {
           return $.trim($(this).find('td').eq(idx-1).text()) === "0.0000"
        }).toggle();

        });
    });

    // DataTables Initialization
    $('#transactionstable').DataTable( {
            "order" : [0, 'desc']
        });

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


    // Grab Portfolio Stats and place on table
    $.ajax({
        type: 'GET',
        url: '/portstats',
        dataType: 'json',
        success: function (data) {
            // $('#storage').data("btcprice", data.data.quotes.USD.price);
            // $('#storage').data("btc24chg", data.data.quotes.USD.percent_change_24h);
            // $('#storage').data("lastupd", data.data.last_updated);
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
            sumcustody();

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
                        image = '<img src="static/images/btc_crash.png" width="15" height="20" ></img>';
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
                    if (ret < -99) {
                        ret = "---"
                        cost = "---"
                        $('#return'+ticker).html(ret.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 }));
                        $('#cost'+ticker).html(cost.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 0, minimumFractionDigits : 0 }));
                    } else {
                        $('#return'+ticker).html(ret.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+"%");
                        $('#cost'+ticker).html(cost.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 0, minimumFractionDigits : 0 }));
                    }

                    var pnl = pos - buynotional - sellnotional - fees;

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

        // Hide empty or small balances on tables:
        var $rowsNo = $('#positionstable tbody tr').filter(function () {
           return $.trim($(this).find('td').eq(11).text()) === "---"
        }).toggle();




        $('#portfolio tr').each(function () {
            var ticker = $(this).children("th").html();
            var pos = $('#position'+ticker).data('position');
            var pct = (pos / $('#storage').data('portfolio')) * 100
            if (pct > 0.009) {
            tmp = {};
            var allocation = pct;
            tmp["name"] = ticker;
            tmp["y"] = allocation;
            chartdata.push(tmp);
            };

            var myChart = Highcharts.chart('piechart', {
            credits: {
                text: "",
                href: ""
            },
            legend: {
                enabled: false
            },
            chart: {
                plotBackgroundColor: null,

                backgroundColor:"#FAFAFA",
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
                data: chartdata,
                size: '90%',
                innerSize: '70%',
                dataLabels: {
                    enabled: true,
                    align: 'right',
                    allowOverlap: false,
                    distance: 20,
                    padding: 0,
                    x:  3,
                    y: -4,
                    format: '{point.name} : {point.y:.2f}%'
                },
            }]
            });

            myChart.reflow();

    });
    };



}

function sumcustody () {
    if ($('#storage').data('custodydone') == false) {
        $('#storage').data("custodydone", true);

    $('tr').each(function () {
       //the value of sum needs to be reset for each row, so it has to be set inside the row loop
       var fx = false;
       var sum = 0;
       //find the combat elements in the current row and sum it
       $(this).find('.position').each(function () {
           var txt = $(this).text();
           if (txt.indexOf('$') != -1) {
                fx = true;
            }

           var position = $(this).text().replace(/,/g, '').replace('$', '');
           if (!isNaN(position) && position.length !== 0) {
               sum += parseFloat(position);
           }
       });
       //set the value of currents rows sum to the total-combat element in the current row
       if (fx == true) {
           $('.total-position', this).html("$ "+sum.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 }));
        } else {
            $('.total-position', this).html(sum.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 4, minimumFractionDigits : 4 }));
        }

        var table_look = $('#custodytable');
        var idx = table_look.find('th.total0').index();

        var $rowsNo = $('#custodytable tbody tr').filter(function () {
           return $.trim($(this).find('td').eq(idx-1).text()) === "0.0000"
        }).toggle();


    });



};
};
