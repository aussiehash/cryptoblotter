$(document).ready(function() {
    createcharts(chartjs);
    createcolchart(coldatajs, labelsjs);
    // createhistogram(coldatajs);
} );

// DISABLED FOR NOW. NOT SURE THIS IS USEFUL DATA.
// Not enough data points for a monthly histogram
// function createhistogram(data) {
//         var myChart = Highcharts.chart('histogramchart', {
//             title: {
//             text: 'Histogram & Scatter plot of returns'
//         },
//         xAxis: {
//             title: { text: 'Histogram' },
//             alignTicks: false,
//             opposite: true
//         },
//
//         yAxis: {
//             title: { text: 'Histogram' },
//             opposite: true
//         },
//         series: {
//             name: 'Histogram',
//             type: 'histogram',
//             binsNumber: 30,
//             xAxis: 1,
//             yAxis: 1,
//             data: data,
//             baseSeries: data,
//             zIndex: -1,
//             dataLabels: {
//                 enabled: true,
//                 format: '{point.y:.0f}'
//             },
//             },
//     });
// };


function createcolchart(data, labels) {

        var myChart = Highcharts.chart('colchart', {
            chart: {
            type: 'column'
        },
        title: {
            text: 'Monthly Returns'
        },
        xAxis: {
            categories: labels,
            labels: {
            rotation: 270
        }
        },
        yAxis: {
            labels: {
            rotation: 90
        }
        },
        credits: {
            enabled: false
        },
        series: [{
            name: 'Monthly Return',
            data: data,
            dataLabels: {
                enabled: true,
                format: '{point.y:.2f}%'
            },
            borderWidth: 0,
            tooltip: {
                headerFormat: 'Performance<br/>',
                pointFormat: '{point.y:.2f}%</b>'
            }
        }]


    });
};


function createcharts(data) {

        var myChart = Highcharts.chart('container', {
            exporting: {
                buttons: {
                    contextButton: {
                        align: 'left'
                    }
                }
            },
            credits: {
                text: "CryptoBlotter | HeatMap",
                href: "/home"
            },
            chart: {
                type: 'heatmap',
                marginTop: 60,
                marginBottom: 80,
                plotBorderWidth: 1,

            },
            title: {
                text: 'Portfolio HeatMap'
            },
            subtitle: {
                text: '(monthly returns)'
            },

            legend: {
                align: 'right',
                layout: 'vertical'
            },
            xAxis: {
                categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'EOY']
            },
            yAxis: {
                title: {
                    text: null,
                },
                minPadding: 0,
                maxPadding: 0,
                startOnTick: false,
                endOnTick: false,
                tickWidth: 0.5
            },
            colorAxis: {
                stops: [
                    [0, '#c4463a'],
                    [0.5, '#fffbbc'],
                    [1, '#3060cf']
                    ]
        },

            series: [{
                borderWidth: 0,
                name: 'Monthly Returns',
                data: data,
                dataLabels: {
                    enabled: true,
                },
                tooltip: {
                    headerFormat: 'Performance<br/>',
                    pointFormat: '{point.value:.2f}%</b>'
                }
            }],
            plotOptions:{
                series:{
                    dataLabels:{
                        formatter:function(){
                            if(this.point.value != 0) {
                                var a = this.point.value.toLocaleString('en-US', { style: 'decimal', maximumFractionDigits : 2, minimumFractionDigits : 2 })+"%"
                                // this.point.fontSize = '3px';
                                return a}
                            else {
                                this.point.color = "#DBDBDB"
                            }
                            }
                        }
                    }
                }

        });
};
