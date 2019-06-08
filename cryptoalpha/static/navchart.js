$(document).ready(function() {
    console.log (portchartjs);
    createcharts(navchartjs);
} );

function createcharts(data) {

        var myChart = Highcharts.stockChart('portchart', {
            credits: {
                text: "CryptoBlotter | Historical Portfolio Chart"
            },
            chart: {
                zoomType: 'x',
                backgroundColor:"#FAFAFA",
            },
            rangeSelector: {
                selected: 2
            },
            title: {
                text: 'Portfolio Value over time'
            },
            subtitle: {
                text: document.ontouchstart === undefined ?
                        'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
            },
            xAxis: [
                {type: 'datetime',
                id: 'x1'
                },
                {type: 'datetime',
                id: 'x2'
                },
            ],
            yAxis: [
                {
    		        title: {
    		            text: 'NAV'
    		        },
                    height: '35%',
                    lineWidth: 2,
                    opposite: true
    		    },
                {
		        title: {
		            text: 'Portfolio Market Value and Cost Basis'
		        },
		        lineWidth: 4,
                top: '35%',
                height: '35%',
                offset: 0
		    }, {
		        title: {
		            text: 'PnL compared to Cost basis'
		        },
	            lineWidth: 2,
                top: '70%',
                height: '30%',
                offset: 0,
                opposite: true
		    }],
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


            series: [
                {
                    type: 'line',
                    name: 'NAV [100 = first trade date]',
                    yAxis: 0,
                    // The line below maps the dictionary coming from Python into
                    // the data needed for highcharts. It's weird but the *1 is
                    // needed, otherwise the date does not show on chart.
                    data: Object.keys(navchartjs).map((key) => [((key*1)), navchartjs[key]]),
                    turboThreshold: 0,
                    tooltip: {
                        pointFormat: "NAV (first trade=100): {point.y:,.0f}"
                    },
                },
                {
                    type: 'line',
                    name: 'Portfolio Value',
                    yAxis: 1,
                    // The line below maps the dictionary coming from Python into
                    // the data needed for highcharts. It's weird but the *1 is
                    // needed, otherwise the date does not show on chart.
                    data: Object.keys(portchartjs['PORT_usd_pos']).map((key) => [((key*1)), portchartjs['PORT_usd_pos'][key]]),
                    turboThreshold: 0,
                    tooltip: {
                        pointFormat: "Portfolio Market Value: ${point.y:,.0f}"
                    },
                },
                {
                    type: 'line',
                    name: 'Cost Basis',
                    yAxis: 1,
                    // The line below maps the dictionary coming from Python into
                    // the data needed for highcharts. It's weird but the *1 is
                    // needed, otherwise the date does not show on chart.
                    data: Object.keys(portchartjs['PORT_ac_CFs']).map((key) => [((key*1)), portchartjs['PORT_ac_CFs'][key]]),
                    turboThreshold: 0,
                    tooltip: {
                        pointFormat: "Portfolio Cost Basis: ${point.y:,.0f}"
                    },
                },
                {
                    type: 'column',
                    name: 'PnL compared to Cost basis',
                    yAxis: 2,
                    // The line below maps the dictionary coming from Python into
                    // the data needed for highcharts. It's weird but the *1 is
                    // needed, otherwise the date does not show on chart.
                    data: Object.keys(portchartjs['ac_pnl']).map((key) => [((key*1)), portchartjs['ac_pnl'][key]]),
                    turboThreshold: 0,
                    tooltip: {
                        pointFormat: "PnL compared to Cost Basis: ${point.y:,.0f}"
                    },
                }
            ]
        });


};
