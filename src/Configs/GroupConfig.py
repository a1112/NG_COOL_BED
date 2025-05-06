from .ConfigBase import ConfigBase


class GroupConfig(ConfigBase):
    """
    组合识别
    """
    def __init__(self, config):
        super().__init__()
        self.config = config
        print(config)


class CoolBedGroupConfig(ConfigBase):
    """
    冷床的组合识别配置
    """
    def __init__(self,key, config):
        super().__init__()
        print(config)
        self.config = config
        self.key = key
        self.camera_list = self.config["camera_list"]
        self.camera_map = {}

        self.groups = [GroupConfig(g) for g in config["group"]]
