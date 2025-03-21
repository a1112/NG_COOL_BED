import time

import cv2
import numpy as np

import tool
from Configs.CameraConfigs import CameraConfig


class ImageBuffer:

    def __init__(self, camera_config: CameraConfig):
        self.camera_config = camera_config
        self.key = camera_config.key
        self.create_time = time.time()
        self.ret_ = 0
        self.frame_ = None
        self.image_ = None
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
        return self.image_

    @image.setter
    def image(self, value):
        self.set_image_time = time.time()
        self.image_ = value

    def show_frame(self, show_rect = True):
        if show_rect:
            trans = self.camera_config.trans
            pts = np.array(trans, np.int32)
            pts = pts.reshape((-1, 1, 2))  # 必须重塑为 (N,1,2) 格式[3,5](@ref)
            # 参数说明：图像、顶点、是否闭合、颜色（BGR）、线宽
            cv2.polylines(self.frame, [pts], isClosed=True, color=(0,255, 0), thickness = 3)
        return tool.show_cv2(self.frame, self.key)

    def show(self):
        return tool.show_cv2(self.image, self.key)