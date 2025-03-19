
import time
from queue import Queue

import cv2
from threading import Thread

from CameraStreamer.ConversionImage import ConversionImage
from Configs.CameraConfigs import CameraConfig
from Loger import logger
from ImageBuffer import ImageBuffer


class RtspCapTure(Thread):
    def __init__(self, camera_config:CameraConfig):
        self.camera_config = camera_config
        super().__init__()
        self.cap = None
        self.camera_buffer = Queue()
        self.conversion = self.camera_config.conversion
        self.conversion: ConversionImage    # 图像转换
        self.start()


    def get_video_capture(self):
        return cv2.VideoCapture(self.camera_config.rtsp_url)

    def run(self):
        logger.debug(f"start RtspCapTure {self.camera_config.key}")

        self.cap = self.get_video_capture()
        # ret, frame = cap.read()
        index = 0
        num = 0
        while True:
            buffer = ImageBuffer()
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
            image = self.conversion.image_conversion(frame)
            buffer.image = image
            self.camera_buffer.put(buffer)

            self.camera_buffer.get() if self.camera_buffer.qsize() > 1 else time.sleep(0.01)
            num += 1