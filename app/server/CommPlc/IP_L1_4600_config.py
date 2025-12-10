import threading
import time
import logging
import datetime
from HslCommunication import SiemensS7Net, SiemensPLCS
from threading import Thread
from snap7.util import get_int, get_real, get_dword, get_string, get_bool, get_char
import PLC_config


# DB = 0x84  # DB  区域c

class L1_4600(threading.Thread):
    def __init__(self):
        super().__init__()
        self.has_run = True
        self.PLC_DATA = b""
        self.DB_AD = "DB4600.0"
        self.DB_LEN = 114
        self.last_data_dict = {}
        self.start()

    def close(self):
        self.has_run = False

    def run(self) -> None:
        PLC_IP = PLC_config.IP_L1_4600  # 热矫
        siemens = SiemensS7Net(SiemensPLCS.S400, PLC_IP)
        siemens.SetSlotAndRack(0, 11)
        while self.has_run:
            try:
                startTime = time.time()
                self.PLC_DATA = siemens.Read(self.DB_AD, self.DB_LEN).Content
                now = datetime.datetime.now()
                endTime = time.time()
            except BaseException as e:
                logging.error(f"{self.DB_AD} PLC 读取 出现错误： {e}")
            else:
                try:
                    self.decodePLC_DATA(self.PLC_DATA, {
                        "getDateTime": now,  # 最新的刷新时间
                        "getTimeLen": endTime - startTime  # PLC 读取延时
                    })
                except BaseException as e:
                    pass
                    # logger.error(f"{self.DB_AD} PLC 解析 出现错误： {e}  : {self.PLC_DATA}")
        logging.info(f"exit： {self.DB_AD} 读取线程自然推出！ ")


    def decodePLC_DATA(self, PLC_DATA, otherInfo):
        RTC_ALL = bin(ord(PLC_DATA[2:3]))[2:].zfill(8)+bin(ord(PLC_DATA[3:4]))[2:].zfill(8)
        RTC_ALL = [int(i) for i in RTC_ALL]
        self.last_data_dict.update(
            {"D0_RTD_L2": bool(RTC_ALL[1]),
             "D0_RTCB_11": bool(RTC_ALL[2]),
             "D0_RTCB_12": bool(RTC_ALL[3]),
             "D0_RTCB_13": bool(RTC_ALL[4]),
             "D0_RTCB_14": bool(RTC_ALL[5]),
             "D0_RTCB_21": bool(RTC_ALL[6]),
             "D0_RTCB_22": bool(RTC_ALL[7]),
             "D0_RTCB_23": bool(RTC_ALL[8]),

             "DB_VAR2": get_int(PLC_DATA[4:6], 0),
             "DB_VAR3": get_int(PLC_DATA[8:10], 0),

             "STEEL_LENGTH_19": get_real(PLC_DATA[10:14], 0),
             "STEEL_WIDTH_19": get_real(PLC_DATA[10:14], 0),
             "STEEL_THICK_19": get_real(PLC_DATA[14:18], 0),
             "STEEL_TEMP_IN": get_real(PLC_DATA[18:22], 0),

             "DB_VAR12": get_int(PLC_DATA[26:28], 0),
             "DB_VAR11": get_int(PLC_DATA[28:30], 0),

             "STEEL_WEIGHT": get_real(PLC_DATA[30:34], 0),
             "STEEL_NO": get_string(PLC_DATA[34:54], 0).strip(),

             "AL_ROLL_SPEED_REF": get_real(PLC_DATA[58:62], 0),     # 设置速度

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
        # print(self.last_data_dict)


if __name__=="__main__":
    L1_4600()
