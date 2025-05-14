from IPython.terminal.shortcuts.auto_suggest import accept

from CommPlc.communication import com
from alg.Result import DetResult


class Business:
    def __init__(self):
        self.cool_beds=['L1','L2']
        self.com = com


    def do_l1(self, steels):
        """
        处理1号冷床数据
        :param steels:
        :return:
        """
        steels: DetResult


    def do_l2(self,steels):
        """
        处理二号冷床逻辑
        :param steels:
        :return:
        """
        pass

    def update(self,steel_infos:dict):
        print(f"update Business {steel_infos}")
        assert "L1" in steel_infos,"error"
        assert "L2" in steel_infos, "error"
        self.do_l1(steel_infos["L1"])
        self.do_l2(steel_infos["L2"])