from Configs.GlobalConfig import GlobalConfig
from Loger import logger
from threading import Thread

from Configs import CameraConfigs
from CameraStreamer.RtspCapTure import RtspCapTure
from Configs.CameraManageConfig import camera_manage_config


class CoolBedThreadWorker(Thread):
    def __init__(self,key, config:CameraConfigs.CoolBedConfig, global_config:GlobalConfig):
        super().__init__()
        self.key = key
        self.global_config = global_config
        self.run_worker = camera_manage_config.run_worker_key(key)
        self.config = config
        self.camera_map = {}

    def run(self):
        for key, camera_config in self.config.camera_map.items():
            camera_config:CameraConfigs
            camera_config.set_start(self.global_config.start_datetime_str) # 设置统一时间
            cap_ture = RtspCapTure(camera_config, self.global_config) # 执行采集                    <<<--------------------------------------
            self.camera_map[key] = cap_ture

        # join
        for key, cap_ture in self.camera_map.items():
            cap_ture.join()


cool_bed_thread_worker_map = {}
def main():
    logger.info("start main")
    global_config = GlobalConfig()
    # 1 获取参数 数据
    for key, config in CameraConfigs.cool_bed_map.items():
        logger.debug(f"初始化 {key} ")
        cool_bed_thread_worker_map[key] = CoolBedThreadWorker(key, config, global_config)

    for key, cool_bed_thread_worker in cool_bed_thread_worker_map.items():
        if  cool_bed_thread_worker.run_worker:
            logger.debug(f"开始 执行 {key} ")
            cool_bed_thread_worker.start()

    logger.info("end main")


if __name__ == '__main__':
    main()
