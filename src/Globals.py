from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Configs.GlobalConfig import GlobalConfig
from Loger import logger
from ProjectManagement.Business import Business
from ProjectManagement.Main import CoolBedThreadWorker
from Configs.CameraManageConfig import camera_manage_config
business_main = Business()

global_config = GlobalConfig()
cool_bed_thread_worker_map = {}
# 1 获取参数 数据
for key, config in camera_manage_config.group_dict.items():
    config: CoolBedGroupConfig  # 冷床 参数中心，用于管理冷床参数
    logger.debug(f"初始化 {key} ")
    cool_bed_thread_worker_map[key] = CoolBedThreadWorker(key, config, global_config)