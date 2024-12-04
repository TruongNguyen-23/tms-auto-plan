# from Server.Process.Handle.handle_file import render_content_file_HTML, option_menu_data
# from Server.Process.ActionUser.action_for_trip import user_action_trip
# from Server.TemplateDefault.cluster_default import ClusterDefault
# from Server.TemplateDefault.chart_default import TripChartDefault
# from Server.Process.Trips.trip_confirm import TripClusterConfirm
# from Server.Process.Cluster.merge_cluster import MergerCluster
# from Server.Process.Cluster.kmeans_cluster import Process_Data
# from Server.Process.Cluster.merge_trip_view import MergeTrip
# from Server.Map.map_trip_location import MapTripLocation
# from flask import Flask, request, abort, make_response
# from flask_restx import Resource, Api, reqparse
# from Server.Process.TSP.tsp import ProcessTSP
# from Server.Models.model import order_model
# import json



# app = Flask(__name__)
# api = Api(app, version='1.0', title='API TMS', description='TMS Auto Plan')

# class ClusterResource(Resource):
#     def get(self):
#         return "API TMS"
    
# api.add_resource(ClusterResource, "/")

# class Algorithm(Resource):
#     def get(self, name):
#         arr_data = []
#         f = open("filter.json")
#         data = json.load(f)
#         for items in data["Filter"]:
#             for item in items[name.capitalize()]:
#                 arr_data.append(item)
#         f.close()
#         return arr_data
    
# api.add_resource(Algorithm, "/algorithm/<string:name>")

# class DrawMap(Resource):
#     def get(self, option):
#         return option_menu_data(option)
    
# api.add_resource(DrawMap, "/get/data/<string:option>")


# # api show content data file html to link
# # @api.route(
# #     "/get/map/<string:file>",
# # )
# class MapRoute(Resource):
#     def get(self, file):
#         file_name = f"{file}.html"
#         if request:
#             data = request.get_json()
#             file_name = f"{file}{data}.html"
#         return render_content_file_HTML(file_name)

#     def post(self, file):
#         try:
            
#             file_name = f"{file}.html"
#             if file_name == "trip.html":
#                 data = request.get_json()
#                 return MapTripLocation().handle_data(data, file)
#             else:
#                 data = request.get_json()
#                 file_name = f"{file}{data}.html"
#                 if data:
#                     return render_content_file_HTML(file_name)
#                 else:
#                     if file_name == "clusterNone.html" or file_name == "cluster.html":
#                         response = make_response(ClusterDefault().show_map())
#                     elif file_name == "charttripNone.html" or file_name == "charttrip.html":
#                         response = make_response(TripChartDefault().show_chart_bar())
#                     response.headers["Content-Type"] = "text/html"
#                     return response
#         except ValueError as e:
#             raise ("Log Error", e)
        
# api.add_resource(MapRoute, "/get/map/<string:file>")

# # api timeLine
# # model_time_line = api.model("TimeLine", {"Id": fields.Integer(required=True)})
# class TimeLine(Resource):
#     # @api.expect(model_time_line)
#     def get(self, timeLineID):
#         if timeLineID:
#             file_name = f"timeline{timeLineID}.html"
#             return render_content_file_HTML(file_name)
#         else:
#             data = {
#                 "errorCode": 202,
#                 "errMessage": "No file name is not exits",
#                 "fileName": file_name,
#             }
#             return abort(202, data)
        
# api.add_resource(TimeLine, "/get/map/timeline<timeLineID>")

# # api get data: trip or cluster order
# class ClusterKmean(Resource):
#     parser = reqparse.RequestParser()
#     parser.add_argument("data", type=dict, required=True, location="json")

#     @api.expect(order_model)
#     def post(self):
#         try:
#             data = request.get_json()
#             result = Process_Data().process_cluster_algorithms(data)
#             return result
#         except ValueError as e:
#             raise ("Log Error", e)
        
# api.add_resource(ClusterKmean, "/get/data/cluster")

# # api merge cluster:
# class ClusterMerge(Resource):
#     parser = reqparse.RequestParser()
#     parser.add_argument("data", type=dict, required=True, location="json")

#     # @api.expect(model_merge_trip)
#     def post(self): 
#         try:
#             data = request.get_json()
#             result = MergerCluster().merge_trip(data)
#             return result
#         except ValueError as e:
#             raise ("Log Error", e)
        
# api.add_resource(ClusterMerge, "/get/data/merge/cluster")

# class TripMerge(Resource):
#     parser = reqparse.RequestParser()
#     parser.add_argument("data", type=dict, required=True, location="json")

#     # @api.expect(model_merge_trip)
#     def post(self):
#         try:
#             data = request.get_json()
#             result = MergeTrip().merge_trip_view_map(data)
#             return result
#         except ValueError as e:
#             raise ("Log Error", e)
        
# api.add_resource(TripMerge, "/get/data/view/merge/trip")


# # api show data map tsp:
# class TspRoute(Resource):
#     parser = reqparse.RequestParser()
#     parser.add_argument("data", type=dict, required=True, location="json")

#     # @api.expect(tsp_model)
#     def post(self):
#         data = request.get_json()
#         result = ProcessTSP().tsp_route(data)
#         return result
    
# api.add_resource(TspRoute, "/get/data/tsp")

# # api save action user: trip/identify
# class TripActionDetails(Resource):
#     def get(self):
#         json = request.get_json()
#         return user_action_trip(json)
    
# api.add_resource(TripActionDetails, "/trip/identify")

# class TripConfirm(Resource):
#     def post(self):
#         data = request.get_json()
#         result = TripClusterConfirm().process_trip_confirm(data)
#         return result
    
# api.add_resource(TripConfirm, "/get/data/trip/confirm")

# if __name__ == "__main__":
#     app.run(debug=True)