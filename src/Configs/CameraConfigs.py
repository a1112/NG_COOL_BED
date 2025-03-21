from CONFIG import CONFIG_FOLDER, IP_LIST_CAMERA_CONFIG
from CameraStreamer.ConversionImage import ConversionImage
from tool import load_json
from Loger import logger

from Configs.CameraManageConfig import camera_manage_config

# 获取所有的Ip
camera_configs = load_json(IP_LIST_CAMERA_CONFIG)


class CameraConfig:
    """
    相机参数
    """
    def __init__(self, key, config):
        self.key = key
        self.config = config
        self.ip = config["ip"]
        self.enable = config["enable"]
        self.conversion = ConversionImage(self.key)
        base_rtsp_url = "rtsp://admin:ng123456@{}/stream" #Streaming/Channels/1
        self.rtsp_url = base_rtsp_url.format(self.ip)
        logger.debug(f"rtsp: {self.rtsp_url}")

    @property
    def trans(self):
        return self.conversion.trans


class CoolBedConfig:
    """
    冷床参数
    """
    def __init__(self,key,config):
        self.key = key
        self.config = config
        self.ip_map = config["ipList"]
        self.camera_map = {}
        for key,value in self.ip_map.items():
            self.camera_map[key] = CameraConfig(key, value)


cool_bed_map = {
    key:CoolBedConfig(key,camera_configs[key])
    for key in camera_configs.keys() if camera_manage_config.run_worker_key(key)
}

logger.info(cool_bed_map)
