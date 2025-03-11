def get_number_mode_capacity(capacity):
    if capacity == "Q":
        num = 6
    elif capacity == "W":
        num = 7
    elif capacity == "V":
        num = 8
    return num

def calculate_centroid(point):
    lat = sum(float(item[1]) for item in point)
    lon = sum(float(item[2]) for item in point)
    num_point = len(point)
    center_lat = lat / num_point
    center_lon = lon / num_point
    return [center_lat, center_lon]

def capacity_for_trip(trips, index):
    
    capacity = sum(trip[index] for trip in trips)
    location = [trip[5] for trip in trips]
    centroid = calculate_centroid(trips)
    return capacity, ','.join(location), centroid


def total_drop_points_for_trips(trips):
    location = []
    for trip in trips:
        lat = trip[1]
        lon = trip[2]
        if [lat,lon] not in location:
            location.append([lat,lon])
    total = len(location)
    return total


# def calculate_centroid(point):
#     lat = sum(float(item["Lat"]) for item in point)
#     lon = sum(float(item["Lon"]) for item in point)
#     num_point = len(point)
#     center_lat = lat / num_point
#     center_lon = lon / num_point
#     return [center_lat, center_lon]


def calculate_total_capacity(trip, index):
    
    total_weight_trip = 0
    for value in trip:
        if value != []:
            total_weight_trip += value[index]
    return total_weight_trip

def handle_trip_gt_mt_area(trips):
    trips = sorted(trips, key= lambda item : item[4])
    super_market = "MT"
    list_mt = []
    count_area = {}
    for idx in reversed(range(len(trips))):
        ship_to = trips[idx][4]
        if trips[idx][-1][:2] == super_market:
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
            count_area[list_mt[-1][4]] -= 1
            list_mt.pop(-1)
        else:
            pass
        for key, value in list(count_area.items()):
            if value == 0:
                del count_area[key]
        number_mt = len(count_area.keys())

    return list_mt, trips

def remove_order_in_trips(trip, order, equipment, index):
    remove = False
    orders = []
    
    while not remove:
        weight = sum(value[index] for value in trip)
        if weight > equipment and trip != [] and len(trip) > 1:
            trip = sum_weight_with_area(trip, equipment, index)
            if trip[-1][index] > equipment:
                order.append([trip[-1]])
            else:
                orders.append(trip[-1])
            trip.pop()
        else:
            remove = True
    return orders, trip

def sum_weight_with_area(area, equipment, index):
    i = 0
    while i < len(area):
        j = i + 1
        while j < len(area):
            if area[i][index] + area[j][index] > equipment:
                area[-1], area[j] = area[j], area[-1]
                j += 1
            else:
                break
        i += 1
    return area

# func fix
# def capacity_for_trip(trips, index):
    
#     capacity = sum(trip[index] for trip in trips)
#     location = [trip["AreaDesc"] for trip in trips]
#     centroid = calculate_centroid(trips)
#     return capacity, ','.join(location), centroid

# # func fix
# def get_number_mode_capacity(capacity):
#     if capacity == "Q":
#         num = "Qty"
#     elif capacity == "W":
#         num = "Weight"
#     elif capacity == "V":
#         num = "Volume"
#     return num
# def total_drop_points_for_trips(trips):
#     location = []
#     for trip in trips:
#         lat = trip["Lat"]
#         lon = trip["Lon"]
#         if [lat,lon] not in location:
#             location.append([lat,lon])
#     total = len(location)
#     return total