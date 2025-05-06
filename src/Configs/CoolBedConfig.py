from Configs.CameraConfig import CameraConfig
from Configs.CameraManageConfig import camera_manage_config
from Configs.ConfigBase import ConfigBase
from Configs.GroupConfig import CoolBedGroupConfig


class CoolBedConfig(ConfigBase):
    """
    冷床参数
    """
    def __init__(self,key,config):
        self.key = key
        self.config = config
        self.ip_map = config["ipList"]
        self.camera_map = {}
        self.group_config = camera_manage_config.get_group_config(key)
        self.group_config:CoolBedGroupConfig
        for key in self.group_config.camera_list:
            self.camera_map[key] = CameraConfig(key, config["ipList"][key])

        # for key,value in self.ip_map.items():
        #     print(fr" value: {value}")
        #     self.camera_map[key] = CameraConfig(key, value)
