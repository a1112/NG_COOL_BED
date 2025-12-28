import json
import time
from datetime import datetime
from typing import Optional, Dict

import cv2

from CONFIG import CAMERA_SAVE_FOLDER, ONE_CAP_FOLDER
from Result.DataItem import DataItem
from Result.DataMap import DataMap
from Result.DetResult import DetResult


class Business:
    def __init__(self):
        self.data_item_l1 = None
        self.data_item_l2 = None
        self.data_map: Optional[DataMap] = None
        self.count = 0
        self.cool_beds=['L1','L2']
        self.steel_infos = {}
        self.data_item_dict : Dict[str, Dict[str, DataItem]] = {}
        self.send_data_dict = {}
        self.current_datas = {}
        self.send_data_byte = bytearray(b"")
        self.fault_active = False
        self.fault_message = ""
        self.fault_ts = 0.0
        self._last_fault_send_ts = 0.0

    def get_current_data(self,cool_bed_key):
        item : DataItem = self.current_datas[cool_bed_key]
        return item.get_info()

    def get_current_steels(self,steels_dict):
        """
        获取当前的钢坯数据
        """
        for key, steels in steels_dict.items():
            steels: DetResult
            if steels.can_get_data:
                return steels
        return None


    def _do_base_(self,key, steels:DetResult) -> DataItem:
        return DataItem(key, steels)

    def do_base(self,steels_dict,key):
        self.data_item_dict[key] = {key_:self._do_base_(key_, steels) for key_, steels in steels_dict.items()}
        steels = self.get_current_steels(steels_dict)
        return self._do_base_(key, steels)

    def do_l1(self, steels_dict) -> DataItem:
        """
        处理1号冷床数据
        :param steels_dict:
        :return:
        """

        return self.do_base(steels_dict,"L1")



    def do_l2(self, steels_dict) -> DataItem:
        """
        处理二号冷床逻辑
        :param steels_dict:
        :return:
        """
        return self.do_base(steels_dict,"L2")

    def up_count(self):
        self.count += 1
        if self.count > 999:
            self.count = 0

    @property
    def send_data(self):
        last_write_ok_ts = 0.0
        last_write_ok_before_0_1s = None
        try:
            from CommPlc.communication import db6_sender

            last_write_ok_ts = float(getattr(db6_sender, "last_write_ok_ts", 0.0) or 0.0)
            if last_write_ok_ts > 0:
                last_write_ok_before_0_1s = max(0, int((time.time() - last_write_ok_ts) * 10))
        except Exception:
            pass

        return {
            "bytes":str(bytes(self.send_data_byte)),
            "data":self.send_data_dict,
            "plc_last_write_ok_ts": last_write_ok_ts,
            "plc_last_write_ok_before_0_1s": last_write_ok_before_0_1s,
            "fault_active": self.fault_active,
            "fault_message": self.fault_message,
            "fault_ts": self.fault_ts,
        }

    def mark_fault(self, message, send_fault_signal: bool = True):
        self.fault_active = True
        self.fault_message = str(message)
        self.fault_ts = time.time()
        if not send_fault_signal:
            return
        if not self.data_map or not self.send_data_dict:
            return
        now = time.time()
        if now - self._last_fault_send_ts < 1.0:
            return
        fault_data = dict(self.send_data_dict)
        fault_data["I_NAI_ERROR_CB1"] = True
        fault_data["I_NAI_ERROR_CB2"] = True
        try:
            self.send_data_byte = self.data_map.data_to_byte(fault_data)
            self.send_data_dict = fault_data
            self.data_map.send(self.send_data_byte)
            self._last_fault_send_ts = now
        except Exception:
            pass

    def clear_fault(self):
        self.fault_active = False
        self.fault_message = ""
        self.fault_ts = 0.0


    def update(self,steel_infos:Dict[str,DetResult]):
        self.data_item_l1 = self.do_l1(steel_infos["L1"])
        self.data_item_l2 = self.do_l2(steel_infos["L2"])
        self.steel_infos = steel_infos
        self.up_count()
        self.current_datas = {"L1": self.data_item_l1, "L2": self.data_item_l2}
        self.data_map = DataMap(self.count,self.current_datas)
        self.send_data_dict = self.data_map.get_data_map()
        # print(fr"send_data_dict {self.send_data_dict}")
        self.send_data_byte = self.data_map.data_to_byte(self.send_data_dict)
        # print(fr"send data {self.send_data_byte}")
        self.data_map.send(self.send_data_byte)
        self.clear_fault()
        # self.save_cap()

    def save_cap(self):
        """
            保存切片：
        """

        print("保存单张 切片")

        save_folder = CAMERA_SAVE_FOLDER/"cap"/datetime.now().strftime("%Y%m%d")/datetime.now().strftime("%H%M%S")
        save_folder.mkdir(parents=True, exist_ok=True)

        all_dict = {}
        all_dict.update(self.steel_infos["L1"])
        all_dict.update(self.steel_infos["L2"])
        for key, item in all_dict.items():
            item: DetResult
            item.save_cap(key,save_folder)

        json_data = {
            # "steel_info":{
            #     key:item.info()
            #      for key,item in all_dict.items()
            # },
            "currentKey":[ self.data_item_l1.key, self.data_item_l2.key],
            "send_data_dict":self.send_data_dict,
            "send_data_byte":str(self.send_data_byte)
        }
        print(json_data)
        json.dump(json_data, open(CAMERA_SAVE_FOLDER/"cap"/"cap.json","w"))


    def save_one_cap(self):
        """
        保存当前相机画面至 save_data/one_cap
        """
        from Globals import cool_bed_thread_worker_map

        timestamp = datetime.now()
        date_folder = timestamp.strftime("%Y%m%d")
        time_folder = timestamp.strftime("%H%M%S")
        save_folder = ONE_CAP_FOLDER / date_folder / time_folder
        save_folder.mkdir(parents=True, exist_ok=True)

        saved = 0
        for cool_bed_key, worker in cool_bed_thread_worker_map.items():
            frames = worker.snapshot_camera_frames()
            if not frames:
                continue
            bed_folder = save_folder / cool_bed_key
            bed_folder.mkdir(parents=True, exist_ok=True)
            for camera_key, frame in frames.items():
                if frame is None:
                    continue
                save_path = bed_folder / f"{camera_key}.jpg"
                cv2.imwrite(str(save_path), frame)
                saved += 1

        result = {
            "folder": str(save_folder),
            "count": saved,
            "timestamp": timestamp.isoformat()
        }
        print(f"save_one_cap -> {result}")
        return result


    @property
    def current_info(self):
        return {}

