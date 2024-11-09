from sklearn.cluster import MeanShift, estimate_bandwidth
class MeanShift:
    def __init__(self):
        print("Mean Shift")

    def convent_point(self, data, labels,number):
        point = []
        for i in range(number):
            cluster_points = data[labels == i]
            point.append(cluster_points)
        return point

    def get_data_show_map(self, data,number):
        bandwidth = estimate_bandwidth(data, quantile=0.2)
        ms = MeanShift()
        ms.fit(data)
        data_center = ms.cluster_centers_.tolist()
        labels = ms.labels_
        data_point = self.convent_point(data, labels,number)
        return data_center, data_point

