from Server.Process.Handle.handle_file import render_content_file_HTML,save_file
from dotenv import load_dotenv
import os
class MapTripLocation:
    def __init__(self):
        load_dotenv()
        self.api_Key = os.getenv("API_KEY")
    def handle_data(self, data, file_name):
        user_id = data["UserID"]
        trip = data["TripNo"]
        trip = f"Trip #{trip}"   
        template_string = ""
        
        with open(f'Server\TemplateDefault\ClusterCache\cluster{user_id}.html', 'r') as f:
            template = f.read()
            template_string = template
            
        insertion = f"""
            var numberTrip = tripNo.indexOf("{trip}");
            var boundsTrip = new google.maps.LatLngBounds();
            number = numberTrip;
            if (numberTrip || numberTrip == 0){{
                (points[numberTrip].length === 1 ? [points[numberTrip][0]] : points[numberTrip]).forEach(function (item) {{
                    makerLat= markerViewBackground.position.lat
                    makerLon= markerViewBackground.position.lng
                    latPoint = item[1];
                    lonPoint = item[2];
                    if (parseFloat(latPoint) == makerLat && parseFloat(lonPoint) == makerLon) 
                    {{
                        if (point.length == 1) {{
                            infoWindows[numberTrip].open(map, markerViewBackground);
                            var location_trip = new google.maps.LatLng(latPoint, lonPoint);
                            map.setCenter(location_trip);
                            map.setZoom(10);
                        }}
                        else {{
                            var unique = point.filter(onlyUnique);
                            if (unique.length == 1) {{
                                infoWindows[numberTrip].open(map, markerViewBackground);
                                setZoom(boundsTrip, unique)
                            }}
                            else{{
                                // unique.forEach(function(item,index){{
                                //     boundsTrip.extend(new google.maps.LatLng(parseFloat(item[1]), parseFloat(item[2])));
                                //     map.fitBounds(boundsTrip);
                                // }})
                                //hide maker center cricle
                                var pointCenter = new google.maps.LatLng(centerCricle[numberTrip][0], centerCricle[numberTrip][1]);
                                var markerCenter = new google.maps.Marker({{
                                    position: pointCenter,
                                    map: map,
                                }});
                                map.setCenter(pointCenter);
                                map.setZoom(10);
                                markerCenter.setVisible(false);
                                infoWindows[numberTrip].open(map, markerCenter);
                            }}
                        }}
                        // var infoMaker = new google.maps.InfoWindow({{content: contentInfoMaker(location)}});
                        // infoMaker.open(map, markerViewBackground);
                    }}
                }})
            }}
        """
        cmd_data = ""
        cmd_bounds = "bounds.extend(new google.maps.LatLng(location[1], location[2]));"
        cmd_map_bounds = "map.fitBounds(bounds);"
        content = template_string.replace('<!-- GET_LOCATION -->', insertion)
        content = content.replace(cmd_bounds, cmd_data)
        content = content.replace(cmd_map_bounds, cmd_data)
        file_name = f"cluster{user_id}"
        save_file(content,file_name)
        return render_content_file_HTML(f"{file_name}.html")
    def show_map(self,point):
        html_content = f"""
        <!DOCTYPE html>
            <html>
            <head>
                <title>Map</title>
                <script src="https://maps.googleapis.com/maps/api/js?key={self.api_Key}&callback=initMap" async defer></script>
                <script>
                    const data = {point};
                    function initMap() {{
                         const map = new google.maps.Map(document.getElementById('map'), {{
                            zoom: 5
                        }});

                        const directionsService = new google.maps.DirectionsService();
                        const directionsRenderer = new google.maps.DirectionsRenderer({{
                            map: map,
                            suppressMarkers: true
                        }});
                        
                        const waypoints = data.map(pointOrder => ({{
                            location: new google.maps.LatLng(pointOrder[0], pointOrder[1])
                        }}));
                        data.forEach(function (pointOrder, index) {{
                            var marker = new google.maps.Marker({{
                                position: new google.maps.LatLng(pointOrder[0], pointOrder[1]),
                                map: map,
                                animation: google.maps.Animation.DROP,
                                label: (index + 1).toString()
                            }});
                        }});
                        const request = {{
                            origin: waypoints[0].location,
                            destination: waypoints[waypoints.length - 1].location,
                            waypoints: waypoints.slice(1, waypoints.length - 1),
                            travelMode: google.maps.TravelMode.DRIVING
                        }};
                
                        directionsService.route(request, function(result, status) {{
                            if (status == 'OK') {{
                                directionsRenderer.setDirections(result);
                            }}
                        }});
                    }}
                </script>
            </head>
                <body>
                    <div id="map" style="height: 830px; width: 100%;">
                    </div>
                </body>
            </html>
            """
        return html_content