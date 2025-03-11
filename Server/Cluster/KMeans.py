from Server.Process.Distance.distance_Matrix import DistanceMatrix

def cluster_labels(orders, start_point):
    data_cluster = {"Points": [], "Centroid": [], "Trip": [], "Labels": []}
    area = list(set(item["AreaDesc"] for item in orders))
    for i in range(len(area)):
        trip_orders = []
        location = []
        for j in range(len(orders)):
            if orders[j]["AreaDesc"] == area[i]:
                location.append([float(orders[j]["Lat"]), float(orders[j]["Lon"])])
                orders[j]["Labels"] = i + 1
                trip_orders.append(orders[j])
                data_cluster["Labels"].append(i + 1)
        # Add start point to route distance
        location.insert(0,start_point)
        center_point = DistanceMatrix.calculate_centroid(location)
        data_cluster["Trip"].append(trip_orders)
        data_cluster["Points"].append(location)
        data_cluster["Centroid"].append(center_point)
    data_cluster["Direction"] = DistanceMatrix.calculate_distance_route(data_cluster["Points"])
    data_cluster["Radius"] = DistanceMatrix.calculate_radius_cluster(data_cluster["Points"], data_cluster["Centroid"])
    return data_cluster
