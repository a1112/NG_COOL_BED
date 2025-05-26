from .DataItem import DataItem
from CommPlc.communication import com

class DataMap:
    def __init__(self, count, data_dict):
        self.data_dict = data_dict
        self.count = count
        self.com = com
        self.l1_data:DataItem = self.data_dict["L1"]
        self.l2_data:DataItem = self.data_dict["L2"]

    def get_info_by_cool_bed(self,cool_bed):
        data_item = self.data_dict[cool_bed]

        return {
            "left_cool_bed_has_steel":data_item.has_cool_bed_steel_left,
            "right_cool_bed_has_steel": data_item.has_cool_bed_steel_right,
            "left_roll_bed_has_steel": data_item.has_roll_steel_left,
            "right_roll_bed_has_steel": data_item.has_roll_steel_right,
            "group_key": data_item.group_key,
            "has_error": data_item.has_error,
            "left_under_steel_to_center": data_item.left_under_steel.to_roll_center_y,
            "right_under_steel_to_center": data_item.right_under_steel.to_roll_center_y,
        }

    def get_data_map(self):
        data =  {
            "I_NAI_W0_ALV_CNT":self.count, # 心跳
            "I_NAI_MET_F1": self.l1_data.has_roll_steel_left, # L1 左侧是否有板子
            "I_NAI_MET_F2": self.l1_data.has_roll_steel_right, # L1 右侧是否有板子
            "I_NAI_MET_F5": self.l2_data.has_roll_steel_left, # L2 左侧是否有板子
            "I_NAI_MET_F6": self.l2_data.has_roll_steel_right, # L2 右侧是否有板子
            "I_NAI_ERROR_CB1": self.l1_data.has_error, # L1 冷床是否有错误
            "I_NAI_ERROR_CB2": self.l2_data.has_error,  #L2 冷床是否有错误
            "I_NAI_W1_spare1": self.l1_data.has_cool_bed_steel_left, # 一号冷床左半段有钢
            "I_NAI_W1_spare2": self.l1_data.has_cool_bed_steel_right, # 一号冷床右半段有钢
            "I_NAI_W1_spare3": self.l2_data.has_cool_bed_steel_left, # 二号冷床左半段有钢
            "I_NAI_W1_spare4": self.l2_data.has_cool_bed_steel_right, # 二号冷床右半段有钢
        }

        left_under_steel_l1 = self.l1_data.left_under_steel
        data.update({
            "I_NAI_X_dis_CB1G3": left_under_steel_l1.x_mm,
            "I_NAI_Y_dis_CB1G3": left_under_steel_l1.y_mm,
            "I_NAI_Len_CB1G3": left_under_steel_l1.w_mm,
            "I_NAI_Wid_CB1G3": left_under_steel_l1.h_mm,
            "I_NAI_Ang_CB1G3": 0,
        })
        right_under_steel_l1 = self.l1_data.right_under_steel
        data.update({
            "I_NAI_X_dis_CB1G4":right_under_steel_l1.x_mm,
            "I_NAI_Y_dis_CB1G4":right_under_steel_l1.y_mm,
            "I_NAI_Len_CB1G4":right_under_steel_l1.w_mm,
            "I_NAI_Wid_CB1G4":right_under_steel_l1.h_mm,
            "I_NAI_Ang_CB1G4":0,
        })

        left_under_steel_l2 = self.l2_data.left_under_steel
        data.update({
            "I_NAI_X_dis_CB2G3": left_under_steel_l2.x_mm,
            "I_NAI_Y_dis_CB2G3": left_under_steel_l2.y_mm,
            "I_NAI_Len_CB2G3": left_under_steel_l2.w_mm,
            "I_NAI_Wid_CB2G3": left_under_steel_l2.h_mm,
            "I_NAI_Ang_CB2G3": 0,
        })
        right_under_steel_l2 = self.l2_data.right_under_steel

        data.update({
            "I_NAI_X_dis_CB2G4":right_under_steel_l2.x_mm,
            "I_NAI_Y_dis_CB2G4":right_under_steel_l2.y_mm,
            "I_NAI_Len_CB2G4":right_under_steel_l2.w_mm,
            "I_NAI_Wid_CB2G4":right_under_steel_l2.h_mm,
            "I_NAI_Ang_CB2G4":0,
        })

        data.update(
            {
            "I_NAI_Y_dis_F1":left_under_steel_l1.to_roll_center_y,
            "I_NAI_Ang_F1": 0
            }
        )

        data.update(
            {
            "I_NAI_Y_dis_F2":right_under_steel_l1.to_roll_center_y,
            "I_NAI_Ang_F2": 0
            }
        )

        data.update(
            {
            "I_NAI_Y_dis_F5":left_under_steel_l2.to_roll_center_y,
            "I_NAI_Ang_F5": 0
            }
        )

        data.update(
            {
            "I_NAI_Y_dis_F6":right_under_steel_l2.to_roll_center_y,
            "I_NAI_Ang_F6": 0
            }
        )
        print(data)
        return data

    def send(self):
        data = self.get_data_map()