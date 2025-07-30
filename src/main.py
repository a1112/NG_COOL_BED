"""
入口

"""
import logging

# 禁用日志记录
logging.disable(logging.WARNING)

from multiprocessing import freeze_support

from Configs.CameraManageConfig import camera_manage_config
from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Globals import cool_bed_thread_worker_map, business_main
from Loger import logger
from Server import ApiServer


def main():
    logger.info("start main")
    while True:
        try:
            steel_infos = {}
            for key, config in camera_manage_config.group_dict.items():
                config: CoolBedGroupConfig  # 冷床 参数中心，用于管理冷床参数
                worker = cool_bed_thread_worker_map[key]
                steel_infos[key] = worker.get_steel_info()
            business_main.update(steel_infos)
        except Exception as e:
            logger.error(fr"主进程存在报错")
            logger.error(e)

if __name__ == "__main__":
    freeze_support()
    # 启动 HTTP 服务
    ApiServer.start()
    # 启动运行线程
    main()