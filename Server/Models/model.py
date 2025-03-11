from flask_restx import fields
from datetime import time
from tms import *

order_models = api.model(
    "Orders",
    {
        "OrderNo": fields.String,
        "ShipTo": fields.String,
        "Lat": fields.Float,
        "Lon": fields.Float,
        "Qty": fields.Integer,
        "Weight": fields.Float,
        "Volume": fields.Float,
        "AreaDesc": fields.String,
        "AreaCode": fields.String,
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
order_model = api.model(
    "OrderModel",
    {
        "Orders": fields.List(fields.Nested(order_models)),
        "NumberCluster": fields.Integer,
        "NameAlgorithmsCluster": fields.String,
        "CapacityFactor": fields.String,
        "EquipmentType": fields.Nested(equipment_trip),
    },
)
# models api tsp
tsp_orders = api.model(
    "Order",
    {
        "OrderNo": fields.String,
        "ShipTo": fields.String,
        "Lat": fields.Float,
        "Lon": fields.Float,
        "Qty": fields.Integer,
        "Weight": fields.Float,
        "Volume": fields.Float,
    },
)
tsp_model = api.model(
    "TspModel",
    {
        "StartPoint": fields.Nested(tsp_orders),
        "Orders": fields.List(fields.Nested(tsp_orders)),
        "NameTSP": fields.String,
        "StartTime": fields.String,
        "WattingBeforeTime": fields.Integer,
        "WattingAfterTime": fields.Integer,
        "ServiceTime": fields.Integer,
        "CongestionWeight": fields.Float,
        "ModeReturn": fields.Boolean,
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
        "Qty": fields.Integer,
        "Weight": fields.Float,
        "Volume": fields.Float,
        "ETA": fields.String,
        "ETD": fields.String,
    },
)
model_merge_trip = api.model(
    "Merge",
    {
        "TripNo": fields.String,
        "Orders": fields.Integer,
        "Drops": fields.Integer,
        "Area": fields.String,
        "RouteDistance": fields.String,
        "Equipment": fields.String,
        "Driver": fields.String,
        "DriverID": fields.String,
        "EquipmentType": fields.String,
        "Capacity": fields.String,
        "WVQ": fields.String,
        "LoadRate": fields.String,
        "Weight": fields.String,
        "EquipmentTypes": fields.Float,
        "CapacityFactor": fields.String,
        "OrdersClusters": fields.List(fields.Nested(order_models), required=True),
    },
)
# model get file time line
model_time_line = api.model("TimeLine", {"Id": fields.Integer(required=True)})
