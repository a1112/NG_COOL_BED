from pathlib import Path

import CONFIG
from tool import load_json
from CONFIG import SAVE_CONFIG, CAMERA_CONFIG_FOLDER, FIRST_SAVE_FOLDER, CAMERA_SAVE_FOLDER
from .ConfigBase import ConfigBase


class SaveConfig(ConfigBase):
    """
    参数保存类
    """
    def __init__(self):
        self.config = load_json(SAVE_CONFIG)
        self.camera_save_config = self.config["camera"]
        self.camera_saved = self.camera_save_config["enable"]
        self.camera_save_folder = CAMERA_SAVE_FOLDER / Path(self.camera_save_config["folder"])
        self.first_save_enabled = not getattr(CONFIG, "IS_LOC", True)
        self.first_save_map_folder = FIRST_SAVE_FOLDER / "mapping"
        if self.first_save_enabled:
            self.first_save_map_folder.mkdir(parents=True, exist_ok=True)
        self.camera_save_folder.mkdir(parents=True, exist_ok=True)
        self.first_save_camera_folder = FIRST_SAVE_FOLDER / "camera"
        if self.first_save_enabled:
            self.first_save_camera_folder.mkdir(parents=True, exist_ok=True)

        self.camera_save_name = self.camera_save_config["name"]

        self.data_save_config = self.config["data"]
        self.data_saved = self.data_save_config["enable"]
        self.data_save_folder = CAMERA_CONFIG_FOLDER / Path(self.data_save_config["folder"])
        self.data_save_folder.mkdir(parents=True, exist_ok=True)
        self.data_save_name = self.data_save_config["name"]

save_config = SaveConfig()
