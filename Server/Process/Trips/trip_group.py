
from Server.Process.Distance.distance_Matrix import DistanceMatrix
from Server.Process.Handle.handle_trip import *

def group_trip_with_drop_points(order, trips, equipment, capacity, kilometer, drops):

    """
    Function group data trip single have weight < equipment,a
    And use kilometer distance nears to group trip
    """
    # km_distance_near = 11 
    mode_index = get_number_mode_capacity(capacity)
    is_drops = False
    while order:
        for i in range(len(order)):
            arr = {"Distance":[]}
            for j in range(len(trips)):
                capacity_order, location_order, centroid_order = capacity_for_trip(order[i],mode_index)
                capacity_trip, location_trip, centroid_trip = capacity_for_trip(trips[j],mode_index)
                distance = DistanceMatrix.haversine_distance(centroid_order, centroid_trip)
                # function drops point
                drops_start = total_drop_points_for_trips(order[i])
                drops_end = total_drop_points_for_trips(trips[j])
                total_drops = drops_start + drops_end
                if total_drops < drops:
                    is_drops = True
                #______________________#
                if capacity_order > equipment:
                    while capacity_order > equipment:
                        order.append([order[i][-1]])
                        order[i].remove(order[i][-1])
                        capacity_order,location_order,centroid_order = capacity_for_trip(order[i],mode_index)
                if location_order in location_trip and capacity_order + capacity_trip < equipment and is_drops:
                    trips[j].extend(order[i])
                    order.remove(order[i])
                elif capacity_order + capacity_trip < equipment and distance < kilometer and is_drops:
                   arr["Distance"].append({f"{j}": distance})
            if arr["Distance"]:
                min_distance_key = min(arr['Distance'], key=lambda x: list(x.values())[0])
                min_key = int(list(min_distance_key.keys())[0])
                drop_trips_key = total_drop_points_for_trips(trips[min_key])
                if drop_trips_key + drops_start <= drops:
                    trips[min_key].extend(order[i])
                else:
                    trips.append(order[i])
                order.remove(order[i])
                break
            else:
                if len(order[i]) > 0:
                    if order[i] not in trips:
                        trips.append(order[i])
                    order.remove(order[i])
                    break
    return trips