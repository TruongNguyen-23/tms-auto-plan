from dotenv import load_dotenv
import os

class ClusterDefault:
    def __init__(self):
        load_dotenv()
        self.api_Key = os.getenv("API_KEY")
        
    def show_map(self):
        html = f"""
        <!DOCTYPE html>
            <html>
            <head>
                <title>Map Cluster</title>
                <script src="https://maps.googleapis.com/maps/api/js?key={self.api_Key}&callback=initMap" async defer></script>
                <script>
                    function initMap() {{
                        var map = new google.maps.Map(document.getElementById('map'), {{
                            center: {{lat: 10.813975039910598, lng: 106.64436107457777}},
                            zoom: 8
                        }});
                        // map.show();
                    }}
                </script>
            </head>
                <body>
                    <div id="map" style="
                        height:100%;
                        width:100%;
                        position:absolute;
                        top:0;
                        left:0;
                        overflow:hidden;">
                    </div>
                </body>
            </html>
            """
        return html
