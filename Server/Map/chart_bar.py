from Server.Process.ActionUser.action_calculate_time import get_color_template
from flask import abort
class TripChart:
    def __init__(self):
        self.color = get_color_template()

    def show_chart(self, trips, input_data):
        """
        """
        qty, weight, volume = trips["Quality"]
        
        label = trips["LabelTripNo"]
        
        capacity = input_data["CapacityFactor"]
        equipment = input_data["EquipmentType"]         
        def role_chart():
            result = []
            title = []  
            if capacity == None or capacity == "":
                abort(400, "Capacity cannot be empty")
            elif capacity == "W":
                result = weight
            elif capacity == "V":
                result = volume
            elif capacity == "Q":
                result = qty
            else:
                return None
            if label == "" or label == None:
                for i in range(0, len(result)):
                    title.append(f"Trip {i+1}")
            else:
                for item in label:
                    title.append(item)
            return result, title

        mode_capacity, title_trip = role_chart()
        html = self.show_bar_chart(mode_capacity, title_trip, equipment)
        return html

    def set_value_title(self, data):
        if len(data) < 10:
            for i in range(len(data), 10):
                data.insert(i, "")
        else:
            return data
        
        return data
        
    def get_value_bar_chart(self, trip, equipment):
        data = {}
        max_column = 0
        max_value = int(max([round(items, 3) for items in trip]))
        
        if equipment == "" or equipment == None:
            equipment = max_value
            
        if int(equipment) > max_value:
            max_column = int(equipment)
        else:
            max_column = int(equipment) + (int(equipment) * 0.2)
            
        data["MaxSize"] = int(max_column)
        data["StepSize"]= int(max_column * 0.2)
        data["MaxSizeUpdate"] = round(int(max_value + max_value * 0.2), -1)
        data["StepSizeUpdate"] = int(data["MaxSizeUpdate"] * 0.2)
        
        return data

    def show_bar_chart(self, trip, title, equipment):
        size = self.get_value_bar_chart(trip, equipment)
        colors = get_color_template()[: len(trip)]
        labels = self.set_value_title(title)
        line_at = "" if equipment == 0 or equipment== "" else equipment
        
        
        css_labels_trip = """
        xAxes:[{
            ticks: {
                maxRotation: 0,
                minRotation: 0,
                padding: 10
            }
        }],"""

        html_content = f"""
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.3/Chart.min.js"></script>
            <script src="https://code.jquery.com/jquery-3.6.4.min.js"></script>
            <script type="text/javascript">
                window.onload = function () {{
                    var ctx = document.getElementById("canvas");
                    function raiseEvent(event,trip) {{
                        result = {{
                            "TripNo": trip,
                            "EventName": event
                        }}
                        window.chrome.webview.postMessage(JSON.stringify(result));
                    }}
                    Chart.pluginService.register({{
                        afterDraw: function (chart) {{
                            if (typeof chart.config.options.lineAt != 'undefined') {{
                                var lineAt = chart.config.options.lineAt;
                                var ctxPlugin = chart.chart.ctx;
                                var xAxe = chart.scales[chart.config.options.scales.xAxes[0].id];
                                var yAxe = chart.scales[chart.config.options.scales.yAxes[0].id];
                                if (yAxe.min != 0) return;
                                ctxPlugin.strokeStyle = "#c40e32";
                                ctxPlugin.beginPath();
                                lineAt = (lineAt - yAxe.min) * (100 / yAxe.max);
                                lineAt = (100 - lineAt) / 100 * (yAxe.height) + yAxe.top;
                                ctxPlugin.moveTo(xAxe.left, lineAt);
                                ctxPlugin.lineTo(xAxe.right, lineAt);
                                ctxPlugin.stroke();
                            }}
                            var ctx = chart.chart.ctx;
                            chart.data.datasets.forEach(function (dataset, i) {{
                                var meta = chart.getDatasetMeta(i);
                                if (!meta.hidden) {{
                                    meta.data.forEach(function (element, index) {{
                                        var position = element.tooltipPosition();
                                        var value = dataset.data[index];
                                        var yAxe = chart.scales[chart.config.options.scales.yAxes[0].id];
                                        var middleY = (element._model.y + yAxe.bottom) / 2;
                                        ctx.fillStyle = 'white'; 
                                        ctx.font = 'bold 10px Arial';
                                        ctx.textAlign = 'center';
                                        ctx.fillText(value, position.x, middleY);
                                    }});
                                }}
                            }});
                        }}
                    }});
                    var myChart = new Chart(ctx, {{
                        type: 'bar',
                        data: {{
                            labels: {labels},
                            datasets: [{{
                                data:{[round(item,3) for item in trip]},
                                backgroundColor:{colors},
                                borderWidth: 2
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            legend: {{
                                display: false
                            }},
                            lineAt:{line_at},
                            scales: {{
                                {css_labels_trip if len(trip) == 1 else ""}
                                yAxes: [{{
                                    ticks: {{
                                        min: 0,
                                        autoSkip: false,
                                        beginAtZero: true,
                                        stepSize:{size["StepSize"]},
                                        max:{size["MaxSize"]}
                                    }}
                                }}]
                            }},
                            onClick: function (e) {{
                                var tripLabels = this.getElementsAtEvent(e)[0]._model.label;
                                var numberTrip = tripLabels.replace("Trip", "").trim();
                                numberTrip=numberTrip.replace("#","")
                                raiseEvent("TRIP_CLICK", numberTrip)
                            }},
                            onResize: function (chart, size) {{
                                if (chart.height > 300) {{
                                    chart.options.lineAt = {line_at};
                                    chart.options.scales.yAxes[0].ticks.max = {size["MaxSizeUpdate"]};
                                    chart.options.scales.yAxes[0].ticks.stepSize = {size["StepSizeUpdate"]};
                                    chart.update();
                                }}
                                else {{
                                    chart.options.lineAt = {line_at};
                                    chart.options.scales.yAxes[0].ticks.max = {size["MaxSize"]};
                                    chart.options.scales.yAxes[0].ticks.stepSize = {size["StepSize"]};
                                    chart.update();
                                }}
                            }}
                        }},
                    }});
                    function onDoubleClick(e) {{
                        var tripLabels = myChart.getElementsAtEvent(e)[0]._model.label;
                        var numberTrip = tripLabels.replace("Trip", "").trim();
                        numberTrip = numberTrip.replace("#", "")
                        raiseEvent("TRIP_DOUBLE_CLICK", numberTrip)
                    }}
                    ctx.oncontextmenu = onDoubleClick;
                }}

            </script>
            <style>
                .chart-container {{
                    width: 100%;
                    height: 95vh;
                }}
                canvas {{
                    width: 100% !important;
                    height: 100% !important;
                }}
            </style>
        </head>
            <body>
                <div class="chart-container">
                    <canvas id="canvas"></canvas>
                </div>
            </body>
        </html>
        """
        return html_content
