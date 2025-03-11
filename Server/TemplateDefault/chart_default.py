class TripChartDefault:
    def __init__(self):
        print('Trip Chart')
    def show_chart_bar(self):
        html = f"""
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.3/Chart.min.js"></script>
            <script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
            <script type="text/javascript">
                // $(document).ready(function () {{
                //    $('body').scrollTop(1000);
                //}});
                window.onload = function () {{
                    var ctx = document.getElementById("canvas");
                    var myChart = new Chart(ctx, {{
                        type: 'bar',
                        data: {{
                            datasets: [{{
                                borderWidth: 2
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            legend: {{
                                display: false
                            }},
                            scales: {{
                                yAxes: [{{
                                    ticks: {{
                                        autoSkip: false,
                                        beginAtZero: true,
                                    }}
                                }}]
                            }}
                        }},
                    }});
                }}

            </script>
        </head>
            <body>
                <canvas id="canvas"></canvas>
                    <style>
                    #canvas {{
                        width: 100% !important;
                        height: 100% !important;
                        position: relative;
                    }}
                    </style>
            </body>
        </html>
        """
        return html
