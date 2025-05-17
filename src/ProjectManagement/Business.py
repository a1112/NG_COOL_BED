from IPython.terminal.shortcuts.auto_suggest import accept

from CommPlc.communication import com
from alg.Result import DetResult


class Business:
    def __init__(self):
        self.cool_beds=['L1','L2']
        self.com = com
        self.data_map = {
            "I_NAI_W0_ALV_CNT":0,
            "I_NAI_MET_F1":False, # L1 左侧是否有板子
            "I_NAI_MET_F2":False, # L1 右侧是否有板子
            "I_NAI_MET_F5":False, # L2 左侧是否有板子
            "I_NAI_MET_F6":False, # L2 右侧是否有板子
            "I_NAI_ERROR_CB1": "", # L1 冷床是否有错误
            "I_NAI_ERROR_CB2": "",  #L2 冷床是否有错误
            "I_NAI_W1_spare1": "",
            "I_NAI_W1_spare2": "",
            "I_NAI_W1_spare3": "",
            "I_NAI_W1_spare4": "",
        }


    def do_l1(self, steels):
        """
        处理1号冷床数据
        :param steels:
        :return:
        """
        steels: DetResult
        print(steels)



    def do_l2(self,steels):
        """
        处理二号冷床逻辑
        :param steels:
        :return:
        """
        steels: DetResult

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