from Result.DataItem import DataItem
from Result.DataMap import DataMap
from Result.DetResult import DetResult


class Business:
    def __init__(self):
        self.data_item_l1 = None
        self.data_item_l2 = None
        self.data_map:DataMap | None = None
        self.count = 0
        self.cool_beds=['L1','L2']
        self.steel_infos = {}
        self.data_item_dict = {}
        self.send_data = {}

    def get_current_steels(self,steels_dict):
        for key, steels in steels_dict.items():
            steels: DetResult
            if steels.can_get_data:
                return steels
        return None


    def _do_base_(self,key, steels) -> DataItem:

        data_item = DataItem(key, steels)
        steels: DetResult
        if steels.has_roll_steel:

            for steel in steels.roll_steel:
                if steel.in_left:
                    data_item.has_roll_steel_left = True
                if steel.in_right:
                    data_item.has_roll_steel_right = True

        if steels.has_cool_bed_steel:
            for steel in steels.cool_bed_steel:
                if steel.in_left:
                    data_item.has_cool_bed_steel_left = True
                if steel.in_right:
                    data_item.has_cool_bed_steel_right = True

        return data_item

    def do_base(self,steels_dict,key):
        self.data_item_dict[key] = {key_:self._do_base_(key_, steels) for key_, steels in steels_dict.items()}
        steels = self.get_current_steels(steels_dict)
        return self._do_base_(key, steels)

    def do_l1(self, steels_dict):
        """
        处理1号冷床数据
        :param steels:
        :return:
        """

        return self.do_base(steels_dict,"L1")



    def do_l2(self, steels_dict):
        """
        处理二号冷床逻辑
        :param steels:
        :return:
        """
        return self.do_base(steels_dict,"L2")

    def up_count(self):
        self.count += 1
        if self.count > 999:
            self.count = 0


    def update(self,steel_infos:dict):
        print(f"update Business {steel_infos}")
        self.data_item_l1 = self.do_l1(steel_infos["L1"])
        self.data_item_l2 = self.do_l2(steel_infos["L2"])
        self.steel_infos = steel_infos
        self.up_count()
        self.data_map = DataMap(self.count,{"L1":self.data_item_l1,"L2":self.data_item_l2})
        try:
            self.send_data = self.data_map.get_data_map()
            self.data_map.send()
        except BaseException as e:
            print(e)
