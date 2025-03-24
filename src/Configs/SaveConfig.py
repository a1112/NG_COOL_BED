from pathlib import Path

from tool import load_json
from CONFIG import SAVE_CONFIG, CAMERA_CONFIG_FOLDER
from .ConfigBase import ConfigBase


class SaveConfig(ConfigBase):
    """
    参数保存类
    """
    def __init__(self):
        self.config = load_json(SAVE_CONFIG)
        self.camera_save_config = self.config["camera"]
        self.camera_saved = self.camera_save_config["enable"]
        self.camera_save_folder = CAMERA_CONFIG_FOLDER / Path(self.camera_save_config["folder"])
        self.camera_save_folder.mkdir(parents=True, exist_ok=True)
        self.camera_save_name = self.camera_save_config["name"]

save_config = SaveConfig()