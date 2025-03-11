from flask_restx import fields
from .api import api

order_models = api.model(
    "Orders",
    {
        "OrderIds": fields.String,
        "OrderNo": fields.String,
        "ShipTo": fields.String,
        "ShipToCode": fields.String,
        "Lat": fields.String,
        "Lon": fields.String,
        "Qty": fields.Float,
        "Weight": fields.Float,
        "Volume": fields.Float,
        "ETA": fields.String,
        "ETD": fields.String,
        "Seq": fields.Integer,
        "AreaDesc": fields.String,
        "AreaCode": fields.String,
        "ItemNo": fields.String,
        "PickupCode": fields.String,
        "PickupName": fields.String,
        "PickupLat": fields.String,
        "PickupLon": fields.String,
        "WVQ": fields.String,
        "OrderCount": fields.Integer,
        "ParentAreaCode": fields.String,
        "Region": fields.String,
        "ItemNote": fields.String,
        "RequestGroup": fields.String,
        "ShopType": fields.String,
        "ShipToType": fields.String,
        "InfoChange": fields.Boolean,
        "TripType": fields.String,
        "DeliveryDate": fields.String,
        "PickUpID": fields.String,
        "ShipToID": fields.String,
        "Priority": fields.Integer,
        "RequestTruckType": fields.String,
        "ArrivalTime": fields.String,
        "COD": fields.Float,
        "CODAmount": fields.Float,
        "OtherRefNo1":fields.String,
        "OrderPriority": fields.Integer,
        "ShipToAddress": fields.String,
        "RouteDesc":fields.String
    },
)
equipment_trip = api.model(
    "Equipment Type",
    {
        "EquipmentType": fields.String,
        "Length": fields.Float,
        "Width": fields.Float,
        "Height": fields.Float,
        "Volume": fields.Float,
        "VolumeUnit": fields.String,
        "Weight": fields.Float,
        "WeightUnit": fields.String,
    },
)

# models api tsp
tsp_model = api.model(
    "Tsp",
    {
        "StartPoint": fields.Nested(order_models),
        "Orders": fields.List(fields.Nested(order_models)),
        "NameTSP": fields.String,
        "StartTime": fields.String,
        "EndTime": fields.String,
        "WattingBeforeTime": fields.Integer,
        "WattingAfterTime": fields.Integer,
        "ServiceTime": fields.Integer,
        "CongestionWeight": fields.Float,
        "ModeReturn": fields.Boolean,
        "UserID": fields.String,
        "CustomerCode": fields.String,
        "MapOption": fields.String,
        "ModeDropPoint": fields.Boolean
    },
)
model_trip = api.model(
    "Trip",
    {
        "OrderId": fields.Integer,
        "OrderNo": fields.String,
        "ShipTo": fields.String,
        "Lat": fields.String,
        "Lon": fields.String,
        "Qty": fields.Float,
        "Weight": fields.Float,
        "Volume": fields.Float,
        "ETA": fields.String,
        "ETD": fields.String,
    },
)
merge_trip = api.model(
    "Trips",
    {
        "TripNo": fields.String,
        "Orders": fields.Integer,
        "Drops": fields.Integer,
        "Area": fields.String,
        "AreaCode": fields.String,
        "RouteDesc":fields.String,
        "TotalShipTo":fields.String,
        "ParentAreaCode": fields.String,
        "Region": fields.String,
        "RouteDistance": fields.Float,
        "Equipment": fields.String,
        "Driver": fields.String,
        "DriverID": fields.String,
        "EquipmentType": fields.String,
        "Capacity": fields.String,
        "WVQ": fields.String,
        "LoadRate": fields.Float,
        "Weight": fields.Float,
        "Volume": fields.Float,
        "EquipmentTypes": fields.Float,
        "CapacityFactor": fields.String,
        "CentroidLat": fields.String,
        "CentroidLon": fields.String,
        "OrdersClusters": fields.List(fields.Nested(order_models), required=True),
    },
)
order_model = api.model(
    "Cluster",
    {
        "Orders": fields.List(fields.Nested(order_models)),
        "Trips": fields.List(fields.Nested(merge_trip)),
        "DistanceMergeRoute":fields.Integer,
        "PercentMergeRoute":fields.Float,
        "CapacityPercent":fields.Integer,
        "MergeTrip":fields.Boolean,
        "SplitCapacity":fields.Boolean,
        "NumberCluster": fields.String,
        "NameAlgorithmsCluster": fields.String,
        "CapacityFactor": fields.String,
        "Radius":fields.String,
        "UserID":fields.String,
        "CustomerCode":fields.String,
        "MapOption":fields.String,
        "DropsPoint":fields.Integer,
        "EquipmentType": fields.Nested(equipment_trip),
    },
)
model_merge_trip = api.model(
    "Merge",
    {
        "LstCluters": fields.List(fields.Nested(merge_trip)),
        "UserID":fields.String,
        "CustomerCode":fields.String
    },
    
)
# model get file time line
# model_time_line = api.model("TimeLine", {"Id": fields.Integer(required=True)})
