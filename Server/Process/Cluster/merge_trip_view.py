from Server.Process.Handle.handle_file import save_file, render_content_file_HTML
from Server.TravelingSalesmanProblem.nearest_neighbor import NearestNeighbor
from Server.Process.Distance.distance_Matrix import DistanceMatrix
from Server.Map.map_big_tsp import ManyRoutePoint
from dotenv import load_dotenv
import requests
import os

class MergeTrip:
    def __init__(self):
        print('Merger Trip In Map')
        load_dotenv()
        self.url_start_point = os.getenv("START_POINT")
        self.user_id = ""
    def merge_trip_view_map(self, data):

        points = self.get_data_trips(data)
        station = self.get_data_station(points)
        html_content = ManyRoutePoint().showManyContent(points, station)
        file_name = f"{self.user_id}" + "trip"
        save_file(html_content,file_name)
        file_render_html = file_name + ".html"
        return render_content_file_HTML(file_render_html)
    
    def get_data_trips(self, data):
        # Update no use api
        # request_data = requests.get(self.url_start_point).json()
        # start_lat = request_data["Lat"]
        # start_lon = request_data["Lon"]
        # start_point = (start_lat, start_lon)
        
        # update start point in 05/12/2024
        start_point = (float(data["PickupLat"]), float(data["PickupLon"]))
        
        points = [] 
        for item in data["LstCluters"]:
            
            for value in item["OrdersClusters"]:
                lat_order = value["Lat"]
                lon_order = value["Lon"]
                
                if (lat_order,lon_order) not in points:
                    points.append((lat_order, lon_order))
                    
                if start_point not in points:
                    points.insert(0,start_point)
        self.user_id = data["UserID"]
        distance = DistanceMatrix.calculate_distances(points)
        path, _ = NearestNeighbor.tsp_nearest_neighbor(distance, 0, points, False, True)
        return path
    
    def get_data_station(self, location):
        station = []
        for items in location:
            lat , lon = items
            location_station = {"lat": lat, "lng": lon}
            
            if location_station not in station:
                station.append(location_station)
                
        return station
    
    # edit content file html if we change UI
    def write_html_content(self):
        print('')
                
