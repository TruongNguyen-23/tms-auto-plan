from sklearn.cluster import MiniBatchKMeans


class MiniBathKMean:
    def __init__(self):
        print("Mini Bath K Mean")

    def get_DataMap(self, data, cluster):
        kmeans = MiniBatchKMeans(n_clusters=cluster, batch_size=1024, random_state=0)
        kmeans.fit(data)
        data_centers = kmeans.cluster_centers_.tolist()
        labels = kmeans.labels_
        data_point = self.convent_point(data, labels, cluster)
        return data_centers, data_point

    def convent_point(self, data, labels, cluster):
        point = []
        for i in range(cluster):
            cluster_points = data[labels == i]
            point.append(cluster_points)
        return point

