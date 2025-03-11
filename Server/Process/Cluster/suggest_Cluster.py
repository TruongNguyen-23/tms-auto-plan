from Server.Process.ActionUser.action_calculate_time import timer_func
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import silhouette_score
from kneed import KneeLocator
import numpy as np

class Suggest:
    def __init__(self):
        print("Suggest Data Cluster")
        
    @timer_func
    def suggest_number_cluster(orders): # elbow method
        if len(orders) <= 1:
            return 1
        else:
            sse = []
            location = []
            for item in orders:
                if len(item) == 2:
                    lat, lon = map(float, item)
                else:
                    lat, lon = item[1], item[2]
                location.append([lat, lon])
            k_values = range(1, len(location))
            for k in k_values:
                k_means = MiniBatchKMeans(n_clusters=k)
                k_means.fit(location)
                sse.append(k_means.inertia_)
            kl = KneeLocator(k_values, sse, curve="convex", direction="decreasing")
            if kl.elbow is None:
                optimal_k = len(location)
            else:
                optimal_k = int(kl.elbow)
            return optimal_k
        
    @ timer_func
    def gap_statistic_method(data): # gap method
        orders= [[float(item[1]),float(item[2])] for item in data]
        input_data = np.array(orders)
        max_clusters = len(orders)
        n_refs = max_clusters
        gaps = np.zeros((len(range(1, max_clusters)),))
        for gap_index, k in enumerate(range(1, max_clusters)):
            ref_disps = np.zeros(n_refs)
            for i in range(n_refs):
                randomReference = np.random.random_sample(size=input_data.shape)
                km = KMeans(k)
                km.fit(randomReference)
                ref_disp = km.inertia_
                ref_disps[i] = ref_disp
            km = KMeans(k)
            km.fit(input_data)
            orig_Disp = km.inertia_
            gap = np.log(np.mean(ref_disps)) - np.log(orig_Disp)
            gaps[gap_index] = gap
        return gaps.argmax() + 1
        
    @ timer_func
    def silhouette_method(data): 
        range_n_clusters = [item + 2 for item in range(len(data)) if item + 2 < len(data)]
        arr_silhouette_score = []
        orders= [[float(item[1]),float(item[2])] for item in data]
        input_data = np.array(orders)
        for n_clusters in range_n_clusters:
            cluster = KMeans(n_clusters=n_clusters)
            cluster_labels = cluster.fit_predict(input_data)
            silhouette_avg = silhouette_score(input_data, cluster_labels)
            arr_silhouette_score.append(silhouette_avg)
        number_cluster = arr_silhouette_score.index(max(arr_silhouette_score)) + 1
        return number_cluster