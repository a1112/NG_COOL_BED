import time
from typing import Optional

from tqdm import tqdm

import CONFIG
from Base import RollingQueue
from Base.Error import CoolBedError
from Configs.CalibrateConfig import CalibrateConfig
from Configs.GlobalConfig import GlobalConfig
from Configs.GroupConfig import GroupConfig
from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Loger import logger
from threading import Thread
from Configs.CameraConfig import CameraConfig
from CameraStreamer.RtspCapTure import RtspCapTure
from Configs.CameraManageConfig import camera_manage_config
from Save.CapJoinSave import CapJoinSave
from alg.YoloModel import SteelDetModel, SteelPredict
from Result.DetResult import DetResult
from tool import show_cv2
from collections import OrderedDict

class CoolBedThreadWorker(Thread):
    """
    单个冷床 的 循环
    """
    def __init__(self,key, config:CoolBedGroupConfig, global_config:GlobalConfig):
        super().__init__()
        self.save_thread: Optional[CapJoinSave] = None
        self.key = key
        self.global_config = global_config
        self.run_worker = camera_manage_config.run_worker_key(key)
        self.config = config  #  对于组别的参数试图
        self.camera_map = {}
        self.steel_data_queue = RollingQueue(maxsize=1)
        self.FPS = 7

        self.join_image_dict = {}  # 全部的 返回參數

        if  self.run_worker:
            logger.debug(f"开始 执行 {key} ")
            self.start()

    def get_image(self, key,show_mask):
        if key in self.join_image_dict:
            id_,calibrate = self.join_image_dict[key]
            calibrate:CalibrateConfig
            if show_mask:
                return id_, calibrate.mask_image
            return id_, calibrate.image
        return -1, None

    def snapshot_camera_frames(self):
        frames = {}
        for key, capture in self.camera_map.items():
            frame = capture.get_latest_frame()
            if frame is not None:
                frames[key] = frame
        return frames

    def _up_join_image_(self,key, calibrate:CalibrateConfig):
        if key in self.join_image_dict:
            self.join_image_dict[key][0] = self.join_image_dict[key][0]+1
            self.join_image_dict[key][1] = calibrate
        else:
            self.join_image_dict[key] = [0, calibrate]

    def get_data(self):
        return

    def run(self):
        print(f"start  CoolBedThreadWorker {self.key}")
        # model = SteelDetModel()
        predictor = SteelPredict()
        if not CONFIG.DEBUG_MODEL:
            self.save_thread = CapJoinSave(self.config)
        #  工作1， 相机初始化
        for key, camera_config in self.config.camera_map.items():
            camera_config:CameraConfig
            camera_config.set_start(self.global_config.start_datetime_str)  # 设置统一时间
            self.camera_map[key] = RtspCapTure(camera_config, self.global_config)  # 执行采集   <<<-------------------
        cap_index=0
        tq = tqdm()
        while True:
            # tq.update(1)
            cap_index += 1
            start_time = time.time()
            # 工作2 采集 1 CAPTURE
            cap_dict = {key: cap_ture.get_cap() for key, cap_ture in self.camera_map.items()}
            steel_info_dict = {}
            # 工作3 处理 透视 表
            try:
                for group_config in self.config.groups:  # 注意排序规则
                    group_config: GroupConfig
                    calibrate = group_config.calibrate_image(cap_dict)
                    self._up_join_image_(group_config.group_key, calibrate)
                    # 调整中的工作-----------------------------------
                    # 工作4 识别
                    if self.save_thread:
                        self.save_thread.save_buffer(group_config.group_key, calibrate)

                    # steel_info = DetResult(calibrate, model_data, group_config.map_config)

                    steel_info = predictor.predict(calibrate, group_config)

                    # if self.key == "L2":
                    #     print(fr" steel_info: {steel_info} ")

                    steel_info_dict[group_config.group_key] = steel_info
                    # if steel_info.can_get_data: # 如果有符合（无冷床遮挡）则返回数据
                    #     continue
                # 工作5 识别结果 的逻辑处理
                self.steel_data_queue.put(steel_info_dict)
                # if steel_info is not None:
                #     self.steel_data_queue.put(steel_info)
                # else:
                #     self.steel_data_queue.put(CoolBedError("无法获取有效数据：过多相机失联，或无有效数据"))
                end_time=time.time()
                use_time =end_time-start_time
                # print(f"FPS： {self.FPS} use time： {use_time}  ")
                if use_time < 1 / self.FPS:
                    time.sleep(1 / self.FPS - use_time)
                else:
                    if not CONFIG.DEBUG_MODEL:
                        logger.warning(f"单帧处理时间 {use_time}")
                if CONFIG.DEBUG_MODEL:
                    time.sleep(0.2)
            except BaseException as e:
                logger.error(e)
        # join
        # for key, cap_ture in self.camera_map.items():
        #     cap_ture.join()

    def get_steel_info(self):
        return self.steel_data_queue.get()


    # for key, cool_bed_thread_worker in cool_bed_thread_worker_map.items():  # 等待
    #     if cool_bed_thread_worker.run_worker:
    #         cool_bed_thread_worker.join()
