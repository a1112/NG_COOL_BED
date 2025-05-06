import logging

from CONFIG import CAMERA_MANAGE_CONFIG, CAMERA_CONFIG_FOLDER, IP_LIST_CAMERA_CONFIG, CalibratePath
from .ConfigBase import ConfigBase
from .GlobalConfig import GlobalConfig
from tool import load_json
from .CoolBedGroupConfig import CoolBedGroupConfig



class CameraManageConfig(ConfigBase):
    """
    管理
    CameraManage.json
    """
    def __init__(self):
        self.config = load_json(CAMERA_MANAGE_CONFIG)

        self.camera_map = {}
        self.group_dict = {key:CoolBedGroupConfig(key, config) for key,config in  self.config["group"].items()}


    def run_worker_key(self, key):
        is_run = key in self.config["run"]
        print(key)
        print(self.config)
        if not is_run:
            logging.error(f"不执行 {key}")
        return is_run

    def get_debug_frame_url(self, key):
        file_name = key.replace("_", "-") + ".jpg"
        return CalibratePath / file_name

    def get_camera_config(self, key):
        return self.config["camera"][key]


    def get_group_config(self, key):
        return self.group_dict[key]


camera_manage_config = CameraManageConfig()  # 管理參數