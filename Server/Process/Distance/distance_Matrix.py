from Server.TravelingSalesmanProblem.nearest_neighbor import NearestNeighbor
from math import radians, sin, cos, sqrt, atan2
from geopy.distance import great_circle
import numpy as np

RADIUS_DEFAULT = 1000
RADIANS = 6371.0


class DistanceMatrix:
    def __init__(self):
        print("Distance Matrix")

    def calculate_distances(data):
        def euclidean_distance(point1, point2):
            distances = great_circle(point1, point2).kilometers

            distances = round(distances, 3)

            return distances

        num_points = len(data)
        distances = [[0 for _ in range(num_points)] for _ in range(num_points)]

        for i in range(num_points):
            for j in range(i + 1, num_points):
                distance = euclidean_distance(data[i], data[j])
                distances[i][j] = distance
                distances[j][i] = distance
        return distances

    def calculate_route(route):
        def haversine_distance(lat1, lon1, lat2, lon2):
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = RADIANS * c

            return distance

        total_distance = 0
        for i in range(len(route) - 1):
            lat1, lon1 = route[i]
            lat2, lon2 = route[i + 1]
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            total_distance += distance
        return total_distance

    # haversine cluster and tsp
    def haversine_distance(coord1, coord2):
        lat1, lon1 = np.radians(list(coord1))
        lat2, lon2 = np.radians(list(coord2))
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            np.sin(dlat / 2) ** 2
            + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
        )
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        distance = RADIANS * c
        return distance

    def set_default_value_radius(radius, center):
        data = []
        for i in range(len(center)):
            data.append(radius * RADIUS_DEFAULT)
        return data

    def calculate_radius_cluster(points, center):
        radius = []
        for i, group in enumerate(points):
            max_distance = 0
            for point in group:
                distance = DistanceMatrix.haversine_distance(point, center[i])
                if distance > max_distance:
                    max_distance = distance
            radius.append(max_distance)
        radius = np.array(radius) * RADIUS_DEFAULT
        return radius

    def calculate_centroid(data):
        num_point = len(data)
        lat = sum(item[0] for item in data)
        lon = sum(item[1] for item in data)
        center_lat = lat / num_point
        center_lon = lon / num_point

        return [center_lat, center_lon]

    def calculate_weight_start(data, next, prev, index):
        start = sum(trip_start[index] for trip_start in data[next])
        end = sum(trip_end[index] for trip_end in data[prev])
        return start, end
    
    def calculate_distance_route(point):
        direction = []
        temp = 0
        for items in point:
            distance = DistanceMatrix.calculate_distances(items)
            _path, _cost = NearestNeighbor.tsp_nearest_neighbor(
                distance, temp, items, False, True
            )
            direction.append(round(_cost, 3))
        return direction
