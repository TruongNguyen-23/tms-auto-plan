# import sys

# sys.path.append("E:\TMS_PLAN\API\Server\Process")
from Server.Process.Handle.handle_file import save_file, save_content_cluster_cache
from Server.TravelingSalesmanProblem.nearest_neighbor import NearestNeighbor
from Server.Process.Distance.distance_Matrix import DistanceMatrix
from Server.TemplateDefault.cluster_default import ClusterDefault
from Server.TemplateDefault.chart_default import TripChartDefault
from Server.Process.RouteDefine.sub_route import SubRouteTrip
from Server.Process.ActionUser.action_calculate_time import *
from Server.Process.Orders.split_orders import SplitOrders
from Server.Process.Cluster.suggest_Cluster import Suggest
from Server.Process.ActionUser.action_for_trip import *
from Server.Cluster.KMeans import cluster_labels
from Server.MachineLearning.Src.train import *
from Server.Map.map_Cluster import MapCluster
from Server.Map.chart_bar import TripChart
from timeit import default_timer as timer
from sklearn.cluster import KMeans
from dotenv import load_dotenv
from flask import abort
import numpy as np
import requests
import os
import re


class Process_Data:
    def __init__(self):
        load_dotenv()
        self.url_start_point = os.getenv("START_POINT")
        self.fileCluster = os.getenv("FILE_CLUSTER")
        self.fileChart = os.getenv("FILE_CHART")
        self.data_input = {}
        self.start_point = []
        self.cluster_file = ""
        self.chart_file = ""
        self.mode_draw = ""
        self.tripNo = []
        self.max_radius = 0
        self.mode_ml = False

    def process_cluster_algorithms(self, data):
        """
            Process Data Use Function Clustering K Mean and Split Data Trip
        """
        time_start = timer()
        self.equipment_capacity_factor(data)      
        self.data_input["Trips"] = [] 
        self.mode_ml = data["ML"]
        order = self.handle_data_order(data)
        
        if self.mode_ml:
            trips = trip_for_machine_learning(data)
        else:
            trips_define = self.handle_data_trip_define(data)

            equipment_type = self.data_input["EquipmentType"]
            mode_define = self.data_input["DataEquipmentType"]


            if mode_define == "trip_out_town":
                trips = self.data_input["TripOutTown"]
                equipment_type = -1

            if mode_define == "trip_define":
                return self.order_algorithms_default()

            if equipment_type == "" or equipment_type is None or self.max_radius:
                trips = self.k_mean(order)
                trips.extend(self.data_input["Trips"])
            elif int(equipment_type) >= 0:
                self.data_input["StartPoint"] = self.start_point
                trips = SplitOrders().condition_weight(self.data_input, order)
                trips.extend(self.data_input["Trips"])
    
            if trips_define:
                trips.extend(trips_define["Trip"])
            if trips_define["TripNo"]:
                self.tripNo[-len(trips_define["TripNo"]):] = trips_define["TripNo"]
                
        trips = self.process_data_trips(trips)
        
        # Add more validate for case
    
        random_color_for_trip(len(trips["Trip"]))
        html_cluster = MapCluster().show_map(trips, self.tripNo, self.mode_draw)
        html_chart_cluster = TripChart().show_chart(trips, self.data_input)
        
        save_file(html_cluster, self.cluster_file)
        save_file(html_chart_cluster, self.chart_file)
        save_content_cluster_cache(html_cluster, self.cluster_file)
        
        # function remove data start point
        trips = self.remove_data_start_point_in_trips(trips)
        # clear compile for project
        # clear_cache_compile()
        return self.mapping_result_data(trips, time_start)
    
    def remove_data_start_point_in_trips(self, trips):
        for items in trips["Trip"]:
            for item in items:
                if item["OrderNo"] == "":
                    items.remove(item)
        return trips
    
    def handle_data_order(self, data):
        # request_data = requests.get(self.url_start_point).json()
        # start_lat = request_data["Lat"]
        # start_lon = request_data["Lon"]
        
        start_lat = data["PickupLat"]
        start_lon = data["PickupLon"]
       
        self.start_point = [float(start_lat),float(start_lon)]
        
        user_id = data["UserID"]
        self.cluster_file = f"{self.fileCluster}{user_id}"
        self.chart_file = f"{self.fileChart}{user_id}"
        radius_cluster = data["Radius"]
        
        if radius_cluster == "" or radius_cluster is None:
            self.max_radius = ""
        else:
            self.max_radius = int(data["Radius"])
        
        if self.mode_ml:
            order_cluster = data["Orders"]
        else:
            
            trip_sub_route, order_cluster = self.process_data_sub_route(data)

            if not order_cluster and not trip_sub_route:
                suggest_cluster = 0
                equipment_type = "trip_define"
            elif trip_sub_route and not order_cluster:
                suggest_cluster = 0
                equipment_type = "trip_out_town"
                self.data_input["TripOutTown"] = trip_sub_route
            else:
                equipment_type = self.handle_data_equipment_type(order_cluster)
                # suggest_cluster = Suggest.suggest_number_cluster(equipment_type)

            if self.data_input["SplitCapacity"] is False:
                order_cluster = data["Orders"]
            
            # self.data_input["Suggest"] = suggest_cluster
            self.data_input["DataEquipmentType"] = equipment_type
            self.data_input["Trips"] = trip_sub_route
        
        return order_cluster
    
    def process_data_sub_route(self, orders):
        sub_route = SubRouteTrip().get_data_sub_route_db()
        list_route = SubRouteTrip().handle_sub_route(orders, sub_route)
        return  SubRouteTrip().order_sub_route(orders, list_route, self.data_input, self.start_point)
        # return  SubRouteTrip().order_sub_route(orders, list_route, self.data_input)
           
    # Fix function 
    def handle_data_equipment_type(self, order):
        keys = [
            "OrderNo","Lat","Lon","Qty","Weight",
            "Volume","AreaDesc","ShipToCode",
            "ShipTo","OrderId","AreaCode","ParentAreaCode",
            "ShipToType"
            ]
        orders = []
        
        for item in order:
            if item["Lat"] == "" or item["Lon"] == "":
                order_id = item["OrderId"]
                return abort(400, f"Missing parameter lat,lon in order {order_id} please check your data")
            data_order = [item.get(key) for key in keys]
            orders.append(data_order)
        return orders
    
    # func fix
    # def handle_data_equipment_type(self, order):
    #     for item in order:
    #         if item["Lat"] == "" or item["Lon"] == "":
    #             order_id = item["OrderId"]
    #             return abort(400, f"Missing parameter lat,lon in order {order_id} please check your data")
    #     return order
            
    def order_algorithms_default(self):
        """
            Default algorithm for order clustering
        """
        result = {"Cluster": [], "NumberCluster": 0}
        cluster = ClusterDefault().show_map()
        chart = TripChartDefault().show_chart_bar()
        save_file(cluster, self.cluster_file)
        save_file(chart, self.chart_file)
        save_content_cluster_cache(cluster, self.cluster_file)
        return result
    
    def handle_data_trip_define(self, data):
        data_trip = {
            "Trip":[],
            "TripNo":[]
        }
        if data["Trips"] :
            for trips in data["Trips"]:
                temp_trip_define = []
                trip_no = trips["TripNo"]
                data_trip["TripNo"].append(f"Trip #{trip_no}")
                for trip in trips["OrdersClusters"]:
                    if trip["RequestGroup"]:
                        temp_trip_define.append(trip)
                if temp_trip_define:
                    data_trip["Trip"].append(temp_trip_define)
        
                
        return data_trip
    
    
    def process_data_trips(self, trips):
        data = {
            "Points": [], 
            "Centroid": [],
            "TripOrders": [],
            "StartPoint":[],
            "Weight": [],
            "Volume":[],
            "Qty": [],
            "PointRadius":[],
            "PickUp":[]
            }
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
            
        for index, items in enumerate(trips):
            if self.mode_draw != "M01":
                items.insert(0, data_start_point)
            
            trip_no = f"Trip #{index + 1}"
            data["TripOrders"].append(trip_no)
            self.tripNo.append(trip_no)
            
            points = [[float(points["Lat"]), float(points["Lon"])] for points in items]
            temp_point = points.copy()
            centerPoint = DistanceMatrix.calculate_centroid(points)
            
            data["Centroid"].append(centerPoint)
            data["PointRadius"].append(temp_point)
            points.insert(0, self.start_point)
            data["Points"].append(points)
            
            total_weight = 0
            total_volume = 0
            total_qty = 0
            
            for item in items:
                total_qty += item["Qty"]
                total_weight += item["Weight"]
                total_volume += item["Volume"]
                
            data["Weight"].append(total_weight)
            data["Volume"].append(total_volume)
            data["Qty"].append(total_qty)
            
        if data["Points"] != [] and data["Centroid"] != []:
            data["Direction"], route_path = self.calculate_route_distance(data["Points"])
            
            data["Radius"] = DistanceMatrix.calculate_radius_cluster(data["PointRadius"], data["Centroid"])
            
        elif data["Points"] == []:
            data["Direction"] = []
            data["Radius"] = []
            
        data["StartPoint"] = self.start_point
        data["LabelTripNo"] = self.tripNo
        # data["Trip"] = trips
        data["Trip"] = self.convent_data_trips_route_path(trips, route_path)
        
        data["Quality"] = [data["Qty"],data["Weight"],data["Volume"]]
        return data

    def equipment_capacity_factor(self, data):
        """
            Calculate the equipment capacity factor
        """
        self.data_input["SplitCapacity"] = data["SplitCapacity"]
        
        self.data_input["NameAlgorithms"] = data["NameAlgorithmsCluster"]
        
        self.mode_draw = data["MapOption"]
        
        capacity_factor = data["CapacityFactor"]
        equipment_type = 0
        
        if capacity_factor == "W":
            
            equipment_type = data["EquipmentType"]["Weight"]
            
        elif capacity_factor == "V":
            
            equipment_type = data["EquipmentType"]["Volume"]
            
        elif capacity_factor == "Q":
            if "Qty" in data["EquipmentType"]:
                equipment_type = data["EquipmentType"]["Qty"]
            else:
                equipment_type = 0
            
        self.data_input["CapacityFactor"] = capacity_factor
        
        if data["CapacityPercent"]:
            if equipment_type:
                equipment_type *= int(data["CapacityPercent"])/100
        
        if data["MergeTrip"] and equipment_type:
            self.data_input["Merge"] = True
        elif data["MergeTrip"] and not equipment_type:
            abort(400,"Function No Support")
        else:
            self.data_input["Merge"] = False
            
        if data["PercentMergeRoute"] and equipment_type:
            self.data_input["PercentMergeRoute"] = equipment_type * data["PercentMergeRoute"]/100
        else:
            self.data_input["PercentMergeRoute"] = 100
            
        self.data_input["EquipmentType"] = equipment_type
        
        if data["DistanceMergeRoute"]:
            self.data_input["DistanceMergeRoute"] = int(data["DistanceMergeRoute"])
        else:
            self.data_input["DistanceMergeRoute"] = 0
            
        if data["DropsPoint"]:
            self.data_input["DropsPoint"] = data["DropsPoint"]
        else:
            self.data_input["DropsPoint"] = None
        
        
    def mapping_result_data(self, cluster, time_start):   
        """

        """
        result = {"Cluster": [], "NumberCluster": ""}
        total_drops_points = []
        for index, items in enumerate(cluster["Trip"]):
            order_no = []
            area_desc = []
            area_code = []
            # route_desc = []
            ship_to = {}
            # ship_to = []
            total_ship_to = []
            parent_code = []
            region = []
            number_orders = 0
            number_drop_points = []
            
            centroid_lat = str(cluster["Centroid"][index][0])
            centroid_lon = str(cluster["Centroid"][index][1])
            
            if self.data_input["CapacityFactor"] == "Q":
                index_value_factor = "Qty"
            elif self.data_input["CapacityFactor"] == "W":
                index_value_factor = "Weight"
            elif self.data_input["CapacityFactor"] == "V":
                index_value_factor = "Volume"
                
            # total ship to 
            for item in items:
                lat, lon = item["Lat"], item["Lon"]
                order_no.append(item["OrderNo"])
                # check more shipto
                if item["ShipTo"] not in ship_to:
                    ship_to[item["ShipTo"]] = [item["ShipToType"]]
                else:
                    pass
                # total_ship_to.append(item["ShipToType"])
                
                area_desc.append(item["AreaDesc"])
                
                area_code.append(item["AreaCode"])
                
                # if item["RouteDesc"]:
                #     route_desc.append(item["RouteDesc"])
                
                
                parent_code.append(item["ParentAreaCode"])
                
                region.append(item["Region"])
                
                number_orders += 1
                if [lat,lon] not in number_drop_points:
                    number_drop_points.append([lat,lon])
                if [lat,lon] not in total_drops_points:
                    total_drops_points.append([lat,lon])
            # total ship to
            for key,value in ship_to.items():
                total_ship_to.extend(list(set(value)))

            # trip no
            trip_no = self.tripNo[index][6:]
            if len(trip_no) > 2:
                characters_to_remove = ['#', 'Trip']
                pattern = '[' +  ' '.join(characters_to_remove) +  ']'
                trip_no = re.sub(pattern, '', trip_no)
                
            # load rate
            if self.data_input["EquipmentType"]:
                load_rate = cluster[index_value_factor][index]/self.data_input["EquipmentType"]*100
            else:
                load_rate = 0
                
            result["Cluster"].append(
                {
                    "OrderNo": ",".join(order_no),
                    "TripNo": trip_no,
                    "Weight": cluster["Weight"][index],
                    "Volume": cluster["Volume"][index],
                    "LoadRate": round(load_rate,3),
                    "RouteDistance": cluster["Direction"][index],
                    "TotalShipTo": get_total_ship_to(total_ship_to),
                    "Area": ",".join(list(set(area_desc))),
                    "AreaCode": ",".join(list(set(area_code))),
                    # "RouteDesc": ",".join(list(set(route_desc))),
                    "ParentAreaCode": ",".join(list(set(parent_code))),
                    "Region": ",".join(list(set(region))),
                    "CentroidLat": centroid_lat,
                    "CentroidLon": centroid_lon,
                    "WVQ":self.total_weight_volume_qty_trip(cluster, index),
                    "Orders": number_orders,
                    "Drops": len(number_drop_points),
                    "OrderCluster": items
                }
            )
        result["NumberCluster"] = len(cluster["Weight"])
        result["TotalDrops"] = len(total_drops_points)
        result["TotalWVQ"] = self.total_weight_volume_qty_route(cluster)
        time_end = timer()
        result["Timer"] = round(time_end - time_start)
        return result
    #______________________________FIX_____________________________________#
    def total_weight_volume_qty_trip(self, total, index):
        """
        """
        weight = self.format_data_total_trip(total["Weight"][index])
        volume = self.format_data_total_trip(total["Volume"][index])
        qty = self.format_data_total_trip(total["Qty"][index])
        format_data = [weight,volume,qty]
        return '/'.join(format_data)
    
    def format_data_total_trip(self, value):
        return str(round(value,3))
        
    def total_weight_volume_qty_route(self, total):
        """
        """
        data = [total["Qty"],total["Weight"],total["Volume"]]
        result = []
        for item in data:
            result.append(str(round(sum(item),3)))
        first_element = result.pop(0)
        result.append(first_element)
        return '/'.join(result)
        #______________________________FIX_____________________________________#
    def convent_data_label_trip(self, label, index, order, number, centroid):
        """

        """
        temp = []
        temp_order = order.copy()
        temp_order = np.delete(temp_order, index, 0)
        labels = np.delete(label, index)
        for i in range(number):
            if i not in labels:
                temp.append(i)
        centroid = [centroid[i] for i in range(len(centroid)) if i not in temp]
        if len(temp_order) == 1:
            data = [temp_order]
        else:
            data = self.set_value_data_point(temp_order, labels, len(centroid))
        if len(centroid) > len(data):
            centroid.pop()
        else:
            return data, centroid
        
    def k_mean(self, order):
        try:
            code = self.data_input["NameAlgorithms"]
            #_________FIX CODE___________#
            data_trips = cluster_labels(order, self.start_point)
            order_radius, cluster = self.convent_order_radius(data_trips)
            trips = data_trips["Trip"]
            #_________FIX CODE___________#
            if code == "CT01":
                data_orders = np.array(order_radius)
            elif code == "CT05":
                # order.extend(pickUp)
                data_orders = np.array(order_radius)
            else:
                response = {"message": "No Algorithms Cluster Running"}
                return response
            
            matrix_location = np.array(
                [
                    [
                        float(item["Lat"]),
                        float(item["Lon"]),
                    ]
                    for item in data_orders
                ]
            )
            if self.max_radius != "":
                return self.limit_radius_cluster(order, cluster, matrix_location)
            return trips
        except Exception as e:
            message = f"Sever error: {e}"
            return abort(400, message)
       
    def limit_radius_cluster(self, order, cluster, matrix_location):
        """
            This function is used to limit the radius of the cluster
        """
        is_checked = False
        max_iterations = 300
        temp_center, temp_labels = [], []
        while not is_checked:
            k_means_cluster = KMeans(n_clusters = cluster, max_iter = max_iterations, random_state = 0, n_init = 10)
            k_means_cluster.fit(matrix_location)
            centers = k_means_cluster.cluster_centers_.tolist()
            labels = k_means_cluster.labels_
            distances = np.array(
                [
                    DistanceMatrix.haversine_distance(
                        [float(matrix_location[i][0]), float(matrix_location[i][1])],
                        [centers[labels[i]][0], centers[labels[i]][1]],
                    )
                    for i in range(len(matrix_location))
                ]
            )
            points_outside = distances > self.max_radius
            if np.any(points_outside):
                points = np.where(points_outside)[0]
                labels, centers = self.convent_data_label_trip(
                    labels, points, matrix_location, cluster, centers
                )
                _order = matrix_location[points]
                _number = Suggest.suggest_number_cluster(_order.tolist())
                cluster = _number
                matrix_location = _order
            else:
                labels = self.set_value_data_point(matrix_location, labels, cluster)
                is_checked = True
            temp_center.extend(centers)
            temp_labels.extend(labels)
        return self.get_data_trip_radius(temp_labels, temp_center, order)
                
    def convent_order_radius(self, trip):
        orders = []
        area_cluster = []
        for order in trip["Trip"]:
            for items in order:
                orders.append(items)
                if items["AreaDesc"] not in area_cluster:
                    area_cluster.append(items["AreaDesc"])
        return orders, len(area_cluster)

    def get_data_trip_radius(self, label, center, order):
        trip = []
        for items in label:
            tempTrip = []
            for item in items:
                for value in order:
                    if (
                        value["Lat"] == str(item[0])
                        and value["Lon"] == str(item[1])
                        and value not in tempTrip
                    ):
                        tempTrip.append(value)
            if tempTrip != []:
                trip.append(tempTrip) 
        return trip
    # def add_start_point_route_direction(self, trips):
    #     temp_trip=trips.copy()
    #     for trip in temp_trip:
    #         trip.append(self.start_point)
    #     return temp_trip
    def calculate_route_distance(self, point):
        """

        """
        start_index = 0
        direction = []
        route_path = [] 
        for items in point:
            if items != []:
                distance = DistanceMatrix.calculate_distances(items)
                path, cost = NearestNeighbor.tsp_nearest_neighbor(distance, start_index, items, False, True)
            else:
                cost = 0
            route_path.append(path)
            direction.append(round(cost, 3))
        return direction, route_path

    def set_value_data_point(self, data, labels, number_cluster):
        """
        
        """
        data_convent = []
        points = []
        for i in range(number_cluster):
            cluster_points = data[labels == i]
            points.append(cluster_points.tolist())
        for item in points:
            if item != []:
                data_convent.append(item)
        return data_convent
    
    def convent_data_trips_route_path(self, trips, routes):
        """
            
        """     
        new_trip = []
        for trip, route in zip(trips,routes):
            temp_trip = []
            for item_route in route:
                lat_route = str(item_route[0])
                lon_route = str(item_route[1])
                for i in reversed(range(len(trip))):
                    lat_trip = trip[i]["Lat"]
                    lon_trip = trip[i]["Lon"]
                    if lat_route == lat_trip and lon_route == lon_trip:
                        temp_trip.append(trip[i])
                        del trip[i]
            if temp_trip and temp_trip not in new_trip:
                new_trip.append(temp_trip)
        return new_trip
        
    

