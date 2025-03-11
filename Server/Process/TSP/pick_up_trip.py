from Server.Map.mapMutiplePickUp.map_mutiple_pick_up import RouteMultiple
from Server.Process.ActionUser.action_calculate_time import get_content_for_user_id
from Server.Process.Handle.handle_file import save_file
from Server.Process.Distance.distance_google_map import DataGoogleMapAPI
from Server.Process.Distance.distance_Matrix import DistanceMatrix
from Server.Map.time_line import TimeLineRoute
from datetime import datetime, timedelta
from geopy.distance import geodesic
from flask import abort
import numpy as np


class PickUpTrip:
    def __init__(self):
        self.startPoint, self.pickUp, self.route = [], [], []
        self.tempPickUp, self.tempOrder = [], []
        self.tempStartPoint = []
        self.nameTimeLine = ""
        self.modeReturn = False
        self.modelData = []
        self.modelStart = []
        self.orders = []
        self.modelPickUp = []
        self.userId = ""
        self.customer = ""
        self.timeLineName = ""

    def ruleTrip(self, data, userId, customer):
        self.userId = userId
        self.customer = customer
        self.handleData(data)
        self.routeMultiplePickUp()
        return self.calDistanceDataRoute(data)

    def handleData(self, data):
        keys = [
            "OrderNo",
            "ShipTo",
            "Qty",
            "Lat",
            "Lon",
            "Weight",
            "Volume",
            "OrderId",
            "ShipToCode",
        ]
        
        self.startPoint = [
            float(data["StartPoint"]["Lat"]),
            float(data["StartPoint"]["Lon"]),
        ]
        # Update data start point in 05/12/2024
        
        self.tempStartPoint = self.startPoint.copy()
        self.setDataOrderPickUp(keys, data)
        for item in self.pickUp:
            self.tempPickUp.append([str(item["location"][0]), str(item["location"][1])])
        dateTimeLine = datetime.now()
        self.nameTimeLine = dateTimeLine.strftime("%d%m%H%M%S")
        self.modelStart = (
            list(map(data["StartPoint"].get, keys)) if data["StartPoint"] else False
        )
        self.modeReturn = data["ModeReturn"]
        self.route.append(self.startPoint)

    def setDataOrderPickUp(self, key, data):
        loopPickUp = []
        orderPickUp = []
        for item in data["Orders"]:
            self.modelData.append([item.get(key) for key in key])
            latPick = item["PickupLat"]
            lonPick = item["PickupLon"]
            point = {"Lat": latPick, "Lon": lonPick}
            qty, weight, volume, orderId = 0, 0, 0, 0
            shipTo = item["PickupName"]
            if point not in loopPickUp:
                # if point["Lat"] != "" or point["Lon"] != "":
                loopPickUp.append({"Lat": point["Lat"], "Lon": point["Lon"]})
                self.modelPickUp.append(
                    [
                        "-2",
                        shipTo,
                        qty,
                        str(latPick),
                        str(lonPick),
                        weight,
                        volume,
                        orderId,
                        shipTo,
                    ]
                )
        for items in data["Orders"]:
            tempPickUp = []
            for pick in loopPickUp:
                # if pick["Lat"] != "" or pick["Lon"] != "":
                if (
                    pick["Lat"] == items["PickupLat"]
                    and pick["Lon"] == items["PickupLon"]
                ):
                    tempPickUp.append(
                        {
                            "location": [float(pick["Lat"]), float(pick["Lon"])],
                            "orders": [float(items["Lat"]), float(items["Lon"])],
                        }
                    )
            self.orders.append([float(items["Lat"]), float(items["Lon"])])
            orderPickUp.append(tempPickUp)

        for item in orderPickUp:
            location = item[0]["location"]
            orders = item[0]["orders"]
            found = False
            for loc_order in self.pickUp:
                if loc_order["location"] == location:
                    loc_order["orders"].extend([orders])
                    found = True
                    break
            if not found:
                self.pickUp.append({"location": location, "orders": [orders]})

    def processFindData(self, start, order, pickups):
        distanceOrder, distancePickup = [], []
        for o in order:
            distanceOrder.append(geodesic(start, o).kilometers)
        for pickup in pickups:
            distancePickup.append(geodesic(start, pickup["location"]).kilometers)
        return distanceOrder, distancePickup

    def routeMultiplePickUp(self):
        while self.pickUp:
            nearest_pickup = min(
                self.pickUp,
                key=lambda x: geodesic(self.startPoint, x["location"]).kilometers,
            )
            self.route.append(nearest_pickup["location"])
            orders_in_nearest_pickup = nearest_pickup["orders"]
            self.pickUp.remove(nearest_pickup)
            if self.pickUp:
                order, pick = self.processFindData(
                    nearest_pickup["location"], orders_in_nearest_pickup, self.pickUp
                )
                if min(order) <= min(pick):
                    if orders_in_nearest_pickup:
                        indexes_to_remove = []
                        for idx, distanceOrder in enumerate(order):
                            if distanceOrder < min(pick):
                                self.route.append(orders_in_nearest_pickup[idx])
                                indexes_to_remove.append(idx)
                            elif distanceOrder > max(
                                pick
                            ):  # greater than all three elements in pick
                                indexOfPick = pick.index(min(pick))
                                self.pickUp[indexOfPick]["orders"].append(
                                    orders_in_nearest_pickup[idx]
                                )
                                indexes_to_remove.append(idx)
                            else:  # greater than one of the three elements in pick
                                # print('cook')
                                indexOfPick = pick.index(min(pick))
                                self.pickUp[indexOfPick]["orders"].append(
                                    orders_in_nearest_pickup[idx]
                                )
                                indexes_to_remove.append(idx)
                        for index in sorted(indexes_to_remove, reverse=True):
                            del orders_in_nearest_pickup[index]
                    else:
                        print("No data Order")
                    sorted_orders = sorted(
                        orders_in_nearest_pickup,
                        key=lambda x: geodesic(
                            nearest_pickup["location"], x
                        ).kilometers,
                    )
                    self.route.extend(sorted_orders)
                    self.startPoint = self.route[-1]
                else:
                    idx = np.argmin(np.array([pick]))
                    temp = self.pickUp[idx]
                    nearest_pickup = nearest_pickup["location"]
                    temp["orders"].extend(orders_in_nearest_pickup)
                    self.startPoint = self.route[-1]

            else:
                sorted_orders = sorted(
                    orders_in_nearest_pickup,
                    key=lambda x: geodesic(nearest_pickup["location"], x).kilometers,
                )
                self.route.extend(sorted_orders)
        if self.modeReturn == True:
            self.route.append(self.tempStartPoint)
        else:
            return self.route
        return self.route, self.tempPickUp

    def saveFileTSP(self, data):

        file_name = get_content_for_user_id("tsp", self.userId)
        self.timeLineName = file_name[3:]
        save_file(data, file_name)

    def conventDataPickUp(self, pickUp):
        self.modelData.extend(self.modelPickUp)

    def calDistanceDataRoute(self, data):
        result = []
        file_name = get_content_for_user_id("tsp", self.userId)
        self.timeLineName = file_name[3:]
        costReal, timeReal = DataGoogleMapAPI().data_real_time(
            self.route
        )  # cal distance direction route
        costDirection = DistanceMatrix.calculate_route(self.route)
        etaETD, timeRoute = self.cal_ETA_ETD(
            data, self.route, self.nameTimeLine, self.modeReturn
        )  # cal eta etd and show result seq
        self.modelData.insert(0, self.modelStart)
        self.conventDataPickUp(data)
        for items in self.route:
            lat = str(items[0])
            lon = str(items[1])
            _q = []
            for item in self.modelData:
                if lat == item[3] and lon == item[4]:
                    _q.append(item)
            result.append(_q)
        response = {
            "Orders": [],
            "KmDirection": f"{round(costDirection,3)} km",
            "KmRoute": costReal,
            "TimeRoute": timeRoute,
            "TimeLineName": self.timeLineName,
        }
        # remove data arr empty
        temp = []
        for item in result:
            if item != []:
                temp.append(item)
        for index, item in enumerate(temp):
            response["Orders"].append(
                {
                    "Seq": index + 1,
                    "OrderNo": item[0][0],
                    "OrderId": item[0][7],
                    "ShipTo": item[0][1],
                    "ShipToCode": item[0][8],
                    "Qty": item[0][2],
                    "Lat": item[0][3],
                    "Lon": item[0][4],
                    "Weight": item[0][5],
                    "Volume": item[0][6],
                    "ETA": etaETD[index][0],
                    "ETD": etaETD[index][1],
                }
            )
        # save data html file map tsp
        dataHTML = RouteMultiple().show_Content(
            self.route, self.tempPickUp, self.modelData
        )
        print('file name start',file_name)
        save_file(dataHTML, file_name)
        print('file name end',file_name)
        # self.saveFileTSP(dataHTML)
        return response

    def cal_ETA_ETD(self, data, path, fileName, mode):
        time = self.conventTimeStartEnd(data["StartTime"], "Start")
        endTime = datetime.strptime(data["EndTime"], "%d/%m/%Y %H:%M")
        startRoute = (time, time)
        congestionTime = self.setValueCongestionWeight(data["CongestionWeight"])
        dataTime = self.calTimeEtaEtd(
            time,
            path,
            congestionTime,
            data["WattingBeforeTime"],
            data["ServiceTime"],
            data["WattingAfterTime"],
        )
        eta_ETD = self.setValueETAETD(dataTime, startRoute, mode, path)
        start_Time = datetime.combine(
            datetime.today(), self.conventTimeStartEnd(data["StartTime"], "End")
        )
        totalTime = self.time_Route(start_Time, eta_ETD[-1][1])
        timeLine = self.getDataTimeLine(
            data["StartTime"], eta_ETD, fileName, mode, endTime
        )
        return self.conventETAETD(eta_ETD), totalTime

    def setValueCongestionWeight(self, time):
        if time < 0 or time > 3:
            return abort(
                400, "The Congestion Weight value only accepts values from 0 to 3"
            )
        elif isinstance(time, int):
            return int(time)
        else:
            return float(time)

    def conventTimeStartEnd(self, time, name):
        formatTime = "%d/%m/%Y %H:%M"
        time_ = datetime.strptime(time, formatTime)
        if name == "Start":
            return time_
        elif name == "End":
            return time_.time()

    def calTimeEtaEtd(self, time, route, cgTime, wbTime, srTime, waTime):
        eta_ETD = []
        for i in range(len(route)):
            origin = f"{route[i][0]},{route[i][1]}"
            destination = (
                f"{route[i + 1][0]},{route[i + 1][1]}" if i + 1 < len(route) else origin
            )
            distance = DataGoogleMapAPI().get_distance(origin, destination)
            if distance is not None:
                traffic_Time = distance + (distance * cgTime)
                time = time + timedelta(minutes=traffic_Time)
                estimated_time = (
                    time
                    + timedelta(minutes=wbTime)
                    + timedelta(minutes=srTime)
                    + timedelta(minutes=waTime)
                )
                eta_ETD.append((time, estimated_time))
                # case if the congestion time cannot be transmitted
                # time = estimated_time + timedelta(minutes=traffic_Time)
                time = estimated_time
        return eta_ETD

    def setValueETAETD(self, etaEtd, startRoute, modeReturn, route):
        etaEtd.insert(0, startRoute)
        etaEtd.pop()
        if modeReturn == False:
            etaEtd = self.setValueDuplicated(route, etaEtd, modeReturn)
            return etaEtd
        else:
            etaEtd = self.setValueDuplicated(route, etaEtd, modeReturn)
            timeConvent = [list(item) for item in etaEtd]
            timeConvent[-1][1] = timeConvent[-1][0]
            return timeConvent

    def setValueDuplicated(self, data, time, mode):
        indexData = self.findIndexDuplicate(data)
        duplicateNear = self.findValueContinuousDuplicates(data)
        time = [list(item) for item in time]
        for item in duplicateNear:
            indexData.remove(item)
        timeEnd = time[-1]
        if duplicateNear:
            for dup in duplicateNear:
                time[dup] = time[dup - 1]
                # missing case update time
        if indexData:
            for value in indexData:
                time[value] = time[value]
        if mode == True:
            time[-1] = timeEnd
        return time

    def findValueContinuousDuplicates(self, data):
        duplicateNear = []
        # cal duplicate near
        for i in range(len(data) - 1):
            if data[i] == data[i + 1]:
                duplicateNear.append(i + 1)
        return duplicateNear

    def findIndexDuplicate(self, data):
        setValue = []
        duplicate = []
        for index, item in enumerate(data):
            if item not in setValue:
                setValue.append(item)
            else:
                duplicate.append(index)
        return duplicate

    def time_Route(self, start_Time, end_Time):
        time = end_Time - start_Time
        hours, remainder = divmod(time.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        str_Time = f"""{hours} giờ {minutes} phút"""
        return str_Time

    def getDataTimeLine(self, time, items, fileName, _return, endWorkTime):
        formatTime = "%d/%m/%Y %H:%M"
        timeFormat = datetime.strptime(time, formatTime) - timedelta(minutes=60)
        startTime = str(timeFormat)
        endTime = str(items[-1][1])
        data = self.conventTimeLineData(items)
        html = TimeLineRoute().showDataTimeLine(
            startTime, endTime, data, fileName, _return, endWorkTime, self.timeLineName
        )
        return html

    def conventTimeLineData(self, data):
        temp = 0
        for item in data:
            if item[0] == item[1]:
                temp += 1
            else:
                temp = 0
        dataTime = self.setValueDuplicateTime(temp, data)
        return dataTime

    def setValueDuplicateTime(self, num, data):
        _data = []
        if num >= len(data):
            for item in data:
                eta = item[0] + timedelta(minutes=20)
                etd = item[1] + timedelta(minutes=40)
                startTime = eta.strftime("%Y-%m-%d, %H:%M:%S")
                endTime = etd.strftime("%Y-%m-%d, %H:%M:%S")
                _data.append(
                    [startTime, endTime],
                )
                eta = etd + timedelta(minutes=90)
        else:
            for item in data:
                startTime = item[0].strftime("%Y-%m-%d, %H:%M:%S")
                endTime = item[1].strftime("%Y-%m-%d, %H:%M:%S")
                _data.append(
                    [startTime, endTime],
                )
        return _data

    def conventETAETD(self, data):
        _data = []
        for items in data:
            eta = items[0].strftime("%d/%m/%Y %H:%M")
            etd = items[1].strftime("%d/%m/%Y %H:%M")
            # eta = items[0].strftime("%H:%M")
            # etd = items[1].strftime("%H:%M")
            _data.append(
                [eta, etd],
            )
        return _data
