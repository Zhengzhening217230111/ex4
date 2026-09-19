## Import the necessary modules
## Logic for loading and reading from a JSON file. 
## The function must return only the items
import json
import os
# from pathlib import Path
def load_items(filename):
    with open(filename, "r") as f:
        data = json.load(f)
        return data["items"]

## Logic for getting only those items that are not yet claimed 
## It should return only the items that are unclaimed
def get_unclaimed_items(items):
    return [item for item in items if item["status"] == "unclaimed"]

## Logic to save the result to a JSON file.
## The function should create the directory if it does not exist and save the result in a JSON format.
def save_result(result, filename):
    dir_name = os.path.dirname(filename)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        # path = Path("output") / "filename"
        # path.parent.mkdir(parents=True, exist_ok=True)
