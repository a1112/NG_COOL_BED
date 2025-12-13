import time
from typing import Optional

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
from ProjectManagement.PriorityManager import priority_registry

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
        self.DEBUG_FPS = 7

        self.join_image_dict = {}  # 全部的 返回參數
        self.priority_controller = priority_registry.create_controller(key, self.config.groups)
        self.group_results = {group.group_key: None for group in self.config.groups}

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
        predictor = SteelPredict()
        if not CONFIG.DEBUG_MODEL:
            self.save_thread = CapJoinSave(self.config)
        for key, camera_config in self.config.camera_map.items():
            camera_config:CameraConfig
            camera_config.set_start(self.global_config.start_datetime_str)  # 设置统一时间
            self.camera_map[key] = RtspCapTure(camera_config, self.global_config)  # 执行采集   <<<-------------------
        cap_index = 0
        while True:
            cap_index += 1
            start_time = time.time()
            plan_groups = self.priority_controller.next_iteration_groups()
            if not plan_groups:
                if all(getattr(group_config, "shield", False) for group_config in self.config.groups):
                    steel_info_dict = {group.group_key: None for group in self.config.groups}
                    self.steel_data_queue.put(steel_info_dict)
                    time.sleep(0.2)
                else:
                    time.sleep(0.1)
                continue
            need_cameras = set()
            for group_key in plan_groups:
                group_config = self.config.groups_dict.get(group_key)
                if group_config:
                    need_cameras.update(group_config.camera_list)
            if not need_cameras:
                time.sleep(0.02)
                continue
            cap_dict = {key: self.camera_map[key].get_cap() for key in need_cameras if key in self.camera_map}
            try:
                for group_key in plan_groups:
                    group_config = self.config.groups_dict.get(group_key)
                    if group_config is None:
                        continue
                    calibrate = group_config.calibrate_image(cap_dict)
                    self._up_join_image_(group_config.group_key, calibrate)
                    if self.save_thread:
                        self.save_thread.save_buffer(group_config.group_key, calibrate)
                    steel_info = predictor.predict(calibrate, group_config)
                    self.group_results[group_key] = steel_info
                    priority_registry.record_detection(self.key, group_key, steel_info)
                steel_info_dict = {}
                missing_data = False
                for group_config in self.config.groups:
                    result = self.group_results.get(group_config.group_key)
                    if result is None and not getattr(group_config, "shield", False):
                        missing_data = True
                    steel_info_dict[group_config.group_key] = result
                if missing_data:
                    time.sleep(0.01)
                    continue
                self.steel_data_queue.put(steel_info_dict)
                end_time = time.time()
                use_time = end_time - start_time
                if CONFIG.DEBUG_MODEL:
                    if use_time < 1 / self.DEBUG_FPS:
                        time.sleep(1 / self.DEBUG_FPS - use_time)
                    else:
                        logger.warning(f"单帧处理时间 {use_time}")
                    time.sleep(0.2)
            except BaseException as e:
                logger.error(e)
                for group_key in plan_groups:
                    priority_registry.record_detection(self.key, group_key, None)

    def get_steel_info(self):
        return self.steel_data_queue.get()


    # for key, cool_bed_thread_worker in cool_bed_thread_worker_map.items():  # 等待
    #     if cool_bed_thread_worker.run_worker:
    #         cool_bed_thread_worker.join()
