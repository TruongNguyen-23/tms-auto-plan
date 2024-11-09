from geopy.distance import great_circle
import networkx as nx
import random

class Ant:
    def __init__(self):
        print("Ant Colony Optimization")

    def convent_route(self, route, point):
        data = [point[i] for i in route]
        return data

    def calculate_cost(self, graph, path):
        cost = 0
        for i in range(len(path) - 1):
            cost += graph[path[i]][path[i + 1]]["distance"]
        return cost

    def calculate_distance(self, coord1, coord2):
        return great_circle(coord1, coord2).kilometers

    def ant_colony_optimization(
        self,
        on_Return,
        graph,
        num_ants,
        num_iterations,
        alpha,
        beta,
        evaporation_rate,
        start_node,
    ):
        num_nodes = len(graph.nodes())
        best_path = None
        best_cost = float("inf")
        try:
            for _ in range(num_iterations):
                ants = [[] for _ in range(num_ants)]

                for ant in ants:
                    ant.append(start_node)

                for _ in range(num_nodes - 1):
                    for ant in ants:
                        current_node = ant[-1]
                        unvisited_nodes = set(range(num_nodes)) - set(ant)

                        probabilities = []
                        total_pheromone = 0
                        for node in unvisited_nodes:
                            pheromone = graph[current_node][node]["pheromone"]
                            distance = graph[current_node][node]["distance"]
                            total_pheromone += (pheromone**alpha) * (distance**beta)

                        for node in unvisited_nodes:
                            pheromone = graph[current_node][node]["pheromone"]
                            distance = graph[current_node][node]["distance"]
                            probability = (
                                (pheromone**alpha) * (distance**beta)
                            ) / total_pheromone
                            probabilities.append(probability)

                        next_node = random.choices(
                            list(unvisited_nodes), probabilities
                        )[0]
                        ant.append(next_node)
            if on_Return == True:
                for ant in ants:
                    ant.append(start_node)

                for i in range(num_ants):
                    path = ants[i]
                    cost = self.calculate_cost(graph, path)
                    if cost < best_cost:
                        best_cost = cost
                        best_path = path
                    for j in range(num_nodes):
                        graph[path[j]][path[j + 1]]["pheromone"] += 1 / cost

                for edge in graph.edges():
                    graph[edge[0]][edge[1]]["pheromone"] *= 1 - evaporation_rate
                return best_path, best_cost
            else:
                for i in range(num_ants):
                    path = ants[i]
                    cost = self.calculate_cost(graph, path)
                    if cost < best_cost:
                        best_cost = cost
                        best_path = path
                    for j in range(num_nodes - 1):
                        graph[path[j]][path[j + 1]]["pheromone"] += 1 / cost

                for edge in graph.edges():
                    graph[edge[0]][edge[1]]["pheromone"] *= 1 - evaporation_rate

                best_path.remove(start_node)
                best_path = [start_node] + best_path
                return best_path, best_cost
        except ValueError as e:
            print("Log Error", e)

    def use_ant(self, point, start_Point, on_Return, mode_Start):
        try:
            if mode_Start == True:
                point.insert(0, start_Point)
            num_nodes = len(point)
            random.seed(42)
            graph = nx.complete_graph(num_nodes)
            for i in range(num_nodes):
                for j in range(i + 1, num_nodes):
                    distance = self.calculate_distance(point[i], point[j])
                    graph[i][j]["distance"] = distance
                    graph[j][i]["distance"] = distance
                    graph[i][j]["pheromone"] = 1.0
                    graph[j][i]["pheromone"] = 1.0

            start_node = 0
            best_path, best_cost = self.ant_colony_optimization(
                on_Return,
                graph,
                num_ants=20,
                num_iterations=100,
                alpha=1,
                beta=2,
                evaporation_rate=0.5,
                start_node=start_node,
            )
            route = self.convent_route(best_path, point)
            cost = round(best_cost, 3)
            return route, cost
        except ValueError as e:
            print("Log Error", e)