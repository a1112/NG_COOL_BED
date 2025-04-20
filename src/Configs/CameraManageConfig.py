import logging

from CONFIG import CAMERA_MANAGE_CONFIG, CAMERA_CONFIG_FOLDER
from .ConfigBase import ConfigBase
from tool import load_json

class MapConfig(ConfigBase):
    """
    管理 相机与实际对应的
    Map.json
    """
    def __init__(self, config):
        self.config = config
        if isinstance(config, str):
            self.config = load_json(config)
        self.size = self.config["size"] if "size" in self.config else [512, 512]




class CameraManageConfig(ConfigBase):
    """
    管理
    CameraManage.json
    """
    def __init__(self):
        self.config = load_json(CAMERA_MANAGE_CONFIG)
        calibrate_base_path = self.config["calibrate"]["path"]
        self.calibrate_path = CAMERA_CONFIG_FOLDER/calibrate_base_path
        self.camera_map = {}

    def get_calibrate_json_path(self, key):
        file_name = key.replace("_", "-") + ".json"
        return self.calibrate_path / file_name

    def run_worker_key(self, key):
        is_run = key in self.config["run"]
        if not is_run:
            logging.error(f"不执行 {key}")
        return is_run

    def get_debug_frame_url(self, key):
        file_name = key.replace("_", "-") + ".jpg"
        return self.calibrate_path / file_name

    def get_camera_config(self, key):
        return self.config["camera"][key]

    def get_map(self, key):
        print(self.config["map"])
        map_ = MapConfig(self.config["map"][key.replace("_", "-")])
        return map_

camera_manage_config = CameraManageConfig()