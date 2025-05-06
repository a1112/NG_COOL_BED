from datetime import datetime

from CONFIG import DEBUG_MODEL
from Configs.CameraListConfig import camera_list_config
from Configs.ConfigBase import ConfigBase


class CameraConfig(ConfigBase):
    """
    相机参数
    """
    def __init__(self,cool_bed_key, camera_key):
        self.cool_bed_key = cool_bed_key
        self.camera_key = camera_key
        self.config = camera_list_config.get_item_config(cool_bed_key, camera_key)
        self.ip = self.config["ip"]
        self.enable = self.config["enable"] if not DEBUG_MODEL else True
        # self.conversion = ConversionImage(self.key)
        base_rtsp_url = "rtsp://admin:ng123456@{}/stream" #Streaming/Channels/1
        self.rtsp_url = base_rtsp_url.format(self.ip)
        self.start = datetime.now().strftime("DATETIME_FMT")

    # @property
    # def trans(self):
    #     return self.conversion.trans

    def set_start(self,datetime_str):
        self.config["start"] = datetime_str
        self.start = datetime_str
