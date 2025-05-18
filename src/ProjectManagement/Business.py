from CommPlc.communication import com
from Result.DetResult import DetResult


class DataItem:
    def __init__(self,key, steels: DetResult):
        self.key = key
        self.steels = steels
        self.has_roll_steel_left = False  #  辊道存在板子 左侧
        self.has_roll_steel_right = False  # 辊道存在板子 右侧

        self.has_cool_bed_steel_left = False
        self.has_cool_bed_steel_right = False

    @property
    def roll_steel(self):
        return self.steels.roll_steel

    @property
    def cool_bed_steel(self):
        return self.steels.cool_bed_steel


class Business:
    def __init__(self):
        self.cool_beds=['L1','L2']
        self.com = com
        self.data_map = {
            "I_NAI_W0_ALV_CNT":0, # 心跳
            "I_NAI_MET_F1": False, # L1 左侧是否有板子
            "I_NAI_MET_F2": False, # L1 右侧是否有板子
            "I_NAI_MET_F5": False, # L2 左侧是否有板子
            "I_NAI_MET_F6": False, # L2 右侧是否有板子
            "I_NAI_ERROR_CB1": "", # L1 冷床是否有错误
            "I_NAI_ERROR_CB2": "",  #L2 冷床是否有错误
            "I_NAI_W1_spare1": "", # 一号冷床左半段有钢
            "I_NAI_W1_spare2": "",
            "I_NAI_W1_spare3": "",
            "I_NAI_W1_spare4": "",
        }


    def do_base(self,steels,key):
        data_item = DataItem(key,steels)
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
        steels
        print(steels)
        return data_item

    def do_l1(self, steels):
        """
        处理1号冷床数据
        :param steels:
        :return:
        """
        return self.do_base(steels,"L1")



    def do_l2(self,steels):
        """
        处理二号冷床逻辑
        :param steels:
        :return:
        """
        return self.do_base(steels,"L2")

    def up_count(self):
        self.data_map["I_NAI_W0_ALV_CNT"] += 1
        if self.data_map["I_NAI_W0_ALV_CNT"] > 999:
            self.data_map["I_NAI_W0_ALV_CNT"] = 0


    def set_data(self):
        self.up_count()


    def update(self,steel_infos:dict):
        print(f"update Business {steel_infos}")
        assert "L1" in steel_infos,"error"
        assert "L2" in steel_infos, "error"
        self.do_l1(steel_infos["L1"])
        self.do_l2(steel_infos["L2"])
        self.set_data()