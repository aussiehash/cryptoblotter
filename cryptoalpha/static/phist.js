$(document).ready(function() {
    $('table.display').DataTable({
        "scrollY":        "400px",
        "scrollCollapse": true,
        "paging":         false,
        "order": [[ 0, "desc" ]],

        columnDefs: [
    {
        targets: [0,1,2,3,4],
        className: 'dt-body-right dt-head-center'
    }]
    });

    createcharts(chartjs);
} );


function createcharts(data) {

        var myChart = Highcharts.chart('navchart', {
            credits: {
                text: "CryptoBlotter | Historical Portfolio Chart",
                href: "/home"
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
                data: data,
                turboThreshold: 0
            }]
        });


        var myChart = Highcharts.chart('portchart', {
            credits: {
                text: "CryptoBlotter | Historical Portfolio Chart",
                href: "/home"
            },
            chart: {
                zoomType: 'x',
                backgroundColor:"#FAFAFA",
            },
            title: {
                text: 'Portfolio Value over time (in USD)'
            },
            subtitle: {
                text: document.ontouchstart === undefined ?
                        'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
            },
            xAxis: {
                type: 'category',
                tickInterval: 30,
                labels: {
                rotation: 270
                }
            },
            yAxis: {
                title: {
                    text: 'Portfolio Value'
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
                type: 'column',
                name: 'Portfolio Value',
                data:   Object.keys(phistoryjs)
                        .map((key) => [(key), phistoryjs[key]]),
                turboThreshold: 0
            }]

            
        });


};
