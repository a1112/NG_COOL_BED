import json
from datetime import datetime
from typing import Optional, Dict

import cv2

from CONFIG import CAMERA_SAVE_FOLDER, ONE_CAP_FOLDER
from Result.DataItem import DataItem
from Result.DataMap import DataMap
from Result.DetResult import DetResult
from ProjectManagement.PriorityManager import priority_registry


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
        return {
            "bytes":str(bytes(self.send_data_byte)),
            "data":self.send_data_dict,
        }


    def update(self,steel_infos:Dict[str,DetResult]):
        self.data_item_l1 = self.do_l1(steel_infos["L1"])
        self.data_item_l2 = self.do_l2(steel_infos["L2"])
        self.steel_infos = steel_infos
        self.up_count()
        self.current_datas = {"L1": self.data_item_l1, "L2": self.data_item_l2}
        self.data_map = DataMap(self.count,self.current_datas)
        self._update_priority_states()

        self.send_data_dict = self.data_map.get_data_map()
        # print(fr"send_data_dict {self.send_data_dict}")
        self.send_data_byte = self.data_map.data_to_byte(self.send_data_dict)
        # print(fr"send data {self.send_data_byte}")
        self.data_map.send(self.send_data_byte)
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

    def _update_priority_states(self):
        if not self.current_datas:
            return
        for cool_bed_key, data_item in self.current_datas.items():
            group_key = ""
            if data_item is not None:
                group_key = data_item.group_key or ""
            if group_key:
                priority_registry.mark_sending(cool_bed_key, group_key)
            else:
                priority_registry.mark_sending(cool_bed_key, None)
