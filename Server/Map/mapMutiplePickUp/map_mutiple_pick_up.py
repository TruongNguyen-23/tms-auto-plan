from dotenv import load_dotenv
from unidecode import unidecode
import os
class RouteMultiple:
    def __init__(self):
        load_dotenv()
        self.api_Key = os.getenv("API_KEY")
    def compareData(self,route,order):
        arrData=[]
        for items in route:
            latPoint=items[0]
            lonPoint=items[1]
            for item in order:
                for i in range(len(item)):
                    if item[i] == None:
                        item[i] = 0
                latOrder=float(item[3])
                lonOrder=float(item[4])
                if latPoint == latOrder and lonPoint == lonOrder:
                    print(item,item)
                    if isinstance(item[1],str):
                        item[1]=unidecode(item[1])
                        item[8]=unidecode(item[8])
                    elif isinstance(item[1],int):
                        item[1]=""
                    arrData.append(item)
                    break
        return arrData
    def show_Content(self,route,pickUp,order):
        newDataRoute=self.compareData(route,order)
        html = f"""
        <!DOCTYPE html>
            <html>
            <head>
                <title>Route TSP Multiple Pick Up</title>
                <script src="https://maps.googleapis.com/maps/api/js?key={self.api_Key}&libraries=geometry&callback=initMap" async defer"></script>
                <script>
                    const data = {newDataRoute};
                    const pickUp={pickUp};
                    const iconTruck ="https://raw.githubusercontent.com/NguyenKhoaTruong/Test/master/snapedit_1706238297481.png";
                    function initMap() {{
                        const map = new google.maps.Map(document.getElementById('map'), {{
                            zoom: 5
                        }});

                        const directionsService = new google.maps.DirectionsService();
                        const directionsRenderer = new google.maps.DirectionsRenderer({{
                            map: map,
                            suppressMarkers: true
                        }});
                        
                        const waypoints = data.map(point => ({{
                            location: new google.maps.LatLng(point[3], point[4])
                        }}));
                        var currentInfoWindow = null;
                        const request = {{
                            origin: waypoints[0].location,
                            destination: waypoints[waypoints.length - 1].location,
                            waypoints: waypoints.slice(1, waypoints.length - 1),
                            travelMode: google.maps.TravelMode.DRIVING
                        }};
                        data.forEach(function (point, index) {{
                            var marker = new google.maps.Marker({{
                                position: new google.maps.LatLng(point[3], point[4]),
                                map: map,
                                animation: google.maps.Animation.DROP,
                                label: (index + 1).toString()
                            }});
                            pickUp.forEach(function (pick, idx) {{
                                if(point[3] == pick[0] && point[4] == pick[1]){{
                                    var iconSize = new google.maps.Size(70, 70);
                                    var icon = {{
                                        url: iconTruck,
                                        scaledSize: iconSize 
                                    }};
                                    marker.setIcon(icon)
                                }}
                                else{{
                                    return false
                                }}
                            }});
                            marker.addListener('click', function () {{
                                var contentString = `<p>
                                            Order No:&nbsp;${{point[0]}}</br>
                                            Ship To Name:&nbsp;${{point[1]}}</br>
                                            Ship To Address:&nbsp;${{point[8]}}
                                            </p>`;
                                var infoMaker = new google.maps.InfoWindow({{content: contentString }});
                                if (currentInfoWindow != null) {{
                                    currentInfoWindow.close();
                                }}
                                infoMaker.open(map, marker);
                                currentInfoWindow = infoMaker;
                            }});
                            marker.addListener('rightclick', function (event) {{
                                var contextMenu = new google.maps.InfoWindow();
                                var contentString = '<div class="menu">' +
                                    '<ul>' +
                                    '<li id="deleteOrder">Delete Order</li><p class="line"></p>' +
                                    '<li id="transferOrder">Transfer Order</li>' +
                                    '</ul>' +
                                    '</div>';
                                contextMenu.setContent(contentString);
                                contextMenu.setPosition(event.latLng);
                                contextMenu.setOptions({{ pixelOffset: new google.maps.Size(80, 100) }});
                                contextMenu.open(map);
                                google.maps.event.addListener(contextMenu, 'domready', function () {{
                                    
                                    var optionDelete = document.getElementById('deleteOrder');
                                    if (optionDelete) {{
                                        optionDelete.addEventListener('click', function () {{
                                            // marker.setMap(null);
                                            contextMenu.close();
                                            raiseEvent("DELETE_ORDER");
                                        }});
                                    }}
                                }});
                            }});
                            function raiseEvent(event) {{
                                result = {{
                                    "OrderId": point[7],
                                    "EventName": event
                                }}
                                window.chrome.webview.postMessage(JSON.stringify(result));
                            }}
                        }});
                        directionsService.route(request, function(result, status) {{
                            if (status == 'OK') {{
                                directionsRenderer.setDirections(result);
                            }}
                        }});
                    }}
                </script>
            </head>
            <body onload="initMap()">
                            <style>
                    .gm-style-iw-tc {{
                        display: none;
                    }}
                
                    .gm-style-iw-d {{
                        display: block;
                    }}
                    .menu{{
                        border-radius: 5px;
                        border: 1px solid lightgray;
                    }}
                    .line{{
                        width: 125px;
                        height: 1px;
                        margin: 0;
                        padding: 0;
                        background-color: lightgray;
                    }}
                    ul{{
                        text-align: center;
                        list-style: none;
                        padding: 0px;
                        /* border: 1px solid red; */
                    }}
                    li{{
                        margin: 5px;
                        border: 1px;

                    }}
                    li:hover{{
                        cursor: pointer;
                    }}
                </style>
                <div id="map" style="height: 1000px; width: 100%;"></div>
            </body>
            </html>
        """
        return html
    
    
 