
$(document).ready(function() {
    console.log("-------------");
    console.log("00000080   01 04 45 54 68 65 20 54  69 6D 65 73 20 30 33 2F   ..EThe Times 03/");
    console.log("00000090   4A 61 6E 2F 32 30 30 39  20 43 68 61 6E 63 65 6C   Jan/2009 Chancel");
    console.log("000000A0   6C 6F 72 20 6F 6E 20 62  72 69 6E 6B 20 6F 66 20   lor on brink of ");
    console.log("000000B0   73 65 63 6F 6E 64 20 62  61 69 6C 6F 75 74 20 66   second bailout f");
    console.log("000000C0   6F 72 20 62 61 6E 6B 73  FF FF FF FF 01 00 F2 05   or banksÿÿÿÿ..ò.");
    console.log("--------------");

    // Format Red and Green Numbers (negative / positive)
    $("td.redgreen").removeClass('red');
    $("td.redgreen").addClass('green');
    $("td.redgreen:contains('-')").removeClass('green');
    $("td.redgreen:contains('-')").addClass('red');

    // Show / hide small and closed positions on button click
    $('.small_pos').toggle(100);
    $('.lifo_costtable').toggle();

    $('#myonoffswitch').on('click',function(){
		$('.small_pos').toggle(100);
    });

    $('#myfifolifoswitch').on('click',function(){
		$('.fifo_costtable').toggle();
        $('.lifo_costtable').toggle();
        $('#acc_method').html(function(i, text){
         return text === 'Method: LIFO (Last-in First-Out)' ? 'Method: FIFO (First-in First-Out)' : 'Method: LIFO (Last-in First-Out)';
         });

	});


    // Grab Portfolio Statistics from JSON and return to table
    $.ajax({
        type: 'GET',
        url: '/portstats',
        dataType: 'json',
        success: function (data) {
            createcharts(); //Load pie chart
            $('#end_nav').html(data.end_nav.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 }));
            var max_nav_txt = data.max_nav.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 }) + "<span class='small'> on "
            max_nav_txt = max_nav_txt + data.max_nav_date + "</span>"
            $('#max_nav').html(max_nav_txt);
            var min_nav_txt = data.min_nav.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 }) + "<span class='small'> on "
            min_nav_txt = min_nav_txt + data.min_port_date + "</span>"
            $('#min_nav').html(min_nav_txt);
            $('#end_portvalue').html("$ "+data.end_portvalue.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 0, minimumFractionDigits : 0 }));
            var max_pv_txt = "$ " + data.max_portvalue.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 0, minimumFractionDigits : 0 }) + "<span class='small'> on "
            max_pv_txt = max_pv_txt + data.max_port_date + "</span>"
            $('#max_portvalue').html(max_pv_txt);
            $('#return_1d').html((data.return_1d*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+"%");
            $('#return_1wk').html((data.return_1wk*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+"%");
            $('#return_30d').html((data.return_30d*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+"%");
            $('#return_90d').html((data.return_90d*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+"%");
            $('#return_ATH').html((data.return_ATH*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+"%");
            $('#return_SI').html((data.return_SI*100).toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+"%");
            var stats_dates_txt = data.start_date+" to "+data.end_date
            $('#stats_dates_txt').html(stats_dates_txt);

            // re-apply redgreen filter (otherwise it's all assumed positive since fields were empty before ajax)
            $("td.redgreen").removeClass('red');
            $("td.redgreen").addClass('green');
            $("td.redgreen:contains('-')").removeClass('green');
            $("td.redgreen:contains('-')").addClass('red');
        }
        });

    getblockheight();

    // Get NAV Data for chart
    $.ajax({
        type: 'GET',
        url: '/navchartdatajson',
        dataType: 'json',
        success: function (data) {
            navChart(data);
        }
        });


});


function getblockheight() {
    // GET latest Bitcoin Block Height
    $.ajax({
        type: 'GET',
        url: 'https://blockexplorer.com/api/status?q=getBlockCount',
        dataType: 'jsonp',
        timeout: 5000,
        success: function (data) {
            $('#latest_btc_block').html(data.info.blocks.toLocaleString('en-US', {style: 'decimal', maximumFractionDigits : 0, minimumFractionDigits : 0 }));
        },
        error: function () {
            getblockheight();
            }
            });
}

// Pie Chart - allocation
function createcharts() {

    // Create the plot data
    chartdata = piechartjs

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
                text: "Portfolio Allocation",
                style: {
                        "fontSize": "12px"
                },
            },
            tooltip: {
                pointFormat: '{series.name}: <b>{point.percentage:.0f}%</b>'
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
                size: '70%',
                innerSize: '50%',
                dataLabels: {
                    enabled: true,
                    align: 'left',
                    allowOverlap: true,
                    format: '{point.name} {point.y:.0f}%',
                    connectorPadding: 1,
                    distance: 1,
                    softConnector: true,
                    crookDistance: '20%'
                },
            }]
            });

            myChart.reflow();

    };


// NAV CHART
function navChart(data) {
        var myChart = Highcharts.stockChart('navchart', {
            credits: {
                text: "click here for detailed historical chart",
                style: {
                    fontSize: '13px',
                    color: '#da5526'
                },
                position: {
                    align: 'right',
                    y: 0
                },
                href: "/navchart"
            },
            navigator: {
                enabled: false
            },
            rangeSelector: {
                selected: 1
            },
            chart: {
                zoomType: 'x',
                backgroundColor:"#FAFAFA",
            },
            title: {
                text: 'Portfolio NAV over time'
            },
            subtitle: {
                text: document.ontouchstart === undefined ?
                        'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
            },
            xAxis: {
                type: 'datetime'
            },
            yAxis: {
                title: {
                    text: 'NAV'
                }
            },
            legend: {
                enabled: false
            },
            plotOptions: {
                area: {
                    fillColor: {
                        linearGradient: {
                            x1: 0,
                            y1: 0,
                            x2: 0,
                            y2: 1
                        },
                        stops: [
                            [0, Highcharts.getOptions().colors[0]],
                            [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                        ]
                    },
                    marker: {
                        radius: 2
                    },
                    lineWidth: 1,
                    states: {
                        hover: {
                            lineWidth: 1
                        }
                    },
                    threshold: null
                }
            },

            series: [{
                type: 'line',
                name: 'NAV',
                // The line below maps the dictionary coming from Python into
                // the data needed for highcharts. It's weird but the *1 is
                // needed, otherwise the date does not show on chart.
                data: Object.keys(data).map((key) => [((key*1)), data[key]]),
                turboThreshold: 0,
                tooltip: {
                    pointFormat: "NAV (first trade=100): {point.y:,.0f}"
                }
            }]
        });

};
