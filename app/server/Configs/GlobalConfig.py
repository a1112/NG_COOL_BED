from datetime import datetime
import time

import CONFIG
from CONFIG import DATETIME_FMT
from .ConfigBase import ConfigBase


class GlobalConfig(ConfigBase):
    def __init__(self):
        self.debug = CONFIG.DEBUG_MODEL
        self.start_datetime = datetime.now()
        self.start_datetime_str = self.start_datetime.strftime(DATETIME_FMT)
        self.start_time = time.time()