import CONFIG
import json

def load_json(url):
    with open(url, "r", encoding = CONFIG.encoding ) as f:
        return json.load(f)