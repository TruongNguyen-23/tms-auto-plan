from Server.Process.ActionUser.action_calculate_time import *
from Server.Process.ActionUser.action_for_trip import *
from Server.Process.Handle.handle_file import save_file, save_content_cluster_cache
from Server.Process.Distance.distance_Matrix import DistanceMatrix
from Server.TemplateDefault.cluster_default import ClusterDefault
from Server.TemplateDefault.chart_default import  TripChartDefault
from Server.Map.map_Cluster import MapCluster
from Server.Map.chart_bar import TripChart
from timeit import default_timer as timer
from dotenv import load_dotenv
import requests
import re
import os
from flask_restx import abort

class MergerCluster:
    def __init__(self):
        load_dotenv()
        self.url_start_point = os.getenv("START_POINT")
        self.file_cluster = os.getenv("FILE_CLUSTER")
        self.file_chart = os.getenv("FILE_CHART")
        self.cluster = {"Trip": []}
        self.limit_weight = 0
        self.cluster_file = ""
        self.chart_file = ""
        self.mode_capacity = ""
        self.start_point = []

    def merge_trip(self, data):
        time_start = timer()
        self.cluster_file = get_content_for_user_id(self.file_cluster, data["UserID"])
        self.chart_file = get_content_for_user_id(self.file_chart, data["UserID"])     
        data_trips = self.get_data_trips(data)
        
        if data_trips["LabelTripNo"]:
            content_html_cluster = MapCluster().show_map(self.cluster, data_trips["LabelTripNo"], self.cluster["TypeMap"])
            html = TripChart().show_chart(data_trips, self.cluster)
            save_file(content_html_cluster, self.cluster_file)
            save_content_cluster_cache(content_html_cluster, self.cluster_file)
            save_file(html, self.chart_file)
        
        else:
            cluster = ClusterDefault().show_map()
            chart = TripChartDefault().show_chart_bar()
            save_file(cluster, self.cluster_file)
            save_file(chart, self.chart_file)
        
        return self.show_result_merge(time_start, data_trips)

    def find_value_type_map(self):

        file_name = f"teamplates\{self.cluster_file}.html"
        
        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8") as file:
                html_content = file.read()
            variable_name = "typeMap"
            pattern = re.compile(r"\b" + re.escape(variable_name) + r'\b\s*=\s*["\']([^"\']+)["\']')
            match = pattern.search(html_content)
            if match:
                variable_value = match.group(1)
            else:
                variable_value = None

            return variable_value
        else:
           return "M01"


    def show_result_merge(self, time_start, trips):
        route = DistanceMatrix.calculate_distance_route(self.pick_up_to_route_distance(trips["Trip"]))
        result = {"Cluster": [], "NumberCluster": len(trips["Trip"])}
        total_drops_points = []
        for index in range(len(trips["Trip"])):
            number_drops_trip = []
            
            if self.mode_capacity == "V":
                load_rate = trips["Volume"][index] / self.limit_weight * 100
            elif self.mode_capacity == "W":
                load_rate = trips["Weight"][index] / self.limit_weight * 100
            elif self.mode_capacity == "Q":
                load_rate = trips["Qty"][index] / self.limit_weight * 100
                
            for items in trips["Trip"][index]:
                if items not in number_drops_trip:
                    number_drops_trip.append(items)
                if items not in total_drops_points:
                    total_drops_points.append(items)
                    
            result["Cluster"].append(
                {
                    "OrderNo" : trips["OrderNo"][index],
                    "TripNo" : trips["TripNo"][index],
                    "Weight" : trips["Weight"][index],
                    "Volume" : trips["Volume"][index],
                    "RouteDistance" : route[index],
                    "Area" : ",".join(trips["Area"][index]),
                    "RouteDesc" : ",".join(trips["RouteDesc"][index]),
                    "TotalShipTo":get_total_ship_to(trips["TotalShipTo"][index]),
                    "AreaCode" : ",".join(trips["AreaCode"][index]),
                    "ParentAreaCode" : ",".join(trips["ParentCode"][index]),
                    "LoadRate" : load_rate,
                    "Region" : ",".join(trips["Region"][index]),
                    "CentroidLat" : str(trips["Centroid"][index][0]),
                    "CentroidLon" : str(trips["Centroid"][index][1]),
                    "WVQ" : self.total_weight_volume_qty_trip(index, trips),
                    "Orders" : len(trips["Trip"][index]) - 1,
                    "Drops" : len(number_drops_trip) - 1,
                    "OrderCluster": trips["OrderCluster"][index]
                }
            )
        if len(total_drops_points) == 0:
            result["TotalDrops"] = len(total_drops_points)
        else:
            result["TotalDrops"] = len(total_drops_points) - 1
        result["TotalWVQ"] = self.total_weight_volume_qty_route(trips)
        time_end = timer()
        # round(time_end - time_start,3)
        result["Timer"] = round(time_end - time_start)
        return result
    
    def total_weight_volume_qty_trip(self,index, data):
        """
        """
        weight = self.format_data_total_trip(data["Weight"][index])
        volume = self.format_data_total_trip(data["Volume"][index])
        qty = self.format_data_total_trip(data["Qty"][index])
        format_data = [weight,volume,qty]
        return '/'.join(format_data)
    
    def format_data_total_trip(self, value):
        return str(round(value,3))
    
    def total_weight_volume_qty_route(self, data):
        weight = self.format_data_total_trip(sum(data["Weight"]))
        volume = self.format_data_total_trip(sum(data["Volume"]))
        qty = self.format_data_total_trip(sum(data["Qty"]))
        
        result = [weight,volume,qty]
        return '/'.join(result)
    def pick_up_to_route_distance(self, trips):
        for trip in trips:
            trip.append(self.start_point)
        return trips
    
    def get_data_capacity(self, trip):
        if trip["CapacityFactor"]:
            self.mode_capacity = trip["CapacityFactor"]
        # 23/10 4:02
        # if self.mode_capacity == "V":
        #     self.limit_weight = trip["Volume"]
        # elif self.mode_capacity =="W":
        #     self.limit_weight = trip["Weight"]
        # 23/10 4:05
        
            
    def get_data_trips(self, data):
        keys_column = [
            "OrderNo","Weight","Qty","Volume","Area","TripNo","LabelTripNo",
            "AreaCode","ParentCode","Region","LoadRate","Centroid","Trip",
            "Quality","TripOrder","OrderCluster","RouteDesc","TotalShipTo"
        ]
        capacity = []
        # case capacity null or 0
        capacity_temp = []
        obj_data = dict((key,[]) for key in keys_column)
        
        # request_data = requests.get(self.url_start_point).json()
        # start_lat = request_data["Lat"]
        # start_lon = request_data["Lon"]
        self.start_point = [float(data["PickupLat"]), float(data["PickupLon"])]
        
        
        
        if data["LstCluters"]:
            for item in data["LstCluters"]:
                obj_data["LabelTripNo"].append("Trip #" + str(item["TripNo"]))
                obj_data["TripNo"].append(item["TripNo"])
                obj_data["LoadRate"].append(item["LoadRate"])
                self.get_data_capacity(item)
                if item["Capacity"]:
                    capacity.append(item["Capacity"])
                else:
                    capacity.append(0)
                    if item["CapacityFactor"] == "V":
                        capacity_temp.append(item["Volume"])
                    elif item["CapacityFactor"] == "W":
                        capacity_temp.append(item["Weight"])

                data_hard = {
                    "weight": 0, 
                    "volume": 0, 
                    "qty": 0, 
                    "temp": [],
                    "orderNo": [],
                    "area": [],
                    "areaCode": [],
                    "routeDecs":[],
                    "totalShipTo":[],
                    "parentCode":[],
                    "region":[],
                    "tripOrder": [],
                    "trip": []
                    }
                ship_to = {}
                obj_data["OrderCluster"].append(item["OrdersClusters"])
                for value in item["OrdersClusters"]:
                    
                    data_hard["trip"].append(value)
                    if self.start_point:
                        data_start_point = {
                            "OrderNo":"",
                            "Lat":str(self.start_point[0]),
                            "Lon":str(self.start_point[1]),
                            "ShipToCode":"",
                            "ShipTo":"",
                            "OrderId":"",
                            "ShipToType":"",
                            "Weight":0,
                            "Volume":0,
                            "Qty":0
                        }
                        data_hard["trip"].append(data_start_point)

                    if str(value["AreaDesc"]) not in data_hard["area"]:
                        data_hard["area"].append(str(value["AreaDesc"]))

                    if str(value["AreaCode"]) not in data_hard["areaCode"]:
                        data_hard["areaCode"].append(value["AreaCode"])
                    
                    if str(value["RouteDesc"]) not in data_hard["routeDecs"] and value["RouteDesc"]:
                        data_hard["routeDecs"].append(value["RouteDesc"])
                        
                    # if str(value["ShipToType"]) not in data_hard["totalShipTo"]:
                    #     data_hard["totalShipTo"].append(value["ShipToType"])
                    
                    if value["ShipTo"] not in ship_to:
                        ship_to[value["ShipTo"]] = [value["ShipToType"]]
                    else:
                        pass

                    if str(value["ParentAreaCode"]) not in data_hard["parentCode"]:
                        data_hard["parentCode"].append(value["ParentAreaCode"])

                    if str(value["Region"]) not in data_hard["region"]:
                        data_hard["region"].append(value["Region"]) 

                    data_hard["temp"].append([float(value["Lat"]), float(value["Lon"])])
                    data_hard["tripOrder"].append(
                        [
                            value["OrderNo"],
                            value["Lat"],
                            value["Lon"],
                            value["ShipToCode"],
                            value["ShipTo"],
                            value["OrderId"],
                            item["TripNo"],
                        ]
                    )
                    data_hard["orderNo"].append(str(value["OrderNo"]))
                    data_hard["weight"] += float(value["Weight"])
                    data_hard["volume"] += float(value["Volume"])
                    data_hard["qty"] += float(value["Qty"])
                    
                for key,value in ship_to.items():
                    data_hard["totalShipTo"].extend(list(set(value)))

                centroid = DistanceMatrix.calculate_centroid(data_hard["temp"])

                obj_data["Centroid"].append(centroid)
                obj_data["Trip"].append(data_hard["temp"])
                obj_data["Area"].append(data_hard["area"])
                obj_data["OrderNo"].append(",".join(data_hard["orderNo"]))
                obj_data["Weight"].append(data_hard["weight"])
                obj_data["Volume"].append(data_hard["volume"])
                obj_data["Qty"].append(data_hard["qty"])

                obj_data["AreaCode"].append(data_hard["areaCode"])
                obj_data["RouteDesc"].append(data_hard["routeDecs"])
                obj_data["TotalShipTo"].append(data_hard["totalShipTo"])
                obj_data["ParentCode"].append(data_hard["parentCode"])
                obj_data["Region"].append(data_hard["region"])
                obj_data["TripOrder"].append(data_hard["tripOrder"])
                obj_data["Quality"] = [obj_data["Qty"],obj_data["Weight"],obj_data["Volume"]]


                self.cluster["Trip"].append(data_hard["trip"])
                random_color_for_trip(len(self.cluster["Trip"]))
                self.cluster["TripNo"] = obj_data["LabelTripNo"]
                self.cluster["Centroid"] = self.calculate_data_point_center(obj_data["Trip"])
                self.cluster["Radius"] = DistanceMatrix.calculate_radius_cluster(
                obj_data["Trip"], self.cluster["Centroid"])
                self.cluster["TypeMap"] = self.find_value_type_map()
                self.cluster["StartPoint"] = self.start_point
                self.cluster["CapacityFactor"] = self.mode_capacity
                

            if capacity_temp and len(capacity_temp) == len(obj_data["Trip"]) :
                self.limit_weight = max(capacity_temp)
            else:
                self.limit_weight = max(capacity)
            self.cluster["EquipmentType"] = self.limit_weight
        return obj_data
            

    def calculate_data_point_center(self, trip):
        point = []
        for i, items in enumerate(trip):
            if len(items) <= 1:
                point.insert(i, [[item[0], item[1]] for item in items][0])
            else:
                item = [[item[0], item[1]] for item in items]
                n = len(item)
                sum_lat, sum_lon = 0, 0
                for value in item:
                    sum_lat += value[0]
                    sum_lon += value[1]
                centroid = [sum_lat / n, sum_lon / n]
                point.insert(i, centroid)
        return point


