from Server.TravelingSalesmanProblem.nearest_neighbor import NearestNeighbor
from Server.Process.Distance.distance_Matrix import DistanceMatrix
from dotenv import load_dotenv
import requests
import os
class TripClusterConfirm:
    def __init__(self):
        load_dotenv()
        self.url_start_point = os.getenv("START_POINT")
    def process_trip_confirm(self, input_data):
        routes = self.handle_path_data(input_data)
        return self.convent_data_and_show_result(routes, input_data)
        
    def handle_path_data(self, data):
        
        request_data = requests.get(self.url_start_point).json()
        start_lat = request_data["Lat"]
        start_lon = request_data["Lon"]
        start_point = [start_lat, start_lon]
        orders_point = []
        points = []
        for order in data["Orders"]:
            orders_point.append([order["Lat"],order["Lon"]])
        points.append(start_point)
        points.extend(orders_point)
        
        distance = DistanceMatrix.calculate_distances(points)
        path, _ = NearestNeighbor.tsp_nearest_neighbor(distance, 0, points, False, True)
        
        return path
    def convent_data_and_show_result(self, routes, data):
        path_data = []
        order_id_seq = []
        result = {}
        for route in routes:
            lat_route = route[0]
            lon_route = route[1]    
            for items in data["Orders"]:
                lat_order = items["Lat"]
                lon_order = items["Lon"]
                if lat_route == lat_order and lon_route == lon_order:
                    path_data.append(items)
                    data["Orders"].remove(items)
        
        for index, path in enumerate(path_data):
            order_id = path["OrderId"]
            order_id_seq.append(f"{order_id}|{index + 1}")
        result["OrderIdSeq"] = ",".join(order_id_seq)
        return result
        