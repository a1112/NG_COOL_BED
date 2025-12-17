import CONFIG
import tool
from Configs import save_config
from Configs.CalibrateConfig import CalibrateConfig
from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Loger import logger
from Save.SaveBase import ImageSaveBase


class CapJoinSave(ImageSaveBase):
    def __init__(self, camera_config: CoolBedGroupConfig):
        super().__init__()
        self.first_buffer_saved = False
        self.first_buffer_saved = False
        self.camera_config = camera_config
        self.save_first_dict={}
        self.start()

    def save_first_image(self,key, frame):
        if not getattr(save_config, "first_save_enabled", True):
            return
        save_folder = save_config.first_save_map_folder
        save_url = save_folder/fr"{key}.{CONFIG.IMAGE_SAVE_TYPE}"
        self.camera_buffer.put([frame, save_url])

    def save_buffer(self,key, calibrate:CalibrateConfig):
        """
        采集保存
        """
        frame = calibrate.image
        if key not in self.save_first_dict:
            self.save_first_image(key,frame)
            self.save_first_dict[key] = 1
        self.save_first_dict[key]+=1
        if not self.save_first_dict[key] % 50:
            save_folder = save_config.camera_save_folder / "join"/ key
            save_url = save_folder / tool.get_new_data_str() / fr"{key}_{tool.get_now_data_time_str()}.{CONFIG.IMAGE_SAVE_TYPE}"
            self.camera_buffer.put([frame, save_url])
