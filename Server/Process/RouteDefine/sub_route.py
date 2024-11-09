from Server.Process.Distance.distance_Matrix import DistanceMatrix
from dotenv import load_dotenv
import requests
import os

class SubRouteTrip:
    def __init__(self):
        load_dotenv()
        self.url_sub_route = os.getenv("SUB_ROUTE")
           
    def get_data_sub_route_db(self):
        data = requests.get(self.url_sub_route).json()
        area_remove = "28,18"
        sub_route = {}
        for item in data:
            rt_id = item['RTId']
            if item["AreaCode"] not in area_remove:
                area_code = item["AreaCode"] + ","
                if rt_id in sub_route:
                    sub_route[rt_id] += area_code
                else:
                    sub_route[rt_id] = area_code
        return sub_route
    
    
    def handle_sub_route(self, data, sub_route):
        list_route = []
        for index,route in enumerate(sub_route):
            arr = []
            for item in data["Orders"]:
                area_code = item["AreaCode"]
                if area_code in sub_route[route]:
                    arr.insert(index,area_code)
            if arr:
                list_route.append(list(set(arr)))
        # remove value duplicate in route
        list_route = [val for index, val in enumerate(list_route) if val not in list_route[:index]]
        return list_route
    
    
    def group_lists(self, route):
        result = []
        while route:
            first, *rest = route
            first = set(first)
            lf = -1
            while len(first) > lf:
                lf = len(first)
                temp_rest = []
                for items in rest:
                    number_intersection = first.intersection(set(items))
                    if number_intersection:
                        if len(first) > len(items):
                            items = [item for item in items if item not in first]
                            temp_rest.append(items)
                        elif len(first) < len(items):
                            value_duplicate = [item for item in first if item not in items]
                            temp_rest.append(value_duplicate)
                            first = set(items)
                        elif len(first) == len(items):
                            for item in items:
                                if item in first:
                                    items.remove(item)
                            temp_rest.append(items)
                            ######
                            # first |= set(items)
                    else:
                        if items:
                            temp_rest.append(items)
                rest = temp_rest
            result.append(sorted(list(first),reverse=True))
            route = rest
        return result
    def total_drop_points_for_trips(self, trips):
        location = []
        for trip in trips:
            lat = trip["Lat"]
            lon = trip["Lon"]
            if [lat,lon] not in location:
                location.append([lat,lon])
        total = len(location)
        return total
    def order_sub_route(self, data, routes, capacity):
        temp_data = data["Orders"].copy()
        limit_weight = capacity["EquipmentType"]
        mode_capacity = capacity["CapacityFactor"]
        mode_split_capacity = data["SplitCapacity"]
        km_distance_merge = data["DistanceMergeRoute"]
        merge_trips = data["MergeTrip"]
        max_drop_points = data["DropsPoint"]
   
        grouped_temp = self.group_lists(routes)
        temp_dict = {i: ",".join(values) for i, values in enumerate(grouped_temp)}
        if temp_dict:
            if limit_weight and mode_split_capacity is True:
                sub_route = self.split_trips_sub_route(data, temp_dict, limit_weight, mode_capacity)
                if merge_trips:
                  sub_route = self.merge_trip_sub_route_with_distance(sub_route, limit_weight, 
                                                                      mode_capacity, km_distance_merge,
                                                                      max_drop_points)
            else:
                # data_sub_route = []
                # for index,route in enumerate(temp_dict):
                #     arr = []
                #     for item in data["Orders"]:
                #         area_code = item["AreaCode"]
                #         if area_code in temp_dict[route]:
                #             arr.insert(index,item)
                #             temp_data.remove(item)
                #     if arr:
                #         data_sub_route.append(arr)
                # data["Orders"] = temp_data
                # sub_route = data_sub_route
                data_sub_route = []
                while self.check_data_in_route_define(data, temp_dict):
                    for index,route in enumerate(temp_dict):
                        arr = []
                        for idx in reversed(range(len(data["Orders"]))):
                            item = data["Orders"][idx]
                            area_code = item["AreaCode"]
                            if area_code in temp_dict[route]:
                                arr.insert(index,item)
                                data["Orders"].remove(item)
                        if  max_drop_points:
                            number_drop_point = self.total_drop_points_for_trips(arr)
                            while number_drop_point > max_drop_points:
                                data["Orders"].append(arr[-1])
                                arr.pop(-1)

                                number_drop_point = self.total_drop_points_for_trips(arr)
                        if arr:
                            data_sub_route.append(arr)
                sub_route = data_sub_route
        else:   
            sub_route = []
        return sub_route, data["Orders"]
    
    def total_trip(self, trips, mode_capacity):
        
        if trips:
              total = sum([trip[mode_capacity] for trip in trips])
        else:
              return 0
        return total
    
    def check_data_in_route_define(self, data, route_define):
        for route in route_define:
            for item in data["Orders"]:
                area_code = item["AreaCode"]
                if area_code in route_define[route]:
                    return True
    def check_data_in_trip(self, data_prev, data_next):
        area_data_prev = [items["AreaCode"] for items in data_prev]
        area_data_next = [items["AreaCode"] for items in data_next]
        if bool(set(area_data_next) & set(area_data_prev)):
             return True
        else:
             return False
    def split_trips_sub_route(self, data, route_define, limit_weight, mode_capacity):
        value_option = self.get_mode_value_capacity(mode_capacity)
        max_drops_points = data["DropsPoint"]
        data["Orders"] = sorted(data["Orders"], key = lambda x : x["AreaCode"],reverse = True)
        # data["Orders"] = sorted(sorted(data["Orders"], key = lambda x : x["AreaCode"]), key = lambda x : x["Volume"], reverse = True)
        data_sub_route= []
        is_run = False
        while not is_run:
            for index,route in enumerate(route_define):
                temp_trip = []
                for idx in reversed(range(len(data["Orders"]))):
                    item = data["Orders"][idx]
                # for item in data["Orders"]:
                    area_code = item["AreaCode"]
                    if area_code in route_define[route]:
                        sum_ = self.total_trip(temp_trip, value_option)
                        if  sum_ < limit_weight:
                            temp_trip.insert(index,item)
                            data["Orders"].pop(idx)
                            # data["Orders"].remove(item)  
                sum_ = self.total_trip(temp_trip,value_option)
                
                while sum_ > limit_weight and len(temp_trip) > 1:
                    temp_trip = sorted(temp_trip,key = lambda x : x ["AreaCode"], reverse = True)
                    if temp_trip[-1] not in data["Orders"]:     
                        data["Orders"].append(temp_trip[-1])
                    temp_trip.pop(-1)
                    sum_ = self.total_trip(temp_trip,value_option)
                # Function limit drop point for trip:
                
                number_drop_point = self.total_drop_points_for_trips(temp_trip)
                if max_drops_points:
                    while number_drop_point > max_drops_points:
                        if temp_trip[-1] not in data["Orders"]: 
                            data["Orders"].append(temp_trip[-1])
                        temp_trip.pop(-1)
                        number_drop_point = self.total_drop_points_for_trips(temp_trip)
                    
                # __________________________________#
                if temp_trip:
                    data_sub_route.append(temp_trip)
                if not self.check_data_in_route_define(data, route_define):
                    is_run = True
        return self.group_data_single_to_trips_split(data_sub_route, value_option, max_drops_points, limit_weight)
    def group_data_single_to_trips_split(self, sub_data, val, drops, limit_weight):
        for i in range(len(sub_data)):
             for j in range(i+1,len(sub_data)):
                  total_start, total_end  = self.total_trip(sub_data[i],val), self.total_trip(sub_data[j],val)
                  check_ = self.check_data_in_trip(sub_data[i],sub_data[j])
                  # function drop point
                  drop_start = self.total_drop_points_for_trips(sub_data[i])
                  drop_end = self.total_drop_points_for_trips(sub_data[j])
                  total_drop = drop_start + drop_end
                  #____________________#
                  if total_start + total_end < limit_weight and check_:
                       if drops:
                           if sub_data[j] not in sub_data[i] and total_drop < drops:
                               sub_data[i].extend(sub_data[j])
                               sub_data.remove(sub_data[j])
                       else:
                            sub_data[i].extend(sub_data[j])
                            sub_data.remove(sub_data[j])
                       break
                  else:
                       pass
        return sub_data
    def get_mode_value_capacity(self, capacity):
        mode = ""
        if capacity == "W":
            mode = "Weight"
        elif capacity == "V":
            mode ="Volume"
        elif capacity == "Q":
            mode = "Qty"
        return mode
    # def get_location_area(self, routes):
    #     location = []
    #     trips = [] 
    #     for items in routes:
    #         for item in items:
    #             if item["AreaDesc"] not in location:
    #                 location.append(item["AreaDesc"])
    #                 trips.append([]) 
    #     return location, trips
    
    # def get_trip_sub_route_split(self, routes, location, trips, mode_capacity):
    #     for items in routes[:]:  
    #         items = sorted(items, key=lambda x: x[mode_capacity])
    #         for item in items[:]: 
    #             if item["AreaDesc"] in location:
    #                 index = location.index(item["AreaDesc"])
    #                 trips[index].append(item)  
    #                 items.remove(item)
    #     return trips  
    # def split_trips_sub_route(self, routes, limit_weight, mode_capacity, route_define):

    #     """
    #     """
    #     check = False
    #     while not check:
    #         orders = []
    #         value_option = self.get_mode_value_capacity(mode_capacity)
    #         for index, route in enumerate(routes):
    #             total = 0 
    #             temp_route = []
    #             for items in route:
    #                 total += items[value_option]
    #                 if total > limit_weight and len(route) > 1:
    #                     total -= items[value_option]
    #                     orders.append(items)
    #                     route.remove(items)
    #                 else:
    #                     if items:
    #                         temp_route.append(items)
                
    #             if len(routes) > 1 and len(routes[index]) <= len(temp_route):
    #                 routes[index] = temp_route
    #             else:
    #                 orders.extend(temp_route)
    #                 for items in temp_route:
    #                     routes[index].remove(items)
    
    #         route_orders = []
    #         for index,value in enumerate(route_define):
    #             temp = []
    #             for order in orders:
    #                 area_code = order["AreaCode"]
    #                 if area_code in route_define[value]:
    #                     temp.insert(index,order)
    #             if temp:
    #                 route_orders.append(temp)
    #         if route_orders:
    #             routes.extend(route_orders)
    #         if not orders:
    #             check = True
    #     routes = [ items for items in routes if items ]
    #     return routes
    def merge_trip_sub_route_with_distance(self, routes, equipment, mode, km_distance, drops):
        order = []
        value_option = self.get_mode_value_capacity(mode)
        for items in routes:
            total = 0
            for item in items:
                total += item[value_option]
            if total < equipment * 0.8:
               order.append(items)
               routes.remove(items)
      
        
        temp = {"Data": {"Start": [], "End": []}, "Distance": []}
        for i in range(len(order)):
            for j in range(i + 1, len(order)):
                capacity_trip_start, capacity_trip_end = (
                    self.calculate_weight_start(order, i, j, value_option)
                )
                centroid_trip_start, centroid_trip_end = self.calculate_centroid(
                    order[i]
                ), self.calculate_centroid(order[j])
                distance = DistanceMatrix.haversine_distance(
                    centroid_trip_start, centroid_trip_end
                )
                # function drop for trip
                drops_start = self.total_drop_points_for_trips(order[i])
                drops_end = self.total_drop_points_for_trips(order[j])
                total_drops = drops_start + drops_end 
                #______________________#
                if (
                    capacity_trip_start + capacity_trip_end < equipment
                    and distance < km_distance
                ):
                    temp["Data"]["Start"].append(order[i])
                    temp["Data"]["End"].append(order[j])
                    temp["Distance"].append(distance)
                    if drops:
                        if total_drops < drops:
                            if order[i] not in temp["Data"]["Start"]:
                                temp["Data"]["Start"].append(order[i])
                            if order[j] not in temp["Data"]["End"]:
                                temp["Data"]["End"].append(order[j])
                            if distance not in temp["Distance"]:
                                temp["Distance"].append(distance)
                elif (
                    capacity_trip_start + capacity_trip_end > equipment
                    and distance < km_distance
                ):
                    if len(order[j]) > 1:
                        for items in order[j]:
                            lat = float(items["Lat"])
                            lon = float(items["Lon"])
                            weight = items[value_option]
                            distance_order_to_trip = (
                                DistanceMatrix.haversine_distance(
                                    centroid_trip_start, [lat, lon]
                                )
                            )
                            if (
                                capacity_trip_start + weight < equipment
                                and distance_order_to_trip < km_distance
                            ):
                                order[i].append(items)
                                order[j].remove(items)
                                capacity_trip_start = capacity_trip_start + weight
                            else:
                                continue
                    else:
                        break
                else:
                    continue
                if temp["Distance"] != []:
                    min_index = temp["Distance"].index(min(temp["Distance"]))
                    order[i].extend(temp["Data"]["End"][min_index])
                    order.remove(temp["Data"]["End"][min_index])
                    temp = self.set_default_data(temp)
                    break
                else:
                    continue
        routes.extend(order)
        return routes
    # def merge_trip_sub_route_with_distance(self, routes, equipment, mode, km_distance):
    #     """"
    #         Function temp
    #     """
    #     orders = []
    #     value_option = self.get_mode_value_capacity(mode)

    #     for index, route in enumerate(routes):
    #         route = sorted(route, key=lambda x: x[value_option],reverse=True) 
    #         total = 0 
    #         temp_route = []
    #         for items in route:
    #             total += items[value_option]
    #             if total > equipment:
    #                 total -= items[value_option]
    #                 orders.append([items])
    #             else:
    #                 temp_route.append(items)
    #         routes[index] = temp_route
    
    #     while orders:
    #         for i in range(len(orders)):
    #             arr = {"Distance":[]}
    #             for j in range(len(routes)):
                    
    #                 capacity_order, location_order, centroid_order = self.capacity_for_trip(orders[i],value_option)
    #                 capacity_trip, location_trip, centroid_trip = self.capacity_for_trip(routes[j],value_option)
    #                 distance = DistanceMatrix.haversine_distance(centroid_order, centroid_trip)
    #                 if capacity_order > equipment:
    #                     while capacity_order > equipment:
    #                         orders.append([orders[i][-1]])
    #                         orders[i].remove(orders[i][-1])
    #                         capacity_order,location_order,centroid_order = self.capacity_for_trip(orders[i],value_option)
    #                 if location_order in location_trip and capacity_order + capacity_trip < equipment :
    #                     routes[j].extend(orders[i])
    #                     orders.remove(orders[i])
    #                 elif capacity_order + capacity_trip < equipment and distance < km_distance:
    #                     arr["Distance"].append({f"{j}": distance})
    #                 if not orders:
    #                     break
                    
    #             if arr["Distance"]:
    #                 min_distance_key = min(arr['Distance'], key=lambda x: list(x.values())[0])
    #                 min_key = int(list(min_distance_key.keys())[0])
    #                 routes[min_key].extend(orders[i])
    #                 orders.remove(orders[i])
    #                 break
    #             elif not orders:
    #                 break
    #             else:
    #                 if len(orders[i]) > 0:
    #                     if orders[i] not in routes:
    #                         routes.append(orders[i])
    #                     orders.remove(orders[i])
    #                     break
    #     return routes
    def set_default_data(self, data):
        """
        Set default data dict, we can  use for loop get data
        """
        data["Data"]["Start"] = []
        data["Data"]["End"] = []
        data["Distance"] = []
        return data
    def calculate_weight_start(self, data, next, prev, index):
        start = sum(trip_start[index] for trip_start in data[next])
        end = sum(trip_end[index] for trip_end in data[prev])
        return start, end
    def calculate_centroid(self, point):
        lat = sum(float(item["Lat"]) for item in point)
        lon = sum(float(item["Lon"]) for item in point)
        num_point = len(point)
        center_lat = lat / num_point
        center_lon = lon / num_point
        return [center_lat, center_lon]

    def capacity_for_trip(self, trips, index):
        capacity = sum(trip[index] for trip in trips)
        location = [trip["AreaDesc"] for trip in trips]
        centroid = self.calculate_centroid(trips)
        return capacity, ','.join(location), centroid
    
    
    
        
        

            
            


