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
        print(self.data)
        # {'up': [8, 1024, 380, 431], 'down': [5, 1020, 738, 768], 'r_0_2': [14, 66, 437, 733], 'coolbed': [3, 1024, 1, 378]}

    @property
    def x_map(self):
        list_ = [[self.cool_bed[0],0],[self.cool_bed[0]+self.cool_bed[2],
                    self.glob_cool_bed_config.cool_bed_width]]
        item_width = list_[1][1] - list_[0][1]

        px_asp =  item_width / list_[1][0] - list_[0][0]
        list_.insert(0,-px_asp * list_[0][0])
        return list_

    @property
    def y_map(self):
        return [
                [self.down[1]+self.down[3], -self.glob_cool_bed_config.down_seat_height],
                [self.down[1], 0],
                [self.up[1]+self.up[3],self.glob_cool_bed_config.up_seat_d],
                [self.up[1], self.glob_cool_bed_config.up_seat_u],
                [self.cool_bed[1], self.glob_cool_bed_config.up_cool_bed]
                ]  # 自下而上

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
        for index in range(len(x_map_list)+1):
            x_px, x_mm = x_map_list[index]
            if x_ <= x_px:
                if index == 0:
                    item_width = x_map_list[1][1]=x_map_list[0][1]
                elif index==len(x_map_list):
                    item_width = x_map_list[len(x_map_list)-1][1] = x_map_list[len(x_map_list)-2][1]
                else:
                    item_width = x_map_list[index][1]-x_map_list[index-1][1]

        cool_bed_width_asp = (x_-self.cool_bed[0]) / self.cool_bed[2]
        return self.glob_cool_bed_config.cool_bed_width * cool_bed_width_asp

    def px_to_y(self,y_):
        if y_< self.cool_bed[]

    def get_rect(self,rect):
        """
        获取毫米值的 矩形
        :param rect:
        :return:
        """
        x,y,w,h = rect
        x,y,x2,y2 = x,y,x+2,y+h
        self.glob_cool_bed_config.get_x()

if __name__ =="__main__":
    MappingConfig("L1_g1_6")
