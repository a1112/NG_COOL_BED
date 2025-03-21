#  回去圖像的 SDK
from abc import ABC, abstractmethod

from PIL import Image
import cv2
import numpy as np
import tool

from Configs.CameraManageConfig import camera_manage_config


class CameraSdkBase(ABC):
    """

    """
    def __init__(self):
        pass

    @abstractmethod
    def read(self):
        ...

    @abstractmethod
    def release(self):
        ...

    @abstractmethod
    def  show(self):
        ...

class OpenCvCameraSdk(CameraSdkBase):

    def __init__(self, key, rtsp_url):
        super().__init__()
        self.key = key
        self.rtsp_url = rtsp_url
        self.camera = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 10000)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        self.camera.set(cv2.CAP_PROP_FPS, 8)
    def read(self):
        det, img = self.camera.read()
        return det, img

    def release(self):
        return self.camera.release()

    def show(self):
        pass


class DebugCameraSdk(CameraSdkBase):

    def __init__(self, key):
        super().__init__()
        self.key = key
        self.camera = None
        self.det = 0
        self.frame_url = camera_manage_config.get_debug_frame_url(self.key)
        self.frame = Image.open(str(self.frame_url))
        self.frame = np.array(self.frame)

    def read(self):
        self.det+=1
        return self.det,self.frame

    def release(self):
        pass

    def show(self):
        return tool.show_cv2(self.frame, self.key)