from Server.Process.Distance.distance_Matrix import DistanceMatrix
from Server.TravelingSalesmanProblem.nearest_neighbor import NearestNeighbor
from flask import abort

def calculate_weight_volume_qty(trip):
    """
        Function calculate qty,volume,weight in trip
        Use for loop function for return data
    """
    weight = []
    volume = []
    qty = []
    for items in trip:
        total_weight = 0
        total_volume = 0
        total_qty = 0
        if items:
            for item in items:
                total_weight += item["Weight"]
                total_volume += item["Volume"]
                total_qty += item["Qty"]
            weight.append(total_weight)
            volume.append(total_volume)
            qty.append(total_qty)
    return [qty,weight,volume]

def path_optimal_route(points):  
    """
        Function calculate route minimum distance
    """
    routes = [] 
    
    for point in points:
        start_index = 0
        mode_return = False
        distance = DistanceMatrix.calculate_distances(point)
        path, cost = NearestNeighbor.tsp_nearest_neighbor(distance, start_index, point, mode_return, not mode_return)
        path.pop(0)
        routes.append(path)
        
    return routes

def change_location_order_trip(trips, routes):
    def find_order_by_coordinates(trip_list, lat, lon):
        for trip in trip_list:
            if float(trip['Lat']) == lat and float(trip['Lon']) == lon:
                return trip
        return None

    new_trips = []
    number_change=[]
    for route in routes:
        new_trip = []
        for lat, lon in route:
            for index,trip_list in enumerate(trips):
                order = find_order_by_coordinates(trip_list, lat, lon)
                if order:
                    new_trip.append(order)
                    trip_list.remove(order)
                    if index not in number_change:
                        number_change.append(index)
                    break
        new_trips.append(new_trip)
    
    return new_trips,number_change


def convent_data_trip(trips, routes):
    """
        Function convent data route to trip simple 
    """
    data_trip = []
    for route in routes:
        for location in route:
            lat = location[0]
            lon = location[1]
            for trip in trips:
                temp_trip = []
                for items in trip:
                    lat_trip = float(items["Lat"])
                    lon_trip = float(items["Lon"])
                    if lat == lat_trip and lon == lon_trip and len(trip) == len(route):
                        temp_trip.append(items)
                        trip.remove(items)
                if temp_trip and temp_trip not in data_trip:
                    data_trip.append(temp_trip)
    return data_trip


def optimize_trip(trip, start_point):
    """ 
        Function calculate best route use nearest neighbor algorithms.
    """
    try:  
        trip_convent = []
        for index, items in enumerate(trip["Trip"]):
            temp_trip = []
            for item in items:
                order_lat = float(item["Lat"])
                order_lon = float(item["Lon"])  
                temp_trip.append([order_lat, order_lon])
            temp_trip.insert(0, start_point)
            trip_convent.append(temp_trip)
        # trip_convent.insert(0, start_point)
        best_route_trip = path_optimal_route(trip_convent)
        # best_route_trip.pop(0)
        trip_convent = best_route_trip
        return convent_data_trip(trip["Trip"], trip_convent)
    except ValueError as e:
        return abort(400,f"Optimize Trip: {e}")