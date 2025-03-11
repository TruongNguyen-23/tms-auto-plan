class NearestNeighbor:
    def __init__(self):
        print("NearestNeighbor")

    def tsp_nearest_neighbor(distance_matrix, start_point_index, points, on, off):
        def find_nearest_neighbor(distance_matrix, current_vertex, visited):
            nearest_neighbor = None
            min_distance = float("inf")

            for v in range(len(distance_matrix)):
                if not visited[v] and distance_matrix[current_vertex][v] < min_distance:
                    nearest_neighbor = v
                    min_distance = distance_matrix[current_vertex][v]
            return nearest_neighbor

        num_vertices = len(distance_matrix)
        visited = [False] * num_vertices
        path = [start_point_index]
        current_vertex = start_point_index
        visited[start_point_index] = True
        total_distance = 0.0

        for _ in range(num_vertices - 1):
            nearest_neighbor = find_nearest_neighbor(
                distance_matrix, current_vertex, visited
            )
            path.append(nearest_neighbor)
            visited[nearest_neighbor] = True
            total_distance += distance_matrix[current_vertex][nearest_neighbor]
            current_vertex = nearest_neighbor
        if on == True:
            path.append(start_point_index)
            total_distance += distance_matrix[current_vertex][start_point_index]
        elif off == True:
            total_distance
        tsp_path_latlon = [(points[idx][0], points[idx][1]) for idx in path]
        return tsp_path_latlon, total_distance
