# 用于图像数据保存
from threading import Thread
from queue import Queue

from PIL import Image
import numpy as np

from CameraStreamer.ImageBuffer import ImageBuffer
from Configs.CameraConfigs import CameraConfig
from Configs.SaveConfig import save_config
from Loger import logger
import CONFIG


class ImageSaveBase(Thread):
    def __init__(self, camera_config:CameraConfig):
        super().__init__()
        self.camera_config = camera_config
        self.camera_buffer = Queue()
        self.save_path = self.camera_config.key
        self.start()

    def run(self):
        while CONFIG.APP_RUN:
            frame, save_url = self.camera_buffer.get()
            logger.debug(f"save {save_url}")
            if isinstance(frame, np.ndarray):
                image = Image.fromarray(frame)
            else:
                image = frame
            image.save(save_url)


class CameraImageSave(ImageSaveBase):
    """
    相机图像的保存
    """
    def __init__(self, camera_config:CameraConfig):
        super().__init__(camera_config)
        self.first_buffer_saved = False

    def save_first_buffer(self, buffer: ImageBuffer):
        """
        保存第一帧图像
        :param buffer:
        :return:
        """

        if not self.first_buffer_saved:
            logger.debug(fr"start time {self.camera_config.key} {self.camera_config.start}")

            self.first_buffer_saved = True
            frame = buffer.frame
            save_folder = save_config.camera_save_folder /self.camera_config.start
            save_folder.mkdir(parents=True, exist_ok=True)
            save_url = save_folder / fr"{self.camera_config.key}.jpg"
            self.camera_buffer.put([frame,save_url])

class ImageSave(ImageSaveBase):
    pass

