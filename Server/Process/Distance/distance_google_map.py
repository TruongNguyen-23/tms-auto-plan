from datetime import datetime
from dotenv import load_dotenv
import googlemaps
import requests
import os

TIME_HOUR = 3600
KILOMETER = 1000
TIME_MINUTE = 60


class DataGoogleMapAPI:
    def __init__(self):
        load_dotenv()
        self.api_Key = os.getenv("API_KEY")
        self.mode_direction = os.getenv("MODE_DIRECTION")
        self.url_distance = os.getenv("URL_GOOGLE_CALCULATE_DISTANCE")
        self.gmaps = googlemaps.Client(key=self.api_Key)

    def url_google_map(self, start_point, end_point, key, mode):
        return f"https://maps.googleapis.com/maps/api/{mode}/json?origin={start_point}&destination={end_point}&mode=driving&key={key}"

    def data_real_time(self, way_point):
        total_distance = 0
        total_time = 0
        directions_result = self.gmaps.directions(
            origin = way_point[0],
            destination = way_point[-1],
            waypoints = way_point[1:-1],
            mode = "driving",
            departure_time = datetime.now(),
        )
        for leg in directions_result[0]["legs"]:
            total_distance += leg["distance"]["value"]
            total_time += leg["duration"]["value"]
        total_distance_text = f"{total_distance / KILOMETER:.2f} km"
        total_time_text = f"{total_time // TIME_HOUR} giờ {total_time % TIME_HOUR // TIME_MINUTE} phút"
        return total_distance_text, total_time_text
    def get_directions_way_point(self, point):
        total_distance = 0
        total_duration = 0
        for i in range(len(point) - 1):
            start_point = f"{point[i]['lat']},{point[i]['lng']}"
            end_point = f"{point[i + 1]['lat']},{point[i + 1]['lng']}"
            url = self.url_google_map(
                start_point, end_point, self.api_Key, self.mode_direction
            )
            response = requests.get(url)
            data = response.json()
            if data["status"] == "OK":
                route = data["routes"][0]
                distance = route["legs"][0]["distance"]["value"]
                duration = route["legs"][0]["duration"]["value"]
                total_distance += distance
                total_duration += duration
        cost = total_distance / KILOMETER
        time = total_duration / TIME_HOUR
        return cost, time

    def get_distance(self, origin, destination):
        params = {
            "origins": {origin},
            "destinations":{destination},
            "mode": "driving",
            "key": {self.api_Key}
        }
        response = requests.get(self.url_distance, params=params)
        data = response.json()
        if data["status"] == "OK":
            time = data["rows"][0]["elements"][0]["duration"]["value"]
            return int(time / TIME_MINUTE)
        return None
