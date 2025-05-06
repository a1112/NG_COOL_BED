import CONFIG
import tool
from Configs import save_config
from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Loger import logger
from Save.SaveBase import ImageSaveBase


class CapJoinSave(ImageSaveBase):
    def __init__(self, camera_config: CoolBedGroupConfig):
        super().__init__()
        self.first_buffer_saved = False
        self.first_buffer_saved = False
        self.camera_config = camera_config
        self.start()

    def save_buffer(self,key, frame):
        """
        采集保存
        """
        save_folder = save_config.camera_save_folder / "join"/ key
        save_url = save_folder / tool.get_new_data_str() / fr"{key}_{tool.get_now_data_time_str()}.{CONFIG.IMAGE_SAVE_TYPE}"
        self.camera_buffer.put([frame, save_url])
