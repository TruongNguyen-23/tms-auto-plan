from flask import render_template_string, make_response, abort
from dotenv import load_dotenv
import json
import os

load_dotenv()
FOLDER_FILE_CACHE = os.getenv("FOLDER_FILE_CACHE")
FOLDER_FILE_TEMPLATE = os.getenv("FOLDER_FILE_TEMPLATE")
DATA_MENU_OPTION = os.getenv("DATA_MENU_OPTION")
DATA_FILL_TYPE = os.getenv("DATA_FILL_TYPE")


def save_file(data, name):
    file_name = f"{FOLDER_FILE_TEMPLATE}/{name}.html"
    try:
        with open(file_name, "r") as file:
            print(f"Cleared old content in {file_name}")
    except FileNotFoundError:
        print(f"File {file_name} does not exist")
    with open(file_name, "w") as file:
        file.write(data)
        print(f"Written content{file_name}")


def read_template_file(template_name):
    try:
        template_path = f"{FOLDER_FILE_TEMPLATE}/{template_name}"
        if os.path.isfile(template_path):
            with open(template_path, "r") as template_file:
                template_content = template_file.read()
            return template_content
        else:   
            return abort(400, "File Not Found")
    except ValueError as e:
        raise ("Log Error", e)
    

def auto_remove_file():
    files = os.listdir(FOLDER_FILE_TEMPLATE)
    for file in files:
        if file.startswith("timeline"):
            os.remove(f"{FOLDER_FILE_TEMPLATE}/{file}")
        else:
            return False
    return True


def render_content_file_HTML(file):
    rendered_template = render_template_string(read_template_file(file))
    response = make_response(rendered_template)
    response.headers["Content-Type"] = "text/html"
    return response


def save_content_cluster_cache(data, name):
    file_name = f"{FOLDER_FILE_CACHE}/{name}.html"
    print('file_name',file_name)
    try:
        with open(file_name, "r") as file:
            print(f"Cleared old content in {file_name}")
    except FileNotFoundError:
        print(f"File {file_name} does not exist")
    with open(file_name, "w") as file:
        file.write(data)
        print(f"Written content{file_name}")


def option_menu_data(name):
    arrData = []
    f = open(DATA_MENU_OPTION)
    data = json.load(f)
    name_upper = list(name)
    
    for index in [0, 3]:
        if 0 <= index < len(name):
            name_upper[index] = name_upper[index].upper()
    name_upper = "".join(name_upper)
    if name_upper == "CluSter":
        name_upper = "Cluster"
    for items in data[DATA_FILL_TYPE]:
        for item in items[name_upper]:
            arrData.append(item)
    f.close()
    return arrData
    # optimal time use list comprehension
    # name_upper = ''.join([s.upper() if i in [0, 3] else s for i, s in enumerate(name_upper)])
    # arrData=[item for items in data[DATA_FILL_TYPE] for item in items[name_upper]]
    
