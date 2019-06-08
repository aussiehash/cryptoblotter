// Start the dataTables function
$(document).ready( function () {
    $('#portfoliohistory').DataTable( {
        "order" : [0, 'desc']
    });
    test_ajax();
} );


$(function(){
  $('#expand').on('hide.bs.collapse', function () {
    $('#button').html('<span class="glyphicon glyphicon-collapse-down"></span> Show');
  })
  $('#expand').on('show.bs.collapse', function () {
    $('#button').html('<span class="glyphicon glyphicon-collapse-up"></span> Hide');
  })
})

function test_ajax () {
console.log("Here");
$.ajax({
        type: "GET",
        dataType: 'json',
        url: "/portfoliohistory?json=true",
        success: function(data){
            console.log("Success");
            createcharts(data);
        }
});

};


function createcharts(datachart) {

    data = datachart;

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
                data: data
            }]
        });
};
