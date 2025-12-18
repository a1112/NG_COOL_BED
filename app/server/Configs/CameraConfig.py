from datetime import datetime

from CONFIG import DEBUG_MODEL, DATETIME_FMT
from Configs.CameraListConfig import camera_list_config
from Configs.ConfigBase import ConfigBase


class CameraConfig(ConfigBase):
    """
    相机参数
    """
    def __init__(self,cool_bed_key, camera_key):
        self.cool_bed_key = cool_bed_key
        self.camera_key = camera_key
        self.config = camera_list_config.get_item_config(cool_bed_key, camera_key)
        self.ip = self.config["ip"]
        self.enable = self.config["enable"] if not DEBUG_MODEL else True
        # self.conversion = ConversionImage(self.key)
        self.rtsp_url = self._build_rtsp_url()
        self.start = datetime.now().strftime(DATETIME_FMT)

    def _build_rtsp_url(self) -> str:
        from urllib.parse import quote

        explicit = self.config.get("rtsp_url", "")
        if isinstance(explicit, str) and explicit.strip():
            return explicit.strip()

        user = self.config.get("rtsp_user", "admin")
        password = self.config.get("rtsp_pass", "ng123456")
        path = self.config.get("rtsp_path", "/stream")
        if not isinstance(path, str) or not path:
            path = "/stream"
        if not path.startswith("/"):
            path = "/" + path

        user = quote(str(user or ""), safe="")
        password = quote(str(password or ""), safe="")
        if user and password:
            return f"rtsp://{user}:{password}@{self.ip}{path}"
        return f"rtsp://{self.ip}{path}"

    # @property
    # def trans(self):
    #     return self.conversion.trans

    def set_start(self,datetime_str):
        self.config["start"] = datetime_str
        self.start = datetime_str
