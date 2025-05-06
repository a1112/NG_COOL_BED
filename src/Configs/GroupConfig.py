from .ConfigBase import ConfigBase
from Configs.CameraConfig import CameraConfig


class GroupConfig(ConfigBase):
    """
    组合识别
    """
    def __init__(self,key, config):
        super().__init__()
        self.key = key
        self.config = config
        print(config)


class CoolBedGroupConfig(ConfigBase):
    """
    冷床的组合识别配置
    """
    def __init__(self,key, config):
        super().__init__()
        self.config = config
        self.key = key
        self.camera_list = self.config["camera_list"]
        self.camera_map = {
            camera_key : CameraConfig(key,camera_key) for camera_key in self.camera_list
        }

        self.groups = [GroupConfig(key, g) for g in config["group"]]
