from Server.Process.Distance.distance_Matrix import DistanceMatrix
from dotenv import load_dotenv
import requests
import os

TYPE_MT = "MT"
TYPE_GT = "GT"
class SubRouteTrip:
    def __init__(self):
        load_dotenv()
        self.url_sub_route = os.getenv("SUB_ROUTE")
        self.start_point = []
           
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
                            # 05/12/2024 
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
    def total_drop_points_for_trips_no_split(self, trip_prev, trip_next):
        location_data = []
        location_prev = [[items["Lat"],items["Lon"]] for items in trip_prev]
        location_next = [[items["Lat"],items["Lon"]] for items in trip_next]
        location_prev.extend(location_next)
        for items in location_prev:
            if items not in location_data:
                location_data.append(items)
        return len(location_data)
    
    def order_sub_route(self, data, routes, capacity, start_point):
        
        limit_weight = capacity["EquipmentType"]
        mode_capacity = capacity["CapacityFactor"]
        mode_split_capacity = data["SplitCapacity"]
        km_distance_merge = data["DistanceMergeRoute"]
        merge_trips = data["MergeTrip"]
        max_drop_points = data["DropsPoint"]
        self.start_point = start_point
        
        routes = self.sorted_route_define(routes)
        
        grouped_temp = self.group_lists(routes)
        
        grouped_temp = self.sorted_route_define(grouped_temp)
        
        temp_dict = {i: ",".join(values) for i, values in enumerate(grouped_temp)}
        if temp_dict:
            if limit_weight and mode_split_capacity:
                sub_route = self.split_trips_sub_route(data, temp_dict, limit_weight, mode_capacity)
            else:
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
            
                            ship_to = len(list(set([item['ShipTo'] for item in arr])))
                            while ship_to > 1:
                                trip_, temp_data = self.handle_trip_gt_mt_area(arr)
                                data_sub_route.append(temp_data)
                                arr = trip_
                                ship_to = len(list(set([item['ShipTo'] for item in arr])))

                        if arr:
                            data_sub_route.append(arr)
                value_option = self.get_mode_value_capacity(mode_capacity)
                sub_route = self.group_data_no_split(data_sub_route,value_option,max_drop_points,limit_weight,temp_dict)
        else:   
            sub_route = []
        if merge_trips:
            sub_route = self.merge_trip_sub_route_with_distance(sub_route, limit_weight, 
                                                              mode_capacity, km_distance_merge,
                                                              max_drop_points)
        return sub_route, data["Orders"]
    
    
    def sorted_route_define(self, routes):
        for items in routes:
            items.sort(reverse = False)
        return routes    
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
    # def check_data_in_trip(self, data_prev, data_next):
        
    #     area_data_prev = [items["AreaCode"] for items in data_prev]
    #     area_data_next = [items["AreaCode"] for items in data_next]
    #     if bool(set(area_data_next) & set(area_data_prev)):
    #          return True
    #     else:
    #          return False
    def check_data_in_trip(self, data_prev, data_next, route_define):
        # print('route_define',route_define)
        check = False
        list_data = route_define.values()
        sub_route =[item for item in list_data] 
        area_data_prev = list(set([items["AreaCode"] for items in data_prev]))
        area_data_next = list(set([items["AreaCode"] for items in data_next]))
        # print('area_data_prev',area_data_prev)
        # print('area_data_next',area_data_next)
        area_data_prev.extend(area_data_next)
        # print('sub_route',sub_route)
        # print('area_data_prev',area_data_prev)
        for items in sub_route:
            items = set(items.split(','))
            items_area = ",".join(area_data_prev)
            items_area = set(items_area.split(','))
            if items_area.issubset(items):
                check = True
            # else:
            #     check = False
        # print('check',check)
        return check
    
    def check_mt_gt_in_trip(self, data_prev, data_next):
        
        mt_prev = self.data_mt_gt(data_prev, TYPE_MT)
        mt_next = self.data_mt_gt(data_next, TYPE_MT)
        mt_prev.extend(mt_next)
        return len(list(set(mt_prev))) > 1 
    def check_mt_gt_join_trip(self, data_prev, data_next):
        
        mt_prev = self.data_mt_gt(data_prev, TYPE_MT)
        mt_next = self.data_mt_gt(data_next, TYPE_MT)
        gt_prev = self.data_mt_gt(data_prev, TYPE_GT)
        gt_next = self.data_mt_gt(data_next, TYPE_GT)
        
        # Join datâ
        mt_prev.extend(mt_next)
        gt_prev.extend(gt_next)
        
        # Remove data duplicated
        number_mt = len(list(set(mt_prev)))
        number_gt = len(list(set(gt_prev)))
        
        # Check validation
        if number_mt == 1 and number_gt == 1:
            return True
        elif number_mt == 0:
            return True
        else:
            return False
    def data_mt_gt(self, data, type):
        return list(set([items["ShipTo"] for items in data if items["ShipToType"][:2] == type]))
    def split_trips_sub_route(self, data, route_define, limit_weight, mode_capacity):
        list_data = route_define.values()
        sub_routes = []
        for item in list_data:
            item = item.split(",")
            sub_routes.extend(item)
 
        routes = []
        for item in data["Orders"]:
            if item["AreaCode"] in sub_routes:
                if item["AreaCode"] not in routes:
                    routes.append(item["AreaDesc"])
                    
        # print('routes',routes)
        
        max_drops_points = data["DropsPoint"]
        
        # Step 1: Group by area code
        value_option = self.get_mode_value_capacity(mode_capacity)
        data_sub_route = []
        data['Orders'].sort(key=lambda x: x['AreaDesc'])
        for route in sorted(routes,reverse=True):
            temp_data = []     
            i = len(data["Orders"]) - 1
            while i >= 0:
                for item in data['Orders']:
                    if item["AreaDesc"] == route:
                        temp_data.append(item)
                        data["Orders"].remove(item)
                i -= 1
            # Step 2: Sorted data item group check sum trip for limit weight
            total_trip = self.total_trip(temp_data, value_option)
            
            while total_trip > limit_weight and len(temp_data) > 1:
                temp_data = sorted(temp_data,key = lambda x : x [value_option], reverse = False)
                data_sub_route.append([temp_data[0]])
                temp_data.pop(0)
                total_trip = self.total_trip(temp_data, value_option)
                
                
            # Function limit drop point for trip:
            number_drop_point = self.total_drop_points_for_trips(temp_data)
            if max_drops_points:
                while number_drop_point > max_drops_points:
                    if temp_data[-1] not in data["Orders"]: 
                        data["Orders"].append(temp_data[-1])
                    temp_data.pop(-1)
                    number_drop_point = self.total_drop_points_for_trips(temp_data)
                # Function GT MT
                trip_, temp_data = self.handle_trip_gt_mt_area(temp_data)
                if trip_: data_sub_route.append(trip_) 
                    
            if temp_data: data_sub_route.append(temp_data)
   
        data_sub_route = sorted(data_sub_route, key=lambda group: group[0]['ParentAreaCode'])
        # for item in data_sub_route:
        #     print('item',item)
        # Step 3: Return Group trip
        return self.group_data_single_to_trips_split(data_sub_route, value_option, max_drops_points, limit_weight, route_define)
        # return data_sub_route

    def group_data_single_to_trips_split(self, sub_data, val, drops, limit_weight, route_define):
        i = len(sub_data) 
        while i >= 0: 
            arr = {"Distance":[]}
            for j in range(i + 1, len(sub_data)):  
                total_start, total_end = self.total_trip(sub_data[i], val), self.total_trip(sub_data[j], val)
                check_ = self.check_data_in_trip(sub_data[i], sub_data[j], route_define)
                mt_gt = self.check_mt_gt_in_trip(sub_data[i], sub_data[j])
                mt_gt_join = self.check_mt_gt_join_trip(sub_data[i], sub_data[j])
                drop_start = self.total_drop_points_for_trips(sub_data[i])
                drop_end = self.total_drop_points_for_trips(sub_data[j])
                total_drop = drop_start + drop_end
                
                if total_start + total_end < limit_weight and check_:
                    arr["Distance"].append({f"{j}": i})
                    if drops:
                        if sub_data[j] not in sub_data[i] and total_drop < drops:
                            if not mt_gt:   
                                sub_data[i].extend(sub_data[j])
                                sub_data.remove(sub_data[j])
                        if mt_gt_join:
                            sub_data[i].extend(sub_data[j])
                            sub_data.remove(sub_data[j])
                    else:
                        sub_data[i].extend(sub_data[j])
                        sub_data.remove(sub_data[j])
                    break
            # print('arr',arr["Distance"])  
            i -= 1
        # sub_data = self.group_data_no_split(sub_data, val, drops, limit_weight, route_define)
        
        return sub_data
    
    # def group_data_single_to_trips_split(self, sub_data, val, drops, limit_weight, route_define):
    #     i = len(sub_data) 
    #     while i >= 0: 
    #         for j in range(i + 1, len(sub_data)):  
    #             total_start, total_end = self.total_trip(sub_data[i], val), self.total_trip(sub_data[j], val)
    #             check_ = self.check_data_in_trip(sub_data[i], sub_data[j], route_define)
    #             mt_gt = self.check_mt_gt_in_trip(sub_data[i], sub_data[j])
    #             mt_gt_join = self.check_mt_gt_join_trip(sub_data[i], sub_data[j])
    #             drop_start = self.total_drop_points_for_trips(sub_data[i])
    #             drop_end = self.total_drop_points_for_trips(sub_data[j])
    #             total_drop = drop_start + drop_end
    #             if total_start + total_end < limit_weight and check_:
    #                 if drops:
    #                     if sub_data[j] not in sub_data[i] and total_drop < drops:
    #                         if not mt_gt:   
    #                             sub_data[i].extend(sub_data[j])
    #                             sub_data.remove(sub_data[j])
    #                     if mt_gt_join:
    #                         sub_data[i].extend(sub_data[j])
    #                         sub_data.remove(sub_data[j])
    #                 else:
    #                     sub_data[i].extend(sub_data[j])
    #                     sub_data.remove(sub_data[j])
    #                 break  
    #         i -= 1
    #     # sub_data = self.group_data_no_split(sub_data, val, drops, limit_weight, route_define)
        
    #     return sub_data


    def capacity_for_trip_test(self, trips, index):
        capacity = sum(trip[index] for trip in trips)
        centroid = self.calculate_centroid_test(trips)
        return capacity, centroid
    def calculate_centroid_test(self, point):
        lat = sum(float(item['Lat']) for item in point)
        lon = sum(float(item['Lon']) for item in point)
        num_point = len(point)
        center_lat = lat / num_point
        center_lon = lon / num_point
        return [center_lat, center_lon] 
    
    # def group_data_single_to_trips_split(self, sub_data, val, drops, limit_weight, route_define):
    #     # nếu có chung một route chọn khoảng cách gần nhất để lấy dữ liệu
    #     # sorted dữ liệu data sub data với điểm bắt đầu
    #     sub_data = self.sort_data_sub_route_with_start_point(sub_data)
    #     num = 10
    #     for _ in range(num):
    #         print('###')
    #         for i in range(len(sub_data)): 
    #             arr = {"Distance":[]}
    #             for j in range(i + 1, len(sub_data)):
    #                 total_start, centroid_start = self.capacity_for_trip_test(sub_data[i],val)
    #                 total_end, centroid_end = self.capacity_for_trip_test(sub_data[j],val)
    #                 distance = DistanceMatrix.haversine_distance(centroid_start, centroid_end)  
    #                 check_ = self.check_data_in_trip(sub_data[i], sub_data[j], route_define)
    #                 if total_start + total_end < limit_weight and check_:
    #                     arr["Distance"].append({f"{j}": distance})

    #             if arr["Distance"]:
    #                 mt_gt = self.check_mt_gt_in_trip(sub_data[i], sub_data[j])
    #                 mt_gt_join = self.check_mt_gt_join_trip(sub_data[i], sub_data[j])
    #                 drop_start = self.total_drop_points_for_trips(sub_data[i])
    #                 drop_end = self.total_drop_points_for_trips(sub_data[j])
    #                 total_drop = drop_start + drop_end
    #                 if drops:
    #                     if sub_data[j] not in sub_data[i] and total_drop < drops:
    #                         if not mt_gt:   
    #                             sub_data[i].extend(sub_data[j])
    #                             sub_data.remove(sub_data[j])
    #                     if mt_gt_join:
    #                         sub_data[i].extend(sub_data[j])
    #                         sub_data.remove(sub_data[j])
    #                 else:
    #                     min_distance_key = min(arr['Distance'], key=lambda x: list(x.values())[0])
    #                     min_key = int(list(min_distance_key.keys())[0])
    #                     sub_data[min_key].extend(sub_data[j])
    #                     sub_data.remove(sub_data[j])
    #                 break
    #     # sub_data = self.group_data_no_split(sub_data, val, drops, limit_weight, route_define)
    #     return sub_data
    def calculate_average_distance(self, route):
        distances = [
            DistanceMatrix.haversine_distance(self.start_point,[float(item['Lat']), float(item['Lon'])])
            for item in route
        ]
        return sum(distances) / len(distances)
    def sort_data_sub_route_with_start_point(self, routes):
        routes.sort(key=lambda route: self.calculate_average_distance(route))
        # for item in routes:
        #     print('item',item)
        #     print('#########################')
        for idx, route in enumerate(routes, 1):
            print(f"Route {idx}: Average Distance = {self.calculate_average_distance(route):.2f} km")
        return routes
    def group_data_no_split(self, sub_data, val, drops, limit_weight, route_define):
        for i in reversed(range(len(sub_data))): 
            for j in range(i + 1, len(sub_data)):  
                total_start, total_end = self.total_trip(sub_data[i], val), self.total_trip(sub_data[j], val)
                check_ = self.check_data_in_trip(sub_data[i], sub_data[j], route_define)
                total_drop = self.total_drop_points_for_trips_no_split(sub_data[i],sub_data[j])
                if total_start + total_end < limit_weight and check_ and total_drop <= drops:
                    sub_data[i].extend(sub_data[j])
                    sub_data.remove(sub_data[j])  
                    break
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

    def merge_trip_sub_route_with_distance(self, routes, equipment, mode, km_distance, drops):
        order = []
        value_option = self.get_mode_value_capacity(mode)
        # for items in routes:
        #     total = 0
        #     for item in items:
        #         total += item[value_option]
        #     if total < equipment * 0.8:
        #        order.append(items)
        #        routes.remove(items)
            #    fix function when remove items
                     
        # 20/11/2024
        for i in reversed(range(len(routes))):
            total = 0
            for item in routes[i]:
                total += item[value_option]
            if total < equipment * 0.8:
                order.append(routes[i])
                routes.remove(routes[i])
                
                
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
                mt_gt = self.check_mt_gt_in_trip(order[i], order[j])
                if (
                    capacity_trip_start + capacity_trip_end < equipment
                    and distance < km_distance
                ):
                    if drops:
                        if total_drops < drops and mt_gt:
                            if order[i] not in temp["Data"]["Start"]:
                                temp["Data"]["Start"].append(order[i])
                            if order[j] not in temp["Data"]["End"]:
                                temp["Data"]["End"].append(order[j])
                            if distance not in temp["Distance"]:
                                temp["Distance"].append(distance)
                    else:
                        temp["Data"]["Start"].append(order[i])
                        temp["Data"]["End"].append(order[j])
                        temp["Distance"].append(distance)
                elif (
                    capacity_trip_start + capacity_trip_end > equipment
                    and distance < km_distance
                ):
                    # if len(order[j]) > 1:
                    #     for items in order[j]:
                    #         lat = float(items["Lat"])
                    #         lon = float(items["Lon"])
                    #         weight = items[value_option]
                    #         distance_order_to_trip = (
                    #             DistanceMatrix.haversine_distance(
                    #                 centroid_trip_start, [lat, lon]
                    #             )
                    #         )
                    #         if (
                    #             capacity_trip_start + weight < equipment
                    #             and distance_order_to_trip < km_distance
                    #         ):
                    #             order[i].append(items)
                    #             order[j].remove(items)
                    #             capacity_trip_start = capacity_trip_start + weight
                    #         else:
                    #             continue
                    # else:
                    #     break
                    #20/11/2024
                    # remove funtion trên
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
    
    # def check_order_in_data(self, order, data):
    #     area_order = order["AreaCode"]
    #     for items in data:
    #         if area_order in items["AreaCode"]:
    #             return True
    
    
    def handle_trip_gt_mt_area(self, trips):
        trips = sorted(trips, key= lambda item : item["ShipTo"])
        super_market = "MT"
        list_mt = []
        count_area = {}
        for idx in reversed(range(len(trips))): 
            ship_to = trips[idx]["ShipTo"]
            if trips[idx]["ShipToType"][:2] == super_market:
                if ship_to in count_area:
                    count_area[ship_to] += 1
                else:
                    count_area[ship_to] = 1
                list_mt.append(trips[idx])
                del trips[idx]

        number_mt = len(count_area.keys())
        if  number_mt == 1:
            trips.extend(list_mt)
            list_mt.clear()

        while number_mt > 1:
            if len(list_mt) > 1:
                trips.append(list_mt[-1])
                count_area[list_mt[-1]["ShipTo"]] -= 1
                list_mt.pop(-1)
            else:
                pass
            for key, value in list(count_area.items()):
                if value == 0:
                    del count_area[key]
            number_mt = len(count_area.keys())

        return list_mt, trips

    
    
    
        
        

            
            


