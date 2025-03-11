
# css Map Clutter
def css_map_cluster():
    styles = """
            <style>
                .main-menu{
                    display: flex;
                    
                }
                .container-main {
                    display: flex;
                    top:0px;
                }
                .container{
                    height: 830px;
                    width: 400px;
                    background-color:#d7e3d4;
                    overflow: auto;
                }
                .route-main {
                    position: absolute;
                    right:0px;
                    bottom:0px;
                    z-index: 1000;
                }
                .route{
                    height: 200px;
                    width: 350px;
                    background-color:#d7e3d4;
                    border-radius:25px;
                    margin:10px;
                    padding:10px;
                }
                .tripline {
                    position: relative;
                    margin: 10px auto;
                    width: 80%;
                }
                .title{
                    font-size:15px;
                    color:#3498db;
                    font-weight:bold
                }
                .event {
                    position: relative;
                    padding: 10px;
                    border-left: 1px solid #3498db;
                    margin: 10px 0;
                }

                .event-date {
                    font-weight: bold;
                    color: #3498db;
                    margin-bottom: 5px;
                }

                .event-description {
                    color: #666;
                }

                .event:before {
                    content: "";
                    position: absolute;
                    top: 0;
                    left: -10px;
                    width: 20px;
                    height: 20px;
                    background-color: #3498db;
                    border-radius: 50%;
                }

                .sub-events {
                    margin-left: 10px;
                    padding-left: 10px;
                    border-left: 1px solid #ccc;
                }

                .sub-event {
                    padding: 10px 0;
                }

                .sub-event-date {
                    font-weight: bold;
                    color: #3498db;
                    font-size:15px
                }

                .sub-event-description {
                    color: #e33232;
                    font-size:15px
                }
                
                .title-text{
                    font-size:20px;
                    color:red;
                    margin:10px;
                    padding:10px;
                    font-weight:bold;
                }
                table, td, th {  
                    border: 1px solid #ddd;
                    text-align: left;
                    }

                table {
                    border-collapse: collapse;
                    width: 100%;
                    }

                th, td {
                    padding: 15px;
                    font-size:15px;
                    font-weight:bold;
                    }
            </style>
            """
    return styles
