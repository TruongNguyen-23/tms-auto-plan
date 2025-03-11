from Server.Process.ActionUser.action_calculate_time import get_color_template
from dotenv import load_dotenv
from unidecode import unidecode
import random
import os

class MapCluster:
    def __init__(self):
        load_dotenv()
        self.api_Key = os.getenv("API_KEY")

    def handle_unicode_data(self, data):
        for idx, items in enumerate(data):
            for item in items:
                item[4] = unidecode(item[4])
                item.append(f"{idx + 1}")
        data = self.valid_data(data)
        return data

    def valid_data(self, data):
        for item in data:
            if item == []:
                data.remove(item)
        return data

    def set_data_map_cluster(self, data):
        dict_data_trip = {}
        dict_data_trip["StartPoint"] = data[0]["StartPoint"]
        dict_data_trip["Trip"] = data[0]["Trip"]
        dict_data_trip["Radius"] = data[0]["Radius"]
        dict_data_trip["Centroid"] = data[0]["Centroid"]
        dict_data_trip["TripNo"] = data[1]
        dict_data_trip["TypeMap"] = data[2]
        return dict_data_trip
    
    def valid_data_order_id(self, data):
        # process with order id == None
        for items in data:
            for item in items:
                if not item[5]:
                    item[5] = random.randint(0,100)
        return data
    def convent_data_point(self, points):
        data = []
        for index, items in enumerate(points):
            temp = []
            for item in items:
                temp.append(
                    [
                        item["OrderNo"],
                        item["Lat"],
                        item["Lon"],
                        item["ShipToCode"],
                        item["ShipTo"],
                        item["OrderId"],
                        str(index),
                        item["ShipToType"]
                    ]
                )
            data.append(temp)
        return self.valid_data_order_id(data)
    

    def show_map(self, *args):
        cluster = self.set_data_map_cluster(args)
        trips = self.convent_data_point(cluster["Trip"])
        point = self.handle_unicode_data(trips)
        center_point = cluster["Centroid"]
        color = get_color_template()[: len(cluster["TripNo"])]

        _html = f"""
        <!DOCTYPE html>
            <html>
            <head>
                <title>Map Cluster</title>
                <script src="https://maps.googleapis.com/maps/api/js?key={self.api_Key}&callback=initMap" async defer></script>
                <script>
                    async function initMap() {{
                        var centerCricle={center_point};
                        var tripNo={cluster["TripNo"]};
                        var radius={list(cluster["Radius"])};
                        var points={point};
                        const {{ AdvancedMarkerElement, PinElement }} = await google.maps.importLibrary("marker");
                        const pathIcon="https://www.google.com/mapfiles/marker_green.png";
                        var bounds = new google.maps.LatLngBounds();
                        var directionsService = new google.maps.DirectionsService;
                        var map = new google.maps.Map(document.getElementById('map'), {{
                            center: {{lat: {center_point[0][0]}, lng: {center_point[0][1]}}},
                            mapId: "4504f8b37365c3d0",
                            zoom: 5
                        }});
                        var typeMap = "{cluster["TypeMap"]}";
                        var colorMaker = {color}
                        var circles = [];
                        var infoWindows = [];
                        var labelTrip = [];
                        var currentInfoWindow = null;
                        var makerSplit=[];
                        var showInfoEvent=false;
                        var number=-1;
                        var MAX_WAYPOINTS_EXCEEDED = 0;
                        var duplicatePoint = [];
                        var pickUp = {cluster["StartPoint"]}
                        drawTypeCluster()
                        function arrayEquals(a, b) {{
                            return a.length === b.length && a.every((val, i) => val === b[i]);
                        }}
                        function showData(){{
                            points.forEach(function (point,idx) {{
                                var pointUnique=removeLocationDuplicate(point);
                                showPoint(pointUnique,idx);
                                show_location_pick_up();
                            }});
                            function removeLocationDuplicate(points){{
                                const map = new Map();
                                points.forEach(item => {{
                                    const key = item[1];
                                    if (map.has(key)) {{
                                        map.get(key)[0] += ',' + item[0];
                                        map.get(key)[5] += ',' + item[5];
                                    }} else {{
                                        map.set(key, [...item]);
                                    }}
                                }});
                                const result = Array.from(map.values());
                                return result
                            }}
                            function show_location_pick_up() {{
                                if(typeMap){{
                                    const pinBackground = new PinElement({{
                                        glyphColor: "yellow"
                                    }});
                                    var markerViewBackground = new AdvancedMarkerElement({{
                                        map,
                                        position: {{ lat: pickUp[0], lng: pickUp[1] }},
                                        content: pinBackground.element,
                                        //gmpDraggable: true
                                    }});
                                }}
                            }}
                            function showPoint(point,idx) {{
                                point.forEach(function (location, index) {{
                                    locationDuplicate = [location[1], location[2]];
                                    if(duplicatePoint.some(arr => arrayEquals(arr, locationDuplicate))){{
                                        return
                                    }}
                                    else{{
                                        duplicatePoint.push(locationDuplicate);
                                        location_ = [parseFloat(location[1]), parseFloat(location[2])];
                                         if (location_[0] == pickUp[0] && location_[1] == pickUp[1]) {{
                                            return
                                        }}
                                        else{{
                                            const pinBackground = new PinElement({{
                                            background: colorMaker[idx],    
                                            borderColor: colorMaker[idx],
                                            glyphColor: "#EEEEEE"
                                            }});
                                            var markerViewBackground = new AdvancedMarkerElement({{
                                                map,
                                                position: {{lat: parseFloat(location[1]), lng: parseFloat(location[2])}},
                                                content: pinBackground.element,
                                                //gmpDraggable: true
                                            }});
                                        }}
                                        
                                    }}

                                    markerViewBackground.addListener('click', function () {{
                                        if (number != -1){{
                                            infoWindows[number].close();
                                        }}
                                        infoWindows[location[8]-1].close();
                                        if (event.ctrlKey) {{
                                            markerViewBackground.content.classList.add("bounce")
                                            dataSplit= {{ "TripNo": location[8], "OrderId": location[5] }}
                                            if (makerSplit.includes(dataSplit) == false){{
                                                makerSplit.push(dataSplit)
                                                if (point.length == 1){{
                                                    alert('You cant split trip because trip has only one point')
                                                    markerViewBackground.content.classList.remove("bounce");
                                                }}
                                                else{{
                                                    showDataSplit(makerSplit)
                                                }}
                                                // showDataSplit(makerSplit)
                                            }}
                                            else {{
                                                return makerSplit
                                            }}
                                            currentInfoWindow.close();
                                        }}
                                        else if(event.altKey){{
                                            markerViewBackground.content.classList.remove("bounce");
                                            makerSplit = makerSplit.filter(function (item) {{
                                                return item["OrderId"] !== location[5]
                                            }})
                                            // showDataSplit(makerSplit)
                                        }}
                                        else {{
                                            label_trip_no = tripNo[parseInt(location[8] - 1)]
                                            if (label_trip_no.length > 10) {{
                                                location[8] = label_trip_no.replaceAll("Trip", "").replaceAll("#", "").replaceAll(" ", "")
                                            }}
                                            else {{
                                                location[8] = label_trip_no.slice(6)
                                            }}
                                            var infoMaker = new google.maps.InfoWindow({{ content: contentInfoMaker(location) }});
                                            if (currentInfoWindow != null) {{
                                                currentInfoWindow.close();
                                            }}
                                            infoMaker.open(map, markerViewBackground);
                                            currentInfoWindow = infoMaker;
                                            
                                        }}
                                    }});
                                    moveMakerOrder(markerViewBackground, location,point);
                                    <!-- GET_LOCATION --> 
                                    bounds.extend(new google.maps.LatLng(location[1], location[2]));
                                }})
                            }}
                            function validDataSplit(data) {{
                                const obj = {{}};
                                data.split(",").forEach(item => {{
                                    obj[item] = true;
                                }});
                                const result = Object.keys(obj).join(",");
                                return result
                            }}
                            function showDataSplit(maker){{
                                var orderId = "";
                                var _tripNo = "";
                                makerSplit.forEach(function (item, idx) {{
                                    orderId = orderId.concat(item["OrderId"]) + ",";
                                    _tripNo = tripNo[parseInt(item["TripNo"]) - 1].slice(6);
                                }})
                                raiseEvent("SPLIT_ORDER", validDataSplit(orderId.slice(0, -1)), _tripNo);
                            }}
                            function setZoom(bound,point){{
                                bound.extend(new google.maps.LatLng(parseFloat(point[0][1]), parseFloat(point[0][2])));
                                return map.fitBounds(bound);
                            }}
                            function onlyUnique(value, index, array) {{
                                for (let i = 0; i < index; i++) {{
                                    if (array[i][1] === value[1] && array[i][2] === value[2]) {{
                                        return false;
                                    }}
                                }}
                                return true;
                            }}
                            function contentInfoMaker(data){{
                                var contentString =`<p>
                                    Trip No:&nbsp;${{data[8]}}</br>
                                    Order No:&nbsp;${{data[0]}}</br>
                                    Ship To:&nbsp;${{data[4]}} :&nbsp${{data[7]}}</br>
                                    </p>`;
                                return contentString
                                // Ship To Address:&nbsp;${{data[4]}}
                            }}
                            function moveMakerOrder(marker, locationMove,dataOrder){{
                                google.maps.event.addListener(marker, 'dragend', function (){{
                                    if (event.ctrlKey) {{
                                        return false
                                    }}
                                    else{{
                                        checkMarkerInsideCircles(marker, locationMove,dataOrder);
                                    }}
                                }});
                            }}
                            function checkMarkerInsideCircles(marker,location,dataOrder) {{
                                var distanceCricle=[],radiusCricle=[];
                                var numTrip = findLocation(location);
                                var markerPosition = marker.position;
                                var orderId= location[5].toString();
                                circles.forEach(function (circle, index) {{
                                    var circleCenter = circle.getCenter();
                                    var circleRadius = circle.getRadius();
                                    var distance = google.maps.geometry.spherical.computeDistanceBetween(markerPosition, circleCenter);
                                    distanceCricle.push(distance);
                                    radiusCricle.push(circleRadius);
                                }})
                                // remove location:
                                if (distanceCricle[numTrip - 1]> radiusCricle[numTrip - 1]){{
                                    var tempDC = 0, tempRC = 0 , tempRCS = 0;

                                    for(let i=0;i<=distanceCricle.length;i++){{
                                    
                                        if(distanceCricle[i]>radiusCricle[i]){{
                                            tempDC+=1;
                                        }}
                                        else if(distanceCricle[i]<= radiusCricle[i]){{
                                            tempRC+=1;
                                            tempRCS= i + 1;
                                        }}
                                    }}
                                    //case 1: move order:
                                    if (tempRC > 0) {{
                                        numTrip=tempRCS;
                                        raiseEvent("TRANSFER_ORDER",orderId,numTrip);
                                    }}
                                    //case 2: delete order:
                                    else if(tempDC=distanceCricle.length){{
                                        // numTrip=null;
                                        // marker.setMap(null);
                                        if (dataOrder.length == 1) {{
                                            alert('You cant delete trip because trip has only one point')
                                            marker.position = {{ lat: parseFloat(location[1]), lng: parseFloat(location[2]) }}
                                            return
                                        }}
                                        else{{
                                            numTrip= tripNo[parseInt(location[8] - 1)].slice(6)
                                            raiseEvent("DELETE_ORDER", orderId, numTrip);
                                        }}
                                        // raiseEvent("DELETE_ORDER",orderId,numTrip);
                                    }}
                                }}
                                // case 3: move order in cluster
                                else{{
                                    raiseEvent("MOVE_ORDER_IN_CLUSTER",orderId,numTrip);
                                }}
                                function findLocation(data){{
                                    points.forEach(function (items, idx) {{
                                        items.forEach(function (item, i) {{
                                            if (data[0].includes(item[0])) {{
                                                numTrip = idx + 1;
                                            }}
                                        }})
                                    }})
                                    return numTrip
                                }}
                            }}
                            map.fitBounds(bounds);
                        }}
                        function drawTypeCluster(){{
                             if (typeMap == "M01"){{
                                for (var i = 0; i < {len(center_point)}; i++) {{
                                    var center = new google.maps.LatLng({center_point}[i][0], {center_point}[i][1]);
                                    var circle = new google.maps.Circle({{
                                    center: center,
                                    radius: radius[i],
                                    strokeColor: colorMaker[i],
                                    fillColor: colorMaker[i],
                                    map: map
                                    }});
                                    circles.push(circle);
                                    getInfomationTrip(i,circle);
                                    bounds.extend(center);
                                }}
                             }}
                             else if (typeMap == "M02" || typeMap == "M03"){{
                                point = convertPoint(points)
                                for (var i = 0; i < point.length; i++) {{
                                    var polyline = new google.maps.Polyline({{
                                        path: point[i],
                                        geodesic: true,
                                        strokeColor: colorMaker[i],
                                        strokeOpacity: 1.0,
                                        strokeWeight: 5
                                    }});
                                    polyline.setMap(map);
                                    getInfomationTrip(i,polyline)
                                }}
                             }}
                            else if (typeMap == "M04"){{
                                point = convertPoint(points)
                                point.forEach(function (item, i) {{
                                    if (MAX_WAYPOINTS_EXCEEDED > 0) {{
                                        directionsService = drawMaxWayPointsExceeded(item, colorMaker[i]);
                                    }}
                                    else {{
                                        directionsService = calculateAndDisplayRoute(directionsService, item, colorMaker[i]);
                                    }}
                                    getInfomationTrip(i, directionsService)

                                }})
                            }}
                            function getInfomationTrip(index,typeData){{
                                // if (points[index] != undefined) {{
                                //     var contentTrip = (points[index].length > 1) ? points[index].map(item => item[0]).join(",") : points[index][0][0];
                                // }}
                                infoWindows.push(new google.maps.InfoWindow({{ content: contentTripOrders(tripNo,index,points)}}));
                                hoverData(typeData, infoWindows, map);
                            }}
                            function contentTripOrders(tripNo,num,points){{
                                var content = [];
                                var shipTo = [];
                                var shipToType = [];
                                points[num].forEach(function(items,index){{
                                    content.push(items[0]);
                                    shipTo.push(items[4]);
                                    shipToType.push(items[7]);
                                }})
                                var textShipTo = removeDataDuplicate(shipTo)
                                var textShipToType = removeDataDuplicate(shipToType)
                                var textContent = removeDataDuplicate(content)
                                var template = "Trip No: " + tripNo[num].replaceAll("Trip", "").replaceAll("#", "").replaceAll(" ", "") + "</br>" + "Order No: " + content + "</br>" + "Ship To: " + textShipTo + " " + ":" + " " +textShipToType
                                return template
                            }}
                            function removeDataDuplicate(data) {{
                                var uniqueData = [...new Set(data)];
                                var textShipTo = uniqueData.join(",");
                                return textShipTo
                            }}
                            function hoverData(obj,arr,map) {{
                                function closeTitle(){{
                                    for (var i = 0; i < arr.length; i++) {{
                                        arr[i].close();
                                    }}
                                }}
                                google.maps.event.addListener(obj, 'mouseover', (function (index) {{
                                    return function (event) {{
                                        showInfoEvent = true;
                                        if (currentInfoWindow !=null){{
                                            currentInfoWindow.close();
                                        }}
                                        closeTitle()
                                        arr[index].setPosition(event.latLng);
                                        arr[index].open(map, obj);
                                    }};
                                }})(i));
                                google.maps.event.addListener(obj, 'mouseout', function () {{
                                    showInfoEvent=false;
                                    closeTitle()
                                }});
                            }}
                            function calculateAndDisplayRoute(directionsService, points, color) {{
                                var waypoints = [];
                                for (var i = 1; i < points.length - 1; i++) {{
                                    waypoints.push({{
                                        location: points[i],
                                        stopover: true
                                    }});
                                }}
                                directionsService.route({{
                                    origin: points[0],
                                    destination: points[points.length - 1],
                                    waypoints: waypoints,
                                    // optimizeWaypoints: true,
                                    travelMode: 'DRIVING'
                                }}, function (response, status) {{
                                    if (status === 'OK') {{
                                        var directionsRenderer = new google.maps.DirectionsRenderer({{
                                            map: map,
                                            suppressMarkers: true,
                                            preserveViewport: true,
                                            polylineOptions: {{
                                                strokeColor: color,
                                                strokeWeight: "5"
                                            }}
                                        }});
                                        directionsRenderer.setDirections(response);
                                    }} else {{
                                        alert('No Route: ' + status);
                                    }}
                                }});
                                return directionsService;
                            }}
                            function convertPoint(dataPoint){{
                                let point = []
                                dataPoint.forEach(function (point) {{
                                    if (point.length > 23) {{
                                        MAX_WAYPOINTS_EXCEEDED = 1
                                    }}
                                }})
                                for (let i = 0; i <= dataPoint.length; i++) {{
                                    if (dataPoint[i] !== undefined) {{
                                        if (typeMap == "M03") {{
                                            dataPoint[i].push(dataPoint[i][0])
                                        }}
                                        let temp = dataPoint[i].map(item => ({{ lat: parseFloat(item[1]), lng: parseFloat(item[2]) }}));
                                        point.push(dataPoint[i].length > 1 ? temp : [temp[0]]);
                                    }}
                                }} 
                                return point;
                            }}
                        }}
                    function splitOrderCluster(){{
                        var orderId="";
                        var tripNo="";
                        map.addListener("rightclick", function (event) {{
                            var contextMenu = new google.maps.InfoWindow();
                            var contentString =
                                '<div class="menu"><ul>' +
                                '<div class="split"><img class="iconSplit"/><li id="splitOrder">Split Order</li></div><p class="line"></p>' +
                                '</ul></div>';
                            contextMenu.setContent(contentString);
                            contextMenu.setPosition(event.latLng);
                            contextMenu.setOptions({{ pixelOffset: new google.maps.Size(80, 100) }});
                            contextMenu.open(map);
                            google.maps.event.addListener(contextMenu, 'domready', function () {{
                                var optionSplit = document.getElementById('splitOrder');
                                if (optionSplit) {{
                                    optionSplit.addEventListener('click', function () {{
                                        contextMenu.close();
                                        if (makerSplit.length == 0){{
                                            alert('No Data You Can Not Use Function')
                                            return false
                                        }}
                                        makerSplit.forEach(function (item, idx) {{
                                            orderId = orderId.concat(item["OrderId"]) + ",";
                                            tripNo = tripNo.concat(item["TripNo"]) + ",";
                                        }})
                                        raiseEvent("SPLIT_ORDER", validDataSplit(orderId), validDataSplit(tripNo));
                                    }});
                                }}
                            }});
                        }})
                        function validDataSplit(data){{
                            const obj = {{}};
                            data.split(",").forEach(item => {{
                                obj[item] = true;
                            }});
                            const result = Object.keys(obj).join(",");
                            return result
                        }}
                    }}
                    function drawMaxWayPointsExceeded(points, color) {{
                        for (var i = 0, parts = [], max = 25 - 1; i < points.length; i = i + max)
                            parts.push(points.slice(i, i + max + 1));
                        var service_callback = function (response, status) {{
                            if (status != 'OK') {{
                                {{
                                    console.log('Directions request failed due to ' + status);
                                    return;
                                }}
                            }}
                            var renderer = new google.maps.DirectionsRenderer;
                            renderer.setMap(map);
                            renderer.setOptions({{
                                suppressMarkers: true, preserveViewport: true, polylineOptions: {{
                                    strokeColor: color,
                                    strokeWeight: "5"
                                }}
                            }});
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
                                travelMode: 'DRIVING'
                            }};
                            directionsService.route(service_options, service_callback);
                        }}
                        return directionsService
                    }}       
                    function raiseEvent(event, orderId, tripNo) {{
                        result = {{
                            "OrderId": orderId,
                            "TripNo": tripNo,
                            "EventName": event
                        }}
                        window.chrome.webview.postMessage(JSON.stringify(result));
                    }}
                    showData()
                    // splitOrderCluster()
                    }}
                </script>
                    <style>
                        .gm-style .gm-style-iw-d{{
                            margin-top: -30px !important;
                            max-width: 300px !important;
                            /*
                            min-width: 200px !important; 
                            width: 200px !important; */
                            width:auto;
                            height: 100px;
                            line-height: 1.5rem;
                            text-align: unset;
                            padding-left: 10px;
                            white-space: nowrap;
                        }}
                        .gm-style-iw-d {{
                            display: block;
                        }}
                        .menu {{
                            margin-top: 20px;
                            border-radius: 5px;
                        }}
                        .split {{
                            display: flex;
                        }}
                        img.iconSplit {{
                            width: 25px;
                            height: 25px;
                            margin-left: 5px;
                        }}

                        .line {{
                            width: auto;
                            height: 1px;
                            /* margin: 0;
                            padding: 0; */
                            background-color: lightgray;
                        }}


                        ul {{
                            text-align: center;
                            list-style: none;
                            padding: 0px;
                            /* border: 1px solid red; */
                        }}
                        li#splitOrder {{
                            font-size: 15px;
                            padding-left: 10px;
                            font-weight: 500;
                            font-family: sans-serif;
                            letter-spacing: 1.5px;
                        }}
                        li {{
                            margin: 5px;
                            border: 1px;
                        }}

                        li:hover {{
                            cursor: pointer;
                        }}
                        /* css animation maker */
                        .bounce {{
                            animation: bounce 2s infinite;
                            -webkit-animation: bounce 2s infinite;
                            -moz-animation: bounce 2s infinite;
                            -o-animation: bounce 2s infinite;
                        }}

                        @-webkit-keyframes bounce {{
                            0%, 20%, 50%, 80%, 100% {{-webkit-transform: translateY(0);}} 
                            40% {{-webkit-transform: translateY(-30px);}}
                            60% {{-webkit-transform: translateY(-15px);}}
                        }}

                        @-moz-keyframes bounce {{
                            0%, 20%, 50%, 80%, 100% {{-moz-transform: translateY(0);}}
                            40% {{-moz-transform: translateY(-30px);}}
                            60% {{-moz-transform: translateY(-15px);}}
                        }}

                        @-o-keyframes bounce {{
                            0%, 20%, 50%, 80%, 100% {{-o-transform: translateY(0);}}
                            40% {{-o-transform: translateY(-30px);}}
                            60% {{-o-transform: translateY(-15px);}}
                        }}
                        @keyframes bounce {{
                            0%, 20%, 50%, 80%, 100% {{transform: translateY(0);}}
                            40% {{transform: translateY(-30px);}}
                            60% {{transform: translateY(-15px);}}
                        }}
                    </style>
            </head>
                <body>
                    <div id="map" style="
                        height:100%;
                        width:100%;
                        position:absolute;
                        top:0;
                        left:0;
                        overflow:hidden;">
                    </div>
                </body>
            </html>
            """
        return _html
