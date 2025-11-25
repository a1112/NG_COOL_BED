import time

import cv2
import numpy as np

import CONFIG
import tool
from Configs.CameraConfig import CameraConfig
from CameraStreamer.ConversionImage import ConversionImage


class ImageBuffer:

    def __init__(self, camera_config: CameraConfig):
        self.camera_config = camera_config
        self.key = camera_config.camera_key
        # self.conversion:ConversionImage = camera_config.conversion
        self.create_time = time.time()
        self.ret_ = 0
        self.frame_ = None
        self.image_ = None
        # self.trans = camera_config.trans
        # 设置时间
        self.set_image_time = time.time()
        # 采集时间
        self.set_frame_time = time.time()

    @property
    def ret(self):
        return self.ret_

    @ret.setter
    def ret(self, value):
        self.ret_ = value

    @property
    def frame(self):
        return self.frame_

    @frame.setter
    def frame(self, value):
        self.set_frame_time = time.time()
        self.frame_ = value

    @property
    def frame_time(self):
        return self.set_frame_time

    @property
    def time_difference(self):
        return self.set_frame_time - self.create_time

    @property
    def image(self):
        if self.image_ is None:
            pass
            return self.frame_
            # self.image_ = self.conversion(self.frame)

        return self.image_

    @image.setter
    def image(self, value):
        self.set_image_time = time.time()
        self.image_ = value

    def show_frame(self, show_rect=True):
        # trans = self.camera_config.trans
        if CONFIG.show_camera:
            # if show_rect:
            #     pts = np.array(trans, np.int32)
            #     pts = pts.reshape((-1, 1, 2))  # 必须重塑为 (N,1,2) 格式[3,5](@ref)
            #     # 参数说明：图像、顶点、是否闭合、颜色（BGR）、线宽
            #     cv2.polylines(self.frame, [pts], isClosed=True, color=(0,255, 0), thickness = 3)
            return tool.show_cv2(self.frame, self.key)

    def show(self):
        if self.image is not None and CONFIG.show_camera:
            return tool.show_cv2(self.image, self.key)
