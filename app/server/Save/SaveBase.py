from pathlib import Path
from queue import Queue
from threading import Thread

import cv2
import numpy as np
from PIL import Image

import CONFIG
from Configs.CameraConfig import CameraConfig
from Loger import logger


class ImageSaveBase(Thread):
    def __init__(self):
        super().__init__()
        self.camera_buffer = Queue()


    def run(self):
        while CONFIG.APP_RUN:
            frame, save_url = self.camera_buffer.get()
            try:
                if frame is None or not save_url:
                    continue
                logger.debug(f"save {save_url}")
                if isinstance(frame, np.ndarray):
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    image = Image.fromarray(frame)
                else:
                    image = frame
                Path(save_url).parent.mkdir(parents=True, exist_ok=True)
                image.save(save_url)
            except Exception:
                logger.exception("image save failed: %s", save_url)
                continue
