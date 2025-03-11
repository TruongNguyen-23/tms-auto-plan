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
        order_id_seq = []
        lat_lon_groups = {}
        result = {}
        for route in routes:
            lat_route, lon_route = route
            for items in data["Orders"]:
                lat_order = items["Lat"]
                lon_order = items["Lon"]
                order_id = items["OrderId"]
                if lat_route == lat_order and lon_route == lon_order:
                    lat_lon = (lat_order,lon_order)
                    if lat_lon not in lat_lon_groups:
                        lat_lon_groups[lat_lon] = []
                    lat_lon_groups[lat_lon].append(order_id)
                    data["Orders"].remove(items)
                else:   
                    pass
        # function group order id seq
        for idx, (lat_lon, order_ids) in enumerate(lat_lon_groups.items()):
            for items in order_ids:
                order_id_seq.append(f"{items}|{idx + 1}")
            result["OrderIdSeq"] = ",".join(order_id_seq)
            
        return result
        # function group seq old    
        # for index, path in enumerate(path_data):
        #     order_id = path["OrderId"]
        #     order_id_seq.append(f"{order_id}|{index + 1}")
        # result["OrderIdSeq"] = ",".join(order_id_seq)
        
        