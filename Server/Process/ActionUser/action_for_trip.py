# Go to location TripNo and show infomation trip
from Server.Process.Distance.distance_Matrix import DistanceMatrix
from Server.Process.Handle.handle_file import save_file
from Server.Process.Handle.handle_trip import *
from dotenv import load_dotenv
import os

load_dotenv()
FOLDER_CACHE = os.getenv("FOLDER_FILE_CACHE")

def group_data_trip(order, equipment, mode, drops):
    """
    Function group trip single into trip > equipment

    """
    mode_index = get_number_mode_capacity(mode)
    order_fit = []
    order_not_fit = []
    for idx, val in enumerate(order):
        if val == []:
            del order[idx]
    # for item in order:
    for i in range(len(order)):
        item = order[i]
        if depth(item) == 1:    
            item = [item]
        total_drop_point = total_drop_points_for_trips(item)
        if drops:
            while total_drop_point > drops:
                order.append([item[-1]])
                item.pop(-1)
                total_drop_point = total_drop_points_for_trips(item)
        total_weight_trip = calculate_total_capacity(item, mode_index)
        if total_weight_trip < equipment:
            order_fit.append(item)
        elif total_weight_trip > equipment and len(item) == 1:
            order_not_fit.append(item)
        else:
            item = sorted(item, key=lambda x: x[4], reverse = False)
            # item = sorted(sorted(item, key = lambda x : x[4]), key = lambda x : x[mode_index], reverse = False)
            order_remove, item = remove_order_in_trips(
                item, order_not_fit, equipment, mode_index
            )
            
            if item not in order_not_fit:
                order_not_fit.append(item)
            if order_remove != []:
                order_remove, item = remove_order_in_trips(
                    order_remove, order_not_fit, equipment, mode_index
                )
                if order_remove != []:
                    order_fit.append(order_remove)
                if item != [] and item not in order_not_fit:
                    order_fit.append(item)
    return order_fit, order_not_fit

def group_trip(order, trips, equipment, capacity, kilometer, drops):
    
    """
    Function group data trip single have weight < equipment,a
    And use kilometer distance nears to group trip
    """
    # km_distance_near = 11 
    mode_index = get_number_mode_capacity(capacity)
    
    while order:
        for i in range(len(order)):
            arr = {"Distance":[]}
            for j in range(len(trips)):
                capacity_order, location_order, centroid_order= capacity_for_trip(order[i],mode_index)
                
                capacity_trip, location_trip, centroid_trip = capacity_for_trip(trips[j],mode_index)
                distance = DistanceMatrix.haversine_distance(centroid_order, centroid_trip)

                if capacity_order > equipment:
                    while capacity_order > equipment:
                        order.append([order[i][-1]])
                        order[i].remove(order[i][-1])
                        capacity_order,location_order,centroid_order = capacity_for_trip(order[i],mode_index)
                        
                if location_order in location_trip and capacity_order + capacity_trip < equipment:
                    trips[j].extend(order[i])
                    order.remove(order[i])
                     
                elif capacity_order + capacity_trip < equipment and distance < kilometer:
                   arr["Distance"].append({f"{j}": distance})
                               
            if arr["Distance"]:
                min_distance_key = min(arr['Distance'], key=lambda x: list(x.values())[0])
                min_key = int(list(min_distance_key.keys())[0])
                trips[min_key].extend(order[i])
                order.remove(order[i])
                break
            else:
                if len(order[i]) > 0:
                    if order[i] not in trips:
                        trips.append(order[i])
                    order.remove(order[i])
                    break
    return trips

def set_default_data(data):
    """
    Set default data dict, we can  use for loop get data
    """
    data["Data"]["Start"] = []
    data["Data"]["End"] = []
    data["Distance"] = []
    return data

def depth(lst):
    """
    Function find type list ex: [[[1,2]]] = 3 check type
    """
    if not isinstance(lst, list):
        return 0
    elif len(lst) == 0:
        return 1
    else:
        return 1 + max(depth(item) for item in lst)

def user_action_trip(data):
    """
    Function Support User Click Column Chart
    Get Location Point In Google Map
    """
    name_cluster = data["ClusterName"]
    trip = data["TripNo"]
    template_string = ""
    trip = trip[:5] + "#" + trip[5:]
    with open(f"{FOLDER_CACHE}/cluster{name_cluster}.html", "r") as f:
        template = f.read()
        template_string = template
    insertion = f"""
        var numberTrip = tripNo.indexOf("{trip}");;
        var boundsTrip = new google.maps.LatLngBounds();
        number = numberTrip;
        if (numberTrip || numberTrip == 0){{
            (points[numberTrip].length === 1 ? [points[numberTrip][0]] : points[numberTrip]).forEach(function (item) {{
                latPoint = item[1]; lonPoint = item[2];
                if(parseFloat(latPoint) == markerViewBackground.position.lat && parseFloat(lonPoint) == markerViewBackground.position.lng )
                {{
                    boundsTrip.extend(new google.maps.LatLng(location[1], location[2]));
                    var infoMaker = new google.maps.InfoWindow({{ content: contentInfoMaker(location) }});
                    infoMaker.open(map, markerViewBackground);
                }}
            }})
            map.fitBounds(boundsTrip);
        }}
    """
    content = template_string.replace("<!-- GET_LOCATION -->", insertion)
    file_name = f"cluster{name_cluster}"
    save_file(content, file_name)
    return data