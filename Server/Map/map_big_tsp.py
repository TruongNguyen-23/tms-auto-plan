from dotenv import load_dotenv
import os
class ManyRoutePoint:
    def __init__(self):
        load_dotenv()
        self.api_Key = os.getenv("API_KEY")
    def showManyContent(self,point,data):
        _point = [[float(item[0]),float(item[1])] for item in point]
        _data = [{'lat':float(item['lat']),'lng':float(item['lng'])} for item in data]
        html = f"""
        <!DOCTYPE html>
            <html>
            <head>
                <title>Route TSP</title>
                <script src="https://maps.googleapis.com/maps/api/js?key={self.api_Key}&libraries=geometry&callback=initMap" async defer"></script>
                <script>
                   const start_Point={_point[0][0]}
                    const end_Point={_point[0][1]}
                    function initMap() {{
                        const service = new google.maps.DirectionsService;
                        const station={_data}
                        const map = new google.maps.Map(document.getElementById('map'), {{
                            center: {{lat: 10.813975039910598, lng: 106.64436107457777}},
                            zoom: 11
                        }});
                        {_point}.forEach(function (point,index) {{
                            var marker = new google.maps.Marker({{
                                position: new google.maps.LatLng(point[0], point[1]),
                                map: map,
                                label: (index + 1).toString()
                            }});
                        }});
                        for (var i = 0, parts = [], max = 25 - 1; i < station.length; i = i + max)
                            parts.push(station.slice(i, i + max + 1));

                        var service_callback = function (response, status) {{
                            if (status != 'OK') {{
                                console.log('Directions request failed due to ' + status);
                                return;
                            }}
                            var renderer = new google.maps.DirectionsRenderer;
                            renderer.setMap(map);
                            renderer.setOptions({{ suppressMarkers: true, preserveViewport: true }});
                            renderer.setDirections(response);
                        }};
                        for (var i = 0; i < parts.length; i++) {{
                            var waypoints = [];
                            for (var j = 1; j < parts[i].length - 1; j++)
                                waypoints.push({{ location: parts[i][j], stopover: false }});
                            var service_options = {{
                                origin: parts[i][0],
                                destination: parts[i][parts[i].length - 1],
                                waypoints: waypoints,
                                travelMode: 'WALKING'
                            }};
                            service.route(service_options, service_callback);
                        }}
                    }}
                </script>
            </head>
            <body onload="initMap()">
                <style>
                    html,
                     body {{
                        height: 100%;
                        margin: 0;
                        padding: 0;
                    }}
                </style>
                <div id="map" style="height: 100%; width: 100%;"></div>
            </body>
            </html>
        """
        return html
    
    
 