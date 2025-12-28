import time
import queue
from typing import Optional

import numpy as np

import CONFIG
from Base import RollingQueue
from Base.Error import CoolBedError
from Configs.CalibrateConfig import CalibrateConfig
from Configs.GlobalConfig import GlobalConfig
from Configs.GroupConfig import GroupConfig
from Configs.CoolBedGroupConfig import CoolBedGroupConfig
from Loger import logger
from threading import Thread, Lock
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
        self.DEBUG_FPS = 12

        self._image_lock = Lock()
        self._latest_image_cache = {}
        self._latest_image_cache_id = {}

        self.join_image_dict = {}  # 全部的 返回參數
        self.group_results = {group.group_key: None for group in self.config.groups}

        if  self.run_worker:
            logger.debug(f"开始 执行 {key} ")
            self.start()

    def get_image(self, key,show_mask):
        with self._image_lock:
            item = self.join_image_dict.get(key)
        if item is not None:
            id_, calibrate = item
            calibrate: CalibrateConfig
            if show_mask:
                return id_, calibrate.mask_image
            return id_, calibrate.image
        return -1, None

    def _build_latest_calibrate(self, group_key: str):
        group_config = self.config.groups_dict.get(group_key)
        if group_config is None:
            return None, 0.0
        frames = []
        newest_ts = 0.0
        for camera_id in group_config.camera_list:
            capture = self.camera_map.get(camera_id)
            if capture is None:
                return None, 0.0
            if hasattr(capture, "get_latest_frame_with_ts"):
                frame, ts = capture.get_latest_frame_with_ts()
            else:
                frame, ts = capture.get_latest_frame(), 0.0
            if frame is None:
                return None, 0.0
            frames.append(frame)
            if ts and ts > newest_ts:
                newest_ts = ts
        conversion_image_list = [
            conv.image_conversion(frame)
            for conv, frame in zip(group_config.conversion_list, frames)
        ]
        return CalibrateConfig(conversion_image_list), newest_ts

    def get_latest_image(self, group_key: str, show_mask: int, min_interval_s: float = 0.05):
        """
        Build the latest stitched image directly from each camera's latest frame.
        This bypasses the full detection loop to avoid UI latency.
        """
        now = time.time()
        show_mask = int(show_mask)
        with self._image_lock:
            cached = self._latest_image_cache.get(group_key)
            if cached and now - float(cached.get("ts") or 0.0) < float(min_interval_s):
                cached_id = int(cached.get("id") or 0)
                return cached_id, (cached.get("mask") if show_mask else cached.get("image"))

        calibrate, frame_ts = self._build_latest_calibrate(group_key)
        if calibrate is None:
            return -1, None

        image = calibrate.image
        mask = None
        if show_mask:
            mask = getattr(calibrate, "mask_image", None)
            if mask is None:
                mask = np.zeros_like(image)

        with self._image_lock:
            next_id = int(self._latest_image_cache_id.get(group_key) or 0) + 1
            self._latest_image_cache_id[group_key] = next_id
            self._latest_image_cache[group_key] = {
                "id": next_id,
                "ts": now,
                "frame_ts": frame_ts,
                "image": image,
                "mask": mask,
            }
        return next_id, (mask if show_mask else image)

    def snapshot_camera_frames(self):
        frames = {}
        for key, capture in self.camera_map.items():
            frame = capture.get_latest_frame()
            if frame is not None:
                frames[key] = frame
        return frames

    def _up_join_image_(self,key, calibrate:CalibrateConfig):
        with self._image_lock:
            if key in self.join_image_dict:
                self.join_image_dict[key][0] = self.join_image_dict[key][0] + 1
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
            try:
                cap_index += 1
                start_time = time.time()
                plan_groups = [
                    group.group_key
                    for group in self.config.groups
                    if not getattr(group, "shield", False)
                ]
                if not plan_groups:
                    steel_info_dict = {group.group_key: None for group in self.config.groups}
                    self.steel_data_queue.put(steel_info_dict)
                    time.sleep(0.02)
                    continue
                try:
                    missing_data = False
                    batch_items = []
                    batch_images = []
                    fetch_start = time.time()
                    for group_key in plan_groups:
                        group_config = self.config.groups_dict.get(group_key)
                        if group_config is None:
                            continue
                        calibrate, _ = self._build_latest_calibrate(group_key)
                        if calibrate is None:
                            self.group_results[group_key] = None
                            missing_data = True
                            continue
                        batch_items.append((group_key, group_config, calibrate))
                        batch_images.append(calibrate.image)
                    fetch_time = time.time() - fetch_start

                    infer_time = 0.0
                    batch_boxes = []
                    if batch_images:
                        infer_start = time.time()
                        batch_boxes = predictor.det_model.get_steel_rect_batch(batch_images)
                        infer_time = time.time() - infer_start

                    for idx, (group_key, group_config, calibrate) in enumerate(batch_items):
                        self._up_join_image_(group_config.group_key, calibrate)
                        if self.save_thread:
                            self.save_thread.save_buffer(group_config.group_key, calibrate)
                        model_data = batch_boxes[idx] if idx < len(batch_boxes) else []
                        steel_info = predictor.predict_from_boxes(calibrate, group_config, model_data)
                        self.group_results[group_key] = steel_info

                    logger.info(
                        "batch_groups=%s fetch_s=%.3f infer_s=%.3f",
                        len(batch_images),
                        fetch_time,
                        infer_time,
                    )
                    steel_info_dict = {}
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
                    logger.info("全链路耗时=%.3fs batch_groups=%s", use_time, len(batch_images))
                except BaseException as e:
                    logger.error(e)
            except Exception as exc:
                logger.exception("CoolBedThreadWorker loop error: %s", exc)
                time.sleep(0.5)

    def get_steel_info(self):
        try:
            return self.steel_data_queue.get()
        except queue.Empty:
            return None


    # for key, cool_bed_thread_worker in cool_bed_thread_worker_map.items():  # 等待
    #     if cool_bed_thread_worker.run_worker:
    #         cool_bed_thread_worker.join()
