import json
from pathlib import Path,WindowsPath

root_folder=Path("calibrate")
json_list = list(root_folder.glob("*.json"))

for js_url in json_list:
    js_url:WindowsPath
    js_data = None
    with js_url.open("r") as f:
        js_data = json.load(f)
    js_data["imageData"]=None
    with js_url.open("w") as f:
        json.dump(js_data, f)