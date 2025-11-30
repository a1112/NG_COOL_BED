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
        self.groups_dict = {config.group_key:config  for config in self.groups}


    @property
    def info(self):
        info ={}
        info.update(
            {
                "all": list(self.groups_dict.keys()),
                "run": list(self.groups_dict.keys()),
                "data":{
                    key : config.info
                    for key,config in self.groups_dict.items()
                }
            }
        )
        return info