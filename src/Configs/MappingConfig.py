from PIL import Image
import tool
import CONFIG
from Configs.GlobalCoolBedConfig import get_config, GlobalCoolBedConfigBase


class MappingConfig:
    """
    指标转换参数
    """
    def __init__(self,cool_bed_key, key):
        self.cool_bed_key = cool_bed_key
        image_url = CONFIG.MappingPath/fr"{key}.jpg"
        self.map_image = Image.open(image_url)
        self.width,self.height = self.map_image.size
        self.glob_cool_bed_config:GlobalCoolBedConfigBase = get_config(cool_bed_key,self.width,self.height)
        self.data = tool.load_xml(CONFIG.MappingPath/fr"{key}.xml") # 读取物理坐标标定
        # {'up': [8, 1024, 380, 431], 'down': [5, 1020, 738, 768], 'r_0_2': [14, 66, 437, 733], 'coolbed': [3, 1024, 1, 378]}

        self.x_map = self.get_x_map()
        self.y_map = self.get_y_map()

        self.MAX_LEN = 400 # 距离最 近大允许范围
        print(self.data)
        print(f'x_map  {self.x_map}')
        print(f"y_map  {self.y_map}")

    @property
    def up_seat_d(self):
        return self.glob_cool_bed_config.roll_height

    @property
    def up_seat_u(self):
        return self.glob_cool_bed_config.up_seat_u

    @property
    def up_cool_bed(self):
        return self.glob_cool_bed_config.up_cool_bed

    def get_x_map(self):
        list_ = [
                    [self.cool_bed[0],0],
                    [self.cool_bed[0]+self.cool_bed[2], self.glob_cool_bed_config.cool_bed_width]
                 ]

        if list_[0][0] > 0:
            item_width = list_[1][1] - list_[0][1]
            px_asp =  item_width /( list_[1][0] - list_[0][0])
            list_.insert(0, [0, -px_asp * list_[0][0]])

        last_index = len(list_)-1
        if list_[last_index][0] < self.width:
            item_width = list_[last_index][1] - list_[last_index-1][1]
            px_asp = item_width / (list_[last_index][0] - list_[last_index-1][0])
            list_.append([self.width, px_asp *(self.width -list_[last_index][0] ) +list_[last_index][1] ])
        return list_

    def get_y_map(self):
        list_ = [
                    [self.down[1]+self.down[3], -self.glob_cool_bed_config.down_seat_height],
                    [self.down[1], 0],
                    [self.up[1]+self.up[3],self.glob_cool_bed_config.up_seat_d],
                    [self.up[1], self.glob_cool_bed_config.up_seat_u],
                    [self.cool_bed[1], self.glob_cool_bed_config.up_cool_bed]
                ]  # 自下而上
        if list_[0][0] < self.height:
            item_height = list_[1][1] - list_[0][1]
            px_asp = item_height /( list_[0][0] - list_[1][0])
            list_.insert(0, [self.height, -px_asp * (self.height-list_[0][0]) + list_[0][1]])

        last_index = len(list_) - 1
        if  list_[last_index][0]>0:
            item_width = list_[last_index][1] - list_[last_index - 1][1]
            px_asp = abs(item_width / (list_[last_index][0] - list_[last_index - 1][0]))
            list_.append([0, abs(px_asp * (0 - list_[last_index][0])) + list_[last_index][1]])
        return list_

    @property
    def up(self):
        """
        上轴承座
        :return:
        """
        return self.data["up"]

    @property
    def down(self):
        """
        下轴承座
        :return:
        """
        return self.data["down"]

    @property
    def cool_bed(self):
        return self.data["coolbed"]

    def px_to_x(self,x_):
        x_map_list = self.x_map
        for index in range(len(x_map_list)):
            x_px, x_mm = x_map_list[index]
            if x_ == x_px:
                return x_mm
            if x_<x_px:
                px_asp = (x_map_list[index][1] - x_map_list[index-1][1])/(x_map_list[index][0] - x_map_list[index-1][0])
                px_asp = abs(px_asp)
                return x_map_list[index-1][1] + px_asp * (x_-x_map_list[index-1][0])
        # if CONFIG.DEBUG_MODEL:
        #     return 1
        raise ValueError(f" X 出现越界 ")


    def px_to_y(self,y_):
        y_map_list = self.y_map
        for index in range(len(y_map_list)):
            y_px, y_mm = y_map_list[index]
            if y_ == y_px:
                return y_mm
            if y_ > y_px:
                px_asp = (y_map_list[index][1] - y_map_list[index - 1][1]) / (
                            y_map_list[index][0] - y_map_list[index - 1][0])
                px_asp = abs(px_asp)
                return y_map_list[index - 1][1] + px_asp * abs(y_ - y_map_list[index - 1][0])
        raise ValueError(f" X 出现越界 ")

    def get_rect(self,rect):
        """
        获取毫米值的 矩形
        :param rect:
        :return:
        """
        x,y,w,h = rect
        x,y,x2,y2 = x,y,x+w,y+h
        x_mm,y_mm,x2_mm,y2_mm = self.px_to_x(x),self.px_to_y(y),self.px_to_x(x2),self.px_to_y(y2)
        return  x_mm,y_mm,x2_mm-x_mm,y_mm - y2_mm

    @property
    def mm_center_x(self):
        return self.glob_cool_bed_config.cool_bed_width/2

    @property
    def roll_center_y(self):
        return self.glob_cool_bed_config.roll_height/2

if __name__ =="__main__":
    MappingConfig("L1_g1_6")

