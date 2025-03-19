import logging
from Configs.CameraManageConfig import camera_manage_config

from tool import load_json

class ConversionImage:
    """
    This class is responsible for converting the image to the desired format.
    """
    def __init__(self, key):
        self.key = key
        calibrate_json_path = camera_manage_config.get_calibrate_json_path(self.key)
        if not calibrate_json_path.exists():
            logging.error(f"{calibrate_json_path} 不存在 ! ")
            json_data = {}
        else:
            json_data = load_json(calibrate_json_path)
