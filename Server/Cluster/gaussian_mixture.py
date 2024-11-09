from sklearn.mixture import GaussianMixture
class Gausian:
    def __init__(self):
        print("Gausian Mixture")

    def convent_point(self, data, labels, cluster):
        point = []
        for i in range(cluster):
            cluster_points = data[labels == i]
            point.append(cluster_points)
        return point

    def get_data_show_map(self, data, cluster):
        gmm = GaussianMixture(n_components=cluster, random_state=0)
        gmm.fit(data)
        labels = gmm.predict(data)
        means = gmm.means_
        data_point = self.convent_point(data, labels, cluster)
        data_center = [[items[0], items[1]] for items in means]

        return data_center, data_point

