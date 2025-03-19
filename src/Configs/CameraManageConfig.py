import logging
from CONFIG import CAMERA_MANAGE_CONFIG, CAMERA_CONFIG_FOLDER

from tool import load_json

class CameraManageConfig:
    """
    管理
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


camera_manage_config = CameraManageConfig()