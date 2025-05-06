from CONFIG import IP_LIST_CAMERA_CONFIG
from Configs.ConfigBase import ConfigBase
from tool import load_json


class CameraListConfig(ConfigBase):
    def __init__(self):
        self.config = load_json(IP_LIST_CAMERA_CONFIG)

    def get_item_config(self, cool_bed_key, camera_key):
        return self.config[cool_bed_key]["ipList"][camera_key]

camera_list_config = CameraListConfig()
