
import time
# from queue import Queue

import cv2
from threading import Thread

from joblib.externals.loky.backend.queues import Queue
from typing_extensions import override
from multiprocessing import Process, Queue
from CameraStreamer.ConversionImage import ConversionImage
from Configs.CameraConfigs import CameraConfig
from Loger import logger
from .ImageBuffer import ImageBuffer
from .CameraSdk import DebugCameraSdk, OpenCvCameraSdk, AvCameraSdk
from CONFIG import DEBUG_MODEL

class RtspCapTure(Thread): # Process
    def __init__(self, camera_config:CameraConfig):
        self.camera_config = camera_config
        self.key = camera_config.key
        self.rtsp_url = camera_config.rtsp_url
        self.trans=camera_config.trans
        super().__init__()
        self.cap = None
        self.camera_buffer = Queue()
        self.conversion = self.camera_config.conversion
        self.conversion: ConversionImage    # 图像转换
        self.start()


    def get_video_capture(self):
        if DEBUG_MODEL:
            return DebugCameraSdk(self.key)
        return AvCameraSdk(self.key, self.rtsp_url)
        # return OpenCvCameraSdk(self.key, self.rtsp_url)


    def run(self):
        logger.debug(f"start RtspCapTure {self.key}")

        self.cap = self.get_video_capture()
        print(self.cap)
        # ret, frame = cap.read()
        index = 0
        num = 0
        while True:
            buffer = ImageBuffer(self.key,self.trans)
            ret, frame = self.cap.read()
            buffer.ret = ret
            buffer.frame = frame
            index += 1
            if frame is None:
                print("相机为空")
                self.cap.release()
                time.sleep(2)
                self.cap = self.get_video_capture()
                continue

            image = frame
            # image = self.conversion.image_conversion(frame)
            buffer.image = image
            self.camera_buffer.put(buffer)
            print(image.shape)
            buffer.show_frame()
            time.sleep(0.2)
            self.camera_buffer.get() if self.camera_buffer.qsize() > 1 else time.sleep(0.01)
            num += 1