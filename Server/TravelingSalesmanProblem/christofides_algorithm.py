import networkx as nx
import math


class Christofides:
    def __init__(self):
        print("Christofides Algorithm")

    def convent_route(self, route, point):
        data = [point[i] for i in route]
        return data

    def use_christofides(self, point, start_point, on_return, mode_start):
        try:
            if mode_start == True:
                point.insert(0, start_point)
            n = len(point)
            G = nx.complete_graph(n)

            def haversine(lat1, lon1, lat2, lon2):
                R = 6371
                dlat = math.radians(lat2 - lat1)
                dlon = math.radians(lon2 - lon1)
                a = (
                    math.sin(dlat / 2) ** 2
                    + math.cos(math.radians(lat1))
                    * math.cos(math.radians(lat2))
                    * math.sin(dlon / 2) ** 2
                )
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                return R * c

            dist_matrix = [
                [haversine(lat1, lon1, lat2, lon2) for lat2, lon2 in point]
                for lat1, lon1 in point
            ]
            tsp_tour = nx.approximation.traveling_salesman_problem(G, cycle=True)
            if on_return == True:
                total_distance = sum(
                    dist_matrix[i][j] for i, j in zip(tsp_tour, tsp_tour[1:])
                )
            else:
                tsp_tour = tsp_tour[:-1]
                total_distance = sum(
                    dist_matrix[i][j] for i, j in zip(tsp_tour, tsp_tour[1:])
                )
            route = self.convent_route(tsp_tour, point)
            cost = round(total_distance, 3)
            return route, cost
        except ValueError as e:
            print("Log Error", e)

