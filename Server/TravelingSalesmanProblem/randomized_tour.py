import random
class RandomizedTour:
    def __init__(self):
        print("Randomized_Tour")

    @staticmethod
    def randomized_tour(distance_matrix, start_point_index, on, off):
        n = len(distance_matrix)
        tour = [i for i in range(n)]
        random.shuffle(tour)
        start_index = tour.index(start_point_index)
        tour.insert(0, tour.pop(start_index))
        total_distance = 0
        if on == True:
            for i in range(n):
                total_distance += distance_matrix[tour[i]][tour[(i + 1) % n]]
            tour.append(tour[0])
        if off == True:
            for i in range(n - 1):
                total_distance += distance_matrix[tour[i]][tour[(i + 1) % n]]
        return tour, total_distance
