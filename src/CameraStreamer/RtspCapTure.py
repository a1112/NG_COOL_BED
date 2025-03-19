import time
from queue import Queue

import cv2
from threading import Thread

from Configs.CameraConfigs import CameraConfig


class RtspCapTure(Thread):
    def __init__(self, camera_config:CameraConfig):
        self.camera_config = camera_config
        super().__init__()
        self.cap = None
        self.camera_buffer = Queue()
        self.start()


    def get_video_capture(self):
        return cv2.VideoCapture(self.camera_config.rtsp_url)

    def run(self):
        cap = self.get_video_capture()
        print(cap)
        ret, frame = cap.read()
        index = 1
        num = 1
        while True:
            ret, frame = cap.read()
            index += 1
            if frame is None:
                print("相机为空")
                cap.release()
                time.sleep(2)
                cap = self.get_video_capture()
                continue
            img = img_change(frame, trans)
            self.camera_buffer.put(img)

            self.camera_buffer.get() if self.camera_buffer.qsize() > 1 else time.sleep(0.01)
            num += 1