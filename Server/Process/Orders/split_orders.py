from Server.Process.ActionUser.action_for_trip import depth, group_data_trip, group_trip, get_number_mode_capacity
from Server.Process.ActionUser.action_calculate_time import random_color_for_trip
from Server.Process.Distance.distance_Matrix import DistanceMatrix
from Server.Process.Trips.trip_group import *
from sklearn.cluster import KMeans
from flask import abort
import numpy as np

class SplitOrders:
    def __init__(self):
        self.suggest_cluster = ""
        self.name_algorithms = ""
        self.mode_capacity = ""
        self.number_cluster = 0
        self.limit_weight = 0
        self.order = []
        self.data_order = []
        self.start_point = []
        
    def condition_weight(self, input_data, orders):
        self.distance_merge_trip = input_data["DistanceMergeRoute"]
        self.percent_merge = input_data["PercentMergeRoute"]
        self.name_algorithms = input_data["NameAlgorithms"]
        
        self.mode_capacity = input_data["CapacityFactor"]
        data_equipment = input_data["DataEquipmentType"]
        self.limit_weight = input_data["EquipmentType"]
        self.start_point = input_data["StartPoint"]
        
        self.merge_trip = input_data["Merge"]
        self.drop_point = input_data["DropsPoint"]
        self.order = data_equipment
        self.data_order = orders
        self.number_suggest_cluster(data_equipment)
        return self.process_data_cluster_with_equipment()
    
    
    def process_data_cluster_with_equipment(self):
        if self.suggest_cluster > 0:
            return self.function_remove_order(self.k_mean())
        else:
            pass
        
    def number_suggest_cluster(self, equipment):
        address_cluster = [item for idx, item in enumerate(equipment) if item not in equipment[:idx]] 
        self.suggest_cluster = len(address_cluster)
        self.numberCluster = len(address_cluster)
        return address_cluster

    def function_remove_order(self, data):
        return self.calculate_centroid_trip(self.optimal_trips(data))
    
    def optimal_trips(self, data):
        """
            Function optimal trips when data run algorithms k - means
            Variable order need remove data duplicate: can use for loop
        """
        trips = []
        run_orders = False     
        order = [item for idx, item in enumerate(data) if item not in data[:idx]]
        while not run_orders:
            order_fit, order_not_fit = group_data_trip(order, self.limit_weight, self.mode_capacity, self.drop_point)
            if order_not_fit:
                trips.extend(order_not_fit)
            if self.check_mode_total_weight_trip(order_fit):
                run_orders = True
            else:
                order, new_order_not_fit = group_data_trip(order_fit, self.limit_weight, self.mode_capacity, self.drop_point)
                if new_order_not_fit:
                    trips.extend(new_order_not_fit)
        if self.merge_trip:
            orders, trips = self.handle_data_merger(order_fit, trips)
            if self.drop_point and self.percent_merge:
                result = group_trip_with_drop_points(orders, trips ,self.limit_weight, self.mode_capacity, self.distance_merge_trip, self.drop_point)
            elif self.percent_merge:
                result = group_trip(orders, trips ,self.limit_weight, self.mode_capacity, self.distance_merge_trip, self.drop_point)    
            return result
        
        else:
            trips.extend(order_fit)
            return trips
        
    def handle_data_merger(self, orders, trips):
        for order in orders:
            total = 0
            for items in order:
                total += items[8]
            if total > self.percent_merge:
                trips.append(order)
                orders.remove(order)
        return orders, trips
                    
        
    def check_mode_total_weight_trip(self, trips):
        index_capacity = get_number_mode_capacity(self.mode_capacity) 
        mode = True
        for trip in trips:
            total = 0
            for item in trip:
                total += item[index_capacity]
            if total > self.limit_weight:
                mode = False

        return mode
    
    def calculate_centroid_trip(self, trip):
        try:
            result_compare = []
            for items in trip:
                temp = []
                if depth(items) == 1:
                    items = [[""]]
                for item in items:
                    temp_trip = []
                    for value in self.data_order:
                        if value["OrderNo"] == item[0]:
                            temp_trip = value
                        else:
                            continue
                    temp.append(temp_trip)
                result_compare.append(temp)
            random_color_for_trip(len(result_compare))
            return result_compare
        except Exception as e:
            return abort(400, f"Server Error:{e}")
            
    def set_value_data_point(self, data, labels, number):
        point = []
        for i in range(number):
            cluster_points = data[labels == i]
            point.append(cluster_points)
        return point
    
    def get_data_trip(self, data, order):
        trip = []
        for items in data:
            temp_data = []
            for item in items:
                lat = item[0]
                lon = item[1]
                for value in order:
                    if lat == float(value[1]) and lon == float(value[2]):
                        data = [value[0], value[1], value[2], value[7], value[8], value[6], value[3], value[4], value[5], value[9]]
                        if data not in temp_data:
                            temp_data.append(data)
            trip.append(temp_data)
        return trip

    def k_mean(self):
        """
            If use init function centroid result trip to random
            Use init = cluster_centroid: replace centroid algorithms to manual center point
        """
        centroid = self.calculate_cluster_centroid()
        self.numberCluster = len(centroid)
        cluster_centroid = np.array(centroid)
        order = np.array(self.order)
        matrix_location = np.array(
            [
                [
                    float(item[1]),
                    float(item[2]),
                ]
                for item in order
            ]
        )
        weight = np.array([float(item[3]) for item in order]).tolist()
        volume = np.array([float(item[4]) for item in order]).tolist()
        qty = np.array([float(item[2]) for item in order]).tolist()
        if self.name_algorithms == "CT01":
            cluster_k_mean = KMeans(n_clusters = self.numberCluster, n_init = 1, random_state = 0, init = cluster_centroid)
            
            def capacity_k_mean():
                if self.mode_capacity == "W":
                    cluster_k_mean.fit(matrix_location, sample_weight = weight)
                elif self.mode_capacity == "V":
                    cluster_k_mean.fit(matrix_location, sample_weight = volume)
                elif self.mode_capacity == "Q":
                    cluster_k_mean.fit(matrix_location, sample_weight = qty)

            capacity_k_mean()
            label = cluster_k_mean.labels_
            point = self.set_value_data_point(matrix_location, label, self.numberCluster)
            trips = self.get_data_trip(point, self.order)
        else:
            response = {"message": "No Algorithms Cluster Running"}
            return response

        return trips

    def calculate_cluster_centroid(self):
        data = self.order
        centroid = []
        order = []
        area = list(set(item[6] for item in data))
        # get data point
        for i in range(len(area)):
            location = []
            for j in range(len(data)):
                if data[j][6] == area[i]:
                    location.append([float(data[j][1]), float(data[j][2])])
                    data[j].append(i + 1)
            order.append(location)
        # cal centroid
        for items in order:
            center_point = DistanceMatrix.calculate_centroid(items)
            centroid.append(center_point)
        return centroid