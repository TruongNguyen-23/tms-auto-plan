from timeit import default_timer as timer
from dotenv import load_dotenv
from random import randbytes
from datetime import date
import shutil
import json
import os

load_dotenv()
DATA_COLOR = os.getenv("DATA_COLOR_DRAW")
MODE = "colors"

def get_content_for_user_id(name, user_id):
    return f"{name}{user_id}"

def get_color_template():
    color = []
    f = open(DATA_COLOR)
    data = json.load(f)
    for items in data[MODE]:
        color.append(items["code"]["hex"])
    return color

def random_color_for_trip(number):
    while len(get_color_template()) < number:
        color_random = f"#{randbytes(3).hex()}"
        template_color = {
            "color": "",
            "category": "",
            "type": "primary",
            "code": {
                "rgba": [255, 0, 0, 1],
                "hex": color_random
                }
            }
        with open(DATA_COLOR, 'r') as file:
            data = json.load(file)
        if template_color not in data["colors"]:
            data['colors'].append(template_color)
        with open(DATA_COLOR, 'w') as file:
            json.dump(data, file)
            
def timer_func(func):
    def wrapper(*args, **kwargs):
        t1 = timer()
        result = func(*args, **kwargs)
        t2 = timer()
        execution_time = t2 - t1
        print(f'{func.__name__}() executed in {execution_time:.6f}s')
        return result, execution_time 
    return wrapper



def clear_cache_compile():
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                shutil.rmtree(os.path.join(root, dir_name))
                print(f"Directory: {os.path.join(root, dir_name)}")

def get_date_time_user_action():
    return date.today().strftime("%d%M%Y")

