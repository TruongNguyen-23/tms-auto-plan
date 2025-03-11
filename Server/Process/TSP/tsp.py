from Server.Process.ActionUser.action_calculate_time import get_content_for_user_id
from Server.TravelingSalesmanProblem.nearest_neighbor import NearestNeighbor
from Server.Process.Distance.distance_google_map import DataGoogleMapAPI
from Server.Process.Distance.distance_Matrix import DistanceMatrix
from Server.Process.Cluster.kmeans_cluster import Process_Data
from Server.Process.Handle.handle_file import save_file
from Server.Process.TSP.pick_up_trip import PickUpTrip
from Server.Map.map_big_tsp import ManyRoutePoint
from Server.Map.time_line import TimeLineRoute
from datetime import datetime, timedelta
from Server.Map.map_TSP import MapTSP
from dotenv import load_dotenv
from flask import abort
import requests
import os


FORMAT_TIME = "%d/%m/%Y %H:%M" 
FORMAT_TIME_LINE = "%Y-%m-%d, %H:%M:%S"

class ProcessTSP:
    def __init__(self):
        load_dotenv()
        self.point = []
        self.orders = []
        self.user_id = ""
        self.time_line_name = ""
        self.mode_option = False 
        self.url_start_point = os.getenv("START_POINT")

    def tsp_route(self, data):
        keys = [
            "OrderNo", "ShipTo", "Qty", "Lat", "Lon", 
            "Weight", "Volume","OrderId", "ShipToCode",
            "ItemNote","RequestGroup","ShopType","ShipToType"
        ]
        
        # request_data = requests.get(self.url_start_point).json()
        # start_lat = request_data["Lat"]
        # start_lon = request_data["Lon"]
        # start_point = [start_lat, start_lon]
        # update start point in pickup  05/12/2024
        
        file_name = datetime.now().strftime("%d%m%H%M%S")
        customer = data["CustomerCode"]
        name_algorithms = data["NameTSP"]
        self.user_id = data["UserID"]
        
        # if data["ModeGroup"]:
        #     group_data =  Process_Data().process_cluster_algorithms(data)
        #     with open(f'teamplates\cluster{self.user_id}.html', 'r') as source_file:
        #         content = source_file.read()
                
        #     file_content = f"tsp{self.user_id}"
        #     save_file(content,file_content)
        #     return group_data
        # else:
        self.mode_option = data["ModeDropPoint"]
        if name_algorithms == "ALNS":
            return PickUpTrip().ruleTrip(data, self.user_id, customer)
        elif name_algorithms == "TP01":
            for items in data["Orders"]:
                self.point.append([items["Lat"], items["Lon"]])
                self.orders.append([items.get(key) for key in keys])
                start_lat = str(items["PickupLat"])
                start_lon = str(items["PickupLon"])
                start_point = [start_lat,start_lon]
                
            self.point.insert(0, start_point)
            data["LocationStart"] = ["","",0, start_lat, start_lon, 0, 0, 0,"","","","",""]
            print('data["LocationStart"]',data["LocationStart"])
            return self.calculate_data_tsp(data, start_point, file_name)
        else:
            return abort(400, f"No Name Algorithms {name_algorithms} Please Check Again")
        
    

    def calculate_data_tsp(self,data, start_point, file_name):
        data_start_point = ["" if value is None else value for value in data["LocationStart"]]
        mode_return = data["ModeReturn"]
        self.handle_validate_data(data, start_point)
        
        distance = DistanceMatrix.calculate_distances(self.point)
        path, cost = NearestNeighbor.tsp_nearest_neighbor(distance, 0, self.point, mode_return, not mode_return)
        points = self.handle_data_option_mode_draw(path)
        
        if len(self.point) < 25:
            self.save_file_map_tsp(MapTSP().show_Content(points, self.orders, data_start_point))
            real_distance, _ = DataGoogleMapAPI().data_real_time(self.point)
        else:
            if data_start_point not in self.orders:
                self.orders.append(data_start_point)
            real_distance = self.big_map(points)
        
        if self.mode_option:
            temp_location_start = path[0]
            path = self.remove_data_duplicate(path)
            path.append(temp_location_start)
        
            
        eta_etd, time_route = self.cal_ETA_ETD(data, path, file_name, mode_return)
        return self.result_tsp_route(cost, real_distance, time_route, path, eta_etd)
        
    def remove_data_duplicate(self, data):
        duplicate = []
        for items in data:
            if items not in duplicate:
                duplicate.append(items)
        return duplicate
    
    def handle_data_option_mode_draw(self, points):
        point = []
        if self.mode_option:
            for items in points:
                if list(items) not in point:
                    point.append(list(items))
            return point
        else:
            return points

    def handle_validate_data(self, data, start_point):
        number_empty = 0
        for item in data["Orders"]:
            if item["Lat"] == "" or item["Lon"] == "":
                number_empty += 1
        if not all(start_point) or number_empty > 0:
            return abort(400, "Missing Parameter Lat,Lon. Please Check Your Data")

    def big_map(self, point):
        """
            Apply for google map if want show <25 points 
        """
        data = []
        for items in point:
            data.append({"lat": items[0], "lng": items[1]})
        cost, time = DataGoogleMapAPI().get_directions_way_point(data)
        self.save_file_map_tsp(ManyRoutePoint().showManyContent(point, data))
        route_distance = f"{round(cost,3)} km"
        return route_distance

    def result_tsp_route(self, cost, distance, time_route, path, eta_etd):
        drop_mode_order = []
        response = {
            "Orders": [],
            "KmDirection": f"{round(cost,3)} km",
            "KmRoute": distance,
            "TimeRoute": time_route,
            "TimeLineName": self.time_line_name,
        }
        temp = self.convent_data_tsp(path)      
                
        if self.mode_option:
            temp = self.remove_data_duplicate_for_drop_point(temp)
            eta_etd = self.remove_data_duplicate(eta_etd)
            
        for index, item in enumerate(temp):
            print('item',item,index)
            total_wvq = self.format_data_number(item)
            lat, lon = item[0][3], item[0][4]
            # order_id = str(item[0][7])
            order_id = item[0][7]
            if order_id == None:
                order_id = None
            else:
                order_id = str(item[0][7])

            order_no = str(item[0][0])
            order_ids = ""
            item_note = item[0][9]
            request_group = item[0][10]
            shop_type = item[0][11]
            ship_to_type = item[0][12]
            
            if index == 0:
                order_point = 0
            else:
                order_point = len(item) 
            
            if [lat,lon] not in drop_mode_order:
                drop_mode_order.append([lat, lon])
                
            if self.mode_option:
                if index == 0:
                    order_point = 0
                else:
                    order_point = len(order_no.split(","))
                order_ids = order_id
                order_id = ""

            response["Orders"].append(
                {
                    "Seq": index + 1,
                    "OrderNo": order_no,
                    "OrderId": order_id,
                    "ShipTo": item[0][1],
                    "ShipToCode": item[0][8],
                    "Qty": item[0][2],
                    "Lat": lat,
                    "Lon": lon,
                    "Weight": item[0][5],
                    "Volume": item[0][6],
                    "ETA": eta_etd[index][0],
                    "ETD": eta_etd[index][1],
                    "OrderCount":str(order_point),
                    "WVQ":total_wvq,
                    "OrderIds":order_ids,
                    "ItemNote":item_note,
                    "RequestGroup":request_group,
                    "ShopType":shop_type,
                    "ShipToType":ship_to_type
                }
            )
        response["Drops"] = len(drop_mode_order) - 1
        return response
    
    def format_data_number(self, data):
        return f"{round(data[0][5],3)}"+ "/" + f"{round(data[0][6],3)}" + "/" + f"{round(data[0][2],3)}"
    def remove_data_duplicate_for_drop_point(self, trips):
        drop, order = 0, 0
        orders_obj = {}
        data = []
        
        
        for item in trips:
            order += 1
            drop += 1
            lat, lon = item[0][3], item[0][4]
            order_no, order_id = item[0][0], item[0][7]
            qty, volume, weight = item[0][2], item[0][6], item[0][5]
        
            if (lat, lon) not in orders_obj:
                
                orders_obj[(lat, lon)] = {
                    "order_no": order_no,
                    "order_id": str(order_id),
                    "qty": qty,
                    "weight": weight,
                    "volume": volume,
                    "item": item  
                }
                data.append(item)
            else:
                drop -= 1
                obj = orders_obj[(lat, lon)]
                obj["order_no"] += "," + order_no
                obj["order_id"] += "," + str(order_id)
                obj["qty"] += qty
                obj["weight"] += weight
                obj["volume"] += volume
        
                obj_item = obj["item"]
                obj_item[0][0] = obj["order_no"]
                obj_item[0][7] = obj["order_id"]
                obj_item[0][2] = obj["qty"]
                obj_item[0][5] = obj["weight"]
                obj_item[0][6] = obj["volume"]
        return data
    def convent_data_tsp(self, path):
        routes = []
        for items in path:
            lat = items[0]
            lon = items[1]
            for item in self.orders:
                temp_point = [] 
                if lat == item[3] and lon == item[4] and item not in temp_point:
                        temp_point.append(item)
                        self.orders.remove(item)
                if temp_point:
                    routes.append(temp_point)
                    
        for idx, item in enumerate(routes):
            if len(item) == 2:
                routes.insert(idx + 1, [item[-1]])
                item.remove(item[-1])
            if item == []:
                routes.remove(item)  
        return routes
        
    def convent_data_path(self, point):
        path = []
        for item in point:
            path.append([float(item[0]),float(item[1])])
        return path

    def time_route(self, start_time, end_time):
        time = end_time - start_time
        hours, remainder = divmod(time.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        str_time = f"""{hours} giờ {minutes} phút"""
        return str_time

    def convent_eta_etd(self, data):
        time_eta_etd = []
        for items in data:
            eta = items[0].strftime(FORMAT_TIME)
            etd = items[1].strftime(FORMAT_TIME)
            time_eta_etd.append([eta, etd])
        return time_eta_etd

    def convent_time_start(self, time):
        return datetime.strptime(time, FORMAT_TIME)

    def convent_time_end(self, data):
        return datetime.strptime(data, FORMAT_TIME).time()
         

    def cal_ETA_ETD(self, data, path, file_name, mode_return):
        """
            Fix code many function
        """
        start_time = data["StartTime"]
        end_time = datetime.strptime(data["EndTime"], FORMAT_TIME)
        
        route = self.convent_data_path(path)
        time = self.convent_time_start(start_time)
        start_route = (time, time)
        
        data_time = self.calculate_time_eta_etd(time, route, data)
        eta_etd = self.set_value_eta_etd(data_time, start_route, mode_return, route)
        
        start_Time = datetime.combine(datetime.today(), self.convent_time_end(start_time))
        total_time = self.time_route(start_Time, eta_etd[-1][1])
        if self.mode_option:
            eta_etd = self.remove_data_duplicate(eta_etd)
            
        timeLine = self.getDataTimeLine(start_time, eta_etd, file_name, mode_return, end_time)
        
        return self.convent_eta_etd(eta_etd), total_time

    def calculate_time_eta_etd(self, time, route, data):
        waiting_before_time = data["WattingBeforeTime"]
        waiting_after_time = data["WattingAfterTime"]
        congestion_weight = data["CongestionWeight"]
        service_time = data["ServiceTime"]
        congestion_time = self.set_value_congestion_weight(congestion_weight)
        
        eta_etd = []
        for i in range(len(route)):
            origin = f"{route[i][0]},{route[i][1]}"
            destination = (f"{route[i + 1][0]},{route[i + 1][1]}" if i + 1 < len(route) else origin)
            distance = DataGoogleMapAPI().get_distance(origin, destination)
            if distance is not None:
                traffic_time = distance + (distance * congestion_time)
                time = time + timedelta(minutes = traffic_time)
                estimated_time = (
                    time
                    + timedelta(minutes = waiting_before_time)
                    + timedelta(minutes = service_time)
                    + timedelta(minutes = waiting_after_time)
                )
                eta_etd.append((time, estimated_time))
                time = estimated_time + timedelta(minutes = traffic_time)
        return eta_etd

    def set_value_congestion_weight(self, time):
        # traffic jam time hour
        config_time = [0,1,2,3]
        
        if time < config_time[0] or time > config_time[-1]:
            return abort(400, "The Congestion Weight value only accepts values from 0 to 3")
        elif time in config_time:
            congestion_time = int(time)
        else:
            congestion_time = float(time)
            
        return congestion_time

    def set_value_eta_etd(self, eta_etd, start_route, mode_return, route):
        eta_etd.insert(0, start_route)
        eta_etd.pop()
        eta_etd = self.set_value_duplicated(route, eta_etd, mode_return)
        if mode_return == False:
            return eta_etd
        else:
            time_convent = [list(item) for item in eta_etd]
            time_convent[-1][1] = time_convent[-1][0]
            return time_convent

    def set_value_duplicated(self, data, time, mode):
        index_data = self.find_index_duplicate(data)
        time = [list(item) for item in time]
        time_end = time[-1]
        for value in index_data:
            time[value] = time[value - 1]
        if mode == True:
            time[-1] = time_end
        return time

    def find_index_duplicate(self, data):
        set_value = []
        duplicate = []
        for index, item in enumerate(data):
            if item not in set_value:
                set_value.append(item)
            else:
                duplicate.append(index)
        return duplicate

    def save_file_map_tsp(self, data):
        name = get_content_for_user_id("tsp", self.user_id)
        self.time_line_name = name[3:]
        save_file(data, name)

    def convent_time_line_data(self, data):
        temp = 0
        for item in data:
            if item[0] == item[1]:
                temp += 1
            else:
                temp = 0
        data_time = self.set_value_duplicate_time(temp, data)
        return data_time

    def set_value_duplicate_time(self, number, data):
        time_format = FORMAT_TIME_LINE
        time_config = []
        if number >= len(data):
            for item in data:
                eta = item[0] + timedelta(minutes=20)
                etd = item[1] + timedelta(minutes=40)
                start_time = eta.strftime(time_format)
                end_time = etd.strftime(time_format)
                time_config.append([start_time, end_time])
                eta = etd + timedelta(minutes=90)
        else:
            for item in data:
                start_time = item[0].strftime(time_format)
                end_time = item[1].strftime(time_format)
                time_config.append([start_time, end_time])
        return time_config

    def getDataTimeLine(self, time, items, file_name, mode_return, end_time_work):
        """
            Fix parameter function
        """
        start_time = str(datetime.strptime(time, FORMAT_TIME) - timedelta(minutes=60))
        end_time = str(items[-1][1])
        
        data = self.convent_time_line_data(items)
        html = TimeLineRoute().showDataTimeLine(start_time, end_time, data, file_name, mode_return, end_time_work, self.time_line_name)
        
        return html
