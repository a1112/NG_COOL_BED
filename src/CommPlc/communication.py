import threading
import time
import datetime
from HslCommunication import SiemensS7Net, SiemensPLCS
from threading import Thread
from snap7.util import get_int, get_real, get_dword, get_string, get_bool, get_char, set_real
import PLC_config
from Loger import logger
from CONFIG import DEBUG_MODEL


# DB = 0x84  # DB  区域c


class ComPlc(threading.Thread):
    def __init__(self):
        super().__init__()
        self.has_run = True
        self.PLC_DATA = b""
        self.DB_AD = "DB6.0"
        self.DB_LEN = 64
        self.last_data_dict = {}
        self.old_temp_in = 0.0
        self.max_temp = 0.0
        self.PLC_IP = PLC_config.IP_L1  # 热矫
        self.siemens = SiemensS7Net(SiemensPLCS.S400, self.PLC_IP)
        self.siemens.SetSlotAndRack(PLC_config.ROCK, PLC_config.SLOT)
        self.set_speed_value = 0
        self.start()

    def close(self):
        self.has_run = False

    def run(self) -> None:
        while self.has_run:
            try:
                time.sleep(0.01)
                start_time = time.time()
                self.PLC_DATA = self.siemens.Read(self.DB_AD, self.DB_LEN).Content
                now = datetime.datetime.now()
                end_time = time.time()
                logger.error(f"PLC DATA ： { self.PLC_DATA}")
            except BaseException as e:
                logger.error(f"{self.DB_AD} PLC 读取 出现错误： {e}")
            else:
                try:
                    self.decodePLC_DATA(self.PLC_DATA, {
                        "getDateTime": now,  # 最新的刷新时间
                        "getTimeLen": end_time - start_time  # PLC 读取延时
                    })
                except BaseException as e:
                    pass
                    # logger.error(f"{self.DB_AD} PLC 解析 出现错误： {e}  : {self.PLC_DATA}")

    def getMaxTemp(self, temp_in):
        self.old_temp_in = max(self.old_temp_in, temp_in)
        self.max_temp = self.old_temp_in
        # if not temp_in == 0.0:
        #     self.old_temp_in = max(self.old_temp_in, temp_in)
        #     self.max_temp = self.old_temp_in
        # else:
        #     self.old_temp_in = 0

    def setInRollerBedSpeed(self, selectList, set_speed_value):
        self.selectList = selectList
        self.set_speed_value = set_speed_value

    old_steel=''
    def decodePLC_DATA(self, PLC_DATA, otherInfo):
        strData = PLC_DATA[34:54].strip(b"\x00")
        strData_15 = PLC_DATA[126:145].strip(b"\x00")
        temp_in = get_real(PLC_DATA[22:26], 0)
        steel=strData.decode("utf-8")

        self.last_data_dict.update(otherInfo)

    def select(self,select_list=None):
            if not select_list:
                select_list=[0,0,0,0,0,0,0,0]
            self.selectList=select_list
            plcList = ["0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "1.0", "1.1"]
            for pcl_data, value in zip(plcList, self.selectList):
                self.siemens.WriteBool(f"DB4600.{pcl_data}", bool(value))
            return True



    def write_byte(self,bytes__):
        print(bytes__)
        print("send len : ",len(bytes__),"  ",self.siemens.Write("DB6.0", bytearray(bytes__)).Message)


class ComDebug:
    pass

if DEBUG_MODEL:
    com = ComDebug()
else:
    com = ComPlc()


if __name__ == "__main__":
    logger.debug("__main__")
