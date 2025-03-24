from datetime import datetime
import time

from CONFIG import DATETIME_FMT
from .ConfigBase import ConfigBase


class GlobalConfig(ConfigBase):
    def __init__(self):
        self.start_datetime = datetime.now()
        self.start_datetime_str = self.start_datetime.strftime(DATETIME_FMT)
        self.start_time = time.time()