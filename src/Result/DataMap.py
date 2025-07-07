from .DataItem import DataItem
from CommPlc.communication import com

def byte_join(*args):
    return b''.join(args)

def format_int(data_item):
    return int(data_item/10)

def get_int_byte(value:int):
    return bytearray(value.to_bytes(2, "little", signed = True))

def get_bools_byte(original:list):
    bits = [int(b) for b in original]
    byte_data = bytes([int(''.join(map(str, bits)), 2)])
    return byte_data

class DataMap:
    def __init__(self, count, data_dict):
        self.data_dict = data_dict
        self.count = count
        self.com = com
        self.l1_data:DataItem = self.data_dict["L1"]
        self.l2_data:DataItem = self.data_dict["L2"]

    def get_info_by_cool_bed(self,cool_bed):
        data_item = self.data_dict[cool_bed]
        data_item:DataItem
        return {
            "left_cool_bed_has_steel":data_item.has_cool_bed_steel_left,
            "right_cool_bed_has_steel": data_item.has_cool_bed_steel_right,
            "left_roll_bed_has_steel": data_item.has_roll_steel_left,
            "right_roll_bed_has_steel": data_item.has_roll_steel_right,
            "group_key": data_item.group_key,
            "has_error": data_item.has_error,
            "left_under_steel_to_center": data_item.left_under_steel.to_roll_center_y,
            "right_under_steel_to_center": data_item.right_under_steel.to_roll_center_y,


            "objects" : data_item.steels.infos
        }

    def get_data_map(self):
        data =  {
            "VERSION":"1.0.0",
            "I_NAI_W0_ALV_CNT":self.count, # 心跳
            "I_NAI_MET_F1": self.l1_data.has_roll_steel_left, # L1 左侧是否有板子
            "I_NAI_MET_F2": self.l1_data.has_roll_steel_right, # L1 右侧是否有板子
            "I_NAI_MET_F5": self.l2_data.has_roll_steel_left, # L2 左侧是否有板子
            "I_NAI_MET_F6": self.l2_data.has_roll_steel_right, # L2 右侧是否有板子
            "I_NAI_LONG_CB1":False, "I_NAI_LONG_CB2":False,
            "I_NAI_ERROR_CB1": self.l1_data.has_error, # L1 冷床是否有错误
            "I_NAI_ERROR_CB2": self.l2_data.has_error,  #L2 冷床是否有错误
            "I_NAI_LONG_F12":False, "I_NAI_LONG_F56":False,
            "I_NAI_W1_spare1": self.l1_data.has_cool_bed_steel_left, # 一号冷床左半段有钢
            "I_NAI_W1_spare2": self.l1_data.has_cool_bed_steel_right, # 一号冷床右半段有钢
            "I_NAI_W1_spare3": self.l2_data.has_cool_bed_steel_left, # 二号冷床左半段有钢
            "I_NAI_W1_spare4": self.l2_data.has_cool_bed_steel_right, # 二号冷床右半段有钢
            "I_NAI_W1_spare5": False, "I_NAI_W1_spare6": False
        }

        left_under_steel_l1 = self.l1_data.left_under_cool_bed_steel
        data.update({
            "I_NAI_X_dis_CB1G3":format_int( left_under_steel_l1.x_mm),
            "I_NAI_Y_dis_CB1G3":int(left_under_steel_l1.to_under_mm),#format_int(  left_under_steel_l1.to_under_mm),
            "I_NAI_Len_CB1G3": format_int( left_under_steel_l1.w_mm),
            "I_NAI_Wid_CB1G3": format_int( left_under_steel_l1.h_mm),
            "I_NAI_Ang_CB1G3": 0,
        })
        right_under_steel_l1 = self.l1_data.right_under_cool_bed_steel
        data.update({
            "I_NAI_X_dis_CB1G4":format_int( right_under_steel_l1.x_mm),
            "I_NAI_Y_dis_CB1G4":int(right_under_steel_l1.to_under_mm), #format_int( right_under_steel_l1.y_mm),
            "I_NAI_Len_CB1G4":format_int( right_under_steel_l1.w_mm),
            "I_NAI_Wid_CB1G4":format_int( right_under_steel_l1.h_mm),
            "I_NAI_Ang_CB1G4":0,
        })

        left_under_steel_l2 = self.l2_data.left_under_cool_bed_steel
        data.update({
            "I_NAI_X_dis_CB2G3": format_int( left_under_steel_l2.x_mm),
            "I_NAI_Y_dis_CB2G3":int(left_under_steel_l2.to_under_mm),# format_int( left_under_steel_l2.y_mm),
            "I_NAI_Len_CB2G3": format_int( left_under_steel_l2.w_mm),
            "I_NAI_Wid_CB2G3": format_int( left_under_steel_l2.h_mm),
            "I_NAI_Ang_CB2G3": 0,
        })
        right_under_steel_l2 = self.l2_data.right_under_cool_bed_steel
        print(fr"self.l2_data.right_under_cool_bed_steel {self.l2_data.right_under_cool_bed_steel}")
        data.update({
            "I_NAI_X_dis_CB2G4":format_int( right_under_steel_l2.x_mm),
            "I_NAI_Y_dis_CB2G4":int(right_under_steel_l2.to_under_mm),#format_int( right_under_steel_l2.y_mm),
            "I_NAI_Len_CB2G4":format_int( right_under_steel_l2.w_mm),
            "I_NAI_Wid_CB2G4":format_int( right_under_steel_l2.h_mm),
            "I_NAI_Ang_CB2G4":0,
        })

        data.update(
            {
            "I_NAI_Y_dis_F1":format_int(left_under_steel_l1.to_roll_center_y),
            "I_NAI_Ang_F1": 0
            }
        )

        data.update(
            {
            "I_NAI_Y_dis_F2":format_int(right_under_steel_l1.to_roll_center_y),
            "I_NAI_Ang_F2": 0
            }
        )

        data.update(
            {
            "I_NAI_Y_dis_F5":format_int(left_under_steel_l2.to_roll_center_y),
            "I_NAI_Ang_F5": 0
            }
        )

        data.update(
            {
            "I_NAI_Y_dis_F6":format_int(right_under_steel_l2.to_roll_center_y),
            "I_NAI_Ang_F6": 0
            }
        )

        data.update(
            {
              "I_NAI_W30_spare":0,
                "I_NAI_W31_spare":0
            }

        )
        print(data)
        return data

    def data_to_byte(self, data):
        return (get_int_byte(data["I_NAI_W0_ALV_CNT"])
                +get_bools_byte([data["I_NAI_MET_F1"], data["I_NAI_MET_F2"],
                                 data["I_NAI_MET_F5"], data["I_NAI_MET_F6"],
                                 data["I_NAI_LONG_CB1"], data["I_NAI_LONG_CB2"],
                                 data["I_NAI_ERROR_CB1"], data["I_NAI_ERROR_CB2"],
                                 ])
                +get_bools_byte([data["I_NAI_LONG_F12"], data["I_NAI_LONG_F56"],
                                 data["I_NAI_W1_spare1"], data["I_NAI_W1_spare2"],
                                 data["I_NAI_W1_spare3"], data["I_NAI_W1_spare4"],
                                 data["I_NAI_W1_spare5"], data["I_NAI_W1_spare6"],
                                 ])

                + get_int_byte(data["I_NAI_X_dis_CB1G3"])
                + get_int_byte(data["I_NAI_Y_dis_CB1G3"])
                + get_int_byte(data["I_NAI_Len_CB1G3"])
                + get_int_byte(data["I_NAI_Wid_CB1G3"])
                + get_int_byte(data["I_NAI_Ang_CB1G3"])

                + get_int_byte(data["I_NAI_X_dis_CB1G4"])
                + get_int_byte(data["I_NAI_Y_dis_CB1G4"])
                + get_int_byte(data["I_NAI_Len_CB1G4"])
                + get_int_byte(data["I_NAI_Wid_CB1G4"])
                + get_int_byte(data["I_NAI_Ang_CB1G4"])

                + get_int_byte(data["I_NAI_X_dis_CB2G3"])
                + get_int_byte(data["I_NAI_Y_dis_CB2G3"])
                + get_int_byte(data["I_NAI_Len_CB2G3"])
                + get_int_byte(data["I_NAI_Wid_CB2G3"])
                + get_int_byte(data["I_NAI_Ang_CB2G3"])

                + get_int_byte(data["I_NAI_X_dis_CB2G4"])
                + get_int_byte(data["I_NAI_Y_dis_CB2G4"])
                + get_int_byte(data["I_NAI_Len_CB2G4"])
                + get_int_byte(data["I_NAI_Wid_CB2G4"])
                + get_int_byte(data["I_NAI_Ang_CB2G4"])

                + get_int_byte(data["I_NAI_Y_dis_F1"])
                + get_int_byte(data["I_NAI_Ang_F1"])

                + get_int_byte(data["I_NAI_Y_dis_F2"])
                + get_int_byte(data["I_NAI_Ang_F2"])

                + get_int_byte(data["I_NAI_Y_dis_F5"])
                + get_int_byte(data["I_NAI_Ang_F5"])

                + get_int_byte(data["I_NAI_Y_dis_F6"])
                + get_int_byte(data["I_NAI_Ang_F6"])

                + get_int_byte(data["I_NAI_W30_spare"])
                + get_int_byte(data["I_NAI_W31_spare"])
                )



    def send(self,send_data_byte):
        self.com.write_byte(send_data_byte)