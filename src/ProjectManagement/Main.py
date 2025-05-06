from Configs.GlobalConfig import GlobalConfig
from Configs.GroupConfig import CoolBedGroupConfig
from Loger import logger
from threading import Thread

from Configs import CameraConfigs
from CameraStreamer.RtspCapTure import RtspCapTure
from Configs.CameraManageConfig import camera_manage_config


class CoolBedThreadWorker(Thread):
    """
    单个冷床 的 循环

    """
    def __init__(self,key, config:CoolBedGroupConfig, global_config:GlobalConfig):
        super().__init__()
        self.key = key
        self.global_config = global_config
        self.run_worker = camera_manage_config.run_worker_key(key)
        self.config = config  #  对于组别的参数试图
        self.camera_map = {}
        if  self.run_worker:
            logger.debug(f"开始 执行 {key} ")
            self.start()

    def run(self):

        group_config:CoolBedGroupConfig

        for key, camera_config in self.config.camera_map.items():
            camera_config:CameraConfigs
            camera_config.set_start(self.global_config.start_datetime_str) # 设置统一时间
            cap_ture = RtspCapTure(camera_config, self.global_config) # 执行采集   <<<---------------------------------
            self.camera_map[key] = cap_ture

        # join
        for key, cap_ture in self.camera_map.items():
            cap_ture.join()


cool_bed_thread_worker_map = {}
def main():
    logger.info("start main")
    global_config = GlobalConfig()
    # 1 获取参数 数据
    for key, config in camera_manage_config.group_dict:
        config:CoolBedGroupConfig    # 冷床 参数中心，用于管理冷床参数
        logger.debug(f"初始化 {key} ")
        cool_bed_thread_worker_map[key] = CoolBedThreadWorker(key,config, global_config)

    for key, cool_bed_thread_worker in cool_bed_thread_worker_map.items():  # 等待
            cool_bed_thread_worker.join()

    logger.info("end main")


if __name__ == '__main__':
    main()
