from typing import Optional

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
        self.data_item_dict = {}
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


    def _do_base_(self,key, steels) -> DataItem:

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


    def update(self,steel_infos:dict):
        print(f"update Business {steel_infos}")
        self.data_item_l1 = self.do_l1(steel_infos["L1"])
        self.data_item_l2 = self.do_l2(steel_infos["L2"])
        self.steel_infos = steel_infos
        self.up_count()
        self.current_datas = {"L1": self.data_item_l1, "L2": self.data_item_l2}
        self.data_map = DataMap(self.count,self.current_datas)

        self.send_data_dict = self.data_map.get_data_map()
        self.send_data_byte = self.data_map.data_to_byte(self.send_data_dict)

        self.data_map.send(self.send_data_byte)


    @property
    def current_info(self):
        return {}