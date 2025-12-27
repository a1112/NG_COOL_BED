import os

from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Configs.GlobalConfig import GlobalConfig
from Loger import logger
from ProjectManagement.Business import Business
from ProjectManagement.Main import CoolBedThreadWorker
from Configs.CameraManageConfig import camera_manage_config

business_main = Business()

global_config = GlobalConfig()
cool_bed_thread_worker_map = {}


def init_cool_bed_workers(enable_capture: bool = True):
    if not enable_capture:
        return cool_bed_thread_worker_map
    if cool_bed_thread_worker_map:
        return cool_bed_thread_worker_map
    # 1 获取参数 数据
    for key, config in camera_manage_config.group_dict.items():
        config: CoolBedGroupConfig  # 冷床 参数中心，用于管理冷床参数
        logger.debug(f"初始化 {key} ")
        cool_bed_thread_worker_map[key] = CoolBedThreadWorker(key, config, global_config)
    return cool_bed_thread_worker_map


_auto_start = os.getenv("NG_CAPTURE_AUTO_START", "1").strip().lower() not in {"0", "false", "no"}
init_cool_bed_workers(enable_capture=_auto_start)
