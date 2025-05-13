import threading
import time
import datetime
from HslCommunication import SiemensS7Net, SiemensPLCS
from threading import Thread
from snap7.util import get_int, get_real, get_dword, get_string, get_bool, get_char, set_real,get_sint,get_word
import PLC_config
from Loger import logger


DB_AD = "DB6.0"
DB_LEN = 64
PLC_IP = "10.20.28.145"
siemens = SiemensS7Net(SiemensPLCS.S300, PLC_IP)
siemens.SetSlotAndRack(0, 2)
PLC_DATA = siemens.Read(DB_AD, 6).Content
print(PLC_DATA)


a=1345
siemens.Write(f"DB6.0.0",bytearray(a.to_bytes(2,"little")))
siemens.WriteBool(f"DB6.2.0",True)

class L1_4600(threading.Thread):
    def __init__(self):
        super().__init__()
        self.has_run = True
        self.PLC_DATA = b""
        self.DB_AD = "DB4600.0"
        self.DB_LEN = 162
        self.last_data_dict = {}
        self.old_temp_in = 0.0
        self.max_temp = 0.0
        self.PLC_IP = PLC_config.IP_L1_4600  # 热矫
        self.siemens = SiemensS7Net(SiemensPLCS.S400, self.PLC_IP)
        self.siemens.SetSlotAndRack(0, 11)
        self.set_speed_value = 0
        self.selectList = [0, 0, 0, 0, 0, 0, 0, 0]
        self.start()

    def close(self):
        self.has_run = False

    def run(self) -> None:
        while self.has_run:
            try:
                time.sleep(0.01)
                startTime = time.time()
                self.PLC_DATA = self.siemens.Read(self.DB_AD, self.DB_LEN).Content
                now = datetime.datetime.now()
                endTime = time.time()
            except BaseException as e:
                logger.error(f"{self.DB_AD} PLC 读取 出现错误： {e}")
            else:
                try:
                    self.decodePLC_DATA(self.PLC_DATA, {
                        "getDateTime": now,  # 最新的刷新时间
                        "getTimeLen": endTime - startTime  # PLC 读取延时
                    })
                except BaseException as e:
                    logger.error(f"{self.DB_AD} PLC 解析 出现错误： {e}  : {self.PLC_DATA}")
        logger.debug(f"exit： {self.DB_AD} 读取线程自然推出！ ")

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
        if not steel == self.old_steel:
            self.old_steel = steel
            self.old_temp_in = 0
        self.getMaxTemp(temp_in)
        self.last_data_dict.update(
            {
                "SELECT_RTCB1": get_bool(PLC_DATA, 0, 2),
                "SELECT_RTCB2": get_bool(PLC_DATA, 0, 3),
                "SELECT_RTCB3": get_bool(PLC_DATA, 0, 4),
                "SELECT_RTCB4": get_bool(PLC_DATA, 0, 5),
                "SELECT_RTCB5": get_bool(PLC_DATA, 0, 6),
                "SELECT_RTCB6": get_bool(PLC_DATA, 0, 7),
                "SELECT_RTCB7": get_bool(PLC_DATA, 1, 0),
                "SELECT_RTCB8": get_bool(PLC_DATA, 1, 1),

                "STOP": get_bool(PLC_DATA, 3, 2),
                "TO_RK":get_bool(PLC_DATA, 3, 4),

                "19_OUT":True,  # 19号位置脱离

                "D0_RTD_L2": get_bool(PLC_DATA, 2, 1),
                "D0_RTCB_11": get_bool(PLC_DATA, 2, 2),
                "D0_RTCB_12": get_bool(PLC_DATA, 2, 3),
                "D0_RTCB_13": get_bool(PLC_DATA, 2, 4),
                "D0_RTCB_14": get_bool(PLC_DATA, 2, 5),
                "D0_RTCB_21": get_bool(PLC_DATA, 2, 6),
                "D0_RTCB_22": get_bool(PLC_DATA, 2, 7),
                "D0_RTCB_23": get_bool(PLC_DATA, 3, 0),
                "D0_RTCB_19_OUT": get_bool(PLC_DATA, 3, 0),
                "RollerCont": get_bool(PLC_DATA, 3, 3),
                "RTCB1_RUN": get_bool(PLC_DATA, 4, 1),
                "RTCB2_RUN": get_bool(PLC_DATA, 4, 2),
                "RTCB3_RUN": get_bool(PLC_DATA, 4, 3),
                "RTCB4_RUN": get_bool(PLC_DATA, 4, 4),
                "RTCB5_RUN": get_bool(PLC_DATA, 4, 5),
                "RTCB6_RUN": get_bool(PLC_DATA, 4, 6),

                "STEEL_LENGTH_19": get_real(PLC_DATA[10:14], 0),
                "STEEL_WIDTH_19": get_real(PLC_DATA[14:18], 0),
                "STEEL_THICK_19": get_real(PLC_DATA[18:22], 0),
                "STEEL_LENGTH_15": get_real(PLC_DATA[146:150], 0),
                "STEEL_WIDTH_15": get_real(PLC_DATA[150:154], 0),
                "STEEL_THICK_15": get_real(PLC_DATA[154:158], 0),
                "STEEL_NO_15": strData_15.decode("utf-8"),

                "STEEL_TEMP_IN": self.max_temp,
                "STEEL_TEMP_IN_MAX": self.max_temp,

                "DB_VAR12": get_int(PLC_DATA[26:28], 0),
                "DB_VAR11": get_int(PLC_DATA[28:30], 0),

                "STEEL_WEIGHT": get_real(PLC_DATA[30:34], 0),
                "STEEL_NO": strData.decode("utf-8"),

                "AL_ROLL_SPEED_REF": get_real(PLC_DATA[58:62], 0),

                "R0_RTD_L2_SPEED": get_real(PLC_DATA[70:74], 0),
                "R0_RTCB1_SPEED": get_real(PLC_DATA[74:78], 0),
                "R0_RTCB2_SPEED": get_real(PLC_DATA[78:82], 0),
                "R0_RTCB3_SPEED": get_real(PLC_DATA[82:86], 0),
                "R0_RTCB4_SPEED": get_real(PLC_DATA[86:90], 0),
                "R0_RTCB5_SPEED": get_real(PLC_DATA[90:94], 0),
                "R0_RTCB6_SPEED": get_real(PLC_DATA[94:98], 0),
                "R0_RTCB7_SPEED": get_real(PLC_DATA[98:102], 0),
                "R0_RTCB8_SPEED": get_real(PLC_DATA[102:106], 0),
                "R0_RTCB_SPEED_REF": get_real(PLC_DATA[106:110], 0),
            }
        )
        self.last_data_dict.update(otherInfo)

    def select(self,select_list=None):
            if not select_list:
                select_list=[0,0,0,0,0,0,0,0]
            self.selectList=select_list
            plcList = ["0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "1.0", "1.1"]
            for pcl_data, value in zip(plcList, self.selectList):
                self.siemens.WriteBool(f"DB4600.{pcl_data}", bool(value))
            return True

    def setL1Lock(self, lock):
        logger.debug(f"辊道 设置 锁定 {lock}")
        self.siemens.WriteBool(f"DB4600.3.3", bool(lock))

    def setSpeed(self,speed):
        self.set_speed_value = speed
        data = bytearray(4)
        self.siemens.Write("DB4600.58", set_real(data, 0, self.set_speed_value))
        return True

    def stop(self):
        self.select()
        self.setSpeed(0)
        return True


