
from .ConfigBase import ConfigBase
import tool
import CONFIG


class MappingConfig(ConfigBase):
    """
    指标转换参数
    """
    def __init__(self,key):
        tool.load_json(CONFIG.CONFIG_FOLDER)