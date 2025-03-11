from Server.MachineLearning.Src.split_data_order import *
from sklearn import preprocessing
import pandas as pd
import numpy as np

# Create pipline here
label_encoder = preprocessing.LabelEncoder()

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    return 6371 * 2 * np.arcsin(np.sqrt(a))

def encode_features(df, key):
    df['ShipToTypes'] = label_encoder.fit_transform(df['ShipToType'].astype(str))
    df['AreaCodes'] = label_encoder.fit_transform(df['AreaCode'].astype(str))
    df['EquipTypeNo'] = df.groupby(key)['Volume'].transform('sum')
    df['PickupLat'] = df['PickupLat'].astype(float)
    df['PickupLon'] = df['PickupLon'].astype(float)
    df['ShipToLat'] = df['Lat'].astype(float)
    df['ShipToLon'] = df['Lon'].astype(float)
    df['Distance'] = haversine(df['PickupLat'], df['PickupLon'], df['ShipToLat'], df['ShipToLon'])
    return df
   
def data_predict_processing(data, limit_truck):
    orders_data = pd.DataFrame.from_dict(data["Orders"])
    # split_orders = []
    
    # for index, row in orders_data.iterrows():
    #     order = row.to_dict()
    #     split_result = split_order(order, limit_truck)
    #     split_orders.extend(split_result)
        
    # orders_data = pd.DataFrame(split_orders)
    orders_data = encode_features(orders_data,"OrderId")
    return orders_data

