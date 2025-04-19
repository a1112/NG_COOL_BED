from datetime import datetime

from CONFIG import CONFIG_FOLDER, IP_LIST_CAMERA_CONFIG, DATETIME_FMT, DEBUG_MODEL
from CameraStreamer.ConversionImage import ConversionImage
from .ConfigBase import ConfigBase
from tool import load_json
from Loger import logger

from Configs.CameraManageConfig import camera_manage_config

# 获取所有的Ip
camera_configs = load_json(IP_LIST_CAMERA_CONFIG)


class CameraConfig(ConfigBase):
    """
    相机参数
    """
    def __init__(self, key, config):
        self.key = key
        self.config = config
        self.ip = config["ip"]
        self.enable = config["enable"] if not DEBUG_MODEL else True
        self.conversion = ConversionImage(self.key)
        base_rtsp_url = "rtsp://admin:ng123456@{}/stream" #Streaming/Channels/1
        self.rtsp_url = base_rtsp_url.format(self.ip)
        self.start = config["start"] if "start" in config else datetime.now().strftime("DATETIME_FMT")

    @property
    def trans(self):
        return self.conversion.trans

    def set_start(self,datetime_str):
        self.config["start"] = datetime_str
        self.start = datetime_str

class CoolBedConfig(ConfigBase):
    """
    冷床参数
    """
    def __init__(self,key,config):
        self.key = key
        self.config = config
        self.ip_map = config["ipList"]
        self.camera_map = {}
        for key,value in self.ip_map.items():
            print(fr" value: {value}")
            self.camera_map[key] = CameraConfig(key, value)


cool_bed_map = {
    key:CoolBedConfig(key,camera_configs[key])
    for key in camera_configs.keys() if camera_manage_config.run_worker_key(key)
}


def get_cool_bed_config(key)->CoolBedConfig:
    return cool_bed_map[key]


def get_camera_config(key)->CameraConfig:
    for cool_bed_config in cool_bed_map.values():
        if key in cool_bed_config.camera_map:
            return cool_bed_config.camera_map[key]
    raise Exception(f"没有找到相机配置 {key}")


logger.info(cool_bed_map)
