import json
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
        if not is_run:
            logging.error(f"不执行 {key}")
        return is_run

    def get_debug_frame_url(self, key):
        file_name = key + ".jpg"
        return CalibratePath / file_name

    def get_camera_config(self, key):
        return self.config["camera"][key]


    def get_group_config(self, key):
        return self.group_dict[key]

    def save(self):
        CAMERA_MANAGE_CONFIG.write_text(
            json.dumps(self.config, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def set_group_shield(self, cool_bed_key: str, group_key: str, shield: bool):
        group_info = self.config.get("group", {}).get(cool_bed_key)
        if not group_info:
            raise KeyError(f"cool_bed_key not found: {cool_bed_key}")
        target_group = None
        for group in group_info.get("group", []):
            if group.get("key") == group_key:
                target_group = group
                break
        if target_group is None:
            raise KeyError(f"group_key not found: {group_key}")
        target_group["shield"] = bool(shield)
        if cool_bed_key in self.group_dict:
            self.group_dict[cool_bed_key].set_group_shield(group_key, bool(shield))
        self.save()

    @property
    def info(self):
        info = {}
        info.update(
            {
            "all":list(self.group_dict.keys()),
            "run":self.config["run"],
            "data" : {
            key:config.info
            for key,config in self.group_dict.items()
                    }
            }
        )
        return info

camera_manage_config = CameraManageConfig()  # 管理參數
