# 用于图像数据保存

from CameraStreamer.ImageBuffer import ImageBuffer
from Configs.CameraConfig import CameraConfig
from Configs.SaveConfig import save_config
from Loger import logger
import CONFIG
import tool
from Save.SaveBase import ImageSaveBase


class CameraImageSave(ImageSaveBase):
    """
    相机图像的保存
    """
    def __init__(self, camera_config:CameraConfig):
        super().__init__()
        self.first_buffer_saved = False
        self.camera_config = camera_config
        self.save_path = self.camera_config.camera_key
        self.start()


    def save_first_buffer(self, buffer: ImageBuffer):
        """
        保存第一帧图像
        :param buffer:
        :return:
        """

        if not getattr(save_config, "first_save_enabled", True):
            return

        if not self.first_buffer_saved:
            """
            开机保存
            """
            logger.debug(fr"start time {self.camera_config.camera_key} {self.camera_config.start}")
            self.first_buffer_saved = True
            frame = buffer.frame
            save_folder = save_config.first_save_camera_folder
            save_url = save_folder /fr"{self.camera_config.camera_key}.{CONFIG.IMAGE_SAVE_TYPE}"
            self.camera_buffer.put([frame, save_url])

    def save_buffer(self, buffer:ImageBuffer):
        """
        采集保存
        """
        frame = buffer.frame
        save_folder = save_config.camera_save_folder /self.camera_config.camera_key

        save_url = save_folder /"原图"/tool.get_new_data_str()/fr"{tool.get_now_data_time_str()}.{CONFIG.IMAGE_SAVE_TYPE}"
        self.camera_buffer.put([frame, save_url])

