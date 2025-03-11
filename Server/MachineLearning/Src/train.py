from Server.Process.ActionUser.action_calculate_time import *
from Server.MachineLearning.Src.preprocess import *
from Server.Map.chart_bar import *
from dotenv import load_dotenv
import pickle

load_dotenv()
FEATURE_KEY = ['Volume','AreaCodes','ShipToLat', 'ShipToLon','PickupLat', 'PickupLon','Distance','EquipTypeNo','ShipToTypes']

def training_data(data):
    limit_truck = get_data_limit_truck(data)
    orders_data = data_predict_processing(data, limit_truck)

    model_file = "Server/MachineLearning/Models/model.pkl"
    
    if model_file:
        with open(model_file, 'rb') as file:
            model = pickle.load(file)

    orders_data['PredictedLabel'] = model.predict(orders_data[FEATURE_KEY])
    return orders_data, limit_truck
def get_data_limit_truck(data):
    if data["CapacityFactor"] == "V":
        limit_truck = data['EquipmentType']['Volume']
    return limit_truck
            
def trip_for_machine_learning(data):
    result = []
    orders_data, limit_truck = training_data(data)
    
    for label, group in orders_data.groupby('PredictedLabel'):
        current_group = []
        current_weight = 0

        for _, row in group.iterrows():
            # if current_weight + row['Volume'] > limit_truck:
            #     if current_group:
            #         result.append(current_group)
            #     current_group = []
            #     current_weight = 0
            current_group.append(row.to_dict())
            # current_weight += row['Volume']

        if current_group:
            result.append(current_group)
    # Handle to map chart result
    # random_color_for_trip(len(result["Trip"]))
    
    # html_cluster = MapCluster().show_map(trips, self.tripNo, self.mode_draw)
    # html_chart_cluster = TripChart().show_chart(trips, self.data_input)
    
    # save_file(html_cluster, self.cluster_file)
    # save_file(html_chart_cluster, self.chart_file)
    # save_content_cluster_cache(html_cluster, self.cluster_file)
    return result


 