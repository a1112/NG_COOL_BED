import time

from Base import RollingQueue
from Base.Error import CoolBedError
from Configs.GlobalConfig import GlobalConfig
from Configs.GroupConfig import GroupConfig
from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Loger import logger
from threading import Thread

from Configs.CameraConfig import CameraConfig
from CameraStreamer.RtspCapTure import RtspCapTure
from Configs.CameraManageConfig import camera_manage_config
from Save.CapJoinSave import CapJoinSave
from alg.YoloModel import YoloModel
from tool import show_cv2


class CoolBedThreadWorker(Thread):
    """
    单个冷床 的 循环

    """
    def __init__(self,key, config:CoolBedGroupConfig, global_config:GlobalConfig):
        super().__init__()
        self.save_thread:CapJoinSave|None = None
        self.key = key
        self.global_config = global_config
        self.run_worker = camera_manage_config.run_worker_key(key)
        self.config = config  #  对于组别的参数试图
        self.camera_map = {}
        self.steel_data_queue = RollingQueue(maxsize=1)
        self.FPS = 5
        if  self.run_worker:
            logger.debug(f"开始 执行 {key} ")
            self.start()

    def run(self):
        print(f"start  CoolBedThreadWorker {self.key}")
        model = YoloModel()
        self.save_thread = CapJoinSave(self.config)
        #  工作1， 相机初始化
        for key, camera_config in self.config.camera_map.items():
            camera_config:CameraConfig
            camera_config.set_start(self.global_config.start_datetime_str)  # 设置统一时间
            self.camera_map[key] = RtspCapTure(camera_config, self.global_config)  # 执行采集   <<<-------------------
        cap_index=0
        while True:
            cap_index += 1
            start_time = time.time()
            # 工作2 采集 1 CAPTURE
            cap_dict = {key: cap_ture.get_cap() for key, cap_ture in self.camera_map.items()}
            steel_info = None
            # 工作3 处理 透视 表
            for group_config in self.config.groups:  # 注意排序规则
                group_config: GroupConfig
                join_image = group_config.calibrate_image(cap_dict)
                show_cv2(join_image,title="join_image  "+group_config.msg)
                # 调整中的工作-----------------------------------
                # 工作4 识别
                if not cap_index%(self.FPS*10):
                    self.save_thread.save_buffer(group_config.group_key, join_image)
                steel_info = model.predict(join_image)
                if steel_info.can_get_data: # 如果有符合（无冷床遮挡）则返回数据
                    continue
            # 工作5 识别结果 的逻辑处理
            if steel_info is not None:
                self.steel_data_queue.put(steel_info)
            else:
                self.steel_data_queue.put(CoolBedError("无法获取有效数据：过多相机失联，或无有效数据"))
            end_time=time.time()
            use_time =end_time-start_time
            print(f"FPS： {self.FPS} use time： {use_time}  ")
            if use_time < 1 / self.FPS:
                time.sleep(1 / self.FPS - use_time)
            else:
                logger.warning(f"单帧处理时间 {use_time}")


        # join
        # for key, cap_ture in self.camera_map.items():
        #     cap_ture.join()


cool_bed_thread_worker_map = {}
def main():
    logger.info("start main")
    global_config = GlobalConfig()
    # 1 获取参数 数据
    for key, config in camera_manage_config.group_dict.items():
        config:CoolBedGroupConfig    # 冷床 参数中心，用于管理冷床参数
        logger.debug(f"初始化 {key} ")
        cool_bed_thread_worker_map[key] = CoolBedThreadWorker(key,config, global_config)

    for key, cool_bed_thread_worker in cool_bed_thread_worker_map.items():  # 等待
        if cool_bed_thread_worker.run_worker:
            cool_bed_thread_worker.join()
    logger.info("end main")


if __name__ == '__main__':
    main()
