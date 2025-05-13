from Configs.CameraConfig import CameraConfig
from Configs.ConfigBase import ConfigBase
from Configs.GroupConfig import GroupConfig
from Configs.MappingConfig import MappingConfig


class CoolBedGroupConfig(ConfigBase):
    """
    冷床的组合识别配置
    """
    def __init__(self,key, config):
        super().__init__()
        self.config = config
        self.key = key
        print(self.config)
        self.camera_list = self.config["camera_list"]
        self.camera_map = {
            camera_key : CameraConfig(key,camera_key) for camera_key in self.camera_list
        }
        self.groups = [GroupConfig(key, g) for g in config["group"]]
