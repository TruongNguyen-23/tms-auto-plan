from dotenv import load_dotenv
from unidecode import unidecode
import os

class MapTSP:
    def __init__(self):
        load_dotenv()
        self.api_Key = os.getenv("API_KEY")
        self.data=[]
    def compareData(self,point,data):
        arrData=[]
        for items in point:
            latPoint=items[0]
            lonPoint=items[1]
            for item in data:
                latOrder=item[3]
                lonOrder=item[4]
                if latPoint == latOrder and lonPoint == lonOrder:
                    arrData.append(item)
                    break
        return arrData
    def deleteUnicode(self,data):
        for item in data:
            if isinstance(item[1],str):
                item[1]=unidecode(item[1])
            if isinstance(item[1],int):
                item[1]=str(item[1])
        return data
    
    def convent_data_point(self, data):
        for item in data:
            if item[7] == None:
                item[7] = 0
        return data
            
    def show_Content(self,point,order,startPoint):
        startPoint=[0 if value == None else value for value in startPoint]
        order.append(startPoint)
        data = self.deleteUnicode(order)
        newPoint = self.convent_data_point(self.compareData(point,data))
        print('newPoint',newPoint)
        html = f"""
        <!DOCTYPE html>
            <html>
            <head>
                <title>Route TSP</title>
                <script src="https://maps.googleapis.com/maps/api/js?key={self.api_Key}&libraries=geometry&callback=initMap" async defer"></script>
                <script>
                    const data = {newPoint};
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
                            location: new google.maps.LatLng(pointOrder[3], pointOrder[4])
                        }}));
                        var currentInfoWindow = null;
                        data.forEach(function (pointOrder, index) {{
                            var marker = new google.maps.Marker({{
                                position: new google.maps.LatLng(pointOrder[3], pointOrder[4]),
                                map: map,
                                animation: google.maps.Animation.DROP,
                                label: (index + 1).toString()
                            }});
                            marker.addListener('click', function () {{
                                var contentString = `<p>
                                            Order No:&nbsp;${{pointOrder[0]}}</br>
                                            Ship To Name:&nbsp;${{pointOrder[1]}}</br>
                                            Ship To Address:&nbsp;${{pointOrder[8]}}
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
                                    "OrderId": pointOrder[7],
                                    "EventName": event
                                }}
                                window.chrome.webview.postMessage(JSON.stringify(result));
                            }}
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
            <body onload="initMap()">
                <style>
                    html,
                     body {{
                        height: 100%;
                        margin: 0;
                        padding: 0;
                    }}
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
                <div id="map" style="height: 100%; width: 100%;"></div>
            </body>
            </html>
        """
        return html
    
    
 