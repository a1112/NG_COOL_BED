import numpy as np

from CameraStreamer.ConversionImage import ConversionImage
from .CalibrateConfig import CalibrateConfig
from .ConfigBase import ConfigBase
from .MappingConfig import MappingConfig


def join_conversion_image_list(image_list):
    return np.hstack(image_list)



class GroupConfig(ConfigBase):
    """
    组合识别
    单组识别，记录组内的相机拼接顺序
    """
    def __init__(self,key, config):
        super().__init__()
        self.key = key
        self.camera_list = config["camera_list"]
        self.config = config
        self.msg = config["msg"]
        self.group_key = config["key"]
        size_list = config["size_list"]
        self.map_config = MappingConfig(self.key,self.config["key"])

        self.conversion_list = [ConversionImage(key,size[0],size[1]) for key, size in zip(self.camera_list,size_list)]  # 拿到 对应的 透视 参数


        # 拿到 对应的 透视 参数

    def calibrate_image(self, cap_dict):
        image_list = [cap_dict[key] for key in self.camera_list]  # 拿到 对应的 透视 参数
        conversion_image_list = [conv.image_conversion(image.frame) for image,conv in zip(image_list,self.conversion_list)]
        # 透视拼接
        return CalibrateConfig(conversion_image_list) # join_conversion_image_list(conversion_image_list)

    @property
    def info(self):
        info = self.config
        return info